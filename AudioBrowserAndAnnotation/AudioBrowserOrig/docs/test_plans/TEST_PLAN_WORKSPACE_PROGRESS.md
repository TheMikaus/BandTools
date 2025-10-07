# Test Plan: Workspace Layouts & Status Bar Progress Indicators

**Feature Set**: Section 2.3.3 (Workspace Layouts) and Section 1.5 enhancement (Status Bar Progress Indicators)  
**Implementation Date**: January 2025  
**Test Plan Version**: 1.0

---

## Overview

This test plan covers two new features implemented in AudioBrowser:
1. **Workspace Layouts** - Save and restore window geometries and splitter positions
2. **Status Bar Progress Indicators** - Visual progress feedback for background operations

---

## Test Environment Requirements

### Hardware
- Windows, macOS, or Linux system
- Display resolution: 1920x1080 or higher recommended
- Mouse/trackpad for window resizing and splitter adjustment

### Software
- Python 3.8+
- PyQt6
- AudioBrowser application (latest version)
- Sample audio files (WAV/MP3) for testing fingerprinting and waveform generation

### Test Data
- Practice folder with 10-20 audio files
- Mix of files with and without existing waveforms
- Mix of files with and without fingerprints

---

## Feature 1: Workspace Layouts

### Test Case 1.1: Save Window Layout
**Objective**: Verify that window geometry and splitter state can be saved

**Prerequisites**:
- Application is running
- Window is at default size (1360x900)

**Steps**:
1. Resize the main window to a custom size (e.g., 1600x1000)
2. Adjust the main splitter by dragging it to change the file tree and content panel proportions
3. Navigate to View menu → "Save Window Layout" (or press Ctrl+Shift+L)

**Expected Results**:
- Status bar shows "Window layout saved" message for 3 seconds
- No error dialogs appear
- Application continues to function normally

**Pass Criteria**: ✅ Status message appears and no errors occur

---

### Test Case 1.2: Restore Window Layout (Same Session)
**Objective**: Verify that saved layout persists after manual changes

**Prerequisites**:
- Test Case 1.1 completed successfully
- Window layout has been saved

**Steps**:
1. Resize window to a different size
2. Adjust splitter to different proportions
3. Navigate to View menu → "Restore Window Layout" (or press Ctrl+Shift+R)

**Expected Results**:
- Window resizes to the previously saved dimensions
- Splitter returns to the previously saved position
- All content remains visible and functional

**Pass Criteria**: ✅ Window and splitter return to saved state

---

### Test Case 1.3: Restore Window Layout (New Session)
**Objective**: Verify that saved layout persists across application restarts

**Prerequisites**:
- Test Case 1.1 completed successfully
- Window layout has been saved

**Steps**:
1. Close the application completely
2. Restart the application
3. Observe the initial window size and splitter position

**Expected Results**:
- Window opens at the saved size
- Splitter is positioned as previously saved
- All UI elements are visible and functional

**Pass Criteria**: ✅ Saved layout is automatically restored on startup

---

### Test Case 1.4: Reset to Default Layout
**Objective**: Verify that layout can be reset to default state

**Prerequisites**:
- Application is running
- Custom layout has been saved (Test Case 1.1)

**Steps**:
1. Navigate to View menu → "Reset to Default Layout"
2. Observe window size and splitter position

**Expected Results**:
- Window resizes to 1360x900
- Splitter is positioned at 40:60 ratio (left:right)
- Status bar shows "Layout reset to default" message for 3 seconds
- Saved layout settings are cleared

**Pass Criteria**: ✅ Window returns to default size and splitter proportions

---

### Test Case 1.5: Layout Persistence After Reset
**Objective**: Verify that reset clears saved settings

**Prerequisites**:
- Test Case 1.4 completed successfully

**Steps**:
1. Close the application
2. Restart the application
3. Observe initial window size and splitter position

**Expected Results**:
- Window opens at default size (1360x900)
- Splitter is at default position (40:60)

**Pass Criteria**: ✅ Default layout is used after reset and restart

---

### Test Case 1.6: Keyboard Shortcuts
**Objective**: Verify keyboard shortcuts work for layout operations

**Prerequisites**:
- Application is running

**Steps**:
1. Press Ctrl+Shift+L to save layout
2. Resize window to different size
3. Press Ctrl+Shift+R to restore layout

**Expected Results**:
- Ctrl+Shift+L saves the current layout
- Ctrl+Shift+R restores the saved layout
- Keyboard shortcuts work as expected

**Pass Criteria**: ✅ All keyboard shortcuts function correctly

---

### Test Case 1.7: Edge Cases - Minimum Window Size
**Objective**: Verify layout handling with very small window sizes

**Prerequisites**:
- Application is running

**Steps**:
1. Resize window to minimum size (as small as OS allows)
2. Save layout (Ctrl+Shift+L)
3. Maximize window
4. Restore layout (Ctrl+Shift+R)

**Expected Results**:
- Minimum window size is saved and restored correctly
- All UI elements remain accessible
- No visual glitches or overlapping elements

**Pass Criteria**: ✅ Small window sizes are handled properly

---

### Test Case 1.8: Edge Cases - Maximum Window Size
**Objective**: Verify layout handling with maximized window

**Prerequisites**:
- Application is running

**Steps**:
1. Maximize the window
2. Save layout (Ctrl+Shift+L)
3. Restore to normal size
4. Restart application

**Expected Results**:
- Window opens maximized after restart
- Splitter position is restored correctly
- All UI elements scale appropriately

**Pass Criteria**: ✅ Maximized window state is preserved

---

## Feature 2: Status Bar Progress Indicators

### Test Case 2.1: Waveform Generation Progress Display
**Objective**: Verify progress indicator appears during waveform generation

**Prerequisites**:
- Practice folder with audio files without waveforms
- Auto-generation is enabled

**Steps**:
1. Open a folder with files that don't have waveforms
2. Enable auto-generation (if not already enabled)
3. Trigger waveform generation (folder selection or manual)
4. Observe status bar during generation

**Expected Results**:
- Progress bar appears in status bar (right side)
- Progress label shows: "Generating waveforms: X/Y (filename)"
- Progress bar fills from 0% to 100%
- Current filename is displayed (truncated if too long)
- Progress updates in real-time

**Pass Criteria**: ✅ Progress indicator is visible and updates correctly

---

### Test Case 2.2: Waveform Generation Progress Completion
**Objective**: Verify progress indicator is hidden after completion

**Prerequisites**:
- Test Case 2.1 in progress or completed

**Steps**:
1. Wait for waveform generation to complete
2. Observe status bar after completion

**Expected Results**:
- Progress bar disappears when generation completes
- Progress label disappears when generation completes
- Status bar returns to showing file statistics

**Pass Criteria**: ✅ Progress indicators are properly hidden

---

### Test Case 2.3: Fingerprint Generation Progress Display
**Objective**: Verify progress indicator appears during fingerprint generation

**Prerequisites**:
- Practice folder with audio files without fingerprints
- Auto-generation is enabled

**Steps**:
1. Open a folder with files that don't have fingerprints
2. Enable fingerprint auto-generation
3. Trigger fingerprint generation
4. Observe status bar during generation

**Expected Results**:
- Progress bar appears in status bar
- Progress label shows: "Generating fingerprints: X/Y (filename)"
- Progress bar fills from 0% to 100%
- Current filename is displayed
- Progress updates in real-time

**Pass Criteria**: ✅ Progress indicator is visible and updates correctly

---

### Test Case 2.4: Fingerprint Generation Progress Completion
**Objective**: Verify progress indicator is hidden after fingerprint completion

**Prerequisites**:
- Test Case 2.3 in progress or completed

**Steps**:
1. Wait for fingerprint generation to complete
2. Observe status bar after completion

**Expected Results**:
- Progress bar disappears when generation completes
- Progress label disappears when generation completes
- Status bar returns to showing file statistics

**Pass Criteria**: ✅ Progress indicators are properly hidden

---

### Test Case 2.5: Sequential Operations (Waveforms then Fingerprints)
**Objective**: Verify progress indicators work correctly for sequential operations

**Prerequisites**:
- Practice folder with files needing both waveforms and fingerprints
- Auto-generation enabled for both

**Steps**:
1. Open a folder that will trigger both waveform and fingerprint generation
2. Observe status bar during both operations
3. Note the transition between operations

**Expected Results**:
- Progress shows "Generating waveforms" first
- After waveform completion, progress shows "Generating fingerprints"
- Progress bar resets to 0% when starting fingerprints
- Both operations complete without visual glitches

**Pass Criteria**: ✅ Progress indicator transitions smoothly between operations

---

### Test Case 2.6: Progress Accuracy
**Objective**: Verify progress percentages are accurate

**Prerequisites**:
- Practice folder with exactly 10 audio files

**Steps**:
1. Trigger waveform generation
2. Observe progress values at different stages
3. Count actual files processed vs. displayed progress

**Expected Results**:
- Progress shows "1/10" after first file (10%)
- Progress shows "5/10" halfway through (50%)
- Progress shows "10/10" at completion (100%)
- Percentages are mathematically correct
- All files are processed

**Pass Criteria**: ✅ Progress values are accurate

---

### Test Case 2.7: Long Filename Truncation
**Objective**: Verify long filenames are properly truncated in progress label

**Prerequisites**:
- Practice folder with files having very long names (>50 characters)

**Steps**:
1. Create or rename a file to have a very long name
2. Trigger waveform or fingerprint generation
3. Observe progress label when processing the long-named file

**Expected Results**:
- Filename is truncated with "..." if too long
- Progress label text doesn't overflow or break layout
- Total label length doesn't exceed 60 characters
- Progress bar remains properly aligned

**Pass Criteria**: ✅ Long filenames are properly truncated

---

### Test Case 2.8: Cancellation Behavior
**Objective**: Verify progress indicator is hidden when generation is canceled

**Prerequisites**:
- Practice folder with many audio files (20+)

**Steps**:
1. Trigger waveform or fingerprint generation
2. While generation is in progress, cancel the operation
3. Observe status bar behavior

**Expected Results**:
- Progress indicator is immediately hidden upon cancellation
- Status bar returns to normal display
- No orphaned progress widgets remain visible

**Pass Criteria**: ✅ Progress indicators are properly cleaned up on cancellation

---

### Test Case 2.9: Multiple Window Resizing During Progress
**Objective**: Verify progress indicators remain visible during window operations

**Prerequisites**:
- Generation operation in progress

**Steps**:
1. Start waveform or fingerprint generation
2. While in progress, resize the window multiple times
3. Minimize and restore the window
4. Observe progress indicators

**Expected Results**:
- Progress bar and label remain visible and properly positioned
- Progress continues to update normally
- No visual glitches or layout issues
- Progress widgets scale appropriately with window

**Pass Criteria**: ✅ Progress indicators remain functional during window operations

---

### Test Case 2.10: Status Bar Interaction
**Objective**: Verify progress indicators don't interfere with other status bar elements

**Prerequisites**:
- Application is running

**Steps**:
1. Trigger waveform generation to show progress
2. Perform other operations that update status bar messages
3. Observe status bar behavior

**Expected Results**:
- Progress indicators stay on the right side (permanent widgets)
- Temporary status messages appear on the left
- Both types of messages are visible simultaneously when applicable
- No overlap or visual conflicts

**Pass Criteria**: ✅ Progress indicators coexist with other status bar messages

---

## Integration Tests

### Test Case 3.1: Layout Persistence During Background Operations
**Objective**: Verify layout operations work during generation

**Prerequisites**:
- Practice folder with files needing generation

**Steps**:
1. Start waveform generation
2. While generation is in progress, save layout (Ctrl+Shift+L)
3. Resize window
4. Restore layout (Ctrl+Shift+R)
5. Wait for generation to complete

**Expected Results**:
- Layout operations work normally during background operations
- Progress indicators remain visible and functional
- No conflicts or errors occur

**Pass Criteria**: ✅ Both features work independently without interference

---

### Test Case 3.2: Layout Restoration with Active Progress
**Objective**: Verify layout restoration doesn't disrupt active progress indicators

**Prerequisites**:
- Saved custom layout exists
- Generation operation can be triggered

**Steps**:
1. Set window to non-saved size
2. Start waveform generation
3. While progress is showing, restore saved layout (Ctrl+Shift+R)

**Expected Results**:
- Window resizes to saved layout
- Progress indicators remain visible
- Progress continues to update correctly
- No visual glitches

**Pass Criteria**: ✅ Layout restoration doesn't affect active progress display

---

## Regression Tests

### Test Case 4.1: Existing Features Functionality
**Objective**: Verify new features don't break existing functionality

**Prerequisites**:
- Application is running
- Practice folder is loaded

**Steps**:
1. Test basic file playback
2. Test annotation creation
3. Test file tree navigation
4. Test menu operations
5. Test keyboard shortcuts for existing features

**Expected Results**:
- All existing features work as before
- No new errors or crashes
- Performance is not degraded

**Pass Criteria**: ✅ No regressions in existing functionality

---

### Test Case 4.2: Settings Persistence
**Objective**: Verify existing settings are not affected

**Prerequisites**:
- Existing settings configured (theme, undo limit, etc.)

**Steps**:
1. Verify current settings are preserved
2. Use layout features
3. Restart application
4. Check all settings

**Expected Results**:
- Existing settings remain unchanged
- New layout settings don't conflict with existing settings
- Settings dialog continues to work correctly

**Pass Criteria**: ✅ Existing settings are preserved

---

## Performance Tests

### Test Case 5.1: Progress Update Performance
**Objective**: Verify progress updates don't impact generation performance

**Prerequisites**:
- Practice folder with 50+ audio files

**Steps**:
1. Measure time to generate waveforms without progress feature (if possible)
2. Measure time with progress feature active
3. Compare generation times

**Expected Results**:
- Performance impact is negligible (<5% difference)
- UI remains responsive during generation
- Progress updates are smooth (no stuttering)

**Pass Criteria**: ✅ Progress indicators have minimal performance impact

---

### Test Case 5.2: Layout Save/Restore Performance
**Objective**: Verify layout operations are fast

**Prerequisites**:
- Application is running

**Steps**:
1. Measure time to save layout
2. Measure time to restore layout
3. Repeat 10 times and average

**Expected Results**:
- Save operation completes in < 100ms
- Restore operation completes in < 200ms
- Operations feel instantaneous to user

**Pass Criteria**: ✅ Layout operations are performant

---

## Known Limitations

1. **Layout on Multi-Monitor Setups**: Window position may not restore correctly if saved on a different monitor configuration
2. **Theme Changes**: Layout is preserved but theme changes still require restart
3. **Progress Granularity**: Progress updates once per file, not during individual file processing
4. **Manual Fingerprinting**: Uses separate QProgressDialog, not status bar indicator

---

## Test Execution Summary

**Date**: _________________  
**Tester**: _________________  
**Build Version**: _________________  

### Results Summary

| Test Case | Pass | Fail | Notes |
|-----------|------|------|-------|
| 1.1 - Save Window Layout | ☐ | ☐ | |
| 1.2 - Restore Layout (Same Session) | ☐ | ☐ | |
| 1.3 - Restore Layout (New Session) | ☐ | ☐ | |
| 1.4 - Reset to Default Layout | ☐ | ☐ | |
| 1.5 - Layout Persistence After Reset | ☐ | ☐ | |
| 1.6 - Keyboard Shortcuts | ☐ | ☐ | |
| 1.7 - Edge Cases - Minimum Size | ☐ | ☐ | |
| 1.8 - Edge Cases - Maximum Size | ☐ | ☐ | |
| 2.1 - Waveform Progress Display | ☐ | ☐ | |
| 2.2 - Waveform Progress Completion | ☐ | ☐ | |
| 2.3 - Fingerprint Progress Display | ☐ | ☐ | |
| 2.4 - Fingerprint Progress Completion | ☐ | ☐ | |
| 2.5 - Sequential Operations | ☐ | ☐ | |
| 2.6 - Progress Accuracy | ☐ | ☐ | |
| 2.7 - Long Filename Truncation | ☐ | ☐ | |
| 2.8 - Cancellation Behavior | ☐ | ☐ | |
| 2.9 - Window Resizing During Progress | ☐ | ☐ | |
| 2.10 - Status Bar Interaction | ☐ | ☐ | |
| 3.1 - Layout + Background Operations | ☐ | ☐ | |
| 3.2 - Layout Restoration + Progress | ☐ | ☐ | |
| 4.1 - Existing Features | ☐ | ☐ | |
| 4.2 - Settings Persistence | ☐ | ☐ | |
| 5.1 - Progress Performance | ☐ | ☐ | |
| 5.2 - Layout Performance | ☐ | ☐ | |

**Total Tests**: 24  
**Passed**: _____  
**Failed**: _____  
**Pass Rate**: _____%

---

## Bug Reporting Template

**Bug ID**: ___________  
**Test Case**: ___________  
**Severity**: ☐ Critical ☐ Major ☐ Minor ☐ Cosmetic  
**Description**: _______________________________________________  
**Steps to Reproduce**: _______________________________________________  
**Expected Result**: _______________________________________________  
**Actual Result**: _______________________________________________  
**Screenshots/Logs**: _______________________________________________  

---

## Sign-off

**Test Plan Reviewed By**: _________________  
**Date**: _________________  

**Testing Completed By**: _________________  
**Date**: _________________  

**Approved for Release**: _________________  
**Date**: _________________  

---

**Notes**: 
- All test cases should be executed in order
- Document any deviations or unexpected behavior
- Update known limitations section if new issues discovered
- Attach screenshots for any visual issues
