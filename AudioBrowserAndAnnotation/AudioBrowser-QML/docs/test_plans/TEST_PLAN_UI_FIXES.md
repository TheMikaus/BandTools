# Test Plan: UI Contrast and Logging Improvements

## Purpose
This test plan verifies the UI contrast fixes and enhanced logging features implemented to address the following issues:
- Menu bar text readability
- Dialog contrast and readability
- Null reference errors
- Logging comprehensiveness

## Test Environment
- Application: AudioBrowser-QML
- Version: 0.14.0+
- Platform: Windows/Linux/Mac

## Pre-Test Setup
1. Clear the log file if it exists: `audiobrowser.log`
2. Launch the AudioBrowser-QML application
3. Open a folder with audio files for testing

---

## Test Cases

### TC-001: Menu Bar Visibility
**Objective**: Verify menu bar text is readable with proper contrast

**Steps**:
1. Launch the application
2. Observe the menu bar (File, View, Edit, Help)
3. Hover over each menu item
4. Click on each menu to open dropdown
5. Observe menu item text in dropdowns

**Expected Results**:
- Menu bar text should be clearly visible (white or light gray on dark background)
- Hover state should show visual feedback (highlighted background)
- Dropdown menu items should be readable
- Disabled items should appear grayed out but still readable

**Log Verification**:
```
AudioBrowser QML application started
Log file: [path]/audiobrowser.log
```

---

### TC-002: Auto-Generation Settings Dialog
**Objective**: Verify the recommendation box has proper contrast

**Steps**:
1. Click Edit menu → Auto-Generation Settings...
2. Scroll to the "Recommendations" section (blue box at bottom)
3. Read the recommendation text

**Expected Results**:
- Title "ℹ️ Recommendations" should be white and clearly visible
- Bullet points text should be white and easily readable on blue background
- No black text on blue background

**Log Verification**:
```
Creating SettingsManager...
SettingsManager created successfully
```

---

### TC-003: Practice Statistics Dialog
**Objective**: Verify Practice Statistics dialog opens without errors and has proper background

**Steps**:
1. In Library tab, click the "..." button
2. Select "📊 Practice Stats"
3. Wait for dialog to open
4. Observe dialog background and text readability

**Expected Results**:
- Dialog should open without errors
- Dialog should have proper background color (not transparent)
- Text should be readable against background
- No error message: "Practice statistics manager not initialized"

**Log Verification**:
```
Creating PracticeStatistics...
PracticeStatistics initialized
PracticeStatistics created successfully
Connecting PracticeGoals to PracticeStatistics...
PracticeGoals connected to PracticeStatistics successfully
```

When dialog opens:
```
Generating practice statistics
Generating statistics from root path: [path]
Discovered [N] practice folders with audio files
Statistics generated: [N] sessions, [N] unique songs
```

---

### TC-004: Practice Goals Dialog
**Objective**: Verify Practice Goals dialog has proper styling and properties

**Steps**:
1. In Library tab, click the "..." button
2. Select "🎯 Practice Goals"
3. Wait for dialog to open
4. Observe dialog background and text readability
5. Try switching between "Active Goals" and "Manage Goals" tabs

**Expected Results**:
- Dialog should open without errors
- Dialog should have proper background color
- Both tabs should be functional
- Text should be clearly readable

**Log Verification**:
```
Creating PracticeGoals...
PracticeGoals created successfully
```

---

### TC-005: Setlist Builder Dialog
**Objective**: Verify Setlist Builder dialog opens and functions without null errors

**Steps**:
1. In Library tab, click the "..." button
2. Select "🎵 Setlist Builder"
3. Wait for dialog to open
4. Try clicking "New Setlist" button
5. Enter a setlist name
6. Click OK

**Expected Results**:
- Dialog should open without errors
- "New Setlist" button should work
- Creating a new setlist should not throw "Cannot call method 'createSetlist' of null"
- Dialog should have proper background color

**Log Verification**:
```
Creating SetlistManager...
SetlistManager created successfully
```

---

### TC-006: Library Tab File List
**Objective**: Verify file list displays count without null errors

**Steps**:
1. Open a folder with audio files
2. Observe the file list header showing "Files (N)"
3. Try "Batch Rename" and "Convert WAV→MP3" menu items

**Expected Results**:
- File count should display correctly
- No "Cannot call method 'count' of null" error
- Menu items should enable/disable based on file count
- File list should populate correctly

**Log Verification**:
```
Loading saved root directory: [path]
```

---

### TC-007: Enhanced Logging
**Objective**: Verify comprehensive logging is working

**Steps**:
1. Launch application (fresh start)
2. Open a folder
3. Open Practice Statistics dialog
4. Create an annotation
5. Play an audio file
6. Close application
7. Open the log file: `audiobrowser.log`

**Expected Results**:
Log file should contain:
- Startup banner with "=" separators
- Module names in log entries (e.g., `backend.practice_statistics`)
- File names and line numbers for each log entry
- Log level indicators (INFO, DEBUG, ERROR)
- Detailed initialization messages for each backend manager
- Connection messages between managers
- QML loading messages
- Application startup success message

**Sample Log Format**:
```
2024-XX-XX XX:XX:XX - backend.log_viewer - INFO - [log_viewer.py:XX] - ================================================================================
2024-XX-XX XX:XX:XX - backend.log_viewer - INFO - [log_viewer.py:XX] - AudioBrowser QML application started
2024-XX-XX XX:XX:XX - backend.log_viewer - INFO - [log_viewer.py:XX] - Log file: /path/to/audiobrowser.log
2024-XX-XX XX:XX:XX - backend.log_viewer - INFO - [log_viewer.py:XX] - ================================================================================
2024-XX-XX XX:XX:XX - __main__ - INFO - [main.py:XX] - Creating SettingsManager...
2024-XX-XX XX:XX:XX - __main__ - INFO - [main.py:XX] - SettingsManager created successfully
...
2024-XX-XX XX:XX:XX - backend.practice_statistics - INFO - [practice_statistics.py:XX] - PracticeStatistics initialized
...
2024-XX-XX XX:XX:XX - __main__ - INFO - [main.py:XX] - Exposing backend objects to QML context...
2024-XX-XX XX:XX:XX - __main__ - INFO - [main.py:XX] - Backend objects exposed to QML successfully
2024-XX-XX XX:XX:XX - __main__ - INFO - [main.py:XX] - Loading QML file: /path/to/qml/main.qml
2024-XX-XX XX:XX:XX - __main__ - INFO - [main.py:XX] - AudioBrowser QML Phase 7 - Application started successfully
```

---

## Test Summary

### Pass Criteria
- All test cases pass without errors
- Menu bar and dialogs are readable
- No null reference errors occur
- Log file contains detailed, structured information
- All features log their execution

### Known Limitations
- Logging is at DEBUG level, which may create large log files over time
- Menu styling depends on Qt theme support

### Test Execution Date
Date: ________________

### Tester Name
Name: ________________

### Results

| Test Case | Pass/Fail | Notes |
|-----------|-----------|-------|
| TC-001    |           |       |
| TC-002    |           |       |
| TC-003    |           |       |
| TC-004    |           |       |
| TC-005    |           |       |
| TC-006    |           |       |
| TC-007    |           |       |

### Overall Result
☐ PASS - All test cases passed
☐ FAIL - One or more test cases failed (see notes)

---

## Troubleshooting

### Issue: Menu text still hard to read
**Resolution**: Check if QtQuick.Controls.Basic is being used. Verify Theme.textColor is properly set.

### Issue: Dialog background is white/transparent
**Resolution**: Verify the background Rectangle is properly set in the dialog's QML file.

### Issue: Null reference errors persist
**Resolution**: Check that properties are properly passed from main.qml to dialogs. Verify backend managers are initialized before QML loads.

### Issue: Log file is empty or missing entries
**Resolution**: Check log file location. Verify logging.basicConfig is called before any logging occurs. Ensure LogViewer is created early in initialization.
