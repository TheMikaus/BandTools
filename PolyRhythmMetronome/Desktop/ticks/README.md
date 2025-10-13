# Ticks Folder

This folder contains MP3 (or WAV) files that can be used as tick sounds in the PolyRhythmMetronome.

## File Naming Convention

Audio files in this folder can be used in two ways:

1. **Single Sound**: A regular MP3 file will be used for all ticks
2. **Two Sounds**: Files named with `_1` and `_2` suffixes will be paired
   - Example: `click_1.mp3` and `click_2.mp3` will be treated as a pair
   - The `_1` file is used for accented beats (first beat of measure)
   - The `_2` file is used for regular beats

## Adding Your Own Ticks

Simply place MP3 files in this folder. The application will automatically detect them and make them available in the MP3 tick mode selection.

### Supported Formats
- **MP3** (requires pydub and ffmpeg/libav)
- **WAV** (always supported)

## Creating Your Own Tick Sounds

### Option 1: Record Your Own
Use any audio recording software to record short click sounds (50-100ms).

### Option 2: Generate Programmatically
Use Python with numpy and scipy to generate tones:

```python
import numpy as np
import wave

def create_click(filename, freq=1000, duration=0.05, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(freq * 2 * np.pi * t)
    envelope = np.exp(-t / 0.01)  # Quick decay
    audio = (tone * envelope * 0.5 * 32767).astype(np.int16)
    
    with wave.open(filename, 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(audio.tobytes())

# Create a high click for accents
create_click("ticks/myclick_1.wav", freq=1200)

# Create a low click for regular beats
create_click("ticks/myclick_2.wav", freq=800)
```

### Option 3: Convert to MP3
If you have WAV files, convert them to MP3 using ffmpeg:

```bash
ffmpeg -i ticks/myclick_1.wav -b:a 192k ticks/myclick_1.mp3
ffmpeg -i ticks/myclick_2.wav -b:a 192k ticks/myclick_2.mp3
```

## Example Files

You can add files like:
- `woodblock.mp3` (single sound)
- `click_1.mp3` and `click_2.mp3` (paired - accent and regular)
- `cowbell_1.mp3` and `cowbell_2.mp3` (paired)
- `beep.mp3` (single sound)
- `stick_1.wav` and `stick_2.wav` (paired - WAV format)

## Tips for Good Tick Sounds

1. **Keep them short**: 30-100ms is ideal
2. **High frequencies cut through**: 800-2000 Hz works well
3. **Add attack**: A sharp attack (quick rise) makes the click more pronounced
4. **Normalize volume**: Make sure all your ticks are at similar volume levels
5. **Test with music**: Play your tick alongside music to ensure it's audible

## Troubleshooting

**MP3 files not appearing?**
- Make sure you have pydub installed: `pip install pydub`
- Ensure ffmpeg or libav is installed on your system
- Try using WAV files instead (always supported)

**No sound when playing?**
- Check file permissions
- Verify the audio file isn't corrupted
- Ensure the sample rate is reasonable (44100 Hz is standard)
