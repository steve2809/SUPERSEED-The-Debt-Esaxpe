import pygame as pg
import pymunk
import random
import math
from src.settings import *
from src.sprites import Platform, SuperseedToken
from src.interactive import Door
from src.levels.base_level import BaseLevel

class Level2(BaseLevel):
    """Level 2: Financial District - More complex level with building-themed platforms"""
    def __init__(self, game):
        self.level_num = 2
        super().__init__(game)
        
    def setup_level(self):
        """Setup the Financial District level"""
        # Set level dimensions
        self.width = WIDTH * 3
        self.height = HEIGHT
        self.death_height = HEIGHT + 50
        
        # Set player starting position
        self.start_x = 150
        self.start_y = HEIGHT - 240
        
        # Set spawn protection time
        self.spawn_protection_time = 1.0
        
        # Starting platform (safe area)
        start_platform = self.add_platform(50, HEIGHT - 200, 300, 20, "building")
        
        # Create financial district buildings
        self.create_buildings()
        
        # Add moving platforms (floating finance symbols)
        self.add_moving_platforms()
        
        # Add boundary walls
        self.add_boundary_walls()
        
        # Ensure we have exactly 10 tokens
        self.ensure_token_count(LEVEL_DOOR_TOKENS_REQUIRED)
        
        # Add final exit door
        self.add_final_door()
        
    def create_buildings(self):
        """Create financial district buildings with connecting platforms"""
        # Main buildings at different heights
        buildings = [
            # [x, y, width, height]
            [350, HEIGHT - 150, 300, 20],      # Short building
            [750, HEIGHT - 250, 250, 20],      # Medium building
            [1100, HEIGHT - 350, 300, 20],     # Tall building
            [1500, HEIGHT - 250, 250, 20],     # Medium building
            [1850, HEIGHT - 300, 200, 20],     # Medium-tall building
            [2150, HEIGHT - 350, 350, 20],     # Skyscraper
            [2650, HEIGHT - 250, 400, 20],     # Financial district building
        ]
        
        # Create building platforms
        building_tokens = 0
        stepping_stone_tokens = 0
        
        # Add all buildings first
        for i, b in enumerate(buildings):
            building = self.add_platform(*b, platform_type="building")
            
            # Always add tokens on selected buildings
            if i in [1, 3, 5]:  # Add tokens to specific buildings rather than random
                token_x = b[0] + b[2] // 2  # Center of building
                token_type = self.token_types[i % len(self.token_types)]
                self.add_token(token_x, b[1] - 50, token_type=token_type)
                building_tokens += 1
            
        # Add stepping stones between buildings for navigation
        prev_building = None
        for b in buildings:
            if prev_building:
                # Calculate gap between buildings
                gap = b[0] - (prev_building[0] + prev_building[2])
                steps_needed = max(1, gap // 200)  # Determine number of steps based on gap size
                
                for step in range(steps_needed):
                    # Position steps evenly between buildings
                    step_x = prev_building[0] + prev_building[2] + (gap * (step + 1)) // (steps_needed + 1)
                    
                    # Vary height but ensure it's jumpable
                    if b[1] < prev_building[1]:  # Going up
                        step_y = prev_building[1] - ((prev_building[1] - b[1]) * (step + 1)) // (steps_needed + 1)
                    else:  # Going down or level
                        step_y = prev_building[1] + ((b[1] - prev_building[1]) * (step + 1)) // (steps_needed + 1)
                    
                    # Add a smaller platform as a stepping stone
                    step_width = 80 + random.randint(0, 40)
                    step_platform = self.add_platform(step_x, step_y, step_width, 15, platform_type="floating")
                    
                    # 70% chance to add token above stepping stone
                    if random.random() < 0.7 and stepping_stone_tokens < 3:  # Keep token count manageable
                        token_type = self.token_types[random.randint(0, len(self.token_types)-1)]
                        self.add_token(step_x + step_width//2, step_y - 60, token_type=token_type)
                        stepping_stone_tokens += 1
            
            prev_building = b
    
    def add_moving_platforms(self):
        """Add moving platforms (floating finance symbols)"""
        moving_platforms = [
            # [x, y, width, height, distance, speed_multiplier]
            [500, HEIGHT - 350, 80, 20, 150, 1.0],
            [1300, HEIGHT - 450, 100, 20, 200, 1.2],
            [2000, HEIGHT - 450, 120, 20, 250, 1.5],
            [2500, HEIGHT - 350, 80, 20, 180, 1.8],
        ]
        
        token_count = 0
        for i, mp in enumerate(moving_platforms):
            # Create moving platform
            plat = self.add_platform(
                mp[0], mp[1], mp[2], mp[3], 
                platform_type="floating", 
                moving=True, 
                move_distance=mp[4], 
                move_speed=PLATFORM_SPEED * mp[5]
            )
            
            # Always add a token on each moving platform - these are guaranteed for level completion
            token_type = self.token_types[i % len(self.token_types)]
            self.add_token(mp[0] + mp[2]//2, mp[1] - 50, token_type=token_type)
            token_count += 1
            
    def add_final_door(self):
        """Add exit door on the final platform"""
        # Position a door on the final building
        door_width = 80
        door_height = 120
        door_x = 2800
        door_y = HEIGHT - 370  # Place it above the final building
        
        self.add_exit_door(door_x, door_y, LEVEL_DOOR_TOKENS_REQUIRED)
    
    def ensure_token_count(self, required_tokens):
        """Ensure we have exactly the required number of tokens in the level"""
        current_token_count = len(self.tokens)
        
        if current_token_count < required_tokens:
            # Calculate how many more tokens we need
            tokens_needed = required_tokens - current_token_count
            
            # Always create guaranteed tokens at strategic locations
            guaranteed_positions = [
                [600, HEIGHT - 350],   # Above first gap
                [950, HEIGHT - 400],   # Above second building
                [1300, HEIGHT - 500],  # High above middle section
                [2200, HEIGHT - 450],  # Near skyscraper
                [2500, HEIGHT - 300],  # Path to exit
                [2700, HEIGHT - 350],  # Near exit
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
                    
                    # Position tokens at consistent heights that are reachable
                    token_y = HEIGHT - 350 - (50 * (i % 3))  # Vary heights between a few standard elevations
                    
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
            print(f"Warning: Level 2 expected {required_tokens} tokens but has {final_count}")
