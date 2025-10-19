# Waveform Display Fix - User Guide

## What Was Fixed

The waveform visualization in the Annotations tab was not displaying. This has been fixed by adding proper signal notifications between the Python backend and QML interface.

## What to Expect

### Before the Fix
- The waveform area would remain empty even after selecting an audio file
- You might see only a blank area or loading indicator
- Annotations and playback markers wouldn't be visible on the waveform

### After the Fix
- The waveform displays immediately when you select an audio file
- You'll see blue vertical lines representing the audio amplitude over time
- A gray horizontal line shows the center axis
- During playback, a red vertical line (playhead) moves across the waveform
- Annotation markers appear on the waveform at their timestamp positions

## How to Verify the Fix

### Step 1: Open the Application
Launch AudioBrowserQML

### Step 2: Navigate to Annotations Tab
Click on the "Annotations" tab in the main window

### Step 3: Select an Audio File
- Use the Library tab to browse to a folder with audio files
- Click on an audio file to select it
- The file should load in the audio engine

### Step 4: Return to Annotations Tab
- Switch back to the Annotations tab
- You should now see the waveform displayed in the upper area

### Step 5: Test Playback
- Click the play button
- Verify the red playhead line moves across the waveform
- Verify the playhead position updates smoothly (20 times per second)

### Step 6: Test Waveform Interaction
- Click anywhere on the waveform
- Verify playback seeks to that position
- Verify the playhead jumps to where you clicked

## Visual Reference

```
┌─────────────────────────────────────────────────────────┐
│ Annotations Tab                                          │
├─────────────────────────────────────────────────────────┤
│ ┌───────────────────────────────────────────────────┐   │
│ │ Waveform Display (should show blue waveform)     │   │
│ │ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│━━ │   │
│ │ ▁▂▃▅▇█▇▅▃▂▁ ▁▂▃▅▇█▇▅▃▂▁ (waveform peaks)       │   │   │
│ │ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│━━ │   │
│ │                      ↑ playhead (red line)        │   │
│ └───────────────────────────────────────────────────┘   │
│                                                          │
│ Annotations List:                                        │
│ ┌───────────────────────────────────────────────────┐   │
│ │ Time     | Text           | Category              │   │
│ │ 0:15.234 | Intro riff     | Structure             │   │
│ │ 1:03.567 | First verse    | Structure             │   │
│ └───────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Color Legend

- **Blue Lines**: Audio waveform peaks showing amplitude
- **Gray Line**: Center axis (zero amplitude)
- **Red Line**: Playhead showing current playback position
- **Colored Markers**: Annotation markers at specific timestamps

## Troubleshooting

### Waveform Still Not Showing

If the waveform still doesn't display after the fix:

1. **Check File Selection**
   - Verify an audio file is actually selected (check the Now Playing area)
   - Try selecting a different file

2. **Check File Format**
   - Verify the file is a supported format (WAV, MP3)
   - Try with a known-good WAV file first

3. **Check Waveform Generation**
   - First time loading a file requires waveform generation
   - This can take 5-30 seconds for large files
   - Look for a loading indicator and progress bar
   - Subsequent loads should be instant (cached)

4. **Check Console Output**
   - Look for any error messages in the terminal
   - Common issues: missing FFmpeg for MP3 files

5. **Check Tab Selection**
   - Ensure you're on the Annotations tab
   - The waveform is currently only shown in the Annotations tab

### Performance Issues

If the waveform displays but performance is poor:

1. **Large Files**
   - Very long audio files (>30 minutes) may have thousands of peaks
   - Consider using clips to work with smaller sections

2. **Slow Generation**
   - Waveform generation happens in background thread
   - First generation takes time, but is cached for subsequent loads
   - MP3 files require FFmpeg and are slower than WAV

## Technical Details

### Waveform Data
- Waveform is represented as 2000 peak samples
- Each peak has min and max amplitude
- Peaks are cached for fast reload

### Update Rate
- Playhead position updates 20 times per second (50ms interval)
- Provides smooth visual feedback during playback

### Caching
- Waveforms are cached in `.waveform_cache.json` in the audio folder
- Cache includes file modification time to detect changes
- Delete cache file to force regeneration

## Getting Help

If you continue to experience issues with waveform display:

1. Check the console output for error messages
2. Verify you have the latest version of the application
3. Try with a simple WAV file first
4. Report the issue on GitHub with:
   - File format and size
   - Console error messages
   - Steps to reproduce

## What's Next

This fix enables:
- Viewing waveforms in Annotations tab ✓
- Adding annotations at specific waveform positions ✓
- Visual feedback during playback ✓
- Click-to-seek on waveform ✓

Future enhancements may include:
- Waveform in other tabs (Library, Clips)
- Zoom and pan controls
- Multiple waveform rendering modes
- Spectrogram view
