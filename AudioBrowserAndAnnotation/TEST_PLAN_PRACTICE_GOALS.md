# Test Plan: Practice Goals Feature

**Feature**: Section 3.1.2 (Practice Goals & Tracking)  
**Implementation Date**: January 2025  
**Test Plan Version**: 1.0

---

## Overview

This test plan covers the newly implemented Practice Goals feature in AudioBrowser. The feature allows users to set and track practice goals including:
1. **Time-based Goals** - Weekly/monthly practice time targets
2. **Session Count Goals** - Weekly/monthly practice session targets
3. **Song-specific Goals** - Per-song practice count and best take goals

---

## Test Environment Requirements

### Hardware
- Windows, macOS, or Linux system
- Display resolution: 1920x1080 or higher recommended
- Mouse/keyboard for form input and navigation

### Software
- Python 3.8+
- PyQt6
- AudioBrowser application (latest version with Practice Goals feature)
- Sample practice folders with audio files for testing

### Test Data
- Multiple practice folders with different dates (e.g., dated folders like "2025-01-01-Practice")
- Audio files with provided names assigned
- Mix of files marked as "Best Take" and regular recordings
- At least 5-10 practice folders spanning different dates for realistic testing

---

## Feature 1: Goal Creation and Management

### Test Case 1.1: Access Practice Goals Dialog
**Objective**: Verify the Practice Goals dialog can be accessed

**Prerequisites**:
- Application is running
- At least one practice folder is loaded

**Steps**:
1. Open Help menu
2. Click "Practice Goals" menu item

**Expected Results**:
- Dialog opens successfully
- Dialog title shows "AudioBrowser - Practice Goals"
- Two tabs visible: "Active Goals" and "Manage Goals"
- Dialog is resizable and properly formatted

**Pass Criteria**: ✅ Dialog opens correctly with proper layout

**Alternative Access**:
1. Press `Ctrl+Shift+G` keyboard shortcut

**Expected Results**:
- Same dialog opens using keyboard shortcut

---

### Test Case 1.2: Create Weekly Time Goal
**Objective**: Verify creation of weekly practice time goal

**Prerequisites**:
- Practice Goals dialog is open
- On "Manage Goals" tab

**Steps**:
1. In goal creation form, select "Weekly Time Goal" from Goal Type dropdown
2. Set Target to 300 minutes (5 hours)
3. Set Start Date to current date
4. Set End Date to 7 days from current date
5. Click "Create Goal" button

**Expected Results**:
- Form updates to show " minutes" suffix on target field
- End date automatically suggests 7 days ahead (can be overridden)
- Goal is created successfully
- Confirmation dialog appears: "Your practice goal has been created successfully!"
- Dialog automatically switches to "Active Goals" tab
- New goal appears in Active Goals list with progress bar
- Goal appears in Existing Goals table on Manage Goals tab

**Pass Criteria**: ✅ Weekly time goal created and displayed correctly

---

### Test Case 1.3: Create Monthly Session Count Goal
**Objective**: Verify creation of monthly session count goal

**Prerequisites**:
- Practice Goals dialog is open
- On "Manage Goals" tab

**Steps**:
1. Select "Monthly Session Count" from Goal Type dropdown
2. Set Target to 8 sessions
3. Set Start Date to first day of current month
4. Set End Date to last day of current month
5. Click "Create Goal" button

**Expected Results**:
- Form updates to show " sessions" suffix on target field
- Default target changes to 3 sessions
- End date automatically suggests 30 days ahead
- Goal created successfully with confirmation message
- Goal appears in both Active Goals and Existing Goals

**Pass Criteria**: ✅ Monthly session count goal created correctly

---

### Test Case 1.4: Create Song Practice Count Goal
**Objective**: Verify creation of per-song practice goal

**Prerequisites**:
- Practice Goals dialog is open
- Know the name of at least one song in practice folders

**Steps**:
1. Select "Song Practice Count" from Goal Type dropdown
2. Notice Song Name field becomes enabled
3. Enter song name (e.g., "Test Song")
4. Set Target to 5 practices
5. Set date range (7-30 days)
6. Click "Create Goal" button

**Expected Results**:
- Song Name input field is enabled for song goals
- Target field shows " practices" suffix
- Goal created successfully
- Goal card shows "Song: Test Song - Practice Count" as title
- Progress calculation reflects actual practices of that song

**Pass Criteria**: ✅ Song-specific practice goal created with song name

---

### Test Case 1.5: Create Song Best Take Goal
**Objective**: Verify creation of song best take goal

**Prerequisites**:
- Practice Goals dialog is open

**Steps**:
1. Select "Song Best Take" from Goal Type dropdown
2. Enter song name in Song Name field
3. Notice Target field is automatically set to 1 and disabled
4. Set date range
5. Click "Create Goal" button

**Expected Results**:
- Song Name field is enabled
- Target field shows 1 and is disabled (can't be changed)
- Goal created successfully
- Goal progress shows either "Best take recorded!" or "No best take yet"

**Pass Criteria**: ✅ Song best take goal created with correct constraints

---

### Test Case 1.6: Invalid Goal Creation - Missing Song Name
**Objective**: Verify validation when song name is missing for song goals

**Prerequisites**:
- Practice Goals dialog is open on Manage Goals tab

**Steps**:
1. Select "Song Practice Count" from Goal Type dropdown
2. Leave Song Name field empty
3. Set target and dates
4. Click "Create Goal" button

**Expected Results**:
- Warning dialog appears: "Please enter a song name for song-specific goals."
- Goal is not created
- User remains on Manage Goals tab

**Pass Criteria**: ✅ Validation prevents creation of song goal without song name

---

### Test Case 1.7: Invalid Goal Creation - Invalid Date Range
**Objective**: Verify validation of date range

**Prerequisites**:
- Practice Goals dialog is open

**Steps**:
1. Select any goal type
2. Set Start Date to current date
3. Set End Date to a date before Start Date (or same as Start Date)
4. Click "Create Goal" button

**Expected Results**:
- Warning dialog appears: "End date must be after start date."
- Goal is not created
- User can correct the dates

**Pass Criteria**: ✅ Validation prevents invalid date ranges

---

### Test Case 1.8: Delete Goal
**Objective**: Verify goal deletion functionality

**Prerequisites**:
- At least one goal exists
- Practice Goals dialog is open on Manage Goals tab

**Steps**:
1. Locate a goal in the Existing Goals table
2. Click "Delete" button in the Actions column
3. Confirm deletion in confirmation dialog

**Expected Results**:
- Confirmation dialog appears: "Are you sure you want to delete this goal?"
- After confirming, goal is removed from table
- Goal also removed from Active Goals tab
- Goals data is persisted (`.practice_goals.json` updated)

**Pass Criteria**: ✅ Goal deletion works with confirmation

---

### Test Case 1.9: Cancel Goal Deletion
**Objective**: Verify deletion can be canceled

**Prerequisites**:
- At least one goal exists

**Steps**:
1. Click "Delete" button for a goal
2. Click "No" in confirmation dialog

**Expected Results**:
- Goal is NOT deleted
- Goal remains in both tables
- No changes to persisted data

**Pass Criteria**: ✅ Deletion can be canceled safely

---

## Feature 2: Goal Progress Tracking

### Test Case 2.1: Weekly Time Goal Progress Calculation
**Objective**: Verify progress calculation for time-based goals

**Prerequisites**:
- Have practice folders with known file counts
- Create weekly time goal with date range covering existing practice folders

**Steps**:
1. Create weekly time goal for 300 minutes
2. Set date range to cover existing practice folders
3. View goal in Active Goals tab

**Expected Results**:
- Progress bar shows estimated progress (files × 3 minutes rough estimate)
- Progress message shows "X of 300 minutes"
- Percentage calculated correctly
- Progress bar color reflects status:
  - Blue/Orange for in-progress (< 75%)
  - Green for near-completion or complete (≥ 75% or 100%)

**Pass Criteria**: ✅ Time goal progress calculated and displayed correctly

**Note**: Time calculation is an estimate (3 min per file). Actual playback time tracking is not yet implemented.

---

### Test Case 2.2: Session Count Goal Progress
**Objective**: Verify session count progress calculation

**Prerequisites**:
- Have multiple practice folders with different dates

**Steps**:
1. Create weekly/monthly session count goal
2. Set date range covering multiple practice folders
3. View progress in Active Goals

**Expected Results**:
- Progress shows actual count of practice sessions (folders) in date range
- Progress message shows "X of Y sessions"
- Percentage calculated correctly (sessions / target × 100)

**Pass Criteria**: ✅ Session count accurately reflects practice folder count in range

---

### Test Case 2.3: Song Practice Count Progress
**Objective**: Verify song-specific practice count tracking

**Prerequisites**:
- Have a song that appears in multiple practice folders
- Know which folders contain that song

**Steps**:
1. Create song practice count goal for a specific song
2. Set target and date range covering folders with that song
3. View progress

**Expected Results**:
- Progress counts how many practice sessions included that song
- Progress message shows "X of Y practices"
- Only practices within date range are counted

**Pass Criteria**: ✅ Song practice count accurately reflects session count containing song

---

### Test Case 2.4: Song Best Take Goal Progress
**Objective**: Verify best take goal completion detection

**Prerequisites**:
- Have a song marked as "Best Take"

**Steps**:
1. Create song best take goal for a song with a best take
2. View progress

**Expected Results**:
- Progress shows 100% complete
- Status message: "Best take recorded!"
- Status indicator is green

**Alternative Steps**:
1. Create song best take goal for a song WITHOUT a best take
2. View progress

**Expected Results**:
- Progress shows 0%
- Status message: "No best take yet"

**Pass Criteria**: ✅ Best take detection works correctly

---

### Test Case 2.5: Goal Status - In Progress
**Objective**: Verify goal status for active goals

**Prerequisites**:
- Create a goal with current date in range
- Goal is not yet complete

**Steps**:
1. Create goal with partial progress
2. View in Active Goals tab

**Expected Results**:
- Status shows "⏰ X days remaining"
- Progress bar is blue or orange depending on progress
- Status field shows "X% (in_progress)"

**Pass Criteria**: ✅ In-progress goals show correct status

---

### Test Case 2.6: Goal Status - Complete
**Objective**: Verify goal status when target is met

**Prerequisites**:
- Create a goal that can be completed (e.g., low target)

**Steps**:
1. Create goal with target equal to or less than current progress
2. View in Active Goals

**Expected Results**:
- Status shows "✅ Goal completed! Great work!"
- Progress bar is green
- Progress shows 100%
- Status field shows "100% (complete)"

**Pass Criteria**: ✅ Completed goals show celebration message and green indicator

---

### Test Case 2.7: Goal Status - Expired
**Objective**: Verify goal status for expired goals

**Prerequisites**:
- Create a goal with end date in the past (or modify JSON manually)

**Steps**:
1. Create/modify goal with end date before today
2. Goal should not be complete
3. View in Active Goals

**Expected Results**:
- Status shows "⚠️ Goal expired (X days ago)"
- Progress bar is red
- Status field shows "X% (expired)"
- Goal still visible if expired within last 7 days
- Goal hidden if expired more than 7 days ago

**Pass Criteria**: ✅ Expired goals show warning status with red indicator

---

### Test Case 2.8: Days Remaining Calculation
**Objective**: Verify accurate countdown of days remaining

**Prerequisites**:
- Create goal with known end date

**Steps**:
1. Create goal ending in 5 days
2. Check days remaining in Active Goals

**Expected Results**:
- Status shows "⏰ 5 days remaining"
- Days remaining updates as dates change

**Pass Criteria**: ✅ Days remaining calculated correctly

---

## Feature 3: Goal Persistence

### Test Case 3.1: Goals Saved Across Sessions
**Objective**: Verify goals persist after closing and reopening application

**Prerequisites**:
- Create several goals of different types

**Steps**:
1. Create 2-3 different goals
2. Close Practice Goals dialog
3. Close AudioBrowser application completely
4. Reopen AudioBrowser
5. Open Practice Goals dialog

**Expected Results**:
- All previously created goals still exist
- Progress information is recalculated on load
- Goals data loaded from `.practice_goals.json` in root folder

**Pass Criteria**: ✅ Goals persist correctly across application restarts

---

### Test Case 3.2: Goals File Location
**Objective**: Verify goals are stored in correct location

**Prerequisites**:
- At least one goal created

**Steps**:
1. Create a goal
2. Navigate to root practice folder in file system
3. Look for `.practice_goals.json` file

**Expected Results**:
- File exists in root practice folder (not in individual session folders)
- File is valid JSON
- File contains all created goals with correct structure

**Pass Criteria**: ✅ Goals file created in correct location with valid structure

---

### Test Case 3.3: Goals Survive Folder Changes
**Objective**: Verify goals persist when changing practice folders

**Prerequisites**:
- Multiple root practice folders available
- Goals created in one folder

**Steps**:
1. Create goals in Folder A
2. Close Practice Goals dialog
3. Change to Folder B (different root folder)
4. Open Practice Goals dialog

**Expected Results**:
- Folder B has its own goals (or no goals if new)
- Goals from Folder A are not shown
- Each root folder maintains separate goals

**Pass Criteria**: ✅ Goals are folder-specific and don't interfere

---

## Feature 4: UI/UX Tests

### Test Case 4.1: Form Field Updates
**Objective**: Verify form fields update correctly when goal type changes

**Prerequisites**:
- Practice Goals dialog open on Manage Goals tab

**Steps**:
1. Select "Weekly Time Goal"
   - Check target suffix is " minutes"
   - Check default value is 300
   - Check song name is disabled
2. Select "Monthly Session Count"
   - Check target suffix is " sessions"
   - Check default value changes to 3
   - Check song name is disabled
3. Select "Song Practice Count"
   - Check target suffix is " practices"
   - Check default value is 5
   - Check song name is enabled
4. Select "Song Best Take"
   - Check target is 1 and disabled
   - Check song name is enabled

**Expected Results**:
- All field updates happen correctly
- Appropriate fields enabled/disabled based on goal type
- Defaults are sensible for each goal type

**Pass Criteria**: ✅ Form adapts correctly to goal type selection

---

### Test Case 4.2: Date Picker Functionality
**Objective**: Verify date pickers work correctly

**Prerequisites**:
- Practice Goals dialog open

**Steps**:
1. Click Start Date calendar icon
2. Select a date from calendar popup
3. Click End Date calendar icon
4. Select a later date

**Expected Results**:
- Calendar popup appears
- Date selection works
- Selected dates display in format YYYY-MM-DD
- Can type dates manually as well

**Pass Criteria**: ✅ Date pickers functional and user-friendly

---

### Test Case 4.3: Goal Card Visual Design
**Objective**: Verify goal cards are visually appealing and informative

**Prerequisites**:
- Multiple goals with different statuses

**Steps**:
1. Create goals with different progress levels
2. Create an expired goal
3. Create a completed goal
4. View Active Goals tab

**Expected Results**:
- Each goal has its own card with gray background
- Progress bars are clearly visible
- Color coding is appropriate:
  - Green for complete
  - Red for expired
  - Blue/Orange for in-progress
- Status icons (✅, ⚠️, ⏰) are visible
- Text is readable and well-formatted

**Pass Criteria**: ✅ Goal cards are visually clear and informative

---

### Test Case 4.4: Tab Navigation
**Objective**: Verify tab switching works correctly

**Prerequisites**:
- Practice Goals dialog open

**Steps**:
1. Click "Active Goals" tab
2. Verify content displays
3. Click "Manage Goals" tab
4. Verify content displays
5. Create a new goal (should auto-switch to Active Goals)

**Expected Results**:
- Tabs switch smoothly
- Content updates correctly
- Creating goal auto-switches to Active Goals to show new goal

**Pass Criteria**: ✅ Tab navigation is intuitive

---

### Test Case 4.5: Dialog Resizing
**Objective**: Verify dialog can be resized

**Steps**:
1. Open Practice Goals dialog
2. Resize dialog window smaller
3. Resize dialog window larger

**Expected Results**:
- Dialog is resizable
- Content adapts to new size
- No clipping or overlap issues
- Scroll areas work when content exceeds visible area

**Pass Criteria**: ✅ Dialog resizes properly

---

### Test Case 4.6: Empty State Display
**Objective**: Verify appropriate message when no goals exist

**Prerequisites**:
- No goals created yet

**Steps**:
1. Open Practice Goals dialog with no existing goals
2. View Active Goals tab

**Expected Results**:
- Friendly message displayed: "No practice goals set. Use the 'Manage Goals' tab to create your first goal!"
- No error or blank screen

**Pass Criteria**: ✅ Empty state handled gracefully

---

### Test Case 4.7: Many Goals Display
**Objective**: Verify UI handles many goals correctly

**Prerequisites**:
- Ability to create 10+ goals

**Steps**:
1. Create 10+ goals of various types
2. View Active Goals tab

**Expected Results**:
- All goals displayed
- Scroll area allows viewing all goals
- No performance issues
- Layout remains clean

**Pass Criteria**: ✅ Multiple goals displayed without issues

---

## Feature 5: Integration Tests

### Test Case 5.1: Integration with Practice Statistics
**Objective**: Verify goals use same data source as Practice Statistics

**Prerequisites**:
- Have practice folders with known data
- Both Practice Statistics and Practice Goals features

**Steps**:
1. Open Practice Statistics (Ctrl+Shift+S)
2. Note session count, song practices, etc.
3. Close Practice Statistics
4. Open Practice Goals (Ctrl+Shift+G)
5. Create goals matching observed statistics
6. Check goal progress

**Expected Results**:
- Goal progress matches what's shown in Practice Statistics
- Both features analyze same practice folders
- Data is consistent between features

**Pass Criteria**: ✅ Goals and statistics show consistent data

---

### Test Case 5.2: Goal Progress Updates After New Practice
**Objective**: Verify goals update when new practices are added

**Prerequisites**:
- Active goal with partial progress

**Steps**:
1. Note current goal progress
2. Close Practice Goals dialog
3. Add new practice folder with audio files
4. Mark files with provided names
5. Reopen Practice Goals dialog
6. Check goal progress

**Expected Results**:
- Progress is recalculated including new practice session
- New practice session counted in applicable goals
- Progress bars and percentages update correctly

**Pass Criteria**: ✅ Goals reflect new practice data

---

### Test Case 5.3: Best Take Goal Updates After Marking
**Objective**: Verify song best take goals update when best takes are marked

**Prerequisites**:
- Song best take goal for a song without a best take

**Steps**:
1. Create best take goal for a song
2. Note goal shows "No best take yet"
3. Close Practice Goals dialog
4. Mark one recording of that song as "Best Take"
5. Reopen Practice Goals dialog

**Expected Results**:
- Goal now shows "Best take recorded!"
- Progress is 100%
- Status is "complete"
- Progress bar is green

**Pass Criteria**: ✅ Best take goals update when best takes are marked

---

## Feature 6: Edge Cases and Error Handling

### Test Case 6.1: No Practice Folders
**Objective**: Verify behavior when no practice folders exist

**Prerequisites**:
- Empty root folder or folder with no audio files

**Steps**:
1. Open Practice Goals dialog
2. Try to create a goal
3. View progress

**Expected Results**:
- Goals can still be created
- Progress shows 0% (no practices found)
- No errors or crashes
- Appropriate message if no data available

**Pass Criteria**: ✅ Feature handles missing data gracefully

---

### Test Case 6.2: Song Name Not Found
**Objective**: Verify behavior when song name doesn't exist in practice folders

**Prerequisites**:
- Practice folders with some songs

**Steps**:
1. Create song practice goal with non-existent song name
2. View progress

**Expected Results**:
- Goal created successfully
- Progress shows 0% (song not found in any practice)
- No errors
- Goal remains visible and can be used when song is added later

**Pass Criteria**: ✅ Non-existent song names handled gracefully

---

### Test Case 6.3: Very Long Song Names
**Objective**: Verify UI handles long song names

**Steps**:
1. Create song goal with very long song name (100+ characters)
2. View in Active Goals and Manage Goals

**Expected Results**:
- Song name displays without breaking layout
- Text wraps or truncates appropriately
- No UI overflow or corruption

**Pass Criteria**: ✅ Long song names don't break UI

---

### Test Case 6.4: Special Characters in Song Names
**Objective**: Verify special characters are handled correctly

**Steps**:
1. Create song goal with special characters (e.g., "Song: Part 1 (Demo) [2025]")
2. Save and reload

**Expected Results**:
- Song name saved correctly
- JSON encoding handles special characters
- Progress calculation works
- No errors loading goals

**Pass Criteria**: ✅ Special characters handled correctly

---

### Test Case 6.5: Corrupted Goals File
**Objective**: Verify behavior when `.practice_goals.json` is corrupted

**Prerequisites**:
- Manually corrupt the goals JSON file

**Steps**:
1. Edit `.practice_goals.json` to have invalid JSON
2. Open Practice Goals dialog

**Expected Results**:
- Application doesn't crash
- Empty goals state shown (no goals)
- User can create new goals
- New goals file overwrites corrupted file

**Pass Criteria**: ✅ Corrupted file doesn't crash application

---

## Feature 7: Performance Tests

### Test Case 7.1: Large Number of Goals Performance
**Objective**: Verify performance with many goals

**Prerequisites**:
- Create 50+ goals

**Steps**:
1. Create 50 goals
2. Open Practice Goals dialog
3. Switch between tabs
4. Scroll through Active Goals

**Expected Results**:
- Dialog opens in reasonable time (< 2 seconds)
- No lag when switching tabs
- Scrolling is smooth
- Progress calculation completes quickly

**Pass Criteria**: ✅ Performance acceptable with many goals

---

### Test Case 7.2: Large Practice Folder Set Performance
**Objective**: Verify performance with many practice folders

**Prerequisites**:
- 50+ practice folders with audio files

**Steps**:
1. Create goals
2. Open Practice Goals dialog (triggers statistics analysis)
3. Check time to open

**Expected Results**:
- Dialog opens in reasonable time (< 5 seconds for 50 folders)
- Progress calculation completes
- No freezing or hanging

**Pass Criteria**: ✅ Performance acceptable with large data set

---

## Regression Tests

### Test Case 8.1: Practice Statistics Still Works
**Objective**: Verify Practice Statistics feature not affected

**Steps**:
1. Open Practice Statistics (Ctrl+Shift+S)
2. Verify all statistics display correctly
3. Check no errors or crashes

**Expected Results**:
- Practice Statistics works as before
- No interference from Practice Goals feature

**Pass Criteria**: ✅ No regression in Practice Statistics

---

### Test Case 8.2: Existing Features Unaffected
**Objective**: Verify other features still work

**Steps**:
1. Play audio files
2. Create annotations
3. Mark best takes
4. Use other menus and features

**Expected Results**:
- All existing features work normally
- No new errors or crashes
- Performance not degraded

**Pass Criteria**: ✅ No regressions in existing functionality

---

### Test Case 8.3: Keyboard Shortcuts Don't Conflict
**Objective**: Verify Ctrl+Shift+G doesn't conflict with other shortcuts

**Steps**:
1. Check all existing keyboard shortcuts still work
2. Verify Ctrl+Shift+G opens Practice Goals dialog
3. Verify Ctrl+Shift+S still opens Practice Statistics

**Expected Results**:
- No shortcut conflicts
- Both shortcuts work as intended
- Other shortcuts unaffected

**Pass Criteria**: ✅ No keyboard shortcut conflicts

---

## Known Limitations

1. **Time Estimation**: Practice time goals use rough estimation (3 minutes per file) rather than actual playback time tracking
2. **Date Range Limitations**: Goals cannot span multiple years (though date picker allows it)
3. **Goal History**: No historical view of completed/expired goals beyond 7 days
4. **Goal Editing**: Goals cannot be edited after creation, only deleted and recreated
5. **Notifications**: Goal achievement notifications are visual only (no system notifications)
6. **Multiple Root Folders**: Each root folder has separate goals (not shared across folders)

---

## Test Execution Summary

**Date**: _________________  
**Tester**: _________________  
**Build Version**: _________________  

### Results Summary

| Test Category | Total Tests | Passed | Failed | Skipped | Notes |
|--------------|-------------|--------|--------|---------|-------|
| Goal Creation | 9 | | | | |
| Progress Tracking | 8 | | | | |
| Persistence | 3 | | | | |
| UI/UX | 7 | | | | |
| Integration | 3 | | | | |
| Edge Cases | 5 | | | | |
| Performance | 2 | | | | |
| Regression | 3 | | | | |
| **TOTAL** | **40** | | | | |

### Test Execution Checklist

- [ ] All test cases executed
- [ ] Failed tests documented with bug reports
- [ ] Known limitations verified
- [ ] Screenshots captured for visual issues
- [ ] Performance metrics recorded
- [ ] Regression tests passed
- [ ] Ready for release

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
- Test on multiple operating systems if possible (Windows, macOS, Linux)
