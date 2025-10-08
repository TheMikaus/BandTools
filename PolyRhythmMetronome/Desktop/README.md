# PolyRhythmMetronome

A stereo subdivision metronome with multi-layer support, visual flashing, and advanced rhythm features.

## Features

- **Stereo Layers**: Independent rhythm layers for left and right ears
- **Multiple Sound Sources**: 
  - Tone generation (configurable frequency)
  - WAV file playback
  - Drum synthesis (kick, snare, hihat, crash, tom, ride)
- **Per-Layer Controls**:
  - Mute/unmute individual layers
  - Volume control
  - Color coding for visual feedback
  - Subdivision settings (1, 2, 4, 8, 16, 32, 64 notes per beat)
- **Global Settings**:
  - BPM control
  - Time signature (beats per measure)
  - Accent factor for beat 1
  - Visual flash notifications
- **Save/Load**: Save and load rhythm patterns as JSON files
- **WAV Export**: Export your rhythm patterns to stereo WAV files
- **Auto-save**: Automatically saves your current rhythm on changes

## Usage

Run the application:
```bash
python3 Poly_Rhythm_Metronome.py
```

The application will auto-install required dependencies (numpy, sounddevice/simpleaudio).

## Error Logging

If the audio engine encounters errors, they are logged to `metronome_log.txt` in the current directory. The log includes:

- Timestamp of when the error occurred
- Context of what was happening (e.g., "Exception in sounddevice callback")
- Current playback state (running/stopped)
- Number of left and right layers, including how many are muted
- Number of active sounds being mixed
- Full Python traceback for debugging

### Example Log Entry

```
======================================================================
Timestamp: 2025-10-01 14:23:45.123
Context: Exception in sounddevice callback
Running: True
Left layers: 3 (muted: 1)
Right layers: 2 (muted: 0)
Active sounds: 4
----------------------------------------------------------------------
Traceback (most recent call last):
  File "Poly_Rhythm_Metronome.py", line 316, in _callback
    ...
ValueError: Example error message
======================================================================
```

This detailed logging helps diagnose issues, especially when toggling mute states or managing multiple layers during playback.

## Requirements

- Python 3.7+
- numpy
- sounddevice (preferred) or simpleaudio (fallback)
- tkinter (usually included with Python)

## Development

See [CHANGELOG.md](CHANGELOG.md) for version history and recent changes.
