import pygame as pg
import pymunk
import random
import math
from src.settings import *
from src.sprites import Platform, SuperseedToken, EnhancedBackground, Lightning
from src.entities.player import Player
from src.interactive import Door
from src.ui import ParticleSystem, Panel, Button

class Level:
    """Handles level design, loading and interaction"""
    def __init__(self, game, level_num=1):
        self.game = game
        self.level_num = level_num
        
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
        
        # Spawn protection
        self.level_start_time = 0
        self.spawn_protection_time = 1.0  # Default value, overridden in level creation
        
        # Completion animation
        self.completion_particles = ParticleSystem("x_mark", 150)
        self.celebration_text = None
        self.celebration_font = pg.font.SysFont(None, 72)
        
        # Death animation
        self.death_particles = ParticleSystem("circle", 100)
        self.death_text = None
        self.death_font = pg.font.SysFont(None, 72)
        
        # Load level
        self.load_level(level_num)
        
    def load_level(self, level_num):
        """Load level data and create game objects"""
        if level_num == 1:
            # Level 1: Teal X Obstacle Course
            self.width = WIDTH * 3
            self.height = HEIGHT
            self.create_level_1()
        elif level_num == 2:
            # Level 2: Financial District Obstacle Course
            self.width = WIDTH * 3
            self.height = HEIGHT
            self.create_level_2()
        elif level_num == 3:
            # Level 3: Market Crash
            self.width = WIDTH * 4  # Wider level for final challenge
            self.height = HEIGHT
            self.create_level_3()
        else:
            # Default test level
            self.width = WIDTH * 2
            self.height = HEIGHT
            self.create_test_level()
            
    def create_test_level(self):
        """Create a simple test level with platforms and tokens"""
        # Starting platform
        start_platform = Platform(self.game, 0, HEIGHT - 100, 200, 20)
        self.platforms.add(start_platform)
        self.game.space.add(start_platform.body, start_platform.shape)
        
        # Platforms
        platforms = [
            # [x, y, width, height]
            [300, HEIGHT - 150, 200, 20],
            [550, HEIGHT - 250, 200, 20],
            [800, HEIGHT - 350, 200, 20],
            [1050, HEIGHT - 250, 200, 20],
            [1300, HEIGHT - 150, 200, 20],
            [1550, HEIGHT - 250, 300, 20],
            [1900, HEIGHT - 350, 200, 20],
        ]
        
        for p in platforms:
            plat = Platform(self.game, *p)
            self.platforms.add(plat)
            self.game.space.add(plat.body, plat.shape)
            
        # Add a moving platform
        moving_plat = Platform(self.game, 400, HEIGHT - 300, 120, 20)
        moving_plat.setup_movement(PLATFORM_SPEED, 200)
        self.platforms.add(moving_plat)
        self.game.space.add(moving_plat.body, moving_plat.shape)
            
        # X Tokens (spread throughout the level)
        token_positions = [
            [350, HEIGHT - 200],
            [600, HEIGHT - 300],
            [850, HEIGHT - 400],
            [1100, HEIGHT - 300],
            [1350, HEIGHT - 200],
            [1600, HEIGHT - 300],
            [1950, HEIGHT - 400],
        ]
        
        for pos in token_positions:
            token_type = self.token_types[random.randint(0, len(self.token_types)-1)]
            token = SuperseedToken(self.game, *pos, token_type=token_type)
            self.tokens.add(token)
            self.game.space.add(token.body, token.shape)

        # Add exit door on the final platform
        door_width = 70
        door_height = 100
        door_x = 1900
        door_y = HEIGHT - 450
        
        # Create door that requires 7 tokens (all tokens in test level)
        exit_door = Door(self.game, door_x, door_y, door_width, door_height, "vertical", 7)
        self.interactive_objects.add(exit_door)
        self.game.space.add(exit_door.body, exit_door.shape)
            
        # Add walls at the edges of the level
        left_wall = Platform(self.game, -10, 0, 10, HEIGHT)
        right_wall = Platform(self.game, self.width, 0, 10, HEIGHT)
        self.platforms.add(left_wall, right_wall)
        self.game.space.add(left_wall.body, left_wall.shape)
        self.game.space.add(right_wall.body, right_wall.shape)
            
    def create_level_1(self):
        """Create level 1: Teal X Obstacle Course"""
        # No ground - player dies if they fall
        # We only set a death line height for checking in the update method
        self.death_height = HEIGHT + 50
        
        # Start platform (safe area) - Wider to prevent accidental falls
        start_platform = Platform(self.game, 50, HEIGHT - 200, 300, 20, platform_type="building")
        self.platforms.add(start_platform)
        self.game.space.add(start_platform.body, start_platform.shape)
        
        # Update player start position - Better aligned with platform height
        self.start_x = 150
        self.start_y = HEIGHT - 240
        
        # Add spawn protection
        self.spawn_protection_time = 1.0  # 1 second of spawn protection
        
        # Ceiling to prevent super high jumps
        ceiling = Platform(self.game, 0, 0, self.width, 20)
        self.platforms.add(ceiling)
        self.game.space.add(ceiling.body, ceiling.shape)
        
        # Token counter
        token_count = 0
        
        # SECTION 1: Basic jumps with increasing difficulty
        section1_y = HEIGHT - 200  # Same height as starting platform
        
        # Series of platforms with increasing gaps
        platforms_section1 = [
            # [x, y, width, height]
            [350, section1_y, 150, 20],
            [600, section1_y, 120, 20],
            [820, section1_y, 100, 20],
            [1050, section1_y, 80, 20],
        ]
        
        for i, p in enumerate(platforms_section1):
            plat = Platform(self.game, *p, platform_type="building")
            self.platforms.add(plat)
            self.game.space.add(plat.body, plat.shape)
            
            # Add tokens above some platforms
            if i % 2 == 0:  # Every other platform
                token_x = p[0] + p[2] // 2
                token_y = p[1] - 60
                token_type = self.token_types[i % len(self.token_types)]
                token = SuperseedToken(self.game, token_x, token_y, token_type=token_type)
                self.tokens.add(token)
                self.game.space.add(token.body, token.shape)
                token_count += 1
        
        # SECTION 2: Vertical challenges
        section2_x = 1250
        
        # Create a vertical series of smaller platforms
        platform_heights = [
            HEIGHT - 200,  # Same as section 1
            HEIGHT - 280,
            HEIGHT - 360,
            HEIGHT - 420,
            HEIGHT - 380,
            HEIGHT - 300,
            HEIGHT - 200,
        ]
        
        for i, y in enumerate(platform_heights):
            x = section2_x + i * 120
            width = 80 if i != 3 else 50  # Make middle platform smaller for challenge
            
            plat = Platform(self.game, x, y, width, 20, platform_type="building")
            self.platforms.add(plat)
            self.game.space.add(plat.body, plat.shape)
            
            # Add tokens at peak height platforms
            if i == 3:  # Highest platform
                token_type = self.token_types[random.randint(0, len(self.token_types)-1)]
                token = SuperseedToken(self.game, x + width // 2, y - 60, token_type=token_type)
                self.tokens.add(token)
                self.game.space.add(token.body, token.shape)
                token_count += 1
        
        # SECTION 3: Moving platforms
        section3_x = 2050
        section3_y = HEIGHT - 250
        
        # Series of moving platforms with carefully placed tokens
        moving_platform_data = [
            # x, y, width, height, movement_distance
            [section3_x, section3_y, 100, 20, 150],
            [section3_x + 250, section3_y - 50, 80, 20, 100],
            [section3_x + 450, section3_y, 120, 20, 200],
            [section3_x + 700, section3_y + 30, 100, 20, 120],
        ]
        
        for i, data in enumerate(moving_platform_data):
            plat = Platform(self.game, *data[:4], platform_type="floating")
            plat.setup_movement(PLATFORM_SPEED + (i * 20), data[4])  # Increase speed with each platform
            self.platforms.add(plat)
            self.game.space.add(plat.body, plat.shape)
            
            # Add token above all moving platforms - they're challenging to get
            # Use a different token type for each platform
            token_type = self.token_types[i % len(self.token_types)]
            token = SuperseedToken(self.game, data[0] + data[2] // 2, data[1] - 60, token_type=token_type)
            self.tokens.add(token)
            self.game.space.add(token.body, token.shape)
            token_count += 1
        
        # SECTION 4: Final stretch
        final_x = section3_x + 900
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
            plat = Platform(self.game, *p, platform_type="building")
            self.platforms.add(plat)
            self.game.space.add(plat.body, plat.shape)
            
            # Add token to platforms except the last one
            if i < len(final_platforms) - 1 and random.random() < 0.5 and token_count < 10:
                token_type = self.token_types[random.randint(0, len(self.token_types)-1)]
                token = SuperseedToken(self.game, p[0] + p[2] // 2, p[1] - 60, token_type=token_type)
                self.tokens.add(token)
                self.game.space.add(token.body, token.shape)
                token_count += 1
                
        # Add end door on the last platform
        last_platform = final_platforms[-1]
        door_width = 70
        door_height = 100
        door_x = last_platform[0] + last_platform[2] - door_width - 20
        door_y = last_platform[1] - door_height
        
        # Create door that requires 10 tokens
        end_door = Door(self.game, door_x, door_y, door_width, door_height, "vertical", 10)
        self.interactive_objects.add(end_door)
        self.game.space.add(end_door.body, end_door.shape)
        
        # Ensure we have exactly 10 tokens
        if token_count < 10:
            # Calculate how many more tokens we need
            tokens_needed = 10 - token_count
            
            # Distribute remaining tokens at challenging locations
            for i in range(tokens_needed):
                # Position based on percentage through level
                segment = (i + 1) / (tokens_needed + 1)
                token_x = int(segment * (self.width - 400)) + 200
                
                # Randomize Y position but keep it above platforms
                token_y = HEIGHT - 300 - random.randint(0, 100)
                
                token_type = self.token_types[random.randint(0, len(self.token_types)-1)]
                token = SuperseedToken(self.game, token_x, token_y, token_type=token_type)
                self.tokens.add(token)
                self.game.space.add(token.body, token.shape)
        
        # Add walls at the edges
        left_wall = Platform(self.game, -10, 0, 10, HEIGHT)
        right_wall = Platform(self.game, self.width, 0, 10, HEIGHT)
        self.platforms.add(left_wall, right_wall)
        self.game.space.add(left_wall.body, left_wall.shape)
        self.game.space.add(right_wall.body, right_wall.shape)
            
    def create_level_2(self):
        """Create level 2: Financial District Obstacle Course"""
        # No ground - player dies if they fall
        # We only set a death line height for checking in the update method
        self.death_height = HEIGHT + 50
        
        # Start platform (safe area) - Wider to prevent accidental falls
        start_platform = Platform(self.game, 50, HEIGHT - 200, 300, 20, platform_type="building")
        self.platforms.add(start_platform)
        self.game.space.add(start_platform.body, start_platform.shape)
        
        # Update player start position - Better aligned with platform height
        self.start_x = 150
        self.start_y = HEIGHT - 240
        
        # Add spawn protection
        self.spawn_protection_time = 1.0  # 1 second of spawn protection
        
        # Buildings (series of platforms at different heights)
        # Carefully designed with jump heights in mind
        buildings = [
            # [x, y, width, height]
            [350, HEIGHT - 150, 300, 20],      # Short building
            [750, HEIGHT - 250, 250, 20],      # Medium building
            [1100, HEIGHT - 350, 300, 20],     # Tall building
            [1500, HEIGHT - 250, 250, 20],     # Medium building
            [1850, HEIGHT - 300, 200, 20],     # Medium-tall building
            [2150, HEIGHT - 350, 350, 20],     # Skyscraper
            [2650, HEIGHT - 250, 400, 20],     # Financial district building
            [3150, HEIGHT - 350, 300, 20],     # Final building
        ]
        
        # Token counter
        token_count = 0
        
        # Add building platforms and ensure connectivity
        prev_building = None
        for i, b in enumerate(buildings):
            building = Platform(self.game, *b, platform_type="building")
            self.platforms.add(building)
            self.game.space.add(building.body, building.shape)
            
            # Add stepping stones between buildings for better navigation
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
                    step_platform = Platform(self.game, step_x, step_y, step_width, 15, platform_type="floating")
                    self.platforms.add(step_platform)
                    self.game.space.add(step_platform.body, step_platform.shape)
                    
                    # 50% chance to add token above stepping stone
                    if random.random() < 0.5 and token_count < 10:
                        token_type = self.token_types[random.randint(0, len(self.token_types)-1)]
                        token = SuperseedToken(self.game, step_x + step_width//2, step_y - 60, token_type=token_type)
                        self.tokens.add(token)
                        self.game.space.add(token.body, token.shape)
                        token_count += 1
            
            prev_building = b
            
        # Add tokens on buildings
        for b in buildings:
            # 40% chance to add a token on each building
            if random.random() < 0.4 and token_count < 10:
                token_x = b[0] + random.randint(50, b[2] - 50)
                token_type = self.token_types[random.randint(0, len(self.token_types)-1)]
                token = SuperseedToken(self.game, token_x, b[1] - 50, token_type=token_type)
                self.tokens.add(token)
                self.game.space.add(token.body, token.shape)
                token_count += 1
                
        # Add some moving platforms (floating finance symbols)
        moving_platforms = [
            [500, HEIGHT - 350, 80, 20, 150],
            [1300, HEIGHT - 450, 100, 20, 200],
            [2000, HEIGHT - 450, 120, 20, 250],
            [2500, HEIGHT - 350, 80, 20, 180],
        ]
        
        for mp in moving_platforms:
            plat = Platform(self.game, *mp[:4], platform_type="floating")
            plat.setup_movement(PLATFORM_SPEED, mp[4])
            self.platforms.add(plat)
            self.game.space.add(plat.body, plat.shape)
            
            # Add a token on each moving platform if we still need tokens
            if token_count < 10:
                token_type = self.token_types[random.randint(0, len(self.token_types)-1)]
                token = SuperseedToken(self.game, mp[0] + mp[2]//2, mp[1] - 50, token_type=token_type)
                self.tokens.add(token)
                self.game.space.add(token.body, token.shape)
                token_count += 1
        
        # Add an end door on the final building
        final_building = buildings[-1]
        door_width = 80
        door_height = 120
        door_x = final_building[0] + final_building[2] - door_width - 30
        door_y = final_building[1] - door_height
        
        # Create door that requires 10 tokens
        end_door = Door(self.game, door_x, door_y, door_width, door_height, "vertical", 10)
        self.interactive_objects.add(end_door)
        self.game.space.add(end_door.body, end_door.shape)
        
        # Ensure we have exactly 10 tokens
        if token_count < 10:
            # Calculate how many more tokens we need
            tokens_needed = 10 - token_count
            
            # Add additional tokens in strategic locations
            for i in range(tokens_needed):
                # Position based on percentage through level
                segment = (i + 1) / (tokens_needed + 1)
                token_x = int(segment * (self.width - 400)) + 200
                
                # Randomize Y position but keep it above buildings
                token_y = HEIGHT - 400 - random.randint(0, 100)
                
                token_type = self.token_types[random.randint(0, len(self.token_types)-1)]
                token = SuperseedToken(self.game, token_x, token_y, token_type=token_type)
                self.tokens.add(token)
                self.game.space.add(token.body, token.shape)
            
        # Add walls at the edges
        left_wall = Platform(self.game, -10, 0, 10, HEIGHT)
        right_wall = Platform(self.game, self.width, 0, 10, HEIGHT)
        self.platforms.add(left_wall, right_wall)
        self.game.space.add(left_wall.body, left_wall.shape)
        self.game.space.add(right_wall.body, right_wall.shape)
        
    def create_level_3(self):
        """Create level 3: Market Crash - Final Challenge"""
        # No ground - player dies if they fall
        self.death_height = HEIGHT + 50
        
        # Create specialized background for Market Crash level
        if hasattr(self.game, 'background'):
            self.game.background = EnhancedBackground(self.game, "market_crash")
        
        # Start platform (safe area)
        start_platform = Platform(self.game, 50, HEIGHT - 200, 350, 20, platform_type="building")
        self.platforms.add(start_platform)
        self.game.space.add(start_platform.body, start_platform.shape)
        
        # Update player start position
        self.start_x = 150
        self.start_y = HEIGHT - 240
        
        # Add spawn protection
        self.spawn_protection_time = 1.0
        
        # Ceiling
        ceiling = Platform(self.game, 0, 0, self.width, 20)
        self.platforms.add(ceiling)
        self.game.space.add(ceiling.body, ceiling.shape)
        
        # Token counter
        token_count = 0
        
        # Initialize lightning hazards list
        self.lightning_hazards = []
        self.lightning_spawn_timer = 0
        self.lightning_spawn_interval = 3.0  # Time between lightning spawns
        
        # SECTION 1: Wider platforms with gaps (intro section)
        section1_y = HEIGHT - 200
        
        platforms_section1 = [
            # [x, y, width, height]
            [400, section1_y, 300, 20],  # First wide platform
            [800, section1_y, 250, 20],  # Second platform
            [1150, section1_y, 350, 20], # Third wider platform
            [1600, section1_y, 250, 20], # Fourth platform
        ]
        
        for i, p in enumerate(platforms_section1):
            plat = Platform(self.game, *p, platform_type="building")
            self.platforms.add(plat)
            self.game.space.add(plat.body, plat.shape)
            
            # Add tokens to alternate platforms
            if i % 2 == 0:
                # Add token in middle of platform
                token_x = p[0] + p[2] // 2
                token_y = p[1] - 60
                token_type = self.token_types[random.randint(0, len(self.token_types)-1)]
                token = SuperseedToken(self.game, token_x, token_y, token_type=token_type)
                self.tokens.add(token)
                self.game.space.add(token.body, token.shape)
                token_count += 1
        
        # SECTION 2: Obstacle section with challenging jumps
        section2_x = 1850
        section2_y = HEIGHT - 250  # Slightly higher
        
        # Main platforms
        platforms_section2 = [
            # These will be wide platforms with some obstacles in between
            [section2_x, section2_y, 400, 20],
            [section2_x + 600, section2_y, 350, 20],
            [section2_x + 1100, section2_y, 400, 20]
        ]
        
        for p in platforms_section2:
            plat = Platform(self.game, *p, platform_type="building")
            self.platforms.add(plat)
            self.game.space.add(plat.body, plat.shape)
        
        # Add small obstacle platforms between main platforms
        # These create narrow passages for the lightning to make challenging
        obstacle_platforms = [
            # Small platform segments with gaps for player to navigate
            [section2_x + 450, section2_y - 100, 50, 100],  # Vertical obstacle
            [section2_x + 500, section2_y - 150, 50, 20],   # Small platform above
            
            # Second set of obstacles
            [section2_x + 1000, section2_y - 80, 50, 80],   # Vertical obstacle
            [section2_x + 950, section2_y - 150, 50, 20],   # Small platform above
        ]
        
        for p in obstacle_platforms:
            plat = Platform(self.game, *p, platform_type="building")
            self.platforms.add(plat)
            self.game.space.add(plat.body, plat.shape)
            
        # Add tokens around obstacle section (forcing player to navigate obstacles)
        obstacle_tokens = [
            [section2_x + 480, section2_y - 200],  # Above first obstacle
            [section2_x + 975, section2_y - 200],  # Above second obstacle
            [section2_x + 830, section2_y - 100],  # In the middle of the gap
        ]
        
        for pos in obstacle_tokens:
            token_type = self.token_types[random.randint(0, len(self.token_types)-1)]
            token = SuperseedToken(self.game, *pos, token_type=token_type)
            self.tokens.add(token)
            self.game.space.add(token.body, token.shape)
            token_count += 1
        
        # SECTION 3: Moving platforms final challenge
        section3_x = section2_x + 1600
        section3_y = HEIGHT - 300
        
        # Final moving platforms (challenging)
        moving_platforms = [
            # x, y, width, height, distance
            [section3_x, section3_y, 150, 20, 200],
            [section3_x + 350, section3_y + 50, 120, 20, 150],
            [section3_x + 650, section3_y - 50, 100, 20, 180],
            [section3_x + 950, section3_y, 180, 20, 100]
        ]
        
        for i, mp in enumerate(moving_platforms):
            plat = Platform(self.game, *mp[:4], platform_type="floating")
            # Increase speed for more challenge in final section
            plat.setup_movement(PLATFORM_SPEED + (i * 30), mp[4])
            self.platforms.add(plat)
            self.game.space.add(plat.body, plat.shape)
            
            # Add token on each moving platform
            if token_count < 10:
                token_x = mp[0] + mp[2] // 2
                token_y = mp[1] - 60
                token_type = self.token_types[random.randint(0, len(self.token_types)-1)]
                token = SuperseedToken(self.game, token_x, token_y, token_type=token_type)
                self.tokens.add(token)
                self.game.space.add(token.body, token.shape)
                token_count += 1
        
        # Final platform with exit door
        final_x = section3_x + 1250
        final_y = HEIGHT - 250
        final_platform = Platform(self.game, final_x, final_y, 350, 20, platform_type="building")
        self.platforms.add(final_platform)
        self.game.space.add(final_platform.body, final_platform.shape)
        
        # Add door on final platform
        door_width = 80
        door_height = 120
        door_x = final_x + 250
        door_y = final_y - door_height
        
        # Door requires all 10 tokens
        exit_door = Door(self.game, door_x, door_y, door_width, door_height, "vertical", 10)
        self.interactive_objects.add(exit_door)
        self.game.space.add(exit_door.body, exit_door.shape)
        
        # Ensure we have exactly 10 tokens
        if token_count < 10:
            # Calculate how many more tokens we need
            tokens_needed = 10 - token_count
            
            # Add remaining tokens at strategic locations
            token_locations = [
                [section2_x + 300, section2_y - 100],
                [section2_x + 750, section2_y - 150],
                [section3_x + 200, section3_y - 150],
                [section3_x + 500, section3_y - 100],
                [section3_x + 800, section3_y - 200],
                [final_x + 150, final_y - 80]
            ]
            
            for i in range(min(tokens_needed, len(token_locations))):
                token_type = self.token_types[random.randint(0, len(self.token_types)-1)]
                token = SuperseedToken(self.game, *token_locations[i], token_type=token_type)
                self.tokens.add(token)
                self.game.space.add(token.body, token.shape)
                token_count += 1
                
        # Add walls at the edges
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
            
        # Update Lightning hazards for Level 3
        if self.level_num == 3 and not self.player_died and not self.level_complete:
            self.update_lightning_hazards()
            
    def check_player_died(self):
        """Check if player has fallen off the platforms"""
        if self.player_died:
            return True
            
        # Check if spawn protection is active
        current_time = self.game.dt * self.game.frame_count
        if current_time - self.level_start_time < self.spawn_protection_time:
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
        
        # Special handling for electrocution/lightning deaths in level 3
        if hasattr(self, 'death_cause') and self.death_cause == "crash":
            # Multi-phase electrocution animation
            if self.death_animation_time < 1.2:  # Extended animation time
                # Character shaking/vibration effect
                shake_x = random.randint(-self.shake_amount, self.shake_amount)
                shake_y = random.randint(-self.shake_amount, self.shake_amount)
                
                # Apply shake to player sprite if we can
                if hasattr(self.game, 'player') and hasattr(self.game.player, 'rect'):
                    # Store original position to reset after level restart
                    original_x, original_y = self.original_player_pos
                    self.game.player.rect.centerx = original_x + shake_x
                    self.game.player.rect.centery = original_y + shake_y
                
                # Phase transitions
                if self.death_animation_time > 0.3 and self.electrocution_phase == 0:
                    # Phase 1: First big pulse of particles
                    self.electrocution_phase = 1
                    self.death_particles.spawn_particles(
                        self.impact_position,
                        30,  # More particles for the pulse
                        spread=80,
                        color=LIGHTNING_COLOR
                    )
                    # Reduce shake as character "stiffens"
                    self.shake_amount = 5
                
                elif self.death_animation_time > 0.6 and self.electrocution_phase == 1:
                    # Phase 2: Second bigger pulse
                    self.electrocution_phase = 2
                    self.death_particles.spawn_particles(
                        self.impact_position,
                        40,  # Even more particles
                        spread=100,
                        color=LIGHTNING_COLOR
                    )
                    # Less shake, more stiffening
                    self.shake_amount = 3
                
                elif self.death_animation_time > 0.9 and self.electrocution_phase == 2:
                    # Phase 3: Final explosion
                    self.electrocution_phase = 3
                    
                    # Create a bigger explosion of particles
                    for i in range(4):
                        angle = i * (math.pi / 2)  # Spread in 4 directions
                        offset_x = math.cos(angle) * 30
                        offset_y = math.sin(angle) * 30
                        
                        explosion_pos = (
                            self.impact_position[0] + offset_x,
                            self.impact_position[1] + offset_y
                        )
                        
                        self.death_particles.spawn_particles(
                            explosion_pos,
                            15,  # 15 particles from each corner
                            spread=70,
                            color=LIGHTNING_COLOR
                        )
                    
                    # Reset player position to center for the explosion
                    if hasattr(self.game, 'player') and hasattr(self.game.player, 'rect'):
                        original_x, original_y = self.original_player_pos
                        self.game.player.rect.centerx = original_x
                        self.game.player.rect.centery = original_y
            
            # After animation completes
            elif self.death_animation_time > 2.0:  # Longer pause before restart
                self.game.restart_level()
        else:
            # Standard death animation for falling
            if self.death_animation_time > 1.5:
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
            # This will be handled by the Game class to present next level / main menu options
            
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
        
        # Create completion menu
        self.completion_menu_panel = Panel(
            WIDTH // 2 - 200, 
            HEIGHT // 2, 
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
        
        # Spawn initial burst of particles at player position
        player_screen_pos = (
            self.game.player.rect.centerx + self.game.camera_offset_x,
            self.game.player.rect.centery + self.game.camera_offset_y
        )
        self.completion_particles.spawn_particles(player_screen_pos, 40, spread=100)
        
    def update_lightning_hazards(self):
        """Update lightning hazards for Level 3"""
        from src.sprites import Lightning
        
        # Update existing lightning
        for lightning in self.lightning_hazards[:]:
            # Update the lightning
            if lightning.update(self.game.dt):
                # Lightning duration is over, remove it
                self.lightning_hazards.remove(lightning)
                continue
                
            # Check for collision with player
            if lightning.check_collision(self.game.player.rect):
                # Player hit by lightning, start crash death animation
                self.start_crash_death_animation(lightning)
                break
        
        # Spawn new lightning if needed
        self.lightning_spawn_timer += self.game.dt
        if self.lightning_spawn_timer >= self.lightning_spawn_interval:
            self.lightning_spawn_timer = 0
            
            # Only spawn new lightning if player is far enough into the level
            if self.game.player.rect.x > 500:
                # Determine where to spawn lightning
                # Create lightning around player's vicinity
                player_x = self.game.player.rect.centerx
                player_y = self.game.player.rect.centery
                
                # Sometimes spawn directly in player's path, sometimes nearby
                spawn_offset_x = random.choice([
                    random.randint(200, 600),   # Ahead of player
                    random.randint(-300, 200)   # Behind or at player
                ])
                
                spawn_offset_y = random.randint(-200, 200)  # Above or below player
                
                # Calculate spawn position
                spawn_x = player_x + spawn_offset_x
                spawn_y = player_y + spawn_offset_y
                
                # Limit to level bounds
                spawn_y = max(100, min(HEIGHT - 100, spawn_y))
                spawn_x = max(100, min(self.width - 100, spawn_x))
                
                # Create lightning with random angle and size
                lightning_height = random.randint(200, 400)  # Length of lightning
                lightning_angle = random.randint(20, 160)    # Angle in degrees
                
                # Create the lightning hazard
                lightning = Lightning(
                    self.game,
                    spawn_x, 
                    spawn_y, 
                    LIGHTNING_WIDTH, 
                    lightning_height,
                    lightning_angle
                )
                
                # Add to hazards list
                self.lightning_hazards.append(lightning)
                
    def start_crash_death_animation(self, lightning):
        """Start death animation when player is hit by market crash lightning"""
        if not self.player_died:
            self.player_died = True
            self.death_animation_time = 0
            self.death_cause = "crash"
            self.electrocution_phase = 0  # Track phase of electrocution animation
            self.shake_amount = 10  # Initial shake amount for character
            self.last_shake_dir = 1  # For alternating shake direction
            
            # Set death text
            self.death_text = self.death_font.render("You've been killed by the crash!", True, LIGHTNING_COLOR)
            
            # Store original player position for animation
            self.original_player_pos = (
                self.game.player.rect.centerx,
                self.game.player.rect.centery
            )
            
            # Get screen impact position
            self.impact_position = (
                self.game.player.rect.centerx + self.game.camera_offset_x,
                self.game.player.rect.centery + self.game.camera_offset_y
            )
            
            # Create particle system for electrocution effect
            self.death_particles = ParticleSystem("lightning", CRASH_EXPLOSION_PARTICLE_COUNT * 2)
            
            # Initial lightning particles (first phase)
            self.death_particles.spawn_particles(
                self.impact_position,
                20,  # Initial burst of particles
                spread=50,
                color=LIGHTNING_COLOR
            )
            
            # Play electrocution sound if available
            if hasattr(self.game, 'sound_manager') and hasattr(self.game.sound_manager, 'play_electrocution'):
                self.game.sound_manager.play_electrocution()
            elif hasattr(self.game, 'sound_manager'):
                self.game.sound_manager.play_death()  # Fallback to regular death sound
                
    def draw(self, surface):
        """Draw all level elements to the surface"""
        # Only draw special effects here - platforms and entities are drawn by the game class
        
        # Draw lightning hazards for level 3
        if self.level_num == 3 and hasattr(self, 'lightning_hazards'):
            for lightning in self.lightning_hazards:
                lightning.draw(surface, self.game.camera_offset_x, self.game.camera_offset_y)
        
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
            pulse = 1.0 + 0.15 * math.sin(self.death_animation_time * 8)
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
