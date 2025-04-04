import pygame as pg
import pymunk
import random
import math
from src.settings import *
from src.sprites import Platform, SuperseedToken, Lightning, EnhancedBackground
from src.interactive import Door
from src.levels.base_level import BaseLevel

class Level3(BaseLevel):
    """Level 3: Market Crash - Final challenging level with lightning hazards"""
    def __init__(self, game):
        self.level_num = 3
        
        # Lightning hazards list - will be populated during setup
        self.lightning_hazards = []
        self.lightning_spawn_timer = 0
        self.lightning_spawn_interval = 3.0  # Time between lightning spawns
        
        super().__init__(game)
        
    def setup_level(self):
        """Setup the Market Crash level - most challenging level"""
        # Set level dimensions - make it wider than previous levels
        self.width = WIDTH * 4
        self.height = HEIGHT
        self.death_height = HEIGHT + 50
        
        # Set player starting position
        self.start_x = 150
        self.start_y = HEIGHT - 240
        
        # Set spawn protection time
        self.spawn_protection_time = 1.0
        
        # Add ceiling
        ceiling = self.add_platform(0, 0, self.width, 20)
        
        # Create specialized background if game has that capability
        if hasattr(self.game, 'background'):
            self.game.background = EnhancedBackground(self.game, "market_crash")
        
        # Starting platform (safe area)
        start_platform = self.add_platform(50, HEIGHT - 200, 350, 20, "building")
        
        # Create level sections
        self.create_intro_section()    # Section 1: Wider platforms with gaps
        self.create_obstacle_section()  # Section 2: Obstacle section with challenging jumps
        self.create_final_section()     # Section 3: Moving platforms final challenge
        
        # Add boundary walls
        self.add_boundary_walls()
        
        # Ensure we have exactly the right number of tokens
        self.ensure_token_count(LEVEL_DOOR_TOKENS_REQUIRED)
        
    def create_intro_section(self):
        """Create section 1: Wider platforms with gaps - intro section"""
        section1_y = HEIGHT - 200
        
        platforms_section1 = [
            # [x, y, width, height]
            [400, section1_y, 300, 20],  # First wide platform
            [800, section1_y, 250, 20],  # Second platform
            [1150, section1_y, 350, 20], # Third wider platform
            [1600, section1_y, 250, 20], # Fourth platform
        ]
        
        for i, p in enumerate(platforms_section1):
            plat = self.add_platform(*p, platform_type="building")
            
            # Add tokens to all platforms for better consistency
            token_x = p[0] + p[2] // 2
            token_y = p[1] - 60
            token_type = self.token_types[i % len(self.token_types)]
            self.add_token(token_x, token_y, token_type=token_type)
            
    def create_obstacle_section(self):
        """Create section 2: Obstacle section with challenging jumps"""
        section2_x = 1850
        section2_y = HEIGHT - 250  # Slightly higher
        
        # Main platforms
        platforms_section2 = [
            # These will be wide platforms with obstacles in between
            [section2_x, section2_y, 400, 20],
            [section2_x + 600, section2_y, 350, 20],
            [section2_x + 1100, section2_y, 400, 20]
        ]
        
        for i, p in enumerate(platforms_section2):
            plat = self.add_platform(*p, platform_type="building")
            
            # Add token on each main platform
            token_x = p[0] + p[2] // 2
            token_y = p[1] - 60
            token_type = self.token_types[i % len(self.token_types)]
            self.add_token(token_x, token_y, token_type=token_type)
        
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
            plat = self.add_platform(*p, platform_type="building")
        
        # Add tokens around obstacle section (forcing player to navigate obstacles)
        obstacle_tokens = [
            [section2_x + 480, section2_y - 200],  # Above first obstacle
            [section2_x + 975, section2_y - 200],  # Above second obstacle
        ]
        
        for i, pos in enumerate(obstacle_tokens):
            token_type = self.token_types[random.randint(0, len(self.token_types)-1)]
            self.add_token(*pos, token_type=token_type)
            
    def create_final_section(self):
        """Create section 3: Moving platforms final challenge"""
        section3_x = 3050  # After the obstacle section
        section3_y = HEIGHT - 300
        
        # Final moving platforms (challenging)
        moving_platforms = [
            # x, y, width, height, distance, speed_multiplier
            [section3_x, section3_y, 150, 20, 200, 1.0],
            [section3_x + 350, section3_y + 50, 120, 20, 150, 1.2],
            [section3_x + 650, section3_y - 50, 100, 20, 180, 1.5],
            [section3_x + 950, section3_y, 180, 20, 100, 1.8]
        ]
        
        for i, mp in enumerate(moving_platforms):
            plat = self.add_platform(
                mp[0], mp[1], mp[2], mp[3], 
                platform_type="floating", 
                moving=True, 
                move_distance=mp[4], 
                move_speed=PLATFORM_SPEED * mp[5]
            )
            
            # Add token on each moving platform
            token_x = mp[0] + mp[2] // 2
            token_y = mp[1] - 60
            token_type = self.token_types[i % len(self.token_types)]
            self.add_token(token_x, token_y, token_type=token_type)
        
        # Final platform with exit door
        final_x = section3_x + 1250
        final_y = HEIGHT - 250
        final_platform = self.add_platform(final_x, final_y, 350, 20, platform_type="building")
        
        # Add door on final platform
        door_x = final_x + 250
        door_y = final_y - 120
        
        # Door requires all 10 tokens
        self.add_exit_door(door_x, door_y, LEVEL_DOOR_TOKENS_REQUIRED)
    
    def ensure_token_count(self, required_tokens):
        """Ensure we have exactly the required number of tokens in the level"""
        current_token_count = len(self.tokens)
        
        if current_token_count < required_tokens:
            # Calculate how many more tokens we need
            tokens_needed = required_tokens - current_token_count
            
            # Add guaranteed tokens at strategic locations
            guaranteed_positions = [
                [600, HEIGHT - 350],     # Above first section
                [1000, HEIGHT - 300],    # Middle of first section
                [1350, HEIGHT - 300],    # End of first section
                [2150, HEIGHT - 400],    # Above obstacle section
                [2350, HEIGHT - 350],    # Middle of obstacles
                [2700, HEIGHT - 400],    # End of obstacles
                [3200, HEIGHT - 400],    # Above first moving platform
                [3500, HEIGHT - 300],    # Between moving platforms
                [3800, HEIGHT - 250],    # Near final area
                [4000, HEIGHT - 350]     # Before exit door
            ]
            
            # Use as many guaranteed positions as needed
            for i in range(min(tokens_needed, len(guaranteed_positions))):
                pos = guaranteed_positions[i]
                token_type = self.token_types[random.randint(0, len(self.token_types)-1)]
                self.add_token(pos[0], pos[1], token_type=token_type)
                
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
            print(f"Warning: Level 3 expected {required_tokens} tokens but has {final_count}")
    
    def update(self):
        """Update all level elements including lightning hazards"""
        # Call parent update method first
        super().update()
        
        # Update Lightning hazards if not dead and not complete
        if not self.player_died and not self.level_complete:
            self.update_lightning_hazards()
            
    def update_lightning_hazards(self):
        """Update lightning hazards"""
        # Update existing lightning
        for lightning in self.lightning_hazards[:]:
            # Update the lightning
            if lightning.update(self.game.dt):
                # Lightning duration is over, remove it
                self.lightning_hazards.remove(lightning)
                continue
                
            # Check for collision with player
            if hasattr(lightning, 'check_collision') and lightning.check_collision(self.game.player.rect):
                # Player hit by lightning, start crash death animation
                self.start_crash_death_animation(lightning)
                break
        
        # Spawn new lightning if needed
        self.lightning_spawn_timer += self.game.dt
        if self.lightning_spawn_timer >= self.lightning_spawn_interval:
            self.lightning_spawn_timer = 0
            
            # Only spawn new lightning if player is far enough into the level
            # and not in the safe starting area
            if self.game.player.rect.x > 500:
                # Spawn lightning near player but not directly on them
                self.spawn_lightning_near_player()
                
    def spawn_lightning_near_player(self):
        """Spawn lightning in the player's vicinity but not directly on them"""
        from src.sprites import Lightning
        
        player_x = self.game.player.rect.centerx
        player_y = self.game.player.rect.centery
        
        # Determine spawn location - sometimes ahead, sometimes to the sides
        spawn_type = random.choice(["ahead", "side", "above"])
        
        if spawn_type == "ahead":
            # Spawn ahead of player in movement direction
            direction = 1 if self.game.player.vel.x >= 0 else -1
            spawn_offset_x = direction * random.randint(200, 400)
            spawn_offset_y = random.randint(-100, 100)
        elif spawn_type == "side":
            # Spawn to the side of player
            spawn_offset_x = random.choice([-1, 1]) * random.randint(50, 150)
            spawn_offset_y = random.randint(-50, 50)
        else:  # "above"
            # Spawn above player
            spawn_offset_x = random.randint(-100, 100)
            spawn_offset_y = -random.randint(100, 200)
        
        # Calculate final spawn position
        spawn_x = player_x + spawn_offset_x
        spawn_y = player_y + spawn_offset_y
        
        # Ensure within level bounds
        spawn_x = max(100, min(self.width - 100, spawn_x))
        spawn_y = max(100, min(HEIGHT - 100, spawn_y))
        
        # Create lightning with random properties
        lightning_width = LIGHTNING_WIDTH
        lightning_height = random.randint(150, 300)
        lightning_angle = random.randint(0, 180)
        
        # Create lightning object
        lightning = Lightning(
            self.game,
            spawn_x,
            spawn_y,
            lightning_width,
            lightning_height,
            lightning_angle
        )
        
        # Add to hazards list
        self.lightning_hazards.append(lightning)
        
        # Add warning effect at location if possible
        if hasattr(self.game, 'token_particles'):
            warning_color = (255, 220, 50)  # Yellow warning color
            self.game.token_particles.spawn_particles(
                (spawn_x + self.game.camera_offset_x, spawn_y + self.game.camera_offset_y),
                5,  # Just a few particles for warning
                spread=20,
                color=warning_color
            )
    
    def start_crash_death_animation(self, lightning):
        """Start death animation when player is hit by market crash lightning"""
        # Only start if not already dead
        if not self.player_died:
            # Store original player position for animation
            self.original_player_pos = (
                self.game.player.rect.centerx,
                self.game.player.rect.centery
            )
            
            # Get impact position on screen
            self.impact_position = (
                self.game.player.rect.centerx + self.game.camera_offset_x,
                self.game.player.rect.centery + self.game.camera_offset_y
            )
            
            # Initialize crash-specific death parameters
            self.electrocution_phase = 0
            self.shake_amount = 10
            
            # Call parent method with special crash death type
            self.start_death_animation("crash")
            
            # Override death text for crash
            self.death_text = self.death_font.render("Crashed to Debt!", True, LIGHTNING_COLOR)
            
            # Create electrocution particle system if needed
            if not hasattr(self, 'electrocution_particles'):
                from src.ui import ParticleSystem
                self.electrocution_particles = ParticleSystem("lightning", 100)  # Use a reasonable default value
                
            # Initial burst of particles
            if hasattr(self, 'electrocution_particles'):
                self.electrocution_particles.spawn_particles(
                    self.impact_position,
                    20,
                    spread=50,
                    color=LIGHTNING_COLOR
                )
    
    def update_death_animation(self):
        """Special handling for death animation"""
        dt = self.game.dt
        self.death_animation_time += dt
        
        # Update particles
        if hasattr(self, 'death_particles'):
            self.death_particles.update(dt)
            
        # Special handling for electrocution/lightning deaths
        if hasattr(self, 'death_cause') and self.death_cause == "crash":
            # If we have electrocution particles, update them
            if hasattr(self, 'electrocution_particles'):
                self.electrocution_particles.update(dt)
                
            # Multi-phase crash animation
            if self.death_animation_time < 1.2:
                # Character shaking/vibration effect
                if hasattr(self, 'shake_amount') and hasattr(self, 'original_player_pos'):
                    shake_x = random.randint(-self.shake_amount, self.shake_amount)
                    shake_y = random.randint(-self.shake_amount, self.shake_amount)
                    
                    # Apply shake to player sprite if possible
                    if hasattr(self.game, 'player') and hasattr(self.game.player, 'rect'):
                        original_x, original_y = self.original_player_pos
                        self.game.player.rect.centerx = original_x + shake_x
                        self.game.player.rect.centery = original_y + shake_y
                
                # Phase transitions
                if self.death_animation_time > 0.3 and self.electrocution_phase == 0:
                    # Phase 1: First big pulse of particles
                    self.electrocution_phase = 1
                    if hasattr(self, 'electrocution_particles') and hasattr(self, 'impact_position'):
                        self.electrocution_particles.spawn_particles(
                            self.impact_position,
                            30,
                            spread=80,
                            color=LIGHTNING_COLOR
                        )
                    # Reduce shake as character "stiffens"
                    self.shake_amount = 5
                
                elif self.death_animation_time > 0.6 and self.electrocution_phase == 1:
                    # Phase 2: Second bigger pulse
                    self.electrocution_phase = 2
                    if hasattr(self, 'electrocution_particles') and hasattr(self, 'impact_position'):
                        self.electrocution_particles.spawn_particles(
                            self.impact_position,
                            40,
                            spread=100,
                            color=LIGHTNING_COLOR
                        )
                    # Less shake, more stiffening
                    self.shake_amount = 3
                
                elif self.death_animation_time > 0.9 and self.electrocution_phase == 2:
                    # Phase 3: Final explosion
                    self.electrocution_phase = 3
                    
                    # Create a bigger explosion of particles if we have them
                    if hasattr(self, 'electrocution_particles') and hasattr(self, 'impact_position'):
                        for i in range(4):
                            angle = i * (math.pi / 2)  # Spread in 4 directions
                            offset_x = math.cos(angle) * 30
                            offset_y = math.sin(angle) * 30
                            
                            explosion_pos = (
                                self.impact_position[0] + offset_x,
                                self.impact_position[1] + offset_y
                            )
                            
                            self.electrocution_particles.spawn_particles(
                                explosion_pos,
                                15,
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
            super().update_death_animation()
    
    def draw(self, surface):
        """Draw all level elements to the surface"""
        # Call parent draw first
        super().draw(surface)
        
        # Draw lightning hazards
        for lightning in self.lightning_hazards:
            lightning.draw(surface, self.game.camera_offset_x, self.game.camera_offset_y)
            
        # Draw electrocution particles if applicable
        if self.player_died and self.death_cause == "crash" and hasattr(self, 'electrocution_particles'):
            self.electrocution_particles.draw(surface)
