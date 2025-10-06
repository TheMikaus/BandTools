# Test Plan: Now Playing Panel

**Feature Set**: Section 1.4 (Unified "Now Playing" Panel)  
**Implementation Date**: January 2025  
**Test Plan Version**: 1.0

---

## Overview

This test plan covers the Now Playing Panel feature, which provides persistent playback controls and quick annotation entry accessible from any tab. The panel reduces the need to switch to the Annotations tab during review workflows.

---

## Test Environment Requirements

### Software
- AudioBrowser application (latest build with Now Playing Panel)
- Python 3.9+
- PyQt6
- Test audio files (WAV and MP3 formats)
- Multiple practice folders with various audio files

### Test Data
- Mix of WAV and MP3 files
- Files with various durations (short: <1 min, medium: 1-5 min, long: >5 min)
- Practice folders with existing annotations
- Fresh folders without annotations

---

## Feature 1: Panel Visibility and Layout

### Test Case 1.1: Panel Appears in Main Window
**Preconditions**: Application started, no file loaded  
**Steps**:
1. Launch AudioBrowser
2. Observe the main window layout

**Expected Results**:
- Now Playing Panel is visible below player bar and above tabs
- Panel shows header "Now Playing" with collapse button (▼)
- Panel shows "No file loaded" message
- Play button and annotation controls are disabled

**Priority**: Critical

---

### Test Case 1.2: Panel Position Remains Fixed
**Preconditions**: Application running, Now Playing Panel visible  
**Steps**:
1. Switch between different tabs (Folder Notes, Library, Annotations)
2. Observe the Now Playing Panel

**Expected Results**:
- Panel remains in the same position regardless of active tab
- Panel is always visible and accessible
- Panel does not move or disappear

**Priority**: High

---

## Feature 2: File Loading and Display

### Test Case 2.1: Panel Updates When File Loaded
**Preconditions**: Application running  
**Steps**:
1. Select and play an audio file from the file tree
2. Observe the Now Playing Panel

**Expected Results**:
- Panel shows file name with music note icon (e.g., "♪ MySong.wav")
- Play button changes to pause icon
- Time display shows "0:00 / [total duration]"
- Play button and annotation controls are enabled
- Mini waveform indicator is visible

**Priority**: Critical

---

### Test Case 2.2: Panel Updates During Playback
**Preconditions**: Audio file playing  
**Steps**:
1. Observe the time display in the Now Playing Panel during playback
2. Watch the mini waveform indicator

**Expected Results**:
- Time display updates continuously (e.g., "0:05 / 3:24")
- Mini waveform background subtly changes to show progress
- Play button shows pause icon
- All updates are smooth without flickering

**Priority**: High

---

### Test Case 2.3: Panel Clears When Playback Stops
**Preconditions**: Audio file playing  
**Steps**:
1. Stop playback (close file or select folder)
2. Observe the Now Playing Panel

**Expected Results**:
- Panel shows "No file loaded"
- Play button changes to play icon
- Play button and annotation controls are disabled
- Time display shows "0:00 / 0:00"

**Priority**: High

---

## Feature 3: Playback Controls

### Test Case 3.1: Play/Pause Button Synchronization
**Preconditions**: Audio file loaded  
**Steps**:
1. Click play button in Now Playing Panel
2. Observe main player controls
3. Click pause button in main player bar
4. Observe Now Playing Panel play button

**Expected Results**:
- Play button in panel is synchronized with main player
- Both buttons show same state (play or pause icon)
- Playback starts/stops as expected
- No conflicts between panel and main controls

**Priority**: Critical

---

### Test Case 3.2: Play Button Shortcuts Work
**Preconditions**: Audio file loaded  
**Steps**:
1. Press Space bar to toggle playback
2. Observe Now Playing Panel play button

**Expected Results**:
- Play button in panel updates to reflect playback state
- Keyboard shortcuts work as expected
- Panel button icon matches actual playback state

**Priority**: High

---

## Feature 4: Quick Annotation Entry

### Test Case 4.1: Add Annotation via Text Entry
**Preconditions**: Audio file playing at position 1:30  
**Steps**:
1. Type "Test annotation" in the annotation text field
2. Press Enter

**Expected Results**:
- Annotation is added at current playback position (1:30)
- Text field clears after adding
- Annotation appears in Annotations tab
- Annotation has correct timestamp (1:30)
- Annotation is a point annotation (not a clip)

**Priority**: Critical

---

### Test Case 4.2: Add Annotation via Button
**Preconditions**: Audio file playing at position 2:15  
**Steps**:
1. Type "Button annotation" in the annotation text field
2. Click "Add Note" button

**Expected Results**:
- Annotation is added at current playback position (2:15)
- Text field clears after adding
- Annotation appears in Annotations tab
- Behavior identical to pressing Enter

**Priority**: High

---

### Test Case 4.3: Empty Text Handling
**Preconditions**: Audio file playing  
**Steps**:
1. Leave annotation text field empty
2. Press Enter or click "Add Note"

**Expected Results**:
- No annotation is added
- No error message appears
- Application remains stable

**Priority**: Medium

---

### Test Case 4.4: Annotation While Paused
**Preconditions**: Audio file loaded and paused at 1:00  
**Steps**:
1. Type "Paused annotation" in text field
2. Press Enter

**Expected Results**:
- Annotation is added at current position (1:00)
- Annotation appears in Annotations tab
- Works same as during playback

**Priority**: High

---

### Test Case 4.5: Quick Annotations Integrate with Undo
**Preconditions**: Audio file playing  
**Steps**:
1. Add annotation "Test 1" via Now Playing Panel
2. Click Undo button in toolbar
3. Observe Annotations tab

**Expected Results**:
- Annotation "Test 1" is removed from annotations list
- Undo works correctly with quick annotations
- Redo button becomes available

**Priority**: High

---

### Test Case 4.6: Multiple Quick Annotations
**Preconditions**: Audio file playing  
**Steps**:
1. Add annotation "First" at 0:10
2. Seek to 0:30 and add annotation "Second"
3. Seek to 1:00 and add annotation "Third"
4. Switch to Annotations tab

**Expected Results**:
- All three annotations appear in correct order
- Each has correct timestamp
- All are point annotations
- All can be selected and deleted normally

**Priority**: High

---

## Feature 5: Collapsible Panel

### Test Case 5.1: Collapse Panel
**Preconditions**: Panel expanded, file playing  
**Steps**:
1. Click collapse button (▼) in panel header
2. Observe the panel

**Expected Results**:
- Panel content (file info, controls, annotation input) hides
- Only panel header remains visible
- Collapse button changes to ▶
- More space available for tabs
- Playback continues uninterrupted

**Priority**: High

---

### Test Case 5.2: Expand Panel
**Preconditions**: Panel collapsed  
**Steps**:
1. Click expand button (▶) in panel header
2. Observe the panel

**Expected Results**:
- Panel content becomes visible again
- Collapse button changes to ▼
- All controls show current state correctly
- Panel displays current file and time

**Priority**: High

---

### Test Case 5.3: Collapsed State Persists
**Preconditions**: Panel collapsed  
**Steps**:
1. Close the application
2. Restart the application
3. Observe the Now Playing Panel

**Expected Results**:
- Panel opens in collapsed state
- User preference is remembered
- State persists across sessions

**Priority**: Medium

---

### Test Case 5.4: Expanded State Persists
**Preconditions**: Panel expanded  
**Steps**:
1. Close the application
2. Restart the application
3. Observe the Now Playing Panel

**Expected Results**:
- Panel opens in expanded state
- User preference is remembered
- State persists across sessions

**Priority**: Medium

---

## Feature 6: Workspace Layout Integration

### Test Case 6.1: Save Layout Saves Panel State
**Preconditions**: Panel collapsed  
**Steps**:
1. Use View → Save Window Layout (Ctrl+Shift+L)
2. Expand the panel
3. Use View → Restore Window Layout (Ctrl+Shift+R)

**Expected Results**:
- Panel returns to collapsed state
- Saved layout includes panel state
- Layout restoration works correctly

**Priority**: Medium

---

### Test Case 6.2: Reset Layout Resets Panel
**Preconditions**: Panel collapsed  
**Steps**:
1. Use View → Reset to Default Layout
2. Observe the Now Playing Panel

**Expected Results**:
- Panel resets to default state (expanded)
- Other layout elements also reset
- Application remains stable

**Priority**: Low

---

## Feature 7: Multi-Tab Workflow

### Test Case 7.1: Add Annotation from Library Tab
**Preconditions**: Audio file playing, Library tab active  
**Steps**:
1. While in Library tab, add annotation via Now Playing Panel
2. Switch to Annotations tab

**Expected Results**:
- Annotation appears in Annotations tab
- No need to switch tabs to add annotation
- Workflow is faster and more efficient

**Priority**: High

---

### Test Case 7.2: Add Annotation from Folder Notes Tab
**Preconditions**: Audio file playing, Folder Notes tab active  
**Steps**:
1. While in Folder Notes tab, add annotation via Now Playing Panel
2. Switch to Annotations tab

**Expected Results**:
- Annotation appears in Annotations tab
- Can annotate while reading/writing folder notes
- Panel accessible from all tabs

**Priority**: High

---

### Test Case 7.3: Playback Control from Any Tab
**Preconditions**: Audio file loaded  
**Steps**:
1. Switch to Library tab
2. Click play in Now Playing Panel
3. Switch to Folder Notes tab
4. Click pause in Now Playing Panel

**Expected Results**:
- Playback controls work from all tabs
- No need to be in Annotations tab to control playback
- Panel functionality consistent across tabs

**Priority**: High

---

## Feature 8: Edge Cases and Error Handling

### Test Case 8.1: Long File Names Display
**Preconditions**: None  
**Steps**:
1. Play file with very long name (>50 characters)
2. Observe Now Playing Panel file name display

**Expected Results**:
- Long file name displays without breaking layout
- May be truncated with ellipsis if needed
- Panel remains properly sized
- No UI overflow or distortion

**Priority**: Medium

---

### Test Case 8.2: Rapid File Switching
**Preconditions**: Multiple files in folder  
**Steps**:
1. Rapidly switch between different files (5+ files quickly)
2. Observe Now Playing Panel updates

**Expected Results**:
- Panel updates correctly for each file
- No flickering or display issues
- Time displays correctly for each file
- No crashes or errors

**Priority**: Medium

---

### Test Case 8.3: Annotation with Special Characters
**Preconditions**: Audio file playing  
**Steps**:
1. Type annotation with special characters: "Test & <special> 'quotes' \"double\""
2. Press Enter
3. Check Annotations tab

**Expected Results**:
- Annotation is added correctly
- Special characters preserved
- No errors or corruption
- Annotation displays properly in table

**Priority**: Medium

---

### Test Case 8.4: Panel with No Audio File
**Preconditions**: Application started, no practice folder opened  
**Steps**:
1. Observe Now Playing Panel
2. Try clicking play button
3. Try typing in annotation field

**Expected Results**:
- Panel shows "No file loaded"
- Play button is disabled
- Annotation field is disabled
- No errors occur
- Application remains stable

**Priority**: Low

---

## Feature 9: Regression Tests

### Test Case 9.1: Existing Annotation Features Work
**Preconditions**: Audio file playing  
**Steps**:
1. Add annotation via Annotations tab annotation controls
2. Add annotation via Now Playing Panel
3. Verify both annotations in table

**Expected Results**:
- Both annotation methods work correctly
- No interference between methods
- All annotations visible and editable
- Categories, importance, undo all work

**Priority**: Critical

---

### Test Case 9.2: Main Player Controls Unaffected
**Preconditions**: Audio file playing  
**Steps**:
1. Use main player bar controls (seek, volume, speed, etc.)
2. Observe Now Playing Panel

**Expected Results**:
- Main player controls work normally
- Panel updates to reflect state changes
- No conflicts or issues
- All existing functionality preserved

**Priority**: Critical

---

### Test Case 9.3: Keyboard Shortcuts Still Work
**Preconditions**: Audio file playing  
**Steps**:
1. Test various keyboard shortcuts (Space for play/pause, N for annotation, etc.)
2. Observe Now Playing Panel

**Expected Results**:
- All keyboard shortcuts work as before
- Panel reflects state changes
- No shortcut conflicts
- Existing functionality preserved

**Priority**: High

---

## Test Execution Summary

### Test Coverage
- **Panel Display**: 2 test cases
- **File Loading**: 3 test cases
- **Playback Controls**: 2 test cases
- **Quick Annotation**: 6 test cases
- **Collapsible Panel**: 4 test cases
- **Workspace Layout**: 2 test cases
- **Multi-Tab Workflow**: 3 test cases
- **Edge Cases**: 4 test cases
- **Regression Tests**: 3 test cases

**Total Test Cases**: 29

### Test Execution Checklist

#### Critical Tests (Must Pass)
- [ ] Test Case 1.1: Panel Appears in Main Window
- [ ] Test Case 2.1: Panel Updates When File Loaded
- [ ] Test Case 3.1: Play/Pause Button Synchronization
- [ ] Test Case 4.1: Add Annotation via Text Entry
- [ ] Test Case 9.1: Existing Annotation Features Work
- [ ] Test Case 9.2: Main Player Controls Unaffected

#### High Priority Tests
- [ ] Test Case 1.2: Panel Position Remains Fixed
- [ ] Test Case 2.2: Panel Updates During Playback
- [ ] Test Case 2.3: Panel Clears When Playback Stops
- [ ] Test Case 3.2: Play Button Shortcuts Work
- [ ] Test Case 4.2: Add Annotation via Button
- [ ] Test Case 4.4: Annotation While Paused
- [ ] Test Case 4.5: Quick Annotations Integrate with Undo
- [ ] Test Case 4.6: Multiple Quick Annotations
- [ ] Test Case 5.1: Collapse Panel
- [ ] Test Case 5.2: Expand Panel
- [ ] Test Case 7.1: Add Annotation from Library Tab
- [ ] Test Case 7.2: Add Annotation from Folder Notes Tab
- [ ] Test Case 7.3: Playback Control from Any Tab
- [ ] Test Case 9.3: Keyboard Shortcuts Still Work

#### Medium Priority Tests
- [ ] Test Case 4.3: Empty Text Handling
- [ ] Test Case 5.3: Collapsed State Persists
- [ ] Test Case 5.4: Expanded State Persists
- [ ] Test Case 6.1: Save Layout Saves Panel State
- [ ] Test Case 8.1: Long File Names Display
- [ ] Test Case 8.2: Rapid File Switching
- [ ] Test Case 8.3: Annotation with Special Characters

#### Low Priority Tests
- [ ] Test Case 6.2: Reset Layout Resets Panel
- [ ] Test Case 8.4: Panel with No Audio File

---

## Known Limitations

1. **Mini Waveform**: Currently shows a simple progress indicator, not an actual waveform thumbnail. Future enhancement could render actual waveform.
2. **Quick Annotations**: Do not support categories or importance flags. Use Annotations tab for categorized annotations.
3. **Clip Annotations**: Quick annotation field only creates point annotations, not clip ranges.

---

## Bug Reporting Template

**Title**: [Now Playing Panel] Brief description

**Priority**: Critical / High / Medium / Low

**Test Case**: (if applicable)

**Steps to Reproduce**:
1. 
2. 
3. 

**Expected Behavior**:

**Actual Behavior**:

**Environment**:
- OS: 
- Python Version: 
- AudioBrowser Version: 

**Additional Notes**:

---

## Sign-Off

### Test Execution
- **Tester Name**: _________________
- **Test Date**: _________________
- **Build Version**: _________________

### Results Summary
- **Total Tests**: 29
- **Tests Passed**: _____
- **Tests Failed**: _____
- **Tests Blocked**: _____
- **Pass Rate**: _____%

### Approval
- **QA Lead**: _________________ Date: _________
- **Product Owner**: _________________ Date: _________

---

## Future Test Enhancements

1. **Automated Testing**: Convert manual tests to automated UI tests using pytest-qt
2. **Performance Tests**: Measure impact on application startup and playback performance
3. **Accessibility Testing**: Screen reader compatibility, keyboard-only navigation
4. **Visual Regression Tests**: Capture screenshots to detect unintended visual changes
5. **Cross-Platform Testing**: Dedicated test runs on Windows, macOS, and Linux
6. **Integration Tests**: Test interaction with all other major features (Practice Goals, Setlists, etc.)
