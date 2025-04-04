import pygame as pg
import math
import random
from src.settings import *

# Ensure lightning color and related constants are available
if 'LIGHTNING_COLOR' not in globals():
    LIGHTNING_COLOR = (255, 50, 50)
    LIGHTNING_WARNING_COLOR = (255, 150, 150, 100)
    CRASH_EXPLOSION_PARTICLE_COUNT = 60

class Shadow:
    """Creates a shadow effect for game objects"""
    @staticmethod
    def apply(surface, offset_x=SHADOW_OFFSET_X, offset_y=SHADOW_OFFSET_Y, blur=SHADOW_BLUR, alpha=128):
        """Apply a shadow effect to a surface"""
        # Create a shadow surface with same dimensions
        shadow_surface = pg.Surface(surface.get_size(), pg.SRCALPHA)
        
        # Create mask from original surface alpha channel
        mask = pg.mask.from_surface(surface)
        mask_surface = mask.to_surface(setcolor=SHADOW_COLOR, unsetcolor=(0, 0, 0, 0))
        
        # Apply blur if requested
        if blur > 0:
            for _ in range(blur):
                # Simple blur by scaling down and up
                scale = 0.8
                scaled_size = (int(mask_surface.get_width() * scale), 
                              int(mask_surface.get_height() * scale))
                mask_surface = pg.transform.smoothscale(mask_surface, scaled_size)
                mask_surface = pg.transform.smoothscale(mask_surface, surface.get_size())
        
        # Add shadow to offset position
        shadow_surface.blit(mask_surface, (offset_x, offset_y))
        
        # Create final composite surface
        result_surface = pg.Surface(surface.get_size(), pg.SRCALPHA)
        result_surface.blit(shadow_surface, (0, 0))  # Shadow first
        result_surface.blit(surface, (0, 0))  # Original on top
        
        return result_surface

class Glow:
    """Creates a glow effect around objects"""
    @staticmethod
    def apply(surface, color=TEAL, intensity=GLOW_INTENSITY, expand=2):
        """Apply a glow effect to a surface"""
        # Create glow surface
        glow_surface = pg.Surface(
            (surface.get_width() + expand*2, surface.get_height() + expand*2), 
            pg.SRCALPHA
        )
        
        # Create mask from the original surface
        mask = pg.mask.from_surface(surface)
        outline = mask.outline()
        
        # Draw expanded outline
        for i in range(1, 4):
            for point in outline:
                # Draw multiple points around each outline point for a soft glow
                for dx in range(-i, i+1):
                    for dy in range(-i, i+1):
                        alpha = int(255 * intensity * (1 - (math.sqrt(dx*dx + dy*dy) / 4)))
                        if alpha > 0:
                            pg.draw.circle(
                                glow_surface, 
                                (*color, alpha), 
                                (point[0] + expand + dx, point[1] + expand + dy), 
                                1
                            )
        
        # Create result surface
        result_surface = pg.Surface(
            (surface.get_width() + expand*2, surface.get_height() + expand*2), 
            pg.SRCALPHA
        )
        # Draw glow first
        result_surface.blit(glow_surface, (0, 0))
        # Draw original centered on top
        result_surface.blit(surface, (expand, expand))
        
        return result_surface

class Animation:
    """Manages animations for game objects"""
    def __init__(self, object_type="platform"):
        self.object_type = object_type
        self.time = 0
        
        # Spring animation properties (for bouncy animations)
        self.spring_pos = 0  # Current position
        self.spring_vel = 0  # Current velocity
        self.spring_target = 0  # Target position
        self.spring_strength = ANIMATION_SPRING_STRENGTH
        self.spring_damping = ANIMATION_DAMPING
        
        # Sin wave animation (for smooth bobbing)
        self.sin_amplitude = 0
        self.sin_speed = 1.0
        
        # Set default animation parameters based on object type
        if object_type == "platform":
            self.sin_amplitude = PLATFORM_OSCILLATION_AMOUNT
            self.sin_speed = random.uniform(0.8, 1.2)
        elif object_type == "token":
            self.sin_amplitude = TOKEN_BOB_AMOUNT
            self.sin_speed = TOKEN_BOB_SPEED
        
    def update(self, dt):
        """Update animation state"""
        self.time += dt
        
        # Update spring physics
        if abs(self.spring_target - self.spring_pos) > 0.01 or abs(self.spring_vel) > 0.01:
            # Spring force = displacement * strength - damping * velocity
            spring_force = (self.spring_target - self.spring_pos) * self.spring_strength
            damping_force = -self.spring_vel * self.spring_damping
            
            # Apply forces
            self.spring_vel += (spring_force + damping_force) * dt
            self.spring_pos += self.spring_vel * dt
            
        return self.get_offset()
    
    def get_offset(self):
        """Get current animation offset"""
        # Combine spring physics and sine wave for more natural movement
        if self.object_type == "platform":
            return 0, self.sin_amplitude * math.sin(self.time * self.sin_speed)
        elif self.object_type == "token":
            return 0, self.sin_amplitude * math.sin(self.time * self.sin_speed)
        elif self.object_type == "player_land":
            # Squash when landing
            return 0, self.spring_pos
        else:
            return 0, 0
            
    def trigger_land(self, intensity=1.0):
        """Trigger landing animation"""
        self.spring_vel += 15 * intensity
        
    def trigger_jump(self, intensity=1.0):
        """Trigger jump animation"""
        self.spring_vel -= 10 * intensity

class BuildingDecorations:
    """Generates decorative elements for buildings"""
    @staticmethod
    def apply(surface, color, is_building=True):
        """Apply decorative elements to a building surface"""
        # Create a copy of the original surface
        result = surface.copy()
        width, height = surface.get_size()
        
        if is_building:
            # Add windows to buildings
            num_floors = max(2, height // 40)
            num_windows_per_floor = max(3, width // 50)
            
            window_width = min(30, (width - 20) // num_windows_per_floor)
            window_height = min(20, (height - 20) // num_floors)
            
            for floor in range(num_floors):
                for window in range(num_windows_per_floor):
                    # Only add window with probability based on density
                    if random.random() < BUILDING_DETAILS_DENSITY:
                        window_x = 10 + window * ((width - 20) // num_windows_per_floor)
                        window_y = 10 + floor * ((height - 20) // num_floors)
                        
                        window_rect = pg.Rect(window_x, window_y, window_width - 5, window_height - 5)
                        pg.draw.rect(result, WINDOW_COLOR, window_rect, border_radius=2)
                        
            # Add rooftop details
            if random.random() < 0.7:
                # Antenna or small structure on top
                antenna_width = random.randint(5, 15)
                antenna_height = random.randint(10, 30)
                antenna_x = random.randint(width // 4, 3 * width // 4)
                
                pg.draw.rect(result, 
                           darken_color(color), 
                           (antenna_x, 0, antenna_width, antenna_height))
                
            # Add X mark branding (SUPERSEED theme)
            if random.random() < 0.5:
                x_size = random.randint(20, 40)
                x_x = random.randint(width // 4, 3 * width // 4)
                x_y = random.randint(height // 4, 3 * height // 4)
                
                pg.draw.line(result, TEAL, 
                           (x_x - x_size//2, x_y - x_size//2),
                           (x_x + x_size//2, x_y + x_size//2), 3)
                pg.draw.line(result, TEAL, 
                           (x_x - x_size//2, x_y + x_size//2),
                           (x_x + x_size//2, x_y - x_size//2), 3)
            
        return result
        
class ParallaxBackground:
    """Creates a multi-layered parallax scrolling background"""
    def __init__(self, width, height, level_type="financial"):
        self.width = width
        self.height = height
        self.level_type = level_type
        self.layers = []
        
        # Generate the background layers
        self._generate_layers()
        
    def _generate_layers(self):
        """Generate the parallax background layers based on level type"""
        if self.level_type == "market_crash":
            self._generate_market_crash_layers()
        else:
            self._generate_financial_layers()
            
    def _generate_financial_layers(self):
        """Generate standard financial district background layers"""
        # Layer 1: Far buildings (silhouettes)
        far_layer = pg.Surface((self.width, self.height), pg.SRCALPHA)
        far_layer.fill((0, 0, 0, 0))  # Transparent background
        
        # Draw distant city silhouette
        horizon_y = self.height * 0.6
        for i in range(0, self.width, 60):
            building_width = random.randint(40, 80)
            building_height = random.randint(80, 200)
            building_color = darken_color(random.choice(BUILDING_COLORS), 0.5)
            
            pg.draw.rect(far_layer, building_color, 
                       (i, horizon_y - building_height, building_width, building_height))
        
        # Layer 2: Mid buildings
        mid_layer = pg.Surface((self.width, self.height), pg.SRCALPHA)
        mid_layer.fill((0, 0, 0, 0))  # Transparent background
        
        horizon_y = self.height * 0.65
        for i in range(-20, self.width, 100):
            building_width = random.randint(70, 120)
            building_height = random.randint(120, 280)
            building_color = darken_color(random.choice(BUILDING_COLORS), 0.3)
            
            building_surface = pg.Surface((building_width, building_height), pg.SRCALPHA)
            building_surface.fill(building_color)
            
            # Add some windows to mid-layer buildings
            decorated_building = BuildingDecorations.apply(building_surface, building_color)
            mid_layer.blit(decorated_building, (i, horizon_y - building_height))
            
        # Layer 3: Clouds/sky elements
        cloud_layer = pg.Surface((self.width, self.height), pg.SRCALPHA)
        cloud_layer.fill((0, 0, 0, 0))  # Transparent background
        
        # Add some subtle clouds
        for _ in range(10):
            cloud_x = random.randint(0, self.width)
            cloud_y = random.randint(50, int(self.height * 0.4))
            cloud_radius = random.randint(30, 70)
            
            # Draw cloud as a cluster of circles
            cloud_color = (200, 220, 230, 50)  # Very transparent white
            for i in range(5):
                offset_x = random.randint(-20, 20)
                offset_y = random.randint(-10, 10)
                size_mod = random.uniform(0.7, 1.3)
                
                pg.draw.circle(
                    cloud_layer, 
                    cloud_color, 
                    (cloud_x + offset_x, cloud_y + offset_y), 
                    cloud_radius * size_mod
                )
                
        # Store all layers with their parallax factors
        self.layers = [
            {"surface": cloud_layer, "factor": 0.1},
            {"surface": far_layer, "factor": 0.3},
            {"surface": mid_layer, "factor": 0.6}
        ]
        
    def _generate_market_crash_layers(self):
        """Generate market crash themed background layers"""
        # Layer 1: Distant buildings with cracks and damage
        far_layer = pg.Surface((self.width, self.height), pg.SRCALPHA)
        far_layer.fill((0, 0, 0, 0))  # Transparent background
        
        # Draw distant city silhouette with damaged buildings
        horizon_y = self.height * 0.6
        for i in range(0, self.width, 60):
            building_width = random.randint(40, 80)
            building_height = random.randint(80, 200)
            
            # Darker, more dramatic color palette for market crash
            building_color = darken_color((
                random.randint(50, 70),  # Dark red tones
                random.randint(20, 40),
                random.randint(40, 60)
            ), 0.7)
            
            # Draw the building
            pg.draw.rect(far_layer, building_color, 
                       (i, horizon_y - building_height, building_width, building_height))
            
            # Add cracks/damage to some buildings
            if random.random() < 0.4:
                # Draw crack lines
                crack_start_x = i + random.randint(0, building_width)
                crack_start_y = horizon_y - building_height + random.randint(0, building_height // 3)
                
                # Create jagged crack line
                crack_points = [(crack_start_x, crack_start_y)]
                current_x, current_y = crack_start_x, crack_start_y
                
                for _ in range(random.randint(3, 6)):
                    current_x += random.randint(-10, 10)
                    current_y += random.randint(10, 20)
                    if current_y > horizon_y:
                        break
                    crack_points.append((current_x, current_y))
                
                if len(crack_points) > 1:
                    pg.draw.lines(far_layer, (30, 30, 30), False, crack_points, 2)
        
        # Layer 2: Mid-distance elements - broken/tilted buildings
        mid_layer = pg.Surface((self.width, self.height), pg.SRCALPHA)
        mid_layer.fill((0, 0, 0, 0))  # Transparent background
        
        horizon_y = self.height * 0.65
        for i in range(-20, self.width, 120):
            building_width = random.randint(70, 120)
            building_height = random.randint(120, 280)
            
            # Darker color palette
            building_color = (
                random.randint(60, 90),  # Dark red-purple tones
                random.randint(30, 50),
                random.randint(50, 70)
            )
            
            # Create building surface
            building_surface = pg.Surface((building_width, building_height), pg.SRCALPHA)
            building_surface.fill(building_color)
            
            # Add some windows to mid-layer buildings
            decorated_building = BuildingDecorations.apply(building_surface, building_color)
            
            # Randomly tilt some buildings for "crash" effect
            if random.random() < 0.3:
                tilt_angle = random.uniform(-10, 10)
                decorated_building = pg.transform.rotate(decorated_building, tilt_angle)
            
            # Position the building
            blit_x = i
            blit_y = horizon_y - building_height
            
            # Add a broken/damaged effect to some buildings
            if random.random() < 0.4:
                # Create a "broken top" effect 
                broken_height = random.randint(20, 50)
                broken_width = random.randint(20, building_width - 20)
                broken_x = random.randint(0, building_width - broken_width)
                
                # Remove part of the top by drawing a black rectangle
                pg.draw.rect(decorated_building, (0, 0, 0, 0), 
                           (broken_x, 0, broken_width, broken_height))
            
            # Blit the building
            mid_layer.blit(decorated_building, (blit_x, blit_y))
            
        # Layer 3: Foreground elements - falling stock charts and debris
        foreground_layer = pg.Surface((self.width, self.height), pg.SRCALPHA)
        foreground_layer.fill((0, 0, 0, 0))  # Transparent background
        
        # Add falling chart lines
        for _ in range(15):
            # Draw downward trending stock lines
            start_x = random.randint(0, self.width)
            start_y = random.randint(0, self.height // 2)
            
            # Create downward points with occasional small upward movements
            chart_points = [(start_x, start_y)]
            x, y = start_x, start_y
            
            for _ in range(random.randint(5, 10)):
                x += random.randint(20, 50)
                # Mostly downward with occasional small recovery
                if random.random() < 0.7:
                    y += random.randint(20, 40)  # Down
                else:
                    y -= random.randint(5, 15)  # Small recovery
                
                chart_points.append((x, y))
                
                # Stop if we reach the bottom
                if y > self.height:
                    break
            
            # Draw the stock chart line
            if len(chart_points) > 1:
                line_color = (200, 50, 50, 100)  # Red, semi-transparent
                pg.draw.lines(foreground_layer, line_color, False, chart_points, 2)
                
                # Add "X" markers at key points
                for i in range(1, len(chart_points), 2):
                    x, y = chart_points[i]
                    marker_size = 5
                    pg.draw.line(foreground_layer, (255, 0, 0, 150), 
                               (x - marker_size, y - marker_size),
                               (x + marker_size, y + marker_size), 2)
                    pg.draw.line(foreground_layer, (255, 0, 0, 150), 
                               (x - marker_size, y + marker_size),
                               (x + marker_size, y - marker_size), 2)
        
        # Add floating debris particles
        for _ in range(30):
            debris_x = random.randint(0, self.width)
            debris_y = random.randint(0, self.height)
            debris_size = random.randint(2, 6)
            
            # Random debris color - dark tones
            debris_color = (
                random.randint(50, 100),
                random.randint(20, 60),
                random.randint(20, 60),
                random.randint(50, 150)  # Semi-transparent
            )
            
            # Draw debris as small rectangles or circles
            if random.random() < 0.5:
                pg.draw.rect(foreground_layer, debris_color, 
                           (debris_x, debris_y, debris_size, debris_size))
            else:
                pg.draw.circle(foreground_layer, debris_color, 
                             (debris_x, debris_y), debris_size)
        
        # Store all layers with their parallax factors
        self.layers = [
            {"surface": foreground_layer, "factor": 0.8},  # Fast moving foreground
            {"surface": mid_layer, "factor": 0.5},         # Mid-ground
            {"surface": far_layer, "factor": 0.3}          # Background
        ]
        
    def draw(self, surface, camera_x):
        """Draw all parallax layers"""
        for layer in self.layers:
            # Calculate offset based on camera position and parallax factor
            offset_x = int(camera_x * layer["factor"]) % self.width
            
            # Draw the layer, repeating horizontally if needed
            surface.blit(layer["surface"], (-offset_x, 0))
            
            # If we need to tile the image horizontally
            if offset_x > 0:
                surface.blit(layer["surface"], (self.width - offset_x, 0))
                
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
