import pygame as pg
import pymunk
from pymunk import Vec2d
import math
import random
from src.settings import *
from src.effects import Shadow, Glow, Animation, BuildingDecorations, ParallaxBackground, darken_color, lighten_color

class PhysicsSprite(pg.sprite.Sprite):
    """Base class for sprites with physics properties"""
    def __init__(self, game, x, y, width, height):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Setup pygame sprite
        self.image = pg.Surface((width, height))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
        # Physics body setup
        self.body = pymunk.Body(1, 100)
        self.body.position = x + width // 2, y + height // 2
        self.shape = pymunk.Poly.create_box(self.body, (width, height))
        self.shape.elasticity = 0.0
        self.shape.friction = 0.5
        self.shape.collision_type = 1
        
        # Animation
        self.animation = None
        self.has_shadow = False
        self.has_glow = False
        
    def update(self):
        # Update pygame rect position from physics body
        x, y = self.body.position
        self.rect.center = (int(x), int(y))
        
        # Apply animation effects if any
        if self.animation:
            offset_x, offset_y = self.animation.update(self.game.dt)
            self.rect.centerx += offset_x
            self.rect.centery += offset_y
        
class StaticObject(pg.sprite.Sprite):
    """Base class for static environment objects"""
    def __init__(self, game, x, y, width, height):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Setup pygame sprite
        self.image = pg.Surface((width, height))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
        # Static body
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = x + width // 2, y + height // 2
        self.shape = pymunk.Poly.create_box(self.body, (width, height))
        self.shape.elasticity = 0.0
        self.shape.friction = 0.5
        self.shape.collision_type = 2
        
        # Visual effects
        self.animation = None
        self.has_shadow = False
        self.visual_offset_y = 0  # For animation effects

class Platform(StaticObject):
    """Platform that characters can stand on"""
    def __init__(self, game, x, y, width, height, platform_type="standard"):
        super().__init__(game, x, y, width, height)
        
        self.platform_type = platform_type
        
        # For moving platforms
        self.is_moving = False
        self.move_speed = 0
        self.move_distance = 0
        self.original_x = x
        self.original_y = y
        self.direction = 1
        
        # Enhanced visuals
        if platform_type == "building":
            # Create a building platform for Financial District level
            self.create_building_appearance()
        elif platform_type == "floating":
            # Create a floating platform with unique appearance
            self.create_floating_appearance()
        else:
            # Standard platform with enhanced appearance
            self.create_standard_appearance()
        
        # Apply shadow effect - buildings and floating platforms get shadows
        if platform_type in ["building", "floating"] or random.random() < 0.7:
            self.has_shadow = True
            self.apply_shadow()
            
        # Add subtle animation for floating platforms
        if platform_type == "floating":
            self.animation = Animation("platform")
            self.animation.sin_amplitude = 8  # More noticeable movement
            self.animation.sin_speed = random.uniform(1.0, 1.5)  # Varied speed
            self.visual_offset_y = 0
        elif platform_type == "building" and width < 300:
            # Slight animation for small buildings
            self.animation = Animation("platform")
            self.animation.sin_amplitude = 1.5  # Very subtle
            self.animation.sin_speed = 0.5
            self.visual_offset_y = 0

    def create_standard_appearance(self):
        """Create a standard platform appearance"""
        # Dark teal base
        base_color = DARK_TEAL
        self.image.fill(base_color)
        
        # Add a subtle top highlight
        highlight_height = min(6, self.height // 4)
        highlight_rect = pg.Rect(0, 0, self.width, highlight_height)
        highlight_color = lighten_color(base_color, 0.3)
        pg.draw.rect(self.image, highlight_color, highlight_rect)
        
        # Add subtle bottom shadow
        shadow_height = min(6, self.height // 4)
        shadow_rect = pg.Rect(0, self.height - shadow_height, self.width, shadow_height)
        shadow_color = darken_color(base_color, 0.7)
        pg.draw.rect(self.image, shadow_color, shadow_rect)
        
    def create_building_appearance(self):
        """Create a building appearance for platforms in Financial District"""
        # Choose a random building color
        base_color = random.choice(BUILDING_COLORS)
        self.image.fill(base_color)
        
        # Apply building decorations (windows, details, etc.)
        self.image = BuildingDecorations.apply(self.image, base_color)
        
    def create_floating_appearance(self):
        """Create a floating platform with a unique appearance"""
        # Use teal as base color but with some variations
        hue_shift = random.uniform(-0.1, 0.1)  # Slight color variation
        base_color = (
            min(255, max(0, int(TEAL[0] * (1 + hue_shift)))),
            min(255, max(0, int(TEAL[1] * (1 + hue_shift)))),
            min(255, max(0, int(TEAL[2] * (1 + hue_shift))))
        )
        self.image.fill(base_color)
        
        # Add glowing edges
        edge_width = 3
        inner_rect = pg.Rect(edge_width, edge_width, 
                            self.width - edge_width*2, 
                            self.height - edge_width*2)
        
        # Draw inner part slightly darker
        pg.draw.rect(self.image, darken_color(base_color, 0.8), inner_rect)
        
        # Add X patterns for SUPERSEED branding
        x_size = min(15, self.width // 10)
        x_count = max(1, self.width // 40)  # Scale with platform width
        
        for i in range(x_count):
            x_pos = (i+1) * self.width // (x_count+1)
            y_pos = self.height // 2
            
            # Draw the X
            pg.draw.line(self.image, LIGHT_TEAL, 
                       (x_pos - x_size//2, y_pos - x_size//2),
                       (x_pos + x_size//2, y_pos + x_size//2), 2)
            pg.draw.line(self.image, LIGHT_TEAL, 
                       (x_pos - x_size//2, y_pos + x_size//2),
                       (x_pos + x_size//2, y_pos - x_size//2), 2)
        
        # Apply a subtle glow effect to make it look magical/floating
        self.image = Glow.apply(self.image, LIGHT_TEAL, 0.3, 2)
        
    def apply_shadow(self):
        """Apply a shadow effect to the platform"""
        self.image = Shadow.apply(self.image)

    def setup_movement(self, speed, distance):
        """Configure platform to move horizontally"""
        self.is_moving = True
        self.move_speed = speed
        self.move_distance = distance
        self.body.body_type = pymunk.Body.KINEMATIC
        
    def update(self):
        # Update position for moving platforms
        if self.is_moving:
            # Calculate new position
            offset = self.move_speed * self.game.dt * self.direction
            pos_x, pos_y = self.body.position
            
            # Check if we need to reverse direction
            if (pos_x - self.original_x > self.move_distance) or (self.original_x - pos_x > self.move_distance):
                self.direction *= -1
                offset = self.move_speed * self.game.dt * self.direction
                
            # Apply movement
            self.body.position = pos_x + offset, pos_y
            self.rect.center = (int(pos_x + offset), int(pos_y))
            
        # Apply animation effects if present
        if self.animation:
            _, offset_y = self.animation.update(self.game.dt)
            self.visual_offset_y = offset_y
            # Note: We don't update physics body position for visual bobbing
            # This is just for drawing
            
    def draw(self, surface, camera_offset_x, camera_offset_y):
        """Custom draw method with animation offset"""
        draw_x = self.rect.x + camera_offset_x
        draw_y = self.rect.y + camera_offset_y + self.visual_offset_y
        surface.blit(self.image, (draw_x, draw_y))
            
class SuperseedToken(pg.sprite.Sprite):
    """Collectable Superseed token that helps transform the character"""
    # Class-level image loading to avoid reloading for each instance
    token_images = {}
    token_types = ["x_token", "star_token", "coin_token", "gem_token", "logo_token"]
    
    @classmethod
    def load_images(cls):
        """Load token images from assets directory"""
        if not cls.token_images:
            for token_type in cls.token_types:
                try:
                    # Load image and convert alpha for transparency
                    image_path = f"assets/images/tokens/{token_type}.png"
                    image = pg.image.load(image_path).convert_alpha()
                    cls.token_images[token_type] = image
                except (pg.error, FileNotFoundError) as e:
                    print(f"Error loading token image {token_type}: {e}")
                    # Create a fallback texture
                    fallback = pg.Surface((32, 32), pg.SRCALPHA)
                    pg.draw.circle(fallback, TEAL, (16, 16), 14)
                    pg.draw.rect(fallback, BLACK, (8, 8, 16, 16), 2)
                    cls.token_images[token_type] = fallback
    
    def __init__(self, game, x, y, token_type=None):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.size = TOKEN_SIZE
        
        # Load token images if not already loaded
        self.load_images()
        
        # Select token type - random if not specified
        if token_type is None:
            self.token_type = random.choice(self.token_types)
        else:
            self.token_type = token_type if token_type in self.token_types else self.token_types[0]
        
        # Create enhanced token with visual design
        # Use larger base size to accommodate glow effects
        expanded_size = self.size * 1.5
        self.base_image = pg.Surface((expanded_size, expanded_size), pg.SRCALPHA)
        
        # Draw multi-layered token with inner and outer circles
        center = expanded_size // 2
        
        # Draw outer glow
        glow_radius = self.size // 2 + 6
        for i in range(5):
            glow_alpha = 150 - i * 30
            pg.draw.circle(
                self.base_image, 
                (*BRIGHT_TEAL, glow_alpha), 
                (center, center), 
                glow_radius - i
            )
        
        # Draw main token body with gradient effect
        token_radius = self.size // 2
        
        # Draw outer ring for 3D effect
        pg.draw.circle(
            self.base_image, 
            DARK_TEAL, 
            (center, center), 
            token_radius
        )
        
        # Draw inner circle (slightly smaller)
        pg.draw.circle(
            self.base_image, 
            TEAL, 
            (center, center), 
            token_radius - 2
        )
        
        # Add highlight at top for 3D effect
        highlight_radius = token_radius - 4
        highlight_rect = pg.Rect(
            center - highlight_radius,
            center - highlight_radius,
            highlight_radius * 2,
            highlight_radius
        )
        pg.draw.ellipse(
            self.base_image,
            LIGHT_TEAL,
            highlight_rect
        )
        
        # Get token image and scale it to fit inside the token
        token_image = self.token_images.get(self.token_type)
        inner_size = token_radius * 1.5
        
        # Scale the token image to fit properly
        if token_image:
            # Scale image to fit within the token
            scale_ratio = inner_size / max(token_image.get_width(), token_image.get_height())
            scaled_width = int(token_image.get_width() * scale_ratio)
            scaled_height = int(token_image.get_height() * scale_ratio)
            
            scaled_image = pg.transform.smoothscale(token_image, (scaled_width, scaled_height))
            
            # Position image in center of token
            image_x = center - scaled_width // 2
            image_y = center - scaled_height // 2
            
            # Draw the token image
            self.base_image.blit(scaled_image, (image_x, image_y))
        
        # Apply additional glow effect
        self.base_image = Glow.apply(self.base_image, BRIGHT_TEAL, 0.6, 4)
        self.image = self.base_image.copy()
        
        # Set up rect with adjusted size to account for visual effects
        self.rect = self.image.get_rect()
        # Center the rect at the given position
        self.rect.center = (x + self.size // 2, y + self.size // 2)
        
        # Physics sensor (doesn't block movement but detects collision)
        self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.body.position = x + self.size // 2, y + self.size // 2
        self.shape = pymunk.Circle(self.body, self.size // 2 - 4)  # Slightly smaller for better feel
        self.shape.sensor = True
        self.shape.collision_type = 3
        
        # Enhanced animation
        self.animation = Animation("token")
        self.animation.sin_amplitude = TOKEN_BOB_AMOUNT * 1.2  # Slightly more pronounced bobbing
        self.animation.sin_speed = TOKEN_BOB_SPEED * 1.2  # Faster bobbing
        self.visual_offset_y = 0
        
        # Improved rotation animation
        self.angle = random.uniform(0, 360)  # Random starting angle
        self.rotation_speed = random.uniform(0.5, 1.5) * (1 if random.random() > 0.5 else -1)
        
        # Pulse animation
        self.pulse_time = random.uniform(0, math.pi * 2)  # Random start phase
        self.pulse_speed = random.uniform(3.0, 5.0)  # Different speeds for variety
        self.pulse_amount = random.uniform(0.05, 0.1)  # Size pulsing amount
        
        # Particles
        self.particle_timer = 0
        self.particle_interval = random.uniform(0.8, 1.5)  # Time between particle emissions
        
    def update(self):
        # Update animation offset
        if self.animation:
            _, offset_y = self.animation.update(self.game.dt)
            self.visual_offset_y = offset_y
            
        # Update rotation animation
        self.angle += self.rotation_speed * self.game.dt * 60
        if self.angle > 360:
            self.angle -= 360
        elif self.angle < 0:
            self.angle += 360
            
        # Update pulse animation
        self.pulse_time += self.game.dt * self.pulse_speed
        pulse_scale = 1.0 + math.sin(self.pulse_time) * self.pulse_amount
        
        # Create pulsing effect
        pulsed_base = pg.transform.smoothscale(
            self.base_image,
            (int(self.base_image.get_width() * pulse_scale),
             int(self.base_image.get_height() * pulse_scale))
        )
        
        # Apply rotation to the image after pulsing
        self.image = pg.transform.rotate(pulsed_base, self.angle)
        
        # Keep the rect center but update its size
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center
        
        # Update position from physics body
        x, y = self.body.position
        self.rect.center = (int(x), int(y))
        
        # Emit particles occasionally
        self.particle_timer += self.game.dt
        if self.particle_timer >= self.particle_interval:
            self.particle_timer = 0
            self.particle_interval = random.uniform(0.8, 1.5)  # Randomize next interval
            
            # Emit a small particle burst
            if hasattr(self.game, 'token_particles'):
                offset_x = random.uniform(-self.size/3, self.size/3)
                offset_y = random.uniform(-self.size/3, self.size/3)
                
                particle_pos = (
                    self.rect.centerx + self.game.camera_offset_x + offset_x,
                    self.rect.centery + self.game.camera_offset_y + offset_y
                )
                
                # Small particle emission
                self.game.token_particles.spawn_particles(
                    particle_pos,
                    2,  # Just a few particles for continuous effect
                    spread=10,
                    color=BRIGHT_TEAL
                )
        
    def draw(self, surface, camera_offset_x, camera_offset_y):
        """Custom draw method with animation offset"""
        draw_x = self.rect.x + camera_offset_x
        draw_y = self.rect.y + camera_offset_y + self.visual_offset_y
        surface.blit(self.image, (draw_x, draw_y))
        
class Lightning:
    """Lightning hazard representing market crash for Level 3"""
    def __init__(self, game, x, y, width, height, angle=45, duration=LIGHTNING_DURATION):
        self.game = game
        self.x = x
        self.y = y
        self.width = width  # Width of the lightning bolt
        self.height = height  # Length of the lightning bolt
        self.angle = angle  # Angle in degrees (0 = horizontal, 90 = vertical)
        self.duration = duration  # How long the lightning exists
        self.time_alive = 0
        self.warning_time = LIGHTNING_WARNING_TIME  # Time for warning before active
        self.is_active = False  # Whether lightning is actually dangerous
        self.particles = []  # For lightning effect
        
        # Create a surface for the lightning
        self.update_surface()
        
        # Calculate collision points
        self.update_collision_points()
        
    def update_surface(self):
        """Update the lightning surface based on current state"""
        # Calculate actual dimensions based on angle
        diagonal = math.sqrt(self.width**2 + self.height**2)
        padded_width = int(diagonal) + 20  # Add padding for rotation
        
        self.surface = pg.Surface((padded_width, padded_width), pg.SRCALPHA)
        center = padded_width // 2
        
        if self.time_alive < self.warning_time:
            # Warning animation - semi-transparent
            color = LIGHTNING_WARNING_COLOR
            # Draw a line for the warning
            end_x = center + int(math.cos(math.radians(self.angle)) * self.height / 2)
            end_y = center + int(math.sin(math.radians(self.angle)) * self.height / 2)
            start_x = center - int(math.cos(math.radians(self.angle)) * self.height / 2)
            start_y = center - int(math.sin(math.radians(self.angle)) * self.height / 2)
            
            # Make the line pulsate based on time remaining until active
            alpha = int(200 * (self.time_alive / self.warning_time))
            warning_color = (*LIGHTNING_COLOR[:3], alpha)
            
            # Draw dashed line for warning
            dash_length = 10
            total_length = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
            num_dashes = int(total_length / dash_length)
            
            for i in range(num_dashes):
                # Draw every other segment for dashed effect
                if i % 2 == 0:
                    t1 = i / num_dashes
                    t2 = (i + 0.5) / num_dashes
                    
                    x1 = start_x + (end_x - start_x) * t1
                    y1 = start_y + (end_y - start_y) * t1
                    x2 = start_x + (end_x - start_x) * t2
                    y2 = start_y + (end_y - start_y) * t2
                    
                    pg.draw.line(self.surface, warning_color, (x1, y1), (x2, y2), LIGHTNING_WIDTH)
        else:
            # Active lightning - full opacity
            # Draw jagged lightning bolt for active state
            points = []
            segments = 8  # Number of segments in the lightning
            
            start_x = center - int(math.cos(math.radians(self.angle)) * self.height / 2)
            start_y = center - int(math.sin(math.radians(self.angle)) * self.height / 2)
            end_x = center + int(math.cos(math.radians(self.angle)) * self.height / 2)
            end_y = center + int(math.sin(math.radians(self.angle)) * self.height / 2)
            
            # Start and end points
            points.append((start_x, start_y))
            
            # Generate jagged points between
            perpendicular_angle = self.angle + 90
            for i in range(1, segments):
                t = i / segments
                # Base point along the line
                base_x = start_x + (end_x - start_x) * t
                base_y = start_y + (end_y - start_y) * t
                
                # Deviation perpendicular to the line
                deviation = random.randint(-15, 15)
                offset_x = deviation * math.cos(math.radians(perpendicular_angle))
                offset_y = deviation * math.sin(math.radians(perpendicular_angle))
                
                points.append((base_x + offset_x, base_y + offset_y))
            
            # Add end point (store for arrow positioning)
            final_point = (end_x, end_y)
            points.append(final_point)
            
            # Add arrow at the bottom to make it look like a stock market line
            # Calculate arrow points (triangle pointing downward at the end)
            arrow_size = 12  # Size of arrow
            # Direction vector of the last segment
            if len(points) >= 2:
                last_point = points[-2]  # Second to last point
                dir_x = final_point[0] - last_point[0]
                dir_y = final_point[1] - last_point[1]
                
                # Normalize direction vector
                length = math.sqrt(dir_x**2 + dir_y**2)
                if length > 0:
                    dir_x /= length
                    dir_y /= length
                    
                    # Calculate perpendicular vector
                    perp_x = -dir_y
                    perp_y = dir_x
                    
                    # Calculate arrow points (triangle)
                    arrow_points = [
                        final_point,  # Tip of arrow
                        (final_point[0] - dir_x * arrow_size + perp_x * arrow_size/1.5, 
                         final_point[1] - dir_y * arrow_size + perp_y * arrow_size/1.5),  # Right corner
                        (final_point[0] - dir_x * arrow_size - perp_x * arrow_size/1.5, 
                         final_point[1] - dir_y * arrow_size - perp_y * arrow_size/1.5)   # Left corner
                    ]
            
            # Draw lightning bolt
            if len(points) >= 2:
                pg.draw.lines(self.surface, LIGHTNING_COLOR, False, points, LIGHTNING_WIDTH)
                
                # Draw arrow at the end (triangle)
                if len(points) >= 2 and 'arrow_points' in locals():
                    pg.draw.polygon(self.surface, LIGHTNING_COLOR, arrow_points)
                
                # Add glow effect
                glow_surface = pg.Surface((padded_width, padded_width), pg.SRCALPHA)
                # Draw lines for glow
                for i in range(len(points) - 1):
                    # Draw slightly wider lines for glow
                    pg.draw.line(
                        glow_surface,
                        (*LIGHTNING_COLOR[:3], 100),  # Semi-transparent
                        points[i],
                        points[i + 1],
                        LIGHTNING_WIDTH + 4
                    )
                
                # Also draw arrow glow if we have arrow points
                if 'arrow_points' in locals():
                    pg.draw.polygon(glow_surface, (*LIGHTNING_COLOR[:3], 80), arrow_points)
                    
                # Apply blur to glow
                for _ in range(3):
                    glow_surface = pg.transform.smoothscale(
                        pg.transform.smoothscale(glow_surface, 
                                               (padded_width // 2, padded_width // 2)),
                        (padded_width, padded_width)
                    )
                
                # Add glow behind lightning
                self.surface.blit(glow_surface, (0, 0), special_flags=pg.BLEND_RGBA_ADD)
            
            # Generate particles along the lightning
            for _ in range(2):  # Add a few particles each update
                # Choose a random segment
                if len(points) >= 2:
                    seg_idx = random.randint(0, len(points) - 2)
                    # Position along the segment
                    t = random.random()
                    part_x = points[seg_idx][0] + (points[seg_idx+1][0] - points[seg_idx][0]) * t
                    part_y = points[seg_idx][1] + (points[seg_idx+1][1] - points[seg_idx][1]) * t
                    
                    # Add particle
                    self.particles.append({
                        'x': part_x,
                        'y': part_y,
                        'vx': random.uniform(-1, 1),
                        'vy': random.uniform(-1, 1),
                        'life': random.uniform(0.2, 0.5),
                        'color': LIGHTNING_COLOR,
                        'size': random.uniform(1, 3)
                    })
    
    def update_collision_points(self):
        """Update collision detection points based on current position and angle"""
        # Calculate start and end points of the lightning
        rad_angle = math.radians(self.angle)
        dx = math.cos(rad_angle) * self.height / 2
        dy = math.sin(rad_angle) * self.height / 2
        
        # Line from center outward in both directions
        self.collision_start = (self.x - dx, self.y - dy)
        self.collision_end = (self.x + dx, self.y + dy)
        
    def update(self, dt):
        """Update lightning state"""
        self.time_alive += dt
        
        # Check if warning phase is over
        if self.time_alive >= self.warning_time and not self.is_active:
            self.is_active = True
            
        # Update collision detection if active
        if self.is_active:
            self.update_collision_points()
            
        # Update particles
        for particle in self.particles[:]:
            particle['life'] -= dt
            if particle['life'] <= 0:
                self.particles.remove(particle)
            else:
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                
        # Update the visual representation
        self.update_surface()
        
        # Check if lightning duration is over
        if self.time_alive >= self.warning_time + self.duration:
            return True  # Signal to remove the lightning
        return False
        
    def check_collision(self, player_rect):
        """Check if the lightning is colliding with player"""
        if not self.is_active:
            return False
            
        # Simple line-rect collision
        # We'll use a simplified collision check by sampling points along the lightning line
        steps = 10
        for i in range(steps + 1):
            t = i / steps
            point_x = self.collision_start[0] + (self.collision_end[0] - self.collision_start[0]) * t
            point_y = self.collision_start[1] + (self.collision_end[1] - self.collision_start[1]) * t
            
            # Check if this point is inside player rect
            if player_rect.collidepoint(point_x, point_y):
                return True
                
        return False
        
    def draw(self, surface, camera_offset_x, camera_offset_y):
        """Draw the lightning with camera offset"""
        # Calculate screen position
        screen_x = self.x + camera_offset_x - self.surface.get_width() // 2
        screen_y = self.y + camera_offset_y - self.surface.get_height() // 2
        
        # Draw the lightning
        surface.blit(self.surface, (screen_x, screen_y))
        
        # Draw particles
        for particle in self.particles:
            # Calculate screen position for particle
            part_screen_x = particle['x'] + camera_offset_x
            part_screen_y = particle['y'] + camera_offset_y
            
            # Alpha based on remaining life
            alpha = int(255 * particle['life'] * 2)  # Fade out
            if alpha > 255:
                alpha = 255
                
            # Draw particle
            pg.draw.circle(
                surface,
                (*particle['color'][:3], alpha),
                (int(part_screen_x), int(part_screen_y)),
                int(particle['size'])
            )

class EnhancedBackground:
    """Advanced scrolling background with parallax effect for different level types"""
    def __init__(self, game, level_type="financial"):
        self.game = game
        self.level_type = level_type
        self.parallax_bg = ParallaxBackground(WIDTH * 2, HEIGHT, level_type)
        self.scroll_x = 0
        
        # For market crash background
        self.flash_timer = 0
        self.flash_alpha = 0
        self.lightning_timer = 0
        self.background_lightning = []
        
    def update(self, target_x):
        # Update scroll position based on target (usually the player)
        self.scroll_x = target_x
        
        # Update market crash specific effects
        if self.level_type == "market_crash":
            self.flash_timer += self.game.dt
            
            # Flash effect
            if self.flash_timer > 3 + random.random() * 5:  # Random interval between flashes
                self.flash_timer = 0
                self.flash_alpha = 100
                
                # Add a background lightning bolt
                if random.random() < 0.4:  # 40% chance of lightning with each flash
                    self.add_background_lightning()
            
            # Fade out flash
            if self.flash_alpha > 0:
                self.flash_alpha = max(0, self.flash_alpha - 300 * self.game.dt)
                
            # Update background lightning
            for lightning in self.background_lightning[:]:
                lightning['life'] -= self.game.dt
                if lightning['life'] <= 0:
                    self.background_lightning.remove(lightning)
        
    def add_background_lightning(self):
        """Add a background lightning effect"""
        # Create a random lightning in the background
        start_x = random.randint(0, WIDTH)
        start_y = random.randint(0, HEIGHT // 3)
        segments = random.randint(3, 6)
        points = [(start_x, start_y)]
        
        # Generate zigzag lightning bolt points
        current_x, current_y = start_x, start_y
        for _ in range(segments):
            current_x += random.randint(-60, 60)
            current_y += random.randint(30, 80)
            points.append((current_x, current_y))
            
        self.background_lightning.append({
            'points': points,
            'width': random.randint(2, 5),
            'life': random.uniform(0.1, 0.3),
            'alpha': 200
        })
        
    def draw(self, surface):
        # Draw gradient sky background
        self.draw_gradient_background(surface)
        
        # Draw parallax background
        self.parallax_bg.draw(surface, self.scroll_x)
        
        # Draw market crash specific effects
        if self.level_type == "market_crash":
            # Draw background lightning
            for lightning in self.background_lightning:
                # Calculate alpha based on remaining life
                alpha = int(lightning['alpha'] * (lightning['life'] * 3))
                if alpha > 0:
                    # Create a temporary surface for the lightning
                    lightning_surface = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
                    # Draw the lightning bolt
                    pg.draw.lines(
                        lightning_surface, 
                        (*LIGHTNING_COLOR[:3], alpha), 
                        False, 
                        lightning['points'], 
                        lightning['width']
                    )
                    # Draw glow around the lightning
                    for i in range(3):
                        glow_width = lightning['width'] + i*2
                        glow_alpha = alpha // (i+2)
                        pg.draw.lines(
                            lightning_surface, 
                            (*LIGHTNING_COLOR[:3], glow_alpha), 
                            False, 
                            lightning['points'], 
                            glow_width
                        )
                    # Add the lightning to the background
                    surface.blit(lightning_surface, (0, 0))
            
            # Draw flash effect
            if self.flash_alpha > 0:
                flash_surface = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
                flash_surface.fill((*LIGHTNING_COLOR[:3], int(self.flash_alpha)))
                surface.blit(flash_surface, (0, 0))
        
    def draw_gradient_background(self, surface):
        """Draw a gradient sky background"""
        # Default financial district has a blue-to-dark gradient
        if self.level_type == "financial":
            top_color = (100, 150, 200)  # Light blue
            bottom_color = (50, 80, 100)  # Dark blue
            
            # Create gradient by drawing lines of decreasing color
            for y in range(HEIGHT):
                # Calculate color for this line
                ratio = y / HEIGHT
                r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
                g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
                b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
                
                pg.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))
                
        # Market crash level has a darker, more dramatic gradient with red tint
        elif self.level_type == "market_crash":
            top_color = (80, 30, 50)     # Dark red-purple
            bottom_color = (30, 20, 40)  # Very dark purple
            
            # Create gradient by drawing lines of decreasing color
            for y in range(HEIGHT):
                # Calculate color for this line
                ratio = y / HEIGHT
                r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
                g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
                b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
                
                pg.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))
                
class LevelThumbnail:
    """Thumbnail preview of a level for level selection screen"""
    def __init__(self, level_num, name, image=None):
        self.level_num = level_num
        self.name = name
        self.width = LEVEL_THUMBNAIL_WIDTH
        self.height = LEVEL_THUMBNAIL_HEIGHT
        
        # Create thumbnail surface
        self.image = pg.Surface((self.width, self.height))
        
        if image:
            # Use provided image
            self.image = pg.transform.scale(image, (self.width, self.height))
        else:
            # Create a default thumbnail
            self.create_default_thumbnail()
            
        # Apply shadow effect
        self.image = Shadow.apply(self.image)
        
        # Unlocked state
        self.is_unlocked = True
        self.is_selected = False
        
        # For animation
        self.orig_image = self.image.copy()
        self.hover_scale = 1.0
        
    def create_default_thumbnail(self):
        """Create a default thumbnail if no image is provided"""
        if self.level_num == 1:
            # Prison level thumbnail
            self.image.fill(DARK_GRAY)
            
            # Draw prison bars
            for x in range(20, self.width - 20, 30):
                pg.draw.line(self.image, LIGHT_TEAL, 
                           (x, 20), (x, self.height - 20), 4)
                           
            # Draw "DEBT PRISON" text
            font = pg.font.SysFont(None, 30)
            text = font.render("DEBT PRISON", True, TEAL)
            text_rect = text.get_rect(center=(self.width//2, self.height//2))
            self.image.blit(text, text_rect)
            
        elif self.level_num == 2:
            # Financial district thumbnail
            self.image.fill((50, 80, 100))  # Dark blue
            
            # Draw some simple buildings
            building_colors = BUILDING_COLORS
            for i, color in enumerate(building_colors[:5]):
                x = i * (self.width // 5)
                height = random.randint(self.height // 2, self.height - 30)
                width = self.width // 6
                
                # Draw building
                building_rect = pg.Rect(x, self.height - height, width, height)
                pg.draw.rect(self.image, color, building_rect)
                
                # Draw some windows
                window_color = WINDOW_COLOR
                for wy in range(self.height - height + 10, self.height - 10, 20):
                    for wx in range(x + 5, x + width - 5, 15):
                        window_rect = pg.Rect(wx, wy, 10, 15)
                        pg.draw.rect(self.image, window_color, window_rect)
                        
            # Draw X mark branding
            x_size = 30
            x_pos = self.width // 2
            y_pos = 40
            pg.draw.line(self.image, TEAL, 
                       (x_pos - x_size//2, y_pos - x_size//2),
                       (x_pos + x_size//2, y_pos + x_size//2), 3)
            pg.draw.line(self.image, TEAL, 
                       (x_pos - x_size//2, y_pos + x_size//2),
                       (x_pos + x_size//2, y_pos - x_size//2), 3)
            
            # Text
            font = pg.font.SysFont(None, 26)
            text = font.render("FINANCIAL DISTRICT", True, TEAL)
            text_rect = text.get_rect(center=(self.width//2, self.height - 20))
            self.image.blit(text, text_rect)
            
        elif self.level_num == 3:
            # Market Crash thumbnail
            # Create a dark, volatile-looking background
            self.image.fill((40, 40, 60))  # Dark blue-purple
            
            # Draw stock market crash pattern
            crash_points = []
            x_step = self.width / 10
            
            # Generate zigzag downward pattern
            baseline_y = self.height // 3
            
            for i in range(11):
                x = i * x_step
                if i == 0:
                    y = baseline_y
                elif i % 2 == 0:
                    y = crash_points[-1][1] + random.randint(10, 25)  # Small recovery
                else:
                    y = crash_points[-1][1] + random.randint(20, 45)  # Bigger drop
                
                # Ensure we don't go off the thumbnail
                y = min(y, self.height - 30)
                
                crash_points.append((x, y))
                
            # Draw the crash line
            pg.draw.lines(self.image, LIGHTNING_COLOR, False, crash_points, 3)
            
            # Add some lightning bolt effects
            for _ in range(3):
                # Select random position for lightning
                start_x = random.randint(20, self.width - 20)
                start_y = random.randint(20, baseline_y)
                
                # Create zigzag lightning
                lightning_points = [(start_x, start_y)]
                current_x, current_y = start_x, start_y
                
                for _ in range(4):  # 4 segments
                    current_x += random.randint(-15, 15)
                    current_y += random.randint(15, 30)
                    lightning_points.append((current_x, current_y))
                
                # Draw the lightning
                pg.draw.lines(self.image, LIGHTNING_COLOR, False, lightning_points, 2)
            
            # Text
            font = pg.font.SysFont(None, 30)
            text = font.render("MARKET CRASH", True, LIGHTNING_COLOR)
            text_rect = text.get_rect(center=(self.width//2, self.height - 25))
            self.image.blit(text, text_rect)
            
    def update(self, mouse_pos, mouse_clicked, dt):
        """Update thumbnail based on mouse interaction"""
        # Check if mouse is over the thumbnail
        rect = self.image.get_rect()
        is_hovered = rect.collidepoint(mouse_pos)
        
        # Handle hover animation
        if is_hovered:
            self.hover_scale += (1.05 - self.hover_scale) * 5 * dt
            if mouse_clicked:
                # Handle click - level selection
                return self.level_num
        else:
            self.hover_scale += (1.0 - self.hover_scale) * 5 * dt
            
        # Apply hover scaling
        if self.hover_scale != 1.0:
            scaled_size = (int(self.width * self.hover_scale), 
                          int(self.height * self.hover_scale))
            self.image = pg.transform.smoothscale(self.orig_image, scaled_size)
            
        # Apply selected effect
        if self.is_selected:
            pg.draw.rect(self.image, TEAL, 
                       (0, 0, self.image.get_width(), self.image.get_height()), 
                       4)  # 4px border
                       
        return None
        
    def draw(self, surface, x, y):
        """Draw the thumbnail at the specified position"""
        # Center the image if scaled
        offset_x = (self.image.get_width() - self.width) // 2
        offset_y = (self.image.get_height() - self.height) // 2
        surface.blit(self.image, (x - offset_x, y - offset_y))
        
        # If locked, draw a lock overlay
        if not self.is_unlocked:
            # Semi-transparent overlay
            overlay = pg.Surface((self.width, self.height), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            surface.blit(overlay, (x, y))
            
            # Lock icon
            lock_size = 40
            lock_x = x + (self.width - lock_size) // 2
            lock_y = y + (self.height - lock_size) // 2
            
            # Draw simple lock shape
            pg.draw.rect(surface, GRAY, 
                       (lock_x, lock_y + lock_size//3, lock_size, lock_size*2//3))
            pg.draw.rect(surface, GRAY, 
                       (lock_x + lock_size//4, lock_y, lock_size//2, lock_size//2))
