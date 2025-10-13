# Accent Frequency Guide

## Overview

The accent frequency feature allows you to set different frequencies (pitches) for accent beats in tone mode. This makes it easier to hear the downbeat of each measure.

## What is an Accent Beat?

An accent beat is the first beat of each measure. For example, in 4/4 time:
- Beat 1: **Accent beat** (emphasized)
- Beat 2: Regular beat
- Beat 3: Regular beat
- Beat 4: Regular beat

By default, the app already makes accent beats louder using the "Accent" volume slider. Now you can also make them a different pitch!

## How to Use

### Setting Accent Frequency

1. **Set a layer to tone mode**
   - In the layer widget, use the mode dropdown and select "tone"

2. **Set the regular frequency**
   - Enter the frequency for regular beats in the top Hz field
   - Example: `440` (A4 note)

3. **Set the accent frequency**
   - Enter the frequency for accent beats in the bottom "Acc Hz" field
   - Example: `880` (A5 note, one octave higher)

4. **Press PLAY**
   - The first beat of each measure will play at the accent frequency
   - Other beats will play at the regular frequency

### Common Accent Frequency Patterns

#### Octave Higher (Most Common)
Makes the downbeat stand out clearly:
- Regular: 440 Hz
- Accent: 880 Hz (one octave higher)

#### Octave Lower
Creates a "thump" on the downbeat:
- Regular: 440 Hz
- Accent: 220 Hz (one octave lower)

#### Fifth Interval
Musical interval that sounds pleasant:
- Regular: 440 Hz (A)
- Accent: 660 Hz (E, a perfect fifth)

#### Same Frequency
If you only want volume accent (not pitch):
- Regular: 440 Hz
- Accent: 440 Hz (same pitch, but still louder)

## Musical Examples

### Jazz Pattern
```
Left Channel:
- Regular: 440 Hz (A4)
- Accent: 880 Hz (A5)
- Subdivision: 3 (three notes per beat)

Right Channel:
- Regular: 330 Hz (E4)
- Accent: 660 Hz (E5)
- Subdivision: 4 (quarter notes)
```

### Rock Pattern
```
Left Channel:
- Regular: 220 Hz (low thump)
- Accent: 440 Hz (higher click)
- Subdivision: 4

Right Channel:
- Regular: 880 Hz (high beep)
- Accent: 1760 Hz (very high beep)
- Subdivision: 8 (eighth notes)
```

### Classical Practice
```
Both Channels:
- Regular: 440 Hz (A4)
- Accent: 880 Hz (A5)
- Subdivision: 4
- BPM: 60-120

Perfect for counting measures during practice!
```

## Tips

1. **Hearing the Accent**: Set accent frequency at least 1.5x higher or lower than regular frequency for clear distinction

2. **Musical Intervals**: Use these multipliers for pleasant intervals:
   - Octave up: 2.0x (e.g., 440 → 880)
   - Octave down: 0.5x (e.g., 440 → 220)
   - Perfect fifth: 1.5x (e.g., 440 → 660)
   - Perfect fourth: 1.33x (e.g., 440 → 587)

3. **Combining with Volume**: Use both accent frequency AND accent volume for maximum emphasis

4. **Matching Instruments**: If practicing with a specific instrument, match the frequency range to your instrument's pitch

## Automatic Features

### Flash Color
When you change a layer's color, the flash color (the bright color when it beeps) is automatically calculated. You don't need to set it manually anymore - it will always be about 2x brighter than your chosen color.

### Auto-Restart
When you add, delete, or mute a layer while the metronome is playing, it will automatically restart with the new configuration. No need to manually stop and start!

## Troubleshooting

**Q: I can't hear a difference between regular and accent beats**
- A: Make sure the accent frequency is different from the regular frequency
- A: Try an octave difference (2x or 0.5x) for maximum clarity
- A: Check that the accent volume slider is greater than 1.0

**Q: The accent frequency field shows the same as regular frequency**
- A: This is the default behavior - they start the same
- A: Simply edit the accent frequency field to change it

**Q: Accent frequency doesn't work in drum mode**
- A: Correct - accent frequency only applies to tone mode
- A: For drums, only the accent volume affects the first beat

**Q: My saved patterns don't have accent frequencies**
- A: Old patterns will load with accent frequency = regular frequency
- A: Edit and save again to add accent frequencies to your patterns

## Related Features

- **Accent Volume Slider**: Controls how much louder accent beats are (applies to all modes)
- **Subdivision**: Determines how many notes per beat (e.g., "3" = three equal notes per beat)
- **Beats Per Measure**: Determines how often the accent occurs (set in global settings)

## Frequency Reference

Common musical notes and their frequencies:
```
A0:  27.5 Hz    A4:  440 Hz     A7: 3520 Hz
C1:  32.7 Hz    C5:  523 Hz     C8: 4186 Hz
E1:  41.2 Hz    E5:  659 Hz     E8: 5274 Hz
G1:  49.0 Hz    G5:  784 Hz     G8: 6272 Hz

A1:  55.0 Hz    A5:  880 Hz
C2:  65.4 Hz    C6: 1047 Hz
E2:  82.4 Hz    E6: 1319 Hz
G2:  98.0 Hz    G6: 1568 Hz

A2: 110.0 Hz    A6: 1760 Hz
C3: 130.8 Hz    C7: 2093 Hz
E3: 164.8 Hz    E7: 2637 Hz
G3: 196.0 Hz    G7: 3136 Hz

A3: 220.0 Hz
C4: 261.6 Hz (Middle C)
E4: 329.6 Hz
G4: 392.0 Hz
```

## Examples in Action

Try these patterns to get started:

### Simple Measure Counter
- Regular: 440 Hz
- Accent: 880 Hz
- Subdivision: 4
- Perfect for counting 1-2-3-4 in 4/4 time

### Polyrhythm Clarity
- Left: Regular 440 Hz, Accent 880 Hz, Subdiv 3
- Right: Regular 330 Hz, Accent 660 Hz, Subdiv 4
- The accent frequencies help distinguish the two layers

### Practice with Backing
- Set one layer to match your backing track's tempo
- Set another layer as a measure counter with accent frequency
- Never lose track of where you are in the song!

---

For more information, see:
- [User Manual](USER_MANUAL.md) - Complete feature guide
- [Feature Enhancements Test Plan](../test_plans/feature_enhancements_test_plan.md) - Detailed testing
