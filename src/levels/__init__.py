"""
Level factory module for loading different game levels
"""
from src.level import Level  # Keep original level class for backward compatibility
from src.levels.level1 import Level1
from src.levels.level2 import Level2
from src.levels.level3 import Level3

def get_level(game, level_num):
    """Factory function to get appropriate level instance
    
    Args:
        game: Game instance
        level_num: Level number to load
        
    Returns:
        Level instance based on the requested level number
    """
    if level_num == 1:
        return Level1(game)
    elif level_num == 2:
        return Level2(game)
    elif level_num == 3:
        return Level3(game)
    else:
        # Fallback to default level if invalid level number
        return Level(game, level_num)
