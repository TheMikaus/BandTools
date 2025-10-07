# Setlist Builder User Guide

## Overview

The Setlist Builder is a powerful tool for organizing songs into performance setlists. It allows you to create, manage, and export setlists for live performances, rehearsals, or recording sessions.

## Opening the Setlist Builder

To open the Setlist Builder:
1. Click the **🎵 Setlist Builder** button in the Library tab toolbar
2. The Setlist Builder dialog will open in a non-modal window, allowing you to continue working with the main application

## Creating a New Setlist

1. In the **Manage Setlists** tab, click the **New** button
2. Enter a name for your setlist (e.g., "Summer Tour 2024", "Recording Session 1")
3. Click **OK**
4. Your new setlist will appear in the left panel

## Adding Songs to a Setlist

1. Select a setlist from the left panel
2. In the main application window, navigate to a song file you want to add
3. Click on the song to select it
4. Return to the Setlist Builder and click **Add Current Song**
5. The song will be added to your setlist with details:
   - Position number
   - Song name (from provided name metadata)
   - Best Take indicator (✓ if marked)
   - Duration
   - Source folder

**Note:** You cannot add the same song twice to a setlist. Songs from different folders can be added to the same setlist.

## Reordering Songs

To change the order of songs in your setlist:
1. Select the song you want to move by clicking on it
2. Click **↑ Move Up** to move it earlier in the setlist
3. Click **↓ Move Down** to move it later in the setlist

## Removing Songs

1. Select the song you want to remove
2. Click **Remove Song**
3. The song will be removed from the setlist (the original file is not affected)

## Adding Performance Notes

Each setlist can have performance notes attached to it:
1. Select a setlist
2. Scroll to the **Performance Notes** section at the bottom
3. Type your notes (e.g., key changes, tuning instructions, gear requirements)
4. Notes are automatically saved as you type

## Renaming a Setlist

1. Select the setlist you want to rename
2. Click the **Rename** button
3. Enter the new name
4. Click **OK**

## Deleting a Setlist

1. Select the setlist you want to delete
2. Click the **Delete** button
3. Confirm the deletion when prompted

**Warning:** This action cannot be undone!

## Validating a Setlist

The **Export & Validation** tab allows you to check your setlist for issues:

1. Switch to the **Export & Validation** tab
2. Select a setlist from the dropdown
3. Click **Validate Setlist**
4. Review the validation results, which include:
   - Total number of songs
   - Total duration
   - Missing files (files that no longer exist)
   - Songs without Best Take markers

### Validation Status

- **✓ Setlist is valid!** (green) - All files exist and are ready
- **⚠ Issues found:** (red) - Some files are missing or have issues
- **No Best Take** (orange) - Song exists but isn't marked as a Best Take

## Exporting a Setlist

To export your setlist to a text file:
1. Go to the **Export & Validation** tab
2. Select a setlist
3. Click **Export as Text**
4. Choose a location and filename
5. Click **Save**

The exported text file includes:
- Setlist name
- Performance notes
- Numbered song list with:
  - Song names
  - Best Take indicators
  - Durations
  - Source folders
- Total song count and duration
- Export timestamp

Example export format:
```
======================================================================
SETLIST: Summer Tour 2024
======================================================================

PERFORMANCE NOTES:
Key: D major, Drop D tuning for songs 3-5

----------------------------------------------------------------------

1. Opening Song
   ✓ Best Take | 3:45 | [practice_2024_01_15]

2. Second Song
   4:12 | [practice_2024_01_20]

...

----------------------------------------------------------------------
Total Songs: 12
Total Duration: 45:30

Exported: 2025-01-15 14:30:00
======================================================================
```

## Tips and Best Practices

### Organizing Setlists

- **Use descriptive names**: Include date, venue, or purpose (e.g., "Blue Note Jazz Club - March 2024")
- **Create multiple versions**: Keep variations for different audiences or venues
- **Mark best takes first**: Validate before exporting to ensure you're using your best recordings

### Performance Notes

Use performance notes to capture:
- Key signatures and transpositions
- Tuning requirements (Drop D, DADGAD, etc.)
- Tempo changes or click track settings
- Special gear or effects needed
- Cues for band members
- Song transitions or medleys

### File Organization

- **Keep files organized**: Store practice recordings in dated folders
- **Use provided names**: Name your files meaningfully so they're easy to identify in setlists
- **Check for missing files**: Run validation before performances to catch any file issues

## Keyboard Shortcuts

Currently, the Setlist Builder does not have dedicated keyboard shortcuts. You can use standard dialog navigation:
- **Tab** - Move between fields
- **Enter** - Confirm dialogs
- **Esc** - Close dialogs

## Troubleshooting

### "This song is already in the setlist"

This means you're trying to add a song that's already in the setlist. Each song can only appear once per setlist.

### Red text and "⚠ MISSING FILE" warning

The file no longer exists at its original location. Possible causes:
- File was moved or renamed
- Folder was deleted or moved
- File was on an external drive that's not connected

**Solution:** Remove the missing song and add the correct version from its new location.

### "No file selected" when adding songs

Make sure you've clicked on a song in the Library tab before clicking "Add Current Song" in the Setlist Builder.

## Data Storage

Setlists are stored in a `.setlists.json` file in your root practice folder. This file contains:
- All setlist definitions
- Song references (folder + filename)
- Performance notes
- Metadata (creation dates, UUIDs)

The file is automatically saved whenever you make changes. You can back up this file to preserve your setlists.

## Future Enhancements

Planned features for future releases:
- **Practice Mode**: Play through setlists automatically with playback controls
- **PDF Export**: Export setlists as formatted PDF files
- **Drag-and-drop reordering**: Drag songs to reorder them
- **Set breaks**: Add markers for breaks or intermissions
- **Print formatting**: Customizable print layouts

---

**Version**: 1.0  
**Last Updated**: January 2025  
**Related**: Phase 9 Implementation
