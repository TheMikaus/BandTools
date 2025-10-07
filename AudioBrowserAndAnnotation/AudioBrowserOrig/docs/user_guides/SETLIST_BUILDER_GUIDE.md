# Setlist Builder User Guide

**Feature**: Performance setlist management and preparation  
**Version**: 1.0  
**Access**: Tools menu → "Setlist Builder" or `Ctrl+Shift+T`

---

## Overview

The Setlist Builder helps you prepare for live performances by organizing your best takes into professional setlists. Create multiple setlists for different shows, validate they're ready to perform, export for printing, and practice in focused sessions.

**Key Benefits**:
- Organize songs from multiple practice sessions into performance sets
- Calculate total setlist duration for timing planning
- Validate all songs are ready (Best Takes marked, files exist)
- Export professional setlists for printing or sharing
- Focus practice sessions on upcoming performance material

---

## Getting Started

### Opening the Setlist Builder

**Method 1**: Menu
1. Click **Tools** in the menu bar
2. Select **Setlist Builder…**

**Method 2**: Keyboard Shortcut
- Press `Ctrl+Shift+T`

The Setlist Builder dialog will open with three tabs:
1. **Manage Setlists** - Create and organize setlists
2. **Practice Mode** - Activate setlists for focused practice
3. **Export & Validation** - Check readiness and export

---

## Creating Your First Setlist

### Step 1: Create a New Setlist

1. Open the Setlist Builder dialog
2. You'll see an empty list on the left side
3. Click the **"New Setlist"** button
4. Enter a name (e.g., "Summer Tour 2024", "Acoustic Set", "Local Brewery Show")
5. Click **OK**

Your new setlist appears in the list showing "(0 songs)".

### Step 2: Add Songs to Your Setlist

1. In the Setlist Builder, select your setlist from the list
2. In the **main AudioBrowser window**, navigate to a practice folder
3. Click on an audio file you want to add
4. Back in the Setlist Builder, click **"Add Song from Current Folder"**
5. The song appears in the songs table!

**Repeat** steps 2-4 to add more songs from any practice folder.

**Tips**:
- Add songs from different practice folders to build your best setlist
- Only Best Takes? Use validation to check!
- Songs show their provided name, not filename
- See which folder each song came from

### Step 3: Organize Song Order

Songs are added in the order you add them, but you can reorder them:

1. Select a song in the songs table
2. Click **"↑ Move Up"** to move it earlier in the setlist
3. Click **"↓ Move Down"** to move it later in the setlist
4. Repeat until your setlist is in performance order

**Position numbers** (1, 2, 3, ...) automatically update as you reorder.

### Step 4: Add Performance Notes

The Performance Notes section is perfect for:
- Key changes ("Song X drops to Eb tuning")
- Tempo notes ("Take the intro slower than practice")
- Gear requirements ("Need acoustic guitar for songs 3-5")
- Stage directions ("Lead singer moves to piano for this one")

1. Click in the **Performance Notes** text area
2. Type your notes
3. Notes **auto-save** as you type!

### Step 5: Check Total Duration

The **Total Duration** label shows your complete setlist length.

Example: `Total Duration: 45:30` means 45 minutes, 30 seconds.

Use this to:
- Plan your set length for venue requirements
- Ensure you're not too short or too long
- Balance acoustic vs. electric segments

---

## Managing Your Setlists

### Renaming a Setlist

1. Select the setlist you want to rename
2. Click **"Rename"** button
3. Enter the new name
4. Click **OK**

All songs and notes are preserved!

### Deleting a Setlist

1. Select the setlist you want to delete
2. Click **"Delete"** button
3. Confirm you want to delete it
4. The setlist is permanently removed

**Warning**: This cannot be undone! Export your setlist first if you want a backup.

### Removing Songs

1. Select your setlist
2. Click on a song in the songs table
3. Click **"Remove Song"** button
4. The song is removed from the setlist (original file is NOT deleted)

---

## Understanding the Songs Table

The songs table shows detailed information about each song:

| Column | Description |
|--------|-------------|
| **#** | Position number (1, 2, 3, ...) |
| **Song Name** | The provided name (or filename if no name set) |
| **Best Take** | ✓ if marked as Best Take, empty otherwise |
| **Duration** | Song length in M:SS format |
| **Folder** | Which practice folder contains this song |
| **Actions** | Reserved for future features |

**Color Coding**:
- **Black text**: File exists and is accessible
- **Red text**: File is missing or folder was moved (see Validation)

---

## Validating Your Setlist

Before a performance, validate your setlist is ready!

### Running Validation

1. Open the Setlist Builder
2. Switch to the **"Export & Validation"** tab
3. Select the setlist you want to validate
4. Click **"Validate Setlist"** button

### Understanding Results

The validation report shows:

**✓ All files exist**: Every song file is found
**❌ Missing Files**: Lists songs that can't be found (file moved or deleted)
**✓ All songs have Best Takes**: Every song is marked as Best Take
**⚠️  Songs without Best Take**: Lists songs that aren't marked as Best Take

### What to Do About Issues

**Missing Files**:
- Remove the song from the setlist
- Or find the file and update the practice folder

**Songs without Best Take**:
- Review the recording
- Mark it as Best Take if it's performance-ready
- Or replace it with a better take

**When you see**: ✅ **Setlist is ready for performance!**
- Your setlist is complete and validated
- All files exist
- All songs are Best Takes
- You're ready to perform!

---

## Exporting Your Setlist

Export your setlist to a text file for printing or sharing with band members.

### How to Export

1. Open the Setlist Builder
2. Go to **"Export & Validation"** tab
3. Select the setlist to export
4. Click **"Export as Text"** button
5. Choose where to save the file
6. Click **Save**

### What's Included

The exported text file contains:
- Setlist name
- Creation and export dates
- Numbered list of songs
- Individual song durations
- Total setlist duration
- Source folder and filename for each song
- **[BEST TAKE]** markers for Best Takes
- **[MISSING]** markers for missing files
- Performance notes

### Example Export

```
SETLIST: Summer Tour 2024
Created: 2025-01-15T12:00:00
Exported: 2025-01-20 15:30:00
============================================================

1. Sweet Home Alabama [BEST TAKE]
   Duration: 4:45
   Source: practice_2024_01_01/01_Sweet_Home_Alabama.mp3

2. Free Bird [BEST TAKE]
   Duration: 9:30
   Source: practice_2024_01_15/05_Free_Bird.mp3

3. Simple Man
   Duration: 5:20
   Source: practice_2024_02_01/03_Simple_Man.mp3

============================================================
Total Songs: 3
Total Duration: 19:35

PERFORMANCE NOTES:
Free Bird - Extended guitar solo in middle section
Simple Man - Acoustic guitar, drop to D tuning
```

---

## Practice Mode

Focus your practice sessions on setlist songs!

### Starting Practice Mode

1. Open the Setlist Builder
2. Go to **"Practice Mode"** tab
3. Select the setlist you want to practice
4. Click **"Start Practice Mode"** button
5. An information dialog confirms practice mode is active

### What Practice Mode Does

When practice mode is active:
- The setlist ID is stored for future enhancements
- You can close the Setlist Builder dialog
- Practice mode continues until you stop it

**Future Enhancements** (coming soon):
- Songs in the active setlist will be highlighted in the file tree
- Auto-play songs in setlist order
- Show current position (Song 3 of 12)
- Practice mode statistics tracking

### Stopping Practice Mode

1. Open the Setlist Builder
2. Go to **"Practice Mode"** tab
3. Click **"Stop Practice Mode"** button

---

## Tips and Best Practices

### Building Great Setlists

**Tip 1: Start with Best Takes**
- Before building a setlist, mark your best recordings as Best Takes
- Use validation to ensure all setlist songs have Best Takes

**Tip 2: Balance Your Set**
- Mix fast and slow songs
- Balance energy levels (don't put all high-energy songs together)
- Consider key changes and guitar tunings

**Tip 3: Time Your Set**
- Check total duration against venue requirements
- Add buffer time for banter/stage setup
- Remember: audiences appreciate pacing

**Tip 4: Document Everything**
- Use Performance Notes extensively
- Note gear changes, tuning changes, tempo adjustments
- Share exported setlist with band before the show

**Tip 5: Multiple Setlists**
- Create different setlists for different venues/audiences
- Have a backup setlist for technical issues
- Build "encore" setlists

### Organizing Practice Folders

**Best Practice**: Use consistent folder naming
- `practice_2024_01_15` (YYYY_MM_DD format)
- `practice_Jan_15_2024`
- `2024-01-15_practice`

This helps when viewing source folders in the songs table!

### Common Workflows

**Pre-Show Preparation**:
1. Create setlist from best takes across multiple practice sessions
2. Order songs for performance flow
3. Add performance notes
4. Validate setlist (all files exist, all are Best Takes)
5. Export to text file
6. Print or share with band

**Weekly Practice**:
1. Create practice setlist of songs you're working on
2. Use Practice Mode to focus on those songs
3. Update as songs improve
4. Move songs to performance setlist when ready

**Post-Show Review**:
1. Create setlist matching what you actually played
2. Compare to original plan (what changed?)
3. Add notes about what worked/didn't work
4. Use for planning next show

---

## Troubleshooting

### "No File Selected" Warning

**Problem**: Clicked "Add Song from Current Folder" but got this warning.

**Solution**: In the main AudioBrowser window, click on an audio file first, then try again.

### "Already in Setlist" Message

**Problem**: Trying to add a song that's already in the setlist.

**Solution**: You can't add the same song twice. If you want it to appear multiple times in your performance, you'll need to have multiple practice recordings.

### Song Appears in Red Text

**Problem**: A song in your setlist shows in red text.

**Solution**: The file no longer exists (moved or deleted). Either:
- Find the file and restore it to the original location
- Remove the song from the setlist
- Replace it with a different recording

### "No Selection" Warnings

**Problem**: Getting warnings about selecting something first.

**Solution**: Always select a setlist from the list before trying to add/remove songs, validate, or export.

### Can't Find the Dialog

**Problem**: Closed the Setlist Builder and can't find it.

**Solution**: 
- Press `Ctrl+Shift+T`
- Or: Tools menu → "Setlist Builder"

### Performance Notes Not Saving

**Problem**: Notes disappear when switching setlists.

**Solution**: Notes auto-save after a brief delay. Wait 1-2 seconds after typing before switching setlists. If notes still don't save, there may be a file permission issue with `.setlists.json`.

---

## Data Storage and Backup

### Where Are Setlists Stored?

Setlists are saved in a file called `.setlists.json` in your root practice folder (the folder you selected as "Band Practice Folder").

**Location**: `[Your Band Practice Folder]/.setlists.json`

### Backing Up Your Setlists

**Method 1: Copy the File**
Copy `.setlists.json` to a backup location (USB drive, cloud storage, etc.)

**Method 2: Export Each Setlist**
Export each setlist to text format. While you'll need to rebuild the setlist, you'll have all the information.

### Sharing Setlists Between Band Members

**Current Method**:
1. Copy `.setlists.json` from your practice folder
2. Send to band member
3. They copy it to their practice folder

**Note**: This replaces their setlists entirely. Future versions may support merging.

### Restoring Setlists

If you accidentally delete setlists:
1. Restore `.setlists.json` from backup
2. Restart AudioBrowser
3. Open Setlist Builder - your setlists are back!

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+T` | Open Setlist Builder |

**Note**: All other operations currently use mouse clicks. More keyboard shortcuts may be added in future versions.

---

## Advanced Features

### Adding Songs from Multiple Folders

You can build a setlist with songs from any practice session:

1. Navigate to practice folder A in main window
2. Select a song
3. Add to setlist
4. Navigate to practice folder B
5. Select a different song
6. Add to setlist
7. Both songs are now in the setlist with their source folders shown!

This lets you collect your best takes across all practice sessions.

### Understanding Song References

**Important**: Setlists store *references* to songs, not copies.

- Songs are stored as: folder name + filename
- Original audio files are NOT copied or moved
- If you move/delete a practice folder, setlist songs from that folder will be marked missing

**Benefit**: No disk space overhead! Your setlist is just a organized list of pointers.

---

## Future Enhancements

These features are planned for future releases:

### Coming Soon
- **PDF Export**: Professional PDF format with formatting options
- **Drag-and-Drop Reordering**: Drag songs to reorder instead of Move Up/Down buttons
- **File Tree Highlighting**: Highlight active setlist songs in the file tree
- **Auto-Play in Practice Mode**: Automatically play songs in setlist order

### Under Consideration
- **Setlist Templates**: Pre-defined templates (3-song opener, full show, acoustic set)
- **Collaborative Editing**: Share and edit setlists with band members
- **BPM Display**: Show song tempo in setlist
- **Statistics Integration**: Track how often you practice setlist songs
- **Multiple Setlist Views**: Grid view, timeline view, etc.

---

## FAQ

**Q: Can I add the same song to multiple setlists?**  
A: Yes! Each setlist is independent. Add a song to as many setlists as you want.

**Q: What happens if I delete a practice folder?**  
A: Songs from that folder in your setlists will show as missing (red text). You can remove them from the setlist or restore the folder.

**Q: Can I change a song's provided name after adding it to a setlist?**  
A: Yes! The setlist shows the current provided name from the song's metadata. Change it in the Library tab and it updates in the setlist.

**Q: How many setlists can I create?**  
A: No limit! Create as many as you need.

**Q: How many songs can be in a setlist?**  
A: No limit! Though very large setlists (100+ songs) may be slow to validate and export.

**Q: Can I print my setlist?**  
A: Yes! Export to text format, then open the text file and print from any text editor or word processor.

**Q: Does creating a setlist affect my practice folders?**  
A: No! Setlists only store references. Your practice folders and audio files are never modified by the Setlist Builder.

**Q: Can I rename files after adding them to a setlist?**  
A: If you use AudioBrowser's "Batch Rename" feature, it updates the provided name but keeps the same filename, so setlist references remain valid. If you manually rename files outside AudioBrowser, the setlist will lose the reference.

**Q: What if I don't see the "Best Take" checkmark?**  
A: The song isn't marked as Best Take in any annotation set. Mark it as Best Take in the Annotations tab, then check again.

---

## Getting Help

**Documentation**:
- [IMPLEMENTATION_SUMMARY_SETLIST_BUILDER.md](../technical/IMPLEMENTATION_SUMMARY_SETLIST_BUILDER.md) - Technical details
- [TEST_PLAN_SETLIST_BUILDER.md](../test_plans/TEST_PLAN_SETLIST_BUILDER.md) - Complete test cases
- [INTERFACE_IMPROVEMENT_IDEAS.md](../technical/INTERFACE_IMPROVEMENT_IDEAS.md) - Future features

**Issues or Suggestions**:
- Report bugs via GitHub Issues
- Request features via GitHub Issues
- See [HOWTO_NEW_FEATURES.md](HOWTO_NEW_FEATURES.md) for general usage

---

## Conclusion

The Setlist Builder bridges the gap between practice and performance. Use it to:
- Organize your best material into professional sets
- Validate you're ready to perform
- Document key changes and requirements
- Share setlists with your band

**Happy performing! 🎸🎤🥁**

---

*Last Updated: January 2025*  
*Version: 1.0*
