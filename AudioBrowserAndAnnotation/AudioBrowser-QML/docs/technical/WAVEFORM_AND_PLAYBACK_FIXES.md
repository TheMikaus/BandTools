# Waveform Display and Playback Fixes

## Overview
This document describes the fixes applied to resolve two critical issues in AudioBrowserQML:
1. Waveform not displaying when a file is selected
2. Playback not starting when the play button is clicked

## Issues Identified

### Issue 1: Waveform Does Not Display
**Problem**: When a user selected an audio file in the Library tab, the waveform did not appear in the Annotations tab.

**Root Cause**: The `WaveformDisplay.qml` component had a `filePath` property that was being set by parent components, but there was no change handler (`onFilePathChanged`) to trigger waveform generation when this property changed.

**Solution**: Added an `onFilePathChanged` handler that calls `setFilePath(filePath)` whenever the `filePath` property is modified. This ensures that:
- If the waveform is already cached, it's loaded immediately
- If not cached and `autoGenerate` is true, waveform generation begins automatically

### Issue 2: Playback Does Not Start
**Problem**: When a user clicked on an audio file to play it, the playback would not start.

**Root Cause**: The code was calling `audioEngine.loadFile(filepath)` followed immediately by `audioEngine.play()`. However, `QMediaPlayer` requires time to load the media file before playback can begin. The `play()` call was happening before the media was loaded, causing it to fail silently.

**Solution**: Implemented a new `loadAndPlay()` method in the AudioEngine that:
1. Sets an internal `_autoplay_pending` flag
2. Loads the media file
3. Waits for the `LoadedMedia` status signal
4. Automatically starts playback once the media is ready

## Technical Details

### WaveformDisplay.qml Changes

#### Added Property Change Handler
```qml
// Handle filePath changes
onFilePathChanged: {
    setFilePath(filePath)
}
```

This handler ensures that whenever the `filePath` property is updated (e.g., when a new file is selected), the component automatically:
- Checks if a cached waveform exists
- Loads cached data if available
- Generates a new waveform if not cached and `autoGenerate` is true

#### Added Position Update Timer
```qml
// Timer to regularly update playback position
Timer {
    id: positionUpdateTimer
    interval: 50  // Update every 50ms for smooth animation
    running: audioEngine && audioEngine.isPlaying()
    repeat: true
    
    onTriggered: {
        if (audioEngine) {
            waveform.positionMs = audioEngine.getPosition()
        }
    }
}
```

This timer provides smooth visual feedback by updating the playback position indicator 20 times per second while audio is playing.

### AudioEngine Changes

#### Added Autoplay State Tracking
```python
self._autoplay_pending = False  # Flag to track if we should play after loading
```

#### New loadAndPlay() Method
```python
@pyqtSlot(str)
def loadAndPlay(self, file_path: str) -> None:
    """
    Load an audio file and automatically play when ready.
    
    Args:
        file_path: Path to the audio file
    """
    try:
        path = Path(file_path)
        if not path.exists():
            self.errorOccurred.emit(f"File not found: {file_path}")
            return
        
        self._current_file = path
        self._autoplay_pending = True  # Set flag to play when loaded
        self._player.setSource(QUrl.fromLocalFile(str(path)))
        self.currentFileChanged.emit(str(path))
        
    except Exception as e:
        self.errorOccurred.emit(f"Error loading file: {e}")
        self._autoplay_pending = False
```

#### Enhanced Media Status Handler
```python
def _on_media_status_changed(self, status: QMediaPlayer.MediaStatus) -> None:
    """Handle media status changes from the media player."""
    # ... existing code ...
    
    # Auto-play when media is loaded if requested
    if status == QMediaPlayer.MediaStatus.LoadedMedia and self._autoplay_pending:
        self._autoplay_pending = False
        self.play()
```

### QML Updates

#### LibraryTab.qml
Changed from:
```qml
audioEngine.loadFile(model.filepath)
audioEngine.play()
```

To:
```qml
audioEngine.loadAndPlay(model.filepath)
```

#### FileContextMenu.qml
Changed from:
```qml
audioEngine.loadFile(filePath);
audioEngine.play();
```

To:
```qml
audioEngine.loadAndPlay(filePath);
```

## Benefits

1. **Immediate Waveform Display**: Users now see waveforms as soon as they select a file
2. **Reliable Playback**: Audio playback starts consistently when files are selected
3. **Smooth Playback Position**: The waveform playhead tracks playback smoothly at 20 FPS
4. **Reduced Code Complexity**: Single `loadAndPlay()` call replaces two separate calls
5. **Better Error Handling**: The autoplay flag is properly reset on errors

## Testing

### Manual Testing Steps
1. **Waveform Display Test**:
   - Launch AudioBrowserQML
   - Select a folder containing audio files
   - Click on an audio file in the Library tab
   - Switch to the Annotations tab
   - Verify that the waveform appears

2. **Playback Test**:
   - Click on an audio file in the Library tab
   - Verify that audio starts playing
   - Observe the playback position indicator moving smoothly across the waveform

3. **Double-Click Test**:
   - Double-click an audio file in the Library tab
   - Verify that the Annotations tab opens and playback starts

### Automated Testing
Run the test script:
```bash
python3 test_waveform_and_playback.py
```

This verifies:
- QML syntax is valid
- Required methods exist in AudioEngine
- Required methods exist in WaveformEngine

## Backwards Compatibility

The changes are fully backwards compatible:
- The original `loadFile()` method still exists and works as before
- The new `loadAndPlay()` method is an addition, not a replacement
- Existing code that doesn't use `loadAndPlay()` will continue to work

## Future Improvements

Possible enhancements for the future:
1. Add user preference for autoplay behavior
2. Implement waveform zoom and pan controls
3. Add visual indicators for buffering state
4. Support for multiple waveform rendering modes (outline, filled, etc.)

## Related Files

### Modified Files
- `qml/components/WaveformDisplay.qml`
- `backend/audio_engine.py`
- `qml/tabs/LibraryTab.qml`
- `qml/components/FileContextMenu.qml`

### Test Files
- `test_waveform_and_playback.py` (new)

## Version History
- **Initial Fix** (2025-10-16): Added onFilePathChanged handler and position update timer
- **Playback Fix** (2025-10-16): Added loadAndPlay method to fix timing issue
