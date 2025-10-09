# AudioBrowser Applications - Comprehensive Test Plan

**Document Version**: 1.0  
**Created**: January 2025  
**Purpose**: Collated test plan for thorough testing of both AudioBrowser applications

---

## Table of Contents

### Part A: AudioBrowserOrig Test Plans
1. [Clickable Status Bar Items](#audiobrowserorig-1-clickable-status-bar-items) (23 test cases)
2. [Now Playing Panel](#audiobrowserorig-2-now-playing-panel) (29 test cases)
3. [Performance Improvements](#audiobrowserorig-3-performance-improvements) (41 test cases)
4. [Practice Goals](#audiobrowserorig-4-practice-goals) (40 test cases)
5. [Setlist Builder](#audiobrowserorig-5-setlist-builder) (43 test cases)
6. [Spectral Analysis](#audiobrowserorig-6-spectral-analysis) (35 test cases)
7. [Stereo Waveform View](#audiobrowserorig-7-stereo-waveform-view) (15 test cases)
8. [Sync Improvements](#audiobrowserorig-8-sync-improvements) (38 test cases)
9. [Tempo & Metronome](#audiobrowserorig-9-tempo-metronome) (31 test cases)
10. [Workspace Layouts & Progress](#audiobrowserorig-10-workspace-progress) (24 test cases)

### Part B: AudioBrowser-QML Test Plans
11. [Spectrogram Overlay](#audiobrowser-qml-11-spectrogram-overlay) (26 test cases)

### Test Execution Resources
- [Master Test Tracking Template](#master-test-tracking-template)
- [Bug Reporting Template](#bug-reporting-template)
- [Test Environment Setup](#test-environment-setup)
- [Overall Test Summary](#overall-test-summary)

---

## Executive Summary

This collated test plan covers **345 total test cases** across both AudioBrowser applications:

- **AudioBrowserOrig**: 319 test cases across 10 features
- **AudioBrowser-QML**: 26 test cases (1 major feature)

### Test Priority Breakdown
- **Critical Priority**: ~75 test cases (must pass for release)
- **High Priority**: ~140 test cases (should pass for quality release)
- **Medium Priority**: ~70 test cases (important for user experience)
- **Low Priority**: ~20 test cases (nice-to-have validations)

### Test Coverage Areas
- ✅ UI/UX functionality and workflows
- ✅ Feature integration and data consistency
- ✅ Performance and optimization
- ✅ Edge cases and error handling
- ✅ Persistence and data integrity
- ✅ Regression testing of existing features
- ✅ Cross-platform compatibility considerations

---

## Test Environment Setup

### Hardware Requirements
- **Minimum**: 4-core CPU, 8GB RAM, 10GB free disk space
- **Recommended**: 8-core CPU, 16GB RAM, SSD storage, 1920x1080+ display
- **Multi-core CPU** for parallel processing tests
- **Sufficient disk space** for test audio libraries and caches

### Software Requirements
- **Python**: 3.8+ (3.9+ recommended)
- **PyQt6**: Latest version
- **AudioBrowser**: Latest development build
- **Audio Codecs**: Support for WAV and MP3 formats
- **Operating Systems**: Windows, macOS, or Linux

### Test Data Requirements
- **Small library**: 10-50 audio files (~50-250 MB)
- **Medium library**: 100-500 audio files (~500 MB - 2.5 GB)
- **Large library**: 1000+ audio files (~5 GB+)
- **Practice folders**: Multiple dated folders with various file states
- **Best Take samples**: Mix of files marked and unmarked
- **Annotation samples**: Files with existing annotations
- **Special cases**: Long filenames, special characters, corrupted files

---

## Quick Reference Guide

### Keyboard Shortcuts to Test
- `Ctrl+Shift+G` - Practice Goals dialog
- `Ctrl+Shift+S` - Practice Statistics
- `Ctrl+Shift+L` - Save Window Layout
- `Ctrl+Shift+R` - Restore Window Layout
- `Ctrl+Shift+H` - Documentation Browser
- `Space` - Play/Pause
- `N` - Add annotation

### Common Test Scenarios
1. **First-time user** - Fresh install, no data
2. **Power user** - Large library, many annotations
3. **Band practice** - Real-time annotation workflow
4. **Library organization** - Batch operations, best take marking
5. **Performance preparation** - Setlist creation and export
6. **Data migration** - Existing data, cache compatibility

---

# Part A: AudioBrowserOrig Test Plans

---

<a name="audiobrowserorig-1-clickable-status-bar-items"></a>
## AudioBrowserOrig 1: Clickable Status Bar Items

**Feature**: Interactive status bar statistics for quick filtering  
**Test Cases**: 23  
**Full Test Plan**: [TEST_PLAN_CLICKABLE_STATUS.md](AudioBrowserOrig/docs/test_plans/TEST_PLAN_CLICKABLE_STATUS.md)

### Feature Overview
Allows users to click on status bar statistics to quickly filter and navigate to specific file categories (reviewed files, files without names, best takes, partial takes).

### Test Categories

#### Visual Display & Interaction (3 tests)
- **1.1 Visual Appearance**: Verify clickable items appear with blue color and underline
- **1.2 Cursor Changes on Hover**: Verify cursor changes to hand pointer
- **1.3 Hover Text Effect**: Verify text becomes bold on hover

#### Reviewed Files Actions (2 tests)
- **2.1 Click "X reviewed"**: Shows dialog with list of reviewed files
- **2.2 Click with No Reviewed**: Item hidden when count is 0

#### Files Without Names Actions (2 tests)
- **3.1 Click "X without names"**: Switches to Library tab and shows files
- **3.2 Click with All Named**: Item hidden when all files have names

#### Best Takes Actions (2 tests)
- **4.1 Click "X best takes"**: Switches to Library tab and shows best takes
- **4.2 Singular/Plural Grammar**: Correct "take" vs "takes" text

#### Partial Takes Actions (2 tests)
- **5.1 Click "X partial takes"**: Switches to Library tab and shows partial takes
- **5.2 Singular/Plural Grammar**: Correct "take" vs "takes" text

#### Dynamic Updates (3 tests)
- **6.1 Status Updates When Marking**: Counts update when files marked/unmarked
- **6.2 Status Updates When Providing Names**: Counts update with name changes
- **6.3 Status Updates When Reviewing**: Counts update with review status

#### Edge Cases (4 tests)
- **7.1 Empty Folder**: Handles no files gracefully
- **7.2 Large File List**: Dialog truncates >10 files with "..."
- **7.3 Rapid Clicking**: Handles multiple rapid clicks
- **7.4 Tab Already on Library**: Works when already on target tab

#### Integration (3 tests)
- **8.1 Progress Indicators Compatibility**: Coexists with progress bars
- **8.2 Window Resizing**: Adapts to window size changes
- **8.3 Dark Mode Compatibility**: Works correctly in dark mode

#### Accessibility (2 tests)
- **9.1 Keyboard Navigation**: ⚠️ Not yet implemented (future enhancement)
- **9.2 Screen Reader Compatibility**: ⚠️ Needs enhancement (future)

**Status**: ✅ Production-ready (core functionality complete)

---

<a name="audiobrowserorig-2-now-playing-panel"></a>
## AudioBrowserOrig 2: Now Playing Panel

**Feature**: Persistent playback controls and quick annotation entry  
**Test Cases**: 29  
**Full Test Plan**: [TEST_PLAN_NOW_PLAYING_PANEL.md](AudioBrowserOrig/docs/test_plans/TEST_PLAN_NOW_PLAYING_PANEL.md)

### Feature Overview
Provides a persistent panel below the player bar with playback controls, mini waveform, and quick annotation entry accessible from any tab.

### Test Categories

#### Panel Visibility & Layout (2 tests)
- **1.1 Panel Appears**: Visible in main window with proper layout
- **1.2 Position Remains Fixed**: Panel stays visible across all tabs

#### File Loading & Display (3 tests)
- **2.1 Panel Updates When File Loaded**: Shows filename, enables controls
- **2.2 Panel Updates During Playback**: Time and waveform update continuously
- **2.3 Panel Clears When Playback Stops**: Returns to "No file loaded" state

#### Playback Controls (2 tests)
- **3.1 Play/Pause Synchronization**: Panel button syncs with main player
- **3.2 Keyboard Shortcuts**: Space bar updates panel button state

#### Quick Annotation Entry (6 tests)
- **4.1 Add via Text Entry**: Enter annotation and press Enter
- **4.2 Add via Button**: Click "Add Note" button
- **4.3 Empty Text Handling**: No annotation added for empty text
- **4.4 Annotation While Paused**: Works at current position when paused
- **4.5 Integration with Undo**: Quick annotations support undo/redo
- **4.6 Multiple Quick Annotations**: Can add several annotations in sequence

#### Collapsible Panel (4 tests)
- **5.1 Collapse Panel**: Hides content, shows only header
- **5.2 Expand Panel**: Shows content again
- **5.3 Collapsed State Persists**: Remembers state across sessions
- **5.4 Expanded State Persists**: Remembers state across sessions

#### Workspace Layout Integration (2 tests)
- **6.1 Save Layout Saves Panel State**: Layout includes panel state
- **6.2 Reset Layout Resets Panel**: Returns to default (expanded)

#### Multi-Tab Workflow (3 tests)
- **7.1 Add Annotation from Library Tab**: No need to switch to Annotations tab
- **7.2 Add from Folder Notes Tab**: Works from any tab
- **7.3 Playback Control from Any Tab**: Controls work from all tabs

#### Edge Cases & Error Handling (4 tests)
- **8.1 Long File Names**: Displays without breaking layout
- **8.2 Rapid File Switching**: Updates correctly without flickering
- **8.3 Special Characters**: Handles special characters in annotations
- **8.4 Panel with No Audio File**: Disabled state handled gracefully

#### Regression Tests (3 tests)
- **9.1 Existing Annotation Features**: Both methods work correctly
- **9.2 Main Player Controls Unaffected**: All controls work normally
- **9.3 Keyboard Shortcuts Still Work**: No conflicts with shortcuts

**Known Limitations**:
1. Mini waveform shows progress indicator, not actual waveform thumbnail
2. Quick annotations don't support categories or importance flags
3. Only creates point annotations, not clip ranges

**Status**: ✅ Production-ready

---

<a name="audiobrowserorig-3-performance-improvements"></a>
## AudioBrowserOrig 3: Performance Improvements & Large Library Support

**Feature**: Faster startup, lazy loading, pagination, and parallel processing  
**Test Cases**: 41  
**Full Test Plan**: [TEST_PLAN_PERFORMANCE_IMPROVEMENTS.md](AudioBrowserOrig/docs/test_plans/TEST_PLAN_PERFORMANCE_IMPROVEMENTS.md)

### Feature Overview
Enables efficient handling of large audio libraries (1000+ files) through lazy loading, parallel waveform generation, pagination, and smart caching.

### Test Categories

#### Lazy Loading of Waveforms (3 tests)
- **1.1 Disable Auto-Generation**: Folder loads quickly without waveform generation
- **1.2 On-Demand Generation**: Waveforms generate only when file is selected
- **1.3 Setting Persistence**: Lazy loading preference persists across sessions

#### Parallel Waveform Generation (3 tests)
- **2.1 Multi-Threaded Generation**: Multiple CPU cores used for faster generation
- **2.2 Resource Management**: Respects system resources, doesn't overwhelm CPU
- **2.3 Cancellation**: User can cancel parallel generation cleanly

#### Incremental Processing (3 tests)
- **3.1 Skip Already-Cached**: Only generates new/changed files
- **3.2 Cache Validation**: Detects modified files and regenerates
- **3.3 Progress Indicator**: Shows accurate incremental progress

#### Pagination for Large Libraries (5 tests)
- **4.1 Enable for 1000+ Files**: Pagination activates automatically
- **4.2 Navigate Between Pages**: Next/previous page navigation works
- **4.3 Search Across All Pages**: Search scans entire library
- **4.4 Large Library Performance**: Remains responsive with 1000+ files
- **4.5 Pagination Configuration**: Can adjust chunk size or disable

#### Advanced Audio Analysis Display (3 tests)
- **5.1 Enhanced Fingerprint Display**: Confidence scores with color coding
- **5.2 Spectral Analysis**: Visualization of frequency data (if implemented)
- **5.3 Algorithm Comparison**: Compare multiple fingerprint algorithms

#### Cache Management (3 tests)
- **6.1 View Cache Statistics**: Shows size, count, location
- **6.2 Clear Cache**: Manual cache clearing works correctly
- **6.3 Automatic Cleanup**: Removes orphaned cache entries

#### Startup Optimization (3 tests)
- **7.1 Fast Startup**: Measures improved launch time
- **7.2 Background Generation Performance**: UI stays responsive during generation
- **7.3 Memory Usage**: Reasonable memory with large libraries

#### Progress Indicators (2 tests)
- **8.1 Detailed Progress**: Shows percentage, file count, time estimates
- **8.2 Fingerprint Progress**: Progress indicator for fingerprints

#### Settings & Preferences (2 tests)
- **9.1 Auto-Generation Preferences**: All settings configurable
- **9.2 Apply Without Restart**: Settings take effect immediately when possible

#### Edge Cases & Error Handling (5 tests)
- **10.1 Empty Folder**: Handles gracefully
- **10.2 Corrupted Audio File**: Skips and continues
- **10.3 Insufficient Disk Space**: Clear error message
- **10.4 Permission Issues**: Handles read-only folders
- **10.5 Very Large Files**: Processes >100MB files successfully

#### Backward Compatibility (2 tests)
- **11.1 Old Cache Format**: Reads old cache files
- **11.2 Mixed Cache Versions**: Handles mix of old and new caches

#### Integration with Existing Features (3 tests)
- **12.1 Fingerprinting Integration**: Works with lazy loading
- **12.2 Best Takes and Reviewed Status**: Pagination doesn't break functionality
- **12.3 Annotations with Lazy Loading**: Annotations work during waveform load

#### Performance Benchmarks (4 tests)
- **13.1 Small Library (30 files)**: Baseline performance metrics
- **13.2 Medium Library (200 files)**: Scaled performance metrics
- **13.3 Large Library (1200 files)**: Large-scale performance metrics
- **13.4 Parallel vs Sequential**: Measures parallel processing improvement

**Pass Criteria**:
- Folder load < 5 seconds (1000+ files)
- Waveform generation: 2x+ faster with parallel processing
- Memory usage < 1 GB for large libraries
- File selection < 200ms response time
- Pagination page load < 500ms

**Known Limitations**:
1. Virtual scrolling not implemented (using pagination)
2. No GPU acceleration (CPU-only)
3. No database backend (JSON files)
4. No global search (per-folder only)

**Status**: ✅ Production-ready

---

<a name="audiobrowserorig-4-practice-goals"></a>
## AudioBrowserOrig 4: Practice Goals

**Feature**: Set and track practice goals (time, sessions, song-specific)  
**Test Cases**: 40  
**Full Test Plan**: [TEST_PLAN_PRACTICE_GOALS.md](AudioBrowserOrig/docs/test_plans/TEST_PLAN_PRACTICE_GOALS.md)

### Feature Overview
Allows users to set and track various practice goals including weekly/monthly time targets, session counts, and song-specific goals (practice count and best take achievement).

### Test Categories

#### Goal Creation & Management (9 tests)
- **1.1 Access Dialog**: Help menu and Ctrl+Shift+G shortcut
- **1.2 Create Weekly Time Goal**: 300 minutes target
- **1.3 Create Monthly Session Count**: Target number of practice sessions
- **1.4 Create Song Practice Count**: Per-song practice tracking
- **1.5 Create Song Best Take Goal**: Track best take achievement for a song
- **1.6 Invalid - Missing Song Name**: Validation prevents creation
- **1.7 Invalid - Invalid Date Range**: Validation prevents invalid dates
- **1.8 Delete Goal**: Confirmation and removal
- **1.9 Cancel Deletion**: Deletion can be canceled

#### Goal Progress Tracking (8 tests)
- **2.1 Weekly Time Progress**: Estimated time calculation (files × 3 min)
- **2.2 Session Count Progress**: Counts practice folders in date range
- **2.3 Song Practice Count**: Counts sessions containing specific song
- **2.4 Song Best Take Progress**: Detects best take marking
- **2.5 Status - In Progress**: Shows days remaining
- **2.6 Status - Complete**: Shows completion message with ✅
- **2.7 Status - Expired**: Shows warning with ⚠️
- **2.8 Days Remaining**: Accurate countdown

#### Goal Persistence (3 tests)
- **3.1 Saved Across Sessions**: Goals persist after restart
- **3.2 Goals File Location**: Stored in `.practice_goals.json` in root folder
- **3.3 Survive Folder Changes**: Each folder has separate goals

#### UI/UX Tests (7 tests)
- **4.1 Form Field Updates**: Fields adapt to goal type selection
- **4.2 Date Picker Functionality**: Calendar widget works correctly
- **4.3 Goal Card Visual Design**: Clear and informative display
- **4.4 Tab Navigation**: Smooth tab switching
- **4.5 Dialog Resizing**: Adapts to window size
- **4.6 Empty State Display**: Friendly message when no goals
- **4.7 Many Goals Display**: Handles 10+ goals without issues

#### Integration Tests (3 tests)
- **5.1 Integration with Statistics**: Consistent with Practice Statistics
- **5.2 Updates After New Practice**: Progress recalculated with new data
- **5.3 Best Take Goal Updates**: Updates when best takes marked

#### Edge Cases & Error Handling (5 tests)
- **6.1 No Practice Folders**: Handles missing data gracefully
- **6.2 Song Name Not Found**: 0% progress for non-existent song
- **6.3 Very Long Song Names**: UI handles long text
- **6.4 Special Characters**: Handles special characters in song names
- **6.5 Corrupted Goals File**: Doesn't crash, allows new goals

#### Performance Tests (2 tests)
- **7.1 Large Number of Goals**: 50+ goals performance
- **7.2 Large Practice Folder Set**: 50+ folders performance

#### Regression Tests (3 tests)
- **8.1 Practice Statistics Still Works**: No interference
- **8.2 Existing Features Unaffected**: All features work normally
- **8.3 Keyboard Shortcuts**: No conflicts with Ctrl+Shift+G

**Known Limitations**:
1. Time estimation uses rough calculation (3 min/file), not actual playback time
2. Goals cannot span multiple years
3. No historical view beyond 7 days for completed/expired goals
4. Goals cannot be edited after creation, only deleted and recreated
5. No system notifications, only visual feedback
6. Each root folder has separate goals (not shared)

**Status**: ✅ Production-ready

---

<a name="audiobrowserorig-5-setlist-builder"></a>
## AudioBrowserOrig 5: Setlist Builder

**Feature**: Create and manage performance setlists  
**Test Cases**: 43  
**Full Test Plan**: [TEST_PLAN_SETLIST_BUILDER.md](AudioBrowserOrig/docs/test_plans/TEST_PLAN_SETLIST_BUILDER.md)

### Feature Overview
Allows users to create and manage performance setlists, organize songs from practice sessions, validate setlist readiness, and export setlists for performance preparation.

### Test Categories

#### Setlist Management (4 tests)
- **1.1 Create New Setlist**: Name entry and creation
- **1.2 Switch Between Setlists**: Multiple setlists
- **1.3 Delete Setlist**: With confirmation
- **1.4 Rename Setlist**: Update setlist name

#### Song Management (9 tests)
- **2.1 Add Song to Setlist**: From practice folders
- **2.2 Remove Song**: Delete from setlist
- **2.3 Reorder Songs**: Drag-and-drop
- **2.4 Song Information Display**: Shows provided name, folder, best take status
- **2.5 Quick Add Best Takes**: Add all best takes at once
- **2.6 Add Multiple Songs**: Select and add multiple
- **2.7 Duplicate Song Handling**: Allow or warn about duplicates
- **2.8 Empty Setlist**: Handle no songs gracefully
- **2.9 Song Count Display**: Shows "X songs" in setlist

#### Performance Notes (2 tests)
- **3.1 Add Performance Notes**: Per-song notes
- **3.2 Edit Performance Notes**: Update existing notes

#### Duration Calculation (3 tests)
- **4.1 Total Duration Display**: Sum of all song durations
- **4.2 Update on Add/Remove**: Recalculates dynamically
- **4.3 Duration Formatting**: Shows hours:minutes:seconds

#### Practice Mode (3 tests)
- **5.1 Enable Practice Mode**: Toggle practice mode
- **5.2 Play Songs in Sequence**: Automatic progression
- **5.3 Loop Setlist**: Repeat from start after last song

#### Validation (4 tests)
- **6.1 Check for Missing Files**: Warns about moved/deleted files
- **6.2 Validate Best Takes**: All songs should have best takes
- **6.3 Validation Report**: Shows issues clearly
- **6.4 Fix Validation Issues**: Guide user to fix problems

#### Export (4 tests)
- **7.1 Export to Text File**: Plain text format
- **7.2 Export to PDF**: Formatted PDF
- **7.3 Export to M3U Playlist**: Audio player compatible
- **7.4 Export with Performance Notes**: Include notes in export

#### Data Persistence (3 tests)
- **8.1 Setlists Saved**: Persist across sessions
- **8.2 File Location**: `.setlists.json` in root folder
- **8.3 Backup/Restore**: Export and import setlists

#### Integration with Main Application (3 tests)
- **9.1 Add Songs from Different Folders**: Cross-folder support
- **9.2 Best Take Status Detection**: Correctly identifies best takes
- **9.3 Provided Name Display**: Shows user-assigned names

#### Edge Cases (5 tests)
- **10.1 Very Long Setlist**: 100+ songs
- **10.2 Special Characters**: Handles special chars in song names
- **10.3 Missing Audio Files**: Handles moved/deleted files
- **10.4 Corrupt Setlist File**: Recovery handling
- **10.5 Empty Practice Folder**: No songs available

#### Keyboard Shortcuts (1 test)
- **11.1 Open Dialog Shortcut**: Keyboard shortcut to open

#### Regression Tests (2 tests)
- **12.1 No Impact on Existing Features**: Other features unaffected
- **12.2 JSON File Compatibility**: Compatible with existing JSON structure

**Status**: ✅ Production-ready

---

<a name="audiobrowserorig-6-spectral-analysis"></a>
## AudioBrowserOrig 6: Spectral Analysis

**Feature**: Spectrogram visualization and frequency analysis  
**Test Cases**: 35 (estimated)  
**Full Test Plan**: [TEST_PLAN_SPECTRAL_ANALYSIS.md](AudioBrowserOrig/docs/test_plans/TEST_PLAN_SPECTRAL_ANALYSIS.md)

### Feature Overview
Provides spectrogram visualization overlaid on waveforms, allowing users to see frequency content over time for better audio analysis.

### Key Test Areas
- Spectrogram generation and caching
- Overlay on waveform display
- Color gradient visualization
- Performance with large files
- Integration with playback and annotation
- Settings and preferences
- Edge cases (very short/long files, corrupted audio)

**Note**: Full test case details available in source document.

**Status**: ✅ Production-ready

---

<a name="audiobrowserorig-7-stereo-waveform-view"></a>
## AudioBrowserOrig 7: Stereo Waveform View & Channel Muting

**Feature**: Separate left/right channel waveforms and channel muting  
**Test Cases**: 15  
**Full Test Plan**: [TEST_PLAN_STEREO_WAVEFORM.md](AudioBrowserOrig/docs/test_plans/TEST_PLAN_STEREO_WAVEFORM.md)

### Feature Overview
Displays separate waveforms for left and right audio channels, allows independent channel muting, and provides per-channel analysis.

### Key Test Areas
- Stereo waveform display (stacked channels)
- Channel muting controls
- Mono file handling
- Playback with muted channels
- Annotation interaction with stereo view
- Performance considerations
- Settings persistence

**Status**: ✅ Production-ready

---

<a name="audiobrowserorig-8-sync-improvements"></a>
## AudioBrowserOrig 8: Sync Improvements

**Feature**: Enhanced cloud synchronization (Google Drive, Dropbox, etc.)  
**Test Cases**: 38  
**Full Test Plan**: [TEST_PLAN_SYNC_IMPROVEMENTS.md](AudioBrowserOrig/docs/test_plans/TEST_PLAN_SYNC_IMPROVEMENTS.md)

### Feature Overview
Improved cloud sync reliability, conflict resolution, multi-device support, and sync status indicators.

### Key Test Areas
- Google Drive integration
- Dropbox integration
- Conflict detection and resolution
- Sync status indicators
- Offline mode handling
- Multi-device scenarios
- Performance with large libraries
- Error handling and recovery

**Status**: ✅ Production-ready

---

<a name="audiobrowserorig-9-tempo-metronome"></a>
## AudioBrowserOrig 9: Tempo & Metronome

**Feature**: Tempo detection, marking, and built-in metronome  
**Test Cases**: 31  
**Full Test Plan**: [TEST_PLAN_TEMPO_METRONOME.md](AudioBrowserOrig/docs/test_plans/TEST_PLAN_TEMPO_METRONOME.md)

### Feature Overview
Automatic tempo detection, manual tempo marking on waveforms, integrated metronome with visual/audio feedback, and tempo-based practice features.

### Key Test Areas
- Tempo detection algorithms
- Tempo marker placement on waveforms
- Metronome functionality (click track)
- Tempo changes and transitions
- Visual tempo feedback
- Integration with practice features
- Export with tempo information

**Status**: ✅ Production-ready

---

<a name="audiobrowserorig-10-workspace-progress"></a>
## AudioBrowserOrig 10: Workspace Layouts & Status Bar Progress

**Feature**: Save/restore window layouts and enhanced progress indicators  
**Test Cases**: 24  
**Full Test Plan**: [TEST_PLAN_WORKSPACE_PROGRESS.md](AudioBrowserOrig/docs/test_plans/TEST_PLAN_WORKSPACE_PROGRESS.md)

### Feature Overview
Save and restore custom window layouts, enhanced status bar progress indicators with clickable elements, and workspace presets.

### Key Test Areas

#### Workspace Layouts (8 tests)
- Save window layout
- Restore layout (same session)
- Restore layout (new session)
- Reset to default layout
- Layout persistence after reset
- Keyboard shortcuts (Ctrl+Shift+L, Ctrl+Shift+R)
- Edge cases (minimum/maximum size)

#### Status Bar Progress Indicators (8 tests)
- Waveform progress display
- Fingerprint progress display
- Cancel operation
- Progress percentage accuracy
- Multiple concurrent operations
- Progress text clarity
- Animation smoothness
- Color coding (blue/green/red)

#### Integration Tests (4 tests)
- Workspace with progress indicators
- Now Playing Panel with layouts
- Practice Goals layout integration
- Setlist Builder layout integration

#### Regression Tests (2 tests)
- Existing features unaffected
- Settings persistence

#### Performance Tests (2 tests)
- Progress update performance
- Layout save/restore speed

**Status**: ✅ Production-ready

---

# Part B: AudioBrowser-QML Test Plans

---

<a name="audiobrowser-qml-11-spectrogram-overlay"></a>
## AudioBrowser-QML 11: Spectrogram Overlay Feature

**Feature**: QML-based spectrogram visualization overlay  
**Test Cases**: 26  
**Full Test Plan**: [TEST_PLAN_SPECTROGRAM.md](AudioBrowser-QML/docs/test_plans/TEST_PLAN_SPECTROGRAM.md)

### Feature Overview
Modern QML implementation of spectrogram overlay on waveforms with gradient color visualization and smooth integration with QML-based audio player.

### Test Categories

#### Basic Functionality (3 tests)
- **TC-1.1 Toggle On/Off**: Enable/disable spectrogram
- **TC-1.2 Initial Display**: Correct rendering on file load
- **TC-1.3 Persistence**: Setting persists across sessions

#### Spectrogram Computation (5 tests)
- **TC-2.1 FFT Processing**: Correct frequency analysis
- **TC-2.2 Time Resolution**: Appropriate window size
- **TC-2.3 Frequency Range**: 20Hz - 20kHz coverage
- **TC-2.4 Computation Performance**: < 2 seconds for 3-minute file
- **TC-2.5 Progress Indication**: Shows progress during computation

#### Color Gradient (3 tests)
- **TC-3.1 Color Mapping**: Blue (low) to red (high) intensity
- **TC-3.2 Dynamic Range**: Proper contrast
- **TC-3.3 Theme Compatibility**: Works in light/dark modes

#### Integration with Existing Features (5 tests)
- **TC-4.1 Playback Position**: Syncs with playback cursor
- **TC-4.2 Click-to-Seek**: Works with spectrogram visible
- **TC-4.3 Tempo Markers**: Visible over spectrogram
- **TC-4.4 Zoom Controls**: Spectrogram scales correctly
- **TC-4.5 Generate Waveform Button**: Regenerates both waveform and spectrogram

#### Edge Cases (5 tests)
- **TC-5.1 Very Short Files**: < 5 seconds
- **TC-5.2 Very Long Files**: > 30 minutes
- **TC-5.3 Mono Files**: Handles single channel
- **TC-5.4 High Sample Rates**: 96kHz audio
- **TC-5.5 Corrupted Audio**: Graceful failure

#### Performance (3 tests)
- **TC-6.1 Memory Usage**: Reasonable memory footprint
- **TC-6.2 Computation Time**: Benchmarks for various file sizes
- **TC-6.3 UI Responsiveness**: No freezing during computation

#### Regression (2 tests)
- **TC-7.1 Waveform Display**: Normal waveform still works
- **TC-7.2 Audio Playback**: Playback unaffected

**Test Execution Summary Template**:

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

**Status**: ✅ Production-ready

---

# Test Execution Resources

---

<a name="master-test-tracking-template"></a>
## Master Test Tracking Template

Use this template to track your testing progress across all features.

### Overall Progress Tracker

**Testing Session Information**:
- **Tester Name**: _________________
- **Test Start Date**: _________________
- **Test End Date**: _________________
- **AudioBrowser Version**: _________________
- **Operating System**: _________________
- **Python Version**: _________________
- **PyQt6 Version**: _________________

### Test Execution Summary by Application

#### AudioBrowserOrig Features

| Feature | Test Cases | Passed | Failed | Blocked | Pass % | Priority | Status |
|---------|-----------|--------|--------|---------|--------|----------|--------|
| 1. Clickable Status Bar | 23 | ___ | ___ | ___ | ___% | High | ☐ |
| 2. Now Playing Panel | 29 | ___ | ___ | ___ | ___% | High | ☐ |
| 3. Performance Improvements | 41 | ___ | ___ | ___ | ___% | Critical | ☐ |
| 4. Practice Goals | 40 | ___ | ___ | ___ | ___% | High | ☐ |
| 5. Setlist Builder | 43 | ___ | ___ | ___ | ___% | High | ☐ |
| 6. Spectral Analysis | 35 | ___ | ___ | ___ | ___% | Medium | ☐ |
| 7. Stereo Waveform | 15 | ___ | ___ | ___ | ___% | Medium | ☐ |
| 8. Sync Improvements | 38 | ___ | ___ | ___ | ___% | Medium | ☐ |
| 9. Tempo & Metronome | 31 | ___ | ___ | ___ | ___% | Medium | ☐ |
| 10. Workspace & Progress | 24 | ___ | ___ | ___ | ___% | Medium | ☐ |
| **AudioBrowserOrig Total** | **319** | ___ | ___ | ___ | ___% | - | ☐ |

#### AudioBrowser-QML Features

| Feature | Test Cases | Passed | Failed | Blocked | Pass % | Priority | Status |
|---------|-----------|--------|--------|---------|--------|----------|--------|
| 11. Spectrogram Overlay | 26 | ___ | ___ | ___ | ___% | High | ☐ |
| **AudioBrowser-QML Total** | **26** | ___ | ___ | ___ | ___% | - | ☐ |

#### Grand Total

| Application | Test Cases | Passed | Failed | Blocked | Pass % |
|------------|-----------|--------|--------|---------|--------|
| AudioBrowserOrig | 319 | ___ | ___ | ___ | ___% |
| AudioBrowser-QML | 26 | ___ | ___ | ___ | ___% |
| **GRAND TOTAL** | **345** | ___ | ___ | ___ | ___% |

### Testing Milestones

- [ ] **Milestone 1**: Critical features tested (Performance, Core UI)
- [ ] **Milestone 2**: High priority features tested (Goals, Setlist, Panel)
- [ ] **Milestone 3**: Medium priority features tested (Spectral, Stereo, Sync)
- [ ] **Milestone 4**: Integration and regression testing complete
- [ ] **Milestone 5**: Edge cases and error handling verified
- [ ] **Milestone 6**: Performance benchmarks completed
- [ ] **Milestone 7**: Cross-platform testing (if applicable)
- [ ] **Milestone 8**: All blockers resolved
- [ ] **Milestone 9**: Documentation updated
- [ ] **Milestone 10**: Ready for release

---

<a name="bug-reporting-template"></a>
## Bug Reporting Template

Use this template to report bugs found during testing.

### Bug Report #____

**Reporter**: _________________  
**Date Reported**: _________________  
**Application**: ☐ AudioBrowserOrig ☐ AudioBrowser-QML  
**Feature/Test Plan**: _________________  
**Test Case ID**: _________________

**Bug Title**: _______________________________________________

**Severity**:
- ☐ **Critical** - Application crashes, data loss, core feature broken
- ☐ **Major** - Feature doesn't work as expected, workaround difficult
- ☐ **Minor** - Small issue, workaround available
- ☐ **Cosmetic** - Visual/text issue, no functional impact

**Priority**:
- ☐ **Must Fix** - Blocks release
- ☐ **Should Fix** - Important for quality release
- ☐ **Nice to Fix** - Can defer to future release
- ☐ **Low Priority** - Minor improvement

**Environment Details**:
- OS: _________________
- OS Version: _________________
- Python Version: _________________
- PyQt6 Version: _________________
- AudioBrowser Version: _________________
- Display Resolution: _________________
- Test Data Size: _________________

**Steps to Reproduce**:
1. _________________
2. _________________
3. _________________
4. _________________

**Expected Result**:
_________________________________________________________________________________

**Actual Result**:
_________________________________________________________________________________

**Screenshots/Attachments**:
- [ ] Screenshot attached
- [ ] Log file attached
- [ ] Video recording attached
- [ ] Sample test data attached

**Console Output/Error Messages**:
```
[Paste console output or error messages here]
```

**Workaround (if any)**:
_________________________________________________________________________________

**Additional Notes**:
_________________________________________________________________________________

**Related Bugs**: #____, #____, #____

**Status**:
- ☐ New
- ☐ Confirmed
- ☐ In Progress
- ☐ Fixed (Pending Verification)
- ☐ Verified Fixed
- ☐ Closed
- ☐ Won't Fix
- ☐ Duplicate of #____

**Assigned To**: _________________  
**Target Release**: _________________

---

<a name="overall-test-summary"></a>
## Overall Test Summary

### Test Coverage Analysis

**Feature Coverage**:
- ✅ **UI/UX Features**: 23 + 29 + 43 + 24 = 119 test cases
- ✅ **Performance & Optimization**: 41 test cases
- ✅ **Practice & Goal Tracking**: 40 test cases
- ✅ **Audio Analysis & Visualization**: 35 + 15 + 26 = 76 test cases
- ✅ **Cloud Sync & Data**: 38 test cases
- ✅ **Musical Features**: 31 test cases
- ✅ **Integration & Regression**: ~40% of all test cases

**Test Type Distribution**:
- **Functional Tests**: ~250 cases (72%)
- **Integration Tests**: ~45 cases (13%)
- **Performance Tests**: ~20 cases (6%)
- **Edge Case/Error Tests**: ~30 cases (9%)

### Risk Assessment

**High Risk Areas** (require thorough testing):
1. **Performance Improvements** - Core functionality, affects all users
2. **Practice Goals** - Complex data tracking and calculations
3. **Setlist Builder** - Data persistence and export functionality
4. **Sync Improvements** - Multi-device data integrity

**Medium Risk Areas**:
1. **Spectral Analysis & Spectrogram** - Computation-intensive features
2. **Now Playing Panel** - Integration with existing playback
3. **Tempo & Metronome** - Audio timing accuracy

**Low Risk Areas**:
1. **Clickable Status Bar** - Simple UI enhancement
2. **Stereo Waveform** - Visualization only
3. **Workspace Layouts** - UI preference storage

### Critical Test Paths

**Path 1: First-Time User**
1. Install application
2. Open practice folder
3. Browse and play audio files
4. Add annotations
5. Mark best takes
6. Create simple setlist

**Path 2: Power User Workflow**
1. Open large library (1000+ files)
2. Verify performance
3. Set practice goals
4. Review practice statistics
5. Create performance setlist
6. Export setlist

**Path 3: Band Practice Session**
1. Open practice folder
2. Play and annotate in real-time
3. Use Now Playing Panel
4. Mark best takes
5. Add performance notes
6. Save and sync

### Test Data Requirements Summary

**Minimum Test Data**:
- Small folder: 10-20 files
- Practice session simulation: 5 dated folders
- Mixed content: WAV and MP3 files
- Various states: Some best takes, some annotated

**Recommended Test Data**:
- Small: 30 files (~150 MB)
- Medium: 200 files (~1 GB)
- Large: 1200 files (~6 GB)
- Multiple practice folders spanning 2-3 months
- Mix of mono and stereo files
- Various sample rates (44.1kHz, 48kHz)

**Comprehensive Test Data**:
- Everything in recommended, plus:
- Very large library: 5000+ files
- Edge cases: Corrupted files, very long files (>30 min)
- Special characters in filenames
- Cloud-synced folders (Google Drive, Dropbox)

### Pre-Testing Checklist

Before beginning testing, ensure:
- [ ] Test environment set up correctly
- [ ] All required software installed and updated
- [ ] Test data prepared and organized
- [ ] Test tracking spreadsheet/template ready
- [ ] Bug reporting system accessible
- [ ] Screen recording software available (for bug reproduction)
- [ ] Backup of test data created
- [ ] Clean install of application (or known good state)
- [ ] Previous test results reviewed (if applicable)

### Post-Testing Checklist

After completing testing:
- [ ] All test cases executed and results recorded
- [ ] All bugs reported and assigned severity/priority
- [ ] Critical and major bugs verified or documented
- [ ] Performance benchmarks recorded
- [ ] Test summary report created
- [ ] Screenshots/videos archived
- [ ] Test data preserved for regression testing
- [ ] Recommendations documented
- [ ] Sign-off obtained (if required)
- [ ] Test results archived

---

## Testing Best Practices

### General Testing Guidelines

1. **Test in Order**: Follow test case numbers for logical progression
2. **Document Everything**: Record all results, even passing tests
3. **Take Screenshots**: Visual evidence is crucial for bug reports
4. **Test Realistically**: Use real-world workflows, not just happy paths
5. **Be Thorough**: Don't skip "obvious" test cases
6. **Report Immediately**: File bugs as soon as found, don't wait
7. **Verify Fixes**: Re-test bugs after developers claim fixes
8. **Think Like a User**: Test from user perspective, not developer perspective

### Specific Testing Tips

**For Performance Tests**:
- Close other applications to avoid interference
- Run multiple times and average results
- Note system specs in all performance reports
- Test with both cold start and warm cache

**For Integration Tests**:
- Test feature interactions, not just individual features
- Verify data consistency across features
- Check for unexpected side effects

**For Edge Cases**:
- Try to break the application intentionally
- Test with invalid, unexpected, or extreme inputs
- Test error recovery paths

**For Regression Tests**:
- Always test existing features when new features are added
- Verify bug fixes don't introduce new bugs
- Check that settings and data persist correctly

### Common Issues to Watch For

- Memory leaks (increasing memory over time)
- UI freezing or lag (especially with large libraries)
- Data loss or corruption
- Inconsistent behavior across sessions
- Settings not persisting
- Keyboard shortcuts not working
- Error messages not helpful
- Progress indicators stuck or inaccurate

---

## Quick Start Guide for Testing

### 1-Hour Quick Test (Smoke Test)

Test the most critical functionality:
1. ☐ Application launches
2. ☐ Can open practice folder
3. ☐ Can play audio file
4. ☐ Can add annotation
5. ☐ Can mark best take
6. ☐ Performance acceptable with 100 files
7. ☐ No crashes in basic workflow

### 4-Hour Essential Test

Add medium-priority features:
1. ☐ All items from 1-hour test
2. ☐ Practice Goals creation and tracking
3. ☐ Setlist Builder basic functionality
4. ☐ Now Playing Panel workflow
5. ☐ Clickable status bar items
6. ☐ Workspace layout save/restore
7. ☐ Basic performance benchmarks

### Full Comprehensive Test (2-3 days)

Complete all 345 test cases following this plan.

---

## Conclusion

This collated test plan provides a comprehensive framework for thoroughly testing both AudioBrowser applications. The **345 test cases** cover all major features, edge cases, integration points, and performance considerations.

**Key Testing Priorities**:
1. **Critical**: Performance Improvements (41 tests) - Must pass for release
2. **High**: Practice Goals (40 tests), Setlist Builder (43 tests), Now Playing Panel (29 tests)
3. **Medium**: All analysis and visualization features
4. **Low**: UI refinements and optional features

**Estimated Testing Time**:
- Quick smoke test: 1 hour
- Essential features: 4 hours
- Complete comprehensive test: 16-24 hours (2-3 days)
- With bug reproduction and verification: Add 50% more time

Use the Master Test Tracking Template to monitor progress and the Bug Reporting Template to document issues. Good luck with testing!

---

**Document Information**:
- **Version**: 1.0
- **Date**: January 2025
- **Total Test Cases**: 345
- **Applications Covered**: AudioBrowserOrig, AudioBrowser-QML
- **Test Plans Collated**: 11

**For detailed test cases, refer to individual test plan documents**:
- AudioBrowserOrig: `AudioBrowserOrig/docs/test_plans/`
- AudioBrowser-QML: `AudioBrowser-QML/docs/test_plans/`
