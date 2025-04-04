import pygame as pg
import pymunk
from pymunk import Vec2d
import math
from src.settings import *

class Player(pg.sprite.Sprite):
    """The main character - transforms from prisoner to wizard frog"""
    def __init__(self, game, x, y):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        
        # State tracking
        self.walking = False
        self.jumping = False
        self.falling = False
        self.facing_right = True
        self.is_wizard = False
        self.tokens_collected = 0
        
        # Double jump tracking
        self.jump_count = 0
        self.max_jumps = 2  # Player can perform 2 jumps before landing
        
        # Create placeholder sprite - will be replaced with character images
        self.load_images()
        self.image = self.prisoner_standing
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
        # Physics body setup
        self.body = pymunk.Body(5, pymunk.moment_for_box(5, (self.width, self.height)))
        self.body.position = x + self.width // 2, y + self.height // 2
        self.shape = pymunk.Poly.create_box(self.body, (self.width - 10, self.height - 5))
        self.shape.friction = 0.9  # Increased friction for better ground control
        self.shape.elasticity = 0
        self.shape.collision_type = 1
        
        # Movement properties
        self.vel = Vec2d(0, 0)
        self.acc = Vec2d(0, 0)
        self.on_ground = False
        self.was_on_ground = False
        self.jump_cooldown = 0
        
        # Platform movement sync
        self.current_platform = None
        self.last_platform_pos = None
        
        # Enhanced coyote time - allows player to jump briefly after leaving a platform
        self.coyote_time = 0
        self.max_coyote_time = PLAYER_COYOTE_TIME  # Seconds the player can jump after leaving ground
        
        # Jump buffer - remembers jump input for a short time before hitting ground
        self.jump_buffer_time = 0
        self.jump_buffered = False
        
        # Variable jump height
        self.jump_cut = False
        self.jump_pressed = False
        self.min_jump_force = PLAYER_JUMP * 0.6  # Minimum jump height when button is released quickly
        
        # Landing effects
        self.landing_dust_particles = []
        self.landing_squish = 0  # Current squish amount (0-1)
        self.fall_distance = 0   # Track distance of fall for landing effects
        self.max_fall_height = 0 # Max height reached during jump/fall
        
        # Animation variables
        self.current_frame = 0
        self.last_update = 0
        self.animation_speed = 150  # milliseconds per frame
        self.squish_recovery_rate = 5.0  # How quickly squish recovers
        
    def load_images(self):
        """Load character images and create basic colored rectangles as placeholders"""
        # Prisoner sprite (blue outfit, teal face)
        self.prisoner_standing = self.create_frog_sprite(BLUE_PRISONER, False)
        self.prisoner_walking = [
            self.create_frog_sprite(BLUE_PRISONER, False, offset=-2), 
            self.create_frog_sprite(BLUE_PRISONER, False),
            self.create_frog_sprite(BLUE_PRISONER, False, offset=2),
            self.create_frog_sprite(BLUE_PRISONER, False)
        ]
        self.prisoner_jump = self.create_frog_sprite(BLUE_PRISONER, False, jump=True)
        
        # Wizard sprite (teal outfit with X patterns, wizard hat)
        self.wizard_standing = self.create_frog_sprite(TEAL, True)  
        self.wizard_walking = [
            self.create_frog_sprite(TEAL, True, offset=-2),
            self.create_frog_sprite(TEAL, True),
            self.create_frog_sprite(TEAL, True, offset=2),
            self.create_frog_sprite(TEAL, True)
        ]
        self.wizard_jump = self.create_frog_sprite(TEAL, True, jump=True)
        
    def create_frog_sprite(self, body_color, is_wizard, offset=0, jump=False):
        """Create a simple frog sprite with the given parameters"""
        image = pg.Surface((self.width, self.height), pg.SRCALPHA)
        
        # Body
        if jump:
            # Stretched/squished body for jump animation
            body_height = self.height - 10
            pg.draw.ellipse(image, body_color, 
                           (5, 15, self.width - 10, body_height))
        else:
            # Regular body, slight squish based on offset for walk animation
            body_height = self.height - 15 + abs(offset)
            pg.draw.ellipse(image, body_color, 
                           (5, 10 - offset, self.width - 10, body_height))
        
        # Face (always teal)
        face_width = self.width - 20
        face_height = self.height // 2 - 5
        pg.draw.ellipse(image, TEAL, 
                       (10, 5, face_width, face_height))
        
        # Eyes (white with black pupils)
        eye_y = 15
        # Left eye
        pg.draw.ellipse(image, WHITE, (15, eye_y, 12, 8))
        pg.draw.ellipse(image, BLACK, (19, eye_y + 2, 4, 4))
        # Right eye
        pg.draw.ellipse(image, WHITE, (self.width - 27, eye_y, 12, 8))
        pg.draw.ellipse(image, BLACK, (self.width - 23, eye_y + 2, 4, 4))
        
        # Mouth (brown)
        mouth_y = 30
        pg.draw.rect(image, BROWN, (self.width // 4, mouth_y, self.width // 2, 8), 
                    border_radius=4)
        
        if is_wizard:
            # Wizard hat
            hat_width = self.width - 20
            hat_height = 30
            hat_x = 10
            hat_y = -5
            
            # Draw conical hat
            pg.draw.polygon(image, TEAL, [
                (hat_x + hat_width // 2, hat_y - hat_height // 2),  # Top
                (hat_x, hat_y + hat_height // 2),                   # Bottom left
                (hat_x + hat_width, hat_y + hat_height // 2)        # Bottom right
            ])
            
            # X mark on hat
            x_size = 10
            x_center = hat_x + hat_width // 2
            x_y = hat_y + 5
            pg.draw.line(image, BLACK, (x_center - x_size//2, x_y - x_size//2), 
                        (x_center + x_size//2, x_y + x_size//2), 2)
            pg.draw.line(image, BLACK, (x_center - x_size//2, x_y + x_size//2), 
                        (x_center + x_size//2, x_y - x_size//2), 2)
            
            # X patterns on body (3 small X marks)
            for i in range(3):
                x_size = 8
                x_y = 45 + i * 20
                x_x = 20 + (i % 2) * 25
                pg.draw.line(image, BLACK, (x_x - x_size//2, x_y - x_size//2), 
                            (x_x + x_size//2, x_y + x_size//2), 2)
                pg.draw.line(image, BLACK, (x_x - x_size//2, x_y + x_size//2), 
                            (x_x + x_size//2, x_y - x_size//2), 2)
        
        return image

    def update(self):
        """Update player position, state and animations"""
        self.apply_physics()
        self.animate()
        self.check_on_ground()
        
        # Update cooldowns
        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1
            
        # Update sprite position from physics body
        x, y = self.body.position
        self.rect.center = (int(x), int(y))
        
    def apply_physics(self):
        """Apply physics calculations to the player with enhanced responsiveness"""
        # Reset acceleration (vertical gravity)
        acc_y = PLAYER_GRAVITY
        acc_x = 0
        
        # Apply horizontal movement based on input with improved responsiveness
        keys = pg.key.get_pressed()
        moving = False
        
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            moving = True
            # Enhanced direction change responsiveness
            if self.body.velocity.x > 0:
                # Rapid direction change when turning around
                acc_x = -PLAYER_ACC * 2.0
            else:
                # Apply acceleration curve for smoother ramping
                current_speed = abs(self.body.velocity.x)
                speed_factor = min(1.0, (current_speed / PLAYER_MAX_SPEED) ** PLAYER_ACCELERATION_CURVE)
                acc_x = -PLAYER_ACC * (1.0 + 0.5 * (1.0 - speed_factor))
            self.facing_right = False
            self.walking = True
        elif keys[pg.K_RIGHT] or keys[pg.K_d]:
            moving = True
            # Enhanced direction change responsiveness
            if self.body.velocity.x < 0:
                # Rapid direction change when turning around
                acc_x = PLAYER_ACC * 2.0
            else:
                # Apply acceleration curve for smoother ramping
                current_speed = abs(self.body.velocity.x)
                speed_factor = min(1.0, (current_speed / PLAYER_MAX_SPEED) ** PLAYER_ACCELERATION_CURVE)
                acc_x = PLAYER_ACC * (1.0 + 0.5 * (1.0 - speed_factor))
            self.facing_right = True
            self.walking = True
        else:
            self.walking = False
        
        # Apply air control - reduced control when not touching ground
        if not self.on_ground:
            acc_x *= PLAYER_AIR_CONTROL
            
        # Smoother stopping when not pressing movement keys
        if not moving:
            # Apply stronger friction for better stopping control
            stop_factor = 0.82 if self.on_ground else 0.92  # Less friction in air
            self.body.velocity = Vec2d(self.body.velocity.x * stop_factor, self.body.velocity.y)
        
        # Apply friction - using optimized value for better control
        acc_x += self.body.velocity.x * PLAYER_FRICTION
        
        # Create acceleration vector
        self.acc = Vec2d(acc_x, acc_y)
        
        # Update velocity and position with enhanced smoothness
        self.body.velocity += self.acc * self.game.dt
        
        # Sync with moving platform if standing on one
        if self.current_platform and self.current_platform.is_moving and self.on_ground:
            # Get platform's current position
            platform_pos = Vec2d(*self.current_platform.body.position)
            
            # If we have a previous position, calculate the delta movement
            if self.last_platform_pos is not None:
                # Calculate how much the platform moved since last frame
                platform_delta = platform_pos - self.last_platform_pos
                
                # Apply this movement to the player's body
                self.body.position += platform_delta
            
            # Store current platform position for next frame
            self.last_platform_pos = platform_pos
        else:
            # Reset last platform position if not on a moving platform
            self.last_platform_pos = None
        
        # Limit horizontal speed using our defined max speed
        if abs(self.body.velocity.x) > PLAYER_MAX_SPEED:
            self.body.velocity = Vec2d(
                math.copysign(PLAYER_MAX_SPEED, self.body.velocity.x),
                self.body.velocity.y
            )
            
        # Update jumping/falling state
        if self.body.velocity.y < 0:
            self.jumping = True
            self.falling = False
        elif self.body.velocity.y > 50:
            self.jumping = False
            self.falling = True
        else:
            self.jumping = False
            self.falling = False
            
    def check_on_ground(self):
        """Check if player is touching the ground with coyote time and better ground detection"""
        # Store previous ground state and velocity
        prev_on_ground = self.on_ground
        prev_velocity_y = self.body.velocity.y
        
        # Reset on_ground
        self.on_ground = False
        
        # Use multiple raycasts for more reliable ground detection
        # We'll consider the player on ground if they're not moving much vertically
        # and there's a platform directly beneath them
        if abs(self.body.velocity.y) < 8.0:  # Slightly increased threshold for more reliable detection
            # Perform three raycasts: one from center, and two from near the feet edges
            foot_positions = [
                # Center raycast
                (self.body.position.x, self.body.position.y + self.height // 2 - 2),
                # Left foot raycast
                (self.body.position.x - self.width//3, self.body.position.y + self.height // 2 - 2),
                # Right foot raycast
                (self.body.position.x + self.width//3, self.body.position.y + self.height // 2 - 2)
            ]
            
            for foot_pos in foot_positions:
                # Check a bit below feet with buffer distance
                query = self.game.space.segment_query(
                    foot_pos,
                    (foot_pos[0], foot_pos[1] + PLAYER_GROUND_BUFFER + 2),
                    1,
                    pymunk.ShapeFilter()
                )
                if query:
                    self.on_ground = True
                    # Reset coyote time when landing
                    self.coyote_time = 0
                    
                    # Reset jump count when landing on ground
                    self.jump_count = 0
                    
                    # Handle buffered jumps - execute jump if buffer is active
                    if self.jump_buffered and self.jump_buffer_time > 0:
                        self.jump()
                        self.jump_buffered = False
                        self.jump_buffer_time = 0
                    
                    # Generate landing dust particles if we just landed from a fall
                    if not prev_on_ground and self.falling:
                        # Calculate landing squish based on fall velocity
                        fall_speed = prev_velocity_y
                        if fall_speed > 200:
                            # Apply landing squish effect proportional to fall speed
                            self.landing_squish = min(1.0, fall_speed / 1000 * PLAYER_LAND_SQUISH)
                            self.create_landing_dust(intensity=self.landing_squish)
                            
                            # Play landing sound when landing from a significant fall
                            if hasattr(self.game, 'sound_manager') and fall_speed > 300:
                                self.game.sound_manager.play_land()
                                
                            # Reset fall tracking
                            self.fall_distance = 0
                            self.max_fall_height = 0
                    break
        
        # Also check based on collision callbacks from pymunk
        if not self.on_ground:
            self.on_ground = getattr(self, '_on_ground', False)
        
        # Update jump buffer timer
        if self.jump_buffer_time > 0:
            self.jump_buffer_time -= self.game.dt
            if self.jump_buffer_time <= 0:
                self.jump_buffered = False
        
        # Handle coyote time - start timer when player leaves ground
        if prev_on_ground and not self.on_ground and self.body.velocity.y >= 0:
            self.coyote_time = PLAYER_COYOTE_TIME  # Use the settings constant
        elif self.coyote_time > 0:
            self.coyote_time -= self.game.dt
            
        # Track fall distance for landing effects
        if self.falling:
            if self.body.position.y > self.max_fall_height:
                self.max_fall_height = self.body.position.y
                
        # Update landing squish recovery
        if self.landing_squish > 0:
            self.landing_squish -= self.game.dt * self.squish_recovery_rate
            if self.landing_squish < 0:
                self.landing_squish = 0
            
    def jump(self):
        """Make the player jump if on ground/coyote time or if double jump is available"""
        # Store previous state
        self.was_on_ground = self.on_ground
        
        # Can we jump? Either on ground/coyote time (first jump) or mid-air with jump count < max (double jump)
        can_first_jump = (self.on_ground or self.coyote_time > 0) and self.jump_cooldown == 0
        can_double_jump = not self.on_ground and self.jump_count < self.max_jumps and self.jump_cooldown == 0
        
        # If we can't jump now, buffer the input for a short time
        if not can_first_jump and not can_double_jump and self.falling:
            self.jump_buffered = True
            self.jump_buffer_time = PLAYER_JUMP_BUFFER_TIME
            return  # Exit early, we'll check for buffered jumps when landing
        
        if can_first_jump:
            # First jump (from ground) - preserve horizontal momentum for better control
            jump_vel = -PLAYER_JUMP
            
            # Add a larger horizontal boost in the direction of movement
            # for better jump arc when running and jumping
            current_vel_x = self.body.velocity.x
            if abs(current_vel_x) > 80:  # Lowered threshold for boost
                # Get direction player is moving
                direction = 1 if current_vel_x > 0 else -1
                # Add stronger horizontal boost (increased from 50)
                boost_amount = min(80, abs(current_vel_x) * 0.3)  # Scale boost with current speed
                current_vel_x += direction * boost_amount
                
            # Apply jump velocity with a slightly increased jump height
            # for better feel (110% of normal)
            self.body.velocity = Vec2d(current_vel_x, jump_vel * 1.1)
            
            # Create jump dust particles
            self.create_jump_dust()
            
            # Play jump sound
            if hasattr(self.game, 'sound_manager'):
                self.game.sound_manager.play_jump()
            
            # Update state
            self.jumping = True
            self.on_ground = False
            self.coyote_time = 0
            self.jump_cooldown = 3  # Even lower cooldown for more responsive jumps (from 4)
            self.jump_cut = False
            self.jump_pressed = True
            self.jump_count = 1  # This is our first jump
            self.max_fall_height = self.body.position.y  # Reset fall height tracking
            
        elif can_double_jump:
            # Double jump (in mid-air) with improved feel
            jump_vel = -PLAYER_JUMP * 0.95  # Slightly weaker second jump
            
            # Reset vertical velocity completely for more consistent double jump height
            # regardless of when it's executed during the jump arc
            if self.body.velocity.y > 0:  # If falling
                # Reset vertical velocity while preserving horizontal velocity
                self.body.velocity = Vec2d(self.body.velocity.x, 0)
                
            # Add a small horizontal boost in the direction the player is facing
            # to improve mid-air control
            if self.facing_right:
                horizontal_boost = 30
            else:
                horizontal_boost = -30
                
            # Apply jump velocity with boost
            self.body.velocity = Vec2d(
                self.body.velocity.x + horizontal_boost, 
                jump_vel
            )
            
            # Create mid-air double jump effect
            if hasattr(self.game, 'token_particles'):
                feet_pos = (
                    self.rect.centerx + self.game.camera_offset_x,
                    self.rect.bottom + self.game.camera_offset_y
                )
                self.game.token_particles.spawn_particles(feet_pos, 12, spread=40)
            
            # Update state
            self.jumping = True
            self.jump_cooldown = 4
            self.jump_cut = False
            self.jump_pressed = True
            self.jump_count += 1  # Increment jump count
            self.max_fall_height = self.body.position.y  # Reset fall height tracking
            
    def create_jump_dust(self):
        """Create dust particles when jumping from the ground"""
        if hasattr(self.game, 'token_particles'):
            # Use token particles system to create dust
            feet_pos = (
                self.rect.centerx + self.game.camera_offset_x,
                self.rect.bottom + self.game.camera_offset_y
            )
            # Create a directed burst of particles at the player's feet
            self.game.token_particles.spawn_particles(feet_pos, 6, spread=20)
            
    def create_landing_dust(self, intensity=0.5):
        """Create dust particles when landing with variable intensity"""
        if hasattr(self.game, 'token_particles'):
            # Use token particles system to create dust
            feet_pos = (
                self.rect.centerx + self.game.camera_offset_x,
                self.rect.bottom + self.game.camera_offset_y
            )
            # Create a burst of particles at the player's feet
            # Scale particle count and spread with intensity of landing
            particle_count = int(8 * intensity) + 4  # At least 4 particles
            spread = int(30 * intensity) + 20        # At least 20 spread
            self.game.token_particles.spawn_particles(feet_pos, particle_count, spread=spread)
        
    def release_jump(self):
        """Called when jump button is released - allows for variable jump height"""
        if self.jumping and self.body.velocity.y < 0 and not self.jump_cut:
            # Cut the jump short if player releases jump button early
            # But don't cut it below minimum height
            if self.body.velocity.y < -self.min_jump_force:
                self.body.velocity = Vec2d(self.body.velocity.x, -self.min_jump_force)
            self.jump_cut = True
            self.jump_pressed = False
        
    def animate(self):
        """Update player animation based on state and apply visual effects like squishing"""
        now = pg.time.get_ticks()
        
        # Determine which set of images to use based on wizard state
        if self.is_wizard:
            standing_img = self.wizard_standing
            walking_frames = self.wizard_walking
            jump_img = self.wizard_jump
        else:
            standing_img = self.prisoner_standing
            walking_frames = self.prisoner_walking
            jump_img = self.prisoner_jump
        
        # Jumping animation
        if self.jumping or self.falling:
            self.image = jump_img
        # Walking animation
        elif self.walking:
            if now - self.last_update > self.animation_speed:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(walking_frames)
                self.image = walking_frames[self.current_frame]
        # Standing animation
        else:
            self.image = standing_img
            
        # Apply landing squish effect if active
        if self.landing_squish > 0 and self.on_ground:
            # Create a squished version of the image
            orig_height = self.image.get_height()
            squish_amount = self.landing_squish * 0.3  # Scale down the effect to keep it subtle
            
            # Calculate new height with squish
            new_height = int(orig_height * (1.0 - squish_amount))
            # Calculate width increase to maintain volume
            width_factor = 1.0 + (squish_amount * 0.5)
            new_width = int(self.image.get_width() * width_factor)
            
            # Scale the image to create squish effect
            # Store original center for positioning
            center = self.rect.center
            
            # Scale the image
            self.image = pg.transform.scale(self.image, (new_width, new_height))
            
            # Update rect and maintain center position
            self.rect = self.image.get_rect()
            self.rect.center = center
            
        # Flip image if facing left
        if not self.facing_right:
            self.image = pg.transform.flip(self.image, True, False)
            
    def collect_token(self):
        """Collect an X token, potentially transforming into wizard form"""
        self.tokens_collected += 1
        
        # Play token collection sound
        if hasattr(self.game, 'sound_manager'):
            self.game.sound_manager.play_token_collect()
            
        if self.tokens_collected >= TOKENS_TO_TRANSFORM and not self.is_wizard:
            self.transform_to_wizard()
            
    def transform_to_wizard(self):
        """Transform from prisoner to wizard form"""
        self.is_wizard = True
        
        # Play transformation sound effect
        if hasattr(self.game, 'sound_manager'):
            self.game.sound_manager.play_level_complete()  # Use level complete sound for transformation
            
        # Create transformation particle effects
        if hasattr(self.game, 'token_particles'):
            # Larger burst of particles at player position
            player_pos = (
                self.rect.centerx + self.game.camera_offset_x,
                self.rect.centery + self.game.camera_offset_y
            )
            self.game.token_particles.spawn_particles(player_pos, 30, spread=100)
            
        # Give a small boost to abilities
        self.max_jumps = 3  # Extra jump as wizard
