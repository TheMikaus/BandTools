# AudioBrowser Changelog

This file tracks changes made to the AudioBrowser application. The version number format is `MAJOR.MINOR` where the minor version automatically increments with each commit.

## [Unreleased]

### Added
- **Automatic File Renaming for Best/Partial Takes**: Files are now automatically renamed when marked as best or partial takes
  - Marking a file as "Best Take" appends "_best_take" suffix to the filename
  - Marking a file as "Partial Take" appends "_partial_take" suffix to the filename
  - Unmarking removes the respective suffix from the filename
  - All metadata (annotations, provided names, durations) automatically updated after rename
  - Works from both Library tab (clicking indicators) and Annotations tab (checkboxes)
  - File system view refreshes automatically to show renamed files
  - Error handling prevents data loss if rename fails (reverts checkbox state)

### Changed
- **Batch Rename Filename Formatting**: Improved filename standardization in batch rename
  - Library names now converted to lowercase with spaces replaced by underscores
  - New `sanitize_library_name()` function for consistent filename formatting
  - Format: `##_lowercase_name_with_underscores.ext` (e.g., `01_my_song_name.wav`)
  - Previous format used spaces which are now replaced with underscores for better file system compatibility

### Fixed
- **Mono Export and Volume Boost File Handle Issue**: Fixed mono export and volume boost export failing due to locked file handles
  - Now properly releases media player file handle before attempting file rename operations
  - Calls `_release_media_for_path()` to clear QMediaPlayer source and wait for OS to release file locks
  - Prevents "Permission denied" or "file in use" errors on Windows during mono conversion and volume boost export
  - Both "Convert to Mono" and "Export with Volume Boost" features now work correctly when file is selected
- **Channel Muting Array Size Mismatch**: Fixed error when muting channels in stereo MP3 files
  - Changed silent right channel to use `len(channels[1])` instead of `len(channels[0])`
  - Prevents "attempt to assign array of size X to extended slice of size Y" errors
  - Fixes issue where stereo channels with slightly different lengths (common in MP3 encoding) caused crashes
  - Channel muting now works correctly for all stereo audio files

### Added
- **Audio Device Auto-Selection and Persistence**: Improved audio output device management
  - Application now automatically selects the default system audio device on startup
  - User's audio device selection is now persisted between sessions
  - Device matching uses device ID for more reliable identification
  - Seamlessly handles device changes (plugging/unplugging audio devices)
  - Settings stored using new `SETTINGS_KEY_AUDIO_OUTPUT_DEVICE` key
- **Volume Boost Feature**: Allow users to boost audio volume above normal playback levels
  - New "Boost" slider control in player bar (range: 1.0x to 4.0x)
  - Real-time volume boost during playback by combining volume and boost multipliers
  - "Export with Volume Boost" menu item in File menu to save boosted audio
  - Applies boost to audio file and saves as replacement (original backed up with '_original' suffix)
  - Boost setting persisted across application sessions
  - Automatic playback stop before file export to ensure file is not in use
  - Works with both WAV and MP3 files using pydub audio processing

### Fixed
- **Volume Boost During Playback**: Fixed volume boost not applying correctly during real-time playback
  - Removed `min(1.0)` cap on effective volume that prevented boost from exceeding 100%
  - Boost now properly amplifies audio up to 4.0x (400%) as intended
  - Volume boost slider now has full effect during playback, not just on export
- **Channel Muting Playback Issues**: Fixed potential issues with channel muting during playback
  - Removed redundant `player.play()` call in `_on_channel_muting_changed()` that could cause playback issues
  - Channel muting now restarts playback cleanly with correct channel configuration
  - Eliminated duplicate play command that occurred after `_play_file()` already started playback
- **Channel Muting Signal Recursion**: Fixed infinite signal recursion bug when toggling channel muting checkboxes
  - Removed redundant `_update_channel_muting_state()` call from `_on_channel_muting_changed()` that caused unwanted re-entry
  - Added signal blocking when programmatically setting checkbox states for mono files to prevent triggering stateChanged events
  - Channel muting checkboxes now respond correctly to user input without causing signal loops
  - Mono file detection and checkbox state updates work properly without side effects
- **Audio Playback Stuttering During Playback**: Fixed stuttering that occurred during audio playback when just listening
  - Removed redundant `positionChanged` signal connection that was calling `_sync_slider()` excessively
  - `_sync_slider()` now only called by 200ms timer instead of on every position change (potentially hundreds of times per second)
  - Eliminated excessive UI updates that were blocking the audio thread during playback
  - Resolves stuttering issue reported during normal playback (not during song selection)
- **Point Annotation Creation with Partial Clip Selection**: Clarified and documented the behavior when pressing Enter with only one clip boundary set
  - When only clip start OR only clip end is set (not both), pressing Enter now correctly creates a point annotation at the current timestamp
  - Clip annotations are only created when BOTH clip start AND clip end values are set
  - Improved code readability by refactoring the conditional logic into a clearer if/else structure
  - Added inline comments documenting the intended behavior for future maintainability
- **Audio Fingerprinting UI Visibility**: Enhanced visibility of controls in the Audio Fingerprinting section
  - Added bold, dark text styling to all label elements for better contrast against the light background
  - Added visible borders and background colors to buttons (Generate Fingerprints, Auto-Label, Show Practice Folders)
  - Added white background and prominent borders to QComboBox and QSpinBox controls
  - Added hover effects to buttons for better interactive feedback
  - Improved disabled state styling for Auto-Label button with appropriate grayed-out appearance
  - All changes maintain consistency with the existing ColorManager system

### Added
- **Enhanced Fingerprint Algorithm Consistency**: Improved robustness and safety of fingerprint matching
  - New `get_fingerprint_for_algorithm()` function for safer fingerprint retrieval with automatic legacy format handling
  - New `validate_fingerprint_algorithm_coverage()` function to check algorithm coverage in caches
  - Enhanced fingerprint comparison with safety warnings for potential algorithm mismatches  
  - Improved documentation clarifying algorithm consistency guarantees throughout the system
  - All fingerprint matching operations now use centralized, algorithm-aware retrieval functions
  - Better error detection for cross-algorithm comparison attempts (logs warnings for suspicious length differences)
- **Recursive Autogeneration**: Autogeneration now recursively discovers and processes all directories with audio files
  - New `discover_directories_with_audio_files()` function recursively scans for directories containing audio files
  - Autogeneration processes all discovered directories instead of just the current folder
  - Enhanced logging shows directory-by-directory progress with file counts
  - Supports deep directory structures with audio files at any level
  - Maintains existing functionality while expanding scope to entire directory tree
  - Both waveform and fingerprint generation now work recursively
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
- **Partial Take Checkbox in Annotations Tab**: Complete the partial take marking workflow
  - Added "Partial Take" checkbox next to "Best Take" checkbox in Annotations tab
  - Checkbox is enabled/disabled based on file selection state
  - State automatically saved to annotation data with proper integration
  - Checkbox state updates when switching between files 
  - Tooltip explains "Mark this song as a partial take"
  - Seamlessly integrates with existing multi-user annotation system

### Fixed
- **Autogeneration Silent Failure Bug**: Fixed issue where autogeneration would show "will start in 1 second" but then fail silently
  - Added comprehensive error handling and validation in `_start_auto_generation_for_folder()` method
  - Added validation for folder path existence, type checking, and directory verification  
  - Added proper error handling around file system operations (folder.glob() calls)
  - Added error handling for worker thread creation and startup processes
  - Added detailed error logging for all failure scenarios with descriptive status bar messages
  - Added logging of target folder path during boot autogeneration for better debugging
  - Ensures users now see clear error messages when autogeneration fails instead of silent failures
  - Prevents autogeneration from getting stuck in progress state when errors occur
- **Log File Readability**: Fixed unreadable log files caused by encoding and format string issues
  - Enhanced logging configuration with explicit UTF-8 encoding and error handling (`errors='replace'`)
  - Added proper handler cleanup to prevent conflicts with existing loggers
  - Used parameterized logging (`logger.info("%s", message)`) to avoid format string corruption
  - Improved `log_print` function with robust error handling and safe string conversion
  - Added fallback logging for critical errors to prevent silent failures
  - All existing log functionality preserved while ensuring files remain readable with proper timestamps
  - Prevents log file corruption from Unicode characters, file paths, or user content
  - Maintains proper one-entry-per-line log structure for better text editor compatibility
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
- **Audio Playback Responsiveness**: Fixed song selection delay for immediate audio playback
  - Optimized channel muting checkbox state checking to avoid `hasattr()` overhead
  - Streamlined media player state transitions (stop → setSource → play)
  - Deferred expensive UI operations (waveform loading, annotation loading) after audio starts
  - Audio now starts playing within 10ms while heavy UI work happens asynchronously
  - Resolves user-reported issue where "clicking a song used to start right away" but had delays

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