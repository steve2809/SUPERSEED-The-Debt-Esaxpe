import pygame as pg
import random
import math
from src.settings import *
from src.ui import Button, Panel, FadeEffect, AnimatedText, ParticleSystem

class Menu:
    """Base class for game menus"""
    def __init__(self, game):
        self.game = game
        self.buttons = []
        self.active = False
        self.fade_effect = FadeEffect(TRANSITION_DURATION)
        self.particle_system = ParticleSystem("x_mark", PARTICLE_COUNT)
        self.animated_elements = []
        
    def activate(self):
        """Activate the menu with transition effect"""
        self.active = True
        self.fade_effect.start_fade_in()
        
    def deactivate(self):
        """Deactivate the menu with transition effect"""
        self.fade_effect.start_fade_out()
        
    def handle_events(self, events):
        """Process events when menu is active"""
        if not self.active:
            return None
            
        for event in events:
            if event.type == pg.QUIT:
                return "quit"
                
            for button in self.buttons:
                # Check for hover sound
                if event.type == pg.MOUSEMOTION:
                    if button.rect.collidepoint(event.pos) and not button.is_hovered:
                        # Just started hovering this button
                        if hasattr(self.game, 'sound_manager'):
                            self.game.sound_manager.play_menu_hover()
                
                # Check for click and action
                action = button.handle_event(event)
                if action:
                    # Play click sound on successful button action
                    if hasattr(self.game, 'sound_manager'):
                        self.game.sound_manager.play_menu_click()
                    return action
                    
        return None
        
    def update(self, dt):
        """Update menu components"""
        if not self.active:
            return
            
        # Update transition effects
        if self.fade_effect.update(dt):
            # Transition completed
            if self.fade_effect.fading_out:
                self.active = False
                
        # Update buttons
        mouse_pos = pg.mouse.get_pos()
        for button in self.buttons:
            button.update(mouse_pos, dt)
            
        # Update animated elements
        for element in self.animated_elements:
            element.update(dt)
            
        # Update particle effects
        self.particle_system.update(dt)
        
        # Spawn new particles occasionally
        if random.random() < 0.05:
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            self.particle_system.spawn_particles((x, y), 1)
            
        # Update the floating X particles for StartMenu
        if isinstance(self, StartMenu) and hasattr(self, 'floating_xs'):
            for x_particle in self.floating_xs:
                # Move particle
                x_particle['x'] += math.cos(x_particle['angle']) * x_particle['speed']
                x_particle['y'] += math.sin(x_particle['angle']) * x_particle['speed']
                
                # Wrap around screen edges
                if x_particle['x'] < -50:
                    x_particle['x'] = WIDTH + 50
                elif x_particle['x'] > WIDTH + 50:
                    x_particle['x'] = -50
                    
                if x_particle['y'] < -50:
                    x_particle['y'] = HEIGHT + 50
                elif x_particle['y'] > HEIGHT + 50:
                    x_particle['y'] = -50
                    
                # Rotate the X
                x_particle['rotation'] += x_particle['rot_speed']
                
                # Randomly change direction occasionally
                if random.random() < 0.005:
                    x_particle['angle'] = random.uniform(0, 2 * math.pi)
            
    def draw(self, surface):
        """Draw the menu on the given surface"""
        if not self.active and self.fade_effect.progress <= 0:
            return
            
        # Draw menu background (can be overridden in subclasses)
        self.draw_background(surface)
        
        # Draw particle effects
        self.particle_system.draw(surface)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(surface)
            
        # Draw animated elements
        for element in self.animated_elements:
            element.draw(surface)
            
        # Draw transition effects
        self.fade_effect.draw(surface)
        
    def draw_background(self, surface):
        """Draw the menu background (to be overridden)"""
        pass
        
class StartMenu(Menu):
    """Main menu shown at game start"""
    def __init__(self, game):
        super().__init__(game)
        
        # Create custom font instead of system font for better appearance
        try:
            # Try to load a custom font if available
            self.title_font = pg.font.Font("assets/fonts/Azonix.otf", 84)
            self.subtitle_font = pg.font.Font("assets/fonts/Azonix.otf", 36)
        except:
            # Fall back to system font if custom font fails to load
            self.title_font = pg.font.SysFont("Arial", 84)
            self.subtitle_font = pg.font.SysFont("Arial", 36)
        
        # Create animated title with more vertical space
        self.title_text = AnimatedText(
            TITLE, 
            self.title_font, 
            TEAL, 
            MENU_CENTER_X, 
            HEIGHT // 4,  # Moved up from HEIGHT // 3
            "pulse"
        )
        self.animated_elements.append(self.title_text)
        
        # Subtitle with typing effect - positioned with more space
        self.subtitle_text = AnimatedText(
            "Free yourself from debt prison!", 
            self.subtitle_font, 
            LIGHT_TEAL, 
            MENU_CENTER_X, 
            HEIGHT // 4 + 120,  # More space below title
            "typing"
        )
        self.animated_elements.append(self.subtitle_text)
        
        # Create main menu with more modern button styling
        button_y = HEIGHT // 2 - 20  # Start buttons higher to fit all buttons
        
        # Enhanced button style with larger size
        button_width = BUTTON_WIDTH + 50  # Wider buttons
        button_height = BUTTON_HEIGHT + 5  # Slightly taller buttons
        button_spacing = BUTTON_SPACING + 5  # Slightly more space between buttons
        
        # Play button
        play_button = Button(
            MENU_CENTER_X - button_width // 2, 
            button_y, 
            button_width, 
            button_height, 
            "Select Level", 
            font_size=36,  # Larger font
            action=lambda: "level_select"
        )
        self.buttons.append(play_button)
        button_y += button_height + button_spacing
        
        # Controls button
        controls_button = Button(
            MENU_CENTER_X - button_width // 2, 
            button_y, 
            button_width, 
            button_height, 
            "Controls", 
            font_size=36,  # Larger font
            action=lambda: "controls"
        )
        self.buttons.append(controls_button)
        button_y += button_height + button_spacing
        
        # Credits button
        credits_button = Button(
            MENU_CENTER_X - button_width // 2, 
            button_y, 
            button_width, 
            button_height, 
            "Credits", 
            font_size=36,  # Larger font
            action=lambda: "credits"
        )
        self.buttons.append(credits_button)
        button_y += button_height + button_spacing
        
        # Quit button
        quit_button = Button(
            MENU_CENTER_X - button_width // 2, 
            button_y, 
            button_width, 
            button_height, 
            "Quit", 
            font_size=36,  # Larger font
            action=lambda: "quit"
        )
        self.buttons.append(quit_button)
        
        # Add interactive floating X particles
        self.floating_xs = []
        for _ in range(15):  # Create 15 floating X marks
            self.floating_xs.append({
                'x': random.randint(0, WIDTH),
                'y': random.randint(0, HEIGHT),
                'size': random.randint(8, 25),
                'speed': random.uniform(0.3, 1.2),
                'angle': random.uniform(0, 2 * math.pi),
                'rotation': random.uniform(0, 360),
                'rot_speed': random.uniform(-1, 1)
            })
        
        # Create character previews for menu animation
        self.prisoner_preview = None
        self.wizard_preview = None
        
        # Spawn initial particles
        for _ in range(30):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            self.particle_system.spawn_particles((x, y), 1)
            
    def activate(self):
        """Show the menu with animation"""
        super().activate()
        # Reset typing animation
        for element in self.animated_elements:
            if hasattr(element, "animation_type") and element.animation_type == "typing":
                element.char_index = 0
                element.displayed_text = ""
                element.timer = 0
                
        # Spawn particles around the title
        self.particle_system.spawn_particles(
            (MENU_CENTER_X, HEIGHT // 3), 
            20, 
            spread=100
        )
        
    def draw_background(self, surface):
        """Draw the start menu background"""
        # Fill with dark background
        surface.fill(BLACK)
        
        # Draw grid of subtle X marks
        spacing = 80
        size = 15
        alpha = 40  # Very transparent
        
        # Create a surface for the X patterns
        pattern_surface = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        
        for x in range(0, WIDTH + spacing, spacing):
            for y in range(0, HEIGHT + spacing, spacing):
                # Add some randomness to positions
                x_pos = x + random.randint(-10, 10)
                y_pos = y + random.randint(-10, 10)
                
                # Draw X mark
                pg.draw.line(
                    pattern_surface, 
                    (*DARK_TEAL, alpha), 
                    (x_pos - size // 2, y_pos - size // 2), 
                    (x_pos + size // 2, y_pos + size // 2), 
                    2
                )
                pg.draw.line(
                    pattern_surface, 
                    (*DARK_TEAL, alpha), 
                    (x_pos - size // 2, y_pos + size // 2), 
                    (x_pos + size // 2, y_pos - size // 2), 
                    2
                )
                
        # Apply a subtle wave effect to the pattern
        time = pg.time.get_ticks() / 1000
        for x in range(WIDTH):
            # Create a subtle sine wave effect
            offset = int(math.sin(time + x / 100) * 5)
            # Only shift columns where offset is not 0
            if offset != 0:
                # Create a vertical slice of the pattern
                slice_rect = pg.Rect(x, 0, 1, HEIGHT)
                slice_surface = pattern_surface.subsurface(slice_rect).copy()
                # Shift the slice
                pattern_surface.blit(
                    slice_surface, 
                    (x, offset), 
                    special_flags=pg.BLEND_ALPHA_SDL2
                )
                
        # Draw the pattern to the screen
        surface.blit(pattern_surface, (0, 0))
        
        # Draw interactive floating X particles
        if hasattr(self, 'floating_xs'):
            for x_particle in self.floating_xs:
                size = x_particle['size']
                x = x_particle['x']
                y = x_particle['y']
                rotation = x_particle['rotation']
                
                # Create a surface for the X
                x_surface = pg.Surface((size * 2, size * 2), pg.SRCALPHA)
                
                # Draw X mark
                line_width = max(1, int(size / 8))
                pg.draw.line(
                    x_surface,
                    (*TEAL, 180),  # Semi-transparent teal
                    (0, 0),
                    (size * 2, size * 2),
                    line_width
                )
                pg.draw.line(
                    x_surface,
                    (*TEAL, 180),  # Semi-transparent teal
                    (0, size * 2),
                    (size * 2, 0),
                    line_width
                )
                
                # Rotate the X
                rotated_surface = pg.transform.rotate(x_surface, rotation)
                
                # Calculate position to center the rotated surface
                pos_x = x - rotated_surface.get_width() // 2
                pos_y = y - rotated_surface.get_height() // 2
                
                # Draw the X
                surface.blit(rotated_surface, (pos_x, pos_y))
        
        # Draw character previews if available
        if self.prisoner_preview:
            # Draw prisoner on left side
            prisoner_x = WIDTH // 4 - self.prisoner_preview.get_width() // 2
            prisoner_y = HEIGHT // 2
            surface.blit(self.prisoner_preview, (prisoner_x, prisoner_y))
            
        if self.wizard_preview:
            # Draw wizard on right side
            wizard_x = 3 * WIDTH // 4 - self.wizard_preview.get_width() // 2
            wizard_y = HEIGHT // 2
            surface.blit(self.wizard_preview, (wizard_x, wizard_y))
            
class PauseMenu(Menu):
    """Pause menu displayed during gameplay"""
    def __init__(self, game):
        super().__init__(game)
        
        # Create semi-transparent panel
        panel_width = WIDTH // 2
        panel_height = HEIGHT // 1.5
        panel_x = WIDTH // 2 - panel_width // 2
        panel_y = HEIGHT // 2 - panel_height // 2
        self.panel = Panel(panel_x, panel_y, panel_width, panel_height)
        
        # Title
        self.title_font = pg.font.SysFont(None, 72)
        self.title_text = AnimatedText(
            "PAUSED", 
            self.title_font, 
            TEAL, 
            WIDTH // 2, 
            panel_y + 50,
            "pulse"
        )
        self.animated_elements.append(self.title_text)
        
        # Create buttons
        button_y = panel_y + 130
        
        # Resume button
        resume_button = Button(
            WIDTH // 2 - BUTTON_WIDTH // 2, 
            button_y, 
            BUTTON_WIDTH, 
            BUTTON_HEIGHT, 
            "Resume", 
            action=lambda: "resume"
        )
        self.buttons.append(resume_button)
        button_y += BUTTON_HEIGHT + BUTTON_SPACING
        
        # Restart button
        restart_button = Button(
            WIDTH // 2 - BUTTON_WIDTH // 2, 
            button_y, 
            BUTTON_WIDTH, 
            BUTTON_HEIGHT, 
            "Restart Level", 
            action=lambda: "restart"
        )
        self.buttons.append(restart_button)
        button_y += BUTTON_HEIGHT + BUTTON_SPACING
        
        # Controls button
        controls_button = Button(
            WIDTH // 2 - BUTTON_WIDTH // 2, 
            button_y, 
            BUTTON_WIDTH, 
            BUTTON_HEIGHT, 
            "Controls", 
            action=lambda: "controls"
        )
        self.buttons.append(controls_button)
        button_y += BUTTON_HEIGHT + BUTTON_SPACING
        
        # Main menu button
        menu_button = Button(
            WIDTH // 2 - BUTTON_WIDTH // 2, 
            button_y, 
            BUTTON_WIDTH, 
            BUTTON_HEIGHT, 
            "Main Menu", 
            action=lambda: "main_menu"
        )
        self.buttons.append(menu_button)
        
    def draw_background(self, surface):
        """Draw pause menu background"""
        # Draw semi-transparent overlay
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Dark semi-transparent overlay
        surface.blit(overlay, (0, 0))
        
        # Draw panel background
        self.panel.draw(surface)
        
class ControlsScreen(Menu):
    """Screen showing game controls"""
    def __init__(self, game):
        super().__init__(game)
        
        # Create panel
        panel_width = WIDTH // 1.5
        panel_height = HEIGHT // 1.5
        panel_x = WIDTH // 2 - panel_width // 2
        panel_y = HEIGHT // 2 - panel_height // 2
        self.panel = Panel(panel_x, panel_y, panel_width, panel_height)
        
        # Title
        self.title_font = pg.font.SysFont(None, 64)
        self.title_text = AnimatedText(
            "Controls", 
            self.title_font, 
            TEAL, 
            WIDTH // 2, 
            panel_y + 50,
            "pulse"
        )
        self.animated_elements.append(self.title_text)
        
        # Controls content
        self.content_font = pg.font.SysFont(None, 32)
        self.controls = [
            ("ARROWS / WASD", "Move character"),
            ("SPACE", "Jump"),
            ("ESC", "Pause game"),
            ("R", "Restart level"),
            ("N", "Next level"),
            ("D", "Toggle debug mode")
        ]
        
        # Back button
        self.back_button = Button(
            WIDTH // 2 - BUTTON_WIDTH // 2, 
            panel_y + panel_height - BUTTON_HEIGHT - MENU_PADDING, 
            BUTTON_WIDTH, 
            BUTTON_HEIGHT, 
            "Back", 
            action=lambda: "back"
        )
        self.buttons.append(self.back_button)
        
    def draw_background(self, surface):
        """Draw controls screen background"""
        # Draw semi-transparent overlay
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        
        # Draw panel background
        self.panel.draw(surface)
        
        # Draw controls list
        start_y = HEIGHT // 2 - len(self.controls) * 20
        for i, (key, action) in enumerate(self.controls):
            # Key text
            key_text = self.content_font.render(key, True, WHITE)
            key_rect = key_text.get_rect(right=WIDTH // 2 - 20, centery=start_y + i * 50)
            surface.blit(key_text, key_rect)
            
            # Action text
            action_text = self.content_font.render(action, True, LIGHT_TEAL)
            action_rect = action_text.get_rect(left=WIDTH // 2 + 20, centery=start_y + i * 50)
            surface.blit(action_text, action_rect)
            
            # Connecting line
            pg.draw.line(
                surface, 
                DARK_TEAL, 
                (key_rect.right + 10, key_rect.centery), 
                (action_rect.left - 10, action_rect.centery), 
                1
            )

class LevelSelectScreen(Menu):
    """Level selection screen"""
    def __init__(self, game):
        super().__init__(game)
        
        # Create panel for level select
        panel_width = WIDTH - 200
        panel_height = HEIGHT - 150
        panel_x = WIDTH // 2 - panel_width // 2
        panel_y = HEIGHT // 2 - panel_height // 2
        self.panel = Panel(panel_x, panel_y, panel_width, panel_height)
        
        # Title
        self.title_font = pg.font.SysFont(None, 64)
        self.title_text = AnimatedText(
            "Select Level", 
            self.title_font, 
            TEAL, 
            WIDTH // 2, 
            panel_y + 50,
            "pulse"
        )
        self.animated_elements.append(self.title_text)
        
        # Level thumbnails
        self.thumbnails = []
        
        # Calculate grid layout
        rows = LEVEL_SELECT_ROWS
        cols = LEVEL_SELECT_COLS
        total_width = cols * LEVEL_THUMBNAIL_WIDTH + (cols - 1) * LEVEL_SPACING
        total_height = rows * LEVEL_THUMBNAIL_HEIGHT + (rows - 1) * LEVEL_SPACING
        
        start_x = WIDTH // 2 - total_width // 2
        start_y = panel_y + LEVEL_SELECT_TITLE_HEIGHT
        
        # Create level thumbnails
        level_count = 0
        for row in range(rows):
            for col in range(cols):
                level_count += 1
                if level_count <= 3:  # We now have three levels
                    x = start_x + col * (LEVEL_THUMBNAIL_WIDTH + LEVEL_SPACING)
                    y = start_y + row * (LEVEL_THUMBNAIL_HEIGHT + LEVEL_SPACING)
                    
                    # Create level thumbnail
                    from src.sprites import LevelThumbnail
                    
                    # Assign level names
                    if level_count == 1:
                        name = "Prison Escape"
                    elif level_count == 2:
                        name = "Financial District"
                    else:
                        name = "Market Crash"
                        
                    thumbnail = LevelThumbnail(level_count, name)
                    thumbnail.is_selected = (level_count == game.level_num)
                    self.thumbnails.append((thumbnail, x, y))
        
        # Level info display area
        self.info_area = pg.Rect(
            panel_x + MENU_PADDING,
            start_y + total_height + MENU_PADDING,
            panel_width - 2 * MENU_PADDING,
            LEVEL_INFO_HEIGHT
        )
        
        # Info font
        self.info_font = pg.font.SysFont(None, 32)
        self.selected_level = game.level_num
        
        # Back button
        self.back_button = Button(
            panel_x + MENU_PADDING,
            panel_y + panel_height - BUTTON_HEIGHT - MENU_PADDING,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "Back",
            action=lambda: "back"
        )
        self.buttons.append(self.back_button)
        
        # Play button
        self.play_button = Button(
            panel_x + panel_width - BUTTON_WIDTH - MENU_PADDING,
            panel_y + panel_height - BUTTON_HEIGHT - MENU_PADDING,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "Play Level",
            action=lambda: f"play_level_{self.selected_level}"
        )
        self.buttons.append(self.play_button)
        
    def handle_events(self, events):
        """Handle events including level selection"""
        result = super().handle_events(events)
        if result:
            return result
            
        # Handle thumbnail clicking
        mouse_pos = pg.mouse.get_pos()
        mouse_clicked = False
        
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True
                
        # Update thumbnails and check for selection
        for thumbnail, x, y in self.thumbnails:
            # Adjust mouse position for thumbnail coordinates
            relative_pos = (mouse_pos[0] - x, mouse_pos[1] - y)
            level_num = thumbnail.update(relative_pos, mouse_clicked, self.game.dt)
            
            if level_num:
                # Level was selected
                self.selected_level = level_num
                
                # Update selected state for all thumbnails
                for thumb, _, _ in self.thumbnails:
                    thumb.is_selected = (thumb.level_num == level_num)
                    
                # Update play button action
                self.play_button.action = lambda: f"play_level_{self.selected_level}"
                
        return None
        
    def update(self, dt):
        """Update level select elements"""
        super().update(dt)
        
        # Additional updates for thumbnails can go here
        # (already handled in handle_events)
                
    def draw_background(self, surface):
        """Draw level select background"""
        # Draw semi-transparent overlay
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        
        # Draw panel background
        self.panel.draw(surface)
        
        # Draw level thumbnails
        for thumbnail, x, y in self.thumbnails:
            thumbnail.draw(surface, x, y)
            
        # Draw level info area
        level_info = f"Level {self.selected_level}: "
        level_info += "Prison Escape" if self.selected_level == 1 else "Financial District"
        
        info_text = self.info_font.render(level_info, True, TEAL)
        info_rect = info_text.get_rect(center=(
            self.info_area.centerx,
            self.info_area.y + 30
        ))
        surface.blit(info_text, info_rect)
        
        # Level description
        description = ""
        if self.selected_level == 1:
            description = "Escape from the debt prison by collecting X tokens!"
        elif self.selected_level == 2:
            description = "Navigate the financial district and collect tokens to reach financial freedom!"
        else:
            description = "Avoid the market crashes and survive the volatile economy to reach true wealth!"
            
        desc_text = self.info_font.render(description, True, LIGHT_TEAL)
        desc_rect = desc_text.get_rect(center=(
            self.info_area.centerx,
            self.info_area.y + 70
        ))
        surface.blit(desc_text, desc_rect)

class CreditsScreen(Menu):
    """Screen showing game credits"""
    def __init__(self, game):
        super().__init__(game)
        
        # Create panel
        panel_width = WIDTH // 1.5
        panel_height = HEIGHT // 1.5
        panel_x = WIDTH // 2 - panel_width // 2
        panel_y = HEIGHT // 2 - panel_height // 2
        self.panel = Panel(panel_x, panel_y, panel_width, panel_height)
        
        # Title
        self.title_font = pg.font.SysFont(None, 64)
        self.title_text = AnimatedText(
            "Credits", 
            self.title_font, 
            TEAL, 
            WIDTH // 2, 
            panel_y + 50,
            "pulse"
        )
        self.animated_elements.append(self.title_text)
        
        # Credits content
        self.content_font = pg.font.SysFont(None, 32)
        self.credits = [
            ("Game Concept", "SUPERSEED: The Debt Escape"),
            ("Character Design", "Teal Frog - Prisoner & Wizard Forms"),
            ("Level Design", "Prison Escape & Financial District"),
            ("Programming", "Python with Pygame & Pymunk"),
            ("Visual Effects", "3D Shadows, Parallax Backgrounds, Animations"),
            ("Theme", "Blockchain finance & debt freedom")
        ]
        
        # Back button
        self.back_button = Button(
            WIDTH // 2 - BUTTON_WIDTH // 2, 
            panel_y + panel_height - BUTTON_HEIGHT - MENU_PADDING, 
            BUTTON_WIDTH, 
            BUTTON_HEIGHT, 
            "Back", 
            action=lambda: "back"
        )
        self.buttons.append(self.back_button)
        
    def draw_background(self, surface):
        """Draw credits screen background"""
        # Draw semi-transparent overlay
        overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        
        # Draw panel background
        self.panel.draw(surface)
        
        # Calculate panel bounds
        panel_content_x = self.panel.rect.x + MENU_PADDING
        panel_content_width = self.panel.rect.width - (MENU_PADDING * 2)
        panel_center_x = self.panel.rect.centerx
        
        # Draw credits list - adjusted to fit within panel bounds
        start_y = self.panel.rect.y + 120  # Start below title
        line_height = 45  # Reduced spacing between lines
        
        for i, (role, credit) in enumerate(self.credits):
            # Role text - align right side to panel center with margin
            role_text = self.content_font.render(role, True, WHITE)
            role_rect = role_text.get_rect(right=panel_center_x - 15, top=start_y + i * line_height)
            
            # Make sure text doesn't exceed panel bounds
            if role_rect.left < panel_content_x:
                # Text is too wide, reduce font size
                smaller_font = pg.font.SysFont(None, 28)  # Smaller font
                role_text = smaller_font.render(role, True, WHITE)
                role_rect = role_text.get_rect(right=panel_center_x - 15, top=start_y + i * line_height)
            
            surface.blit(role_text, role_rect)
            
            # Credit text - align left side to panel center with margin
            credit_text = self.content_font.render(credit, True, LIGHT_TEAL)
            credit_rect = credit_text.get_rect(left=panel_center_x + 15, top=start_y + i * line_height)
            
            # Make sure text doesn't exceed panel bounds
            if credit_rect.right > panel_content_x + panel_content_width:
                # Text is too wide, reduce font size
                smaller_font = pg.font.SysFont(None, 26)  # Even smaller font
                credit_text = smaller_font.render(credit, True, LIGHT_TEAL)
                credit_rect = credit_text.get_rect(left=panel_center_x + 15, top=start_y + i * line_height)
            
            surface.blit(credit_text, credit_rect)
            
            # Connecting line - contained within panel
            pg.draw.line(
                surface, 
                DARK_TEAL, 
                (role_rect.right + 5, role_rect.centery), 
                (credit_rect.left - 5, credit_rect.centery), 
                1
            )
