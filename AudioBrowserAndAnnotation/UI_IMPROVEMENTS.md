# UI Improvements Guide

This document describes recent user interface improvements to the AudioBrowser application for easier workflow management.

## Dark Mode Theme

**Location**: File menu → Preferences → Theme

The application now supports both light and dark color themes:

### How to Use
1. Open the **File** menu
2. Select **Preferences…**
3. In the Theme dropdown, select either **Light** or **Dark**
4. Click **OK**
5. Restart the application for the theme to take effect

### Features
- Full dark theme for all UI elements, menus, and dialogs
- Optimized waveform colors for dark mode visibility
- Comfortable viewing in low-light environments
- Reduces eye strain during extended practice review sessions
- Theme preference persists across application restarts

### Why This Helps
- Better visibility when working at night or in dimly lit rooms
- Reduces eye fatigue during long review sessions
- Modern interface option preferred by many users
- Matches your system theme preference

---

## Export Best Takes Package

**Location**: File menu → Export Best Takes Package…

Export all your Best Take files along with their annotations to a single ZIP package:

### How to Use
1. Mark your favorite recordings as "Best Take" in the Library tab
2. Open the **File** menu
3. Select **Export Best Takes Package…**
4. Choose where to save the ZIP file
5. Click **Save** and wait for the export to complete

### What Gets Exported
The ZIP package includes:
- **audio/** folder - All Best Take audio files (WAV/MP3)
- **annotations/** folder - All annotation files for those recordings
- **SUMMARY.txt** - Complete summary with:
  - List of all exported files
  - Song names for each file
  - All annotations with timestamps and categories
  - Formatted for easy reading

### Features
- Progress dialog shows export status
- Timestamped filename includes practice folder name
- Organized folder structure for easy navigation
- Complete snapshot of your best performances

### Why This Helps
- Easy archiving of your best recordings
- Share your best takes with band members
- Create backups of important recordings
- Prepare for album/demo compilation
- Export practice progress for review

---

## Recent Folders Menu

**Location**: File menu → Recent Folders

The Recent Folders feature provides quick access to your most recently opened practice folders:

### How to Use
1. Open the **File** menu
2. Select **Recent Folders** to see a submenu
3. Click on any folder name to instantly switch to that practice folder
4. Hover over a folder name to see its full path in the tooltip

### Features
- Remembers up to 10 most recently opened folders
- Automatically removes folders that no longer exist
- "Clear Recent Folders" option to reset the list
- Folders are ordered with most recent first

### Why This Helps
- No more navigating through multiple directory dialogs
- Quick switching between current and previous practice sessions
- Speeds up weekly review workflow when comparing recent practices

---

## Preferences Dialog

**Location**: File menu → Preferences

The Preferences dialog consolidates application settings in one convenient location:

### Current Settings

#### Undo Limit
- **Range**: 10 to 1000 operations
- **Default**: 100 operations
- **Purpose**: Controls how many undo operations are kept in history
- **Impact**: Higher values use more memory but provide more undo capability

#### Theme
- **Options**: Light or Dark
- **Default**: Light
- **Purpose**: Controls the color scheme of the application
- **Impact**: Requires application restart to take effect

### How to Use
1. Open the **File** menu
2. Select **Preferences...**
3. Adjust settings as desired
4. Click **OK** to save (or **Cancel** to discard changes)

### Benefits
- Cleaner toolbar (undo limit spinner removed from toolbar)
- Centralized location for application preferences
- Easy to find and adjust settings
- Changes apply immediately and persist across sessions

---

## Toolbar Simplification

The main toolbar has been simplified to reduce clutter:

### What Changed
- **Removed**: Undo limit spinner (moved to Preferences dialog)
- **Kept**: Essential controls only
  - Undo/Redo buttons
  - Up navigation button
  - Auto-switch to Annotations checkbox
  - Sync button

### Benefits
- Less visual clutter
- More space for content
- Easier to focus on essential operations
- Settings accessible when needed via Preferences dialog

---

## Tips for Best Experience

### Recent Folders
- Use descriptive folder names for easy identification in the menu
- The most recently opened folder is always at the top of the list
- Recent folders persist between application sessions

### Preferences
- Adjust undo limit based on your workflow:
  - **Lower values (10-50)**: For lighter weight operation with less memory usage
  - **Medium values (50-200)**: Balanced approach for typical usage
  - **Higher values (200-1000)**: For complex editing sessions with extensive changes
- Choose theme based on your environment:
  - **Light theme**: Better for bright environments, traditional interface
  - **Dark theme**: Better for low-light conditions, reduces eye strain
- Settings are saved immediately when you click OK
- Theme changes require application restart to take effect

### Best Takes Export
- Export Best Takes Package regularly to create backups of your best recordings
- Use descriptive folder names so exported packages are easy to identify
- The SUMMARY.txt file in the export makes it easy to review what's included
- Share packages with band members who don't have the application installed

### Keyboard Shortcuts
Many operations have keyboard shortcuts for even faster workflow. See **Help → Keyboard Shortcuts** for a complete list.

---

## Related Documentation

- [INTERFACE_IMPROVEMENT_IDEAS.md](INTERFACE_IMPROVEMENT_IDEAS.md) - All planned and implemented interface improvements
- [CHANGELOG.md](CHANGELOG.md) - Complete version history with all changes
- [README.md](README.md) - Main application documentation
- [PRACTICE_STATISTICS.md](PRACTICE_STATISTICS.md) - Practice analytics and tracking features

---

**Questions or Suggestions?**
Open an issue on GitHub or check the main README for more information.
