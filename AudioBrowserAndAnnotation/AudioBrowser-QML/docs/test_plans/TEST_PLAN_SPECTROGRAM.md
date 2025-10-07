# Test Plan: Spectrogram Overlay Feature

**Feature**: Spectrogram Overlay Visualization  
**Implementation**: Issue #7  
**Test Plan Version**: 1.0  
**Date**: January 2025

---

## Overview

This test plan covers the spectrogram overlay feature that provides frequency analysis visualization for audio files. The feature uses Short-Time Fourier Transform (STFT) to display frequency content over time.

---

## Test Environment Requirements

### Hardware
- Computer with minimum 4GB RAM
- Audio output device (for playback testing)
- Display capable of showing color gradients accurately

### Software
- AudioBrowser-QML installed and working
- Python 3.8 or higher
- PyQt6 installed
- NumPy installed (`pip install numpy`)
- Test audio files:
  - Short WAV file (< 3 min)
  - Long WAV file (5-10 min)
  - MP3 file (any length)
  - Quiet recording
  - Loud recording
  - Recording with distinct frequency content (e.g., bass-heavy, treble-heavy)

### Prerequisites
- Application launches successfully
- Normal waveform view works correctly
- Audio playback works correctly

---

## Test Cases

### Category 1: Basic Functionality

#### TC-1.1: Toggle Spectrogram On
**Objective**: Verify spectrogram can be enabled  
**Prerequisites**: Application running, audio file loaded  
**Steps**:
1. Navigate to Annotations tab
2. Locate "Spectrogram" checkbox in toolbar
3. Check the checkbox

**Expected Results**:
- ✓ Checkbox becomes checked
- ✓ Waveform display changes to spectrogram view
- ✓ Frequency content visible with color gradient
- ✓ Y-axis shows frequency (low at bottom, high at top)
- ✓ X-axis shows time (same as waveform)
- ✓ Status: [ ] PASS [ ] FAIL

---

#### TC-1.2: Toggle Spectrogram Off
**Objective**: Verify can toggle back to waveform  
**Prerequisites**: Spectrogram view enabled  
**Steps**:
1. Uncheck the "Spectrogram" checkbox

**Expected Results**:
- ✓ Checkbox becomes unchecked
- ✓ Display changes back to waveform view
- ✓ Normal waveform visible
- ✓ Status: [ ] PASS [ ] FAIL

---

#### TC-1.3: Tooltip Display
**Objective**: Verify tooltip appears  
**Prerequisites**: Application running  
**Steps**:
1. Navigate to Annotations tab
2. Hover mouse over "Spectrogram" checkbox
3. Wait 0.5 seconds

**Expected Results**:
- ✓ Tooltip appears
- ✓ Tooltip text: "Show spectrogram view (frequency analysis)"
- ✓ Tooltip disappears when mouse moves away
- ✓ Status: [ ] PASS [ ] FAIL

---

### Category 2: Spectrogram Computation

#### TC-2.1: First Computation (Short File)
**Objective**: Verify spectrogram computes for short audio file  
**Prerequisites**: Short WAV file (< 3 min) loaded  
**Steps**:
1. Enable spectrogram view for first time on this file
2. Observe computation time

**Expected Results**:
- ✓ Spectrogram computes without errors
- ✓ Computation time < 3 seconds
- ✓ Application remains responsive during computation
- ✓ Spectrogram displays with correct colors
- ✓ Status: [ ] PASS [ ] FAIL

---

#### TC-2.2: First Computation (Long File)
**Objective**: Verify spectrogram computes for long audio file  
**Prerequisites**: Long WAV file (5-10 min) loaded  
**Steps**:
1. Enable spectrogram view for first time on this file
2. Observe computation time

**Expected Results**:
- ✓ Spectrogram computes without errors
- ✓ Computation time < 10 seconds
- ✓ Application remains responsive
- ✓ Spectrogram displays correctly
- ✓ Status: [ ] PASS [ ] FAIL

---

#### TC-2.3: Caching Test
**Objective**: Verify spectrogram is cached after first computation  
**Prerequisites**: Spectrogram computed once  
**Steps**:
1. Toggle spectrogram off
2. Toggle spectrogram on again

**Expected Results**:
- ✓ Spectrogram displays instantly (< 0.1 seconds)
- ✓ No recomputation delay
- ✓ Display identical to first time
- ✓ Status: [ ] PASS [ ] FAIL

---

#### TC-2.4: Cache Invalidation
**Objective**: Verify cache clears when file changes  
**Prerequisites**: Spectrogram cached for file A  
**Steps**:
1. Load different file B
2. Enable spectrogram view

**Expected Results**:
- ✓ New spectrogram computed (not instant)
- ✓ Spectrogram shows file B's frequency content
- ✓ No visual artifacts from file A
- ✓ Status: [ ] PASS [ ] FAIL

---

#### TC-2.5: MP3 Support
**Objective**: Verify spectrogram works with MP3 files  
**Prerequisites**: MP3 file loaded  
**Steps**:
1. Enable spectrogram view

**Expected Results**:
- ✓ Spectrogram computes without errors
- ✓ Display quality similar to WAV files
- ✓ No decoding errors
- ✓ Status: [ ] PASS [ ] FAIL

---

### Category 3: Color Gradient

#### TC-3.1: Color Mapping (Quiet File)
**Objective**: Verify color mapping for quiet recording  
**Prerequisites**: Quiet audio file loaded  
**Steps**:
1. Enable spectrogram view
2. Observe color distribution

**Expected Results**:
- ✓ Mostly blue colors (low magnitude)
- ✓ Some green in frequency ranges with content
- ✓ Minimal yellow/red
- ✓ Colors match magnitude correctly
- ✓ Status: [ ] PASS [ ] FAIL

---

#### TC-3.2: Color Mapping (Loud File)
**Objective**: Verify color mapping for loud recording  
**Prerequisites**: Loud audio file loaded  
**Steps**:
1. Enable spectrogram view
2. Observe color distribution

**Expected Results**:
- ✓ More yellow and red colors (high magnitude)
- ✓ Colors brighter overall
- ✓ Frequency ranges with most energy show red
- ✓ Colors accurately represent magnitude
- ✓ Status: [ ] PASS [ ] FAIL

---

#### TC-3.3: Frequency Range Visualization
**Objective**: Verify correct frequency range display  
**Prerequisites**: Audio file with known frequency content  
**Steps**:
1. Load bass-heavy recording (lots of low frequencies)
2. Enable spectrogram view
3. Observe bottom of display

**Expected Results**:
- ✓ Bottom portion shows more color (low frequencies)
- ✓ Low frequencies at bottom, high at top
- ✓ Frequency axis inverted correctly
- ✓ Status: [ ] PASS [ ] FAIL

---

### Category 4: Integration with Existing Features

#### TC-4.1: Playback Position
**Objective**: Verify playhead displays on spectrogram  
**Prerequisites**: Spectrogram view enabled  
**Steps**:
1. Start audio playback
2. Observe playhead line

**Expected Results**:
- ✓ Red playhead line visible on spectrogram
- ✓ Playhead moves smoothly with playback
- ✓ Playhead easy to see against spectrogram colors
- ✓ Playhead position accurate
- ✓ Status: [ ] PASS [ ] FAIL

---

#### TC-4.2: Click-to-Seek
**Objective**: Verify seeking works on spectrogram  
**Prerequisites**: Spectrogram view enabled, audio loaded  
**Steps**:
1. Click at various positions on spectrogram
2. Verify audio seeks to correct position

**Expected Results**:
- ✓ Click seeks to correct time position
- ✓ Playhead moves to click position
- ✓ Audio playback continues from new position
- ✓ Seek accuracy similar to waveform mode
- ✓ Status: [ ] PASS [ ] FAIL

---

#### TC-4.3: Tempo Markers Integration
**Objective**: Verify tempo markers display on spectrogram  
**Prerequisites**: Audio file with BPM set, spectrogram enabled  
**Steps**:
1. Set BPM for current file (e.g., 120 BPM)
2. Enable spectrogram view
3. Observe measure markers

**Expected Results**:
- ✓ Gray dashed vertical lines visible
- ✓ Measure numbers (M4, M8, M12...) visible
- ✓ Markers aligned with musical timing
- ✓ Markers don't obscure spectrogram
- ✓ Status: [ ] PASS [ ] FAIL

---

#### TC-4.4: Zoom Controls
**Objective**: Verify zoom works with spectrogram  
**Prerequisites**: Spectrogram view enabled  
**Steps**:
1. Click "+" zoom button
2. Scroll horizontally
3. Click "−" zoom button
4. Click "Reset" button

**Expected Results**:
- ✓ Zoom in works, spectrogram stretches horizontally
- ✓ Horizontal scroll bar appears when zoomed
- ✓ Scroll works smoothly
- ✓ Zoom out works correctly
- ✓ Reset returns to normal zoom
- ✓ Status: [ ] PASS [ ] FAIL

---

#### TC-4.5: Generate Waveform Button
**Objective**: Verify generate button works with spectrogram  
**Prerequisites**: Audio file loaded  
**Steps**:
1. Enable spectrogram view
2. Click "Generate" button
3. Wait for generation to complete

**Expected Results**:
- ✓ Waveform generates successfully
- ✓ Spectrogram cache cleared automatically
- ✓ New spectrogram computed after generation
- ✓ No errors or crashes
- ✓ Status: [ ] PASS [ ] FAIL

---

### Category 5: Edge Cases

#### TC-5.1: No Audio File
**Objective**: Verify behavior with no file loaded  
**Prerequisites**: No audio file loaded  
**Steps**:
1. Navigate to Annotations tab
2. Attempt to enable spectrogram

**Expected Results**:
- ✓ Checkbox can be checked
- ✓ No errors occur
- ✓ Display shows empty/background only
- ✓ Application doesn't crash
- ✓ Status: [ ] PASS [ ] FAIL

---

#### TC-5.2: Silent Audio
**Objective**: Verify behavior with silent audio  
**Prerequisites**: Silent audio file loaded  
**Steps**:
1. Enable spectrogram view

**Expected Results**:
- ✓ Spectrogram displays (all blue)
- ✓ No errors or crashes
- ✓ Blue colors indicate low magnitude correctly
- ✓ Status: [ ] PASS [ ] FAIL

---

#### TC-5.3: Very Short File
**Objective**: Verify behavior with very short audio (< 1 second)  
**Prerequisites**: Very short audio file loaded  
**Steps**:
1. Enable spectrogram view

**Expected Results**:
- ✓ Spectrogram computes without errors
- ✓ Display shows compressed time axis
- ✓ Frequency content visible
- ✓ Status: [ ] PASS [ ] FAIL

---

#### TC-5.4: NumPy Not Installed
**Objective**: Verify graceful degradation without NumPy  
**Prerequisites**: NumPy uninstalled (test in separate environment)  
**Steps**:
1. Attempt to enable spectrogram view

**Expected Results**:
- ✓ Checkbox becomes checked
- ✓ Display falls back to waveform view
- ✓ Error message in console: "NumPy not available - spectrogram disabled"
- ✓ Application doesn't crash
- ✓ Status: [ ] PASS [ ] FAIL

---

#### TC-5.5: Corrupted Audio File
**Objective**: Verify error handling for corrupted file  
**Prerequisites**: Corrupted audio file loaded  
**Steps**:
1. Attempt to enable spectrogram view

**Expected Results**:
- ✓ Error caught gracefully
- ✓ Error message in console
- ✓ Display falls back to waveform or shows empty
- ✓ Application doesn't crash
- ✓ Status: [ ] PASS [ ] FAIL

---

### Category 6: Performance

#### TC-6.1: Memory Usage
**Objective**: Verify memory usage is acceptable  
**Prerequisites**: Multiple audio files loaded and spectrograms computed  
**Steps**:
1. Load 10 different audio files
2. Enable spectrogram view for each
3. Monitor memory usage

**Expected Results**:
- ✓ Memory increase < 50 MB for 10 files
- ✓ No memory leaks (memory stable over time)
- ✓ Memory freed when application closes
- ✓ Status: [ ] PASS [ ] FAIL

---

#### TC-6.2: Responsiveness
**Objective**: Verify application remains responsive  
**Prerequisites**: Long audio file computing spectrogram  
**Steps**:
1. Enable spectrogram for long file
2. During computation, try to:
   - Move window
   - Click other buttons
   - Switch tabs

**Expected Results**:
- ✓ Window moves smoothly
- ✓ Other buttons respond (though may queue)
- ✓ Tab switching works
- ✓ Application doesn't freeze
- ✓ Status: [ ] PASS [ ] FAIL

---

#### TC-6.3: Toggle Performance
**Objective**: Verify toggle is instant with cached data  
**Prerequisites**: Spectrogram cached  
**Steps**:
1. Toggle spectrogram off and on 10 times rapidly

**Expected Results**:
- ✓ Each toggle completes instantly (< 0.1 sec)
- ✓ Display updates immediately
- ✓ No lag or stuttering
- ✓ Status: [ ] PASS [ ] FAIL

---

### Category 7: Regression Testing

#### TC-7.1: Normal Waveform Still Works
**Objective**: Verify waveform mode unchanged  
**Prerequisites**: Spectrogram feature installed  
**Steps**:
1. Load audio file
2. Keep spectrogram toggle OFF
3. Use normal waveform features

**Expected Results**:
- ✓ Waveform displays correctly
- ✓ All waveform features work as before
- ✓ No performance degradation
- ✓ Status: [ ] PASS [ ] FAIL

---

#### TC-7.2: Existing Tests Still Pass
**Objective**: Verify no regressions in existing functionality  
**Prerequisites**: Test suite available  
**Steps**:
1. Run existing test suite
2. Check all tests pass

**Expected Results**:
- ✓ test_structure.py passes
- ✓ test_waveform_syntax.py passes
- ✓ test_spectrogram_syntax.py passes (new)
- ✓ No new test failures
- ✓ Status: [ ] PASS [ ] FAIL

---

## Test Execution Summary

**Test Execution Date**: _______________  
**Tester Name**: _______________  
**Environment**: _______________

| Category | Total | Passed | Failed | Blocked |
|----------|-------|--------|--------|---------|
| Basic Functionality | 3 | ___ | ___ | ___ |
| Spectrogram Computation | 5 | ___ | ___ | ___ |
| Color Gradient | 3 | ___ | ___ | ___ |
| Integration | 5 | ___ | ___ | ___ |
| Edge Cases | 5 | ___ | ___ | ___ |
| Performance | 3 | ___ | ___ | ___ |
| Regression | 2 | ___ | ___ | ___ |
| **TOTAL** | **26** | ___ | ___ | ___ |

**Pass Rate**: _____ %  
**Overall Status**: [ ] PASS [ ] FAIL [ ] PARTIAL

---

## Known Issues

| Issue # | Description | Severity | Workaround |
|---------|-------------|----------|------------|
| | | | |
| | | | |

---

## Bug Reporting Template

**Bug ID**: ___________  
**Test Case**: ___________  
**Severity**: ☐ Critical ☐ Major ☐ Minor ☐ Cosmetic  

**Description**: _______________________________________________  

**Steps to Reproduce**:
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

**Expected Result**: _______________________________________________  

**Actual Result**: _______________________________________________  

**Screenshots/Logs**: _______________________________________________  

**Environment Details**:
- OS: _______________
- Python Version: _______________
- PyQt6 Version: _______________
- NumPy Version: _______________

---

## Sign-off

**Test Plan Reviewed By**: _________________  
**Date**: _________________  

**Testing Completed By**: _________________  
**Date**: _________________  

**Approved for Release**: _________________  
**Date**: _________________  

---

## Notes

- Execute tests in order for best results
- Document any deviations from expected results
- Take screenshots for visual issues
- Check console output for errors
- Test with various audio file types and lengths

---

**Test Plan Version**: 1.0  
**Last Updated**: January 2025  
**Author**: AudioBrowser-QML Development Team
