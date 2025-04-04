# SUPERSEED: The Game

A Super Mario-style platformer based on the SUPERSEED blockchain finance theme, featuring a frog character that can transform from a debt prisoner to a powerful financial wizard.

## Game Concept

SUPERSEED represents a journey of financial transformation, starting as a prisoner of debt and evolving into a financial wizard through collecting special X tokens. The game uses distinctive teal color schemes and X mark symbolism that represent financial liberation.

## Features

- **Fluid platformer mechanics**: Responsive controls with precise jumping and movement
- **Character transformation**: Collect X tokens to transform from prisoner to wizard form
- **Optimized performance**: Viewport culling, pre-calculated effects, and efficient rendering
- **Visual polish**: Smooth animations, particle effects, and screen transitions
- **Two distinct levels**: Prison escape and Financial District themed environments
- **Spawn protection**: Safe starting periods to prevent immediate deaths

## Controls

- **Left/Right or A/D**: Move character
- **Space**: Jump
- **E**: Interact with objects
- **R**: Restart current level
- **ESC**: Pause game
- **D**: Toggle debug mode (shows physics shapes)
- **P**: Toggle post-processing effects (for better performance)

## Technical Highlights

### Optimizations

- **Efficient rendering**: Only draws objects visible in the viewport
- **Pre-calculated visual effects**: Vignette and other effects are generated once
- **Physics optimizations**: Proper collision filtering and sleeping objects
- **Memory management**: Full level cleanup between scenes

### Game Engine Features

- **Pymunk physics integration**: Accurate physics simulation for movement and collisions
- **State management**: Clean transitions between menus, gameplay, and level completion
- **Particle system**: Dynamic visual effects for tokens, deaths, and celebrations
- **Flexible camera system**: Smooth player tracking with level bounds enforcement

## Gameplay Tips

1. Start by exploring the level and collecting X tokens
2. Once you collect enough tokens, you'll transform into wizard form
3. Use spawn protection time to safely get your bearings
4. Watch for moving platforms and time your jumps carefully
5. The Financial District has more complex jumps between buildings

## Credits

Developed as a showcase of the SUPERSEED brand elements, featuring:
- Teal color palette (#93D0CF) as the primary visual identity
- X mark motifs throughout the character design and collectibles
- Character evolution from debt prisoner to financial wizard
