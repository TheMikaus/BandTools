# What is this tool for?
This tool is to help with listening, critiquing, and cataloging a band's band practices. It's to make the weekly task of listening through a practice easier to manage.

# What are the features of the tool? (several features need to be retested)
- Can play, stop, scrub through a wave or mp3 file.
- Can give the file a song name/meta name
- Can mark songs as "Best Take" from both the Library tab and Annotations tab
- Can mark songs as "Partial Take" to indicate incomplete but usable recordings
- Can bulk rename the folder based off of the song name/meta names provided
- Can leave a comment at a specific timestamp in the file (an annotation)
- Can mark that annotation as "important"
- **Annotation Categories**: Tag annotations with categories (⏱️ Timing, ⚡ Energy, 🎵 Harmony, 📊 Dynamics) for better organization and filtering. See [ANNOTATION_CATEGORIES.md](ANNOTATION_CATEGORIES.md) for complete guide.
- Per folder can see all important annotations in one spot, as well as an overall comment
- Can bulk convert wave -> mp3 if you have ffmpeg installed
- Can create a clip of a file. This is like an annotation that spans a timeframe.
- Can export the clip as a separate file
- Each user can have their own annotation file
- Multiple annotation files can live in a directory, and be visible in the application allowing each bandmate to make their own comments
- Can export the annotations to a text file 
- Has an undo chain
- **Recent Folders**: Quick access menu to recently opened practice folders for faster workflow. See [UI_IMPROVEMENTS.md](UI_IMPROVEMENTS.md) for details.
- **Preferences Dialog**: Centralized application settings (undo limit, theme, etc.) with simplified toolbar. See [UI_IMPROVEMENTS.md](UI_IMPROVEMENTS.md) for details.
- **Dark Mode Theme**: Choose between light and dark color themes for comfortable viewing in any lighting condition. Change theme in File → Preferences.
- **Export Best Takes Package**: Export all your Best Take files along with annotations to a single ZIP file for easy archiving or sharing (File → Export Best Takes Package…).
- **Color Consistency**: Ensures consistent visual appearance across different machines and display setups
- **Automatic Backup System**: Creates timestamped backups of metadata files before modifications
- **Backup Restoration**: Can restore any metadata file to a previous backed up version from within the software
- **Practice Statistics**: Analyzes your practice folders to show which songs you've practiced, frequency, and recording counts. View comprehensive analytics via Help menu or `Ctrl+Shift+S`. See [PRACTICE_STATISTICS.md](PRACTICE_STATISTICS.md) for complete guide.

# Expected Workflow
- Have band practice. Record each song as a separate audio file.
- Create a new dated folder in the practice files folder
- In the library tab click on the file name to start playing, put the name of the song in the provided name column. Do this for all songs.
- Click "Batch Rename" to convert the files to the proper names.
- Listen to each song, leaving annotations, and selecting clips of parts of the song that really stand out.
- Mark your favorite recordings as "Best Take" either from the Library tab or from the Annotations tab while listening.
- Mark incomplete but potentially useful recordings as "Partial Take" for later reference.
- **Practice Statistics**: Analyze your practice folders to see which songs you've practiced, how often, and when! Access via Help menu → "Practice Statistics" or `Ctrl+Shift+S`. See [PRACTICE_STATISTICS.md](PRACTICE_STATISTICS.md) for details.
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

**Note**: GitHub Actions builds do NOT create executables in the repository's `dist/` folder. Built executables are only available through GitHub Artifacts (temporary) or Releases (permanent). See [BUILD.md](BUILD.md) for details.

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

See [BUILD.md](BUILD.md) for detailed build instructions.

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
