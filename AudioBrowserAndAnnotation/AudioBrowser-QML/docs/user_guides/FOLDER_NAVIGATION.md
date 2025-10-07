# Folder Navigation Guide

## Overview

The AudioBrowser QML application now supports hierarchical folder navigation, allowing you to browse a root directory and all its subfolders containing audio files.

## Features

### Folder Tree View

- **Root Folder**: When you select a directory, it becomes your root folder
- **Subfolders**: All subfolders containing audio files are automatically discovered and shown in the folder tree
- **Folder Icons**:
  - 📁 Root folder
  - 📂 Subfolders with audio files
- **File Count**: Each folder shows the number of audio files it contains in parentheses

### Split View Layout

The Library tab now uses a split view layout:

- **Left Panel**: Folder tree showing all directories with audio files
- **Right Panel**: Audio files in the currently selected folder

### How to Use

1. **Select a Root Directory**:
   - Click the "Browse..." button in the top toolbar
   - Navigate to your main practice/recording directory
   - Select the folder and click "Select Folder"

2. **Navigate Folders**:
   - Click on any folder in the left panel to view its audio files
   - The right panel will update to show files in the selected folder

3. **View Files**:
   - Files from the selected folder are displayed in the right panel
   - Each file shows: Take indicators, BPM, Filename, Duration, Size
   - Double-click a file to play it

## Toolbar Organization

The toolbar has been reorganized into two rows for better usability:

### Row 1: Directory Selection
- **Directory Field**: Shows the current root directory path
- **Browse...**: Opens folder selection dialog
- **Refresh**: Reloads files from the current directory

### Row 2: Actions and Filters
- **Actions**:
  - Batch Rename: Rename multiple files at once
  - Convert WAV→MP3: Convert WAV files to MP3 format
  
- **Filters**:
  - ★ Best Takes: Show only files marked as best takes
  - ◐ Partial Takes: Show only files marked as partial takes
  
- **Tools**:
  - 📊 Stats: View practice statistics
  - 🎯 Goals: Manage practice goals
  - 🎵 Setlist: Build setlists

## Metadata Support

### Per-Folder Metadata

The application loads metadata files from each folder independently:

- **`.provided_names.json`**: Custom display names for files
- **`.duration_cache.json`**: Cached audio durations
- **`.takes_metadata.json`**: Best take and partial take markers
- **`.audio_notes_*.json`**: Legacy format (backward compatible)

### How Metadata Works

When you select a file from a subfolder:
1. The application looks for metadata files in that subfolder
2. It uses the metadata specific to that folder
3. This allows different folders to have different naming conventions

### Example

```
Root/
  ├── .provided_names.json       # Metadata for root files
  ├── song1.wav                  # Uses root metadata
  ├── Practice_2024-01/
  │   ├── .provided_names.json   # Metadata for this folder
  │   ├── .takes_metadata.json
  │   └── recording1.wav         # Uses Practice_2024-01 metadata
  └── Practice_2024-02/
      ├── .provided_names.json   # Different metadata
      └── recording2.wav         # Uses Practice_2024-02 metadata
```

## Backward Compatibility

The application supports both old and new metadata formats:

### Legacy Format (Old AudioBrowser)
- **`.audio_notes_<username>.json`**: Contains take markers and annotations
- Format: `{"filename.wav": {"best_take": true, "partial_take": false}}`

### New Format
- **`.takes_metadata.json`**: Simplified take markers
- Format: `{"best_takes": ["file1.wav"], "partial_takes": ["file2.wav"]}`

Both formats are automatically detected and loaded. The application will:
1. Try to load the new format first
2. Fall back to legacy format if new format is not found
3. Merge data from multiple legacy files if needed

## Tips

1. **Organizing Practice Sessions**: 
   - Use subfolders for different practice sessions (e.g., "2024-01-15", "2024-01-20")
   - Each folder can have its own metadata files

2. **Filtering Files**:
   - Use the filter field in the right panel to quickly find files by name
   - Use the Best/Partial Takes filters to focus on specific recordings

3. **Folder Navigation**:
   - The folder tree only shows folders that contain audio files
   - Empty folders are automatically hidden

4. **Performance**:
   - Large directory trees are scanned efficiently
   - Only the selected folder's files are loaded into the file list
   - Metadata is cached per folder for fast access

## Troubleshooting

### Folders Not Showing

If you don't see subfolders in the tree:
- Make sure the subfolders contain audio files (.wav, .mp3)
- Check that folder names don't start with a dot (hidden folders are skipped)

### Metadata Not Loading

If custom names or take markers aren't showing:
- Verify the metadata file is in the same folder as the audio file
- Check the JSON file format is valid
- Look for error messages in the console

### Files Not Appearing

If audio files aren't showing after selecting a folder:
- Click the "Refresh" button to rescan
- Check the filter field isn't hiding files
- Verify the files have .wav, .wave, or .mp3 extensions
