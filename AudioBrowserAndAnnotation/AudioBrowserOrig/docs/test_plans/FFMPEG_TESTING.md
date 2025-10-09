# FFmpeg Detection Testing

## Quick Test

To verify that FFmpeg detection is working correctly on your system, run:

```bash
python test_ffmpeg_detection.py
```

This script will:
1. Check if pydub is installed
2. Test multiple methods of finding FFmpeg
3. Verify FFmpeg is executable
4. Provide installation instructions if issues are found

## Expected Results

### Success Case
```
✓ pydub is available
✓ Found via shutil: C:\Program Files\ffmpeg\bin\ffmpeg.exe
✓ FFmpeg is executable: ffmpeg version 6.0
✓ SUCCESS: FFmpeg detection should work correctly!
```

### Issue Case - Missing FFmpeg
```
✓ pydub is available
✗ Not found via pydub
✗ Not found via shutil
⚠ ISSUE: FFmpeg is not found on your system
```

**Solution**: Install FFmpeg:
- **Windows**: `winget install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`
- **macOS**: `brew install ffmpeg`

### Issue Case - Missing pydub
```
✗ pydub is NOT available: No module named 'pydub'
⚠ ISSUE: pydub is not installed
```

**Solution**: `pip install pydub`

## How the Fix Works

The improved FFmpeg detection in `audio_browser.py`:

1. **Tries pydub's which() first** - For compatibility with existing setups
2. **Falls back to shutil.which()** - More reliable on Windows, uses system PATH
3. **Checks common Windows paths** - Covers manual installations and package managers
4. **Configures pydub automatically** - Sets `AudioSegment.converter` to the found path
5. **Caches the result** - Avoids repeated filesystem lookups

This multi-method approach significantly increases the likelihood of finding FFmpeg even when it's installed in non-standard locations or via different package managers (winget, chocolatey, scoop, etc.).

## What Changed

### Before (Old Behavior)
- Only used `pydub.utils.which()` to find FFmpeg
- This function sometimes fails to find FFmpeg even when it's on the PATH
- Resulted in "No waveform (MP3 needs FFmpeg installed)" errors even with FFmpeg installed

### After (New Behavior)  
- Uses multiple detection methods with fallbacks
- Automatically configures pydub with the found FFmpeg path
- Logs detection attempts for debugging
- Provides helpful error messages with installation instructions

## Log File

The AudioBrowser creates a log file (`audio_browser.log`) that includes FFmpeg detection attempts. Check this file if you're having issues:

```
INFO: FFmpeg found via shutil.which(): C:\Program Files\ffmpeg\bin\ffmpeg.exe
```

or

```
WARNING: FFmpeg not found using any detection method
```

## Testing in AudioBrowser

After ensuring FFmpeg is detected by the test script:

1. Launch AudioBrowser
2. Navigate to a folder with MP3 files
3. Click on an MP3 file
4. The waveform should generate successfully
5. Playback should work

If waveform generation fails, check `audio_browser.log` for FFmpeg-related messages.

## Common Issues

### "pydub.utils.which() found nothing but shutil.which() found FFmpeg"

This is the issue this fix addresses. The old pydub.utils.which() implementation doesn't always find FFmpeg on Windows, especially when installed via winget or other package managers. The new code falls back to Python's standard library shutil.which() which is more reliable.

### "FFmpeg found but waveforms still don't work"

1. Check the log file for errors during audio decode
2. Verify FFmpeg is the correct version (run `ffmpeg -version`)
3. Try with a WAV file first to isolate the issue
4. Restart the application after installing FFmpeg

### "Works with WAV but not MP3"

This confirms pydub/FFmpeg is the issue. Make sure:
1. pydub is installed: `pip install pydub`
2. FFmpeg is installed (see above)
3. The test script shows success
4. Restart AudioBrowser after installing dependencies
