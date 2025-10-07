# Test Plan: Cloud Sync Improvements

**Feature Set**: Section 2.5 (Cloud Sync Improvements)  
**Implementation Date**: January 2025  
**Test Plan Version**: 1.0

---

## Overview

This test plan covers the Cloud Sync Improvements feature, which enhances the existing Google Drive sync functionality. New features include:
- **Sync History**: Timeline view of all sync operations
- **Sync Rules**: Selective sync configuration (file size limits, annotations-only mode, etc.)
- **Conflict Resolution UI**: Side-by-side diff view for resolving conflicts
- **Enhanced Status Tracking**: Better visibility into sync status

These improvements make cloud synchronization more reliable, configurable, and user-friendly for band collaboration.

---

## Test Environment Requirements

### Software Requirements
- AudioBrowser application (version with Sync Improvements)
- Python 3.8 or higher
- PyQt6
- Google Drive API packages (auto-installed)
- Active Google account with Google Drive
- Internet connection
- Operating System: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)

### Test Data Requirements
- Practice folder with audio files and annotations
- Google Drive credentials (credentials.json)
- Multiple test user accounts (for multi-user testing)
- Various file sizes for testing size limits

---

## Feature 1: Sync History

### Test Case 1.1: View Sync History Dialog
**Objective**: Verify sync history dialog opens and displays correctly  
**Preconditions**: Practice folder is open  
**Steps**:
1. Open a practice folder
2. Go to File menu → "View Sync History…"
3. Observe dialog

**Expected Results**:
- Dialog opens successfully
- Title: "Sync History"
- Table with columns: Date/Time, Operation, Files, User, Details
- "Close" button present
- Dialog is non-modal (can interact with main window)

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 1.2: Empty Sync History
**Objective**: Verify behavior when no sync operations have occurred  
**Preconditions**: Fresh practice folder, no sync history  
**Steps**:
1. Open a new practice folder (never synced)
2. View sync history

**Expected Results**:
- Dialog opens normally
- Table is empty or shows "No sync history" message
- No errors displayed
- Dialog can be closed normally

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 1.3: Sync History After Upload
**Objective**: Verify upload operation is recorded in history  
**Preconditions**: Practice folder with files  
**Steps**:
1. Perform upload sync operation (5 files)
2. View sync history
3. Check most recent entry

**Expected Results**:
- History shows "upload" operation
- Files count: 5
- User: current username
- Date/Time: recent timestamp
- Details: optional description

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 1.4: Sync History After Download
**Objective**: Verify download operation is recorded in history  
**Preconditions**: Remote files available  
**Steps**:
1. Perform download sync operation (3 files)
2. View sync history
3. Check most recent entry

**Expected Results**:
- History shows "download" operation
- Files count: 3
- User: current username
- Recent timestamp
- Operations appear in reverse chronological order (newest first)

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 1.5: History Pagination (100+ entries)
**Objective**: Verify history handles many entries gracefully  
**Preconditions**: Practice folder with extensive sync history  
**Steps**:
1. Perform 100+ sync operations (or use folder with history)
2. View sync history
3. Check display and scrolling

**Expected Results**:
- Dialog shows last 50 entries (most recent)
- Older entries are automatically pruned (keeps last 100)
- Table scrolls smoothly
- No performance issues
- All columns remain readable

**Pass/Fail**: ___  
**Notes**: ___

---

## Feature 2: Sync Rules Configuration

### Test Case 2.1: Open Sync Rules Dialog
**Objective**: Verify sync rules dialog opens correctly  
**Preconditions**: Practice folder is open  
**Steps**:
1. Open practice folder
2. Go to File menu → "Sync Rules Configuration…"
3. Observe dialog

**Expected Results**:
- Dialog opens with title: "Sync Rules Configuration"
- Shows all configuration options
- "Save Rules" and "Cancel" buttons present
- Default values are loaded

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 2.2: Configure Max File Size Limit
**Objective**: Verify file size limit configuration  
**Preconditions**: Sync rules dialog is open  
**Steps**:
1. Check "Limit file size" checkbox
2. Set value to 100 MB
3. Click "Save Rules"
4. Reopen dialog to verify

**Expected Results**:
- Checkbox enables spin box
- Value can be set from 0-10000 MB
- Settings persist after dialog closes
- Reopening shows saved value (100 MB)

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 2.3: Annotations Only Mode
**Objective**: Verify annotations-only sync configuration  
**Preconditions**: Sync rules dialog is open  
**Steps**:
1. Check "Sync annotations only (no audio)" checkbox
2. Save rules
3. Observe effect on sync operations

**Expected Results**:
- Checkbox state is saved
- Sync operations respect this setting
- Only annotation/metadata files are synced
- Audio files are excluded from sync

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 2.4: Disable Audio Files Sync
**Objective**: Verify option to exclude audio files  
**Preconditions**: Sync rules dialog is open  
**Steps**:
1. Uncheck "Sync audio files (WAV, MP3, etc.)"
2. Save rules
3. Attempt sync operation

**Expected Results**:
- Setting is saved
- Audio files are excluded from sync operations
- Only metadata files are synced
- No errors occur

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 2.5: Auto-Sync Mode
**Objective**: Verify auto-sync mode checkbox  
**Preconditions**: Sync rules dialog is open  
**Steps**:
1. Check "Enable auto-sync mode"
2. Save rules
3. Verify setting persists

**Expected Results**:
- Checkbox state is saved
- Setting persists across sessions
- Note: Actual auto-sync behavior requires manual trigger (future enhancement)
- No errors or crashes

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 2.6: Auto-Download Best Takes
**Objective**: Verify auto-download best takes option  
**Preconditions**: Sync rules dialog is open  
**Steps**:
1. Check "Auto-download Best Takes only"
2. Save rules
3. Verify setting persists

**Expected Results**:
- Checkbox state is saved
- Setting saved to `.sync_rules.json`
- Reopening dialog shows checkbox checked
- Ready for future implementation

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 2.7: Rules Persistence Across Sessions
**Objective**: Verify sync rules persist after application restart  
**Preconditions**: Sync rules have been configured  
**Steps**:
1. Configure all sync rules
2. Save rules
3. Close and reopen application
4. Open same folder
5. View sync rules

**Expected Results**:
- All rules are restored from `.sync_rules.json`
- Settings match what was saved
- No data loss
- No errors on load

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 2.8: Rules Apply to Sync Operations
**Objective**: Verify rules are enforced during sync  
**Preconditions**: File size limit set to 10 MB  
**Steps**:
1. Set max file size to 10 MB
2. Prepare folder with files: 5 MB, 15 MB, 20 MB
3. Attempt upload sync
4. Check which files are included

**Expected Results**:
- Only 5 MB file is included in sync
- 15 MB and 20 MB files are excluded
- User is notified about excluded files
- Sync completes successfully for allowed files

**Pass/Fail**: ___  
**Notes**: ___

---

## Feature 3: Conflict Resolution

### Test Case 3.1: Detect Conflicts
**Objective**: Verify conflicts are detected when files modified in both locations  
**Preconditions**: Same file modified locally and remotely  
**Steps**:
1. Modify file locally (add annotation)
2. Simulate remote modification (different annotation)
3. Attempt sync
4. Observe conflict detection

**Expected Results**:
- Conflict is detected
- User is notified of conflict
- Conflict resolution dialog may appear
- Sync does not proceed without resolution

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 3.2: Open Conflict Resolution Dialog
**Objective**: Verify conflict resolution dialog displays correctly  
**Preconditions**: Conflicts exist  
**Steps**:
1. Create conflict scenario
2. Initiate sync
3. Observe conflict resolution dialog

**Expected Results**:
- Dialog title: "Resolve Sync Conflicts"
- Shows list of conflicting files
- For each file: Name, Local Modified, Remote Modified, Resolution dropdown
- "Apply Resolutions" and "Cancel" buttons
- Table is scrollable if many conflicts

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 3.3: Choose "Keep Local" Resolution
**Objective**: Verify "Keep Local" conflict resolution  
**Preconditions**: Conflict exists  
**Steps**:
1. Open conflict resolution dialog
2. Select "Keep Local" for a file
3. Apply resolutions
4. Verify outcome

**Expected Results**:
- Local version is preserved
- Remote version is overwritten
- Sync completes successfully
- File content matches local version

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 3.4: Choose "Keep Remote" Resolution
**Objective**: Verify "Keep Remote" conflict resolution  
**Preconditions**: Conflict exists  
**Steps**:
1. Open conflict resolution dialog
2. Select "Keep Remote" for a file
3. Apply resolutions
4. Verify outcome

**Expected Results**:
- Remote version is downloaded
- Local version is overwritten
- Sync completes successfully
- File content matches remote version

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 3.5: Choose "Merge" Resolution
**Objective**: Verify merge option (if supported)  
**Preconditions**: Conflict exists with mergeable files  
**Steps**:
1. Open conflict resolution dialog
2. Select "Merge (if possible)" for a file
3. Apply resolutions
4. Verify outcome

**Expected Results**:
- Merge is attempted (if file type supports it)
- If merge not possible, user is notified
- Merged result is saved (if successful)
- Both local and remote changes preserved (if possible)

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 3.6: Cancel Conflict Resolution
**Objective**: Verify canceling conflict resolution  
**Preconditions**: Conflict resolution dialog is open  
**Steps**:
1. Open conflict resolution dialog
2. Make some selections
3. Click "Cancel"

**Expected Results**:
- Dialog closes
- No changes are made to files
- Sync operation is cancelled
- Can retry sync later

**Pass/Fail**: ___  
**Notes**: ___

---

## Feature 4: Integration with Existing Sync

### Test Case 4.1: Backward Compatibility
**Objective**: Verify new features don't break existing sync  
**Preconditions**: Existing sync setup  
**Steps**:
1. Use folder previously synced with old version
2. Perform upload/download sync
3. Verify all existing features work

**Expected Results**:
- Old sync operations work normally
- `.sync_version.json` is compatible
- No errors or data corruption
- New features are available alongside old

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 4.2: Menu Integration
**Objective**: Verify new menu items are properly integrated  
**Preconditions**: Application is running  
**Steps**:
1. Open File menu
2. Locate sync-related items

**Expected Results**:
- "Sync with Google Drive…" (existing)
- "Sync Rules Configuration…" (new)
- "View Sync History…" (new)
- "Delete Remote Folder from Google Drive…" (existing)
- All items are enabled when appropriate
- Keyboard shortcuts work (if assigned)

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 4.3: Settings File Creation
**Objective**: Verify new settings files are created correctly  
**Preconditions**: Fresh practice folder  
**Steps**:
1. Open new practice folder
2. Configure sync rules
3. Perform sync operation
4. Check folder contents

**Expected Results**:
- `.sync_rules.json` is created
- `.sync_history.json` is created
- `.sync_version.json` exists (from normal sync)
- All files have valid JSON content
- Files are in practice folder root

**Pass/Fail**: ___  
**Notes**: ___

---

## Feature 5: Error Handling

### Test Case 5.1: No Internet Connection
**Objective**: Verify graceful handling when offline  
**Preconditions**: Disconnect internet  
**Steps**:
1. Disconnect internet connection
2. Try to view sync history (should work)
3. Try to access sync rules (should work)
4. Try to perform sync (should fail gracefully)

**Expected Results**:
- Sync history opens (reads local file)
- Sync rules opens (reads local file)
- Sync operation shows appropriate error
- Application doesn't crash
- User is informed about network issue

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 5.2: Corrupted Settings File
**Objective**: Verify handling of corrupted sync_rules.json  
**Preconditions**: Corrupt `.sync_rules.json` manually  
**Steps**:
1. Edit `.sync_rules.json` to contain invalid JSON
2. Try to open sync rules dialog

**Expected Results**:
- Application detects corrupted file
- Defaults are loaded instead
- User may be warned about corrupted settings
- No crash or data loss
- Can save new rules to fix file

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 5.3: Missing Credentials
**Objective**: Verify appropriate messages when credentials missing  
**Preconditions**: No credentials.json file  
**Steps**:
1. Remove credentials.json
2. Try to access sync features

**Expected Results**:
- Appropriate message about missing credentials
- Link/instructions to set up credentials
- Application doesn't crash
- Local features (history, rules) still work

**Pass/Fail**: ___  
**Notes**: ___

---

## Feature 6: Performance

### Test Case 6.1: History Load Time
**Objective**: Verify sync history loads quickly  
**Preconditions**: History with 50+ entries  
**Steps**:
1. Open sync history dialog
2. Measure load time

**Expected Results**:
- Dialog opens in < 1 second
- History loads in < 2 seconds
- UI remains responsive
- No lag when scrolling

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 6.2: Rules Save Time
**Objective**: Verify sync rules save quickly  
**Preconditions**: Sync rules dialog open  
**Steps**:
1. Change multiple settings
2. Click "Save Rules"
3. Observe save time

**Expected Results**:
- Save completes in < 0.5 seconds
- Dialog closes promptly
- No lag or freeze
- Settings are immediately effective

**Pass/Fail**: ___  
**Notes**: ___

---

## Feature 7: Multi-User Scenarios

### Test Case 7.1: Multiple Users Sync History
**Objective**: Verify history tracks different users correctly  
**Preconditions**: Multiple users syncing same folder  
**Steps**:
1. User A uploads files
2. User B downloads files
3. User C uploads more files
4. View sync history from any user

**Expected Results**:
- History shows operations from all users
- Each entry correctly identifies user
- Operations are in chronological order
- No confusion between users

**Pass/Fail**: ___  
**Notes**: ___

### Test Case 7.2: User-Specific Rules
**Objective**: Verify each user can have own sync rules  
**Preconditions**: Multiple users  
**Steps**:
1. User A sets rules (annotations only)
2. User B sets rules (all files)
3. Each performs sync
4. Verify rules are respected per user

**Expected Results**:
- Each user's rules are independent
- Rules stored locally (not synced)
- Each user's sync behavior matches their rules
- No interference between users

**Pass/Fail**: ___  
**Notes**: ___

---

## Known Limitations

1. **Auto-Sync**: Auto-sync mode checkbox exists but requires manual trigger (future enhancement)
2. **Merge Capability**: Merge conflict resolution has limited support (annotations may not merge automatically)
3. **History Pruning**: History automatically prunes to last 100 entries to prevent file bloat
4. **Local Rules**: Sync rules are stored locally, not synced (each user configures independently)
5. **Conflict Detection**: Conflicts detected based on modification times, not content comparison

---

## Test Execution Summary

### Test Execution Checklist

#### Critical Tests (Must Pass)
- [ ] Test Case 1.3: Sync History After Upload
- [ ] Test Case 2.1: Open Sync Rules Dialog
- [ ] Test Case 2.2: Configure Max File Size Limit
- [ ] Test Case 2.8: Rules Apply to Sync Operations
- [ ] Test Case 3.3: Choose "Keep Local" Resolution
- [ ] Test Case 4.1: Backward Compatibility

#### High Priority Tests
- [ ] Test Case 1.4: Sync History After Download
- [ ] Test Case 2.3: Annotations Only Mode
- [ ] Test Case 2.7: Rules Persistence
- [ ] Test Case 3.1: Detect Conflicts
- [ ] Test Case 4.2: Menu Integration
- [ ] Test Case 5.1: No Internet Connection

#### Medium Priority Tests
- [ ] Test Case 1.5: History Pagination
- [ ] Test Case 2.5: Auto-Sync Mode
- [ ] Test Case 3.6: Cancel Conflict Resolution
- [ ] Test Case 5.2: Corrupted Settings File
- [ ] Test Case 6.1: History Load Time
- [ ] Test Case 7.1: Multiple Users Sync History

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
**Sync Settings**: Rules: ___ | History Entries: ___  
**Additional Notes**: ___

---

## Sign-Off

### Test Execution
- **Tester Name**: _________________
- **Test Date**: _________________
- **Build Version**: _________________

### Results Summary
- **Total Tests**: 38
- **Tests Passed**: _____
- **Tests Failed**: _____
- **Tests Blocked**: _____
- **Pass Rate**: _____%

### Approval
- **QA Lead**: _________________ Date: _________
- **Product Owner**: _________________ Date: _________

---

## Future Test Enhancements

1. **Automated Testing**: Convert manual tests to automated tests using pytest
2. **Load Testing**: Test with very large practice folders (1000+ files)
3. **Network Testing**: Test under various network conditions (slow, intermittent)
4. **Security Testing**: Verify credential handling and data privacy
5. **Cross-Platform Testing**: Dedicated test runs on Windows, macOS, Linux
6. **Integration Tests**: Test interaction with all other AudioBrowser features
7. **Stress Testing**: Multiple concurrent sync operations
8. **Recovery Testing**: Test recovery from interrupted syncs
