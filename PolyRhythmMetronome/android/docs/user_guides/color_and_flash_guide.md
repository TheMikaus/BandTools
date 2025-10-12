# Color Picker and Visual Flash Guide

## Overview
Version 1.1.0 introduces custom layer colors and visual flashing, making it easier to see which layers are playing and when.

## Color Picker

### Setting Layer Colors
Each layer now has a "Color:" field where you can specify a custom color:

1. **Locate the Color Field**: Below the layer's mode and subdivision controls
2. **Enter a Hex Color**: Type a color code like `#FF0000`
3. **See the Change**: The layer background will update to show your color

### Hex Color Format
Colors use hexadecimal format:
- **Full format**: `#RRGGBB` (e.g., `#FF0000` for red)
- **Short format**: `#RGB` (e.g., `#F00` also means red)

### Common Colors
Here are some colors to try:

| Color Name | Hex Code  | Short Form |
|------------|-----------|------------|
| Red        | `#FF0000` | `#F00`     |
| Green      | `#00FF00` | `#0F0`     |
| Blue       | `#0000FF` | `#00F`     |
| Yellow     | `#FFFF00` | `#FF0`     |
| Magenta    | `#FF00FF` | `#F0F`     |
| Cyan       | `#00FFFF` | `#0FF`     |
| Orange     | `#FF8800` | -          |
| Purple     | `#8800FF` | -          |
| Pink       | `#FF0088` | -          |
| White      | `#FFFFFF` | `#FFF`     |

### Color Tips
- **Bright colors** are easier to see when flashing
- **Different colors** for left vs right help distinguish channels
- **Similar colors** for layers in the same channel can group them visually
- **Complementary colors** (e.g., blue/orange) provide good contrast

## Visual Flashing

### How It Works
When you press PLAY, the screen will flash with each layer's color whenever that layer plays a beat.

### Flash Timing
The flash timing matches the layer's subdivision:
- **Subdiv 1** (whole notes): 1 flash per measure
- **Subdiv 2** (half notes): 2 flashes per measure
- **Subdiv 4** (quarter notes): 4 flashes per measure
- **Subdiv 8** (eighth notes): 8 flashes per measure
- **Subdiv 16** (sixteenth notes): 16 flashes per measure

### Multiple Layers
When multiple layers play simultaneously:
- Each layer flashes with its own color
- Colors blend briefly when beats overlap
- Fast subdivisions create more frequent flashes

### Flash Duration
Each flash lasts approximately 0.12 seconds (120 milliseconds), providing visible feedback without being distracting.

## Use Cases

### Practice with Visual Cues
Use different colors to track different rhythmic patterns:
1. **Melody rhythm**: Bright blue layer at quarter notes
2. **Chord rhythm**: Green layer at half notes
3. **Bass rhythm**: Red layer at whole notes

### Complex Polyrhythms
Distinguish between multiple layers:
- **Left hand**: Various shades of blue
- **Right hand**: Various shades of red
- **Accent beats**: Bright yellow

### Visual Metronome
For quiet practice or recording:
- Set volume to minimum
- Watch the flashes instead of listening
- Each flash represents a beat

### Accessibility
Visual flashing helps:
- Musicians in noisy environments
- Practice sessions where audio would disturb others
- Learning complex rhythms by both hearing and seeing

## Examples

### Simple 4/4 Time
```
Left Layer:  Subdiv 4, Color #0088FF (blue)
Right Layer: Subdiv 4, Color #FF0088 (red)
Result: Alternating blue (left) and red (right) flashes on each quarter note
```

### Polyrhythm (3 against 4)
```
Left Layer:  Subdiv 3, Color #00FF00 (green)
Right Layer: Subdiv 4, Color #FF0000 (red)
Result: Green flashes 3 times per measure, red 4 times per measure
```

### Complex Rhythm
```
Left Layer 1:  Subdiv 4,  Color #0000FF (blue)    - Quarter notes
Left Layer 2:  Subdiv 16, Color #8888FF (lt blue) - Sixteenth notes
Right Layer 1: Subdiv 4,  Color #FF0000 (red)     - Quarter notes
Right Layer 2: Subdiv 8,  Color #FF8888 (lt red)  - Eighth notes

Result: Multiple flashing patterns create visual complexity matching the audio
```

## Troubleshooting

### Colors Not Showing
- Check hex format starts with `#`
- Ensure 6 digits for full format or 3 for short
- Only use hex digits: 0-9, A-F

### Flash Too Dim/Bright
- Try different colors - some are naturally brighter
- Adjust your device's screen brightness
- Use lighter colors (#FFAAAA) for subtle flash
- Use darker colors (#880000) for less intensity

### Flash Not Visible
- Ensure layers are not muted
- Check PLAY button is pressed
- Verify at least one layer exists
- Make sure BPM is not too fast (try 60-120 first)

### Multiple Flashes Confusing
- Use fewer layers initially
- Stick to one or two subdivisions
- Use very different colors (red vs blue)
- Mute some layers temporarily

## Advanced Techniques

### Color Coding by Function
Assign colors based on musical function:
- **Downbeats**: Bright colors (#FF0000, #00FF00)
- **Upbeats**: Pastel colors (#FFAAAA, #AAFFAA)
- **Offbeats**: Dark colors (#880000, #008800)

### Gradient for Intensity
Use color intensity to show accent patterns:
- **Strong beats**: #FF0000 (full red)
- **Medium beats**: #CC0000 (medium red)
- **Weak beats**: #880000 (dark red)

### Theme-Based Coloring
Match colors to your practice:
- **Jazz**: Blues and purples
- **Rock**: Reds and oranges
- **Classical**: Silvers and golds (grays)
- **Electronic**: Cyans and magentas

## Tips for Best Results

1. **Start Simple**: Begin with 2 layers and basic colors
2. **High Contrast**: Use very different colors for different channels
3. **Consistent Scheme**: Keep similar layers in similar colors
4. **Adjust Brightness**: Match your environment (darker for night practice)
5. **Experiment**: Try different combinations to find what works for you

## Color Resources

### Online Color Pickers
You can use online tools to find hex codes:
- Google "color picker" for a built-in tool
- Search "hex color codes" for color charts
- Many graphic design sites have color palettes

### Color Wheel Basics
- **Complementary**: Opposite colors (red/green, blue/orange)
- **Analogous**: Adjacent colors (red/orange/yellow)
- **Triadic**: Evenly spaced colors (red/blue/green)

## Feedback

The color and flash system is designed to enhance your practice. If you have suggestions for improvements or different color schemes you'd like to see, please share your feedback!
