# Play Button Icon and Metadata Tab Fix

## Overview

This document describes the fixes for two critical issues in the AudioBrowserQML application:

1. **Play button icon not updating** - The play button in the top bar stays on the play triangle instead of turning into the pause button when audio is playing
2. **Metadata tabs showing no data** - The annotations, clips, sections, folder notes, and fingerprints tabs do not display metadata for the selected song

## Root Causes

### Issue 1: Play Button Icon Not Updating

**Problem:** The play/pause button in `PlaybackControls.qml` was using a direct property binding to check the playback state:

```qml
text: (audioEngine && audioEngine.getPlaybackState() === "playing") ? "⏸" : "▶"
```

However, this binding was only evaluated once and was not listening to the `playbackStateChanged` signal emitted by the audio engine. When the playback state changed, the button text was not being re-evaluated.

**Root Cause:** Missing signal handler to update the button icon when playback state changes.

### Issue 2: Metadata Tabs Not Showing Data

**Problem:** When a file is selected in LibraryTab, the code calls:

```qml
audioEngine.loadAndPlay(model.filepath)
```

This updates the audio engine's current file, but the other managers (annotation_manager, clip_manager, etc.) were not being notified of this change. Each manager has a `setCurrentFile` method that loads the metadata for that file, but this method was never being called when a new file was selected.

**Root Cause:** Missing signal connections from `audioEngine.currentFileChanged` to the metadata managers' `setCurrentFile` methods.

## Solutions

### Fix 1: Play Button Icon Update

**File:** `qml/components/PlaybackControls.qml`

**Change:** Added an `onPlaybackStateChanged` signal handler to the existing Connections block:

```qml
Connections {
    target: audioEngine
    
    // ... existing handlers ...
    
    function onPlaybackStateChanged(state) {
        // Update play/pause button icon when playback state changes
        playPauseButton.text = (state === "playing") ? "⏸" : "▶"
    }
}
```

**How it works:**
- The AudioEngine emits a `playbackStateChanged` signal whenever the playback state changes (playing, paused, stopped)
- The Connections block listens to this signal
- When the signal is emitted, the `onPlaybackStateChanged` handler updates the button text
- The button now correctly shows "⏸" when playing and "▶" when paused/stopped

### Fix 2: Metadata Managers Connection

**File:** `main.py`

**Change:** Added signal connections to notify metadata managers when the audio engine's current file changes:

```python
# Connect audio engine's currentFileChanged to update all metadata managers
# This ensures tabs like annotations, clips, sections, folder notes, and fingerprints
# display the correct metadata when a file is selected
audio_engine.currentFileChanged.connect(annotation_manager.setCurrentFile)
audio_engine.currentFileChanged.connect(clip_manager.setCurrentFile)
```

**How it works:**
- When a file is selected in LibraryTab, `audioEngine.loadAndPlay(filepath)` is called
- The audio engine loads the file and emits `currentFileChanged` signal with the file path
- The annotation_manager and clip_manager receive this signal via their connected slots
- Each manager's `setCurrentFile` method is called, which loads the metadata for that file
- The tabs now display the correct annotations and clips for the selected file

**Note about other tabs:**
- **Sections Tab:** Uses annotation_manager (sections are stored as annotations with a subsection flag)
- **Folder Notes Tab:** Already working correctly - it listens to `fileManager.currentDirectoryChanged` as folder notes are directory-level
- **Fingerprints Tab:** Already working correctly - it operates on directory-level data and listens to `fileManager.currentDirectoryChanged`

## Signal Flow Diagram

### Before Fix

```
LibraryTab: File selected
    ↓
audioEngine.loadAndPlay(filepath)
    ↓
AudioEngine: Load file, start playback
    ↓
AudioEngine: Emit currentFileChanged signal
    ↓
[DEAD END - No connections]
    
Result: annotation_manager and clip_manager don't know about the file change
```

### After Fix

```
LibraryTab: File selected
    ↓
audioEngine.loadAndPlay(filepath)
    ↓
AudioEngine: Load file, start playback
    ↓
AudioEngine: Emit currentFileChanged signal
    ↓  ↓
    ↓  → annotation_manager.setCurrentFile(filepath)
    ↓      ↓
    ↓      → Load annotations from file
    ↓      → Emit annotationsChanged signal
    ↓      → AnnotationsTab updates
    ↓
    → clip_manager.setCurrentFile(filepath)
       ↓
       → Load clips from file
       → Emit clipsChanged signal
       → ClipsTab updates

Result: All metadata tabs display correct data
```

## Testing

### Manual Testing Steps

1. **Test Play Button Icon:**
   - Launch AudioBrowserQML
   - Select a directory with audio files
   - Click on an audio file to start playback
   - Verify the play button changes from "▶" to "⏸"
   - Click the pause button
   - Verify the button changes back from "⏸" to "▶"

2. **Test Annotations Tab:**
   - Create some annotations for a file
   - Select a different file
   - Select the original file again
   - Verify annotations are displayed in the Annotations tab

3. **Test Clips Tab:**
   - Create some clips for a file
   - Select a different file
   - Select the original file again
   - Verify clips are displayed in the Clips tab

4. **Test Sections Tab:**
   - Create some sections for a file
   - Select a different file
   - Select the original file again
   - Verify sections are displayed in the Sections tab

### Automated Testing

A test script `test_play_button_and_metadata.py` was created to verify:
- AudioEngine emits playbackStateChanged signal correctly
- AnnotationManager has setCurrentFile method and it works
- ClipManager has setCurrentFile method and it works
- Signal connections between audio engine and managers work correctly

Run the test with:
```bash
python test_play_button_and_metadata.py
```

## Code Quality

### Changes Made
- **PlaybackControls.qml:** 4 lines added (signal handler)
- **main.py:** 5 lines added (signal connections + comments)

### No Breaking Changes
- All changes are additive - no existing code was removed or modified
- Existing functionality remains intact
- No changes to public APIs

### Performance Impact
- Minimal - signal/slot connections are very efficient in Qt
- Metadata is loaded on-demand only when file changes
- No additional background processing or memory overhead

## Related Files

- `qml/components/PlaybackControls.qml` - Play button component
- `qml/components/NowPlayingPanel.qml` - Already had the signal handler
- `backend/audio_engine.py` - Audio playback engine with signals
- `backend/annotation_manager.py` - Annotation management with setCurrentFile
- `backend/clip_manager.py` - Clip management with setCurrentFile
- `main.py` - Application initialization with signal connections

## Future Enhancements

1. Consider adding a visual indicator when metadata is loading
2. Add error handling if metadata files are corrupted or missing
3. Consider caching recently loaded metadata to improve performance when switching between files
4. Add undo/redo support for metadata changes (already exists for annotations)

## References

- PyQt6 Signals and Slots: https://www.riverbankcomputing.com/static/Docs/PyQt6/signals_slots.html
- QML Connections: https://doc.qt.io/qt-6/qml-qtqml-connections.html
