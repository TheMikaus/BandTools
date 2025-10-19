# QMediaDevices Signal Connection Fix

## Issue
The application was encountering an `AttributeError` when trying to connect to the `audioOutputsChanged` signal:

```
AttributeError: 'PyQt6.QtCore.pyqtSignal' object has no attribute 'connect'
  File "backend/audio_engine.py", line 73, in __init__
    QMediaDevices.audioOutputsChanged.connect(self._on_audio_outputs_changed)
```

## Root Cause
The code was attempting to access `audioOutputsChanged` as a class-level attribute of `QMediaDevices`:

```python
QMediaDevices.audioOutputsChanged.connect(self._on_audio_outputs_changed)
```

In PyQt6, signals must be accessed from an **instance** of a class, not from the class itself. The `audioOutputsChanged` signal is an instance signal, not a static/class signal.

## Solution
Created an instance of `QMediaDevices` in the `AudioEngine.__init__` method and connected the signal from that instance:

```python
# Create media devices instance for monitoring device changes
self._media_devices = QMediaDevices()

# Connect to audio device changes from the instance
self._media_devices.audioOutputsChanged.connect(self._on_audio_outputs_changed)
```

## Changes Made
**File:** `AudioBrowserAndAnnotation/AudioBrowser-QML/backend/audio_engine.py`

### Before:
```python
def __init__(self, parent=None):
    """Initialize the audio engine."""
    super().__init__(parent)
    
    # Create media player and audio output
    self._player = QMediaPlayer()
    self._audio_output = QAudioOutput()
    self._player.setAudioOutput(self._audio_output)
    
    # ... other initialization ...
    
    # Connect to audio device changes
    QMediaDevices.audioOutputsChanged.connect(self._on_audio_outputs_changed)  # ❌ WRONG
```

### After:
```python
def __init__(self, parent=None):
    """Initialize the audio engine."""
    super().__init__(parent)
    
    # Create media player and audio output
    self._player = QMediaPlayer()
    self._audio_output = QAudioOutput()
    self._player.setAudioOutput(self._audio_output)
    
    # Create media devices instance for monitoring device changes
    self._media_devices = QMediaDevices()  # ✓ Create instance
    
    # ... other initialization ...
    
    # Connect to audio device changes from the instance
    self._media_devices.audioOutputsChanged.connect(self._on_audio_outputs_changed)  # ✓ CORRECT
```

## Reference Pattern
This fix follows the pattern used in the original `AudioBrowserOrig/audio_browser.py`:

```python
self.media_instance = QMediaDevices()
# ...
self.media_instance.audioOutputsChanged.connect(self._refresh_output_devices)
```

## Static Methods vs Instance Signals
Note that `QMediaDevices` has both static methods and instance signals:

- **Static methods** (called on class): 
  - `QMediaDevices.audioOutputs()` ✓ Works
  - `QMediaDevices.defaultAudioOutput()` ✓ Works
  
- **Instance signals** (require instance):
  - `QMediaDevices().audioOutputsChanged` ✓ Correct
  - `QMediaDevices.audioOutputsChanged` ❌ Wrong

## Impact
This fix resolves the startup crash and allows the application to:
1. Initialize the AudioEngine successfully
2. Monitor audio output device changes
3. Emit signals when audio devices are added or removed

## Testing
The fix was validated by:
1. Python syntax validation (AST parsing)
2. Code structure verification
3. Pattern matching with working reference implementation
