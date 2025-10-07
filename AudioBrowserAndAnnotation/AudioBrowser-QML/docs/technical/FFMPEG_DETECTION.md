# FFmpeg Detection Implementation

## Overview

The AudioBrowser-QML waveform engine uses a robust multi-method FFmpeg detection system to locate and configure FFmpeg for MP3/OGG/FLAC waveform generation.

## Why Separate FFmpeg is Needed

**Important Distinction**: 
- **Qt Multimedia** has built-in FFmpeg for audio **playback** (you'll see "qt.multimedia.ffmpeg: Using Qt multimedia with FFmpeg version X.X.X")
- **Waveform generation** requires a separate FFmpeg installation that `pydub` can access

This is why users may see Qt successfully using FFmpeg for playback, but still get errors about FFmpeg not being found for waveform generation.

## Implementation

### Location
`backend/waveform_engine.py` - `find_ffmpeg()` function

### Detection Methods (in order)

#### Method 1: pydub.utils.which()
- Used first for backward compatibility
- May fail to find FFmpeg on Windows even when it's on PATH
- Issue: Uses a custom implementation instead of OS-standard methods

#### Method 2: shutil.which() (Recommended)
- Python's standard library function
- More reliable on all platforms
- Uses OS-native PATH resolution
- This is the key fix for modern package manager installations (winget, etc.)

#### Method 3: Common Windows Paths
- Checks standard installation locations as fallback
- Covers manual installations and various package managers
- Paths checked:
  - `C:\Program Files\ffmpeg\bin\ffmpeg.exe`
  - `C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe`
  - `C:\ffmpeg\bin\ffmpeg.exe`
  - `~\ffmpeg\bin\ffmpeg.exe`
  - `~\scoop\apps\ffmpeg\current\bin\ffmpeg.exe`

### Configuration

When FFmpeg is found, the code automatically sets:
```python
AudioSegment.converter = <path_to_ffmpeg>
```

This ensures pydub uses the correct FFmpeg executable for all audio operations.

### Caching

The detection result is cached to avoid repeated filesystem lookups:
```python
_ffmpeg_path_cache: Optional[str] = None
_ffmpeg_checked = False
```

### Logging

The detection process logs attempts at different levels:
- `logger.info()`: Successful detection
- `logger.debug()`: Failed methods
- `logger.warning()`: No FFmpeg found after all methods

## Error Messages

The implementation provides context-aware error messages:

1. **FFmpeg not found**: Explains the Qt Multimedia vs separate FFmpeg distinction and provides installation instructions
2. **FFmpeg found but decoding failed**: Suggests corrupted installation or incompatible file format
3. **General decode error**: Falls back to generic error message

## Testing

Run the diagnostic script to verify FFmpeg detection:
```bash
cd AudioBrowser-QML
python3 test_ffmpeg_detection.py
```

Expected output when successful:
```
✓ pydub is available
✓ FFmpeg found at: /usr/bin/ffmpeg
✓ FFmpeg is executable: ffmpeg version 6.x
✓ SUCCESS: FFmpeg detection should work correctly!
```

## Troubleshooting

### FFmpeg installed but not detected

1. Check if FFmpeg is in PATH:
   ```bash
   ffmpeg -version
   ```

2. Run the test script to see which detection method works:
   ```bash
   python3 test_ffmpeg_detection.py
   ```

3. Check application logs for detection attempts

### MP3 playback works but waveforms don't

This is the exact scenario this implementation fixes. The symptoms are:
- You see "qt.multimedia.ffmpeg: Using Qt multimedia with FFmpeg" in console
- MP3 files play correctly
- Waveform generation fails with FFmpeg errors

**Solution**: Install FFmpeg separately as described in README.md

## Related Files

- `backend/waveform_engine.py`: Main implementation
- `test_ffmpeg_detection.py`: Diagnostic script
- `docs/user_guides/WAVEFORM_GUIDE.md`: User-facing troubleshooting
- `README.md`: Installation instructions

## Future Enhancements

Potential improvements (not currently implemented):
- [ ] Automatic FFmpeg download and installation
- [ ] GUI notification when FFmpeg is found/not found
- [ ] Settings panel to manually specify FFmpeg path
- [ ] Support for alternative decoders (avconv)
- [ ] More comprehensive Windows path checking
