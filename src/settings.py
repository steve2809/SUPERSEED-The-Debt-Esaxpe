# Game Settings
TITLE = "SUPERSEED: The Debt Escape"
WIDTH = 1280
HEIGHT = 720
FPS = 60
GRAVITY = 1500

# Graphics & Visual Quality Settings
POST_PROCESSING_ENABLED = True  # Enable visual effects like shadows and glows
ADAPTIVE_PERFORMANCE = True     # Automatically adjust visual effects based on framerate
SHADOW_QUALITY = 2              # 0=Off, 1=Basic, 2=Advanced
PARTICLE_QUALITY = 2            # 0=Low, 1=Medium, 2=High
USE_ANTIALIASING = True         # Smoother edges and animations

# Level 3 "Market Crash" Settings
LIGHTNING_WARNING_TIME = 1.5  # Time in seconds for the warning before lightning strikes
LIGHTNING_DURATION = 2.0      # How long lightning persists
LIGHTNING_WIDTH = 6           # Width of lightning bolt
LIGHTNING_COLOR = (255, 50, 50)  # Red color for lightning
LIGHTNING_WARNING_COLOR = (255, 150, 150, 100)  # Semi-transparent red
CRASH_EXPLOSION_PARTICLE_COUNT = 60  # Number of particles in crash death explosion

# Game States
STATE_MENU = 0
STATE_PLAYING = 1
STATE_PAUSED = 2
STATE_GAMEOVER = 3

# Colors
TEAL = (147, 208, 207)  # #93D0CF
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_TEAL = (73, 150, 150)
LIGHT_TEAL = (180, 230, 230)
BLUE_PRISONER = (70, 70, 180)
BROWN = (150, 100, 80)
GRAY = (100, 100, 100)
DARK_GRAY = (40, 40, 40)
GOLD = (255, 215, 0)
BRIGHT_TEAL = (0, 255, 255)

# Financial District Level Colors
BUILDING_COLORS = [
    (70, 130, 140),    # Dark teal-blue building
    (90, 150, 150),    # Medium teal building
    (110, 170, 170),   # Light teal building
    (60, 110, 120),    # Dark blue-teal
    (80, 140, 160)     # Medium blue-teal
]
WINDOW_COLOR = (200, 240, 255, 150)  # Slightly transparent light blue
SIGN_COLOR = (180, 255, 220)  # Bright teal-green
SHADOW_COLOR = (0, 0, 20, 120)  # Dark blue with alpha

# UI Settings
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
BUTTON_SPACING = 20
MENU_PADDING = 40
TRANSITION_DURATION = 0.5

# Level Select Settings
LEVEL_THUMBNAIL_WIDTH = 280
LEVEL_THUMBNAIL_HEIGHT = 160
LEVEL_SPACING = 30
LEVEL_SELECT_ROWS = 2
LEVEL_SELECT_COLS = 2
LEVEL_SELECT_TITLE_HEIGHT = 100
LEVEL_INFO_HEIGHT = 150

# Menu Positions (centered)
MENU_CENTER_X = WIDTH // 2
MENU_START_Y = HEIGHT // 2 - 50

# Effects
PARTICLE_COUNT = 100
SHADOW_OFFSET_X = 5
SHADOW_OFFSET_Y = 8
SHADOW_BLUR = 3
GLOW_INTENSITY = 0.6
PARALLAX_FACTOR = 0.4  # How much background layers move relative to foreground

# Animation Settings
ANIMATION_SPRING_STRENGTH = 8.0  # Higher = faster oscillation
ANIMATION_DAMPING = 0.3  # Higher = less bouncing
PLATFORM_OSCILLATION_AMOUNT = 3  # How many pixels platforms move up/down
TOKEN_BOB_AMOUNT = 5  # How many pixels tokens bob up/down
TOKEN_BOB_SPEED = 2.0  # Speed of token bobbing
BUILDING_DETAILS_DENSITY = 0.7  # 0-1, how many details to add to buildings

# Rendering Layers (higher renders on top)
LAYER_FAR_BG = 0
LAYER_MID_BG = 1
LAYER_BUILDINGS_BG = 2
LAYER_PLATFORMS = 3
LAYER_DECORATIONS = 4
LAYER_PLAYER = 5
LAYER_PARTICLES = 6
LAYER_UI = 7

# Player settings
PLAYER_ACC = 3500              # Further increased acceleration for even more responsive movement
PLAYER_FRICTION = -0.08        # Optimized friction value for improved control
PLAYER_GRAVITY = 2000
PLAYER_JUMP = 1350             # Increased jump height slightly
PLAYER_MAX_SPEED = 850         # Slightly higher max speed
PLAYER_WIDTH = 64
PLAYER_HEIGHT = 96
PLAYER_COYOTE_TIME = 0.2       # Increased coyote time for better jump feel
PLAYER_GROUND_BUFFER = 5       # Distance check for ground detection
PLAYER_AIR_CONTROL = 0.85      # Amount of control player has while in air (0-1)
PLAYER_JUMP_BUFFER_TIME = 0.15 # Time window where jump input is remembered when hitting ground
PLAYER_LAND_SQUISH = 0.2       # Visual squish factor when landing (0-1)
PLAYER_ACCELERATION_CURVE = 1.2 # Non-linear acceleration curve for smoother movement ramp-up

# Interaction settings
INTERACTION_DISTANCE = 150  # How close player needs to be to interact (increased from 80)
DOOR_OPEN_SPEED = 5         # Speed at which doors open

# X token settings
TOKEN_SIZE = 40
TOKENS_TO_TRANSFORM = 10

# Platform settings
PLATFORM_SPEED = 100
PLATFORM_BOUNCE_FACTOR = 0.1     # How much platforms bounce when landed on
PLATFORM_FRICTION_MULTIPLIER = 1.2  # Multiplier for friction on different platform types
PLATFORM_MAX_OSCILLATION = 5     # Maximum oscillation amount for floating platforms
PLATFORM_MOVEMENT_EASING = 0.2   # Smoothness of platform movement transitions (0-1)

# Level settings
TILE_SIZE = 64
LEVEL_RESPAWN_DELAY = 1.5      # Time delay before respawning after death
LEVEL_EDGE_BUFFER = 50         # Distance from edge that triggers respawn if crossed
LEVEL_CAMERA_SMOOTHING = 0.1   # Camera smoothing factor (0-1), 0=instant, 1=no movement
LEVEL_DOOR_TOKENS_REQUIRED = 10 # Number of tokens needed to open the exit door

# Death/Respawn Animation Settings
DEATH_SCREEN_FADE = 0.7        # Opacity of screen fade on death (0-1)
DEATH_PARTICLES_COUNT = 30     # Number of particles in death explosion
DEATH_SHAKE_INTENSITY = 10     # Maximum screen shake on death (pixels)
DEATH_SHAKE_DURATION = 0.5     # Duration of screen shake on death (seconds)
DEATH_TEXT_SCALE = 1.2         # Max scale factor for death text pulsing

# Completion settings
CONFETTI_COLORS = [
    (255, 50, 50),   # Red
    (50, 255, 50),   # Green
    (50, 50, 255),   # Blue
    (255, 255, 50),  # Yellow
    (255, 50, 255),  # Magenta
    (50, 255, 255),  # Cyan
    (255, 215, 0),   # Gold
    (0, 255, 200)    # Turquoise
]
