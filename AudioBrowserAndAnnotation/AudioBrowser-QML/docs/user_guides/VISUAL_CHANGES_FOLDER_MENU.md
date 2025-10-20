# Visual Changes - Folder Context Menu

## Overview

This document provides a visual representation of the UI changes for the folder context menu feature.

## Folder Tree - Before

```
┌─────────────────────────────────────┐
│ Folders                             │
├─────────────────────────────────────┤
│                                     │
│ 📂 2024-01-15 Practice (5)         │
│   📂 Take 1 (2)                    │  ← Left-click only
│   📂 Take 2 (3)                    │
│                                     │
│ 📂 Studio Recordings (12)          │
│   📂 Song A (4)                    │
│   📂 Song B (8)                    │
│                                     │
└─────────────────────────────────────┘
```

## Folder Tree - After (Right-Click Menu)

```
┌─────────────────────────────────────┐
│ Folders                             │
├─────────────────────────────────────┤
│                                     │
│ 📂 2024-01-15 Practice (5)         │
│   📂 Take 1 (2)                    │ ┌──────────────────────────────┐
│   📂 Take 2 (3) ◄──────────────────┤│ 🔍 Generate Fingerprints     │
│                │                   ││─────────────────────────────┤
│ 📂 Studio Rec  │                   ││ ⭐ Mark as Reference Folder  │
│   📂 Song A (4)│                   ││ 🚫 Mark as Ignore Fingerp... │
│   📂 Song B (8)│                   ││─────────────────────────────┤
│                │                   ││ 📊 Generate Waveforms        │
│                │                   │└──────────────────────────────┘
│                └───────────────────┘
│                   (Right-click context menu)
└─────────────────────────────────────┘
```

## Context Menu Options

### Option 1: Generate Fingerprints

**Menu Text:** 🔍 Generate Fingerprints

**What happens when clicked:**
1. Menu closes
2. Application switches to Fingerprints tab
3. Progress appears in the log:
   ```
   Generating fingerprints for 3 files in /path/to/Take 2
   Processing file 1/3: song1.wav
   Processing file 2/3: song2.wav
   Processing file 3/3: song3.wav
   Fingerprint generation complete!
   ```

### Option 2: Mark as Reference Folder

**Initial state (not marked):**
```
┌──────────────────────────────┐
│ ⭐ Mark as Reference Folder  │  ← Click to mark
└──────────────────────────────┘
```

**After clicking (marked):**
```
┌──────────────────────────────┐
│ ⭐ Unmark Reference Folder   │  ← Click to unmark
└──────────────────────────────┘
```

**Visual indicator (future enhancement):**
```
┌─────────────────────────────────────┐
│ Folders                             │
├─────────────────────────────────────┤
│                                     │
│ 📂 2024-01-15 Practice (5)         │
│ ⭐ Studio Recordings (12)          │  ← Star badge for reference
│   📂 Song A (4)                    │
│   📂 Song B (8)                    │
│                                     │
└─────────────────────────────────────┘
```

### Option 3: Mark as Ignore Fingerprints

**Initial state (not ignored):**
```
┌──────────────────────────────┐
│ 🚫 Mark as Ignore Fingerp... │  ← Click to ignore
└──────────────────────────────┘
```

**After clicking (ignored):**
```
┌──────────────────────────────┐
│ 🚫 Unmark Ignore Fingerpr... │  ← Click to un-ignore
└──────────────────────────────┘
```

**Visual indicator (future enhancement):**
```
┌─────────────────────────────────────┐
│ Folders                             │
├─────────────────────────────────────┤
│                                     │
│ 📂 2024-01-15 Practice (5)         │
│ 🚫 Test Recordings (8)             │  ← Crossed circle for ignored
│   📂 Experiment 1 (3)              │
│   📂 Experiment 2 (5)              │
│                                     │
└─────────────────────────────────────┘
```

### Option 4: Generate Waveforms

**Menu Text:** 📊 Generate Waveforms

**What happens when clicked:**
1. Menu closes
2. Waveform generation starts in background
3. No immediate UI change
4. Waveforms are cached for later use
5. When you select a file, waveform appears instantly

## Batch Operations Menu - Before

```
┌─────────────────────────────────────┐
│ Library Tab - Toolbar               │
├─────────────────────────────────────┤
│                                     │
│ 📁  🔄  [                    ] ⋮   │
│                                ↓    │
│                           ┌────────────┐
│                           │ Batch Ren..│  ← Grayed out even
│                           │ Convert... │     when files exist
│                           └────────────┘
└─────────────────────────────────────┘
```

## Batch Operations Menu - After (Fixed)

```
┌─────────────────────────────────────┐
│ Library Tab - Toolbar               │
├─────────────────────────────────────┤
│                                     │
│ 📁  🔄  [                    ] ⋮   │
│                                ↓    │
│  Files loaded: 15              ┌────────────────┐
│                                │ Batch Rename   │  ← Enabled!
│                                │ Convert WAV→MP3│  ← Enabled!
│                                │─────────────── │
│                                │ ★ Best Takes   │
│                                │ ◐ Partial T... │
│                                └────────────────┘
└─────────────────────────────────────┘

When no files:
┌────────────────┐
│ Batch Rename   │  ← Disabled (grayed)
│ Convert WAV→MP3│  ← Disabled (grayed)
└────────────────┘
```

## User Flow Diagrams

### Flow 1: Generate Fingerprints for Folder

```
User in Library Tab
        ↓
User right-clicks folder
        ↓
Context menu appears
        ↓
User clicks "🔍 Generate Fingerprints"
        ↓
Application switches to Fingerprints Tab
        ↓
Progress shown in log
        ↓
Files processed in background
        ↓
Complete! Fingerprints saved
```

### Flow 2: Mark Folder as Reference

```
User in Library Tab
        ↓
User right-clicks "Studio Recordings" folder
        ↓
Context menu shows "⭐ Mark as Reference Folder"
        ↓
User clicks menu item
        ↓
Folder is marked as reference
        ↓
.audio_fingerprints.json updated
        ↓
Next time: Menu shows "⭐ Unmark Reference Folder"
```

### Flow 3: Batch Operations with Files

```
User in Library Tab
        ↓
User selects folder with files
        ↓
Files list populates (e.g., 10 files)
        ↓
User clicks "⋮" (More) button
        ↓
Menu appears - "Batch Rename" is ENABLED ✓
        ↓
User clicks "Batch Rename"
        ↓
Batch Rename Dialog opens with file list
```

## Code Snippets Showing Changes

### QML - Folder MouseArea (Before)

```qml
MouseArea {
    id: folderMouseArea
    anchors.fill: parent
    hoverEnabled: true
    
    onClicked: {
        // Only handles left-click
        // Select folder and load files
    }
}
```

### QML - Folder MouseArea (After)

```qml
MouseArea {
    id: folderMouseArea
    anchors.fill: parent
    hoverEnabled: true
    acceptedButtons: Qt.LeftButton | Qt.RightButton  // ← Added right-click
    
    onClicked: function(mouse) {
        if (mouse.button === Qt.RightButton) {  // ← New: Right-click handler
            folderContextMenu.folderPath = model.path
            folderContextMenu.folderName = model.name
            folderContextMenu.popup()
        } else {
            // Existing left-click code
        }
    }
}
```

### QML - Batch Operations Menu (Before)

```qml
MenuItem {
    text: "Batch Rename"
    enabled: fileListModel && fileListModel.count() > 0  // ← Evaluated once
}
```

### QML - Batch Operations Menu (After)

```qml
Menu {
    id: moreMenu
    property int fileCount: 0  // ← Dynamic property
    
    onAboutToShow: {  // ← Re-evaluate when menu opens
        fileCount = fileListModel ? fileListModel.count() : 0
    }
    
    MenuItem {
        text: "Batch Rename"
        enabled: moreMenu.fileCount > 0  // ← Uses dynamic property
    }
}
```

## Data Structure Changes

### Fingerprint Cache - Before

```json
{
  "version": 1,
  "files": {
    "song1.wav": {
      "fingerprints": { ... }
    }
  },
  "excluded_files": ["test.wav"]
}
```

### Fingerprint Cache - After

```json
{
  "version": 1,
  "files": {
    "song1.wav": {
      "fingerprints": { ... }
    }
  },
  "excluded_files": ["test.wav"],
  "is_reference_folder": true,      // ← New field
  "ignore_fingerprints": false      // ← New field
}
```

## Interactive Example

### Example Session: Organizing Practice Recordings

**Step 1: User has multiple practice session folders**
```
📂 Practice Sessions
  📂 2024-01-10 (rough takes)
  📂 2024-01-15 (better takes)
  📂 2024-01-20 (final session)
```

**Step 2: User marks folders appropriately**
```
📂 Practice Sessions
  🚫 2024-01-10 (rough takes)        ← Marked as "Ignore"
  📂 2024-01-15 (better takes)
  ⭐ 2024-01-20 (final session)      ← Marked as "Reference"
```

**Step 3: User generates fingerprints for all**
- Right-click each folder → "🔍 Generate Fingerprints"
- Switches to Fingerprints tab
- All folders processed

**Step 4: During matching operations**
- Fingerprints from 2024-01-10 are ignored
- Fingerprints from 2024-01-20 have higher priority
- Matching results prioritize the final session recordings

## Summary of Visual Changes

### New UI Elements
1. **Folder context menu** with 4 options
2. **Dynamic menu text** that changes based on state
3. **Menu icons** for each operation

### Fixed UI Elements
1. **Batch Rename** menu item now enables correctly
2. **Convert WAV→MP3** menu item now enables correctly

### Future Visual Enhancements (Not Yet Implemented)
1. Visual badges on folders (⭐ for reference, 🚫 for ignored)
2. Progress bar for waveform generation
3. Tooltip showing folder status on hover
4. Color coding for different folder types
