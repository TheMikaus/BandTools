# Test Plan: Setlist Builder

**Feature Set**: Section 3.2 (Setlist Builder)  
**Implementation Date**: January 2025  
**Test Plan Version**: 1.0

---

## Overview

This test plan covers the new Setlist Builder feature implemented in AudioBrowser. The feature allows users to create and manage performance setlists, organize songs from practice sessions, validate setlist readiness, and export setlists for performance preparation.

---

## Test Environment Requirements

### Hardware
- Windows, macOS, or Linux system
- Display resolution: 1920x1080 or higher recommended
- Mouse/trackpad for drag-and-drop operations

### Software
- Python 3.8+
- PyQt6
- AudioBrowser application (latest version)
- Sample audio files (WAV/MP3) across multiple practice folders
- Some files marked as "Best Takes"

### Test Data
- Multiple practice folders with 5-10 audio files each
- Mix of files with and without Best Take status
- Mix of files with provided names and without
- At least one folder with missing/moved files (for validation testing)

---

## Feature 1: Setlist Management

### Test Case 1.1: Create New Setlist
**Objective**: Verify that users can create a new empty setlist

**Prerequisites**:
- Application is running
- At least one practice folder is loaded

**Steps**:
1. Navigate to Tools menu → "Setlist Builder…" (or press Ctrl+Shift+T)
2. Verify the Setlist Builder dialog opens
3. Click "New Setlist" button
4. Enter a setlist name (e.g., "Summer Tour 2024")
5. Click OK

**Expected Results**:
- New setlist appears in the setlist list
- Setlist name is displayed correctly
- Song count shows "(0 songs)"
- Status bar shows confirmation message

**Pass Criteria**: ✅ Setlist created successfully and appears in list

---

### Test Case 1.2: Rename Setlist
**Objective**: Verify that users can rename an existing setlist

**Prerequisites**:
- At least one setlist exists
- Setlist Builder dialog is open

**Steps**:
1. Select a setlist from the list
2. Click "Rename" button
3. Enter a new name (e.g., "Fall Concert Series")
4. Click OK

**Expected Results**:
- Setlist name updates in all lists (Manage, Practice, Export tabs)
- Status bar shows confirmation message
- Setlist data is preserved (songs, notes)

**Pass Criteria**: ✅ Setlist renamed successfully with data preserved

---

### Test Case 1.3: Delete Setlist
**Objective**: Verify that users can delete a setlist with confirmation

**Prerequisites**:
- At least one setlist exists
- Setlist Builder dialog is open

**Steps**:
1. Select a setlist from the list
2. Click "Delete" button
3. Verify confirmation dialog appears
4. Click "Yes" to confirm

**Expected Results**:
- Confirmation dialog shows setlist name
- Setlist is removed from all lists
- Status bar shows confirmation message
- Setlist data is removed from .setlists.json file

**Pass Criteria**: ✅ Setlist deleted successfully with confirmation

---

### Test Case 1.4: Delete Setlist - Cancel
**Objective**: Verify that canceling deletion preserves the setlist

**Prerequisites**:
- At least one setlist exists
- Setlist Builder dialog is open

**Steps**:
1. Select a setlist from the list
2. Click "Delete" button
3. Click "No" in confirmation dialog

**Expected Results**:
- Setlist remains in the list
- No changes to setlist data
- No status bar message

**Pass Criteria**: ✅ Setlist preserved when deletion is cancelled

---

## Feature 2: Song Management

### Test Case 2.1: Add Song to Setlist
**Objective**: Verify that users can add the currently selected song to a setlist

**Prerequisites**:
- At least one setlist exists
- An audio file is selected in the main window
- Setlist Builder dialog is open

**Steps**:
1. Select a setlist from the list
2. In the main window, select an audio file
3. Click "Add Song from Current Folder" button

**Expected Results**:
- Song appears in the songs table
- Song shows correct provided name
- Duration is displayed (if available)
- Best Take indicator shows if applicable
- Folder name is shown
- Total duration updates
- Status bar shows confirmation message

**Pass Criteria**: ✅ Song added successfully with correct metadata

---

### Test Case 2.2: Add Song - No Selection
**Objective**: Verify error handling when no song is selected

**Prerequisites**:
- At least one setlist exists
- No audio file selected in main window
- Setlist Builder dialog is open

**Steps**:
1. Select a setlist from the list
2. Click "Add Song from Current Folder" button (without selecting a file in main window)

**Expected Results**:
- Warning dialog appears: "No File Selected"
- No song is added to the setlist
- Setlist remains unchanged

**Pass Criteria**: ✅ Appropriate error message displayed

---

### Test Case 2.3: Add Duplicate Song
**Objective**: Verify that duplicate songs cannot be added

**Prerequisites**:
- A setlist with at least one song exists
- The same song is selected in main window
- Setlist Builder dialog is open

**Steps**:
1. Select the setlist
2. Select the same song that's already in the setlist
3. Click "Add Song from Current Folder" button

**Expected Results**:
- Information dialog appears: "Already in Setlist"
- No duplicate song is added
- Setlist remains unchanged

**Pass Criteria**: ✅ Duplicate prevention works correctly

---

### Test Case 2.4: Remove Song from Setlist
**Objective**: Verify that users can remove a song from the setlist

**Prerequisites**:
- A setlist with at least one song exists
- Setlist Builder dialog is open

**Steps**:
1. Select the setlist
2. Select a song in the songs table
3. Click "Remove Song" button

**Expected Results**:
- Song is removed from the table
- Total duration updates
- Status bar shows confirmation message
- Changes persist when dialog is reopened

**Pass Criteria**: ✅ Song removed successfully

---

### Test Case 2.5: Remove Song - No Selection
**Objective**: Verify error handling when no song is selected for removal

**Prerequisites**:
- A setlist with songs exists
- Setlist Builder dialog is open

**Steps**:
1. Select the setlist
2. Without selecting a song, click "Remove Song" button

**Expected Results**:
- Warning dialog appears: "No Selection"
- No songs are removed
- Setlist remains unchanged

**Pass Criteria**: ✅ Appropriate error message displayed

---

### Test Case 2.6: Move Song Up
**Objective**: Verify that users can reorder songs by moving up

**Prerequisites**:
- A setlist with at least 2 songs exists
- Setlist Builder dialog is open

**Steps**:
1. Select the setlist
2. Select the second song in the list
3. Click "↑ Move Up" button

**Expected Results**:
- Song moves to position 1
- Former position 1 song moves to position 2
- Position numbers (1, 2, 3, ...) update accordingly
- Selection follows the moved song
- Changes persist

**Pass Criteria**: ✅ Song reordered successfully

---

### Test Case 2.7: Move Song Down
**Objective**: Verify that users can reorder songs by moving down

**Prerequisites**:
- A setlist with at least 2 songs exists
- Setlist Builder dialog is open

**Steps**:
1. Select the setlist
2. Select the first song in the list
3. Click "↓ Move Down" button

**Expected Results**:
- Song moves to position 2
- Former position 2 song moves to position 1
- Position numbers update accordingly
- Selection follows the moved song
- Changes persist

**Pass Criteria**: ✅ Song reordered successfully

---

### Test Case 2.8: Move Song Up - First Position
**Objective**: Verify that first song cannot move up

**Prerequisites**:
- A setlist with at least 2 songs exists
- Setlist Builder dialog is open

**Steps**:
1. Select the setlist
2. Select the first song in the list
3. Click "↑ Move Up" button

**Expected Results**:
- Nothing happens
- Song remains in first position
- No error message (graceful handling)

**Pass Criteria**: ✅ Boundary condition handled gracefully

---

### Test Case 2.9: Move Song Down - Last Position
**Objective**: Verify that last song cannot move down

**Prerequisites**:
- A setlist with at least 2 songs exists
- Setlist Builder dialog is open

**Steps**:
1. Select the setlist
2. Select the last song in the list
3. Click "↓ Move Down" button

**Expected Results**:
- Nothing happens
- Song remains in last position
- No error message (graceful handling)

**Pass Criteria**: ✅ Boundary condition handled gracefully

---

## Feature 3: Performance Notes

### Test Case 3.1: Add Performance Notes
**Objective**: Verify that users can add and save performance notes

**Prerequisites**:
- At least one setlist exists
- Setlist Builder dialog is open

**Steps**:
1. Select a setlist
2. Click in the "Performance Notes" text area
3. Type some notes (e.g., "Key change in Song 3 from Am to C major")
4. Wait 1 second for auto-save
5. Switch to a different setlist
6. Switch back to the original setlist

**Expected Results**:
- Notes are auto-saved as you type
- Notes persist when switching between setlists
- Notes are preserved when dialog is closed and reopened
- Notes are stored in .setlists.json file

**Pass Criteria**: ✅ Notes saved and persisted correctly

---

### Test Case 3.2: Edit Performance Notes
**Objective**: Verify that users can edit existing notes

**Prerequisites**:
- A setlist with existing notes
- Setlist Builder dialog is open

**Steps**:
1. Select the setlist
2. Verify existing notes are displayed
3. Edit the notes (add, delete, or modify text)
4. Wait 1 second for auto-save
5. Close and reopen the dialog

**Expected Results**:
- Existing notes are loaded correctly
- Edits are auto-saved
- Modified notes persist after dialog is closed and reopened

**Pass Criteria**: ✅ Notes edited and persisted correctly

---

## Feature 4: Total Duration Calculation

### Test Case 4.1: Duration Calculation - Single Song
**Objective**: Verify that total duration is calculated correctly for one song

**Prerequisites**:
- A setlist with one song (with known duration)
- Setlist Builder dialog is open

**Steps**:
1. Select the setlist
2. Note the duration of the song in the table
3. Check the "Total Duration" label

**Expected Results**:
- Total duration matches the song duration
- Format is "M:SS" (e.g., "3:45")
- Updates when song is added or removed

**Pass Criteria**: ✅ Duration calculated correctly

---

### Test Case 4.2: Duration Calculation - Multiple Songs
**Objective**: Verify that total duration sums multiple songs correctly

**Prerequisites**:
- A setlist with multiple songs (with known durations)
- Setlist Builder dialog is open

**Steps**:
1. Select the setlist
2. Manually calculate expected total (sum of all durations)
3. Check the "Total Duration" label

**Expected Results**:
- Total duration equals sum of all song durations
- Format shows minutes and seconds correctly (e.g., "15:32")
- Updates when songs are added or removed
- Handles songs over 60 minutes correctly

**Pass Criteria**: ✅ Total duration calculated correctly

---

### Test Case 4.3: Duration Calculation - Missing Duration
**Objective**: Verify handling of songs without duration metadata

**Prerequisites**:
- A setlist with a song that has no duration metadata
- Setlist Builder dialog is open

**Steps**:
1. Select the setlist
2. Check the duration column for the song
3. Check the total duration

**Expected Results**:
- Song shows "0:00" duration or blank
- Total duration calculation treats it as 0
- No errors or crashes

**Pass Criteria**: ✅ Missing duration handled gracefully

---

## Feature 5: Practice Mode

### Test Case 5.1: Start Practice Mode
**Objective**: Verify that users can start practice mode for a setlist

**Prerequisites**:
- At least one setlist with songs exists
- Setlist Builder dialog is open
- Practice Mode tab is selected

**Steps**:
1. Select a setlist from the list
2. Click "Start Practice Mode" button

**Expected Results**:
- Information dialog confirms practice mode started
- Shows setlist name
- "Start Practice Mode" button becomes disabled
- "Stop Practice Mode" button becomes enabled
- Status bar shows confirmation message
- Dialog can be closed without stopping practice mode

**Pass Criteria**: ✅ Practice mode started successfully

---

### Test Case 5.2: Start Practice Mode - No Selection
**Objective**: Verify error handling when no setlist is selected

**Prerequisites**:
- Setlist Builder dialog is open
- Practice Mode tab is selected

**Steps**:
1. Without selecting a setlist, click "Start Practice Mode" button

**Expected Results**:
- Warning dialog appears: "No Selection"
- Practice mode is not started
- Both buttons remain in default state

**Pass Criteria**: ✅ Appropriate error message displayed

---

### Test Case 5.3: Stop Practice Mode
**Objective**: Verify that users can stop practice mode

**Prerequisites**:
- Practice mode is active
- Setlist Builder dialog is open
- Practice Mode tab is selected

**Steps**:
1. Click "Stop Practice Mode" button

**Expected Results**:
- "Stop Practice Mode" button becomes disabled
- "Start Practice Mode" button becomes enabled
- Status bar shows confirmation message
- Active setlist highlighting (if implemented) is removed

**Pass Criteria**: ✅ Practice mode stopped successfully

---

## Feature 6: Validation

### Test Case 6.1: Validate Complete Setlist
**Objective**: Verify validation of a complete, ready setlist

**Prerequisites**:
- A setlist where all songs exist and have Best Takes
- Setlist Builder dialog is open
- Export & Validation tab is selected

**Steps**:
1. Select the setlist
2. Click "Validate Setlist" button

**Expected Results**:
- Validation results show:
  - Total song count
  - "All files exist" (✓)
  - "All songs have Best Takes" (✓)
  - "Setlist is ready for performance!" (✅)
- No warnings or errors

**Pass Criteria**: ✅ Validation passes for complete setlist

---

### Test Case 6.2: Validate Setlist with Missing Files
**Objective**: Verify validation detects missing files

**Prerequisites**:
- A setlist with at least one song whose file has been moved/deleted
- Setlist Builder dialog is open
- Export & Validation tab is selected

**Steps**:
1. Select the setlist
2. Click "Validate Setlist" button

**Expected Results**:
- Validation results show:
  - Count of missing files
  - "❌ Missing Files:" section listing each missing file
  - Full path (folder/filename) for each missing file
  - Red text in songs table for missing files

**Pass Criteria**: ✅ Missing files detected and reported

---

### Test Case 6.3: Validate Setlist without Best Takes
**Objective**: Verify validation detects songs without Best Takes

**Prerequisites**:
- A setlist with songs where some don't have Best Take status
- Setlist Builder dialog is open
- Export & Validation tab is selected

**Steps**:
1. Select the setlist
2. Click "Validate Setlist" button

**Expected Results**:
- Validation results show:
  - Count of songs without Best Takes
  - "⚠️  Songs without Best Take:" section listing each song
  - Song names listed clearly

**Pass Criteria**: ✅ Missing Best Takes detected and reported

---

### Test Case 6.4: Validate Empty Setlist
**Objective**: Verify validation of empty setlist

**Prerequisites**:
- An empty setlist (no songs)
- Setlist Builder dialog is open
- Export & Validation tab is selected

**Steps**:
1. Select the empty setlist
2. Click "Validate Setlist" button

**Expected Results**:
- Validation results show:
  - Total songs: 0
  - "All files exist" (✓)
  - "All songs have Best Takes" (✓)
  - May show "Setlist is ready" (technically correct for empty list)

**Pass Criteria**: ✅ Empty setlist validated without errors

---

## Feature 7: Export

### Test Case 7.1: Export Setlist as Text
**Objective**: Verify that users can export a setlist to a text file

**Prerequisites**:
- A setlist with multiple songs and notes
- Setlist Builder dialog is open
- Export & Validation tab is selected

**Steps**:
1. Select the setlist
2. Click "Export as Text" button
3. Choose a save location and filename
4. Click Save
5. Open the exported file in a text editor

**Expected Results**:
- Save file dialog appears
- Default filename is setlist name with .txt extension
- File is created successfully
- File contains:
  - Setlist name
  - Creation and export dates
  - Numbered list of songs with durations
  - Source folder/filename for each song
  - Best Take markers
  - Total song count and duration
  - Performance notes (if any)
- Success message appears
- Status bar shows confirmation

**Pass Criteria**: ✅ Setlist exported correctly as text file

---

### Test Case 7.2: Export - No Selection
**Objective**: Verify error handling when no setlist is selected for export

**Prerequisites**:
- Setlist Builder dialog is open
- Export & Validation tab is selected

**Steps**:
1. Without selecting a setlist, click "Export as Text" button

**Expected Results**:
- Warning dialog appears: "No Selection"
- No file dialog appears
- No file is created

**Pass Criteria**: ✅ Appropriate error message displayed

---

### Test Case 7.3: Export - Cancel Save Dialog
**Objective**: Verify that canceling the save dialog doesn't create a file

**Prerequisites**:
- A setlist exists
- Setlist Builder dialog is open
- Export & Validation tab is selected

**Steps**:
1. Select the setlist
2. Click "Export as Text" button
3. Click "Cancel" in the save file dialog

**Expected Results**:
- No file is created
- No success message appears
- Dialog remains open and functional

**Pass Criteria**: ✅ Cancel handled gracefully

---

### Test Case 7.4: Export - Missing Files
**Objective**: Verify export includes missing file markers

**Prerequisites**:
- A setlist with at least one missing file
- Setlist Builder dialog is open
- Export & Validation tab is selected

**Steps**:
1. Select the setlist
2. Click "Export as Text" button
3. Save the file
4. Open the exported file

**Expected Results**:
- Missing files have "[MISSING]" marker in the text file
- File still exports successfully
- All other data is correct

**Pass Criteria**: ✅ Missing files marked appropriately in export

---

## Feature 8: Data Persistence

### Test Case 8.1: Persistence Across Application Restart
**Objective**: Verify that setlists persist when application is closed and reopened

**Prerequisites**:
- At least one setlist with songs and notes

**Steps**:
1. Create a setlist with songs and notes
2. Close the Setlist Builder dialog
3. Close the AudioBrowser application
4. Restart the application
5. Open the Setlist Builder dialog

**Expected Results**:
- All setlists are loaded
- All songs are preserved in correct order
- Performance notes are preserved
- Setlist metadata (name, dates) is correct

**Pass Criteria**: ✅ All data persisted correctly

---

### Test Case 8.2: Persistence - JSON File Structure
**Objective**: Verify that setlist data is stored correctly in JSON

**Prerequisites**:
- At least one setlist exists

**Steps**:
1. Create or modify a setlist
2. Navigate to the root practice folder
3. Open `.setlists.json` file in a text editor

**Expected Results**:
- File exists and is valid JSON
- Contains setlist ID keys (UUIDs)
- Each setlist has required fields: name, songs, notes, created_date, last_modified
- Songs array contains folder and filename for each song
- Data structure matches expected format

**Pass Criteria**: ✅ JSON file structure is correct

---

### Test Case 8.3: Persistence - Multiple Setlists
**Objective**: Verify that multiple setlists can coexist in the JSON file

**Prerequisites**:
- None

**Steps**:
1. Create 3 different setlists
2. Add different songs to each
3. Add notes to at least one
4. Close and reopen dialog
5. Verify all setlists

**Expected Results**:
- All 3 setlists appear in the list
- Each setlist has correct songs and notes
- No data overlap or corruption
- Each setlist has unique ID

**Pass Criteria**: ✅ Multiple setlists stored independently

---

## Feature 9: Integration with Main Application

### Test Case 9.1: Add Songs from Different Folders
**Objective**: Verify that songs from different practice folders can be added to one setlist

**Prerequisites**:
- Multiple practice folders with audio files
- A setlist exists

**Steps**:
1. Open the Setlist Builder dialog
2. Select the setlist
3. In main window, navigate to folder 1 and select a song
4. Click "Add Song from Current Folder"
5. In main window, navigate to folder 2 and select a different song
6. Click "Add Song from Current Folder" again
7. Verify the songs table

**Expected Results**:
- Both songs appear in the setlist
- Each song shows its respective source folder
- Order is preserved
- Both songs are accessible

**Pass Criteria**: ✅ Songs from multiple folders can be added

---

### Test Case 9.2: Best Take Status Detection
**Objective**: Verify that Best Take status is correctly detected from annotation files

**Prerequisites**:
- Songs with varying Best Take status (some marked, some not)
- A setlist exists

**Steps**:
1. Mark a song as Best Take in the Annotations tab
2. Add that song to a setlist
3. Open Setlist Builder
4. Verify the Best Take column

**Expected Results**:
- Song marked as Best Take shows "✓" in Best Take column
- Song not marked shows empty cell
- Best Take status updates if changed in main window

**Pass Criteria**: ✅ Best Take status detected correctly

---

### Test Case 9.3: Provided Name Display
**Objective**: Verify that songs display their provided names (not filenames)

**Prerequisites**:
- Songs with provided names set
- A setlist exists

**Steps**:
1. Ensure a song has a provided name (not just filename)
2. Add that song to a setlist
3. Verify display in songs table

**Expected Results**:
- Song name column shows provided name
- Filename is shown in Folder column with folder name
- Provided names are loaded from correct practice folder

**Pass Criteria**: ✅ Provided names displayed correctly

---

## Feature 10: Edge Cases and Error Handling

### Test Case 10.1: Empty Setlist Display
**Objective**: Verify UI behaves correctly with empty setlist

**Prerequisites**:
- An empty setlist exists

**Steps**:
1. Select the empty setlist
2. Observe the songs table and controls

**Expected Results**:
- Songs table is empty (no rows)
- Total Duration shows "0:00"
- All buttons remain functional
- No errors or crashes

**Pass Criteria**: ✅ Empty setlist handled gracefully

---

### Test Case 10.2: Long Setlist (50+ Songs)
**Objective**: Verify performance with large setlists

**Prerequisites**:
- Ability to create a setlist with many songs

**Steps**:
1. Create a setlist
2. Add 50+ songs to it
3. Test scrolling, reordering, validation, and export

**Expected Results**:
- UI remains responsive
- All operations work correctly
- No performance degradation
- Export includes all songs

**Pass Criteria**: ✅ Large setlists handled efficiently

---

### Test Case 10.3: Special Characters in Names
**Objective**: Verify handling of special characters in setlist and song names

**Prerequisites**:
- None

**Steps**:
1. Create a setlist with name containing special characters: "Summer & Fall 2024 (Main)"
2. Add songs with special characters in provided names
3. Add notes with special characters
4. Export the setlist

**Expected Results**:
- Special characters display correctly in UI
- JSON file stores characters correctly (UTF-8)
- Export file contains correct characters
- No crashes or encoding errors

**Pass Criteria**: ✅ Special characters handled correctly

---

### Test Case 10.4: Concurrent Editing Prevention
**Objective**: Verify behavior when setlist is edited while dialog is open

**Prerequisites**:
- A setlist exists
- Setlist Builder dialog is open

**Steps**:
1. Open the dialog
2. Manually edit the `.setlists.json` file (add/remove a song)
3. Try to perform operations in the dialog

**Expected Results**:
- Operations work with current in-memory state
- Next dialog open loads updated data from disk
- No data corruption
- (Future enhancement: file watching for external changes)

**Pass Criteria**: ✅ No data corruption occurs

---

### Test Case 10.5: Missing Reference Folder
**Objective**: Verify handling when a song's folder no longer exists

**Prerequisites**:
- A setlist with songs
- One song's practice folder has been deleted/moved

**Steps**:
1. Delete or rename a practice folder containing setlist songs
2. Open Setlist Builder
3. Select the setlist
4. View validation results

**Expected Results**:
- Songs from missing folder show as not existing
- Red text in songs table
- Validation reports missing files
- No crashes
- Can still remove songs or export setlist

**Pass Criteria**: ✅ Missing folders handled gracefully

---

## Feature 11: Keyboard Shortcuts

### Test Case 11.1: Open Dialog with Shortcut
**Objective**: Verify Ctrl+Shift+T opens the Setlist Builder

**Prerequisites**:
- Application is running
- Main window has focus

**Steps**:
1. Press Ctrl+Shift+T

**Expected Results**:
- Setlist Builder dialog opens
- Dialog has focus
- All UI elements are functional

**Pass Criteria**: ✅ Keyboard shortcut works correctly

---

## Feature 12: Regression Tests

### Test Case 12.1: No Impact on Existing Features
**Objective**: Verify that Setlist Builder doesn't break existing functionality

**Prerequisites**:
- Application is running

**Steps**:
1. Test basic playback
2. Test annotation creation
3. Test Best Take marking
4. Test batch rename
5. Test other existing features

**Expected Results**:
- All existing features work as before
- No new crashes or errors
- No performance degradation

**Pass Criteria**: ✅ No regressions detected

---

### Test Case 12.2: JSON File Compatibility
**Objective**: Verify that .setlists.json doesn't interfere with other JSON files

**Prerequisites**:
- Multiple JSON metadata files exist

**Steps**:
1. Create and use setlists
2. Verify other JSON files (.audio_notes.json, .provided_names.json, etc.)
3. Check that other features still work

**Expected Results**:
- .setlists.json is correctly excluded from reserved files
- Other JSON files are not affected
- No file conflicts or errors

**Pass Criteria**: ✅ No interference with other files

---

## Test Execution Summary

### Test Coverage
- **Setlist Management**: 4 test cases
- **Song Management**: 9 test cases
- **Performance Notes**: 2 test cases
- **Duration Calculation**: 3 test cases
- **Practice Mode**: 3 test cases
- **Validation**: 4 test cases
- **Export**: 4 test cases
- **Data Persistence**: 3 test cases
- **Integration**: 3 test cases
- **Edge Cases**: 5 test cases
- **Keyboard Shortcuts**: 1 test case
- **Regression**: 2 test cases

**Total Test Cases**: 43

### Test Execution Checklist

#### Critical Tests (Must Pass)
- [ ] Test Case 1.1: Create New Setlist
- [ ] Test Case 2.1: Add Song to Setlist
- [ ] Test Case 2.4: Remove Song from Setlist
- [ ] Test Case 2.6: Move Song Up
- [ ] Test Case 2.7: Move Song Down
- [ ] Test Case 3.1: Add Performance Notes
- [ ] Test Case 4.2: Duration Calculation - Multiple Songs
- [ ] Test Case 5.1: Start Practice Mode
- [ ] Test Case 6.1: Validate Complete Setlist
- [ ] Test Case 7.1: Export Setlist as Text
- [ ] Test Case 8.1: Persistence Across Application Restart
- [ ] Test Case 9.1: Add Songs from Different Folders
- [ ] Test Case 11.1: Open Dialog with Shortcut
- [ ] Test Case 12.1: No Impact on Existing Features

#### High Priority Tests
- [ ] Test Case 1.2: Rename Setlist
- [ ] Test Case 1.3: Delete Setlist
- [ ] Test Case 2.3: Add Duplicate Song
- [ ] Test Case 2.5: Remove Song - No Selection
- [ ] Test Case 6.2: Validate Setlist with Missing Files
- [ ] Test Case 6.3: Validate Setlist without Best Takes
- [ ] Test Case 8.2: Persistence - JSON File Structure
- [ ] Test Case 9.2: Best Take Status Detection
- [ ] Test Case 10.1: Empty Setlist Display
- [ ] Test Case 10.5: Missing Reference Folder

#### Medium Priority Tests
- [ ] Test Case 1.4: Delete Setlist - Cancel
- [ ] Test Case 2.2: Add Song - No Selection
- [ ] Test Case 2.8: Move Song Up - First Position
- [ ] Test Case 2.9: Move Song Down - Last Position
- [ ] Test Case 3.2: Edit Performance Notes
- [ ] Test Case 4.1: Duration Calculation - Single Song
- [ ] Test Case 4.3: Duration Calculation - Missing Duration
- [ ] Test Case 5.2: Start Practice Mode - No Selection
- [ ] Test Case 5.3: Stop Practice Mode
- [ ] Test Case 6.4: Validate Empty Setlist
- [ ] Test Case 7.2: Export - No Selection
- [ ] Test Case 7.3: Export - Cancel Save Dialog
- [ ] Test Case 7.4: Export - Missing Files
- [ ] Test Case 8.3: Persistence - Multiple Setlists
- [ ] Test Case 9.3: Provided Name Display
- [ ] Test Case 10.2: Long Setlist (50+ Songs)
- [ ] Test Case 10.3: Special Characters in Names
- [ ] Test Case 10.4: Concurrent Editing Prevention
- [ ] Test Case 12.2: JSON File Compatibility

---

## Known Limitations

1. **PDF Export**: Not yet implemented (button disabled with "Coming Soon" label)
2. **Drag-and-Drop Reordering**: Currently uses Move Up/Down buttons instead of drag-and-drop
3. **Practice Mode Visual Highlighting**: Setlist songs not yet highlighted in file tree during practice mode
4. **Auto-Play in Practice Mode**: No automatic sequential playback of setlist songs
5. **Setlist Templates**: No predefined setlist templates
6. **Collaborative Editing**: No real-time sync when multiple users edit same setlist

---

## Bug Reporting Template

When reporting bugs, please include:

**Bug Title**: [Short description]

**Test Case**: [Test case number and name]

**Environment**:
- OS: [Windows/macOS/Linux]
- Python Version: [e.g., 3.10.5]
- PyQt6 Version: [e.g., 6.4.0]

**Steps to Reproduce**:
1. [First step]
2. [Second step]
3. [etc.]

**Expected Result**: [What should happen]

**Actual Result**: [What actually happened]

**Screenshots/Logs**: [If applicable]

**Severity**: [Critical/High/Medium/Low]

---

## Sign-Off

### Test Execution
- **Tester Name**: _________________
- **Test Date**: _________________
- **Build Version**: _________________

### Results Summary
- **Total Tests**: 43
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
2. **Performance Benchmarks**: Measure load time for large setlists (100+ songs)
3. **Cross-Platform Testing**: Dedicated test runs on Windows, macOS, and Linux
4. **Accessibility Testing**: Screen reader compatibility, keyboard navigation completeness
5. **Localization Testing**: If multi-language support is added
6. **Integration Tests**: Test interaction with Practice Goals and Practice Statistics features
