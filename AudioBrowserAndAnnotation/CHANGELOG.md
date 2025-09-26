# AudioBrowser Changelog

This file tracks changes made to the AudioBrowser application. The version number format is `MAJOR.MINOR` where the minor version automatically increments with each commit.

## [Unreleased]

## [1.2] - Version System Implementation

### Added
- Application version number system with automatic minor version increment per commit
- Version display in application window title (e.g., "Audio Folder Player - 1.2")
- Help menu with "About" and "Changelog" buttons in toolbar
- About dialog showing version information and key features
- Changelog dialog for viewing this changelog file
- Version management module (`version.py`) with git-based version calculation
- Comprehensive version testing system
- This changelog file for tracking feature additions and changes

### Changed
- Updated Copilot instructions to include version management guidelines
- Application window title now includes version number
- Enhanced toolbar with help-related actions

### Technical Details
- Version automatically calculated from git commit count: `git rev-list --count HEAD`
- Version format: MAJOR.MINOR (e.g., 1.2 means major version 1, minor version 2)
- Fallback version handling if git is not available
- Version information includes commit hash for build identification

## [1.1] - Initial Version with Existing Features

### Existing Features
- Audio file browser with waveform visualization
- Multi-user annotation system with timestamped notes
- Best take and partial take marking system
- Batch renaming with provided names (##_ProvidedName format)
- Audio conversion (WAV to MP3, stereo to mono)
- Audio fingerprinting for automatic song identification
- Cross-folder fingerprint matching
- Clip creation and export functionality
- Sub-section labeling and playback
- Undo/redo system for annotations
- Backup and restore system for metadata
- Multi-set annotation support with color coding
- Folder notes and important annotation highlighting
- Threaded waveform generation and audio processing
- Auto-progression through playlist
- Volume control and audio output device selection
- Stereo/mono waveform display modes

### Technical Features
- PyQt6-based GUI with modern interface
- JSON-based data persistence
- Auto-installation of Python dependencies
- Robust error handling and graceful degradation
- File signature-based caching for performance
- Multi-threading for responsive UI during heavy operations

---

## Version Numbering Scheme

- **Major Version (1.x)**: Significant feature releases or architectural changes
- **Minor Version (x.N)**: Automatically incremented with each commit using `git rev-list --count HEAD`
- **Build Number**: Equivalent to minor version, represents total commit count
- **Commit Hash**: Short git commit hash for build identification (when available)

The version system ensures every commit results in a new version number for easy tracking and debugging.

### Version Display Locations
- Application window title
- Help > About dialog
- Version module when run directly (`python version.py`)
- This changelog file header