import pygame as pg
import pymunk
import pymunk.pygame_util
import sys
import random
import time
import math
from src.settings import *
from src.sprites import EnhancedBackground
from src.entities.player import Player
from src.levels import get_level
from src.ui import FadeEffect, ParticleSystem, AnimatedText, lighten_color, darken_color
from src.menu import StartMenu, PauseMenu, ControlsScreen, CreditsScreen, LevelSelectScreen
from src.effects import Shadow
from src.sound_manager import SoundManager

class Game:
    def __init__(self):
        # Initialize pygame
        pg.init()
        pg.display.set_caption(TITLE)
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()
        
        # Set up pymunk physics
        self.space = pymunk.Space()
        self.space.gravity = (0, GRAVITY)
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        
        # Game objects
        self.all_sprites = pg.sprite.Group()
        self.current_level = None
        self.player = None
        self.camera_offset_x = 0
        self.camera_offset_y = 0
        self.target_camera_x = 0  # For smooth camera following
        self.target_camera_y = 0
        
        # Camera shake variables
        self.shake_time = 0
        self.shake_intensity = 0
        self.shake_duration = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        
        # Performance tracking
        self.frame_count = 0
        self.dt = 0
        
        # Game state
        self.running = True
        self.playing = False
        self.paused = False
        self.level_num = 2  # Start with Financial District as default
        self.game_over = False
        self.debug = False
        self.game_state = STATE_MENU
        self.prev_state = None
        self.transition_effect = FadeEffect(0.5)
        
        # Post-processing effects
        self.post_processing_enabled = True
        self.vignette_surface = None  # Pre-calculated vignette (for optimization)
        self._generate_vignette()
        
        # Initialize sound manager
        self.sound_manager = SoundManager(self)
        
        # Setup collision handlers
        self.setup_collisions()
        
        # Create menus
        self.start_menu = StartMenu(self)
        self.pause_menu = PauseMenu(self)
        self.controls_screen = ControlsScreen(self)
        self.credits_screen = CreditsScreen(self)
        self.level_select_screen = LevelSelectScreen(self)
        self.current_menu = self.start_menu
        
        # Font for UI
        self.font = pg.font.SysFont(None, 36)
        
        # Particle effects
        self.token_particles = ParticleSystem("circle", 30)
        
        # Setup character previews for main menu
        self._setup_menu_previews()
        
        # Activate the start menu
        self.start_menu.activate()
        
    def _setup_menu_previews(self):
        """Create character preview images for the menu display"""
        # Create larger versions of the character sprites for menu display
        preview_scale = 3.5  # Slightly larger for more detail
        preview_width = PLAYER_WIDTH * preview_scale
        preview_height = PLAYER_HEIGHT * preview_scale
        shadow_offset = 8  # For drop shadow
        
        # Create surfaces with extra space for shadow
        prisoner_preview = pg.Surface((preview_width + shadow_offset, preview_height + shadow_offset), pg.SRCALPHA)
        wizard_preview = pg.Surface((preview_width + shadow_offset, preview_height + shadow_offset), pg.SRCALPHA)
        
        # PRISONER CHARACTER
        # Body (blue jumpsuit)
        prisoner_body = pg.Rect(
            shadow_offset // 2 + 10 * preview_scale, 
            shadow_offset // 2 + 20 * preview_scale, 
            (preview_width - 20 * preview_scale), 
            (preview_height - 30 * preview_scale)
        )
        pg.draw.ellipse(prisoner_preview, BLUE_PRISONER, prisoner_body)
        
        # Highlight on jumpsuit
        highlight_rect = pg.Rect(
            prisoner_body.x + prisoner_body.width // 4,
            prisoner_body.y + prisoner_body.height // 6,
            prisoner_body.width // 4,
            prisoner_body.height // 4
        )
        pg.draw.ellipse(prisoner_preview, lighten_color(BLUE_PRISONER), highlight_rect)
        
        # Face (teal colored)
        face_rect = pg.Rect(
            shadow_offset // 2 + 15 * preview_scale, 
            shadow_offset // 2 + 10 * preview_scale,
            (preview_width - 30 * preview_scale),
            (preview_height // 2 - 15 * preview_scale)
        )
        pg.draw.ellipse(prisoner_preview, TEAL, face_rect)
        
        # Eyes (simple expression)
        eye_size = 5 * preview_scale
        eye_y = shadow_offset // 2 + 25 * preview_scale
        
        # Left eye
        left_eye_x = shadow_offset // 2 + 25 * preview_scale
        pg.draw.circle(prisoner_preview, WHITE, (left_eye_x, eye_y), eye_size)
        pg.draw.circle(prisoner_preview, BLACK, (left_eye_x, eye_y), eye_size // 2)
        
        # Right eye
        right_eye_x = shadow_offset // 2 + preview_width - 25 * preview_scale
        pg.draw.circle(prisoner_preview, WHITE, (right_eye_x, eye_y), eye_size)
        pg.draw.circle(prisoner_preview, BLACK, (right_eye_x, eye_y), eye_size // 2)
        
        # Mouth (slightly sad expression)
        mouth_width = 20 * preview_scale
        mouth_y = shadow_offset // 2 + 40 * preview_scale
        mouth_x_start = shadow_offset // 2 + (preview_width - mouth_width) // 2
        pg.draw.arc(
            prisoner_preview, 
            darken_color(TEAL), 
            (mouth_x_start, mouth_y, mouth_width, 12 * preview_scale),
            0.2, 2.9, 3
        )
        
        # No prisoner number - cleaner design
        
        # WIZARD CHARACTER
        # Body (teal robe)
        wizard_body = pg.Rect(
            shadow_offset // 2 + 10 * preview_scale, 
            shadow_offset // 2 + 25 * preview_scale, 
            (preview_width - 20 * preview_scale), 
            (preview_height - 35 * preview_scale)
        )
        pg.draw.ellipse(wizard_preview, TEAL, wizard_body)
        
        # Highlight on robe
        highlight_rect = pg.Rect(
            wizard_body.x + wizard_body.width // 4,
            wizard_body.y + wizard_body.height // 6,
            wizard_body.width // 4,
            wizard_body.height // 4
        )
        pg.draw.ellipse(wizard_preview, lighten_color(TEAL), highlight_rect)
        
        # Face
        face_rect = pg.Rect(
            shadow_offset // 2 + 15 * preview_scale, 
            shadow_offset // 2 + 15 * preview_scale,
            (preview_width - 30 * preview_scale),
            (preview_height // 2 - 20 * preview_scale)
        )
        pg.draw.ellipse(wizard_preview, LIGHT_TEAL, face_rect)
        
        # Wizard hat (triangular with more detail)
        hat_width = preview_width - 20 * preview_scale
        hat_height = 35 * preview_scale
        hat_points = [
            (shadow_offset // 2 + preview_width // 2, shadow_offset // 2),  # Tip
            (shadow_offset // 2 + 10 * preview_scale, shadow_offset // 2 + hat_height),  # Left bottom
            (shadow_offset // 2 + preview_width - 10 * preview_scale, shadow_offset // 2 + hat_height)  # Right bottom
        ]
        
        # Hat base
        pg.draw.polygon(wizard_preview, darken_color(TEAL), hat_points)
        
        # Hat brim (semicircle)
        brim_rect = pg.Rect(
            shadow_offset // 2 + 5 * preview_scale,
            shadow_offset // 2 + hat_height - 5,
            preview_width - 10 * preview_scale,
            10 * preview_scale
        )
        pg.draw.ellipse(wizard_preview, LIGHT_TEAL, brim_rect)
        
        # Eyes (wise expression)
        eye_size = 5 * preview_scale
        eye_y = shadow_offset // 2 + 30 * preview_scale
        
        # Left eye
        left_eye_x = shadow_offset // 2 + 25 * preview_scale
        pg.draw.circle(wizard_preview, WHITE, (left_eye_x, eye_y), eye_size)
        pg.draw.circle(wizard_preview, BLACK, (left_eye_x, eye_y), eye_size // 2)
        
        # Right eye
        right_eye_x = shadow_offset // 2 + preview_width - 25 * preview_scale
        pg.draw.circle(wizard_preview, WHITE, (right_eye_x, eye_y), eye_size)
        pg.draw.circle(wizard_preview, BLACK, (right_eye_x, eye_y), eye_size // 2)
        
        # Beard (simple white lines)
        beard_start_y = shadow_offset // 2 + 40 * preview_scale
        beard_length = 15 * preview_scale
        beard_center_x = shadow_offset // 2 + preview_width // 2
        for i in range(-10, 11, 2):
            pg.draw.line(
                wizard_preview,
                WHITE,
                (beard_center_x + i * preview_scale, beard_start_y),
                (beard_center_x + i * preview_scale * 1.5, beard_start_y + beard_length),
                2
            )
            
        # X marks on hat and robe
        x_size = 10 * preview_scale
        
        # Hat X - more prominent
        pg.draw.line(
            wizard_preview, 
            BLACK, 
            (shadow_offset // 2 + preview_width // 2 - x_size//2, shadow_offset // 2 + 15 * preview_scale - x_size//2),
            (shadow_offset // 2 + preview_width // 2 + x_size//2, shadow_offset // 2 + 15 * preview_scale + x_size//2), 
            3
        )
        pg.draw.line(
            wizard_preview, 
            BLACK, 
            (shadow_offset // 2 + preview_width // 2 - x_size//2, shadow_offset // 2 + 15 * preview_scale + x_size//2),
            (shadow_offset // 2 + preview_width // 2 + x_size//2, shadow_offset // 2 + 15 * preview_scale - x_size//2), 
            3
        )
        
        # Robe X marks (scattered across robe)
        for i in range(5):  # Add more X marks
            y_pos = (55 + i * 15) * preview_scale
            x_pos = (10 + (i % 3) * 25) * preview_scale
            
            # Left side X
            pg.draw.line(
                wizard_preview, 
                BLACK, 
                (shadow_offset // 2 + x_pos - x_size//3, shadow_offset // 2 + y_pos - x_size//3),
                (shadow_offset // 2 + x_pos + x_size//3, shadow_offset // 2 + y_pos + x_size//3), 
                2
            )
            pg.draw.line(
                wizard_preview, 
                BLACK, 
                (shadow_offset // 2 + x_pos - x_size//3, shadow_offset // 2 + y_pos + x_size//3),
                (shadow_offset // 2 + x_pos + x_size//3, shadow_offset // 2 + y_pos - x_size//3), 
                2
            )
            
            # Right side X (mirror position)
            right_x_pos = preview_width - x_pos
            pg.draw.line(
                wizard_preview, 
                BLACK, 
                (shadow_offset // 2 + right_x_pos - x_size//3, shadow_offset // 2 + y_pos - x_size//3),
                (shadow_offset // 2 + right_x_pos + x_size//3, shadow_offset // 2 + y_pos + x_size//3), 
                2
            )
            pg.draw.line(
                wizard_preview, 
                BLACK, 
                (shadow_offset // 2 + right_x_pos - x_size//3, shadow_offset // 2 + y_pos + x_size//3),
                (shadow_offset // 2 + right_x_pos + x_size//3, shadow_offset // 2 + y_pos - x_size//3), 
                2
            )
        
        # Staff/wand (vertical line with X at top)
        staff_x = shadow_offset // 2 + preview_width - 30 * preview_scale
        staff_top_y = shadow_offset // 2 + 50 * preview_scale
        staff_bottom_y = shadow_offset // 2 + preview_height - 20 * preview_scale
        pg.draw.line(wizard_preview, DARK_TEAL, (staff_x, staff_top_y), (staff_x, staff_bottom_y), 3)
        
        # X mark at staff top
        staff_x_size = 8 * preview_scale
        pg.draw.line(wizard_preview, BRIGHT_TEAL, 
                    (staff_x - staff_x_size//2, staff_top_y - staff_x_size//2),
                    (staff_x + staff_x_size//2, staff_top_y + staff_x_size//2), 3)
        pg.draw.line(wizard_preview, BRIGHT_TEAL, 
                    (staff_x - staff_x_size//2, staff_top_y + staff_x_size//2),
                    (staff_x + staff_x_size//2, staff_top_y - staff_x_size//2), 3)
                    
        # Apply enhanced shadow effects with deeper shadows
        prisoner_preview = Shadow.apply(prisoner_preview, offset_x=7, offset_y=7, blur=4, alpha=160)
        wizard_preview = Shadow.apply(wizard_preview, offset_x=7, offset_y=7, blur=4, alpha=160)
        
        # Set the previews
        self.start_menu.prisoner_preview = prisoner_preview
        self.start_menu.wizard_preview = wizard_preview
        
    def setup_collisions(self):
        """Set up collision handlers for different object types"""
        # Player (1) and X token (3) collision
        handler = self.space.add_collision_handler(1, 3)
        def begin(arbiter, space, data):
            # Get the shapes involved in the collision
            shapes = arbiter.shapes
            player_shape, token_shape = shapes
            
            # Find the token sprite from its shape
            for token in self.current_level.tokens:
                if token.shape == token_shape:
                    self.player.collect_token()
                    token.kill()
                    self.space.remove(token.shape, token.body)
                    
                    # Create particle effect at token position
                    token_pos = token.rect.center
                    self.token_particles.spawn_particles(
                        (token_pos[0] + self.camera_offset_x, 
                         token_pos[1] + self.camera_offset_y), 
                        10
                    )
                    break
                    
            # Return False to ensure no physical collision response
            return False
            
        handler.begin = begin
        
        # Player (1) and Platform (2) collision
        ground_handler = self.space.add_collision_handler(1, 2)
        
        def begin_platform(arbiter, space, data):
            # Get shapes involved in collision
            shapes = arbiter.shapes
            player_shape, platform_shape = shapes
            
            # Find the platform from its shape
            for platform in self.current_level.platforms:
                if platform.shape == platform_shape:
                    # Record this platform as the one player is standing on
                    self.player.current_platform = platform
                    break
            return True
            
        def separate_platform(arbiter, space, data):
            # Player is no longer on this platform
            shapes = arbiter.shapes
            player_shape, platform_shape = shapes
            
            # Only clear if it's the same platform the player was on
            if (hasattr(self.player, 'current_platform') and 
                self.player.current_platform is not None and 
                self.player.current_platform.shape == platform_shape):
                self.player.current_platform = None
            
            return True
            
        def post_solve(arbiter, space, data):
            # When player collides with ground, update on_ground state
            self.player._on_ground = True
            
            # Trigger landing animation
            if hasattr(self.player, 'animation') and self.player.animation:
                self.player.animation.trigger_land()
            
        ground_handler.begin = begin_platform
        ground_handler.separate = separate_platform
        ground_handler.post_solve = post_solve
        
    def new_game(self):
        """Start a new game"""
        # Clear any existing objects
        self.clear_level()
        
        # Create level using the factory function
        self.current_level = get_level(self, self.level_num)
        
        # Create player
        self.player = Player(self, self.current_level.start_x, self.current_level.start_y)
        self.all_sprites.add(self.player)
        self.space.add(self.player.body, self.player.shape)
        
        # Create background based on level type
        if self.level_num == 2:
            level_type = "financial"
        elif self.level_num == 3:
            level_type = "market_crash"
        else:
            level_type = "prison"
            
        self.background = EnhancedBackground(self, level_type)
        
        # Set game state
        self.game_state = STATE_PLAYING
        self.playing = True
        self.paused = False
        
        # Set level start time for spawn protection
        self.current_level.level_start_time = self.dt * self.frame_count
        
        # Start fade in transition
        self.transition_effect.start_fade_in()
        
    def clear_level(self):
        """Clear all game objects from the current level"""
        if self.player:
            self.space.remove(self.player.shape, self.player.body)
            self.player.kill()
            
        if self.current_level:
            for sprite in self.current_level.platforms:
                self.space.remove(sprite.shape, sprite.body)
                sprite.kill()
                
            for sprite in self.current_level.tokens:
                self.space.remove(sprite.shape, sprite.body)
                sprite.kill()
                
            for sprite in self.current_level.enemies:
                self.space.remove(sprite.shape, sprite.body)
                sprite.kill()
                
            for obj in self.current_level.interactive_objects:
                self.space.remove(obj.shape, obj.body)
                obj.kill()
        
    def handle_events(self):
        """Process input events"""
        events = pg.event.get()
        
        for event in events:
            if event.type == pg.QUIT:
                self.playing = False
                self.running = False
                
            # Menu event handling
            if self.game_state == STATE_MENU:
                menu_action = self.current_menu.handle_events(events)
                if menu_action:
                    self.handle_menu_action(menu_action)
                break
                    
            # Pause menu handling
            elif self.game_state == STATE_PAUSED:
                menu_action = self.current_menu.handle_events(events)
                if menu_action:
                    self.handle_menu_action(menu_action)
                break
                
            # Level completion menu handling
            elif self.game_state == STATE_PLAYING and self.current_level.level_complete and self.current_level.completion_time >= 5.0:
                # Check for level completion menu button clicks
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                    mouse_pos = pg.mouse.get_pos()
                    
                    # Check next level button
                    if hasattr(self.current_level, 'next_level_button') and self.current_level.next_level_button.rect.collidepoint(mouse_pos):
                        self.next_level()
                        break
                        
                    # Check main menu button
                    if hasattr(self.current_level, 'main_menu_button') and self.current_level.main_menu_button.rect.collidepoint(mouse_pos):
                        self.game_state = STATE_MENU
                        self.current_menu = self.start_menu
                        self.current_menu.activate()
                        break
                
            # Game input handling
            elif self.game_state == STATE_PLAYING:
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.pause_game()
                            
                    elif event.key == pg.K_SPACE:
                        self.player.jump()
                        
                elif event.type == pg.KEYUP:
                    if event.key == pg.K_SPACE:
                        self.player.release_jump()
                        
                    elif event.key == pg.K_e:
                        # Handle interaction with nearby objects
                        self.handle_player_interaction()
                            
                    elif event.key == pg.K_d:
                        # Toggle debug drawing
                        self.debug = not self.debug
                            
                    elif event.key == pg.K_r:
                        # Restart level
                        self.restart_level()
                            
                    elif event.key == pg.K_n:
                        # Next level
                        self.next_level()
                        
                    elif event.key == pg.K_p:
                        # Toggle post-processing effects (for performance)
                        self.post_processing_enabled = not self.post_processing_enabled
    
    def handle_menu_action(self, action):
        """Process menu action commands"""
        if action == "level_select":
            self.current_menu.deactivate()
            self.current_menu = self.level_select_screen
            self.current_menu.activate()
            
        elif action.startswith("play_level_"):
            # Extract level number from action
            selected_level = int(action.split("_")[-1])
            self.level_num = selected_level
            self.current_menu.deactivate()
            self.new_game()
            
        elif action == "resume":
            self.current_menu.deactivate()
            self.game_state = STATE_PLAYING
            self.paused = False
            
        elif action == "restart":
            self.current_menu.deactivate()
            self.restart_level()
            
        elif action == "main_menu":
            self.current_menu.deactivate()
            self.current_menu = self.start_menu
            self.current_menu.activate()
            self.game_state = STATE_MENU
            
        elif action == "controls":
            self.prev_state = self.game_state
            self.current_menu.deactivate()
            self.current_menu = self.controls_screen
            self.current_menu.activate()
            
        elif action == "credits":
            self.prev_state = self.game_state
            self.current_menu.deactivate()
            self.current_menu = self.credits_screen
            self.current_menu.activate()
            
        elif action == "back":
            self.current_menu.deactivate()
            
            # Return to previous menu/state
            if self.prev_state == STATE_MENU or self.current_menu == self.level_select_screen:
                self.current_menu = self.start_menu
                self.game_state = STATE_MENU
            elif self.prev_state == STATE_PAUSED:
                self.current_menu = self.pause_menu
                self.game_state = STATE_PAUSED
            else:
                self.game_state = STATE_PLAYING
                self.paused = False
                
            self.current_menu.activate()
            
        elif action == "quit":
            self.running = False
            self.playing = False
    
    def pause_game(self):
        """Pause the game and show pause menu"""
        self.paused = True
        self.game_state = STATE_PAUSED
        self.current_menu = self.pause_menu
        self.current_menu.activate()
        
    def restart_level(self):
        """Restart the current level"""
        self.transition_effect.start_fade_out()
        # Wait for transition to complete
        while not self.transition_effect.update(self.clock.tick(FPS) / 1000.0):
            pass
        self.new_game()
        
    def next_level(self):
        """Advance to the next level"""
        self.level_num += 1
        if self.level_num > 3:  # Updated to support 3 levels
            self.level_num = 1  # Loop back to first level
            
        self.transition_effect.start_fade_out()
        # Wait for transition to complete
        while not self.transition_effect.update(self.clock.tick(FPS) / 1000.0):
            pass
        self.new_game()
                    
    def handle_player_interaction(self):
        """Handle player interaction with nearby objects"""
        for obj in self.current_level.interactive_objects:
            if obj.interact():
                # Object was successfully interacted with
                # Add particle effects around the interaction point
                self.token_particles.spawn_particles(
                    (obj.rect.centerx + self.camera_offset_x, 
                     obj.rect.centery + self.camera_offset_y), 
                    5, 
                    spread=30
                )
                break
                
    def camera_shake(self, intensity=5.0, duration=0.5):
        """Trigger a camera shake effect with given intensity and duration"""
        self.shake_intensity = intensity
        self.shake_duration = duration
        self.shake_time = 0
        
    def update(self, dt):
        """Update game objects"""
        # Update based on current game state
        if self.game_state == STATE_MENU or self.game_state == STATE_PAUSED:
            # Update menus
            self.current_menu.update(dt)
            return
            
        # Update transition effects
        self.transition_effect.update(dt)
            
        # Only update gameplay if in playing state
        if self.game_state != STATE_PLAYING:
            return
            
        # Step the physics simulation
        self.space.step(1/FPS)
        
        # Update sprites
        self.all_sprites.update()
        self.current_level.update()
        
        # Update particle effects
        self.token_particles.update(dt)
        
        # Update camera shake effect
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        if self.shake_time < self.shake_duration:
            self.shake_time += dt
            # Calculate shake decay based on time
            shake_decay = 1.0 - (self.shake_time / self.shake_duration)
            # Calculate random offsets, stronger at start and weakening over time
            current_intensity = self.shake_intensity * shake_decay
            self.shake_offset_x = random.uniform(-current_intensity, current_intensity)
            self.shake_offset_y = random.uniform(-current_intensity, current_intensity)
        
        # Update camera position to follow player with smooth following
        target_camera_x = -self.player.rect.centerx + WIDTH // 2
        
        # Add smoothing to camera movement (interpolation)
        camera_smoothness = 0.92  # Higher values = smoother but slower camera
        self.camera_offset_x = self.camera_offset_x * camera_smoothness + target_camera_x * (1 - camera_smoothness)
        
        # Limit camera to level bounds
        max_offset = 0
        min_offset = -self.current_level.width + WIDTH
        self.camera_offset_x = max(min(self.camera_offset_x, max_offset), min_offset)
        
        # Apply camera shake on top of normal camera position
        self.camera_offset_x += self.shake_offset_x
        self.camera_offset_y += self.shake_offset_y
        
        # Update background scroll position
        self.background.update(self.player.rect.centerx)
        
        # Check for death by falling
        if self.player.rect.top > self.current_level.death_height:
            # Start death animation
            if not self.current_level.player_died:
                self.current_level.start_death_animation()
        
        # Check if player reached the end of the level
        if self.current_level.check_level_complete():
            # Level completion is now handled by the level class
            # which provides the completion animation
            # After a delay, we'll proceed to the next level
            if self.current_level.completion_time > 2.5:
                self.next_level()
            
    def draw(self):
        """Render game objects to the screen"""
        # Clear screen
        self.screen.fill(BLACK)
        
        if self.game_state == STATE_PLAYING:
            # Draw game elements
            # Draw background
            self.background.draw(self.screen)
            
            # Create a temporary surface for level elements
            level_surface = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
            level_surface.fill((0, 0, 0, 0))  # Clear with transparent
            
            # Define viewport with extra margin for smoother scrolling
            viewport_margin = 100  # Extra pixels beyond screen edge
            viewport = pg.Rect(-self.camera_offset_x - viewport_margin, 
                             -self.camera_offset_y - viewport_margin,
                             WIDTH + viewport_margin*2, 
                             HEIGHT + viewport_margin*2)
                
            # Draw level with camera offset - only draw visible objects (viewport culling)
            for sprite in self.current_level.platforms:
                # Only draw if in viewport
                if viewport.colliderect(sprite.rect):
                    if hasattr(sprite, 'draw'):
                        sprite.draw(level_surface, self.camera_offset_x, self.camera_offset_y)
                    else:
                        level_surface.blit(sprite.image, 
                                         (sprite.rect.x + self.camera_offset_x, 
                                          sprite.rect.y + self.camera_offset_y))
                
            for sprite in self.current_level.tokens:
                # Only draw if in viewport
                if viewport.colliderect(sprite.rect):
                    if hasattr(sprite, 'draw'):
                        sprite.draw(level_surface, self.camera_offset_x, self.camera_offset_y)
                    else:
                        level_surface.blit(sprite.image, 
                                         (sprite.rect.x + self.camera_offset_x, 
                                          sprite.rect.y + self.camera_offset_y))
                
            # Draw interactive objects with viewport culling
            for obj in self.current_level.interactive_objects:
                # Only draw if in viewport
                if viewport.colliderect(obj.rect):
                    level_surface.blit(obj.image,
                                     (obj.rect.x + self.camera_offset_x,
                                      obj.rect.y + self.camera_offset_y))

            # Draw player with camera offset
            # Check if spawn protection is active
            current_time = self.dt * self.frame_count
            is_protected = current_time - self.current_level.level_start_time < self.current_level.spawn_protection_time
            
            # Draw player - with protection effect if needed
            if is_protected:
                # Create a copy of the player image with a pulsing effect
                player_img = self.player.image.copy()
                
                # Calculate pulsing alpha based on time (0.5-second pulse)
                pulse_alpha = 128 + int(127 * math.sin(current_time * 12))
                
                # Add a colored overlay
                overlay = pg.Surface(player_img.get_size(), pg.SRCALPHA)
                overlay.fill((BRIGHT_TEAL[0], BRIGHT_TEAL[1], BRIGHT_TEAL[2], pulse_alpha))
                player_img.blit(overlay, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
                
                # Draw the protected player
                level_surface.blit(player_img, 
                                 (self.player.rect.x + self.camera_offset_x, 
                                  self.player.rect.y + self.camera_offset_y))
                  
                # Draw protection indicator text
                protection_font = pg.font.SysFont(None, 20)
                protection_text = protection_font.render("Protected", True, BRIGHT_TEAL)
                text_x = self.player.rect.centerx + self.camera_offset_x - protection_text.get_width() // 2
                text_y = self.player.rect.y + self.camera_offset_y - 20
                level_surface.blit(protection_text, (text_x, text_y))
            else:
                # Draw normal player
                level_surface.blit(self.player.image, 
                                 (self.player.rect.x + self.camera_offset_x, 
                                  self.player.rect.y + self.camera_offset_y))
            
            # Draw level surface to screen
            self.screen.blit(level_surface, (0, 0))
            
            # Draw interaction prompts
            self.current_level.draw_interactive_prompts(
                self.screen, self.camera_offset_x, self.camera_offset_y
            )
            
            # Draw token collection particles
            self.token_particles.draw(self.screen)
            
            # Draw death and completion effects from level
            self.current_level.draw(self.screen)
            
            # Debug drawing
            if self.debug:
                self.space.debug_draw(self.draw_options)
                
            # Draw HUD
            self.draw_hud()
            
            # Draw transition effects
            self.transition_effect.draw(self.screen)
            
        # Draw menus if in menu state
        if self.game_state == STATE_MENU or self.game_state == STATE_PAUSED:
            # If in pause state, draw the game underneath first
            if self.game_state == STATE_PAUSED and self.current_menu == self.pause_menu:
                # Draw the game in the background (already done above)
                pass
                
            # Draw active menu
            self.current_menu.draw(self.screen)
            
        # Apply post-processing effects
        if self.post_processing_enabled:
            self.apply_post_processing()
            
        # Flip display
        pg.display.flip()
        
    def _generate_vignette(self):
        """Pre-generate vignette effect for performance optimization"""
        self.vignette_surface = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        
        # Radial gradient from transparent center to dark edges
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        max_dist = math.sqrt(center_x**2 + center_y**2)
        
        for x in range(0, WIDTH, 2):  # Higher quality with 2px step
            for y in range(0, HEIGHT, 2):
                # Calculate distance from center
                dx, dy = x - center_x, y - center_y
                dist = math.sqrt(dx**2 + dy**2)
                
                # Calculate alpha based on distance (more transparent near center)
                alpha = int(min(60, 60 * (dist / max_dist)**2))
                
                # Draw a small rect with calculated alpha
                if alpha > 0:
                    rect = pg.Rect(x, y, 2, 2)
                    pg.draw.rect(self.vignette_surface, (0, 0, 0, alpha), rect)
    
    def apply_post_processing(self):
        """Apply post-processing effects to the final screen"""
        # This method can be expanded for more complex effects
        
        if self.game_state == STATE_PLAYING and self.vignette_surface:
            # Apply pre-calculated vignette to the screen
            self.screen.blit(self.vignette_surface, (0, 0))
        
    def draw_hud(self):
        """Draw game HUD (tokens collected, etc.)"""
        # Create translucent background for HUD
        hud_height = 40
        hud_bg = pg.Surface((WIDTH, hud_height), pg.SRCALPHA)
        hud_bg.fill((0, 0, 0, 150))
        self.screen.blit(hud_bg, (0, 0))
        
        # Create bottom HUD
        bottom_hud = pg.Surface((WIDTH, hud_height), pg.SRCALPHA)
        bottom_hud.fill((0, 0, 0, 150))
        self.screen.blit(bottom_hud, (0, HEIGHT - hud_height))
        
        # Tokens collected text with icon
        token_text = f"X Tokens: {self.player.tokens_collected} / {TOKENS_TO_TRANSFORM}"
        token_surface = self.font.render(token_text, True, TEAL)
        self.screen.blit(token_surface, (20, 10))
        
        # Interaction hint (only show if near an interactive object)
        show_hint = False
        for obj in self.current_level.interactive_objects:
            if obj.is_near_player and not obj.activated:
                show_hint = True
                break
                
        if show_hint:
            hint_text = "Press E to interact"
            hint_surface = self.font.render(hint_text, True, BRIGHT_TEAL)
            hint_x = WIDTH - hint_surface.get_width() - 20
            hint_y = 50
            self.screen.blit(hint_surface, (hint_x, hint_y))
        
        # Player state text
        state_text = "Wizard Form" if self.player.is_wizard else "Prisoner Form"
        state_color = TEAL if self.player.is_wizard else BLUE_PRISONER
        state_surface = self.font.render(state_text, True, state_color)
        self.screen.blit(state_surface, (WIDTH - state_surface.get_width() - 20, 10))
        
        # Level info
        level_text = f"Level {self.level_num}: " + (
            "Teal X Obstacle Course" if self.level_num == 1 else "Financial District"
        )
        level_surface = self.font.render(level_text, True, LIGHT_TEAL)
        self.screen.blit(level_surface, (20, HEIGHT - level_surface.get_height() - 5))
        
        # Controls hint
        controls_text = "ESC: Pause  |  SPACE: Jump  |  E: Interact  |  R: Restart"
        controls_surface = self.font.render(controls_text, True, LIGHT_TEAL)
        controls_x = WIDTH - controls_surface.get_width() - 20
        self.screen.blit(controls_surface, (controls_x, HEIGHT - controls_surface.get_height() - 5))
        
    def run(self):
        """Main game loop"""
        self.running = True
        self.frame_count = 0
        
        # Activate start menu
        self.current_menu = self.start_menu
        self.current_menu.activate()
        self.game_state = STATE_MENU
        
        # Main game loop
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(FPS) / 1000.0
            self.dt = dt  # Store for use in other methods
            self.frame_count += 1
            
            # Handle events
            self.handle_events()
            
            # Update game state
            self.update(dt)
            
            # Draw the frame
            self.draw()
            
def main():
    game = Game()
    game.run()
    pg.quit()
    sys.exit()

if __name__ == "__main__":
    main()
