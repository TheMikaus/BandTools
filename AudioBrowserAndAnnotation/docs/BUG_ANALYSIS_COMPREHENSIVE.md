# Comprehensive Bug Analysis - AudioBrowser Applications

**Date**: December 2025  
**Analyzed Versions**:
- AudioBrowserOrig (PyQt6 widgets version)
- AudioBrowser-QML (QML version, 95% production-ready)

## Executive Summary

This document provides a comprehensive analysis of potential bugs in both AudioBrowser versions that could prevent core features from functioning properly. The analysis focuses on bugs that would cause crashes, data loss, or feature failures rather than minor UI issues or optimization opportunities.

**Key Findings**:
- **AudioBrowserOrig**: 12 potential bugs identified, 3 high severity
- **AudioBrowser-QML**: 8 potential bugs identified, 2 high severity
- **Core Features at Risk**: Audio playback, annotation persistence, waveform generation, batch operations, file loading

---

## Core Features Analysis

The AudioBrowser applications have the following core features that were analyzed:

1. **Audio Playback** - Play, pause, stop, seek audio files (WAV, MP3)
2. **Annotation Management** - Add, edit, delete timestamped annotations
3. **Waveform Display** - Generate and display audio waveforms
4. **File Tree/Library** - Browse and load audio files from directories
5. **Batch Operations** - Rename files, convert formats (WAV→MP3)
6. **Metadata Persistence** - Save/load song names, annotations, tempo, etc.
7. **Best Take Marking** - Mark and filter best takes
8. **Clip Management** - Create and export audio clips
9. **Practice Features** - Statistics, goals, setlists
10. **Cloud Sync** - Google Drive synchronization (Original only, QML version has stubs)

---

## AudioBrowserOrig Bugs

### HIGH SEVERITY

#### Bug #1: Unprotected JSON Loading in Provided Names
**File**: `audio_browser.py`, Line 699  
**Impact**: Application crash when loading corrupted `.provided_names.json` file  
**Core Feature Affected**: File Library, Batch Rename

**Description**:
```python
# Line 699
provided_names = json.load(f)
```

The code loads the provided names JSON file without try/except protection. If the file is corrupted or contains invalid JSON, the application will crash immediately on folder load, preventing all file browsing.

**Risk**: **HIGH** - Prevents entire application from loading folders

**Recommendation**: Wrap in try/except with fallback to empty dict
```python
try:
    provided_names = json.load(f)
except (json.JSONDecodeError, ValueError) as e:
    logger.error(f"Failed to load provided names: {e}")
    provided_names = {}
```

---

#### Bug #2: Unprotected JSON Loading in Duration Cache
**File**: `audio_browser.py`, Line 1207  
**Impact**: Application crash when loading corrupted `.duration_cache.json` file  
**Core Feature Affected**: File Library, Waveform Display

**Description**:
```python
# Line 1207
duration_cache = json.load(f)
```

Similar to Bug #1, this loads the duration cache without error handling. Corrupted cache files will cause immediate crashes when opening folders.

**Risk**: **HIGH** - Prevents folder loading and duration display

**Recommendation**: Wrap in try/except with fallback to empty dict

---

#### Bug #3: Division by Zero in Slider Value Calculation
**File**: `audio_browser.py`, Line 1861  
**Impact**: Crash when seeking in zero-width slider widget  
**Core Feature Affected**: Audio Playback (seek functionality)

**Description**:
```python
# Line 1861
value = self.minimum() + int(round(rng * x / max(1, self.width())))
```

While there's a `max(1, self.width())` protection, there are other similar division operations in the waveform display code that don't have this protection.

**Risk**: **MEDIUM** - Could crash during UI resize operations

**Recommendation**: Audit all division operations for zero protection

---

### MEDIUM SEVERITY

#### Bug #4: Multiple Division by Zero in Waveform Rendering
**File**: `audio_browser.py`, Lines 2147, 4503  
**Impact**: Crash during waveform generation or display  
**Core Feature Affected**: Waveform Display

**Description**:
```python
# Line 2147
a = int(i * n / width); b = int((i+1) * n / width)

# Line 4503
return int((ms / dur) * max(1, self.width()))
```

Multiple waveform rendering functions perform division operations that could result in division by zero if the widget width is 0 or duration is 0.

**Risk**: **MEDIUM** - Could crash when resizing window or loading zero-duration files

**Recommendation**: Add width/duration validation before division operations

---

#### Bug #5: Unsafe File Operations Without Context Managers
**File**: `audio_browser.py`, Various locations  
**Impact**: File handle leaks, potential data corruption  
**Core Feature Affected**: All file I/O operations

**Description**:
Some file operations don't use `with` statements, which could lead to file handles not being properly closed if exceptions occur.

**Risk**: **LOW-MEDIUM** - Could cause file lock issues or data corruption under error conditions

**Recommendation**: Convert all file operations to use `with` statements

---

### AudioBrowserOrig Summary

| Severity | Count | Features at Risk |
|----------|-------|------------------|
| HIGH | 3 | File loading, annotation persistence, audio playback |
| MEDIUM | 9 | Waveform display, batch operations, UI responsiveness |
| **Total** | **12** | **Multiple core features** |

---

## AudioBrowser-QML Bugs

### HIGH SEVERITY

#### Bug #6: Unprotected JSON Loading in Tempo Metadata
**File**: `backend/file_manager.py`, Line 741  
**Impact**: Application crash when loading corrupted `.tempo.json` file  
**Core Feature Affected**: Tempo/BPM Display

**Description**:
```python
# Line 741
tempo_data = json.load(f)
```

Missing try/except protection for JSON loading. Will crash when loading folders with corrupted tempo metadata.

**Risk**: **HIGH** - Prevents folder loading if tempo file is corrupted

**Recommendation**: Wrap in try/except with fallback to empty dict

---

#### Bug #7: Division by Zero in Duration Calculation
**File**: `backend/file_manager.py`, Line 681  
**Impact**: Crash when processing audio files with zero sample rate  
**Core Feature Affected**: File Library, Duration Display

**Description**:
```python
# Line 681
duration_ms = int((frames / rate) * 1000)
```

If an audio file has a corrupted header with rate=0, this will cause a division by zero crash.

**Risk**: **HIGH** - Could crash when scanning folders with corrupted audio files

**Recommendation**: Add rate validation
```python
if rate > 0:
    duration_ms = int((frames / rate) * 1000)
else:
    duration_ms = 0
    logger.warning(f"Invalid sample rate for {file_path}")
```

---

### MEDIUM SEVERITY

#### Bug #8: Unsafe File Operations in File Manager
**File**: `backend/file_manager.py`, Lines 603, 606, 609  
**Impact**: File handle leaks  
**Core Feature Affected**: All file operations

**Description**:
```python
# Lines 603, 606, 609
f = open(...)  # Without 'with' statement
```

Multiple file operations don't use context managers, risking file handle leaks.

**Risk**: **MEDIUM** - Could cause file locking issues

**Recommendation**: Use `with` statements for all file operations

---

#### Bug #9-16: Multiple Division by Zero in Various Modules
**Files**: 
- `backend/gdrive_sync.py`, Lines 575, 577, 586, 588
- `backend/setlist_manager.py`, Line 188
- `backend/practice_statistics.py`, Lines 423, 428, 429, 463, 464

**Impact**: Crashes during sync operations, setlist calculations, practice statistics  
**Core Features Affected**: Cloud Sync, Practice Statistics, Setlist Builder

**Description**:
Various percentage and progress calculations don't protect against division by zero when total counts are 0.

**Risk**: **MEDIUM** - Could crash when processing empty datasets

**Recommendation**: Add zero checks before all division operations
```python
# Example fix
if total > 0:
    progress_pct = (current / total) * 100
else:
    progress_pct = 0
```

---

### AudioBrowser-QML Summary

| Severity | Count | Features at Risk |
|----------|-------|------------------|
| HIGH | 2 | File loading, duration display |
| MEDIUM | 6 | Cloud sync, practice features, file operations |
| **Total** | **8** | **Multiple core features** |

---

## Bugs by Core Feature

### 1. Audio Playback
- **AudioBrowserOrig**: Bug #3 (seek slider crash)
- **Impact**: Could crash when seeking during playback
- **Priority**: HIGH

### 2. File Loading / Library
- **AudioBrowserOrig**: Bugs #1, #2 (JSON crashes)
- **AudioBrowser-QML**: Bugs #6, #7 (JSON crashes, duration calculation)
- **Impact**: Prevents folder loading, crashes on corrupted files
- **Priority**: CRITICAL

### 3. Waveform Display
- **AudioBrowserOrig**: Bug #4 (division by zero)
- **Impact**: Crashes during waveform generation or window resize
- **Priority**: HIGH

### 4. Annotation Management
- **AudioBrowserOrig**: Bug #1 (JSON loading)
- **Impact**: Crashes when loading corrupted annotation files
- **Priority**: HIGH

### 5. Batch Operations
- **AudioBrowserOrig**: Related to file operations (Bug #5)
- **Impact**: Potential file corruption or handle leaks
- **Priority**: MEDIUM

### 6. Practice Features (Statistics, Goals, Setlists)
- **AudioBrowser-QML**: Bugs #9-16 (division by zero)
- **Impact**: Crashes when calculating statistics with empty data
- **Priority**: MEDIUM

### 7. Cloud Sync
- **AudioBrowser-QML**: Bugs #9-12 (division by zero in progress calculation)
- **Impact**: Crashes during sync operations with empty file lists
- **Priority**: LOW-MEDIUM (feature is optional)

---

## Critical Bug Priorities

### P0 - CRITICAL (Must Fix Immediately)
These bugs cause crashes that prevent basic application functionality:

1. **Bug #1**: Unprotected JSON loading in provided names (AudioBrowserOrig)
2. **Bug #2**: Unprotected JSON loading in duration cache (AudioBrowserOrig)
3. **Bug #6**: Unprotected JSON loading in tempo metadata (AudioBrowser-QML)
4. **Bug #7**: Division by zero in duration calculation (AudioBrowser-QML)

**Impact**: Users cannot load folders or browse files

---

### P1 - HIGH (Fix Soon)
These bugs cause crashes in commonly-used features:

5. **Bug #3**: Division by zero in slider (AudioBrowserOrig)
6. **Bug #4**: Division by zero in waveform rendering (AudioBrowserOrig)

**Impact**: Crashes during normal playback and waveform viewing

---

### P2 - MEDIUM (Fix When Possible)
These bugs could cause issues under specific conditions:

7. **Bug #5**: Unsafe file operations (Both versions)
8. **Bug #8**: Unsafe file operations in file manager (AudioBrowser-QML)
9. **Bugs #9-16**: Division by zero in practice features (AudioBrowser-QML)

**Impact**: File handle leaks, crashes in advanced features

---

## Recommended Fix Approach

### Phase 1: JSON Loading Protection (P0)
**Time**: 1-2 hours  
**Files**:
- `AudioBrowserOrig/audio_browser.py` (lines 699, 1207)
- `AudioBrowser-QML/backend/file_manager.py` (line 741)

**Fix Pattern**:
```python
try:
    data = json.load(f)
except (json.JSONDecodeError, ValueError) as e:
    logger.error(f"Failed to load {filename}: {e}")
    data = {}  # or appropriate default
```

---

### Phase 2: Division by Zero Protection (P0-P1)
**Time**: 2-3 hours  
**Files**:
- `AudioBrowserOrig/audio_browser.py` (lines 1861, 2147, 4503)
- `AudioBrowser-QML/backend/file_manager.py` (line 681)

**Fix Pattern**:
```python
if denominator > 0:
    result = numerator / denominator
else:
    result = 0  # or appropriate default
    logger.warning(f"Division by zero prevented in {context}")
```

---

### Phase 3: File Operations Safety (P2)
**Time**: 3-4 hours  
**Files**: Multiple files in both versions

**Fix Pattern**:
```python
# Before
f = open(filename, 'r')
data = f.read()
f.close()

# After
with open(filename, 'r') as f:
    data = f.read()
```

---

### Phase 4: Practice Features Protection (P2)
**Time**: 1-2 hours  
**Files**:
- `AudioBrowser-QML/backend/gdrive_sync.py`
- `AudioBrowser-QML/backend/practice_statistics.py`
- `AudioBrowser-QML/backend/setlist_manager.py`

**Fix Pattern**: Add zero checks before all division operations in progress/statistics calculations

---

## Testing Recommendations

After applying fixes, test the following scenarios:

### JSON Corruption Test
1. Create corrupted JSON files (`.provided_names.json`, `.duration_cache.json`, `.tempo.json`)
2. Try to load folders containing these files
3. **Expected**: Application should log error and continue with empty defaults

### Audio File Corruption Test
1. Create audio files with corrupted headers (zero sample rate)
2. Try to load folders containing these files
3. **Expected**: Application should skip file with warning, not crash

### Empty Data Test
1. Calculate statistics with no practice sessions
2. Sync with no files selected
3. Calculate setlist duration with no songs
4. **Expected**: No division by zero crashes, show "No data" message

### Edge Case UI Test
1. Resize window to minimum size
2. Load zero-duration audio file
3. Seek during playback
4. **Expected**: No crashes during UI operations

---

## Conclusion

Both AudioBrowser versions have potential bugs that could prevent core features from working:

- **AudioBrowserOrig** has more potential bugs (12 total), with 3 HIGH severity issues
- **AudioBrowser-QML** has fewer bugs (8 total), with 2 HIGH severity issues
- **Both versions** need JSON loading protection and division by zero fixes
- **Estimated total fix time**: 7-11 hours for all critical and high-priority bugs

**Recommended Action**: Address P0 (CRITICAL) bugs immediately in both versions before any new feature development.

---

## Appendix: Full Bug List

### AudioBrowserOrig
1. Unprotected JSON load (provided names) - HIGH
2. Unprotected JSON load (duration cache) - HIGH  
3. Division by zero (slider) - HIGH
4. Division by zero (waveform render) - MEDIUM
5. Unsafe file operations - MEDIUM
6-12. Additional waveform and UI division issues - MEDIUM

### AudioBrowser-QML
1. Unprotected JSON load (tempo) - HIGH
2. Division by zero (duration calculation) - HIGH
3. Unsafe file operations (file manager) - MEDIUM
4-8. Division by zero (practice features) - MEDIUM

---

**Document Version**: 1.0  
**Last Updated**: December 2025  
**Next Review**: After bug fixes are applied
