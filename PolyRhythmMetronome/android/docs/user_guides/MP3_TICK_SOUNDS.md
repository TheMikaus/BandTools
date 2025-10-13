# Using MP3 Tick Sounds

## Overview

The Android version of PolyRhythmMetronome supports custom MP3 tick sounds, allowing you to use any audio file as your metronome click. This feature uses Android's native media APIs, so no additional software (like ffmpeg) is required.

## Quick Start

1. Place MP3 files in the `ticks/` folder (in the app directory)
2. Restart the app
3. Add a new layer or edit an existing one
4. Select "mp3_tick" from the mode dropdown
5. Choose your tick sound from the second dropdown
6. Start the metronome!

## Preparing MP3 Files

### File Location

MP3 files must be placed in the `ticks/` folder in the app's directory. On Android, this is typically:
- `/data/data/org.bandtools.polyrhythmmetronome/files/ticks/`

You can use a file manager app with root access, or include the files when building the APK.

### File Naming

#### Single Files

For a single sound that plays on all beats:
```
click.mp3           → Appears as "click" in dropdown
woodblock.mp3       → Appears as "woodblock" in dropdown
my_custom_tick.mp3  → Appears as "my_custom_tick" in dropdown
```

#### Paired Files (Accent vs Regular)

For different sounds on accented vs regular beats:
```
woodblock_1.mp3     → Plays on first beat of measure (accent)
woodblock_2.mp3     → Plays on other beats (regular)
                    → Both appear as single "woodblock" entry in dropdown
```

The `_1` file plays on the **first beat of each measure** (the accented beat).  
The `_2` file plays on **all other beats**.

### File Requirements

- **Format**: MP3 (most common encodings supported)
- **Sample Rate**: Any (will be resampled to 44.1kHz)
- **Channels**: Mono or stereo (stereo will be converted to mono)
- **Duration**: Keep under 1 second for best performance
- **Bitrate**: Any (higher bitrate = larger file, but no quality difference after decoding)
- **File Size**: Recommended under 100 KB per file

### Recommended Settings

For best results, prepare your MP3 files with these settings:
- **Sample Rate**: 44100 Hz
- **Bitrate**: 128 kbps
- **Channels**: Mono
- **Duration**: 50-200ms for short clicks, up to 500ms for longer sounds

## Using MP3 Ticks

### Adding an MP3 Tick Layer

1. Tap the **+** button next to "LEFT Layers" or "RIGHT Layers"
2. A new layer appears with default settings
3. Tap the **mode spinner** (default shows "tone")
4. Select **"mp3_tick"** from the list
5. The second spinner now shows available MP3 ticks
6. Select your desired tick sound
7. Adjust volume and subdivision as needed
8. Tap **Play** to hear it

### Switching Between Ticks

You can change the tick sound at any time:
1. Tap the second spinner (shows current tick name)
2. Select a different tick from the list
3. The change takes effect immediately (even while playing)

### Volume Control

Each layer has an independent volume slider (0.0 to 2.0):
- **0.0** = Silent (muted)
- **1.0** = Original volume
- **2.0** = Double volume

### Accent Volume

Each layer also has an accent volume multiplier (1.0 to 3.0):
- Controls how much louder the first beat of each measure is
- **1.0** = No accent (same volume as other beats)
- **1.6** = Default (60% louder on first beat)
- **3.0** = Triple volume on first beat

For paired MP3 ticks, the accent volume applies to the `_1` file.

## Examples

### Example 1: Single Click Sound

Place `click.mp3` in `ticks/` folder:
```
ticks/
  └── click.mp3
```

In the app:
- Mode dropdown: Select "mp3_tick"
- Tick dropdown: Select "click"
- Result: Same click sound on all beats

### Example 2: Woodblock with Accent

Place two files in `ticks/` folder:
```
ticks/
  ├── woodblock_1.mp3  (higher pitch for accent)
  └── woodblock_2.mp3  (lower pitch for regular)
```

In the app:
- Mode dropdown: Select "mp3_tick"
- Tick dropdown: Select "woodblock"
- Set beats per measure to 4
- Result: 
  - First beat = woodblock_1.mp3 (high pitch)
  - Beats 2, 3, 4 = woodblock_2.mp3 (low pitch)

### Example 3: Mixed Layers

Create multiple layers with different ticks:
```
ticks/
  ├── kick.mp3
  ├── snare.mp3
  ├── hihat_1.mp3
  └── hihat_2.mp3
```

Left ear:
- Layer 1: MP3 tick "kick", subdivision 4 (quarter notes)
- Layer 2: MP3 tick "hihat", subdivision 8 (eighth notes)

Right ear:
- Layer 1: MP3 tick "snare", subdivision 4 (quarter notes)

Result: Basic drum beat pattern!

## Troubleshooting

### Tick doesn't appear in dropdown

**Causes:**
- File is not in `ticks/` folder
- File extension is not `.mp3`
- App hasn't been restarted since adding file

**Solutions:**
1. Verify file is in correct location
2. Check file extension (must be `.mp3`)
3. Restart the app
4. Check file permissions (must be readable by app)

### No sound when playing

**Causes:**
- Volume is set to 0
- Layer is muted
- MP3 file is corrupted or unreadable
- Device volume is muted

**Solutions:**
1. Check layer volume slider (should be > 0)
2. Make sure mute button is not pressed
3. Try a different MP3 file
4. Check device volume
5. Look for error messages in logs

### Sound is distorted or choppy

**Causes:**
- MP3 file has very high or low sample rate
- File is corrupted
- Volume is set too high (> 1.5 can cause clipping)

**Solutions:**
1. Use MP3 files with 44.1kHz sample rate
2. Try a different file
3. Lower the volume slider
4. Re-encode the MP3 with standard settings

### App is slow to start

**Causes:**
- Too many MP3 files in ticks folder
- MP3 files are very large
- Files have very high sample rates

**Solutions:**
1. Limit to 20-30 tick sounds
2. Keep files under 100 KB each
3. Use shorter duration sounds (< 500ms)
4. Remove unused files

### Paired files not working

**Causes:**
- Files don't have matching `_1` and `_2` suffixes
- Base names don't match exactly
- One file is missing

**Solutions:**
1. Verify file names: `name_1.mp3` and `name_2.mp3`
2. Make sure base name matches exactly (case sensitive)
3. Both files must be present

## Advanced Usage

### Creating Custom Tick Sounds

You can create custom tick sounds using audio editing software:

1. **Audacity** (free, open-source):
   - Generate → Tone → Create click sound
   - Trim to desired length (50-200ms)
   - File → Export → Export as MP3

2. **GarageBand** (Mac/iOS):
   - Record custom sound
   - Trim to length
   - Export as MP3

3. **Online Tools**:
   - Use online tone generators
   - Download as MP3
   - Trim if needed

### Finding Tick Sounds

Free resources for metronome sounds:
- **Freesound.org** - Search for "metronome", "click", "woodblock"
- **YouTube Audio Library** - Percussion sounds
- **Sample packs** - Look for percussion one-shots

Always check license terms before using downloaded sounds.

### Organizing Tick Sounds

For large collections, use descriptive names:
```
ticks/
  ├── click_digital.mp3
  ├── click_analog.mp3
  ├── woodblock_bright_1.mp3
  ├── woodblock_bright_2.mp3
  ├── cowbell_loud.mp3
  └── rim_shot.mp3
```

Names appear in alphabetical order in the dropdown.

## Performance Tips

1. **Shorter is better**: 50-200ms sounds load faster and use less memory
2. **Mono over stereo**: Mono files are half the size and load faster
3. **Standard sample rate**: 44.1kHz files don't need resampling
4. **Limit quantity**: Keep under 30 files for best startup performance
5. **Compress appropriately**: 128 kbps is sufficient quality

## Technical Details

- MP3 decoding uses Android's **MediaCodec API**
- No external libraries required (ffmpeg not needed)
- Files are decoded once at startup and cached in memory
- Hardware-accelerated decoding when available
- Supports all MP3 variants that Android supports
- Memory usage: ~17 KB per 100ms of decoded audio

## See Also

- [Technical Documentation](../technical/MP3_MEDIACODEC_IMPLEMENTATION.md) - Implementation details
- [Layer Configuration Guide](LAYER_CONFIGURATION.md) - Layer settings explained
- [README](../../README.md) - App overview and installation
