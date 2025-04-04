import pygame as pg
import math
import random
from src.settings import *

# Utility functions for color manipulation
def darken_color(color, amount=0.7):
    """Utility to darken a color by a specified amount"""
    r, g, b = color[:3]
    return (
        int(r * amount),
        int(g * amount),
        int(b * amount)
    )
    
def lighten_color(color, amount=0.3):
    """Utility to lighten a color"""
    r, g, b = color[:3]
    return (
        min(255, int(r + (255 - r) * amount)),
        min(255, int(g + (255 - g) * amount)),
        min(255, int(b + (255 - b) * amount))
    )

class Button:
    """Interactive button for menus"""
    def __init__(self, x, y, width, height, text, font_size=32, action=None):
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        self.font = pg.font.SysFont(None, font_size)
        self.action = action
        
        # Button states
        self.normal_color = DARK_TEAL
        self.hover_color = TEAL
        self.text_color = WHITE
        self.border_color = LIGHT_TEAL
        self.is_hovered = False
        
        # Animation properties
        self.pulse_effect = 0
        self.alpha = 255  # For transparency effects
        
    def update(self, mouse_pos, elapsed_time):
        """Update button state based on mouse position"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Update pulse animation
        self.pulse_effect = (self.pulse_effect + 0.05) % (2 * math.pi)
        
    def draw(self, surface):
        """Draw the button on the given surface with enhanced 3D effect"""
        # Determine button color based on state
        button_color = self.hover_color if self.is_hovered else self.normal_color
        
        # Add pulse effect if hovered
        if self.is_hovered:
            # Pulsating border width
            border_width = int(3 + math.sin(self.pulse_effect) * 2)
            # Add a glow effect when hovered
            glow_rect = pg.Rect(
                self.rect.x - 5, 
                self.rect.y - 5, 
                self.rect.width + 10, 
                self.rect.height + 10
            )
            glow_size = int(4 + math.sin(self.pulse_effect * 2) * 2)  # Pulsating glow
            glow_alpha = int(40 + math.sin(self.pulse_effect * 3) * 15)  # Pulsating alpha
            
            # Draw glow as a series of increasingly transparent rects
            for i in range(glow_size, 0, -1):
                glow_alpha_step = glow_alpha * (1 - i/glow_size)
                expanded_rect = pg.Rect(
                    glow_rect.x - i, 
                    glow_rect.y - i, 
                    glow_rect.width + i*2, 
                    glow_rect.height + i*2
                )
                pg.draw.rect(
                    surface, 
                    (*BRIGHT_TEAL, glow_alpha_step), 
                    expanded_rect, 
                    border_radius=8+i
                )
        else:
            border_width = 2
        
        # Create shadow effect (darker version underneath, slightly offset)
        shadow_rect = pg.Rect(
            self.rect.x + 4,
            self.rect.y + 4,
            self.rect.width,
            self.rect.height
        )
        pg.draw.rect(surface, darken_color(button_color, 0.5), shadow_rect, border_radius=8)
            
        # Draw button background with 3D effect
        pg.draw.rect(surface, button_color, self.rect, border_radius=8)
        
        # Add subtle gradient highlight at top of button (3D effect)
        highlight_rect = pg.Rect(
            self.rect.x + 2,
            self.rect.y + 2,
            self.rect.width - 4,
            self.rect.height // 3
        )
        highlight_color = lighten_color(button_color, 0.2)
        pg.draw.rect(surface, highlight_color, highlight_rect, border_radius=6)
        
        # Draw button border
        pg.draw.rect(surface, self.border_color, self.rect, 
                    width=border_width, border_radius=8)
        
        # Draw text with a slight shadow for depth
        shadow_offset = 2
        shadow_text = self.font.render(self.text, True, (0, 0, 0, 100))
        shadow_rect = shadow_text.get_rect(center=(self.rect.centerx + shadow_offset, self.rect.centery + shadow_offset))
        surface.blit(shadow_text, shadow_rect)
        
        # Draw main text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        """Handle mouse events on button"""
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:  # Left click
                if self.action:
                    return self.action()
        return False

class Panel:
    """UI panel for containing content"""
    def __init__(self, x, y, width, height, color=None, alpha=200):
        self.rect = pg.Rect(x, y, width, height)
        self.color = color or BLACK
        self.alpha = alpha
        self.border_color = TEAL
        self.shadow_size = 8  # Size of drop shadow
        self.inner_glow = True  # Whether to add subtle inner glow
        
    def draw(self, surface):
        """Draw the panel with semi-transparency and enhanced visuals"""
        # Create shadow first (slightly larger, offset, and darker)
        shadow_rect = pg.Rect(
            self.rect.x + self.shadow_size,
            self.rect.y + self.shadow_size,
            self.rect.width,
            self.rect.height
        )
        shadow_surface = pg.Surface((shadow_rect.width + self.shadow_size, 
                                   shadow_rect.height + self.shadow_size), pg.SRCALPHA)
        
        # Draw blurred shadow (multiple overlapping rects with decreasing opacity)
        for i in range(self.shadow_size, 0, -1):
            shadow_alpha = 20 * (1 - i/self.shadow_size)  # Fade out shadow edges
            shadow_rect_blur = pg.Rect(
                i, i, 
                shadow_rect.width - i, 
                shadow_rect.height - i
            )
            pg.draw.rect(
                shadow_surface, 
                (0, 0, 0, shadow_alpha), 
                shadow_rect_blur, 
                border_radius=12
            )
            
        # Draw shadow to main surface
        surface.blit(shadow_surface, (self.rect.x, self.rect.y))
        
        # Create a transparent surface for the panel
        panel_surface = pg.Surface((self.rect.width, self.rect.height), pg.SRCALPHA)
        
        # Base panel fill
        pg.draw.rect(panel_surface, (*self.color, self.alpha), 
                    (0, 0, self.rect.width, self.rect.height), border_radius=12)
        
        # Add subtle gradient for depth (darker at bottom)
        gradient_height = self.rect.height // 3
        for i in range(gradient_height):
            # Calculate gradient opacity (increases toward bottom)
            alpha = int(40 * (i / gradient_height))
            gradient_rect = pg.Rect(
                0, 
                self.rect.height - gradient_height + i,
                self.rect.width,
                1
            )
            pg.draw.rect(panel_surface, (0, 0, 0, alpha), gradient_rect)
            
        # Add inner glow if enabled (subtle highlight around edges)
        if self.inner_glow:
            glow_size = 4
            for i in range(glow_size, 0, -1):
                # Decreasing alpha for softer glow
                glow_alpha = int(10 * (1 - i/glow_size))
                glow_rect = pg.Rect(
                    i, 
                    i, 
                    self.rect.width - i*2, 
                    self.rect.height - i*2
                )
                pg.draw.rect(
                    panel_surface, 
                    (*LIGHT_TEAL, glow_alpha), 
                    glow_rect, 
                    border_radius=12-i
                )
        
        # Draw outer border (with more pronounced teal color)
        pg.draw.rect(panel_surface, self.border_color, 
                    (0, 0, self.rect.width, self.rect.height), 
                    width=2, border_radius=12)
        
        # Draw subtle inner border highlight (top and left edges)
        highlight_alpha = 30
        pg.draw.line(
            panel_surface,
            (*WHITE, highlight_alpha),
            (12, 2),  # Start at top-left corner (adjusted for border radius)
            (self.rect.width - 12, 2),  # Horizontal top edge
            1
        )
        pg.draw.line(
            panel_surface,
            (*WHITE, highlight_alpha),
            (2, 12),  # Start at top-left corner (adjusted for border radius)
            (2, self.rect.height - 12),  # Vertical left edge
            1
        )
        
        # Draw to the target surface
        surface.blit(panel_surface, self.rect)
        
class FadeEffect:
    """Creates fade in/out transitions"""
    def __init__(self, duration=1.0, color=BLACK):
        self.duration = duration
        self.color = color
        self.progress = 0.0  # 0 = transparent, 1 = opaque
        self.fading_in = False
        self.fading_out = False
        
    def start_fade_in(self):
        """Start fade in transition"""
        self.progress = 1.0
        self.fading_in = True
        self.fading_out = False
        
    def start_fade_out(self):
        """Start fade out transition"""
        self.progress = 0.0
        self.fading_in = False
        self.fading_out = True
        
    def update(self, dt):
        """Update fade effect"""
        if self.fading_in:
            self.progress -= dt / self.duration
            if self.progress <= 0:
                self.progress = 0
                self.fading_in = False
                return True  # Fade completed
                
        elif self.fading_out:
            self.progress += dt / self.duration
            if self.progress >= 1:
                self.progress = 1
                self.fading_out = False
                return True  # Fade completed
                
        return False
        
    def draw(self, surface):
        """Draw the fade effect"""
        if self.progress > 0:
            # Create temporary surface with the fade color and alpha
            fade_surface = pg.Surface((surface.get_width(), surface.get_height()))
            fade_surface.fill(self.color)
            fade_surface.set_alpha(int(255 * self.progress))
            surface.blit(fade_surface, (0, 0))

class AnimatedText:
    """Text with animated effects like typing or pulsing"""
    def __init__(self, text, font, color, x, y, animation_type="pulse"):
        self.full_text = text
        self.displayed_text = text
        self.font = font
        self.color = color
        self.position = (x, y)
        self.animation_type = animation_type
        
        # Animation properties
        self.timer = 0
        self.pulse_value = 0
        self.char_index = 0
        self.typing_speed = 0.05  # seconds per character
        
    def update(self, dt):
        """Update text animation"""
        self.timer += dt
        
        if self.animation_type == "pulse":
            # Pulsing effect (subtle color/size change)
            self.pulse_value = (math.sin(self.timer * 2) + 1) / 2
            
        elif self.animation_type == "typing":
            # Typing effect (characters appear one by one)
            if self.char_index < len(self.full_text):
                if self.timer >= self.typing_speed:
                    self.char_index += 1
                    self.displayed_text = self.full_text[:self.char_index]
                    self.timer = 0
                    
    def draw(self, surface):
        """Draw animated text on the given surface"""
        if self.animation_type == "pulse":
            # Create a slightly altered color based on pulse
            pulse_color = (
                min(255, self.color[0] + int(20 * self.pulse_value)),
                min(255, self.color[1] + int(20 * self.pulse_value)),
                min(255, self.color[2] + int(20 * self.pulse_value))
            )
            
            text_surface = self.font.render(self.displayed_text, True, pulse_color)
            # Slightly scale the text based on pulse
            scale = 1.0 + 0.05 * self.pulse_value
            scaled_size = (int(text_surface.get_width() * scale), 
                          int(text_surface.get_height() * scale))
            scaled_text = pg.transform.scale(text_surface, scaled_size)
            
            # Center the text at the original position
            pos = (self.position[0] - scaled_text.get_width() // 2,
                  self.position[1] - scaled_text.get_height() // 2)
            surface.blit(scaled_text, pos)
            
        else:
            # Standard or typing animation
            text_surface = self.font.render(self.displayed_text, True, self.color)
            text_rect = text_surface.get_rect(center=self.position)
            surface.blit(text_surface, text_rect)
            
class ParticleSystem:
    """System for creating and managing particles"""
    def __init__(self, particle_type="x_mark", max_particles=50):
        self.particles = []
        self.particle_type = particle_type
        self.max_particles = max_particles
        
    def add_particle(self, pos, velocity, size, color, lifetime=1.0):
        """Add a new particle to the system"""
        if len(self.particles) < self.max_particles:
            self.particles.append({
                'pos': list(pos),
                'velocity': list(velocity),
                'size': size,
                'color': color,
                'lifetime': lifetime,
                'age': 0,
                'rotation': 0,
                'rotation_speed': random.uniform(-5, 5)
            })
            
    def spawn_particles(self, pos, count, spread=10, color=None):
        """Spawn multiple particles at once"""
        for _ in range(count):
            # Random velocity direction
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(20, 50)
            velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
            
            # Random position within spread
            spawn_pos = [
                pos[0] + random.uniform(-spread, spread),
                pos[1] + random.uniform(-spread, spread)
            ]
            
            # Random size and color variation
            size = random.uniform(5, 15)
            
            # Determine particle color
            if color is not None:
                # Use provided color with slight variation
                particle_color = (
                    max(0, min(255, color[0] + random.randint(-20, 20))),
                    max(0, min(255, color[1] + random.randint(-20, 20))),
                    max(0, min(255, color[2] + random.randint(-20, 20)))
                )
            elif self.particle_type == "x_mark":
                particle_color = TEAL
            else:
                # Default color variation for generic particles
                particle_color = (
                    max(0, min(255, TEAL[0] + random.randint(-20, 20))),
                    max(0, min(255, TEAL[1] + random.randint(-20, 20))),
                    max(0, min(255, TEAL[2] + random.randint(-20, 20)))
                )
                
            self.add_particle(spawn_pos, velocity, size, particle_color, 
                            random.uniform(0.5, 2.0))
            
    def update(self, dt):
        """Update all particles in the system"""
        for particle in self.particles[:]:
            # Update age
            particle['age'] += dt
            if particle['age'] >= particle['lifetime']:
                self.particles.remove(particle)
                continue
                
            # Apply velocity
            particle['pos'][0] += particle['velocity'][0] * dt
            particle['pos'][1] += particle['velocity'][1] * dt
            
            # Apply gravity (optional - for falling particles)
            # particle['velocity'][1] += 50 * dt
            
            # Update rotation for spinning particles
            particle['rotation'] += particle['rotation_speed'] * dt
            
            # Slow down over time
            drag = 0.95
            particle['velocity'][0] *= drag
            particle['velocity'][1] *= drag
            
    def draw(self, surface):
        """Draw all particles"""
        for particle in self.particles:
            # Calculate alpha (fade out as particle ages)
            progress = particle['age'] / particle['lifetime']
            alpha = int(255 * (1 - progress))
            
            # Calculate size (can shrink as particle ages)
            current_size = particle['size'] * (1 - progress * 0.5)
            
            # Draw based on particle type
            if self.particle_type == "x_mark":
                self.draw_x_mark(surface, particle, alpha, current_size)
            elif self.particle_type == "lightning":
                self.draw_lightning(surface, particle, alpha, current_size)
            else:
                self.draw_circle(surface, particle, alpha, current_size)
                
    def draw_circle(self, surface, particle, alpha, size):
        """Draw a circular particle"""
        # Create a surface for the particle with alpha channel
        particle_surface = pg.Surface((int(size * 2), int(size * 2)), pg.SRCALPHA)
        
        # Draw circle with alpha
        pg.draw.circle(
            particle_surface, 
            (*particle['color'], alpha), 
            (int(size), int(size)), 
            int(size)
        )
        
        # Blit to main surface
        surface.blit(
            particle_surface, 
            (int(particle['pos'][0] - size), int(particle['pos'][1] - size))
        )
        
    def draw_x_mark(self, surface, particle, alpha, size):
        """Draw an X mark particle"""
        # Create a surface with alpha channel
        particle_surface = pg.Surface((int(size * 2), int(size * 2)), pg.SRCALPHA)
        
        # Draw X mark with alpha
        line_width = max(1, int(size / 4))
        pg.draw.line(
            particle_surface,
            (*particle['color'], alpha),
            (0, 0),
            (size * 2, size * 2),
            line_width
        )
        pg.draw.line(
            particle_surface,
            (*particle['color'], alpha),
            (0, size * 2),
            (size * 2, 0),
            line_width
        )
        
        # Rotate the X mark
        rotated_surface = pg.transform.rotate(
            particle_surface, 
            particle['rotation']
        )
        
        # Blit to main surface
        surface.blit(
            rotated_surface,
            (
                int(particle['pos'][0] - rotated_surface.get_width() / 2),
                int(particle['pos'][1] - rotated_surface.get_height() / 2)
            )
        )
        
    def draw_lightning(self, surface, particle, alpha, size):
        """Draw a lightning particle for electrocution effects"""
        # Create a surface with alpha channel (larger to accommodate jagged lightning)
        lightning_size = int(size * 3)  # Larger surface for lightning bolt
        particle_surface = pg.Surface((lightning_size, lightning_size), pg.SRCALPHA)
        
        # Lightning bolt parameters
        center_x, center_y = lightning_size // 2, lightning_size // 2
        segments = 3 + int(size / 5)  # More segments for larger bolts
        segment_length = size / segments
        thickness = max(1, int(size / 6))
        
        # Draw a jagged lightning bolt with multiple branches
        # Main bolt
        start_x, start_y = center_x, center_y - lightning_size // 3
        end_x, end_y = center_x, center_y + lightning_size // 3
        
        # Generate lightning path
        points = [(start_x, start_y)]
        current_x, current_y = start_x, start_y
        
        for i in range(segments):
            # Calculate progress along main direction
            progress = (i + 1) / segments
            target_y = start_y + (end_y - start_y) * progress
            
            # Add randomness to x position (zigzag)
            jitter = (segment_length * 1.2) * (1 - progress)  # Less jitter toward end
            current_x = center_x + random.uniform(-jitter, jitter)
            current_y = target_y
            
            points.append((current_x, current_y))
        
        # Draw main lightning bolt
        if len(points) > 1:
            # Create a glow effect
            for i in range(3):  # Multiple passes for glow
                glow_alpha = alpha // (i+2)  # Decreasing alpha for glow layers
                glow_width = thickness + i*2  # Increasing width for glow layers
                
                pg.draw.lines(
                    particle_surface,
                    (*particle['color'], glow_alpha),
                    False,  # Don't connect last point to first
                    points,
                    glow_width
                )
            
            # Draw the main bright center
            pg.draw.lines(
                particle_surface,
                (255, 255, 255, alpha),  # White center for brightness
                False,
                points,
                max(1, thickness // 2)
            )
            
        # Add occasional branches (with 40% probability)
        if random.random() < 0.4 and len(points) > 2:
            # Pick a random point along the main bolt to branch from
            branch_index = random.randint(1, len(points) - 2)
            branch_start = points[branch_index]
            
            # Create a short branch (30-60% of main bolt length)
            branch_segments = max(2, segments // 2)
            branch_points = [branch_start]
            
            # Random branch direction
            branch_angle = random.uniform(math.pi/4, math.pi/2) * random.choice([-1, 1])
            
            for i in range(branch_segments):
                # Calculate branch growth with decreasing length
                branch_length = segment_length * (1 - i/branch_segments) * 0.8
                
                # Calculate next point
                next_x = branch_points[-1][0] + math.cos(branch_angle) * branch_length
                next_y = branch_points[-1][1] + math.sin(branch_angle) * branch_length
                
                branch_points.append((next_x, next_y))
                
                # Slightly adjust angle for zigzag effect
                branch_angle += random.uniform(-math.pi/6, math.pi/6)
            
            # Draw the branch with glow
            for i in range(2):
                branch_glow_alpha = (alpha // 2) // (i+2)
                branch_glow_width = max(1, thickness // 2) + i
                
                pg.draw.lines(
                    particle_surface,
                    (*particle['color'], branch_glow_alpha),
                    False,
                    branch_points,
                    branch_glow_width
                )
        
        # Rotate the lightning bolt
        rotated_surface = pg.transform.rotate(
            particle_surface, 
            particle['rotation'] * 0.5  # Slower rotation for lightning
        )
        
        # Blit to main surface
        surface.blit(
            rotated_surface,
            (
                int(particle['pos'][0] - rotated_surface.get_width() / 2),
                int(particle['pos'][1] - rotated_surface.get_height() / 2)
            )
        )
