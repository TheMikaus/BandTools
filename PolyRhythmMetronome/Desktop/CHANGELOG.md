# PolyRhythmMetronome Changelog

This file tracks changes made to the PolyRhythmMetronome application.

## [Unreleased]

### Added
- **Verbose Logging Mode**: New debugging and analysis feature
  - "Verbose Log" checkbox to enable/disable real-time timing information
  - Scrollable log window displaying per-layer timing details
  - Shows delta between actual play times and expected intervals
  - Includes timestamp with millisecond precision
  - "Clear Log" button to reset accumulated entries
  - Useful for debugging timing issues and verifying tempo accuracy
  - See [docs/user_guides/verbose_logging.md](docs/user_guides/verbose_logging.md) for details
- **Random Dark Colors**: New layers now automatically get assigned random dark colors for better visual distinction
- **Auto Flash Colors**: Flash colors are automatically generated as brighter versions of layer inactive colors
- **MP3 Tick Support**: Added support for MP3 tick sounds from a `ticks` folder
  - MP3 files can be used as metronome sounds
  - Paired MP3 files (ending in _1 and _2) provide different sounds for accented vs regular beats
  - Ticks folder is automatically included in builds
- **Build Scripts**: Added PyInstaller spec file and build scripts (build.sh, build.bat) for easy executable creation

### Changed
- **Color System**: Layers now use separate colors for inactive and flash (active) states
- **Audio File Support**: Extended WaveCache to support both WAV and MP3 files using pydub
- **Tone Frequencies**: Changed tone mode to use fixed frequencies for clarity:
  - Accent notes now use 800Hz
  - Normal notes now use 400Hz
  - This replaces the user-configurable frequency setting for more consistent metronome behavior
- **MP3 Tick Accent Behavior**: MP3 tick accents now use volume changes instead of different sounds
  - Always uses the non-accent file version
  - Accent is indicated by volume increase (controlled by accent factor)

### Fixed
- **Subdivision Timing**: Fixed critical issue where subdivisions 4 and 8 did not click on time
  - Removed incorrect `notes_per_beat_from_input()` function that was dividing by 4
  - `interval_seconds()` now correctly interprets subdivision as "notes per beat"
  - Subdivision 4 now produces 4 notes per beat (not 1)
  - Subdivision 8 now produces 8 notes per beat (not 2)
  - All subdivision values now match the "notes per beat" behavior documented in README
- **Accent Note Timing**: Fixed issue where accent always played on the fourth note instead of beat 1
  - Changed from global measure-based accent to per-layer note counting
  - Each layer now tracks its own note count independently
  - Accent now always plays on the first note of each layer's measure cycle
  - Formula: accent occurs every (subdivision × beats_per_measure) notes
  - Example: subdivision 4 with 4 beats per measure = accent every 16 notes (notes 0, 16, 32, etc.)
  - This ensures the accent always lands on the "1" count of each layer, regardless of other layers
- **Wave/MP3 Timing Issues**: Fixed issue where wave and MP3 files would not play on time throughout playback
  - Added pre-loading of all audio files into cache before playback begins
  - Audio files are now pre-loaded when layers are added/modified during playback
  - Audio files are cached in memory before the audio thread starts
  - Eliminates disk I/O delays during audio callbacks that caused timing problems
  - Ensures consistent, on-time playback from the first note and throughout playback
- **Improved Exception Logging**: Enhanced error logging in metronome_log.txt for better debugging
  - Added timestamps to all log entries (format: YYYY-MM-DD HH:MM:SS.mmm)
  - Added context information including mute states for left and right layers
  - Added playback state (running, active sounds count)
  - Added clear visual separators between log entries for better readability
  - Logs now show how many layers are muted when errors occur during mute operations
  - Improved diagnostic information helps users and developers identify audio engine issues

## Previous Versions

This is the first version of the changelog. Previous changes were not formally tracked.
