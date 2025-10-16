# Multi-Annotation Sets User Guide

## Overview

The Multi-Annotation Sets feature allows you to organize annotations into separate, named collections. This is useful for:

- **Multiple Users**: Each band member can have their own annotation set
- **Different Contexts**: Separate sets for practice vs. performance notes
- **Version Tracking**: Keep different versions of annotations (e.g., "V1 Notes", "V2 Notes")
- **Collaboration**: Share and compare annotations across sets

## Key Concepts

### Annotation Set
A named collection of annotations with its own color. Each set stores:
- Annotations for audio files
- General notes per file
- Best/partial take markings

### Current Set
The active annotation set. When you create or edit annotations, they go into the current set.

### Merged View
A special mode that displays annotations from all visible sets in a single table, with a "Set" column showing which set each annotation belongs to.

## Getting Started

### Creating Your First Set

When you open a folder for the first time, a default annotation set is automatically created using your username.

To create additional sets:

1. Go to the **Annotations** tab
2. Find the "Annotation Set:" section in the toolbar
3. Click **Add Set**
4. Enter a name for your set (e.g., "Practice Notes", "John's Set")
5. Click **Create**

The new set becomes your current active set automatically.

### Switching Between Sets

Use the **Annotation Set** dropdown to switch between sets:

1. Click the dropdown menu next to "Annotation Set:"
2. Select the set you want to work with
3. The annotations table updates to show only that set's annotations

## Working with Sets

### Adding Annotations

1. Select the set you want to add annotations to
2. Click **Add** in the Annotations toolbar
3. Fill in the annotation details
4. Click **Save**

The annotation is saved to the current set only.

### Renaming a Set

1. Select the set you want to rename
2. Click **Rename**
3. Enter the new name
4. Click **Rename**

### Deleting a Set

⚠️ **Warning**: Deleting a set permanently removes all its annotations!

1. Select the set you want to delete
2. Click **Delete**
3. Confirm the deletion

Note: You cannot delete the last remaining set. At least one set must always exist.

## Merged View Mode

### What is Merged View?

Merged View shows annotations from **all visible sets** in a single table, making it easy to:
- Compare annotations across sets
- See all notes at once
- Identify different perspectives on the same timestamp

### Enabling Merged View

1. Go to the **Annotations** tab
2. Check the box: **"Show all visible sets in table"**
3. The table now shows a "Set" column with the set name for each annotation

### Reading Merged View

In merged view, the table shows:
- **Set**: The name of the annotation set
- **Time**: Timestamp of the annotation
- **Category**: Annotation category
- **Text**: Annotation content
- **User**: Who created the annotation
- **Important**: Important flag

The "Set" column is color-coded to match each set's assigned color.

### Disabling Merged View

Uncheck **"Show all visible sets in table"** to return to single-set view.

## Best Practices

### Naming Conventions

- **User Names**: "John", "Sarah", "Mike" - for multi-user collaboration
- **Context**: "Practice", "Performance", "Rehearsal" - for different scenarios
- **Versions**: "V1", "V2", "Final" - for iterative annotation
- **Dates**: "2024-01-15" - for time-based organization

### When to Use Multiple Sets

**Good Use Cases**:
- Each band member has their own set
- Separate practice notes from performance notes
- Keep old annotations while creating new ones
- Compare different interpretations of the same piece

**Less Useful**:
- Creating too many sets for the same purpose
- Duplicating information across sets unnecessarily

### Organization Tips

1. **Start with one set per user** - Each person gets their own annotation space
2. **Use merged view for reviews** - See everyone's input at once during band meetings
3. **Archive old sets** - Delete or rename sets from old sessions when done
4. **Consistent naming** - Use clear, descriptive names

## Advanced Features

### Set Colors

Each set is automatically assigned a color for visual distinction. Colors are consistent across sessions for the same set name.

### Per-Set Best/Partial Takes

Best and partial take markings are stored per-set, allowing each user or context to have different opinions on which takes are best.

### Persistence

Annotation sets are saved to disk automatically:
- Location: `.{username}_notes.json` in each folder
- Format: JSON with all sets and their data
- Backup: Included in the application's backup system

### Legacy Format Conversion

If you have old annotation files (from before multi-set support), they are automatically converted to the multi-set format on first load.

## Troubleshooting

### My annotations disappeared!

Check that:
1. You're in the correct annotation set (check the dropdown)
2. You haven't accidentally enabled merged view (uncheck "Show all visible sets")
3. The current file is selected (annotations are per-file)

### Cannot delete my set

You cannot delete the last remaining set. Create a new set first, then delete the old one.

### Merged view shows duplicates

This is normal if multiple sets have annotations at similar timestamps. Each annotation belongs to a specific set.

### Set colors don't match

Set colors are automatically assigned based on the set name. Renaming a set may change its color.

## Keyboard Shortcuts

- **Ctrl+A** - Quick add annotation (to current set)
- **[ / ]** - Set clip boundaries (in current set)
- **Ctrl+2** - Switch to Annotations tab

## Related Features

- **Clips System**: Clips are also set-specific
- **Folder Notes**: Each set can have separate folder notes
- **Export**: Export can include all sets or just the current set

## FAQs

**Q: Can I move annotations between sets?**
A: Currently, no. You would need to copy the annotation data manually.

**Q: Are sets shared across directories?**
A: No. Each directory has its own set of annotation sets.

**Q: How many sets can I create?**
A: There's no hard limit, but keeping it to 5-10 sets per directory is practical.

**Q: Do sets affect audio playback?**
A: No. Sets only affect annotations, notes, and take markings.

**Q: Can I export just one set's annotations?**
A: Yes. Disable merged view and export to get only the current set's annotations.

---

**For more information**, see:
- [Annotation Guide](ANNOTATION_GUIDE.md)
- [Keyboard Shortcuts](KEYBOARD_SHORTCUTS.md)
- [Quick Start Guide](QUICK_START.md)
