import pygame as pg
import pymunk
import math
import random
from src.settings import *

class InteractiveObject(pg.sprite.Sprite):
    """Base class for objects that can be interacted with"""
    def __init__(self, game, x, y, width, height, interaction_type="button"):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.interaction_type = interaction_type
        
        # Setup pygame sprite
        self.image = pg.Surface((width, height), pg.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
        # Interactive properties
        self.is_near_player = False
        self.activated = False
        self.can_interact = True
        self.highlight_effect = 0
        self.interaction_prompt = None
        
        # Create prompt text with enhanced visual design
        self.setup_prompt()
        
        # Animation for improved visuals
        self.pulse_animation = 0
        
    def setup_prompt(self):
        """Setup the interaction prompt"""
        font = pg.font.SysFont(None, 24)
        self.interaction_prompt = font.render("Press E to interact", True, WHITE)
        
    def update(self, player=None):
        """Update interactive object state"""
        if player:
            # Check if player is near enough to interact
            dist = math.sqrt((player.rect.centerx - self.rect.centerx)**2 + 
                            (player.rect.centery - self.rect.centery)**2)
            
            self.is_near_player = dist < INTERACTION_DISTANCE
            
        # Update highlight animation
        if self.is_near_player and not self.activated:
            self.highlight_effect = (self.highlight_effect + 0.1) % (2 * math.pi)
        else:
            self.highlight_effect = 0
            
    def interact(self):
        """Handle interaction when player presses E"""
        if self.is_near_player and self.can_interact and not self.activated:
            self.activated = True
            return True
        return False
    
    def draw_interaction_prompt(self, surface, camera_offset_x, camera_offset_y):
        """Draw the interaction prompt when player is near"""
        if self.is_near_player and not self.activated:
            prompt_x = self.rect.centerx + camera_offset_x - self.interaction_prompt.get_width() // 2
            prompt_y = self.rect.top + camera_offset_y - 30
            surface.blit(self.interaction_prompt, (prompt_x, prompt_y))
            
            # Draw highlight effect
            self.draw_highlight(surface, camera_offset_x, camera_offset_y)
    
    def draw_highlight(self, surface, camera_offset_x, camera_offset_y):
        """Draw highlight effect around interactive object"""
        # Create a pulsating highlight thickness
        highlight_width = 2 + int(math.sin(self.highlight_effect) * 2)
        
        # Draw the highlight as a rectangle around the object
        highlight_rect = pg.Rect(
            self.rect.x + camera_offset_x - highlight_width,
            self.rect.y + camera_offset_y - highlight_width,
            self.rect.width + highlight_width * 2,
            self.rect.height + highlight_width * 2
        )
        
        # Use a bright teal color for the highlight
        pg.draw.rect(surface, BRIGHT_TEAL, highlight_rect, highlight_width, border_radius=5)

class Door(InteractiveObject):
    """Interactive door that can be opened once all tokens are collected"""
    def __init__(self, game, x, y, width, height, orientation="vertical", required_tokens=10):
        # Make door bigger (1.5x size)
        enlarged_width = int(width * 1.5)
        enlarged_height = int(height * 1.5)
        
        # Adjust position to keep door's bottom centered
        adjusted_x = x - (enlarged_width - width) // 2
        adjusted_y = y - (enlarged_height - height)
        
        super().__init__(game, adjusted_x, adjusted_y, enlarged_width, enlarged_height, "door")
        
        self.orientation = orientation  # "vertical" or "horizontal"
        self.is_open = False
        self.open_amount = 0  # 0 = closed, 1 = fully open
        self.required_tokens = required_tokens
        self.is_locked = True  # Start locked until required tokens are collected
        
        # Door appearance
        self.door_color = DARK_TEAL
        self.door_border_color = TEAL
        self.lock_color = GOLD
        
        # Lock animation properties
        self.lock_pulse = 0
        self.lock_falling = False
        self.lock_fall_y = 0
        self.lock_fall_speed = 0
        self.lock_rotation = 0
        self.lock_opacity = 255
        
        # Lock dimensions and position
        self.lock_width = self.width // 3
        self.lock_height = self.height // 3
        self.lock_x = (self.width - self.lock_width) // 2
        self.lock_y = (self.height - self.lock_height) // 2
        
        # Glow effect for unlocked door
        self.glow_amount = 0
        
        self.update_appearance()
        
        # Physics body
        self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.body.position = adjusted_x + enlarged_width // 2, adjusted_y + enlarged_height // 2
        self.shape = pymunk.Poly.create_box(self.body, (enlarged_width, enlarged_height))
        self.shape.collision_type = 2  # Same as platforms
        
        # Original position for animations
        self.original_x = adjusted_x
        self.original_y = adjusted_y
        self.target_x = adjusted_x
        self.target_y = adjusted_y
        
        # Door opening animation targets
        if orientation == "vertical":
            # Door slides up
            self.target_y = adjusted_y - enlarged_height
        else:
            # Door slides to the side
            self.target_x = adjusted_x - enlarged_width
    
    def update_appearance(self):
        """Update the door appearance"""
        self.image.fill((0, 0, 0, 0))  # Clear with transparent
        
        # Add glow effect around door if unlocked
        if not self.is_locked and not self.lock_falling:
            # Create a subtle glow effect
            glow_color = (*BRIGHT_TEAL, int(self.glow_amount * 80))
            glow_rect = pg.Rect(-5, -5, self.width + 10, self.height + 10)
            pg.draw.rect(self.image, glow_color, glow_rect, border_radius=10)
            
            # Add more intense inner glow
            inner_glow = (*BRIGHT_TEAL, int(self.glow_amount * 150))
            inner_rect = pg.Rect(-2, -2, self.width + 4, self.height + 4)
            pg.draw.rect(self.image, inner_glow, inner_rect, border_radius=6)
        
        # Draw the door with more detailed design
        door_rect = pg.Rect(0, 0, self.width, self.height)
        pg.draw.rect(self.image, self.door_color, door_rect, border_radius=8)
        pg.draw.rect(self.image, self.door_border_color, door_rect, width=3, border_radius=8)
        
        # Add X pattern to door design
        x_size = min(self.width, self.height) // 2
        pg.draw.line(self.image, self.door_border_color, 
                   (self.width//2-x_size//2, self.height//2-x_size//2),
                   (self.width//2+x_size//2, self.height//2+x_size//2), 2)
        pg.draw.line(self.image, self.door_border_color, 
                   (self.width//2-x_size//2, self.height//2+x_size//2),
                   (self.width//2+x_size//2, self.height//2-x_size//2), 2)
        
        # Add detailed bars/panels to door
        if self.orientation == "vertical":
            # Add horizontal bars for a prison cell door look
            for i in range(1, 7):
                y_pos = i * self.height // 7
                pg.draw.line(self.image, self.door_border_color, 
                           (5, y_pos), (self.width - 5, y_pos), 2)
                           
            # Add small vertical supports
            for i in range(1, 4):
                x_pos = i * self.width // 4
                pg.draw.line(self.image, self.door_border_color,
                           (x_pos, 10), (x_pos, self.height - 10), 2)
        else:
            # Add vertical bars for a prison cell door look
            for i in range(1, 7):
                x_pos = i * self.width // 7
                pg.draw.line(self.image, self.door_border_color, 
                           (x_pos, 5), (x_pos, self.height - 5), 2)
                           
            # Add small horizontal supports
            for i in range(1, 4):
                y_pos = i * self.height // 4
                pg.draw.line(self.image, self.door_border_color,
                           (10, y_pos), (self.width - 10, y_pos), 2)
        
        # Add lock if door is locked (only drawn on main surface if not falling)
        if self.is_locked and not self.lock_falling:
            self._draw_lock_on_surface(self.image, self.lock_x, self.lock_y)
    
    def _draw_lock_on_surface(self, surface, x, y):
        """Draw the lock on the given surface"""
        # Lock body
        lock_width = self.width // 4
        lock_height = self.height // 4
        lock_rect = pg.Rect(x, y, lock_width, lock_height)
        pg.draw.rect(surface, self.lock_color, lock_rect, border_radius=5)
        
        # Lock shackle
        shackle_width = lock_width // 2
        shackle_height = lock_height // 2
        shackle_x = x + (lock_width - shackle_width) // 2
        shackle_y = y - shackle_height // 2
        
        pg.draw.rect(
            surface, 
            self.lock_color, 
            (shackle_x, shackle_y, shackle_width, shackle_height),
            border_radius=4
        )
        
        # Add a keyhole
        keyhole_radius = lock_width // 6
        keyhole_x = x + lock_width // 2
        keyhole_y = y + lock_height // 2
        pg.draw.circle(surface, DARK_TEAL, (keyhole_x, keyhole_y), keyhole_radius)
        
        # Add "X" token counter
        lock_font = pg.font.SysFont(None, max(14, self.width // 8))
        tokens_text = f"X{self.required_tokens}"
        text_surf = lock_font.render(tokens_text, True, DARK_TEAL)
        text_rect = text_surf.get_rect(center=(x + lock_width // 2, y - shackle_height - 5))
        surface.blit(text_surf, text_rect)
    
    def update(self, player=None):
        """Update door state and animation"""
        super().update(player)
        
        # Update lock pulse animation
        if self.is_locked:
            self.lock_pulse = (self.lock_pulse + 0.05) % (2 * math.pi)
        
        # Update glow effect for unlocked doors
        if not self.is_locked and not self.is_open:
            self.glow_amount = 0.5 + 0.5 * math.sin(pg.time.get_ticks() / 200)
        
        # Check if we have enough tokens to unlock
        if self.is_locked and player and player.tokens_collected >= self.required_tokens:
            self.is_locked = False
            self.can_interact = True
            
            # Start lock falling animation
            self.lock_falling = True
            self.lock_fall_y = self.height // 2  # Start position
            self.lock_fall_speed = 0  # Initial falling speed
            
            # Add unlock particle effect
            if hasattr(self.game, 'token_particles'):
                self.game.token_particles.spawn_particles(
                    (self.rect.centerx + self.game.camera_offset_x, 
                     self.rect.centery + self.game.camera_offset_y),
                    25,  # More particles
                    spread=80
                )
        
        # Update falling lock animation
        if self.lock_falling:
            self.lock_fall_speed += 600 * self.game.dt  # Accelerate
            self.lock_fall_y += self.lock_fall_speed * self.game.dt
            self.lock_rotation += 250 * self.game.dt
            
            # Fade out as it falls
            if self.lock_fall_y > HEIGHT:
                self.lock_falling = False
            else:
                # Reduce opacity as it falls
                self.lock_opacity = max(0, 255 - (self.lock_fall_y / HEIGHT) * 255)
        
        # Handle door opening animation
        if self.activated and self.open_amount < 1.0:
            self.open_amount += DOOR_OPEN_SPEED * self.game.dt
            if self.open_amount > 1.0:
                self.open_amount = 1.0
                self.is_open = True
                
            # Calculate current position based on animation progress
            current_x = self.original_x + (self.target_x - self.original_x) * self.open_amount
            current_y = self.original_y + (self.target_y - self.original_y) * self.open_amount
            
            # Update physics body and sprite position
            self.body.position = current_x + self.width // 2, current_y + self.height // 2
            self.rect.topleft = (current_x, current_y)
        
        # Update appearance based on locked state
        if self.is_locked != getattr(self, '_prev_locked_state', None) or self.glow_amount > 0:
            self.update_appearance()
            self._prev_locked_state = self.is_locked
    
    def interact(self):
        """Open the door when player interacts with it"""
        # Don't allow interaction if door is locked
        if self.is_locked:
            # Display a message that more tokens are needed
            if hasattr(self.game, 'token_particles'):
                # More particles with red tint for "still locked" feedback
                self.game.token_particles.spawn_particles(
                    (self.rect.centerx + self.game.camera_offset_x, 
                     self.rect.centery + self.game.camera_offset_y),
                    10,
                    spread=40,
                    color=(255, 80, 80)  # Reddish color to indicate locked
                )
            
            # Display tokens needed if player is near
            if self.is_near_player:
                tokens_needed = self.required_tokens - self.game.player.tokens_collected
                locked_text = f"Need {tokens_needed} more X tokens"
                
                # Player feedback about locked door through sound
                if hasattr(self.game, 'sound_manager'):
                    self.game.sound_manager.play_menu_hover()  # Use hover sound for locked feedback
            
            return False
            
        if super().interact():
            # Trigger the door opening animation
            self.can_interact = False  # Prevent multiple interactions
            
            # Create an intense particle burst when opening
            if hasattr(self.game, 'token_particles'):
                for i in range(3):  # Multiple bursts
                    offset_x = random.randint(-30, 30)
                    offset_y = random.randint(-30, 30)
                    color = random.choice([BRIGHT_TEAL, GOLD, LIGHT_TEAL])
                    
                    self.game.token_particles.spawn_particles(
                        (self.rect.centerx + self.game.camera_offset_x + offset_x, 
                         self.rect.centery + self.game.camera_offset_y + offset_y),
                        15,
                        spread=50,
                        color=color
                    )
            
            # Add camera shake effect when door opens
            if hasattr(self.game, 'camera_shake'):
                self.game.camera_shake(intensity=7.0, duration=0.4)
                
            # Play door open sound
            if hasattr(self.game, 'sound_manager'):
                self.game.sound_manager.play_door_open()
                
            return True
        return False
        
    def draw(self, surface, camera_offset_x, camera_offset_y):
        """Custom draw method that handles the falling lock animation"""
        # First draw the door itself using the normal blit
        surface.blit(self.image, (self.rect.x + camera_offset_x, self.rect.y + camera_offset_y))
        
        # Draw falling lock if needed
        if self.lock_falling:
            # Create a temporary surface for the lock
            lock_width = self.width // 4
            lock_height = self.height // 4
            lock_surface = pg.Surface((lock_width * 2, lock_height * 2), pg.SRCALPHA)
            
            # Draw the lock on this surface
            self._draw_lock_on_surface(lock_surface, lock_width // 2, lock_height // 2)
            
            # Rotate the lock
            rotated_lock = pg.transform.rotate(lock_surface, self.lock_rotation)
            
            # Calculate position of the falling lock
            lock_x = self.rect.x + camera_offset_x + self.width // 2 - rotated_lock.get_width() // 2
            lock_y = self.rect.y + camera_offset_y + self.lock_fall_y - rotated_lock.get_height() // 2
            
            # Apply fading effect
            rotated_lock.set_alpha(int(self.lock_opacity))
            
            # Draw falling lock
            surface.blit(rotated_lock, (lock_x, lock_y))
            
            # Add particle trail behind falling lock
            if hasattr(self.game, 'token_particles') and self.game.dt * self.game.frame_count % 0.1 < 0.03:
                self.game.token_particles.spawn_particles(
                    (lock_x + rotated_lock.get_width() // 2, 
                     lock_y + rotated_lock.get_height() // 2),
                    2,
                    spread=10
                )
    
    def draw_interaction_prompt(self, surface, camera_offset_x, camera_offset_y):
        """Draw the interaction prompt when player is near"""
        if self.is_near_player:
            if self.is_locked:
                # Create "Need X tokens" prompt for locked doors
                tokens_needed = self.required_tokens - self.game.player.tokens_collected
                if tokens_needed > 0:
                    font = pg.font.SysFont(None, 24)
                    prompt_text = f"Need {tokens_needed} more X tokens"
                    prompt = font.render(prompt_text, True, self.lock_color)
                    prompt_x = self.rect.centerx + camera_offset_x - prompt.get_width() // 2
                    prompt_y = self.rect.top + camera_offset_y - 30
                    surface.blit(prompt, (prompt_x, prompt_y))
                    
                    # Draw a lock icon with pulsing effect
                    lock_size = 15
                    lock_x = self.rect.centerx + camera_offset_x
                    lock_y = self.rect.top + camera_offset_y - 50
                    lock_pulse = 1.0 + 0.2 * math.sin(self.lock_pulse * 2)
                    
                    # Lock body
                    lock_rect = pg.Rect(
                        lock_x - (lock_size // 2) * lock_pulse,
                        lock_y,
                        lock_size * lock_pulse,
                        lock_size * 1.2 * lock_pulse
                    )
                    pg.draw.rect(surface, self.lock_color, lock_rect, border_radius=2)
                    
                    # Lock shackle
                    shackle_width = lock_size // 2
                    shackle_height = lock_size // 2
                    shackle_x = lock_x - (shackle_width // 2) * lock_pulse
                    shackle_y = lock_y - (shackle_height // 2) * lock_pulse
                    
                    pg.draw.rect(
                        surface, 
                        self.lock_color, 
                        (shackle_x, shackle_y, shackle_width * lock_pulse, shackle_height * lock_pulse),
                        border_radius=2
                    )
            else:
                # Draw normal interaction prompt for unlocked doors
                prompt_x = self.rect.centerx + camera_offset_x - self.interaction_prompt.get_width() // 2
                prompt_y = self.rect.top + camera_offset_y - 30
                surface.blit(self.interaction_prompt, (prompt_x, prompt_y))
            
            # Draw highlight effect
            self.draw_highlight(surface, camera_offset_x, camera_offset_y)
