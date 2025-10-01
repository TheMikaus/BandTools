# PolyRhythmMetronome Changelog

This file tracks changes made to the PolyRhythmMetronome application.

## [Unreleased]

### Fixed
- **Improved Exception Logging**: Enhanced error logging in metronome_log.txt for better debugging
  - Added timestamps to all log entries (format: YYYY-MM-DD HH:MM:SS.mmm)
  - Added context information including mute states for left and right layers
  - Added playback state (running, active sounds count)
  - Added clear visual separators between log entries for better readability
  - Logs now show how many layers are muted when errors occur during mute operations
  - Improved diagnostic information helps users and developers identify audio engine issues

## Previous Versions

This is the first version of the changelog. Previous changes were not formally tracked.
