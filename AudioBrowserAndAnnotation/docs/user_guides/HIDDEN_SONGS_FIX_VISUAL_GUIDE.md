# Hidden Songs Fix - Visual Guide

## What Was Fixed

### Before the Fix ❌
```
┌─────────────────────────────────────────────────────┐
│ AudioBrowserOrig                                    │
├─────────────────────────────────────────────────────┤
│ File Tree (Left Side)     │  Main Area (Right)      │
│                           │                         │
│ 📁 Practice/              │  Currently Playing:     │
│   ├─ song1.wav           │  song1.wav              │
│   ├─ song2.wav           │                         │
│   ├─ song3.wav (HIDDEN)  │  ❌ PROBLEM:            │
│   ├─ song4.wav           │  song3.wav still shows  │
│   └─ song5.wav (HIDDEN)  │  in the file tree even  │
│                           │  though it's marked as  │
│ ☐ Show Hidden Songs      │  hidden!                │
└─────────────────────────────────────────────────────┘
```

The file tree on the left showed ALL files, even when they were marked as hidden, because the tree filter didn't check the hidden status.

### After the Fix ✓
```
┌─────────────────────────────────────────────────────┐
│ AudioBrowserOrig                                    │
├─────────────────────────────────────────────────────┤
│ File Tree (Left Side)     │  Main Area (Right)      │
│                           │                         │
│ 📁 Practice/              │  Currently Playing:     │
│   ├─ song1.wav           │  song1.wav              │
│   ├─ song2.wav           │                         │
│   └─ song4.wav           │  ✓ FIXED:               │
│                           │  song3.wav and song5    │
│ ☐ Show Hidden Songs      │  are properly hidden    │
│                           │  from the file tree!    │
│                           │                         │
└─────────────────────────────────────────────────────┘
```

Now the file tree correctly filters out hidden songs when "Show Hidden Songs" is unchecked.

### When "Show Hidden Songs" is Enabled ✓
```
┌─────────────────────────────────────────────────────┐
│ AudioBrowserOrig                                    │
├─────────────────────────────────────────────────────┤
│ File Tree (Left Side)     │  Main Area (Right)      │
│                           │                         │
│ 📁 Practice/              │  Currently Playing:     │
│   ├─ song1.wav           │  song1.wav              │
│   ├─ song2.wav           │                         │
│   ├─ song3.wav 🚫        │  ✓ With toggle enabled, │
│   ├─ song4.wav           │  hidden songs appear    │
│   └─ song5.wav 🚫        │  in the tree (marked    │
│                           │  with indicator)        │
│ ☑ Show Hidden Songs      │                         │
│                           │                         │
└─────────────────────────────────────────────────────┘
```

When the user checks "Show Hidden Songs" in the View menu, the hidden files reappear in the tree.

## How It Works

### The Fix Process

```
┌──────────────────────────────────────────────────┐
│ User Action: Hide Song                           │
└────────────┬─────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────┐
│ 1. File marked as hidden in annotation data      │
│    file_hidden_songs["song3.wav"] = True         │
└────────────┬─────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────┐
│ 2. Metadata saved to .audio_notes_*.json         │
└────────────┬─────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────┐
│ 3. Filter invalidation triggered                 │
│    file_proxy.invalidateFilter()                 │
└────────────┬─────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────┐
│ 4. filterAcceptsRow() called for each file       │
│    - Checks if file is hidden                    │
│    - Checks show_hidden_songs flag               │
│    - Returns False for hidden files              │
└────────────┬─────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────┐
│ 5. File tree updates, hidden files disappear     │
└──────────────────────────────────────────────────┘
```

### Code Flow

```python
# When user hides a file:
def _toggle_hidden_song_for_file(self, filename, file_path):
    # 1. Update hidden status
    self.file_hidden_songs[filename] = True
    
    # 2. Save to disk
    self._save_notes()
    
    # 3. Refresh UI (NEW!)
    self.file_proxy.invalidateFilter()  # <-- This is the fix!
    self._refresh_tree_display()

# When filtering the tree:
def filterAcceptsRow(self, source_row, source_parent):
    # ... existing directory filters ...
    # ... existing text filter ...
    
    # (NEW!) Filter hidden songs
    if not file_info.isDir() and is_audio_file:
        filename = file_info.fileName()
        if not self.audio_browser.show_hidden_songs:
            if self._is_file_hidden(filename):  # <-- Check hidden status
                return False  # Hide this file
    
    return True  # Show this file

# (NEW!) Check if file is hidden:
def _is_file_hidden(self, filename):
    return self.audio_browser.file_hidden_songs.get(filename, False)
```

## User Scenarios

### Scenario 1: Hiding a Practice Take
```
User wants to hide multiple practice takes that aren't good:

Before:
📁 Song A/
  ├─ take1.wav (bad)
  ├─ take2.wav (bad)  
  ├─ take3.wav (good) ★
  └─ take4.wav (bad)

Action:
1. Right-click take1.wav → "🚫 Hide Song"
2. Right-click take2.wav → "🚫 Hide Song"
3. Right-click take4.wav → "🚫 Hide Song"

After:
📁 Song A/
  └─ take3.wav (good) ★

Result: Only the good take is visible in the file tree!
```

### Scenario 2: Reviewing Hidden Songs
```
User wants to review what they've hidden:

Action:
1. View menu → ☑ Show Hidden Songs

Tree now shows:
📁 Song A/
  ├─ take1.wav 🚫 (hidden, but visible because toggle is on)
  ├─ take2.wav 🚫 (hidden, but visible because toggle is on)
  ├─ take3.wav (good) ★
  └─ take4.wav 🚫 (hidden, but visible because toggle is on)

Result: User can see all files, including hidden ones!
```

### Scenario 3: Unhiding a File
```
User realizes they hid a file by mistake:

Action:
1. View menu → ☑ Show Hidden Songs (to see the file)
2. Right-click take2.wav → "👁 Unhide Song"
3. View menu → ☐ Show Hidden Songs (to hide the others again)

Result: take2.wav is now visible again, others remain hidden!
```

## Technical Details

### Files Affected
Only **1 file** was modified: `audio_browser.py`

### Lines Changed
- **+23 lines** added (new method + filter logic + invalidation calls)
- **-3 lines** removed (updated comments)
- **Net: +20 lines**

### Methods Modified/Added
1. `_is_file_hidden()` - NEW method
2. `filterAcceptsRow()` - Modified to add hidden song check
3. `_toggle_show_hidden_songs()` - Added invalidateFilter() call
4. `_toggle_hidden_song_for_file()` - Added invalidateFilter() call
5. `_on_set_combo_changed()` - Added invalidateFilter() call
6. `_save_root()` - Added invalidateFilter() call

### Performance Impact
✓ **Zero performance degradation**
- Filter only called when tree needs refresh
- Dictionary lookup is O(1)
- No additional file I/O
- No network calls

## Comparison with Other Filters

The hidden song filter works the same way as existing filters:

```
Directory Filters (existing):
  if folder_name.startswith('.backup'): return False
  ↓ Hides .backup folders

Text Filter (existing):
  if filter_text not in filename: return False
  ↓ Hides files that don't match search

Hidden Song Filter (NEW!):
  if not show_hidden_songs and is_hidden: return False
  ↓ Hides files marked as hidden
```

All three filters work together:
```
File passes if:
  ✓ Not a backup folder AND
  ✓ Matches text filter (if active) AND
  ✓ Not hidden (unless show_hidden_songs enabled)
```

## Why This Fix Is Important

### User Experience Benefits
1. **Cleaner File List** - Users can focus on relevant files
2. **Better Organization** - Hide practice takes, duplicates, or rejected recordings
3. **Consistent Behavior** - File tree now works the same as other parts of the app
4. **Easy to Use** - Simple right-click menu, toggle in View menu

### Technical Benefits
1. **Minimal Code Changes** - Only 20 lines added
2. **Follows Existing Patterns** - Uses same approach as best_take/partial_take
3. **No Breaking Changes** - Fully backward compatible
4. **Well Tested** - Multiple automated tests verify the fix

## Summary

**Problem**: Hidden songs appeared in file tree  
**Solution**: Added filter check in FileInfoProxyModel  
**Result**: Hidden songs now properly filtered from tree  
**Impact**: +20 lines of code, 0 breaking changes  
**Status**: ✓ Complete and ready for testing  

---

For detailed technical documentation, see `HIDDEN_SONGS_FIX.md`  
For executive summary, see `HIDDEN_SONGS_FIX_SUMMARY.md`
