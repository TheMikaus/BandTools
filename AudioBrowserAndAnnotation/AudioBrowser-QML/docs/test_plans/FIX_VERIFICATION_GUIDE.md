# Fix Verification Guide

## Overview

This guide explains how to verify the fixes for two critical AudioBrowserQML issues:

1. **Play button icon not updating** - Button stays on play triangle instead of changing to pause
2. **Metadata tabs showing no data** - Annotations, clips, and sections tabs don't display metadata

## What Was Fixed

### Issue 1: Play Button Icon
**File Modified:** `qml/components/PlaybackControls.qml`

**Change:** Added signal handler to update button icon when playback state changes

```qml
function onPlaybackStateChanged(state) {
    // Update play/pause button icon when playback state changes
    playPauseButton.text = (state === "playing") ? "⏸" : "▶"
}
```

### Issue 2: Metadata Display
**File Modified:** `main.py`

**Changes:** Added signal connections to notify managers of file changes

```python
# Connect audio engine's currentFileChanged to update all metadata managers
audio_engine.currentFileChanged.connect(annotation_manager.setCurrentFile)
audio_engine.currentFileChanged.connect(clip_manager.setCurrentFile)
```

## Quick Verification Steps

### 1. Play Button Icon Test (30 seconds)

```
Launch app → Select audio file → Click play button → Verify icon changes to pause ⏸
Click pause → Verify icon changes back to play ▶
```

**Expected Result:**
- When playing: Button shows ⏸ (pause icon)
- When paused/stopped: Button shows ▶ (play icon)

**If it fails:**
- Button stays as ▶ even when audio is playing
- Check browser console for QML errors

### 2. Annotations Display Test (1 minute)

```
Select file with annotations → Click Annotations tab → Verify annotations appear
```

**Expected Result:**
- Annotations table shows all annotations for the selected file
- Count at top shows correct number of annotations

**If it fails:**
- Table is empty even though file has annotations
- Check browser console for JavaScript errors
- Verify annotations file exists (`.annotations.json` in same directory)

### 3. Clips Display Test (1 minute)

```
Select file with clips → Click Clips tab → Verify clips appear
```

**Expected Result:**
- Clips list shows all clips for the selected file
- Each clip shows start time, end time, and name

**If it fails:**
- List is empty even though file has clips
- Check browser console for JavaScript errors
- Verify clips file exists (`.clips.json` in same directory)

### 4. Sections Display Test (1 minute)

```
Select file with sections → Click Sections tab → Verify sections appear
```

**Expected Result:**
- Sections table shows all sections for the selected file
- Each section shows name, start time, and end time

**If it fails:**
- Table is empty even though file has sections
- Sections are stored as annotations with subsection flag
- Check annotations file

## Detailed Verification Steps

### Setup (First Time Only)

1. **Launch AudioBrowserQML:**
   ```bash
   cd AudioBrowserAndAnnotation/AudioBrowser-QML
   python main.py
   ```

2. **Open a folder with audio files:**
   - Click the folder button (📁) in the Library tab
   - Navigate to a folder with MP3 or WAV files
   - Click "Select Folder"

3. **Create test data** (if you don't have any):
   - Select an audio file
   - Go to Annotations tab
   - Click "Add" and create a test annotation
   - Go to Clips tab
   - Click "Add Clip" and create a test clip
   - Go to Sections tab
   - Click "Add Section" and create a test section

### Test 1: Play Button Icon Changes

**Purpose:** Verify that the play button icon changes when playback starts/stops

**Steps:**

1. In Library tab, click on any audio file
2. Observe the play button in the top toolbar (should show ▶)
3. Click the play button
4. **CHECK:** Button should immediately change to ⏸ (pause icon)
5. Wait for audio to start playing
6. **CHECK:** Button should still show ⏸
7. Click the pause button
8. **CHECK:** Button should immediately change back to ▶
9. Repeat with different files

**Expected Results:**
- ✅ Button shows ▶ when stopped
- ✅ Button shows ⏸ when playing
- ✅ Icon changes immediately when button is clicked
- ✅ Icon stays correct during playback

**Troubleshooting:**
- If button doesn't change: Check QML console for errors
- If button flickers: This is normal during the transition
- If button changes slowly: This might indicate high CPU usage

### Test 2: Annotations Tab Displays Data

**Purpose:** Verify that annotations appear when a file with annotations is selected

**Steps:**

1. In Library tab, select a file that has annotations
   - Files with annotations will have a ⭐ icon
2. Click the "Annotations" tab
3. **CHECK:** The tab should show "Annotations (X)" where X is the number of annotations
4. **CHECK:** The table should display all annotations with:
   - Timestamp
   - Category
   - Text
   - User (if multi-user is enabled)
5. Select a different file
6. **CHECK:** Annotations update to show the new file's annotations
7. Select the original file again
8. **CHECK:** Original annotations are displayed again

**Expected Results:**
- ✅ Annotation count is correct
- ✅ All annotations are displayed
- ✅ Annotations change when file selection changes
- ✅ No delay in updating annotations

**Troubleshooting:**
- If no annotations appear:
  - Check that `.annotations.json` file exists in the same directory as the audio file
  - Check browser console for errors
  - Try creating a new annotation to verify the feature works
- If wrong annotations appear:
  - Check that the file path is correct
  - Verify that audio engine has loaded the file (check Now Playing panel)

### Test 3: Clips Tab Displays Data

**Purpose:** Verify that clips appear when a file with clips is selected

**Steps:**

1. In Library tab, select a file that has clips
2. Click the "Clips" tab
3. **CHECK:** The tab should show a list of clips
4. **CHECK:** Each clip should show:
   - Clip name
   - Start time (formatted as MM:SS)
   - End time (formatted as MM:SS)
   - Duration
5. Select a different file
6. **CHECK:** Clips update to show the new file's clips
7. Select the original file again
8. **CHECK:** Original clips are displayed again

**Expected Results:**
- ✅ All clips are displayed
- ✅ Clip information is correct
- ✅ Clips change when file selection changes
- ✅ No delay in updating clips

**Troubleshooting:**
- If no clips appear:
  - Check that `.clips.json` file exists in the same directory as the audio file
  - Check browser console for errors
  - Try creating a new clip to verify the feature works
- If wrong clips appear:
  - Check that the file path is correct
  - Verify that audio engine has loaded the file

### Test 4: Sections Tab Displays Data

**Purpose:** Verify that sections appear when a file with sections is selected

**Steps:**

1. In Library tab, select a file that has sections
2. Click the "Sections" tab
3. **CHECK:** The tab should show a table of sections
4. **CHECK:** Each section should show:
   - Section name (e.g., "Intro", "Verse", "Chorus")
   - Start time
   - End time
5. Select a different file
6. **CHECK:** Sections update to show the new file's sections
7. Select the original file again
8. **CHECK:** Original sections are displayed again

**Expected Results:**
- ✅ All sections are displayed
- ✅ Section information is correct
- ✅ Sections change when file selection changes
- ✅ No delay in updating sections

**Troubleshooting:**
- Sections are stored as annotations with a special flag
- If no sections appear:
  - Check that `.annotations.json` file exists
  - Check that annotations have `subsection: true` flag
  - Try creating a new section to verify the feature works

## Automated Tests

A test script is provided to verify the signal connections work correctly:

```bash
cd AudioBrowserAndAnnotation/AudioBrowser-QML
python test_play_button_and_metadata.py
```

**Expected Output:**
```
======================================================================
Testing Play Button Icon and Metadata Manager Connections
======================================================================

=== Testing Annotation Manager Connection ===
  ✓ AnnotationManager has setCurrentFile method
  ✓ AnnotationManager correctly sets current file

=== Testing Clip Manager Connection ===
  ✓ ClipManager has setCurrentFile method
  ✓ ClipManager correctly sets current file

======================================================================
Test Summary
======================================================================
✓ PASS: Annotation Manager Connection
✓ PASS: Clip Manager Connection

Total: 2/2 tests passed

✓ All tests passed!
```

## Common Issues

### Play Button Icon Not Updating

**Symptom:** Button stays as ▶ even when audio is playing

**Possible Causes:**
1. QML syntax error in PlaybackControls.qml
2. Signal not being emitted from audio engine
3. Binding not being updated

**Solutions:**
1. Check browser console for QML errors
2. Verify audioEngine is not null
3. Check that playbackStateChanged signal is connected

### Annotations Not Displaying

**Symptom:** Annotation tab is empty even though file has annotations

**Possible Causes:**
1. Signal connection missing or broken
2. Annotation file doesn't exist
3. Audio engine hasn't loaded the file yet

**Solutions:**
1. Check browser console for errors
2. Verify `.annotations.json` file exists in audio file directory
3. Check that audioEngine.getCurrentFile() returns the correct path
4. Verify signal connection in main.py is present

### Clips Not Displaying

**Symptom:** Clips tab is empty even though file has clips

**Possible Causes:**
1. Signal connection missing or broken
2. Clips file doesn't exist
3. Audio engine hasn't loaded the file yet

**Solutions:**
1. Check browser console for errors
2. Verify `.clips.json` file exists in audio file directory
3. Check that audioEngine.getCurrentFile() returns the correct path
4. Verify signal connection in main.py is present

## Success Criteria

The fixes are working correctly if:

- ✅ Play button icon changes from ▶ to ⏸ when playback starts
- ✅ Play button icon changes from ⏸ to ▶ when playback pauses
- ✅ Annotations appear immediately when a file is selected
- ✅ Clips appear immediately when a file is selected
- ✅ Sections appear immediately when a file is selected
- ✅ Metadata updates correctly when switching between files
- ✅ No console errors related to signals or metadata loading

## Additional Resources

- **Technical Documentation:** `docs/technical/PLAY_BUTTON_AND_METADATA_FIX.md`
- **Visual Guide:** `docs/user_guides/PLAY_BUTTON_FIX_VISUAL_GUIDE.md`
- **Test Script:** `test_play_button_and_metadata.py`

## Support

If you encounter issues not covered in this guide:

1. Check the browser/JavaScript console for errors
2. Check the Python console for backend errors
3. Review the technical documentation for detailed implementation details
4. Create an issue on GitHub with:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Console errors (if any)

---

**Last Updated:** January 2025  
**Related Issue:** Play button icon and metadata display fix
