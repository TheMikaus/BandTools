# Batch Operations User Guide

## Overview

The Batch Operations feature in AudioBrowser-QML allows you to perform bulk operations on multiple audio files at once. This is particularly useful for organizing large collections of practice recordings or converting between audio formats.

## Available Operations

### 1. Batch Rename

Rename multiple audio files with a consistent naming pattern.

**Features:**
- Sequential numbering (01_, 02_, 03_, etc.)
- Pattern-based naming
- Preview before committing
- Preserves file extensions
- Sorts by creation time (oldest first)

**How to Use:**

1. Navigate to a folder with audio files
2. Click the **"Batch Rename"** button in the toolbar
3. (Optional) Enter a name pattern:
   - Leave empty to use current filenames
   - Enter a pattern like "song_name" to apply to all files
4. Review the preview showing old → new names
5. Click **OK** to execute the rename

**Example:**

Files before:
```
recording1.wav
practice_session.mp3
take_3.wav
```

With pattern "rehearsal":
```
01_rehearsal.wav
02_rehearsal.mp3
03_rehearsal.wav
```

Without pattern (using existing names):
```
01_recording1.wav
02_practice_session.mp3
03_take_3.wav
```

### 2. Convert WAV to MP3

Convert multiple WAV files to MP3 format for smaller file sizes.

**Features:**
- Batch conversion of all WAV files in folder
- Selectable bitrate (128k, 192k, 256k, 320k)
- Option to delete original WAV files
- Progress tracking
- Error handling per file

**How to Use:**

1. Navigate to a folder with WAV files
2. Click the **"Convert WAV→MP3"** button in the toolbar
3. Select MP3 bitrate (default: 192k)
4. Check/uncheck "Delete original WAV files after conversion"
5. Click **OK** to start conversion
6. Monitor progress in the progress dialog

**Requirements:**
- pydub Python library: `pip install pydub`
- FFmpeg installed and in PATH

**Warning:** If "Delete original WAV files" is checked, the original files will be permanently deleted after successful conversion. Only converted files will remain.

### 3. Convert Stereo to Mono

Convert a stereo audio file to mono, creating a backup of the original.

**Features:**
- Channel selection (left, right, or both)
- Automatic backup to .backup folder
- Preserves original filename for mono version
- Works with WAV and MP3 files

**How to Use:**

1. Select an audio file in the library
2. Right-click and choose "Convert to Mono" (or use toolbar)
3. Select which channels to include:
   - Both channels: Creates balanced mono mix
   - Left only: Uses left channel only
   - Right only: Uses right channel only
4. Click **OK** to convert
5. Original stereo file is backed up with "_stereo" suffix

**Example:**
```
Before: song.wav (stereo)
After:  song.wav (mono)
        .backup/song_stereo.wav (stereo backup)
```

### 4. Volume Boost Export

Export an audio file with increased volume.

**Features:**
- Adjustable boost from 0 to 10 dB
- Creates new file with "_boosted" suffix
- Preserves original file
- Real-time slider control

**How to Use:**

1. Select an audio file in the library
2. Open the batch operations menu
3. Choose "Export with Volume Boost"
4. Adjust the boost slider (0-10 dB)
5. Click **OK** to export
6. New file is created: `filename_boosted.wav`

**Note:** Be careful with high boost values as they may cause clipping (distortion). Start with 3 dB and increase gradually.

## Progress Tracking

All batch operations show a progress dialog with:
- Current operation name
- Files processed / Total files
- Current file being processed
- Progress bar with percentage
- Cancel button (where applicable)

## Error Handling

If errors occur during batch operations:
- Successfully completed operations are preserved
- Failed operations are reported with error messages
- You can review the results summary after completion
- File list is automatically refreshed

## Tips and Best Practices

### Batch Rename
- Always review the preview before confirming
- Use lowercase, underscores instead of spaces for better compatibility
- Keep patterns short and descriptive
- Files are numbered by creation time, not alphabetically

### Format Conversion
- Test with a few files first before converting entire folders
- 192k bitrate is a good balance of quality and size for most uses
- Always keep backups of important recordings
- Conversion speed depends on file size and quantity

### Mono Conversion
- Listen to both channels separately first to decide which to keep
- Useful for separating instrument tracks recorded in stereo
- Check `.backup` folder for original stereo versions

### Volume Boost
- Use when recordings are consistently too quiet
- Better to record at proper levels than boost later
- Test with different values to find optimal boost
- Check for distortion after boosting

## Keyboard Shortcuts

Currently, batch operations are accessed via toolbar buttons. Keyboard shortcuts may be added in future versions.

## Troubleshooting

### "pydub library not available"
**Solution:** Install pydub with `pip install pydub`

### "FFmpeg not found"
**Solution:** 
- **Windows:** Download from ffmpeg.org and add to PATH
- **macOS:** `brew install ffmpeg`
- **Linux:** `sudo apt install ffmpeg` or similar

### Conversion fails with "Permission denied"
**Solution:** 
- Close any applications using the files
- Check file permissions
- Ensure sufficient disk space

### Rename preview shows unexpected results
**Solution:**
- Check that files have correct creation timestamps
- Files are sorted by creation time, not name
- Use pattern field to override filenames

### Progress dialog stuck
**Solution:**
- Click Cancel to stop the operation
- Check system resources (CPU, memory)
- Restart application if needed

## Dependencies

Batch operations require:
- **PyQt6**: Core functionality (included with application)
- **pydub**: Audio format conversion (optional)
- **FFmpeg**: Audio encoding/decoding (required for conversion)

Install optional dependencies:
```bash
pip install pydub
# Then install FFmpeg for your platform
```

## Future Enhancements

Planned features for batch operations:
- Multi-file selection in UI
- Batch annotation copying
- Export best takes to separate folder
- Custom naming patterns with variables
- Undo/rollback functionality
- Batch metadata editing

## See Also

- [Quick Start Guide](QUICK_START.md)
- [Annotation Guide](ANNOTATION_GUIDE.md)
- [Keyboard Shortcuts](KEYBOARD_SHORTCUTS.md)
