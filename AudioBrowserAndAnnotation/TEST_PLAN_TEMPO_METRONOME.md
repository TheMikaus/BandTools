# Test Plan: Tempo & Metronome Integration

**Feature Set**: Section 3.3 (Tempo & Metronome Integration)  
**Implementation Date**: January 2025  
**Test Plan Version**: 1.0

---

## Overview

This test plan covers the Tempo & Metronome Integration feature, which allows users to:
- Set BPM (Beats Per Minute) for each song
- View visual tempo markers (measure lines) on the waveform
- Store tempo data persistently across sessions

The feature helps bands analyze timing, identify tempo issues, and practice with visual measure guides.

---

## Test Environment Requirements

### Software Requirements
- AudioBrowser application (version with Tempo feature)
- Python 3.8 or higher
- PyQt6
- Operating System: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)

### Test Data Requirements
- At least 5-10 audio files (WAV or MP3 format)
- Various song lengths (2-10 minutes)
- Practice folder with existing metadata files

---

## Feature 1: BPM Entry in Library Tab

### Test Case 1.1: Enter BPM for a Song
**Objective**: Verify user can enter BPM in the Library tab  
**Preconditions**: Practice folder is open with at least one audio file  
**Steps**:
1. Open a practice folder with audio files
2. Navigate to Library tab
3. Locate the "BPM" column (between "Partial Take" and "Provided Name")
4. Double-click a cell in the BPM column
5. Enter a valid BPM value (e.g., "120")
6. Press Enter or click elsewhere to save

**Expected Results**:
- BPM column is visible and editable
- Entered BPM value is saved and displayed as integer
- `.tempo.json` file is created in the practice folder
- No error messages appear

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 1.2: BPM Value Validation - Valid Range
**Objective**: Verify BPM accepts values in the valid range  
**Preconditions**: Practice folder is open  
**Steps**:
1. Try entering BPM values: 40, 60, 120, 180, 240, 300
2. Verify each value is accepted

**Expected Results**:
- All values from 1-300 are accepted
- Values are displayed as integers
- `.tempo.json` is updated after each entry

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 1.3: BPM Value Validation - Out of Range
**Objective**: Verify BPM rejects invalid values  
**Preconditions**: Practice folder is open  
**Steps**:
1. Try entering BPM: 0
2. Try entering BPM: -50
3. Try entering BPM: 301
4. Try entering BPM: 500

**Expected Results**:
- Warning message appears: "BPM must be between 1 and 300"
- Previous value (or empty) is restored
- Invalid value is not saved

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 1.4: BPM Value Validation - Non-Numeric
**Objective**: Verify BPM rejects non-numeric input  
**Preconditions**: Practice folder is open  
**Steps**:
1. Try entering: "abc"
2. Try entering: "12.5x"
3. Try entering: "fast"

**Expected Results**:
- Previous value (or empty) is restored
- Invalid input is not saved
- No crash or error

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 1.5: Clear BPM Value
**Objective**: Verify user can remove BPM from a song  
**Preconditions**: Song has a BPM value set  
**Steps**:
1. Double-click BPM cell with existing value
2. Clear the text (delete all characters)
3. Press Enter

**Expected Results**:
- BPM cell becomes empty
- Tempo data is removed from `.tempo.json`
- Waveform tempo markers disappear if song is currently playing

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 1.6: BPM Column Resize
**Objective**: Verify BPM column resizes properly  
**Preconditions**: Library tab is open  
**Steps**:
1. Hover over column border between "BPM" and adjacent columns
2. Drag to resize
3. Verify content is visible

**Expected Results**:
- Column resizes smoothly
- BPM values remain visible
- No layout issues

**Pass/Fail**: ___  
**Notes**: ___

---

## Feature 2: Visual Tempo Markers on Waveform

### Test Case 2.1: Tempo Markers Appear with Valid BPM
**Objective**: Verify tempo markers display on waveform when BPM is set  
**Preconditions**: Practice folder is open  
**Steps**:
1. Select an audio file
2. Set BPM in Library tab (e.g., "120")
3. Switch to Annotations tab to view waveform
4. Observe waveform display

**Expected Results**:
- Vertical dashed gray lines appear on waveform at regular intervals
- Lines represent measure boundaries (4 beats per measure in 4/4 time)
- Measure numbers appear at every 4th measure (M4, M8, M12, etc.)
- Markers span full height of waveform

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 2.2: Tempo Markers Update When BPM Changes
**Objective**: Verify markers update when BPM is changed  
**Preconditions**: Song is playing with BPM set to 120  
**Steps**:
1. Play a file with BPM = 120
2. View waveform in Annotations tab
3. Switch to Library tab
4. Change BPM to 100
5. Return to Annotations tab

**Expected Results**:
- Tempo markers update immediately
- Spacing between markers changes to reflect new BPM
- Measure numbers update correctly

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 2.3: No Tempo Markers Without BPM
**Objective**: Verify no markers appear when BPM is not set  
**Preconditions**: Practice folder is open  
**Steps**:
1. Select an audio file without BPM set (empty BPM cell)
2. View waveform in Annotations tab

**Expected Results**:
- No tempo markers appear on waveform
- Waveform displays normally otherwise
- Other markers (annotations, loops) still visible

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 2.4: Tempo Markers with Different BPM Values
**Objective**: Verify tempo markers work correctly at various BPM  
**Preconditions**: Practice folder is open  
**Steps**:
1. Test with BPM = 60 (slow)
2. Test with BPM = 120 (medium)
3. Test with BPM = 180 (fast)
4. Test with BPM = 240 (very fast)

**Expected Results**:
- Slower BPM: markers are farther apart
- Faster BPM: markers are closer together
- Visual appearance is clean and readable at all speeds
- Measure numbers don't overlap

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 2.5: Tempo Markers Don't Interfere with Other Markers
**Objective**: Verify tempo markers coexist with annotations and loops  
**Preconditions**: Song has BPM, annotations, and A-B loop set  
**Steps**:
1. Set BPM to 120
2. Add several annotations at different timestamps
3. Set A-B loop markers
4. View waveform

**Expected Results**:
- Tempo markers (gray dashed) are distinguishable from annotations (colored)
- Loop markers (cyan) remain visible and distinguishable
- All markers are visible without overlapping issues
- Clicking markers works correctly

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 2.6: Tempo Markers on Very Long Songs
**Objective**: Verify performance with many tempo markers  
**Preconditions**: Have a 10+ minute audio file  
**Steps**:
1. Open a long audio file (10-15 minutes)
2. Set BPM to 120
3. View waveform
4. Scroll through waveform

**Expected Results**:
- Markers display correctly throughout entire song
- No performance degradation
- Safety limit prevents excessive markers (stops at 1000 measures)
- Smooth scrolling and playback

**Pass/Fail**: ___  
**Notes**: ___

---

## Feature 3: Tempo Data Persistence

### Test Case 3.1: Tempo Data Saved to JSON
**Objective**: Verify BPM is saved to `.tempo.json` file  
**Preconditions**: Practice folder is open  
**Steps**:
1. Set BPM = 125 for "Song A"
2. Set BPM = 140 for "Song B"
3. Navigate to practice folder in file system
4. Open `.tempo.json` in text editor

**Expected Results**:
- `.tempo.json` file exists in practice folder
- File contains JSON structure: `{"Song A.mp3": 125, "Song B.mp3": 140}`
- File is human-readable
- Proper JSON formatting

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 3.2: Tempo Data Persists Across Sessions
**Objective**: Verify BPM values persist after closing and reopening app  
**Preconditions**: Songs have BPM values set  
**Steps**:
1. Set BPM for several songs
2. Close AudioBrowser application completely
3. Reopen AudioBrowser
4. Open same practice folder
5. Check Library tab BPM column

**Expected Results**:
- All BPM values are restored correctly
- Values display in Library tab
- Tempo markers appear on waveforms

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 3.3: Tempo Data Specific to Each Folder
**Objective**: Verify tempo data is folder-specific  
**Preconditions**: Have two different practice folders  
**Steps**:
1. Open Folder A, set BPM for songs
2. Switch to Folder B, set different BPM for songs
3. Switch back to Folder A
4. Verify BPM values

**Expected Results**:
- Each folder has its own `.tempo.json` file
- BPM values are independent per folder
- Switching folders loads correct tempo data
- No mixing of data between folders

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 3.4: Handle Missing or Corrupted Tempo File
**Objective**: Verify graceful handling of tempo file issues  
**Preconditions**: Practice folder has `.tempo.json`  
**Steps**:
1. Set BPM for songs
2. Close application
3. Manually delete `.tempo.json` or corrupt it (invalid JSON)
4. Reopen application and open folder

**Expected Results**:
- Application opens without error
- BPM column is empty (default state)
- User can set new BPM values
- New `.tempo.json` is created when BPM is entered

**Pass/Fail**: ___  
**Notes**: ___

---

## Feature 4: Integration with Existing Features

### Test Case 4.1: BPM Column in Auto-Label Preview Mode
**Objective**: Verify BPM column works during auto-labeling  
**Preconditions**: Have unlabeled audio files  
**Steps**:
1. Set BPM for some songs
2. Start auto-label fingerprinting
3. Enter preview mode with suggested names
4. Verify BPM column is visible
5. Apply suggestions

**Expected Results**:
- BPM column remains visible in preview mode
- BPM values are preserved after applying suggestions
- Table layout accommodates BPM + Apply? + Confidence columns
- No layout issues

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 4.2: BPM Preservation During File Rename
**Objective**: Verify BPM is preserved when file is renamed  
**Preconditions**: Song has BPM set  
**Steps**:
1. Set BPM = 130 for "recording_001.mp3"
2. Rename file to "My Song.mp3" via provided name
3. Batch rename files
4. Check BPM value in Library tab

**Expected Results**:
- BPM value follows the renamed file
- `.tempo.json` is updated with new filename
- No data loss during rename

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 4.3: BPM and Best Take Marking
**Objective**: Verify BPM works alongside best take marking  
**Preconditions**: Practice folder is open  
**Steps**:
1. Set BPM for a song
2. Mark song as Best Take
3. Verify both features work
4. Rename file with "_best_take" suffix

**Expected Results**:
- BPM is preserved when marking as best take
- BPM is preserved when file is renamed with suffix
- Both BPM and best take status display correctly in Library tab

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 4.4: BPM in Multi-User Annotation Scenario
**Objective**: Verify tempo data works with multiple annotation sets  
**Preconditions**: Multiple annotation sets exist  
**Steps**:
1. Set BPM for songs
2. Switch between annotation sets
3. Verify tempo markers

**Expected Results**:
- Tempo data is shared across all annotation sets (folder-level)
- Tempo markers display regardless of active annotation set
- `.tempo.json` is separate from annotation files

**Pass/Fail**: ___  
**Notes**: ___

---

## Feature 5: Edge Cases and Error Handling

### Test Case 5.1: Very Fast BPM (300)
**Objective**: Test maximum supported BPM  
**Preconditions**: Practice folder is open  
**Steps**:
1. Set BPM = 300 for a song
2. Play song and view waveform

**Expected Results**:
- BPM is accepted
- Tempo markers are very close together but visible
- Performance remains acceptable
- Measure numbers may be sparse to avoid overlap

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 5.2: Very Slow BPM (40)
**Objective**: Test very low BPM values  
**Preconditions**: Practice folder is open  
**Steps**:
1. Set BPM = 40 for a song
2. Play song and view waveform

**Expected Results**:
- BPM is accepted
- Tempo markers are far apart (6 seconds per measure)
- Markers display correctly across long spans
- Measure numbers are readable

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 5.3: BPM with Very Short Song (< 1 minute)
**Objective**: Test tempo markers on short audio file  
**Preconditions**: Have a 30-second audio file  
**Steps**:
1. Set BPM = 120 for short file
2. View waveform

**Expected Results**:
- Markers display correctly for short duration
- Only a few measures appear (appropriate for length)
- No errors or visual issues

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 5.4: Decimal BPM Values
**Objective**: Test non-integer BPM input  
**Preconditions**: Practice folder is open  
**Steps**:
1. Try entering BPM = "120.5"
2. Try entering BPM = "140.75"

**Expected Results**:
- Decimal values are accepted
- Displayed as integers (rounded down: 120, 140)
- Markers position uses precise float calculation
- `.tempo.json` stores float value

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 5.5: Rapid BPM Changes
**Objective**: Test changing BPM multiple times quickly  
**Preconditions**: Song is currently playing  
**Steps**:
1. Set BPM = 100
2. Immediately change to 120
3. Immediately change to 140
4. Immediately change to 80

**Expected Results**:
- All changes are accepted
- Waveform updates each time
- No lag or performance issues
- Final value is correct (80)

**Pass/Fail**: ___  
**Notes**: ___

---

## Feature 6: User Experience

### Test Case 6.1: BPM Column Tooltip
**Objective**: Verify helpful tooltip on BPM column  
**Preconditions**: Library tab is open  
**Steps**:
1. Hover over a BPM cell
2. Read tooltip

**Expected Results**:
- Tooltip appears: "Double-click to edit BPM (Beats Per Minute)"
- Tooltip is clear and helpful
- Tooltip disappears when mouse moves away

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 6.2: Visual Clarity of Tempo Markers
**Objective**: Verify tempo markers are visually distinguishable  
**Preconditions**: Song has BPM, annotations, and loop markers  
**Steps**:
1. View waveform with all marker types
2. Assess visual clarity

**Expected Results**:
- Tempo markers (gray dashed) are subtle but visible
- Annotations (colored solid) stand out
- Loop markers (cyan) are distinct
- Playhead (dark) is most prominent
- No visual confusion between marker types

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 6.3: Measure Number Readability
**Objective**: Verify measure numbers are readable  
**Preconditions**: Song has BPM set  
**Steps**:
1. View waveform at different zoom levels
2. Check measure numbers (M4, M8, M12, etc.)

**Expected Results**:
- Numbers are readable at default zoom
- Numbers don't overlap with other text
- Font size is appropriate (8pt)
- Color is subtle but visible (#666)

**Pass/Fail**: ___  
**Notes**: ___

---

## Feature 7: Regression Tests

### Test Case 7.1: No Impact on Files Without BPM
**Objective**: Verify feature doesn't affect songs without BPM  
**Preconditions**: Practice folder with no BPM values set  
**Steps**:
1. Open folder, don't set any BPM values
2. Play songs and view waveforms
3. Use all existing features normally

**Expected Results**:
- All existing functionality works normally
- No tempo markers appear (expected)
- No performance impact
- No `.tempo.json` file created until BPM is set

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 7.2: Existing Metadata Files Unaffected
**Objective**: Verify tempo feature doesn't corrupt other metadata  
**Preconditions**: Folder has existing annotations, names, etc.  
**Steps**:
1. Set BPM for songs
2. Verify other metadata files (`.provided_names.json`, `.audio_notes_*.json`, etc.)

**Expected Results**:
- All existing metadata files remain intact
- No data corruption
- `.tempo.json` is added to RESERVED_JSON set
- Backup system includes `.tempo.json` in backups

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 7.3: Library Tab Column Layout
**Objective**: Verify adding BPM column doesn't break table layout  
**Preconditions**: Practice folder is open  
**Steps**:
1. Resize window to different sizes
2. Scroll through Library table
3. Sort by different columns

**Expected Results**:
- All columns are visible and functional
- Column widths are appropriate
- BPM column fits naturally between Partial Take and Provided Name
- Sorting works on all columns
- No horizontal scrollbar unless window is very narrow

**Pass/Fail**: ___  
**Notes**: ___

---

## Test Execution Summary

### Test Coverage

**BPM Entry**: 6 test cases  
**Visual Markers**: 6 test cases  
**Persistence**: 4 test cases  
**Integration**: 4 test cases  
**Edge Cases**: 5 test cases  
**User Experience**: 3 test cases  
**Regression**: 3 test cases  

**Total Test Cases**: 31

### Test Execution Checklist

#### Critical Tests (Must Pass)
- [ ] Test Case 1.1: Enter BPM for a Song
- [ ] Test Case 1.3: BPM Value Validation - Out of Range
- [ ] Test Case 2.1: Tempo Markers Appear with Valid BPM
- [ ] Test Case 2.2: Tempo Markers Update When BPM Changes
- [ ] Test Case 3.1: Tempo Data Saved to JSON
- [ ] Test Case 3.2: Tempo Data Persists Across Sessions
- [ ] Test Case 7.1: No Impact on Files Without BPM
- [ ] Test Case 7.2: Existing Metadata Files Unaffected

#### High Priority Tests
- [ ] Test Case 1.2: BPM Value Validation - Valid Range
- [ ] Test Case 1.5: Clear BPM Value
- [ ] Test Case 2.3: No Tempo Markers Without BPM
- [ ] Test Case 2.5: Tempo Markers Don't Interfere with Other Markers
- [ ] Test Case 3.3: Tempo Data Specific to Each Folder
- [ ] Test Case 4.2: BPM Preservation During File Rename

#### Medium Priority Tests
- [ ] Test Case 1.4: BPM Value Validation - Non-Numeric
- [ ] Test Case 2.4: Tempo Markers with Different BPM Values
- [ ] Test Case 3.4: Handle Missing or Corrupted Tempo File
- [ ] Test Case 4.1: BPM Column in Auto-Label Preview Mode
- [ ] Test Case 5.4: Decimal BPM Values

#### Low Priority Tests
- [ ] Test Case 1.6: BPM Column Resize
- [ ] Test Case 2.6: Tempo Markers on Very Long Songs
- [ ] Test Case 4.3: BPM and Best Take Marking
- [ ] Test Case 4.4: BPM in Multi-User Annotation Scenario
- [ ] Test Case 5.1: Very Fast BPM (300)
- [ ] Test Case 5.2: Very Slow BPM (40)
- [ ] Test Case 5.3: BPM with Very Short Song
- [ ] Test Case 5.5: Rapid BPM Changes
- [ ] Test Case 6.1: BPM Column Tooltip
- [ ] Test Case 6.2: Visual Clarity of Tempo Markers
- [ ] Test Case 6.3: Measure Number Readability
- [ ] Test Case 7.3: Library Tab Column Layout

---

## Known Limitations

1. **Time Signature**: Currently assumes 4/4 time signature (4 beats per measure). Other time signatures (3/4, 6/8, etc.) are not supported.
2. **Tempo Changes**: BPM is constant throughout the song. Songs with tempo changes mid-song are not supported.
3. **Metronome Playback**: Visual markers only. Audio metronome click playback is not yet implemented (future enhancement).
4. **Auto BPM Detection**: Must be entered manually. Automatic BPM detection from audio is not implemented (future enhancement).
5. **Upbeat/Pickup Measures**: Assumes song starts on measure 1, beat 1. Pickup measures are not supported.

---

## Bug Reporting Template

**Bug ID**: ___  
**Test Case**: ___  
**Severity**: [Critical / High / Medium / Low]  
**Description**: ___  
**Steps to Reproduce**:  
1. ___  
2. ___  

**Expected Result**: ___  
**Actual Result**: ___  
**Screenshots**: ___  
**Environment**: [OS, Version, Build]  
**Notes**: ___

---

## Sign-Off

### Test Execution
- **Tester Name**: _________________
- **Test Date**: _________________
- **Build Version**: _________________

### Results Summary
- **Total Tests**: 31
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
2. **Performance Benchmarks**: Measure waveform render time with/without tempo markers
3. **Cross-Platform Testing**: Dedicated test runs on Windows, macOS, and Linux
4. **Accessibility Testing**: Keyboard navigation for BPM entry, screen reader compatibility
5. **Stress Testing**: Test with 1000+ song libraries, extreme BPM values (1-500)
6. **Visual Regression Testing**: Compare waveform screenshots before/after tempo marker changes
7. **Integration Tests**: Test interaction with Practice Goals, Practice Statistics, and Setlist Builder features

---

**Document Version**: 1.0  
**Last Updated**: January 2025  
**Author**: AudioBrowser Development Team
