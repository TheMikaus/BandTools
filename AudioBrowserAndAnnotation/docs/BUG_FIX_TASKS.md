# AudioBrowser Bug Fix Tasks

**Date**: December 2025  
**Status**: Pending Review  
**Reference**: See [BUG_ANALYSIS_COMPREHENSIVE.md](BUG_ANALYSIS_COMPREHENSIVE.md) for detailed analysis

## Overview

This document provides a prioritized task list for fixing bugs in both AudioBrowser versions that may prevent core features from working properly.

---

## Task Summary

| Priority | Tasks | Estimated Time | Status |
|----------|-------|----------------|--------|
| P0 (Critical) | 4 | 1-2 hours | ⬜ Not Started |
| P1 (High) | 2 | 2-3 hours | ⬜ Not Started |
| P2 (Medium) | 10 | 4-6 hours | ⬜ Not Started |
| **Total** | **16** | **7-11 hours** | |

---

## P0 - CRITICAL TASKS (Must Fix Immediately)

These bugs cause crashes that prevent basic application functionality. Users cannot load folders or browse files.

### Task 1: Fix JSON Loading in AudioBrowserOrig Provided Names
**Priority**: P0 - CRITICAL  
**Severity**: HIGH  
**Estimated Time**: 15 minutes  

**File**: `AudioBrowserOrig/audio_browser.py`, Line 699  
**Core Feature**: File Library, Batch Rename  
**Issue**: Application crashes when loading corrupted `.provided_names.json` file

**Fix**:
```python
# Before (Line 699)
provided_names = json.load(f)

# After
try:
    provided_names = json.load(f)
except (json.JSONDecodeError, ValueError) as e:
    logger.error(f"Failed to load provided names: {e}")
    provided_names = {}
```

**Test**:
1. Create corrupted `.provided_names.json` in a test folder
2. Try to load the folder
3. Verify: Application continues with empty provided names, logs error

---

### Task 2: Fix JSON Loading in AudioBrowserOrig Duration Cache
**Priority**: P0 - CRITICAL  
**Severity**: HIGH  
**Estimated Time**: 15 minutes  

**File**: `AudioBrowserOrig/audio_browser.py`, Line 1207  
**Core Feature**: File Library, Duration Display  
**Issue**: Application crashes when loading corrupted `.duration_cache.json` file

**Fix**:
```python
# Before (Line 1207)
duration_cache = json.load(f)

# After
try:
    duration_cache = json.load(f)
except (json.JSONDecodeError, ValueError) as e:
    logger.error(f"Failed to load duration cache: {e}")
    duration_cache = {}
```

**Test**:
1. Create corrupted `.duration_cache.json` in a test folder
2. Try to load the folder
3. Verify: Application continues, durations are recalculated

---

### Task 3: Fix JSON Loading in AudioBrowser-QML Tempo Metadata
**Priority**: P0 - CRITICAL  
**Severity**: HIGH  
**Estimated Time**: 15 minutes  

**File**: `AudioBrowser-QML/backend/file_manager.py`, Line 741  
**Core Feature**: Tempo/BPM Display, File Loading  
**Issue**: Application crashes when loading corrupted `.tempo.json` file

**Fix**:
```python
# Before (Line 741)
tempo_data = json.load(f)

# After
try:
    tempo_data = json.load(f)
except (json.JSONDecodeError, ValueError) as e:
    logger.error(f"Failed to load tempo data: {e}")
    tempo_data = {}
```

**Test**:
1. Create corrupted `.tempo.json` in a test folder
2. Try to load the folder with QML version
3. Verify: Application continues, tempo data is empty

---

### Task 4: Fix Division by Zero in AudioBrowser-QML Duration Calculation
**Priority**: P0 - CRITICAL  
**Severity**: HIGH  
**Estimated Time**: 15 minutes  

**File**: `AudioBrowser-QML/backend/file_manager.py`, Line 681  
**Core Feature**: File Library, Duration Display  
**Issue**: Crash when processing audio files with zero sample rate

**Fix**:
```python
# Before (Line 681)
duration_ms = int((frames / rate) * 1000)

# After
if rate > 0:
    duration_ms = int((frames / rate) * 1000)
else:
    duration_ms = 0
    logger.warning(f"Invalid sample rate (0) for {file_path}")
```

**Test**:
1. Create or modify audio file with corrupted header (zero sample rate)
2. Try to load folder containing the file
3. Verify: Application continues, file is skipped or shows 0 duration

---

## P1 - HIGH PRIORITY TASKS (Fix Soon)

These bugs cause crashes in commonly-used features like playback and waveform viewing.

### Task 5: Fix Division by Zero in AudioBrowserOrig Slider
**Priority**: P1 - HIGH  
**Severity**: MEDIUM  
**Estimated Time**: 30 minutes  

**File**: `AudioBrowserOrig/audio_browser.py`, Line 1861  
**Core Feature**: Audio Playback (seek functionality)  
**Issue**: Crash when seeking in zero-width slider widget

**Fix**:
```python
# Before (Line 1861)
value = self.minimum() + int(round(rng * x / max(1, self.width())))

# After - Already has max(1, ...) but audit similar code
# Check lines with similar patterns without protection
```

**Action**: Audit all slider/seek operations for zero-width protection

**Test**:
1. Resize window to minimum width
2. Try to seek during playback
3. Verify: No crashes, seeking works correctly

---

### Task 6: Fix Division by Zero in AudioBrowserOrig Waveform Rendering
**Priority**: P1 - HIGH  
**Severity**: MEDIUM  
**Estimated Time**: 1-2 hours  

**File**: `AudioBrowserOrig/audio_browser.py`, Lines 2147, 4503  
**Core Feature**: Waveform Display  
**Issue**: Crash during waveform generation with zero width or duration

**Fix**:
```python
# Example for Line 2147
# Before
a = int(i * n / width); b = int((i+1) * n / width)

# After
if width > 0:
    a = int(i * n / width)
    b = int((i+1) * n / width)
else:
    a = b = 0
```

**Action**: Audit all waveform rendering division operations

**Test**:
1. Resize window to minimum size during waveform generation
2. Load zero-duration audio files
3. Verify: No crashes, waveform displays correctly or shows empty

---

## P2 - MEDIUM PRIORITY TASKS (Fix When Possible)

These bugs could cause issues under specific conditions.

### Task 7: Fix Unsafe File Operations in AudioBrowserOrig
**Priority**: P2 - MEDIUM  
**Severity**: MEDIUM  
**Estimated Time**: 2-3 hours  

**File**: `AudioBrowserOrig/audio_browser.py`, Various locations  
**Core Feature**: All file I/O operations  
**Issue**: File handle leaks, potential data corruption

**Fix Pattern**:
```python
# Before
f = open(filename, 'r')
try:
    data = f.read()
finally:
    f.close()

# After
with open(filename, 'r') as f:
    data = f.read()
```

**Action**: Convert all file operations to use `with` statements

**Test**:
1. Perform various file operations
2. Check for open file handles using `lsof` (Linux) or Process Explorer (Windows)
3. Verify: No file handle leaks

---

### Task 8: Fix Unsafe File Operations in AudioBrowser-QML File Manager
**Priority**: P2 - MEDIUM  
**Severity**: MEDIUM  
**Estimated Time**: 30 minutes  

**File**: `AudioBrowser-QML/backend/file_manager.py`, Lines 603, 606, 609  
**Core Feature**: All file operations  
**Issue**: File handle leaks

**Fix**: Same as Task 7, convert to `with` statements

**Test**: Same as Task 7

---

### Task 9: Fix Division by Zero in Google Drive Sync Progress
**Priority**: P2 - MEDIUM  
**Severity**: MEDIUM  
**Estimated Time**: 30 minutes  

**File**: `AudioBrowser-QML/backend/gdrive_sync.py`, Lines 575, 577, 586, 588  
**Core Feature**: Cloud Sync  
**Issue**: Crashes during sync operations with empty file lists

**Fix Pattern**:
```python
# Before
progress_pct = (current / total) * 100

# After
if total > 0:
    progress_pct = (current / total) * 100
else:
    progress_pct = 0
```

**Test**:
1. Attempt sync with no files selected
2. Sync empty folder
3. Verify: No crashes, shows 0% or "No files" message

---

### Task 10: Fix Division by Zero in Setlist Manager Duration Calculation
**Priority**: P2 - MEDIUM  
**Severity**: MEDIUM  
**Estimated Time**: 15 minutes  

**File**: `AudioBrowser-QML/backend/setlist_manager.py`, Line 188  
**Core Feature**: Setlist Builder  
**Issue**: Crash when calculating setlist statistics with no songs

**Fix**: Add zero check before division

**Test**:
1. Create empty setlist
2. Try to calculate total duration
3. Verify: Shows 0:00 or "No songs" instead of crashing

---

### Task 11-16: Fix Division by Zero in Practice Statistics
**Priority**: P2 - MEDIUM  
**Severity**: MEDIUM  
**Estimated Time**: 1 hour  

**File**: `AudioBrowser-QML/backend/practice_statistics.py`, Lines 423, 428, 429, 463, 464  
**Core Feature**: Practice Statistics  
**Issue**: Crashes when calculating statistics with no practice data

**Fix Pattern**: Add zero checks before all division operations

**Test**:
1. Generate statistics with no practice sessions
2. Generate statistics with no songs
3. Verify: Shows "No data" message instead of crashing

---

## Implementation Order

Recommended order for implementing fixes:

1. **Week 1**: P0 tasks (Tasks 1-4) - Critical JSON and division fixes
2. **Week 2**: P1 tasks (Tasks 5-6) - High-priority UI/playback fixes
3. **Week 3**: P2 tasks (Tasks 7-16) - Medium-priority robustness improvements

---

## Testing Checklist

After implementing all fixes, run this comprehensive test:

### JSON Corruption Tests
- [ ] Corrupted `.provided_names.json` - should continue with empty names
- [ ] Corrupted `.duration_cache.json` - should continue with recalculated durations
- [ ] Corrupted `.tempo.json` - should continue with no tempo data
- [ ] Corrupted `.audio_notes_*.json` - should continue with no annotations
- [ ] Corrupted `.audio_fingerprints.json` - should continue with no fingerprints

### Edge Case Tests
- [ ] Audio file with zero sample rate - should skip or show 0:00
- [ ] Window resized to minimum during waveform generation - should not crash
- [ ] Seek slider used at zero width - should not crash
- [ ] Empty folder loaded - should show "No files"
- [ ] Batch rename with no files selected - should show message
- [ ] Sync with no files - should show 0% progress
- [ ] Practice statistics with no data - should show "No data"
- [ ] Setlist with no songs - should show "Empty setlist"

### File Operation Tests
- [ ] Multiple file operations - check for file handle leaks
- [ ] File operations during exceptions - verify proper cleanup
- [ ] File operations with read-only files - should handle gracefully

---

## Regression Testing

After fixes are applied, perform these regression tests to ensure existing functionality still works:

### Core Feature Tests
- [ ] Load folder with valid files - should display all files
- [ ] Play/pause/stop audio - should work correctly
- [ ] Add/edit/delete annotations - should persist correctly
- [ ] Generate waveforms - should display correctly
- [ ] Batch rename files - should rename correctly
- [ ] Mark best takes - should persist correctly
- [ ] Export clips - should export correctly
- [ ] Calculate practice statistics - should show correct data
- [ ] Create setlist - should save correctly
- [ ] Sync to Google Drive - should upload/download correctly

---

## Success Criteria

All tasks are considered complete when:

1. ✅ All P0 tasks implemented and tested
2. ✅ All P1 tasks implemented and tested
3. ✅ All P2 tasks implemented and tested
4. ✅ All testing checklist items pass
5. ✅ All regression tests pass
6. ✅ No new bugs introduced
7. ✅ Code reviewed by maintainer
8. ✅ Documentation updated

---

## Notes

- Each task should include unit tests where applicable
- All error messages should be logged for debugging
- User-facing error messages should be clear and actionable
- Consider adding automatic JSON file validation/repair on load
- Consider adding audio file header validation before processing

---

**Document Version**: 1.0  
**Last Updated**: December 2025  
**Next Review**: After task completion
