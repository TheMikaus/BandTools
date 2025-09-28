# AudioBrowser Changelog

This file tracks changes made to the AudioBrowser application. The version number format is `MAJOR.MINOR` where the minor version automatically increments with each commit.

## [Unreleased]

### Added
- **Console Output Logging System**: All console output is now redirected to a log file for better debugging and user support
  - New log file `audiobrowser.log` created in the application directory
  - Log file is recreated on each application startup (not appended to)
  - All print statements replaced with proper logging calls using timestamps
  - Maintains all existing console output functionality (startup messages, auto-generation feedback, error reporting)
  - Provides better debugging capabilities for users and developers
  - No console output during normal operation - all output goes to log file
- **Enhanced Autogeneration Feedback System**: Users now have full visibility into autogeneration behavior
  - Console output shows loaded settings at startup (waveforms, fingerprints, timing)
  - Clear boot-time decision making with detailed reasoning for why autogeneration did/didn't run
  - Informative skip messages when no audio files found or settings disabled
  - Progress logging during waveform and fingerprint generation with file-by-file updates
  - Status bar messages for all scenarios including skips, progress, and completion
  - Settings change notifications when autogeneration preferences are updated
  - Completion and cancellation confirmations for better user awareness
- **Color Consistency System**: Ensures consistent visual appearance across different machines
  - New ColorManager class for standardized color management across all UI elements
  - Purpose-based color standardization (selection, waveform, text, UI accent colors)
  - HSV-based color manipulation with gamma correction for display consistency
  - Enhanced Qt style selection with fallback support for cross-platform compatibility
  - Application palette override to ensure consistent highlight colors
  - Comprehensive documentation in COLOR_CONSISTENCY.md
- **Channel Muting Controls for Audio Playback**: Allow users to mute left or right channels independently
  - New checkbox controls in waveform section: "Left" and "Right" channel checkboxes
  - Acts like volume controls - unchecking mutes that channel (sets to silence, not duplication)
  - Smart enable/disable based on audio file channel count (only enabled for stereo files)
  - Seamless playback continuation when toggling channel muting during playback
  - Automatic cleanup of temporary channel-muted audio files on app close and startup
  - Now playing indicator shows current muting state (e.g., "Playing: song.mp3 (Left Muted)")
  - Uses proper channel silencing via pydub rather than channel duplication
  - Windows-only build pipeline for AudioBrowser executable
  - Triggers on changes to AudioBrowserAndAnnotation directory
  - Automatic version increment using existing git-based system
  - Build artifacts stored for 30 days, releases created on main branch
  - Uses existing build infrastructure (PyInstaller, version.py, audio_browser.spec)

### Fixed
- **Major Performance Optimization for Song Selection**: Eliminated multi-second delays when selecting songs
  - Fixed WaveformWorker to avoid unnecessary full audio decoding for stereo detection
  - Optimized waveform caching to use lightweight channel count detection (0.06ms vs full decode)
  - Improved cache logic to accept entries without stereo metadata for backward compatibility
  - Enhanced stereo/mono mode switching to avoid regeneration when both are cached
  - Performance improvement: 11,688x faster (selecting 11 songs: ~32s → ~0.003s)
  - Resolves issue where "loop across 11 elements should not take seconds"
- **Additional Performance Optimizations for Song Selection**: Further reduced selection delays
  - Added channel count caching to avoid repeated file I/O operations during selection
  - Optimized channel muting logic with early exit when both channels enabled (default state)
  - Deferred expensive UI state updates (mono button, channel muting) for unchanged file selections
  - Eliminated unnecessary function calls when both channels are enabled by checking state first
  - Cache automatically cleared when changing directories to prevent stale data
  - All `get_audio_channel_count()` calls now use cached version for consistency

### Changed
- **UI Redesign**: Converted toolbar to standard dropdown menus for cleaner interface
  - Added proper menu bar with File and Help menus
  - File menu contains: Change Folder, Up, Batch Rename, Export Annotations, Convert Audio, Restore Backup
  - Help menu contains: About, Changelog
  - Simplified toolbar now only shows: Undo/Redo, Undo limit controls, Auto-switch checkbox
  - All existing functionality preserved with keyboard shortcuts maintained
- **Waveform Stereo Detection Robustness**: Enhanced cache compatibility and stereo detection
  - Cache entries without stereo metadata now trigger lightweight detection instead of full regeneration
  - Improved backward compatibility with older cache files
  - Backward compatible: Existing new-format cache entries continue to work
- **GitHub Actions CI/CD Pipeline**: Fixed multiple compatibility and reliability issues
  - Updated Ubuntu 24.04 system dependencies for Qt library compatibility
  - Replaced deprecated GitHub Actions with modern alternatives
  - Fixed Windows archive creation using Python zipfile instead of 7z dependency
  - Enhanced Linux build dependencies to resolve PyInstaller library warnings
  - Updated action versions for better security and stability
- **GitHub Actions CI/CD Pipeline**: Automated building and releasing system
  - Multi-platform builds (Windows, Linux, macOS) on every commit
  - Automatic release creation with downloadable executables
  - Build artifacts stored for 30 days, releases permanent
  - Integration with existing git-based version system
- **Documentation**: CI/CD setup documentation and updated README/BUILD guides
- **Release Distribution**: Pre-built executables available from GitHub Releases page

### Technical Details
- GitHub Actions workflow triggers on push to main/develop branches
- Cross-platform builds using PyInstaller in containerized environments
- Automated archive creation (.zip for Windows, .tar.gz for Linux/macOS)
- Release tagging format: `audiobrowser-v{version}`
- Manual workflow dispatch option for on-demand releases
- Modern release management using `softprops/action-gh-release@v1`

## [1.3] - Version System Implementation

### Added
- Application version number system with automatic minor version increment per commit
- Version display in application window title (e.g., "Audio Folder Player - 1.3")
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
- Version format: MAJOR.MINOR (e.g., 1.3 means major version 1, minor version 3)
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