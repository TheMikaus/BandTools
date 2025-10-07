# Annotation Guide - AudioBrowser QML

## Overview

The annotation system allows you to mark important points in your audio files with notes, categories, and visual markers. Annotations are automatically saved and persist across sessions.

---

## Quick Start

### Creating Your First Annotation

1. **Load an audio file** in the Library tab
2. **Play the file** or use the seek slider to find the point you want to mark
3. **Switch to the Annotations tab**
4. **Click the "Add" button**
5. **Enter your annotation text** in the dialog
6. **Click OK**

Your annotation now appears:
- As a visual marker on the waveform
- As a row in the annotations table

---

## Features

### Annotation Properties

Each annotation has the following properties:

- **Timestamp**: The exact position in the audio (MM:SS.mmm format)
- **Text**: Your note or description (can be multiple lines)
- **Category**: Optional categorization (timing, energy, harmony, dynamics, notes)
- **Color**: Visual color for the marker (7 colors available)
- **Importance**: Flag to mark critical annotations

### Visual Markers

Annotations appear as vertical lines on the waveform:
- **Color**: Matches the annotation's color
- **Flag**: Important annotations show a star flag at the top
- **Tooltip**: Hover over a marker to see details

### Annotation Table

The table shows all annotations for the current file:
- **Columns**: Time, Category, Text, Important
- **Click**: Select and seek to that timestamp
- **Double-click**: Open the edit dialog

---

## Operations

### Adding Annotations

#### Method 1: Using Current Playback Position
1. Play to the desired point
2. Click **"Add"** button
3. The timestamp is automatically set to current position
4. Enter text and other properties
5. Click **OK**

#### Method 2: Manual Timestamp Entry
1. Click **"Add"** button
2. Enter timestamp manually in MM:SS.mmm format
3. Or click **"Current"** to use playback position
4. Fill in other fields
5. Click **OK**

### Editing Annotations

#### From Table:
1. Click on annotation in table to select
2. Click **"Edit"** button
3. Modify properties in dialog
4. Click **OK**

#### From Waveform:
1. Double-click on marker
2. Dialog opens with current values
3. Modify as needed
4. Click **OK**

### Deleting Annotations

#### Single Annotation:
1. Select annotation in table
2. Click **"Delete"** button
3. Annotation removed immediately

#### All Annotations:
1. Click **"Clear All"** button
2. Confirm in dialog
3. All annotations for current file deleted

### Navigation

#### Seek to Annotation:
- **Click** on annotation in table → jumps to timestamp
- **Click** on marker on waveform → jumps to timestamp

### Filtering

#### By Category:
1. Select category from dropdown
2. Table updates to show only that category
3. Select **"All"** to show everything

#### By Importance:
1. Check **"Important only"** checkbox
2. Table shows only important annotations
3. Uncheck to show all

#### Combined Filters:
- You can use category and importance filters together
- Only annotations matching both criteria are shown

---

## Best Practices

### Naming Conventions

**Good annotation text**:
- "Guitar solo starts - high energy"
- "Vocals enter - melody in C major"
- "Timing issue - slightly behind beat"

**Poor annotation text**:
- "Note" (too vague)
- "Here" (not descriptive)
- "..." (no information)

### Using Categories

- **timing**: Rhythm issues, tempo changes, sync problems
- **energy**: Dynamics, intensity changes, crescendos
- **harmony**: Chord progressions, key changes, harmonies
- **dynamics**: Volume levels, balance issues
- **notes**: General observations, reminders

### Importance Flag

Use for:
- Critical mistakes to fix
- Key musical moments
- Must-remember sections
- Priority items for review

Don't overuse - if everything is important, nothing is.

### Color Coding

Develop your own color system:
- **Red**: Issues/problems to fix
- **Green**: Good takes/highlights
- **Blue**: General notes
- **Orange**: Timing-related
- **Purple**: Harmony-related
- **Teal**: Energy/dynamics
- **Gray**: Questions/uncertain

---

## Keyboard Shortcuts

Currently, all annotation operations require mouse clicks. Keyboard shortcuts are planned for a future update.

---

## File Storage

### Where Annotations Are Saved

Annotations are stored in hidden JSON files next to your audio files:

```
/your/music/folder/
  ├── song.wav
  └── .song_annotations.json  (hidden)
```

### File Format

The JSON format is human-readable and portable:

```json
[
  {
    "timestamp_ms": 15340,
    "text": "Guitar solo starts here",
    "category": "energy",
    "important": true,
    "color": "#e74c3c",
    "user": "default_user",
    "created_at": "2024-12-15T10:30:00",
    "updated_at": "2024-12-15T10:30:00"
  }
]
```

### Backup

To backup your annotations:
1. Copy the `.{filename}_annotations.json` files
2. Store in a safe location
3. Can be restored by copying back

**Note**: Annotation files are hidden (start with `.`), so you may need to enable "Show hidden files" in your file manager.

---

## Multi-User Support

### Username

Each annotation includes the username of who created it. Currently, this is set to "default_user".

To change your username:
1. This feature is planned for a future update
2. For now, all annotations use "default_user"

### Future Enhancements

- User profiles
- Color-coding by user
- Filter by user
- Multi-user collaboration

---

## Tips & Tricks

### Workflow Tips

1. **Annotate during playback**: Pause when you hear something noteworthy
2. **Use categories consistently**: Develop your own system
3. **Be specific**: Include musical context in annotations
4. **Review regularly**: Filter by category to review related items
5. **Mark important**: Use for priority items that need attention

### Performance Tips

1. **Limit annotations**: Large numbers (>1000) may slow rendering
2. **Use zoom**: Zoom in to see markers more clearly
3. **Filter when needed**: Reduce visual clutter with filters
4. **Regular cleanup**: Delete old/obsolete annotations

### Organization Tips

1. **Category structure**: Use categories as your main organization tool
2. **Color consistency**: Stick to your color system
3. **Timestamp precision**: Exact timestamps help with navigation
4. **Clear text**: Future-you will thank you for clear notes

---

## Troubleshooting

### Markers Not Visible

**Problem**: Can't see annotation markers on waveform

**Solutions**:
- Zoom in on waveform for better visibility
- Check that waveform is generated (click "Generate" if needed)
- Verify annotations exist (check table)

### Annotations Lost

**Problem**: Annotations disappeared after closing application

**Solutions**:
- Check that `.{filename}_annotations.json` file exists
- Verify file wasn't moved/renamed
- Check file permissions (must be writable)
- Restore from backup if available

### Can't Edit Annotation

**Problem**: Edit button is disabled

**Solutions**:
- Select annotation in table first (click on row)
- Verify file is loaded in audio engine
- Try restarting application

### Dialog Won't Open

**Problem**: Add/Edit buttons don't respond

**Solutions**:
- Check console for error messages
- Verify a file is loaded
- Restart application
- Report bug if persists

---

## FAQ

### Q: Can I export annotations?

**A**: Not yet. Export to CSV/PDF is planned for a future update.

### Q: Can annotations span a time range?

**A**: Not yet. Currently only point annotations are supported. Time range annotations are planned.

### Q: Can I share annotations with others?

**A**: Yes! Simply copy the `.{filename}_annotations.json` file to share. The recipient needs the same audio file.

### Q: Are annotations compatible with the old PyQt6 version?

**A**: Yes! The JSON format is the same, so annotations work in both versions.

### Q: Can I search annotation text?

**A**: Not yet. Full-text search is planned for a future update.

### Q: How many annotations can I create?

**A**: No hard limit, but performance may degrade with very large numbers (>1000).

### Q: Can I undo/redo changes?

**A**: Not yet. Changes are immediate and permanent. Undo/redo is planned.

### Q: Can I drag markers to adjust timestamps?

**A**: Not yet. This feature is planned for a future update.

---

## Planned Features

### Short-Term
- Keyboard shortcuts
- Annotation search
- Drag markers to adjust time
- Export to CSV/PDF
- Undo/redo

### Long-Term
- Time range annotations
- Annotation templates
- Cloud sync
- Mobile app
- AI-generated annotations

---

## Need Help?

- **Documentation**: See PHASE_3_COMPLETE.md for technical details
- **Developer Guide**: See DEVELOPER_GUIDE.md for customization
- **Issues**: Report bugs on GitHub
- **Questions**: Open a discussion on GitHub

---

**Version**: Phase 3 (v0.3.0)  
**Last Updated**: December 2024  
**Status**: Feature Complete, Testing Pending
