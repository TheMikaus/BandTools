# Folder Context Menu Guide

## Overview

The folder context menu provides quick access to batch operations on entire folders in the Library view. This menu appears when you right-click on any folder in the folder tree.

## Accessing the Folder Context Menu

1. Navigate to the **Library** tab
2. Find the folder tree in the left panel (shows all folders containing audio files)
3. **Right-click** on any folder
4. The context menu will appear with the following options

## Menu Options

### 🔍 Generate Fingerprints

Generates audio fingerprints for all audio files in the selected folder and its subfolders.

**What it does:**
- Scans all audio files in the folder recursively
- Generates fingerprints using the currently selected algorithm
- Runs in the background with progress updates
- Automatically switches to the **Fingerprints** tab when started

**Use cases:**
- Identifying duplicate recordings across different practice sessions
- Matching songs across different folders
- Building a fingerprint database for automatic song identification

**How to use:**
1. Right-click on a folder
2. Select "🔍 Generate Fingerprints"
3. The app will switch to the Fingerprints tab and show progress
4. Wait for the generation to complete

### ⭐ Mark as Reference Folder

Marks the folder as a "reference" folder, giving its fingerprints higher weight during matching operations.

**What it does:**
- Sets a flag in the folder's fingerprint cache
- Fingerprints from this folder will be prioritized during matching
- Useful for designating authoritative or original recordings

**Use cases:**
- Mark a folder containing original song recordings
- Designate a folder with high-quality reference tracks
- Prioritize studio recordings over live performances

**How to use:**
1. Right-click on a folder
2. Select "⭐ Mark as Reference Folder"
3. The menu will show "⭐ Unmark Reference Folder" if the folder is already marked
4. Click again to toggle the status

**Note:** A folder can be both a reference folder and have fingerprints ignored - these flags are independent.

### 🚫 Mark as Ignore Fingerprints

Marks the folder to be excluded from fingerprint matching operations.

**What it does:**
- Sets a flag in the folder's fingerprint cache
- Fingerprints from this folder will not be used for matching
- The fingerprints are still stored but won't appear in match results

**Use cases:**
- Exclude experimental or test recordings
- Ignore low-quality recordings
- Skip folders with duplicate or incomplete takes

**How to use:**
1. Right-click on a folder
2. Select "🚫 Mark as Ignore Fingerprints"
3. The menu will show "🚫 Unmark Ignore Fingerprints" if the folder is already marked
4. Click again to toggle the status

### 📊 Generate Waveforms

Generates visual waveforms for all audio files in the selected folder.

**What it does:**
- Scans all audio files in the folder recursively
- Generates waveform data for each file
- Runs in the background
- Waveforms are cached for future use

**Use cases:**
- Pre-generate waveforms for faster browsing
- Prepare files for annotation work
- Create visual references for all recordings in a session

**How to use:**
1. Right-click on a folder
2. Select "📊 Generate Waveforms"
3. The generation runs in the background
4. You can continue working while waveforms are generated

**Note:** Waveforms are displayed in the Annotations tab when you select a file.

## Tips

- **Batch operations** can take time for folders with many files. Be patient!
- **Reference and Ignore flags** are stored in `.audio_fingerprints.json` files in each folder
- You can use both **Reference** and **Ignore** flags on the same folder if needed (though this is unusual)
- **Waveform generation** happens in the background and doesn't block the UI
- Check the **Fingerprints** tab for detailed progress on fingerprint generation

## Technical Details

### Folder Metadata Storage

The folder flags are stored in each folder's `.audio_fingerprints.json` file:

```json
{
  "version": 1,
  "files": { ... },
  "excluded_files": [ ... ],
  "is_reference_folder": true,
  "ignore_fingerprints": false
}
```

### Fingerprint Algorithms

The folder context menu uses the currently selected fingerprint algorithm (configurable in the Fingerprints tab):
- **Spectral** - Default, frequency-based analysis
- **Lightweight** - Faster, less accurate
- **Chromaprint** - Based on the AcoustID algorithm
- **Audfprint** - Landmark-based matching

### Recursive Scanning

All folder operations scan recursively, meaning:
- Subfolders are included
- Hidden folders (starting with `.`) are skipped
- Only audio files (.wav, .mp3) are processed
