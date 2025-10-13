# PolyRhythmMetronome Changelog

This file tracks changes made to the PolyRhythmMetronome application.

## [Unreleased]

### Added
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

### Fixed
- **Wave/MP3 Timing Issues**: Fixed issue where wave and MP3 files would not play on time when starting from a freshly opened app
  - Added pre-loading of all audio files into cache before playback begins
  - Audio files are now cached in memory before the audio thread starts
  - Eliminates disk I/O delays during audio callbacks that caused timing problems
  - Ensures consistent, on-time playback from the first note
- **Improved Exception Logging**: Enhanced error logging in metronome_log.txt for better debugging
  - Added timestamps to all log entries (format: YYYY-MM-DD HH:MM:SS.mmm)
  - Added context information including mute states for left and right layers
  - Added playback state (running, active sounds count)
  - Added clear visual separators between log entries for better readability
  - Logs now show how many layers are muted when errors occur during mute operations
  - Improved diagnostic information helps users and developers identify audio engine issues

## Previous Versions

This is the first version of the changelog. Previous changes were not formally tracked.
