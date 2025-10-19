# Hidden Songs File Tree Filter Fix

## Issue
Hidden songs were not being filtered out from the song explorer (file tree) on the left side of AudioBrowserOrig, even though the "Show Hidden Songs" toggle existed and the feature worked elsewhere in the application.

## Root Cause
The hidden song filtering was only implemented in the `_list_audio_in_current_dir()` method, which is used by some parts of the application but not by the file tree display. The file tree uses `FileInfoProxyModel.filterAcceptsRow()` for filtering, which had filters for directories like `.backup`, `.waveforms`, etc., and text filtering, but did not check for hidden songs.

## Solution
Added hidden song filtering to the `FileInfoProxyModel` class to ensure the file tree respects the hidden songs setting.

### Changes Made

#### 1. Added `_is_file_hidden()` Method
```python
def _is_file_hidden(self, filename: str) -> bool:
    """Check if a file is marked as hidden in the current annotation set."""
    try:
        if not hasattr(self.audio_browser, 'file_hidden_songs'):
            return False
        return self.audio_browser.file_hidden_songs.get(filename, False)
    except Exception:
        return False
```

This method follows the same pattern as the existing `_is_file_best_take()` and `_is_file_partial_take()` methods, checking the audio browser's `file_hidden_songs` dictionary for the current annotation set.

#### 2. Updated `filterAcceptsRow()` Method
Added logic to filter out hidden audio files when `show_hidden_songs` is False:

```python
# Filter out hidden songs unless show_hidden_songs is enabled
if not file_info.isDir() and f".{file_info.suffix().lower()}" in AUDIO_EXTS:
    filename = file_info.fileName()
    if hasattr(self.audio_browser, 'show_hidden_songs') and not self.audio_browser.show_hidden_songs:
        if self._is_file_hidden(filename):
            return False
```

This ensures that:
- Only audio files are checked (directories are not affected)
- Hidden songs are only filtered when `show_hidden_songs` is False
- The filter gracefully handles cases where the audio browser hasn't initialized the hidden songs data yet

#### 3. Added Filter Invalidation Calls
Added `self.file_proxy.invalidateFilter()` calls in key methods to ensure the filter is re-evaluated when needed:

**In `_toggle_show_hidden_songs()`:**
```python
def _toggle_show_hidden_songs(self):
    """Toggle the visibility of hidden songs."""
    self.show_hidden_songs = self.show_hidden_songs_action.isChecked()
    
    # Refresh the file list and tree to apply the filter
    self._refresh_right_table()
    self.file_proxy.invalidateFilter()  # Re-evaluate filter to show/hide hidden songs
    self._refresh_tree_display()
```

**In `_toggle_hidden_song_for_file()`:**
```python
# Refresh UI to reflect hidden status (will filter out if not showing hidden)
self._refresh_right_table()
self.file_proxy.invalidateFilter()  # Re-evaluate filter to show/hide the file
self._refresh_tree_display()
```

**In `_on_set_combo_changed()`:**
```python
# Refresh tree display to show best take/partial take formatting and hidden songs for the new set
self.file_proxy.invalidateFilter()  # Re-evaluate filter with new set's hidden songs
self._refresh_tree_display()
```

**In `_save_root()`:**
```python
self._refresh_important_table()
self._refresh_annotation_legend()
self._update_fingerprint_ui()
self.file_proxy.invalidateFilter()  # Re-evaluate filter with newly loaded hidden songs
self.waveform.clear()
```

## Testing

### Automated Tests
Created a static code analysis test that verifies:
- ✓ `_is_file_hidden()` method exists and references `file_hidden_songs`
- ✓ `filterAcceptsRow()` filters hidden songs when `show_hidden_songs` is False
- ✓ All relevant methods call `invalidateFilter()` to refresh the tree

All tests passed successfully.

### Manual Testing Checklist
To fully verify the fix, perform these manual tests:

1. **Basic Hide/Unhide Test**
   - [ ] Open AudioBrowserOrig
   - [ ] Right-click a file in the tree and select "🚫 Hide Song"
   - [ ] Verify the file disappears from the tree
   - [ ] Enable "View > Show Hidden Songs"
   - [ ] Verify the file reappears in the tree
   - [ ] Right-click the file and select "👁 Unhide Song"
   - [ ] Verify the file remains visible
   - [ ] Disable "View > Show Hidden Songs"
   - [ ] Verify the file is still visible (not hidden anymore)

2. **Annotation Set Switching Test**
   - [ ] Hide a file in annotation set A
   - [ ] Switch to annotation set B
   - [ ] Verify the file is visible in set B (hidden status is per-set)
   - [ ] Switch back to set A
   - [ ] Verify the file is hidden again in set A

3. **Folder Navigation Test**
   - [ ] Hide a file in folder A
   - [ ] Navigate to folder B
   - [ ] Navigate back to folder A
   - [ ] Verify the file is still hidden in folder A

4. **Persistence Test**
   - [ ] Hide several files
   - [ ] Close the application
   - [ ] Reopen the application
   - [ ] Navigate to the same folder
   - [ ] Verify the files are still hidden

5. **Filter Interaction Test**
   - [ ] Hide a file
   - [ ] Use the text filter to search for the hidden file
   - [ ] Verify the file does not appear (hidden files are excluded from search)
   - [ ] Enable "Show Hidden Songs"
   - [ ] Verify the file now appears in search results

## Benefits
- **Consistent Behavior**: Hidden songs are now filtered consistently across all parts of the application
- **User Experience**: Users can now properly hide unwanted files from the file tree
- **Minimal Changes**: The fix follows existing patterns in the codebase (similar to best take/partial take filtering)
- **No Breaking Changes**: The fix is backward compatible and doesn't affect existing functionality

## Implementation Details

### Filter Order
The filters in `filterAcceptsRow()` are applied in this order:
1. Directory filters (hide `.backup*`, `.waveforms`, `.audiobrowser_temp`)
2. Text filter (for search functionality)
3. Hidden songs filter (new)

This ensures that hidden songs filtering doesn't interfere with other filters.

### Performance Considerations
- The `_is_file_hidden()` method is efficient, using a dictionary lookup
- Filter invalidation is called only when necessary (when hidden songs data changes)
- The implementation follows the same pattern as existing filters, ensuring consistency

### Compatibility
- Works with existing annotation sets (hidden songs are optional)
- Gracefully handles cases where hidden songs data is not yet loaded
- No changes to data storage format or structure

## Files Modified
- `AudioBrowserAndAnnotation/AudioBrowserOrig/audio_browser.py` (+23 lines, -3 lines)

## Related Documentation
- See `HIDDEN_SONG_IMPLEMENTATION.md` for the original hidden songs feature documentation
- See `HIDDEN_SONG_UI_GUIDE.md` for user-facing documentation on the hidden songs feature
