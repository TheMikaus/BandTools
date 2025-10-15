# PolyRhythmMetronome

A stereo subdivision metronome with multi-layer support, visual flashing, and advanced rhythm features.

## Features

- **Stereo Layers**: Independent rhythm layers for left and right ears
- **Multiple Sound Sources**: 
  - Tone generation (configurable frequency)
  - WAV file playback
  - MP3 file playback (from ticks folder)
  - Drum synthesis (kick, snare, hihat, crash, tom, ride)
- **Per-Layer Controls**:
  - Mute/unmute individual layers
  - Volume control
  - Color coding for visual feedback (random dark colors assigned automatically)
  - Separate flash colors (automatically brightened from inactive color)
  - Subdivision settings (1, 2, 4, 8, 16, 32, 64 notes per beat)
- **Global Settings**:
  - BPM control
  - Time signature (beats per measure)
  - Accent factor for beat 1
  - Visual flash notifications
- **Verbose Logging**: Real-time timing information for debugging and analysis
  - Shows delta between actual and expected intervals
  - Scrollable log window with clear function
  - Per-layer timing details
- **Save/Load**: Save and load rhythm patterns as JSON files
- **WAV Export**: Export your rhythm patterns to stereo WAV files
- **Auto-save**: Automatically saves your current rhythm on changes

## Usage

Run the application:
```bash
python3 Poly_Rhythm_Metronome.py
```

The application will auto-install required dependencies (numpy, sounddevice/simpleaudio).

### Verbose Logging

Enable verbose logging by checking the "Verbose Log" checkbox in the application. This will display a scrollable log window showing real-time timing information for each sound:

```
[12:34:56.789] Left Layer 1 (subdiv=4): played | Delta: 250.00ms | Expected: 250.00ms
[12:34:57.039] Right Layer 1 (subdiv=3): played | Delta: 333.33ms | Expected: 333.33ms
```

This is useful for:
- Debugging timing issues
- Verifying tempo accuracy
- Understanding how different subdivisions interact

See [docs/user_guides/verbose_logging.md](docs/user_guides/verbose_logging.md) for detailed usage instructions.

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
- pydub (optional, for MP3 support - requires ffmpeg or libav)

## Building Executable

To build a standalone executable:

### Linux/Mac
```bash
./build.sh
```

### Windows
```batch
build.bat
```

The executable will be created in the `dist` folder. The build automatically includes the `ticks` folder for MP3 tick sounds.

## MP3 Tick Sounds

Place MP3 files in the `ticks` folder to use them as metronome sounds:
- Single files: `click.mp3` - used for all beats
- Paired files: `click_1.mp3` and `click_2.mp3` - _1 for accented beats, _2 for regular beats

See `ticks/README.md` for more details.

## Development

See [CHANGELOG.md](CHANGELOG.md) for version history and recent changes.
