# How-To Guide: New Features

This guide explains how to use the recently added features in AudioBrowser.

## Table of Contents
1. [Dark Mode Theme](#dark-mode-theme)
2. [Export Best Takes Package](#export-best-takes-package)

---

## Dark Mode Theme

The application now supports both light and dark color themes for better visibility in different lighting conditions.

### How to Enable Dark Mode

1. **Open Preferences**
   - Click **File** menu
   - Select **Preferences…**

2. **Select Theme**
   - In the Preferences dialog, find the **Theme** dropdown
   - Select **Dark** (or **Light** to switch back)

3. **Apply and Restart**
   - Click **OK** to save your preference
   - A dialog will appear informing you that restart is required
   - Close the application and restart it

4. **Enjoy Dark Mode**
   - All UI elements, menus, and waveforms will now use the dark theme
   - Your preference is saved and will persist across sessions

### When to Use Each Theme

**Light Theme** (Default)
- Bright, well-lit environments
- Traditional interface appearance
- High contrast text on light background

**Dark Theme**
- Low-light conditions or night work
- Reduces eye strain during extended sessions
- Modern appearance
- Better battery life on laptops with OLED screens

### Theme Features

- Complete dark theme for all UI elements
- Optimized waveform visualization for dark backgrounds
- Consistent color scheme throughout the application
- All dialogs and menus match the selected theme

---

## Export Best Takes Package

Export all your Best Take recordings along with their annotations as a single ZIP file for easy archiving or sharing.

### When to Use This Feature

- **Archiving**: Create backups of your best performances
- **Sharing**: Send your best takes to band members
- **Review**: Keep a organized collection of your progress
- **Album Prep**: Gather candidate recordings for album/demo

### How to Export Best Takes Package

#### Step 1: Mark Your Best Takes

Before exporting, make sure you've marked your favorite recordings as "Best Take":

1. Go to the **Library** tab
2. Find the file you want to mark
3. Check the **Best Take** checkbox in the row
   - OR right-click the file and select "Mark as Best Take"

Repeat for all recordings you want to include in the export.

#### Step 2: Export the Package

1. **Open Export Dialog**
   - Click **File** menu
   - Select **Export Best Takes Package…**

2. **Check for Best Takes**
   - If no files are marked as Best Take, you'll see a message
   - Mark some files first, then try again

3. **Choose Save Location**
   - A file dialog will appear
   - Default filename includes:
     - Practice folder name
     - "BestTakes"
     - Current date and time
   - Example: `2024-01-Practice_BestTakes_20240115_143022.zip`
   - Choose where to save the file
   - Click **Save**

4. **Wait for Export**
   - Progress dialog shows export status
   - Each file is added to the ZIP
   - You can cancel if needed

5. **Export Complete**
   - Success message shows number of files exported
   - Package location is displayed
   - Click **OK** to finish

### What's Included in the Package

The exported ZIP file contains:

```
YourPracticeName_BestTakes_TIMESTAMP.zip
├── audio/
│   ├── 01_SongName.wav
│   ├── 02_AnotherSong.mp3
│   └── ...
├── annotations/
│   ├── .audio_notes_YourName.json
│   └── ...
└── SUMMARY.txt
```

**audio/** folder
- All audio files marked as Best Take
- Original filenames preserved
- Both WAV and MP3 formats included

**annotations/** folder
- All annotation files from the practice folder
- Includes notes from all band members
- JSON format (can be imported back into application)

**SUMMARY.txt** file
- Human-readable summary of the export
- List of all exported files
- Song names for each recording
- All annotations with timestamps
- Organized by file for easy reference

### Example SUMMARY.txt Content

```
Best Takes Export from 2024-01-Practice
Exported: 2024-01-15 14:30:22
Total files: 3

============================================================

1. 01_Recording.wav
   Song: Awesome Song Title
   Annotations:
   [Guitarist John]
     Overview: Great energy on this one
     0:45 [⏱️ Timing] Slight rush in the verse
     2:30 [🎵 Harmony] Beautiful vocal blend

2. 03_Recording.wav
   Song: Another Great Song
   ...
```

### Tips for Best Results

1. **Descriptive Names**
   - Use the "Provided Name" field to give songs descriptive titles
   - These names appear in the SUMMARY.txt file
   - Makes it easier to identify recordings later

2. **Add Annotations First**
   - Add your notes and comments before exporting
   - All annotations are included in the summary
   - Great for remembering what made each take special

3. **Regular Exports**
   - Export after each practice session
   - Build a library of your best work over time
   - Easy to track your progress

4. **File Organization**
   - Exported packages are self-contained
   - Can be shared via email, cloud storage, or USB drive
   - Recipients can read SUMMARY.txt without the application

### Sharing with Others

The exported package is perfect for sharing because:

- **No Software Required**: SUMMARY.txt can be read in any text editor
- **Standard Format**: ZIP files can be opened on any operating system
- **Audio Files Included**: Others can listen to the recordings
- **Complete Context**: Annotations provide context for each recording

### Importing Back

If you need to import the annotations back:

1. Extract the ZIP file
2. Copy the annotation files from `annotations/` folder
3. Paste them into your practice folder
4. Restart AudioBrowser or reload the folder

---

## Troubleshooting

### Dark Mode Issues

**Q: The theme didn't change after selecting Dark mode**
- A: Did you restart the application? Theme changes require a restart.

**Q: Some elements are hard to read in dark mode**
- A: Please report this as a bug! Include which specific UI element is problematic.

**Q: Can I auto-switch based on system theme?**
- A: Not yet, but this is planned for a future update.

### Export Issues

**Q: Export fails with "No Best Takes" message**
- A: Make sure you've checked the "Best Take" checkbox for at least one file in the Library tab.

**Q: Export is taking a long time**
- A: Large audio files take time to compress. The progress dialog shows status. You can cancel if needed.

**Q: Where are the exported files saved?**
- A: By default, they're saved in the parent folder of your practice folder. You can choose a different location in the save dialog.

**Q: Can I export Partial Takes too?**
- A: Not currently, but you could mark them as Best Takes temporarily for export.

**Q: The ZIP file is very large**
- A: Audio files (especially WAV) are large. Consider converting to MP3 first if file size is a concern.

---

## Additional Resources

- **UI Improvements Guide**: See [UI_IMPROVEMENTS.md](UI_IMPROVEMENTS.md) for all recent UI enhancements
- **Interface Ideas**: See [INTERFACE_IMPROVEMENT_IDEAS.md](../technical/INTERFACE_IMPROVEMENT_IDEAS.md) for planned features
- **Changelog**: See [CHANGELOG.md](../../CHANGELOG.md) for complete version history
- **Main Documentation**: See [README.md](../../README.md) for overall application documentation

---

## Feedback

If you have questions or suggestions about these features:
- Open an issue on GitHub
- Check existing documentation for answers
- Suggest improvements via pull requests

Enjoy the new features!
