# Audio Browser Performance Issues and Lessons Learned

**Date**: December 11, 2025  
**Investigation**: Performance bottlenecks and broken features in AudioBrowserOrig  
**Status**: Investigation Complete - Fixes Recommended

---

## Executive Summary

An investigation of the AudioBrowserOrig application revealed **3 performance issues** that can cause UI freezes and slowdowns. While the application has excellent error handling (as verified in previous work), certain operations perform synchronous, blocking work on the main UI thread that should be moved to background threads.

**Key Findings**:
1. **Recursive directory scanning** blocks UI when renaming songs across folders
2. **Duplicate function call** causes unnecessary file I/O on every file selection
3. **Spectrogram computation** blocks UI when enabling spectrogram view

---

## Issues Found

### Issue #1: Blocking Directory Scan During Song Rename

**Severity**: HIGH  
**Impact**: UI freeze on song rename (can last seconds to minutes with deep directory trees)

**Location**: `AudioBrowserOrig/audio_browser.py`, lines 11349, 2929

**Problem**:
When a user saves a "provided name" (song name) for a file, the application offers to propagate the rename to all other files with the same song name. To find these files, it calls `find_files_with_song_name()` which in turn calls `discover_directories_with_audio_files()` at line 2929.

```python
# Line 11349 - Called from _on_provided_name_save()
matching_files = find_files_with_song_name(self.root_path, old_name)

# Line 2929 - Inside find_files_with_song_name()
directories = discover_directories_with_audio_files(root_path)
```

**Why It's Problematic**:
The `discover_directories_with_audio_files()` function (lines 2873-2909) recursively scans the entire directory tree from root, checking every subdirectory for audio files. This is a synchronous operation on the main UI thread:

```python
def discover_directories_with_audio_files(root_path: Path) -> List[Path]:
    """Recursively discover all directories that contain audio files."""
    # ... recursive scan of entire tree ...
    for item in directory.iterdir():
        if item.is_file() and item.suffix.lower() in AUDIO_EXTS:
            has_audio_files = True
        elif item.is_dir():
            subdirectories.append(item)
    
    # Recursively scan subdirectories
    for subdir in subdirectories:
        scan_directory(subdir)  # <-- Blocks UI
```

**User Impact**:
- Application becomes **completely unresponsive** while scanning
- No visual feedback to user that operation is in progress
- On deep directory trees (e.g., hundreds of practice session folders), this can take **10-30 seconds or more**
- User may think application has crashed

**Recommended Fix**:
1. Move the directory scanning to a background thread using QThread
2. Show a progress dialog with "Searching for files..." message
3. Cache the results of directory scans and invalidate cache only when filesystem changes are detected
4. Consider limiting the scan depth or providing a user setting for search scope

---

### Issue #2: Duplicate Function Call on File Selection

**Severity**: MEDIUM  
**Impact**: Unnecessary file I/O on every file selection (minor slowdown, wasted resources)

**Location**: `AudioBrowserOrig/audio_browser.py`, lines 9721 and 9724

**Problem**:
In the `_deferred_annotation_load()` method, `_load_loop_markers()` is called **twice**:

```python
def _deferred_annotation_load(self):
    """Load annotations and waveform data after a brief delay."""
    if self.current_audio_file:
        self._load_annotations_for_current()
        # ... other loading operations ...
        self._load_loop_markers()  # Load loop markers for this file (line 9721)
        self._update_waveform_tempo()
        self._update_waveform_annotations()
        self._load_loop_markers()  # Load loop markers AGAIN (line 9724)
```

**Why It's Problematic**:
The `_load_loop_markers()` method (lines 11807-11831) reads from disk:
```python
def _load_loop_markers(self):
    # Load loop markers metadata
    loop_json_path = self._loop_markers_json_path()
    metadata = load_json(loop_json_path, {})  # <-- File I/O
    # ... process metadata ...
    self._update_loop_markers_on_waveform()  # <-- Triggers widget update
```

**User Impact**:
- Performs duplicate file I/O operation on every file selection
- Triggers unnecessary widget redraws
- Minor performance impact individually, but multiplied across many file selections
- Wastes CPU and disk I/O resources

**Recommended Fix**:
Remove one of the duplicate calls (line 9724 appears to be the redundant one):

```python
def _deferred_annotation_load(self):
    """Load annotations and waveform data after a brief delay."""
    if self.current_audio_file:
        self._load_annotations_for_current()
        # ... other loading operations ...
        self._load_loop_markers()
        self._update_waveform_tempo()
        self._update_waveform_annotations()
        # REMOVED: self._load_loop_markers()  # Duplicate call removed
```

---

### Issue #3: Blocking Spectrogram Computation

**Severity**: HIGH  
**Impact**: UI freeze when enabling spectrogram view (can last several seconds for long files)

**Location**: `AudioBrowserOrig/audio_browser.py`, lines 4330-4332

**Problem**:
When the user toggles spectrogram mode, `_compute_spectrogram()` is called immediately on the main thread:

```python
def set_spectrogram_mode(self, enabled: bool):
    """Toggle spectrogram view mode."""
    if self._show_spectrogram == enabled:
        return
    
    self._show_spectrogram = enabled
    
    # If enabled and we have audio data, compute spectrogram
    if enabled and self._path and self._path.exists() and self._peaks:
        self._compute_spectrogram()  # <-- BLOCKS UI
    
    # Force redraw
    self._pixmap = None
    self.update()
```

**Why It's Problematic**:
The `_compute_spectrogram()` method (lines 4338-4450) performs expensive operations synchronously:

1. **Loads entire audio file into memory**:
```python
with wave.open(str(self._path), 'rb') as wf:
    sample_rate = wf.getframerate()
    n_frames = wf.getnframes()
    frames = wf.readframes(n_frames)  # <-- Loads entire file
    arr = np.frombuffer(frames, dtype=np.int16)
```

2. **Performs FFT analysis** on entire audio:
```python
# STFT parameters
n_fft = 2048
hop_length = n_fft // 4

# Compute spectrogram using NumPy FFT
for i in range(0, len(samples) - n_fft, hop_length):
    window = samples[i:i+n_fft]
    # ... FFT computation ...  # <-- CPU intensive
```

**User Impact**:
- Application **freezes completely** while computing spectrogram
- No progress indication or cancel option
- For a 5-minute WAV file: can take **5-15 seconds** depending on CPU
- User has no feedback that operation is in progress

**Recommended Fix**:
1. Move spectrogram computation to a background thread (similar to waveform generation)
2. Show "Computing spectrogram..." message and progress indicator
3. Allow user to cancel the operation
4. Cache the spectrogram data in the waveform cache file for reuse
5. Consider computing spectrogram progressively (show partial result as it computes)

Example pattern to follow (already used for waveform generation):
```python
def set_spectrogram_mode(self, enabled: bool):
    """Toggle spectrogram view mode."""
    if enabled and self._path:
        # Start background computation
        self._state = "computing_spectrogram"
        self._msg = "Computing spectrogram…"
        self.update()
        
        # Create worker thread (similar to WaveformWorker)
        thread = QThread(self)
        worker = SpectrogramWorker(str(self._path), ...)
        worker.moveToThread(thread)
        # ... connect signals ...
        thread.start()
```

---

## What Was Already Working Well

The investigation also revealed several areas where the application demonstrates **excellent practices**:

### 1. ✅ Waveform Generation (Already Threaded)
- Lines 4563-4580: Waveform generation uses QThread properly
- Progressive drawing shows partial results as they compute
- Cached results avoid redundant computation
- **Pattern to emulate for Issue #3**

### 2. ✅ Error Handling (Already Robust)
- Previous investigation (PR #364) verified comprehensive error handling
- All JSON loading operations protected with try/except
- Division by zero protection in place
- File operations use proper context managers

### 3. ✅ Optimization Checks
- Line 8733: Checks if file actually changed before expensive operations
- Line 6829: Checks if folder changed before reloading metadata
- Caching used throughout (waveforms, durations, fingerprints)

### 4. ✅ Deferred Loading
- Line 9700: Uses QTimer.singleShot for deferred annotation loading
- Improves perceived responsiveness by not blocking initial file selection

---

## Lessons Learned: Best Practices for Future Development

### 1. **Always Use Background Threads for Potentially Long Operations**

**Rule**: Any operation that could take more than **100ms** should run in a background thread.

**Examples of operations that need threading**:
- ❌ Recursive directory scanning (Issue #1)
- ❌ Spectrogram computation (Issue #3)
- ❌ Large file I/O operations
- ❌ FFT analysis or signal processing
- ❌ Network requests
- ❌ Database queries on large datasets
- ✅ Waveform generation (already uses QThread correctly)

**Qt Threading Pattern** (already used in the codebase for waveforms):
```python
# 1. Create QThread and worker
thread = QThread(self)
worker = MyWorker(params)
worker.moveToThread(thread)

# 2. Connect signals
thread.started.connect(worker.run)
worker.progress.connect(self._on_progress)
worker.finished.connect(self._on_finished)

# 3. Start thread
thread.start()
```

### 2. **Always Provide Visual Feedback for Long Operations**

**Rule**: If an operation takes longer than **200ms**, show a progress indicator or message.

**Options for feedback**:
- Status bar messages: `self.statusBar().showMessage("Processing...")`
- Progress dialogs: `QProgressDialog` for operations with known duration
- Progress indicators in status bar (already implemented: `_show_progress()`)
- Cursor change: `QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)`
- Disable/gray out UI controls during operation

**Bad**: Silent operation with frozen UI (Issues #1, #3)  
**Good**: "Searching for files..." dialog with progress bar

### 3. **Cache Results of Expensive Operations**

**Rule**: If the same computation might be repeated, cache the results.

**Already implemented well in the codebase**:
- ✅ Waveform data cached in `.waveform_cache_*.json`
- ✅ Duration data cached in `.duration_cache.json`
- ✅ Fingerprint data cached in `.audio_fingerprints.json`

**Should also be cached**:
- ❌ Directory tree structure (Issue #1)
- ❌ Spectrogram data (Issue #3)

**Cache invalidation strategies**:
- File modification time (mtime) comparison
- File size comparison
- Explicit cache clearing on user request
- Filesystem watcher for automatic invalidation

### 4. **Avoid Duplicate Work**

**Rule**: Profile code paths to find duplicate operations, especially I/O.

**Issue #2 Example**: Duplicate `_load_loop_markers()` call
- Could have been caught with code review
- Could have been caught with logging/profiling
- Small individual impact, but multiplies across many operations

**Prevention strategies**:
- Code review checklists
- Unit tests that verify operations occur only once
- Logging to detect duplicate operations during testing
- Performance profiling during development

### 5. **Use Filesystem Watchers Instead of Polling or Full Scans**

**Rule**: When monitoring for changes, use OS-level file watchers, not directory scans.

**Current implementation**:
- Line 6860: `_update_watched_files()` - already uses QFileSystemWatcher
- ✅ Good practice for detecting changes in current folder

**Improvement for Issue #1**:
- Instead of scanning entire tree on every rename, maintain a cache
- Use file watcher to detect when folders are added/removed
- Only rescan changed portions of the tree

### 6. **Implement Cancellation for Long Operations**

**Rule**: Give users a way to cancel operations that might take a long time.

**Pattern**:
```python
class LongRunningWorker(QObject):
    def __init__(self):
        self._cancel_requested = False
    
    def cancel(self):
        self._cancel_requested = True
    
    def run(self):
        for item in items:
            if self._cancel_requested:
                self.finished.emit(False)  # Emit canceled status
                return
            # ... process item ...
```

**UI Pattern**:
- Progress dialog with Cancel button
- Store reference to worker and call `worker.cancel()` on button click

### 7. **Consider Progressive/Incremental Results**

**Rule**: For operations with many items, show results as they arrive.

**Already implemented well**:
- ✅ Waveform generation shows partial waveform as it computes (line 4671)
- ✅ Auto-generation shows progress per file (line 16009-16013)

**Could apply to Issue #1**:
- Show "Found 15 files so far..." as search progresses
- Allow user to see and select from partial results
- Continue searching in background

### 8. **Test with Large Datasets**

**Rule**: Always test with realistic large datasets, not just small test files.

**Scenarios to test**:
- ❌ Deep directory trees (100+ folders)
- ❌ Large audio files (10+ minutes, high quality)
- ❌ Thousands of audio files in one folder
- ❌ Slow network drives or external drives
- ❌ Low-end hardware (old CPU, limited RAM)

**Performance budgets** (suggested targets):
- File selection to playback start: **< 200ms**
- Folder change operation: **< 500ms**
- Waveform generation (cached): **< 50ms**
- Waveform generation (from scratch): **< 5 seconds** (with progress shown)
- UI responsiveness during any operation: **< 100ms frame time**

### 9. **Use Profiling Tools to Find Bottlenecks**

**Tools for Python/Qt performance analysis**:
- `cProfile`: Built-in Python profiler
- `line_profiler`: Line-by-line profiling
- `py-spy`: Sampling profiler (low overhead)
- Qt Creator's performance analyzer
- Manual timing with `time.time()` or `QElapsedTimer`

**Example profiling code**:
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
# ... code to profile ...
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
```

### 10. **Code Review Checklist for Performance**

**Questions to ask during code review**:
- [ ] Could this operation take more than 100ms?
- [ ] Is this operation running on the main UI thread?
- [ ] Could this be triggered repeatedly (in a loop or event handler)?
- [ ] Is there visual feedback if the operation is slow?
- [ ] Can the user cancel if needed?
- [ ] Are results cached to avoid redundant work?
- [ ] Have we tested with large datasets?
- [ ] Are there any duplicate operations?

---

## Priority Recommendations

### High Priority (Fix Immediately)

1. **Issue #3 - Spectrogram blocking** (Lines 4330-4332)
   - **Reason**: Causes multi-second UI freeze on every spectrogram toggle
   - **Estimated fix time**: 2-3 hours
   - **User-visible impact**: Very high

2. **Issue #1 - Directory scan blocking** (Lines 11349, 2929)
   - **Reason**: Can cause 10-30 second UI freeze on song rename
   - **Estimated fix time**: 3-4 hours (threading + caching)
   - **User-visible impact**: Very high

### Medium Priority (Fix Soon)

3. **Issue #2 - Duplicate function call** (Lines 9721, 9724)
   - **Reason**: Wastes resources on every file selection
   - **Estimated fix time**: 5 minutes
   - **User-visible impact**: Low (but easy fix)

### Future Improvements

4. **Add performance monitoring**
   - Log operation times during development
   - Add performance tests to CI/CD
   - Monitor real-world usage patterns

5. **Implement comprehensive caching strategy**
   - Cache directory structure
   - Cache spectrogram data
   - Implement cache invalidation

---

## Testing Checklist

After fixes are implemented, test these scenarios:

### Scenario 1: Large Directory Tree
- [ ] Create folder structure with 100+ subdirectories
- [ ] Rename a song that appears in multiple folders
- [ ] Verify UI remains responsive
- [ ] Verify progress indication is shown
- [ ] Time operation: should complete search in < 5 seconds with caching

### Scenario 2: Large Audio Files
- [ ] Load 10-minute WAV file
- [ ] Toggle spectrogram view
- [ ] Verify UI remains responsive
- [ ] Verify progress indication is shown
- [ ] Verify can cancel operation
- [ ] Time operation: should complete in < 10 seconds

### Scenario 3: Rapid File Selection
- [ ] Rapidly click through 20+ files
- [ ] Verify no duplicate operations (check logs)
- [ ] Verify smooth playback transition
- [ ] Monitor memory usage (no leaks)

### Scenario 4: Slow Storage
- [ ] Use folder on network drive or USB 2.0 drive
- [ ] Perform all operations above
- [ ] Verify UI remains responsive even with slow I/O

---

## Conclusion

The AudioBrowserOrig application demonstrates excellent error handling and many good practices (threaded waveform generation, deferred loading, caching). However, three specific issues cause UI blocking:

1. **Recursive directory scanning** during song rename
2. **Duplicate function call** on file selection  
3. **Synchronous spectrogram computation**

These issues share a common pattern: **synchronous, potentially long-running operations on the main UI thread**. The fixes all follow the same pattern: **move work to background threads and provide visual feedback**.

By following the lessons learned in this document, future development can avoid these types of issues:
- Always thread long operations
- Always provide visual feedback
- Cache expensive computations
- Avoid duplicate work
- Test with large datasets
- Use profiling tools

---

**Document Version**: 1.0  
**Author**: Code Review Agent  
**Date**: December 11, 2025
