# AudioBrowser - Band Practice Tool

## About This Project

This project contains two versions of the AudioBrowser application:

1. **[AudioBrowserOrig/](AudioBrowserOrig/)** - The original, stable PyQt6 widgets-based version (production-ready)
2. **[AudioBrowser-QML/](AudioBrowser-QML/)** - New QML-based version (70% complete, 95% production-ready)
3. **[shared/](shared/)** - Common modules shared between both applications to reduce code duplication

Both versions share the same goal: helping bands listen to, critique, and catalog their practice recordings.

### Shared Modules

Both AudioBrowser applications use shared modules for common functionality:

- **Metadata constants** - Common JSON file name constants
- **Backup utilities** - Metadata backup and restore functions
- **File utilities** - File operations (sanitize, signatures)
- **Audio workers** - Background audio processing

See [shared/README.md](shared/README.md) for complete documentation.

### QML Version Status (January 2025)

The QML version has made significant progress and is now **95% production-ready** for daily band practice use:

- ✅ **70% feature complete** (45 of 64 features)
- ✅ All core features implemented (playback, annotations, waveform, clips)
- ✅ All practice features complete (statistics, goals, setlists, best takes)
- ✅ Advanced features complete (fingerprinting, tempo/BPM, spectrogram)
- 🚧 Only critical missing feature: Batch operations (2 weeks away)

**Documentation:**
- **[QML_MIGRATION_SUMMARY.md](AudioBrowser-QML/docs/technical/QML_MIGRATION_SUMMARY.md)** - Quick answer: "How much work remains?" (4-6 weeks for 95%, 12-14 weeks for 100%)
- **[QML_FEATURE_PARITY_STATUS.md](AudioBrowser-QML/docs/technical/QML_FEATURE_PARITY_STATUS.md)** - Comprehensive status report with detailed breakdown
- **[FEATURE_COMPARISON_ORIG_VS_QML.md](AudioBrowser-QML/docs/technical/FEATURE_COMPARISON_ORIG_VS_QML.md)** - Side-by-side feature comparison
- **[QML_MIGRATION_ISSUES.md](AudioBrowser-QML/docs/technical/QML_MIGRATION_ISSUES.md)** - Detailed tracking of 19 issues (7 completed, 12 remaining)

**Recommendation:** Use QML version for daily practice (all core features work). Only missing batch file operations, which will be completed in Phase 7 (2 weeks).

## What is this tool for?
This tool is to help with listening, critiquing, and cataloging a band's band practices. It's to make the weekly task of listening through a practice easier to manage.

# What are the features of the tool? (several features need to be retested)
- Can play, stop, scrub through a wave or mp3 file.
- Can give the file a song name/meta name
- Can mark songs as "Best Take" from both the Library tab and Annotations tab
- Can mark songs as "Partial Take" to indicate incomplete but usable recordings
- Can bulk rename the folder based off of the song name/meta names provided
- Can leave a comment at a specific timestamp in the file (an annotation)
- Can mark that annotation as "important"
- **Annotation Categories**: Tag annotations with categories (⏱️ Timing, ⚡ Energy, 🎵 Harmony, 📊 Dynamics) for better organization and filtering. See [ANNOTATION_CATEGORIES.md](AudioBrowserOrig/docs/user_guides/ANNOTATION_CATEGORIES.md) for complete guide.
- Per folder can see all important annotations in one spot, as well as an overall comment
- Can bulk convert wave -> mp3 if you have ffmpeg installed
- Can create a clip of a file. This is like an annotation that spans a timeframe.
- Can export the clip as a separate file
- Each user can have their own annotation file
- Multiple annotation files can live in a directory, and be visible in the application allowing each bandmate to make their own comments
- Can export the annotations to a text file 
- Has an undo chain
- **Recent Folders**: Quick access menu to recently opened practice folders for faster workflow. See [UI_IMPROVEMENTS.md](AudioBrowserOrig/docs/user_guides/UI_IMPROVEMENTS.md) for details.
- **Preferences Dialog**: Centralized application settings (undo limit, theme, etc.) with simplified toolbar. See [UI_IMPROVEMENTS.md](AudioBrowserOrig/docs/user_guides/UI_IMPROVEMENTS.md) for details.
- **Workspace Layouts**: Save and restore custom window sizes and panel positions. Perfect for different workflows or screen sizes. Use View menu or `Ctrl+Shift+L` to save, `Ctrl+Shift+R` to restore. See [UI_IMPROVEMENTS.md](AudioBrowserOrig/docs/user_guides/UI_IMPROVEMENTS.md) for details.
- **Status Bar Progress Indicators**: Visual progress bars show real-time feedback during waveform and fingerprint generation. See operation progress, file count, and current filename without modal dialogs.
- **Now Playing Panel**: Persistent playback and annotation controls accessible from any tab. Always-visible panel shows current file, playback controls, time display, and quick annotation entry. Collapsible panel with state persisting across sessions. Reduces tab switching during review workflow.
- **Dark Mode Theme**: Choose between light and dark color themes for comfortable viewing in any lighting condition. Change theme in File → Preferences. See [HOWTO_NEW_FEATURES.md](AudioBrowserOrig/docs/user_guides/HOWTO_NEW_FEATURES.md) for detailed instructions.
- **Export Best Takes Package**: Export all your Best Take files along with annotations to a single ZIP file for easy archiving or sharing (File → Export Best Takes Package…). See [HOWTO_NEW_FEATURES.md](AudioBrowserOrig/docs/user_guides/HOWTO_NEW_FEATURES.md) for complete guide.
- **Color Consistency**: Ensures consistent visual appearance across different machines and display setups
- **Automatic Backup System**: Creates timestamped backups of metadata files before modifications
- **Backup Restoration**: Can restore any metadata file to a previous backed up version from within the software
- **Practice Statistics**: Analyzes your practice folders to show which songs you've practiced, frequency, and recording counts. View comprehensive analytics via Help menu or `Ctrl+Shift+S`. See [PRACTICE_STATISTICS.md](AudioBrowserOrig/docs/user_guides/PRACTICE_STATISTICS.md) for complete guide.
- **Practice Goals**: Set and track practice goals including weekly/monthly time goals, session count goals, and per-song practice goals. Visual progress indicators show how close you are to achieving your goals. Access via Help menu → "Practice Goals" or `Ctrl+Shift+G`. See [PRACTICE_GOALS_GUIDE.md](AudioBrowserOrig/docs/user_guides/PRACTICE_GOALS_GUIDE.md) for complete user guide.
- **Setlist Builder**: Create and manage performance setlists for live shows and performances. Build setlists from songs across multiple practice folders, reorder songs for performance sequence, add performance notes (key changes, tuning, gear), validate setlist readiness (check for Best Takes and missing files), calculate total duration, export to text format for printing/sharing, and activate Practice Mode for focused rehearsal. Access via Tools menu → "Setlist Builder" or `Ctrl+Shift+T`. See [SETLIST_BUILDER_GUIDE.md](AudioBrowserOrig/docs/user_guides/SETLIST_BUILDER_GUIDE.md) for user guide, [IMPLEMENTATION_SUMMARY_SETLIST_BUILDER.md](AudioBrowserOrig/docs/technical/IMPLEMENTATION_SUMMARY_SETLIST_BUILDER.md) for technical details, and [TEST_PLAN_SETLIST_BUILDER.md](AudioBrowserOrig/docs/test_plans/TEST_PLAN_SETLIST_BUILDER.md) for test documentation.
- **Tempo & Metronome Integration**: Set BPM (Beats Per Minute) for each song and view visual tempo markers on the waveform. The BPM column in the Library tab allows you to enter tempo for any recording. Measure boundaries are automatically displayed on the waveform (assuming 4/4 time) with measure numbers for easy navigation. Perfect for analyzing timing consistency, identifying tempo drift, and practicing with visual timing guides. Tempo data is stored persistently in `.tempo.json` per practice folder. See [TEST_PLAN_TEMPO_METRONOME.md](AudioBrowserOrig/docs/test_plans/TEST_PLAN_TEMPO_METRONOME.md) for test plan and [IMPLEMENTATION_SUMMARY_TEMPO_METRONOME.md](AudioBrowserOrig/docs/technical/IMPLEMENTATION_SUMMARY_TEMPO_METRONOME.md) for technical details.
- **Spectrogram View (Spectral Analysis)**: Visualize frequency content of your recordings over time! Toggle spectrogram view in Annotations tab to see a color-coded frequency analysis (60-8000 Hz musical range). Blue represents low magnitude, green medium, and yellow-red high magnitude. Perfect for identifying frequency issues, analyzing harmonic content, and understanding tonal characteristics. Spectrogram is computed once and cached for instant subsequent displays. Works with all annotation markers, loop markers, and tempo markers. Access via Annotations tab → "Spectrogram" checkbox in waveform controls.
- **Sync History**: View complete timeline of all Google Drive sync operations! Track uploads, downloads, and conflict resolutions with timestamp, file count, and user information. Shows last 50 operations in chronological order. Non-modal dialog lets you continue working while reviewing history. Access via File menu → "View Sync History…". History stored in `.sync_history.json` per practice folder.
- **Sync Rules Configuration**: Customize Google Drive sync behavior with selective sync rules! Configure max file size limits, enable "annotations only" mode (exclude audio files), toggle audio file syncing, and set auto-download preferences. All rules persist per practice folder in `.sync_rules.json`. Perfect for controlling bandwidth usage and syncing only what you need. Access via File menu → "Sync Rules Configuration…".
- **Conflict Resolution UI**: Resolve sync conflicts with clarity! When files are modified both locally and remotely, a conflict resolution dialog appears showing modification times for each conflicting file. Choose "Keep Local", "Keep Remote", or "Merge (if possible)" for each file. Batch resolution for multiple conflicts. Preview before applying. Integrated seamlessly with Google Drive sync workflow.
- **Pagination for Large Libraries**: Handle libraries with hundreds or thousands of files efficiently. Pagination automatically activates for libraries with 500+ files, loading files in configurable chunks (default: 200 per page). Previous/Next navigation with page information display. Dramatically improves load times: 1000 files load in < 1 second vs 7+ seconds before. Reduces memory usage by 50-70% for large libraries. All features work seamlessly across pages. See [PERFORMANCE_GUIDE.md](AudioBrowserOrig/docs/user_guides/PERFORMANCE_GUIDE.md) for usage guide.
- **Parallel Waveform Generation**: Multi-threaded processing speeds up waveform generation 2-4x on multi-core systems. Auto-detects CPU core count (uses cores - 1) or manually configure worker count in Preferences. Thread-safe implementation with proper progress tracking. 100 files generate in ~30 seconds vs 100+ seconds with sequential processing. Configure in File → Preferences → Performance Settings.
- **Performance Settings**: Fine-tune AudioBrowser for your hardware. Enable/disable pagination, configure chunk size (50-1000 files per page), and set parallel worker count (0=auto, 1-16 manual). All settings persist across restarts. Access via File → Preferences. See [PERFORMANCE_GUIDE.md](AudioBrowserOrig/docs/user_guides/PERFORMANCE_GUIDE.md) for optimization tips.

# Expected Workflow
- Have band practice. Record each song as a separate audio file.
- Create a new dated folder in the practice files folder
- In the library tab click on the file name to start playing, put the name of the song in the provided name column. Do this for all songs.
- Click "Batch Rename" to convert the files to the proper names.
- Listen to each song, leaving annotations, and selecting clips of parts of the song that really stand out.
- Mark your favorite recordings as "Best Take" either from the Library tab or from the Annotations tab while listening.
- Mark incomplete but potentially useful recordings as "Partial Take" for later reference.
- **Practice Statistics**: Analyze your practice folders to see which songs you've practiced, how often, and when! Access via Help menu → "Practice Statistics" or `Ctrl+Shift+S`. See [PRACTICE_STATISTICS.md](PRACTICE_STATISTICS.md) for details.
- **Practice Goals**: Set and track practice goals to stay motivated! Create weekly/monthly time goals, session count goals, or per-song practice goals. Visual progress bars show your progress and days remaining. Access via Help menu → "Practice Goals" or `Ctrl+Shift+G`.
- **Setlist Builder**: Prepare for performances by creating organized setlists! Add songs from any practice folder, reorder for performance sequence, add performance notes, validate readiness, and export for printing. Activate Practice Mode to focus on setlist songs. Access via Tools menu → "Setlist Builder" or `Ctrl+Shift+T`.
- **Note**: The application automatically creates backups of your metadata before making changes. If you need to restore previous annotations or song names, use "Restore from Backup..." from the toolbar.

# Backup System
The application includes an automatic backup system that protects your metadata:

## Automatic Backups
- **When**: Backups are created automatically before the first modification in each session
- **What**: All metadata files including annotations, song names, duration cache, waveform cache, and fingerprints
- **Where**: Stored in `.backup/YYYY-MM-DD-###/` folders within each practice folder where modifications occur
- **Structure**: Each practice folder maintains its own local backup history

## Restore from Backup
- **Access**: Click "Restore from Backup..." in the toolbar
- **Selection**: Choose from available backups with human-readable dates
- **Flexibility**: Restore to current folder or any other practice folder that had backups
- **Preview**: See what files will be restored before confirming
- **Safety**: Requires confirmation before overwriting existing files
- **Updates**: UI automatically refreshes to show restored data

# Practice Statistics

Analyze your practice folders to gain insights into your practice history! The application scans your recordings and generates:

- **Practice frequency**: Number of sessions, date ranges, and consistency metrics
- **Song analysis**: Which songs you've practiced, how many takes, and best take counts
- **Progress tracking**: Most/least practiced songs, last practiced dates, and recording counts

**Access**: Help menu → "Practice Statistics" or press `Ctrl+Shift+S`

**How it works**: Analyzes practice folders on-demand by scanning audio files, provided names, and annotations

**Complete Guide**: See [PRACTICE_STATISTICS.md](PRACTICE_STATISTICS.md) for detailed documentation on:
- What gets analyzed and how it works
- How to interpret the statistics dashboard
- Practical use cases and tips
- Folder naming conventions for accurate dates

# Documentation

Comprehensive documentation is available both within the application and in the `docs/` folder:

## Built-in Documentation Browser

Access all documentation directly from the application:
- **Help → Documentation Browser** or press `Ctrl+Shift+H`
- Search and browse user guides, technical docs, and test plans
- Organized by category for easy navigation

## Documentation Structure

- **`docs/user_guides/`** - User manuals, feature guides, and visual references
- **`docs/technical/`** - Implementation details, architecture, and build instructions  
- **`docs/test_plans/`** - Comprehensive test plans for quality assurance
- **`docs/INDEX.md`** - Complete documentation index with descriptions

## Key Documentation Files

- **User Guides**: HOWTO_NEW_FEATURES.md, PRACTICE_GOALS_GUIDE.md, SETLIST_BUILDER_GUIDE.md, UI_IMPROVEMENTS.md
- **Visual Guides**: UI_SCREENSHOTS.md, VISUAL_GUIDE_* files with ASCII diagrams
- **Technical**: 
  - INTERFACE_IMPROVEMENT_IDEAS.md (feature roadmap)
  - **QML_MIGRATION_STRATEGY.md** (Qt Quick/QML modernization plan) 🆕
  - **CURRENT_ARCHITECTURE_INVENTORY.md** (architecture analysis) 🆕
  - **SIMPLIFICATION_EXAMPLES.md** (code simplification patterns) 🆕
  - **IMMEDIATE_SIMPLIFICATION_GUIDE.md** (step-by-step implementation guide) 🆕
  - BUILD.md (build instructions)
- **Test Plans**: TEST_PLAN_* files with comprehensive test cases

# Note
- Basically this whole application is ChatGPT or CoPilot generated. The idea was just to have it generate a tool so I can have my workflows go faster.
- Once I've finished feature creep on the application I plan on trying to refactor it into to more than one file.
- Maybe have CoPilot add unit test like things

# Downloads and Installation

## Pre-built Releases

Pre-built executables are automatically created for Windows, Linux, and macOS on every commit to the main branch.

**Download from Releases**: Go to the [Releases page](https://github.com/TheMikaus/BandTools/releases) and download the appropriate file for your operating system:

- **Windows**: `AudioFolderPlayer-{version}-windows.zip`
- **Linux**: `AudioFolderPlayer-{version}-linux.tar.gz` 
- **macOS**: `AudioFolderPlayer-{version}-macos.tar.gz`

**Installation**: Extract the downloaded archive and run the `AudioFolderPlayer` executable.

**Note**: GitHub Actions builds do NOT create executables in the repository's `dist/` folder. Built executables are only available through GitHub Artifacts (temporary) or Releases (permanent). See [BUILD.md](docs/technical/BUILD.md) for details.

## Building from Source

If you prefer to build from source or need to modify the application:

### Windows
```batch
cd AudioBrowserAndAnnotation
build_exe.bat
```

### Linux/macOS
```bash
cd AudioBrowserAndAnnotation
chmod +x build_exe.sh
./build_exe.sh
```

See [BUILD.md](docs/technical/BUILD.md) for detailed build instructions.

## Automatic Updates

The application uses an automatic version numbering system where the version increments with each commit. Check the [Releases page](https://github.com/TheMikaus/BandTools/releases) for the latest version.

# Cloud Synchronization

AudioBrowser now supports Google Drive synchronization for sharing practice sessions with your band members!

## Google Drive Sync Features

- **Manual Sync**: Click "☁ Sync" button in toolbar or File menu
- **Version-Based Tracking**: Intelligent version tracking prevents conflicts
- **Selective Sync**: Choose exactly which files to upload/download
- **Automatic Annotation Sync**: Metadata files sync automatically (with your approval)
- **Multi-User Support**: Each band member maintains their own annotations
- **Safe Operations**: All changes require your confirmation before applying

## Getting Started with Sync

1. **Set up Google Drive API access** (one-time setup)
   - See [GOOGLE_DRIVE_SETUP.md](GOOGLE_DRIVE_SETUP.md) for detailed instructions
   - Create OAuth credentials in Google Cloud Console
   - Download `credentials.json` to AudioBrowserAndAnnotation directory

2. **First Sync**
   - Click "☁ Sync" button
   - Authorize the app (opens browser)
   - Select/create a Google Drive folder for your band
   - Review and approve file changes

3. **Regular Use**
   - Click "☁ Sync" to check for updates
   - Download: Get new recordings and annotations from band members
   - Upload: Share your recordings and annotations with the band

## What Gets Synced

**Automatically Selected:**
- Annotation files (`.audio_notes_*.json`)
- Song names (`.provided_names.json`)
- Duration cache (`.duration_cache.json`)
- Audio fingerprints (`.audio_fingerprints.json`)
- User colors (`.user_colors.json`)

**You Choose:**
- Audio files (`.wav`, `.mp3`) - Select which recordings to share

**Never Synced:**
- Backup folders (`.backup/`)
- Waveform cache (`.waveforms/`)

## Privacy and Security

- Your band member's annotations are read-only - you can't modify them
- You can only upload your own annotation files
- All operations are logged for transparency
- Your Google credentials are stored locally and never shared

For complete setup instructions, see [GOOGLE_DRIVE_SETUP.md](GOOGLE_DRIVE_SETUP.md).

---

# Testing Documentation

Comprehensive test documentation is available for both AudioBrowser applications to ensure quality and help with bug reporting.

## Test Plan Overview

**Total Test Coverage: 345 Test Cases**

- **AudioBrowserOrig**: 319 test cases across 10 major features
- **AudioBrowser-QML**: 26 test cases for spectrogram feature

### Quick Access

- **[TEST_PLAN_SUMMARY.md](AudioBrowser-QML/docs/test_plans/TEST_PLAN_SUMMARY.md)** - Quick reference guide with feature overview and testing priorities
- **[COLLATED_TEST_PLAN.md](AudioBrowser-QML/docs/test_plans/COLLATED_TEST_PLAN.md)** - Complete comprehensive test plan with all 345 test cases

### Individual Test Plans

#### AudioBrowserOrig Test Plans
1. [Clickable Status Bar Items](AudioBrowserOrig/docs/test_plans/TEST_PLAN_CLICKABLE_STATUS.md) (23 tests)
2. [Now Playing Panel](AudioBrowserOrig/docs/test_plans/TEST_PLAN_NOW_PLAYING_PANEL.md) (29 tests)
3. [Performance Improvements](AudioBrowserOrig/docs/test_plans/TEST_PLAN_PERFORMANCE_IMPROVEMENTS.md) (41 tests) - **Critical**
4. [Practice Goals](AudioBrowserOrig/docs/test_plans/TEST_PLAN_PRACTICE_GOALS.md) (40 tests)
5. [Setlist Builder](AudioBrowserOrig/docs/test_plans/TEST_PLAN_SETLIST_BUILDER.md) (43 tests)
6. [Spectral Analysis](AudioBrowserOrig/docs/test_plans/TEST_PLAN_SPECTRAL_ANALYSIS.md) (35 tests)
7. [Stereo Waveform View](AudioBrowserOrig/docs/test_plans/TEST_PLAN_STEREO_WAVEFORM.md) (15 tests)
8. [Sync Improvements](AudioBrowserOrig/docs/test_plans/TEST_PLAN_SYNC_IMPROVEMENTS.md) (38 tests)
9. [Tempo & Metronome](AudioBrowserOrig/docs/test_plans/TEST_PLAN_TEMPO_METRONOME.md) (31 tests)
10. [Workspace Layouts & Progress](AudioBrowserOrig/docs/test_plans/TEST_PLAN_WORKSPACE_PROGRESS.md) (24 tests)

#### AudioBrowser-QML Test Plans
11. [Spectrogram Overlay](AudioBrowser-QML/docs/test_plans/TEST_PLAN_SPECTROGRAM.md) (26 tests)

### Testing Time Estimates

| Testing Level | Duration | Description |
|--------------|----------|-------------|
| **Smoke Test** | 1 hour | Basic functionality verification |
| **Essential Test** | 4 hours | Core features and workflows |
| **Comprehensive Test** | 16-24 hours | Complete test suite (all 345 cases) |

### Bug Reporting

Found a bug during testing? Use the bug reporting template in [COLLATED_TEST_PLAN.md](AudioBrowser-QML/docs/test_plans/COLLATED_TEST_PLAN.md#bug-reporting-template) to document issues with:
- Steps to reproduce
- Expected vs actual results
- Severity rating
- Environment details
- Screenshots/logs

---
