# Library File Listing - Visual Changes

## Before vs After

### File List Display

#### BEFORE:
```
| Take | File Name                | Library    |
|------|--------------------------|------------|
| ★★   | Beatles - Hey Jude       | 2024-10-16 |
| ★★   | Rolling Stones - Angie   | 2024-10-16 |
```

**Problems:**
- Take column: Two identical gray stars (confusing - what do they mean?)
- File Name: Shows recognized song name, not actual filename
- Library: Shows folder date instead of library/song info
- No duration column

#### AFTER:
```
| Take | File Name                  | Library                | Duration |
|------|----------------------------|------------------------|----------|
| ⭐    | practice_001.wav           | Beatles - Hey Jude     | 03:45    |
|      | practice_002.wav           |                        | 02:30    |
| ◐    | practice_003.mp3           | Rolling Stones - Angie | 04:12    |
```

**Fixed:**
- Take column: 
  - ⭐ Gold star = Best Take (only shows when marked)
  - ◐ Half-blue star = Partial Take (only shows when marked)
  - Empty = No status (unmarked indicators only show subtle dashed outline on hover)
- File Name: Shows actual filename (e.g., "practice_001.wav")
- Library: Shows recognized song name from fingerprinting (e.g., "Beatles - Hey Jude")
- Duration: New column showing file duration (MM:SS format)

### Take Indicators - Visual States

#### Best Take Indicator

**Marked (Best Take):**
```
  ⭐ <- Gold star, clearly visible
```

**Unmarked:**
```
   <- Nothing shown (subtle dashed outline only appears on hover)
```

#### Partial Take Indicator

**Marked (Partial Take):**
```
  ◐ <- Half-filled blue star, clearly visible
```

**Unmarked:**
```
   <- Nothing shown (subtle dashed outline with vertical line appears on hover)
```

### Performance Improvements

#### Folder Selection Speed

**BEFORE:**
```
User clicks folder → [10+ second delay] → Files appear
                     ↑
                     Extracting duration from every audio file
```

**AFTER:**
```
User clicks folder → [< 100ms] → Files appear instantly
                                  (with cached durations only)
```

### Column Mappings

#### Data Flow

```
.provided_names.json                Audio Files
    ↓                                   ↓
"Beatles - Hey Jude"          "practice_001.wav"
                ↓                       ↓
            Library Column          File Name Column

.duration_cache.json
    ↓
30000 (ms)
    ↓
Duration Column (00:30)
```

## Technical Details

### Model Changes (backend/models.py)

```python
# BEFORE
display_name = path.name
if provided_name:
    display_name = provided_name  # Overwrites filename!
library_name = path.parent.name  # Folder name (e.g., "2024-10-16")

# AFTER  
display_name = path.name  # Always actual filename
library_name = provided_name if provided_name else ""  # Song name
# Performance: Only use cached duration, don't extract on-the-fly
```

### UI Changes (qml/tabs/LibraryTab.qml)

Added Duration column:
- Header: "Duration"
- Display: `formatDuration(model.duration || 0)`
- Format: MM:SS or HH:MM:SS
- Width: 80px, right-aligned

### Error Fixes (qml/tabs/AnnotationsTab.qml)

Commented out undefined `waveformDisplay` references:
```javascript
// Before
waveformDisplay.setFilePath(path)  // ERROR: waveformDisplay is not defined

// After  
// TODO: Re-enable when WaveformDisplay is added to this tab
// waveformDisplay.setFilePath(path)
```
