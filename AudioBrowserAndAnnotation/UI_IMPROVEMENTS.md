# UI Improvements Guide

This document describes recent user interface improvements to the AudioBrowser application for easier workflow management.

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
- Settings are saved immediately when you click OK

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
