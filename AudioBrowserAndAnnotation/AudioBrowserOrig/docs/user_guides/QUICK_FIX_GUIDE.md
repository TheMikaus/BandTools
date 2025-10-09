# Quick Fix Guide: MP3 Waveforms Not Working

## TL;DR

If you're seeing "No waveform (MP3 needs FFmpeg installed)" even though you installed FFmpeg:

1. **Close AudioBrowser** if it's running
2. **Run this diagnostic**:
   ```bash
   python test_ffmpeg_detection.py
   ```
3. **Follow the instructions** it provides
4. **Restart AudioBrowser**

That's it! The improved FFmpeg detection should now work.

---

## Detailed Steps

### Step 1: Run the Diagnostic

```bash
cd AudioBrowserAndAnnotation/AudioBrowserOrig
python test_ffmpeg_detection.py
```

### Step 2: Interpret the Results

#### ✅ Good Result
```
✓ pydub is available
✓ Found via shutil: C:\Program Files\ffmpeg\bin\ffmpeg.exe
✓ FFmpeg is executable: ffmpeg version 6.0
✓ SUCCESS: FFmpeg detection should work correctly!
```

**Action**: Just restart AudioBrowser. It should work now!

#### ⚠️ Issue: pydub missing
```
✗ pydub is NOT available: No module named 'pydub'
```

**Fix**: 
```bash
pip install pydub
```

Then run the diagnostic again.

#### ⚠️ Issue: FFmpeg missing
```
✗ Not found via pydub
✗ Not found via shutil
⚠ ISSUE: FFmpeg is not found on your system
```

**Fix (choose one)**:

**Windows**:
```bash
winget install ffmpeg
```

**Linux**:
```bash
sudo apt install ffmpeg
```

**macOS**:
```bash
brew install ffmpeg
```

Then run the diagnostic again.

### Step 3: Restart AudioBrowser

After following the fix steps above:
1. Close AudioBrowser completely
2. Start it again
3. Try loading an MP3 file
4. The waveform should now generate!

---

## Still Not Working?

### Check the Log File

Look at `audio_browser.log` in the same folder as `audio_browser.py`:

**Good** (FFmpeg found):
```
INFO: FFmpeg found via shutil.which(): C:\Program Files\ffmpeg\bin\ffmpeg.exe
```

**Bad** (FFmpeg not found):
```
WARNING: FFmpeg not found using any detection method
```

### Try a WAV File First

WAV files don't need FFmpeg. If WAV files work but MP3 files don't, it confirms this is an FFmpeg issue.

### Verify FFmpeg Installation

Open a terminal/command prompt and run:
```bash
ffmpeg -version
```

If this shows version information, FFmpeg is installed but AudioBrowser can't find it. Please open an issue with:
- Output of `test_ffmpeg_detection.py`
- Output of `ffmpeg -version`
- Contents of `audio_browser.log`

---

## What Changed?

**Old behavior**: AudioBrowser only used pydub's which() to find FFmpeg. This failed for many Windows installations.

**New behavior**: AudioBrowser now tries 3 different methods to find FFmpeg, including the standard Python library method and common installation paths.

This fix specifically addresses FFmpeg installed via:
- winget
- chocolatey
- scoop
- Manual installations

---

## Need More Info?

- **Troubleshooting**: See `FFMPEG_TESTING.md`
- **Technical details**: See `FFMPEG_FIX_SUMMARY.md`
- **All documentation**: See `docs/INDEX.md`
