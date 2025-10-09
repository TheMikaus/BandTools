# FFmpeg Detection Fix - Summary

## Problem

Users reported that MP3 waveforms and playback were not working even after installing FFmpeg via `winget install ffmpeg`. The error message displayed was:

> "No waveform (MP3 needs FFmpeg installed)"

The root cause was that `pydub.utils.which()` was not reliably finding FFmpeg on Windows, particularly when installed via modern package managers like winget.

## Solution

Implemented a robust multi-method FFmpeg detection system that:

1. **Tries multiple detection methods** (pydub.which, shutil.which, common paths)
2. **Automatically configures pydub** to use the found FFmpeg executable
3. **Caches the result** to avoid repeated filesystem lookups
4. **Logs detection attempts** for debugging
5. **Provides helpful error messages** with installation instructions

## Files Modified

### `audio_browser.py`
- Added `find_ffmpeg()` function with multi-method detection
- Replaced 5 instances of `pydub_which("ffmpeg")` with `find_ffmpeg()`
- Added 7 calls to `find_ffmpeg()` before all pydub audio operations
- Improved error messages with multi-platform installation instructions
- Added logging for FFmpeg detection

### New Files
- `test_ffmpeg_detection.py` - Diagnostic script to test FFmpeg detection
- `FFMPEG_TESTING.md` - Documentation for testing and troubleshooting
- `FFMPEG_FIX_SUMMARY.md` - This file

## How to Test

### 1. Run the Test Script

```bash
cd AudioBrowserAndAnnotation/AudioBrowserOrig
python test_ffmpeg_detection.py
```

Expected output on a properly configured system:
```
✓ pydub is available
✓ Found via shutil: C:\Program Files\ffmpeg\bin\ffmpeg.exe
✓ FFmpeg is executable: ffmpeg version 6.0
✓ SUCCESS: FFmpeg detection should work correctly!
```

### 2. Test in AudioBrowser

1. Launch `audio_browser.py`
2. Navigate to a folder containing MP3 files
3. Click on an MP3 file
4. Verify the waveform generates successfully
5. Verify playback works

### 3. Check the Log

Open `audio_browser.log` and look for:
```
INFO: FFmpeg found via shutil.which(): C:\Program Files\ffmpeg\bin\ffmpeg.exe
```

## Technical Details

### Detection Methods (in order)

#### Method 1: pydub.utils.which()
- Used first for backward compatibility
- May fail to find FFmpeg on Windows even when it's on PATH
- Issue: Uses a custom implementation instead of OS-standard methods

#### Method 2: shutil.which() (NEW)
- Python's standard library function
- More reliable on all platforms
- Uses OS-native PATH resolution
- This is the key fix for the winget installation issue

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

## Before vs After

### Before
```python
# Only one method, could fail
if not pydub_which("ffmpeg"):
    show_error("FFmpeg not found")
```

Issues:
- `pydub_which()` sometimes fails on Windows
- No fallback methods
- No automatic pydub configuration
- Generic error message

### After
```python
# Multiple methods with fallbacks
ffmpeg = find_ffmpeg()  # Tries 3 methods, configures pydub
if not ffmpeg:
    show_error_with_instructions()
```

Improvements:
- 3 detection methods with fallbacks
- Automatic pydub configuration
- Caching to avoid repeated lookups
- Detailed logging
- Platform-specific installation instructions

## What This Fixes

✅ MP3 waveform generation with winget-installed FFmpeg  
✅ MP3 playback with winget-installed FFmpeg  
✅ MP3 operations with chocolatey-installed FFmpeg  
✅ MP3 operations with scoop-installed FFmpeg  
✅ MP3 operations with manual FFmpeg installations  
✅ Better error messages when FFmpeg is truly missing  
✅ Logging for troubleshooting  

## What Still Requires FFmpeg

The following features **require FFmpeg** to be installed:

- MP3 file waveform generation
- MP3 file playback
- WAV to MP3 conversion
- Stereo to mono conversion
- Volume boost export
- Any audio format other than WAV

**WAV files** work without FFmpeg (native Python support).

## Installation Instructions (for users)

### If you have FFmpeg but it's not being detected:

1. **First, verify with the test script:**
   ```bash
   python test_ffmpeg_detection.py
   ```

2. **If test shows FFmpeg is not found:**
   - **Windows**: `winget install ffmpeg` (or `choco install ffmpeg`)
   - **Linux**: `sudo apt install ffmpeg`
   - **macOS**: `brew install ffmpeg`

3. **Restart AudioBrowser** after installing FFmpeg

4. **Run the test script again** to verify

### If the test script shows FFmpeg but AudioBrowser still doesn't work:

1. Check `audio_browser.log` for errors
2. Verify you have pydub: `pip install pydub`
3. Try with a WAV file first to isolate the issue
4. Open an issue with the log file contents

## Code Changes Summary

- **Total lines changed**: ~113 insertions
- **Functions added**: 1 (`find_ffmpeg()`)
- **Functions modified**: 8 (added `find_ffmpeg()` calls)
- **Error messages improved**: 4 locations
- **New files**: 3 (test script, 2 documentation files)

## Compatibility

- Python 3.7+
- All platforms (Windows, Linux, macOS)
- PyQt6
- Optional: pydub (required for MP3 support)
- Optional: FFmpeg (required for MP3 support)

## Future Improvements

Potential enhancements (not implemented in this fix):

- [ ] Automatic FFmpeg download and installation
- [ ] GUI notification when FFmpeg is found
- [ ] Settings panel to manually specify FFmpeg path
- [ ] Support for alternative decoders (avconv)

## Questions?

See `FFMPEG_TESTING.md` for detailed testing and troubleshooting information.

For issues, check:
1. `audio_browser.log` - Application log with FFmpeg detection info
2. Run `test_ffmpeg_detection.py` - Diagnostic script
3. Check FFmpeg is installed: `ffmpeg -version`
