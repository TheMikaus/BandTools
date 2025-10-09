# FFmpeg Detection Fix - Summary

## Problem

Users reported seeing the message "qt.multimedia.ffmpeg: Using Qt multimedia with FFmpeg version 7.1.1" but the software still didn't think it could decode MP3s for waveform generation.

The root cause was that **Qt Multimedia has built-in FFmpeg for playback**, but **waveform generation uses pydub which requires a separate FFmpeg installation** that it can find on the system.

The AudioBrowserOrig already had a robust `find_ffmpeg()` function to handle this, but the AudioBrowser-QML version lacked this functionality.

## Solution

Ported the robust multi-method FFmpeg detection system from AudioBrowserOrig to AudioBrowser-QML that:

1. **Tries multiple detection methods** (pydub.which, shutil.which, common paths)
2. **Automatically configures pydub** to use the found FFmpeg executable
3. **Caches the result** to avoid repeated filesystem lookups
4. **Logs detection attempts** for debugging
5. **Provides helpful error messages** that explain the Qt Multimedia vs separate FFmpeg distinction

## What This Fixes

✅ MP3 waveform generation with FFmpeg installed via any method  
✅ MP3 operations with winget/chocolatey/scoop/manual FFmpeg installations  
✅ Better error messages that explain the Qt vs pydub FFmpeg distinction  
✅ Logging for troubleshooting  

## What Still Requires FFmpeg

The following features **require a separate FFmpeg installation** for pydub:

- MP3/OGG/FLAC file waveform generation
- Audio format conversions
- Any non-WAV audio processing

**Note**: MP3/OGG/FLAC playback will work without a separate FFmpeg (Qt's built-in), but waveform display won't.

**WAV files** work without any FFmpeg (native Python support).

## Technical Details

### Detection Methods (in order)

#### Method 1: pydub.utils.which()
- Used first for backward compatibility
- May fail to find FFmpeg on Windows even when it's on PATH
- Issue: Uses a custom implementation instead of OS-standard methods

#### Method 2: shutil.which() (NEW - Key Fix)
- Python's standard library function
- More reliable on all platforms
- Uses OS-native PATH resolution
- This fixes detection for modern package manager installations (winget, etc.)

#### Method 3: Common Windows Paths (NEW)
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

## Files Modified

### `backend/waveform_engine.py`
- Added imports: `os`, `sys`, `shutil`, `logging`, `pydub.utils.which`
- Added `find_ffmpeg()` function with multi-method detection
- Added caching variables: `_ffmpeg_path_cache`, `_ffmpeg_checked`
- Updated `_decode_audio_samples()` to call `find_ffmpeg()` before pydub operations
- Enhanced error messages to explain Qt Multimedia vs separate FFmpeg

### New Files
- `test_ffmpeg_detection.py` - Diagnostic script to test FFmpeg detection
- `docs/technical/FFMPEG_DETECTION.md` - Technical documentation
- `FFMPEG_FIX_SUMMARY.md` - This file

### Documentation Updates
- `README.md` - Added FFmpeg requirement section
- `docs/user_guides/WAVEFORM_GUIDE.md` - Updated troubleshooting section

## How to Test

### 1. Run the Test Script

```bash
cd AudioBrowser-QML
python3 test_ffmpeg_detection.py
```

Expected output on a properly configured system:
```
✓ pydub is available
✓ FFmpeg found at: /usr/bin/ffmpeg
✓ FFmpeg is executable: ffmpeg version 6.x
✓ SUCCESS: FFmpeg detection should work correctly!
```

### 2. Test in AudioBrowser-QML

1. Launch the application: `python3 main.py`
2. Navigate to a folder containing MP3 files
3. Select an MP3 file
4. Verify the waveform generates successfully
5. Verify playback works

### 3. Check the Log

Look for FFmpeg detection messages in application logs:
```
INFO: FFmpeg found via shutil.which(): /usr/bin/ffmpeg
```

## Installation Instructions

To install FFmpeg:
- **Windows**: `winget install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`
- **macOS**: `brew install ffmpeg`

To install pydub (required for MP3 support):
```bash
pip install pydub
```

## Before vs After

### Before
- Only Qt's built-in FFmpeg was used (playback only)
- No FFmpeg detection for waveform generation
- Confusing error messages when MP3 playback worked but waveforms didn't
- Users saw "qt.multimedia.ffmpeg" message but got "FFmpeg not found" errors

### After
- Multi-method FFmpeg detection for waveform generation
- Automatic pydub configuration
- Clear error messages explaining the distinction
- Works with any FFmpeg installation method
- Helpful diagnostic script included

## Compatibility

- Python 3.7+
- All platforms (Windows, Linux, macOS)
- PyQt6 with Qt Quick
- Optional: pydub (required for MP3/OGG/FLAC support)
- Optional: FFmpeg (required for MP3/OGG/FLAC waveform generation)

## Related Documentation

- `docs/technical/FFMPEG_DETECTION.md` - Detailed technical documentation
- `docs/user_guides/WAVEFORM_GUIDE.md` - User guide with troubleshooting
- `test_ffmpeg_detection.py` - Diagnostic script
- `README.md` - Installation and setup

## Code Changes Summary

- **Total lines changed**: ~120 insertions in waveform_engine.py
- **Functions added**: 1 (`find_ffmpeg()`)
- **Functions modified**: 1 (`_decode_audio_samples()`)
- **Error messages improved**: 2 locations
- **New files**: 3 (test script, 2 documentation files)
- **Documentation updates**: 3 files

## Future Improvements

Potential enhancements (not implemented in this fix):

- [ ] Automatic FFmpeg download and installation
- [ ] GUI notification when FFmpeg is found/not found
- [ ] Settings panel to manually specify FFmpeg path
- [ ] Support for alternative decoders (avconv)
- [ ] Integration test with actual MP3 files in CI/CD
