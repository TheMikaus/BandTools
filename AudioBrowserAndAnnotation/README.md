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
- Per folder can see all important annotations in one spot, as well as an overall comment
- Can bulk convert wave -> mp3 if you have ffmpeg installed
- Can create a clip of a file. This is like an annotation that spans a timeframe.
- Can export the clip as a separate file
- Each user can have their own annotation file
- Multiple annotation files can live in a directory, and be visible in the application allowing each bandmate to make their own comments
- Can export the annotations to a text file 
- Has an undo chain
- **Automatic Backup System**: Creates timestamped backups of metadata files before modifications
- **Backup Restoration**: Can restore any metadata file to a previous backed up version from within the software

# Expected Workflow
- Have band practice. Record each song as a separate audio file.
- Create a new dated folder in the practice files folder
- In the library tab click on the file name to start playing, put the name of the song in the provided name column. Do this for all songs.
- Click "Batch Rename" to convert the files to the proper names.
- Listen to each song, leaving annotations, and selecting clips of parts of the song that really stand out.
- Mark your favorite recordings as "Best Take" either from the Library tab or from the Annotations tab while listening.
- Mark incomplete but potentially useful recordings as "Partial Take" for later reference.
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

# Cloud based storage
- Initial thoughts were to use Google drive's oAuth, but that seems to require me to register the app, and I dont' really want to do that, nor do I want to others to have to. So I cancelled that out for now.
- Maybe allow a user to specify an FTP server?
