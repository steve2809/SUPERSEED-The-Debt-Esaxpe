import pygame as pg
import pymunk
import random
import math
from src.settings import *
from src.sprites import Platform, SuperseedToken
from src.interactive import Door
from src.ui import ParticleSystem, Panel, Button

class BaseLevel:
    """Base class for all game levels with common functionality"""
    def __init__(self, game):
        self.game = game
        
        # Level data
        self.width = 0
        self.height = 0
        self.start_x = 100
        self.start_y = HEIGHT - 200
        
        # Sprite groups
        self.platforms = pg.sprite.Group()
        self.tokens = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.interactive_objects = pg.sprite.Group()
        
        # Define token types for variety in the level
        self.token_types = ["x_token", "star_token", "coin_token", "gem_token", "logo_token"]
        
        # Level state
        self.level_complete = False
        self.completion_time = 0
        self.completion_animation_progress = 0
        self.player_died = False
        self.death_animation_time = 0
        self.death_cause = "fall"  # Default death cause
        
        # Spawn protection
        self.level_start_time = 0
        self.spawn_protection_time = 1.0  # Default value
        
        # Completion animation
        self.completion_particles = ParticleSystem("x_mark", 150)
        self.celebration_text = None
        self.celebration_font = pg.font.SysFont(None, 72)
        
        # Death animation
        self.death_particles = ParticleSystem("circle", DEATH_PARTICLES_COUNT)
        self.death_text = None
        self.death_font = pg.font.SysFont(None, 72)
        
        # Set up the level
        self.setup_level()
        
    def setup_level(self):
        """Override this method in subclasses to set up the specific level"""
        # Default implementation creates a simple test level
        self.width = WIDTH * 2
        self.height = HEIGHT
        self.death_height = HEIGHT + 50
        
        # Set default player start position
        self.start_x = 100
        self.start_y = HEIGHT - 200
        
        # Create a simple platform
        self.add_platform(50, HEIGHT - 100, 300, 20)
        
        # Add a few tokens
        self.add_token(200, HEIGHT - 150)
        self.add_token(400, HEIGHT - 200)
        
        # Add boundary walls
        self.add_boundary_walls()
        
    def add_platform(self, x, y, width, height, platform_type="standard", moving=False, move_distance=0, move_speed=PLATFORM_SPEED):
        """Helper method to add a platform to the level"""
        platform = Platform(self.game, x, y, width, height, platform_type)
        
        # Set up movement if specified
        if moving:
            platform.setup_movement(move_speed, move_distance)
            
        # Add to sprite group and physics space
        self.platforms.add(platform)
        self.game.space.add(platform.body, platform.shape)
        
        return platform
        
    def add_token(self, x, y, token_type=None):
        """Helper method to add a token to the level"""
        # If no token type specified, choose a random one
        if token_type is None:
            token_type = self.token_types[random.randint(0, len(self.token_types)-1)]
            
        # Create token
        token = SuperseedToken(self.game, x, y, token_type=token_type)
        self.tokens.add(token)
        self.game.space.add(token.body, token.shape)
        
        return token
        
    def add_exit_door(self, x, y, tokens_required=LEVEL_DOOR_TOKENS_REQUIRED):
        """Helper method to add an exit door"""
        door_width = 80
        door_height = 120
        
        # Create door
        exit_door = Door(self.game, x, y, door_width, door_height, "vertical", tokens_required)
        self.interactive_objects.add(exit_door)
        self.game.space.add(exit_door.body, exit_door.shape)
        
        return exit_door
        
    def add_boundary_walls(self):
        """Add invisible walls at the edges of the level"""
        left_wall = Platform(self.game, -10, 0, 10, HEIGHT)
        right_wall = Platform(self.game, self.width, 0, 10, HEIGHT)
        self.platforms.add(left_wall, right_wall)
        self.game.space.add(left_wall.body, left_wall.shape)
        self.game.space.add(right_wall.body, right_wall.shape)
    
    def update(self):
        """Update all level elements"""
        self.platforms.update()
        self.tokens.update()
        self.enemies.update()
        
        # Update interactive objects with player position
        for obj in self.interactive_objects:
            obj.update(self.game.player)
            
        # Update level completion animation
        if self.level_complete:
            self.update_completion_animation()
            
        # Check for player death (fell off platforms)
        if self.check_player_died():
            self.update_death_animation()
            
    def check_player_died(self):
        """Check if player has fallen off the platforms"""
        if self.player_died:
            return True
            
        # Check if spawn protection is active
        current_time = self.game.dt * self.game.frame_count
        player_has_moved = False
        if hasattr(self.game, 'player'):
            # Check if player has moved from starting position
            dx = abs(self.game.player.rect.x - self.start_x)
            dy = abs(self.game.player.rect.y - self.start_y)
            player_has_moved = dx > 10 or dy > 10
            
        # Only apply spawn protection if player hasn't moved yet
        if current_time - self.level_start_time < self.spawn_protection_time and not player_has_moved:
            return False
            
        # Check if player has fallen below death height
        if hasattr(self, 'death_height') and self.game.player.rect.top > self.death_height:
            self.start_death_animation("fall")
            return True
            
        # Check if player has gone off the sides of the level
        if self.game.player.rect.right < LEVEL_EDGE_BUFFER or self.game.player.rect.left > self.width - LEVEL_EDGE_BUFFER:
            self.start_death_animation("boundary")
            return True
            
        return False
            
    def start_death_animation(self, death_type="fall"):
        """Start death animation when player dies"""
        if not self.player_died:
            self.player_died = True
            self.death_animation_time = 0
            self.death_cause = death_type
            
            # Set death text based on death type
            if death_type == "fall":
                self.death_text = self.death_font.render("You Fell!", True, (255, 50, 50))
            elif death_type == "boundary":
                self.death_text = self.death_font.render("Out of Bounds!", True, (255, 80, 80))
            else:
                self.death_text = self.death_font.render("You Died!", True, (255, 50, 50))
            
            # Play death sound
            if hasattr(self.game, 'sound_manager'):
                self.game.sound_manager.play_death()
            
            # Apply screen shake effect
            if hasattr(self.game, 'camera_shake'):
                self.game.camera_shake(DEATH_SHAKE_INTENSITY, DEATH_SHAKE_DURATION)
            
            # Spawn particles at player position with color based on death type
            player_screen_pos = (
                self.game.player.rect.centerx + self.game.camera_offset_x,
                self.game.player.rect.centery + self.game.camera_offset_y
            )
            
            # Different particle effects for different death types
            if death_type == "boundary":
                # Red warning particles for boundary death
                self.death_particles.spawn_particles(
                    player_screen_pos, 
                    DEATH_PARTICLES_COUNT, 
                    spread=100,
                    color=(255, 50, 50)
                )
            else:
                # Standard death particles
                self.death_particles.spawn_particles(
                    player_screen_pos, 
                    DEATH_PARTICLES_COUNT, 
                    spread=80
                )
            
    def update_death_animation(self):
        """Update death animation"""
        dt = self.game.dt
        self.death_animation_time += dt
        
        # Update particles
        self.death_particles.update(dt)
        
        # After 1.5 seconds, restart the level
        if self.death_animation_time > LEVEL_RESPAWN_DELAY:
            self.game.restart_level()
            
    def update_completion_animation(self):
        """Update the level completion animation"""
        dt = self.game.dt
        self.completion_time += dt
        self.completion_animation_progress = min(1.0, self.completion_time / 5.0)  # Extended to 5 seconds
        
        # Update particles
        self.completion_particles.update(dt)
        
        # Create confetti effect - more intense at the beginning
        if self.completion_time < 3.0:
            # Determine intensity based on time
            if self.completion_time < 1.0:
                intensity = 1.0  # Full intensity in first second
            else:
                intensity = max(0.2, 1.0 - (self.completion_time - 1.0) / 2.0)  # Gradually reduce
                
            # More frequent particle bursts at higher intensity
            if random.random() < 0.3 * intensity:
                # Create confetti around the entire screen
                for _ in range(3):
                    # Randomly position confetti across the visible area
                    pos_x = random.randint(0, WIDTH)
                    pos_y = random.randint(0, HEIGHT // 2)
                    
                    # Random color from confetti colors
                    color = random.choice(CONFETTI_COLORS)
                    
                    # Spawn confetti particles
                    self.completion_particles.spawn_particles(
                        (pos_x, pos_y), 
                        8, 
                        spread=50,
                        color=color
                    )
            
            # Special burst around player at beginning
            if self.completion_time < 0.5 and random.random() < 0.4:
                # Create celebration burst around player
                angle = random.uniform(0, 2 * math.pi)
                dist = random.uniform(30, 150)
                pos_x = self.game.player.rect.centerx + math.cos(angle) * dist
                pos_y = self.game.player.rect.centery + math.sin(angle) * dist
                
                # Spawn particles at this position
                self.completion_particles.spawn_particles(
                    (pos_x + self.game.camera_offset_x, pos_y + self.game.camera_offset_y), 
                    10, 
                    spread=40,
                    color=random.choice(CONFETTI_COLORS)
                )
        
        # Create completion menu after 5 seconds
        if self.completion_time >= 5.0 and not hasattr(self, 'completion_menu_created'):
            self.completion_menu_created = True
            self.create_completion_menu()
            
    def create_completion_menu(self):
        """Create the level completion menu"""
        # Create panel for completion menu
        self.completion_menu_panel = Panel(
            WIDTH // 2 - 200, 
            HEIGHT // 2 - 100, 
            400, 
            200
        )
        
        # Create menu buttons
        button_y = HEIGHT // 2 + 30
        
        # Next Level button
        self.next_level_button = Button(
            WIDTH // 2 - 150, 
            button_y, 
            300, 
            BUTTON_HEIGHT, 
            "Next Level", 
            action=lambda: "next_level"
        )
        
        # Main Menu button
        self.main_menu_button = Button(
            WIDTH // 2 - 150, 
            button_y + BUTTON_HEIGHT + BUTTON_SPACING, 
            300, 
            BUTTON_HEIGHT, 
            "Main Menu", 
            action=lambda: "main_menu"
        )
            
    def check_level_complete(self):
        """Check if the level is complete (player reached and opened door)"""
        # Check if any doors in the level are open
        for obj in self.interactive_objects:
            if isinstance(obj, Door) and obj.is_open and not self.level_complete:
                # Play a door open sound if we have one
                if hasattr(self.game, 'sound_manager') and hasattr(self.game.sound_manager, 'play_door_open'):
                    self.game.sound_manager.play_door_open()
                
                self.start_completion_animation()
                return True
        return False
        
    def start_completion_animation(self):
        """Start the level completion animation"""
        self.level_complete = True
        self.completion_time = 0
        
        # Set celebration texts
        self.celebration_text = self.celebration_font.render("Level Complete!", True, BRIGHT_TEAL)
        
        # Create "You're now debt free!" message
        self.debt_free_text = self.celebration_font.render("You're now debt free!", True, GOLD)
        
        # Spawn initial burst of particles at player position
        player_screen_pos = (
            self.game.player.rect.centerx + self.game.camera_offset_x,
            self.game.player.rect.centery + self.game.camera_offset_y
        )
        self.completion_particles.spawn_particles(player_screen_pos, 40, spread=100)
        
    def draw(self, surface):
        """Draw all level elements to the surface"""
        # Draw level completion elements
        if self.level_complete:
            self.draw_completion_effects(surface)
            
        # Draw death animation
        if self.player_died:
            self.draw_death_effects(surface)
            
    def draw_death_effects(self, surface):
        """Draw death animation effects"""
        # Draw particles
        self.death_particles.draw(surface)
        
        # Draw death text with a pulsing effect
        if self.death_text and self.death_animation_time > 0.3:
            # Calculate pulsing scale based on time
            pulse = 1.0 + (DEATH_TEXT_SCALE - 1.0) * math.sin(self.death_animation_time * 8)
            scaled_width = int(self.death_text.get_width() * pulse)
            scaled_height = int(self.death_text.get_height() * pulse)
            
            # Scale the text
            scaled_text = pg.transform.scale(
                self.death_text, 
                (scaled_width, scaled_height)
            )
            
            # Draw with center position
            text_x = WIDTH // 2 - scaled_width // 2
            text_y = HEIGHT // 3 - scaled_height // 2
            surface.blit(scaled_text, (text_x, text_y))
            
    def draw_completion_effects(self, surface):
        """Draw level completion celebration effects"""
        # Draw particles
        self.completion_particles.draw(surface)
        
        # First 5 seconds - animate celebration texts
        if self.completion_time < 5.0:
            # Draw "Level Complete!" text with a pulsing effect
            if self.celebration_text and self.completion_time > 0.5:
                # Calculate pulsing scale based on time
                pulse = 1.0 + 0.1 * math.sin(self.completion_time * 5)
                scaled_width = int(self.celebration_text.get_width() * pulse)
                scaled_height = int(self.celebration_text.get_height() * pulse)
                
                # Scale the text
                scaled_text = pg.transform.scale(
                    self.celebration_text, 
                    (scaled_width, scaled_height)
                )
                
                # Draw with center position
                text_x = WIDTH // 2 - scaled_width // 2
                text_y = HEIGHT // 3 - scaled_height // 2
                surface.blit(scaled_text, (text_x, text_y))
                
            # Draw "You're now debt free!" text after 1.5 seconds
            if hasattr(self, 'debt_free_text') and self.completion_time > 1.5:
                # Fade in effect
                alpha = min(255, int((self.completion_time - 1.5) * 200))
                debt_free_surf = self.debt_free_text.copy()
                debt_free_surf.set_alpha(alpha)
                
                # Also add a slight pulsing effect, opposite phase from "Level Complete!"
                pulse = 1.0 + 0.08 * math.sin(self.completion_time * 5 + math.pi)
                scaled_width = int(debt_free_surf.get_width() * pulse)
                scaled_height = int(debt_free_surf.get_height() * pulse)
                
                # Scale the text
                scaled_text = pg.transform.scale(
                    debt_free_surf, 
                    (scaled_width, scaled_height)
                )
                
                # Position below the "Level Complete!" text
                text_x = WIDTH // 2 - scaled_width // 2
                text_y = HEIGHT // 2 - scaled_height // 2
                surface.blit(scaled_text, (text_x, text_y))
        
        # After 5 seconds - show completion menu
        else:
            # Draw the menu panel
            if hasattr(self, 'completion_menu_panel'):
                self.completion_menu_panel.draw(surface)
                
                # Draw title text
                title_font = pg.font.SysFont(None, 40)
                title_text = title_font.render("Level Completed!", True, BRIGHT_TEAL)
                title_x = WIDTH // 2 - title_text.get_width() // 2
                title_y = HEIGHT // 2 - 70
                surface.blit(title_text, (title_x, title_y))
                
                # Draw menu buttons
                if hasattr(self, 'next_level_button'):
                    mouse_pos = pg.mouse.get_pos()
                    
                    # Update and draw the next level button
                    self.next_level_button.update(mouse_pos, self.game.dt)
                    self.next_level_button.draw(surface)
                    
                    # Update and draw the main menu button
                    self.main_menu_button.update(mouse_pos, self.game.dt)
                    self.main_menu_button.draw(surface)
            
    def draw_interactive_prompts(self, surface, camera_offset_x, camera_offset_y):
        """Draw interaction prompts for nearby interactive objects"""
        for obj in self.interactive_objects:
            obj.draw_interaction_prompt(surface, camera_offset_x, camera_offset_y)
