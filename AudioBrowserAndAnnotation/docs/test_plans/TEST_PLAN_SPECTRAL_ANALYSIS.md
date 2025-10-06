# Test Plan: Spectral Analysis (Advanced Audio Analysis)

**Feature Set**: Section 6.1 (Advanced Audio Analysis)  
**Implementation Date**: January 2025  
**Test Plan Version**: 1.0

---

## Overview

This test plan covers the Spectral Analysis feature, which provides advanced audio visualization through spectrogram view. Users can:
- Toggle between waveform and spectrogram view
- Visualize frequency content over time
- Identify frequency issues and patterns
- Analyze audio characteristics in the frequency domain

The feature helps bands analyze recordings in more detail, identifying frequency problems, resonances, and tonal characteristics.

---

## Test Environment Requirements

### Software Requirements
- AudioBrowser application (version with Spectral Analysis feature)
- Python 3.8 or higher
- PyQt6
- NumPy (automatically installed)
- Operating System: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)

### Test Data Requirements
- At least 5-10 audio files (WAV or MP3 format)
- Various song types (different instruments, vocals, full band)
- Different audio quality levels
- Practice folder with existing metadata files

---

## Feature 1: Spectrogram Toggle

### Test Case 1.1: Spectrogram Checkbox Appears
**Objective**: Verify spectrogram toggle checkbox is visible in Annotations tab  
**Preconditions**: Practice folder is open with at least one audio file  
**Steps**:
1. Open a practice folder with audio files
2. Navigate to Annotations tab
3. Locate waveform controls section
4. Look for "Spectrogram" checkbox

**Expected Results**:
- "Spectrogram" checkbox is visible next to stereo/mono toggle
- Checkbox is unchecked by default
- Tooltip displays: "Show spectrogram view (frequency analysis)"
- Checkbox is enabled when a file is loaded

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 1.2: Toggle to Spectrogram View
**Objective**: Verify spectrogram view activates when checkbox is checked  
**Preconditions**: Audio file is loaded in Annotations tab  
**Steps**:
1. Select an audio file from the file tree
2. Wait for waveform to load
3. Check the "Spectrogram" checkbox
4. Observe the waveform display

**Expected Results**:
- Waveform display transitions to spectrogram view
- Spectrogram shows frequency content over time
- Colors represent magnitude (blue=low, green=medium, yellow-red=high)
- Time axis remains the same (horizontal)
- Frequency axis is vertical (low frequencies at bottom)

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 1.3: Toggle Back to Waveform View
**Objective**: Verify return to waveform view when checkbox is unchecked  
**Preconditions**: Spectrogram view is active  
**Steps**:
1. With spectrogram view showing
2. Uncheck the "Spectrogram" checkbox
3. Observe the display

**Expected Results**:
- Display returns to normal waveform view
- All waveform features work normally (annotations, markers, etc.)
- No errors or visual glitches
- Transition is smooth

**Pass/Fail**: ___  
**Notes**: ___

---

## Feature 2: Spectrogram Computation

### Test Case 2.1: Spectrogram Computation on First Toggle
**Objective**: Verify spectrogram is computed when first activated  
**Preconditions**: Audio file is loaded, spectrogram not yet computed  
**Steps**:
1. Load an audio file
2. Check "Spectrogram" checkbox for the first time
3. Observe computation time and status

**Expected Results**:
- Spectrogram is computed (may take 1-3 seconds for typical files)
- No error messages appear
- Application remains responsive during computation
- Spectrogram displays correctly after computation

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 2.2: Cached Spectrogram on Subsequent Toggles
**Objective**: Verify spectrogram uses cached data after first computation  
**Preconditions**: Spectrogram has been computed once  
**Steps**:
1. With spectrogram showing, toggle off
2. Toggle spectrogram back on
3. Observe display time

**Expected Results**:
- Spectrogram appears immediately (< 0.5 seconds)
- No recomputation occurs
- Display is identical to first computation
- No performance degradation

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 2.3: Spectrogram for Different Audio Files
**Objective**: Verify spectrogram works with various audio file types  
**Preconditions**: Multiple audio files available (WAV, MP3)  
**Steps**:
1. Load a WAV file, enable spectrogram
2. Load an MP3 file, enable spectrogram
3. Load files of different lengths (short, medium, long)
4. Compare spectrograms

**Expected Results**:
- Spectrogram works for both WAV and MP3 files
- Spectrogram scales appropriately for different file lengths
- Different audio content shows different frequency patterns
- No errors with any supported audio format

**Pass/Fail**: ___  
**Notes**: ___

---

## Feature 3: Spectrogram Visualization

### Test Case 3.1: Color Mapping
**Objective**: Verify spectrogram color mapping represents magnitude correctly  
**Preconditions**: Spectrogram view is active  
**Steps**:
1. Enable spectrogram for an audio file
2. Observe colors in different frequency regions
3. Identify quiet sections (low magnitude)
4. Identify loud sections (high magnitude)

**Expected Results**:
- Blue colors = low magnitude (quiet)
- Green colors = medium magnitude
- Yellow-red colors = high magnitude (loud)
- Color transitions are smooth (no banding artifacts)
- Silent sections show predominantly blue

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 3.2: Frequency Range Display
**Objective**: Verify appropriate frequency range is displayed  
**Preconditions**: Spectrogram view is active  
**Steps**:
1. Enable spectrogram
2. Observe frequency distribution (low at bottom, high at top)
3. Compare spectrogram of bass-heavy vs. treble-heavy audio

**Expected Results**:
- Frequency range focuses on musical range (60-8000 Hz)
- Low frequencies (bass) appear at bottom
- High frequencies (treble) appear at top
- Log-scale frequency axis (more detail in low frequencies)
- Appropriate detail for musical analysis

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 3.3: Time Resolution
**Objective**: Verify time resolution matches waveform  
**Preconditions**: Both waveform and spectrogram views available  
**Steps**:
1. View waveform, note positions of events (e.g., drum hits)
2. Switch to spectrogram view
3. Compare timing of events in spectrogram

**Expected Results**:
- Events appear at same horizontal positions
- Time resolution is adequate for musical analysis
- No significant time-stretching or compression artifacts
- Playhead position matches in both views

**Pass/Fail**: ___  
**Notes**: ___

---

## Feature 4: Integration with Existing Features

### Test Case 4.1: Annotations Display on Spectrogram
**Objective**: Verify annotation markers display correctly on spectrogram  
**Preconditions**: Audio file has annotations  
**Steps**:
1. Load a file with annotations
2. Enable spectrogram view
3. Observe annotation markers

**Expected Results**:
- Annotation markers (vertical lines) display on spectrogram
- Marker colors are preserved
- Markers are clickable and function normally
- Selected marker highlighting works

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 4.2: Loop Markers on Spectrogram
**Objective**: Verify A-B loop markers display on spectrogram  
**Preconditions**: Loop markers are set  
**Steps**:
1. Set A-B loop markers on waveform
2. Switch to spectrogram view
3. Verify loop markers are visible

**Expected Results**:
- Loop markers (A and B) display on spectrogram
- Loop region is highlighted appropriately
- Loop marker labels are visible
- Loop functionality works with spectrogram view

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 4.3: Tempo Markers on Spectrogram
**Objective**: Verify tempo markers display on spectrogram  
**Preconditions**: BPM is set for the song  
**Steps**:
1. Set BPM in Library tab
2. Switch to Annotations tab
3. Enable spectrogram view
4. Observe tempo markers

**Expected Results**:
- Tempo measure lines display on spectrogram
- Measure numbers are visible
- Tempo markers don't obscure frequency information
- Markers are appropriately subtle

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 4.4: Playhead Position in Spectrogram
**Objective**: Verify playhead displays correctly during playback  
**Preconditions**: Audio is playing  
**Steps**:
1. Enable spectrogram view
2. Start audio playback
3. Observe playhead movement

**Expected Results**:
- Playhead (red vertical line) displays on spectrogram
- Playhead moves smoothly with playback
- Playhead position is accurate
- Playhead is easily visible against spectrogram colors

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 4.5: Seek by Clicking in Spectrogram
**Objective**: Verify clicking in spectrogram seeks playback position  
**Preconditions**: Spectrogram view is active  
**Steps**:
1. Enable spectrogram view
2. Click at various positions in spectrogram
3. Verify playback seeks to clicked position

**Expected Results**:
- Clicking in spectrogram seeks playback
- Seek position is accurate
- Seeking works throughout entire spectrogram
- No errors during seeking

**Pass/Fail**: ___  
**Notes**: ___

---

## Feature 5: Performance

### Test Case 5.1: Short Files (< 3 minutes)
**Objective**: Verify spectrogram computation performance for short files  
**Preconditions**: Short audio file loaded  
**Steps**:
1. Load a file under 3 minutes
2. Enable spectrogram
3. Measure computation time

**Expected Results**:
- Computation completes in < 2 seconds
- Application remains responsive
- No lag or freezing
- Immediate feedback to user

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 5.2: Long Files (> 10 minutes)
**Objective**: Verify spectrogram computation for long files  
**Preconditions**: Long audio file loaded  
**Steps**:
1. Load a file over 10 minutes
2. Enable spectrogram
3. Measure computation time
4. Monitor application responsiveness

**Expected Results**:
- Computation completes in reasonable time (< 10 seconds)
- Progress indication if computation takes > 2 seconds
- Application remains responsive (not frozen)
- Spectrogram displays correctly once computed

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 5.3: Multiple File Switches
**Objective**: Verify performance when switching between multiple files  
**Preconditions**: Multiple files in practice folder  
**Steps**:
1. Enable spectrogram for file 1
2. Switch to file 2 (spectrogram auto-enabled)
3. Switch to file 3
4. Return to file 1
5. Repeat several times

**Expected Results**:
- First computation for each file takes normal time
- Cached spectrograms load instantly on return
- No memory leaks or performance degradation
- Application remains stable

**Pass/Fail**: ___  
**Notes**: ___

---

## Feature 6: Edge Cases and Error Handling

### Test Case 6.1: Spectrogram with Empty/Silent Audio
**Objective**: Verify handling of silent audio files  
**Preconditions**: Audio file with silence or very low amplitude  
**Steps**:
1. Load a nearly silent audio file
2. Enable spectrogram view
3. Observe display

**Expected Results**:
- Spectrogram displays (mostly blue/low magnitude)
- No errors or crashes
- Application remains stable
- Can toggle back to waveform normally

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 6.2: Spectrogram Without NumPy
**Objective**: Verify graceful degradation if NumPy unavailable  
**Preconditions**: Test environment without NumPy (if possible)  
**Steps**:
1. Uninstall NumPy (if possible in test environment)
2. Try to enable spectrogram
3. Observe behavior

**Expected Results**:
- Checkbox is present but may be disabled
- Appropriate message if feature unavailable
- No crashes or errors
- Application continues to function normally

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 6.3: Corrupted Audio File
**Objective**: Verify handling of corrupted audio data  
**Preconditions**: Corrupted or malformed audio file  
**Steps**:
1. Load a corrupted audio file
2. Try to enable spectrogram
3. Observe error handling

**Expected Results**:
- Appropriate error message if computation fails
- Application remains stable (no crash)
- Can try with different files
- Error logged appropriately

**Pass/Fail**: ___  
**Notes**: ___

---

## Feature 7: User Interface

### Test Case 7.1: Checkbox State Persistence
**Objective**: Verify spectrogram checkbox state persists across sessions  
**Preconditions**: None  
**Steps**:
1. Enable spectrogram checkbox
2. Close and reopen application
3. Open same practice folder
4. Check spectrogram checkbox state

**Expected Results**:
- Checkbox state persists across sessions (via QSettings)
- Last-used state is restored
- No errors on restore

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 7.2: Tooltip Information
**Objective**: Verify tooltip provides helpful information  
**Preconditions**: None  
**Steps**:
1. Hover over "Spectrogram" checkbox
2. Read tooltip

**Expected Results**:
- Tooltip appears within 1 second
- Text: "Show spectrogram view (frequency analysis)"
- Text is clear and informative
- Tooltip doesn't obstruct interface

**Pass/Fail**: ___  
**Notes**: ___

---

## Feature 8: Regression Tests

### Test Case 8.1: Normal Waveform View Unaffected
**Objective**: Verify waveform view works normally when spectrogram is disabled  
**Preconditions**: Spectrogram feature implemented  
**Steps**:
1. Keep spectrogram checkbox unchecked
2. Use waveform view normally
3. Test all waveform features

**Expected Results**:
- Waveform view works exactly as before
- No performance degradation
- No visual changes to waveform
- All existing features function normally

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 8.2: Stereo Mode Compatibility
**Objective**: Verify spectrogram works with stereo mode  
**Preconditions**: Audio file has stereo data  
**Steps**:
1. Enable stereo mode
2. Enable spectrogram
3. Toggle between stereo/mono
4. Observe spectrogram behavior

**Expected Results**:
- Spectrogram uses left channel (or mixed) for stereo files
- Mode switching doesn't break spectrogram
- Spectrogram recomputes if necessary
- No errors with stereo files

**Pass/Fail**: ___  
**Notes**: ___

---

## Known Limitations

1. **Computation Time**: Initial spectrogram computation may take 1-10 seconds depending on file length
2. **NumPy Required**: Feature requires NumPy to be installed
3. **Memory Usage**: Spectrogram data increases memory usage slightly (typically < 5MB per file)
4. **Mono Analysis**: Stereo files use left channel only for spectrogram
5. **Frequency Range**: Displays 60-8000 Hz (musical range), not full spectrum

---

## Test Execution Summary

### Test Execution Checklist

#### Critical Tests (Must Pass)
- [ ] Test Case 1.2: Toggle to Spectrogram View
- [ ] Test Case 2.1: Spectrogram Computation on First Toggle
- [ ] Test Case 3.1: Color Mapping
- [ ] Test Case 4.1: Annotations Display on Spectrogram
- [ ] Test Case 5.1: Short Files Performance
- [ ] Test Case 8.1: Normal Waveform View Unaffected

#### High Priority Tests
- [ ] Test Case 1.3: Toggle Back to Waveform View
- [ ] Test Case 2.3: Spectrogram for Different Audio Files
- [ ] Test Case 3.2: Frequency Range Display
- [ ] Test Case 4.4: Playhead Position in Spectrogram
- [ ] Test Case 5.2: Long Files Performance
- [ ] Test Case 6.1: Spectrogram with Empty/Silent Audio

#### Medium Priority Tests
- [ ] Test Case 2.2: Cached Spectrogram
- [ ] Test Case 3.3: Time Resolution
- [ ] Test Case 4.2: Loop Markers on Spectrogram
- [ ] Test Case 4.3: Tempo Markers on Spectrogram
- [ ] Test Case 5.3: Multiple File Switches
- [ ] Test Case 7.1: Checkbox State Persistence

---

## Bug Reporting Template

**Bug ID**: ___  
**Test Case**: ___  
**Severity**: Critical / High / Medium / Low  
**Description**: ___  
**Steps to Reproduce**:
1. ___
2. ___
3. ___

**Expected Result**: ___  
**Actual Result**: ___  
**Screenshots**: ___  
**Environment**: OS: ___ | Python: ___ | AudioBrowser Version: ___  
**Additional Notes**: ___

---

## Sign-Off

### Test Execution
- **Tester Name**: _________________
- **Test Date**: _________________
- **Build Version**: _________________

### Results Summary
- **Total Tests**: 35
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
2. **Performance Benchmarks**: Establish baseline performance metrics for various file sizes
3. **Visual Regression Tests**: Capture spectrogram screenshots to detect rendering changes
4. **Accessibility Testing**: Verify color blindness compatibility of colormap
5. **Cross-Platform Testing**: Dedicated test runs on Windows, macOS, and Linux
6. **Memory Profiling**: Monitor memory usage with large libraries and many spectrograms
7. **Frequency Accuracy Tests**: Validate frequency axis accuracy against known test signals
