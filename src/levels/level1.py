import pygame as pg
import pymunk
import random
import math
from src.settings import *
from src.sprites import Platform, SuperseedToken
from src.interactive import Door
from src.levels.base_level import BaseLevel

class Level1(BaseLevel):
    """Level 1: Teal X Obstacle Course - The first level with simple mechanics"""
    def __init__(self, game):
        self.level_num = 1
        super().__init__(game)
        
    def setup_level(self):
        """Setup the Teal X Obstacle Course level"""
        # Set level dimensions
        self.width = WIDTH * 3
        self.height = HEIGHT
        self.death_height = HEIGHT + 50
        
        # Set player starting position
        self.start_x = 150
        self.start_y = HEIGHT - 240
        
        # Set spawn protection time
        self.spawn_protection_time = 1.0
        
        # Add ceiling to prevent super high jumps
        ceiling = self.add_platform(0, 0, self.width, 20)
        
        # Starting platform (safe area)
        start_platform = self.add_platform(50, HEIGHT - 200, 300, 20, "building")
        
        # Create level sections
        self.create_basic_jumps()      # Section 1: Basic jumps with increasing difficulty
        self.create_vertical_section()  # Section 2: Vertical challenges
        self.create_moving_section()    # Section 3: Moving platforms
        self.create_final_section()     # Section 4: Final stretch with exit door
        
        # Add boundary walls
        self.add_boundary_walls()
        
        # Ensure we have exactly the right number of tokens
        self.ensure_token_count(LEVEL_DOOR_TOKENS_REQUIRED)
        
    def create_basic_jumps(self):
        """Create section 1: Basic jumps with increasing difficulty"""
        section1_y = HEIGHT - 200  # Same height as starting platform
        
        # Series of platforms with increasing gaps
        platforms_section1 = [
            # [x, y, width, height]
            [350, section1_y, 150, 20],
            [600, section1_y, 120, 20],
            [820, section1_y, 100, 20],
            [1050, section1_y, 80, 20],
        ]
        
        # Guaranteed token count
        tokens_added = 0
        
        for i, p in enumerate(platforms_section1):
            plat = self.add_platform(*p, platform_type="building")
            
            # Always add tokens on all platforms for better consistency
            token_x = p[0] + p[2] // 2
            token_y = p[1] - 60
            token_type = self.token_types[i % len(self.token_types)]
            self.add_token(token_x, token_y, token_type=token_type)
            tokens_added += 1
            
        # For debugging
        print(f"Basic jumps section: {tokens_added} tokens")
    
    def create_vertical_section(self):
        """Create section 2: Vertical challenges with platforms at different heights"""
        section2_x = 1250
        
        # Create a vertical series of smaller platforms
        platform_heights = [
            HEIGHT - 200,  # Same as section 1
            HEIGHT - 280,
            HEIGHT - 360,
            HEIGHT - 420,  # Peak
            HEIGHT - 380,
            HEIGHT - 300,
            HEIGHT - 200,
        ]
        
        for i, y in enumerate(platform_heights):
            x = section2_x + i * 120
            width = 80 if i != 3 else 50  # Make middle platform smaller for challenge
            
            plat = self.add_platform(x, y, width, 20, platform_type="building")
            
            # Add token at peak height platform
            if i == 3:  # Highest platform
                token_type = self.token_types[random.randint(0, len(self.token_types)-1)]
                self.add_token(x + width // 2, y - 60, token_type=token_type)
            
            # Also add token at one more platform in this section (the descent)
            if i == 5:  # One of the descent platforms
                token_type = self.token_types[random.randint(0, len(self.token_types)-1)]
                self.add_token(x + width // 2, y - 60, token_type=token_type)
    
    def create_moving_section(self):
        """Create section 3: Moving platforms with strategically placed tokens"""
        section3_x = 2050
        section3_y = HEIGHT - 250
        
        # Series of moving platforms with carefully placed tokens
        moving_platform_data = [
            # x, y, width, height, movement_distance, speed_multiplier
            [section3_x, section3_y, 100, 20, 150, 1.0],
            [section3_x + 250, section3_y - 50, 80, 20, 100, 1.2],
            [section3_x + 450, section3_y, 120, 20, 200, 1.5],
            [section3_x + 700, section3_y + 30, 100, 20, 120, 1.8],
        ]
        
        for i, data in enumerate(moving_platform_data):
            plat = self.add_platform(
                data[0], data[1], data[2], data[3], 
                platform_type="floating", 
                moving=True, 
                move_distance=data[4], 
                move_speed=PLATFORM_SPEED * data[5]
            )
            
            # Add token above all moving platforms - they're guaranteed to ensure level completion
            token_type = self.token_types[i % len(self.token_types)]
            self.add_token(data[0] + data[2] // 2, data[1] - 60, token_type=token_type)
    
    def create_final_section(self):
        """Create section 4: Final stretch with increasingly challenging jumps"""
        final_x = 2800  # Start position for final section
        final_y = HEIGHT - 220
        
        # Create a series of small platforms for the final stretch
        final_platforms = [
            [final_x, final_y, 60, 20],
            [final_x + 150, final_y - 40, 50, 20],
            [final_x + 300, final_y, 60, 20],
            [final_x + 450, final_y - 30, 70, 20],
            [final_x + 600, final_y, 200, 20],  # End platform
        ]
        
        for i, p in enumerate(final_platforms):
            plat = self.add_platform(*p, platform_type="building")
            
            # Add token to final platform and one of the approach platforms
            if i == len(final_platforms) - 1 or i == 2:
                token_y = p[1] - 60
                # Special logo token for final platform
                token_type = "logo_token" if i == len(final_platforms) - 1 else self.token_types[random.randint(0, len(self.token_types)-1)]
                self.add_token(p[0] + p[2] // 2, token_y, token_type=token_type)
        
        # Add exit door on the last platform
        last_platform = final_platforms[-1]
        door_x = last_platform[0] + last_platform[2] - 100
        door_y = last_platform[1] - 120
        
        self.add_exit_door(door_x, door_y, LEVEL_DOOR_TOKENS_REQUIRED)
    
    def ensure_token_count(self, required_tokens):
        """Ensure we have exactly the required number of tokens in the level"""
        current_token_count = len(self.tokens)
        
        if current_token_count < required_tokens:
            # Add more tokens at strategic locations
            tokens_needed = required_tokens - current_token_count
            
            # Guaranteed positions that are always accessible
            guaranteed_positions = [
                [400, HEIGHT - 300],    # Above first section
                [700, HEIGHT - 350],    # Between platforms
                [950, HEIGHT - 400],    # Near vertical section
                [1500, HEIGHT - 350],   # After vertical section
                [1850, HEIGHT - 300],   # Before moving platforms
                [2350, HEIGHT - 350],   # Between moving platforms
                [2600, HEIGHT - 300]    # Before final section
            ]
            
            # Use as many guaranteed positions as needed
            for i in range(min(tokens_needed, len(guaranteed_positions))):
                pos = guaranteed_positions[i]
                token_type = self.token_types[random.randint(0, len(self.token_types)-1)]
                self.add_token(pos[0], pos[1], token_type=token_type)
                
            # If we still need more tokens, add them at percentage positions
            if tokens_needed > len(guaranteed_positions):
                remaining = tokens_needed - len(guaranteed_positions)
                for i in range(remaining):
                    # Position based on percentage through level
                    segment = (i + 1) / (remaining + 1)
                    token_x = int(segment * (self.width - 400)) + 200
                    
                    # Position at slightly different heights
                    token_y = HEIGHT - 300 - random.randint(0, 50)
                    
                    token_type = self.token_types[random.randint(0, len(self.token_types)-1)]
                    self.add_token(token_x, token_y, token_type=token_type)
        
        elif current_token_count > required_tokens:
            # Remove excess tokens
            excess = current_token_count - required_tokens
            tokens_list = list(self.tokens)
            
            # Remove random tokens until we have exactly the required number
            for _ in range(excess):
                if tokens_list:
                    token = random.choice(tokens_list)
                    tokens_list.remove(token)
                    self.tokens.remove(token)
                    self.game.space.remove(token.shape, token.body)
        
        # Verify token count again
        final_count = len(self.tokens)
        if final_count != required_tokens:
            print(f"Warning: Level 1 expected {required_tokens} tokens but has {final_count}")
