# QML Migration Issues - Feature Parity Roadmap

This document contains issue templates for tracking the implementation of missing features in AudioBrowser-QML to achieve feature parity with AudioBrowserOrig.

Based on the comprehensive feature comparison in `FEATURE_COMPARISON_ORIG_VS_QML.md`, these issues are organized by priority and implementation phase.

---

## Issue 1: [HIGH PRIORITY] Implement Batch Operations

**Labels**: `enhancement`, `qml-migration`, `high-priority`, `phase-7`

### Overview
Implement batch file operations in AudioBrowser-QML to achieve feature parity with AudioBrowserOrig.

### Missing Features
- [ ] Batch rename (##_ProvidedName format)
- [ ] Convert WAV→MP3 (with option to delete originals)
- [ ] Convert stereo→mono
- [ ] Export with volume boost
- [ ] Mute channels during export
- [ ] Progress tracking for long operations

### Technical Details
- **Estimated Lines of Code**: ~1,500 lines
- **Complexity**: Medium (ffmpeg integration, threading)
- **Priority**: High (frequently used feature)
- **Phase**: Phase 7 (Week 2)
- **Estimated Effort**: 2 weeks

### Implementation Plan
1. Create `backend/batch_operations.py` module (~400 lines)
   - Batch rename engine with pattern matching
   - Batch convert engine
   - Progress tracking
   - Thread-based execution
2. Create QML dialogs
   - `qml/dialogs/BatchRenameDialog.qml` (~200 lines)
   - `qml/dialogs/BatchConvertDialog.qml` (~200 lines)
   - Progress dialog component
3. Add UI controls
   - Toolbar button for batch operations
   - Menu items in File menu
   - Results summary display
4. Testing
   - Test batch rename with various patterns
   - Test format conversions
   - Test error handling and rollback

### Dependencies
- ffmpeg (already used in original)
- PyQt6 QThread workers
- Integration with FileManager backend

### Reference
- FEATURE_COMPARISON_ORIG_VS_QML.md section 8
- AudioBrowserOrig lines ~7,500-9,000 (batch operations code)
- Phase 7 implementation plan

---

## Issue 2: [HIGH PRIORITY] Implement Best/Partial Take Indicators ✅ DONE

**Labels**: `enhancement`, `qml-migration`, `high-priority`, `phase-8`  
**Status**: ✅ COMPLETED  
**Completed Date**: 2025-01

### Overview
Add visual indicators for Best Take and Partial Take marking in the Library tab.

### Missing Features
- [x] Best Take indicator (gold star icon)
- [x] Partial Take indicator (half-filled star icon)
- [x] Context menu options to mark/unmark
- [x] Persistence in JSON metadata
- [x] Visual indicators in file list
- [x] Filter controls to show only Best/Partial takes

### Technical Details
- **Estimated Lines of Code**: ~500 lines
- **Actual Lines of Code**: ~737 lines (backend + QML components)
- **Complexity**: Low-Medium (UI components + persistence)
- **Priority**: High (important for practice workflow)
- **Phase**: Phase 8
- **Estimated Effort**: 1 week
- **Actual Effort**: 1 day

### Implementation Plan ✅
1. Extend backend ✅
   - Update `backend/file_manager.py` with best/partial take tracking ✅
   - Add JSON persistence for take status (`.takes_metadata.json`) ✅
2. Create QML components ✅
   - `qml/components/BestTakeIndicator.qml` (~133 lines) ✅
   - `qml/components/PartialTakeIndicator.qml` (~191 lines) ✅
3. Update Library tab ✅
   - Add indicator column to file list ✅
   - Add filter buttons to toolbar ✅
   - Update context menu with mark/unmark options ✅
4. Testing ✅
   - Test marking and unmarking ✅
   - Test persistence across sessions ✅
   - Test filter functionality ✅
   - Created comprehensive test suite (`test_take_indicators.py`) ✅

### Dependencies
- Extends FileManager and FileListModel
- Integration with LibraryTab

### Reference
- FEATURE_COMPARISON_ORIG_VS_QML.md section 3
- AudioBrowserOrig lines ~327-620 (indicator widgets)
- AudioBrowserOrig lines ~8,400-8,430 (context menu marking)

### Implementation Summary ✅

**Files Added:**
- `qml/components/BestTakeIndicator.qml` - Gold star indicator for best takes
- `qml/components/PartialTakeIndicator.qml` - Half-filled star indicator for partial takes
- `test_take_indicators.py` - Comprehensive test suite

**Files Modified:**
- `backend/file_manager.py` - Added take tracking methods and JSON persistence
- `backend/models.py` - Added `isBestTake` and `isPartialTake` roles to FileListModel
- `qml/tabs/LibraryTab.qml` - Added indicator column, filter buttons, and integration
- `qml/components/FileContextMenu.qml` - Added mark/unmark menu items

**Key Features:**
- Visual indicators with gold star (best) and half-filled star (partial)
- Click-to-toggle functionality directly on indicators
- Context menu options for marking/unmarking
- Persistence via `.takes_metadata.json` file in each directory
- Filter buttons to show only best or partial takes
- Full integration with existing file list and model system

**Testing:**
- All unit tests passing (FileManager, FileListModel integration)
- QML components verified
- Persistence and loading verified

---

## Issue 3: [MEDIUM-HIGH PRIORITY] Implement Practice Statistics ✅ DONE

**Labels**: `enhancement`, `qml-migration`, `medium-high-priority`, `phase-8`  
**Status**: ✅ COMPLETED  
**Completed Date**: 2025-01

### Overview
Implement practice statistics tracking and display to help users monitor their practice sessions.

### Missing Features
- [x] Track practice sessions (date, duration, songs practiced)
- [x] Display practice frequency per song
- [x] Display total practice time per song
- [x] Display session history
- [x] Practice Statistics dialog/tab
- [x] Folder-based session tracking (analyzes practice folders)
- [x] Manual session logging (not implemented - folder-based tracking used instead)

### Technical Details
- **Estimated Lines of Code**: ~1,500 lines
- **Actual Lines of Code**: ~710 lines (backend + QML components)
- **Complexity**: Medium-High (data tracking, analytics, UI)
- **Priority**: Medium-High (band practice feature)
- **Phase**: Phase 8
- **Estimated Effort**: 1.5 weeks
- **Actual Effort**: 1 day

### Implementation Plan ✅
1. Create backend module ✅
   - Created `backend/practice_statistics.py` (~600 lines)
   - Folder discovery and analysis
   - Analytics calculations (session stats, song frequency, practice consistency)
   - HTML formatting for display
2. Create QML dialog ✅
   - Created `qml/dialogs/PracticeStatisticsDialog.qml` (~150 lines)
   - HTML-based statistics display
   - Refresh button functionality
   - Non-modal dialog for continued work
3. Integration ✅
   - Added practiceStatistics manager to main.py
   - Exposed to QML context
   - Added "📊 Practice Stats" button in LibraryTab toolbar
   - Uses folder-based analysis (not file persistence)
4. Testing ✅
   - Created test_practice_statistics.py
   - Tests directory discovery, JSON loading, module structure
   - All tests passing

### Dependencies
- FileManager for root directory path
- Folder structure with audio files (.wav, .mp3)

### Reference
- FEATURE_COMPARISON_ORIG_VS_QML.md section 11
- AudioBrowserOrig practice statistics implementation
- Phase 8 implementation plan

### Implementation Summary ✅

**Files Created:**
- `backend/practice_statistics.py` - Backend manager with statistics generation and HTML formatting
- `qml/dialogs/PracticeStatisticsDialog.qml` - QML dialog for displaying statistics
- `test_practice_statistics.py` - Unit tests for backend functionality

**Files Modified:**
- `main.py` - Added practiceStatistics manager and exposed to QML
- `qml/main.qml` - Added PracticeStatisticsDialog declaration
- `qml/tabs/LibraryTab.qml` - Added Practice Stats button to toolbar

**Key Features:**
- Analyzes practice folders recursively to discover audio files
- Extracts dates from folder names (YYYY-MM-DD pattern) or modification times
- Tracks best take and partial take markers from metadata
- Generates statistics: total sessions, files, unique songs, date range, practice consistency
- Displays recent practice sessions with file counts and best takes
- Shows most/least practiced songs with frequency and last practiced date
- Refresh button to regenerate statistics on demand
- Non-modal dialog allows continued work while viewing stats

**Testing:**
- Backend functionality tested (directory discovery, JSON loading, module structure)
- All unit tests passing (3/3)
- Integration tested with QML dialog

---

## Issue 4: [MEDIUM-HIGH PRIORITY] Implement Practice Goals

**Labels**: `enhancement`, `qml-migration`, `medium-high-priority`, `phase-8`

### Overview
Implement practice goal setting and tracking to help users achieve practice targets.

### Missing Features
- [ ] Create practice goals (time-based, session-based, per-song)
- [ ] Track progress toward goals
- [ ] Display goal completion status
- [ ] Goal deadline tracking
- [ ] Practice Goals dialog
- [ ] Visual progress indicators
- [ ] Goal completion notifications

### Technical Details
- **Estimated Lines of Code**: ~1,500 lines
- **Complexity**: Medium-High (goal management, progress tracking)
- **Priority**: Medium-High (band practice feature)
- **Phase**: Phase 8
- **Estimated Effort**: 1.5 weeks

### Implementation Plan
1. Create backend module
   - Create `backend/practice_goals.py` (~600 lines)
   - Goal CRUD operations
   - Progress tracking
   - Data persistence to `.practice_goals.json`
2. Create QML dialog
   - `qml/dialogs/PracticeGoalsDialog.qml` (~500 lines)
   - Goal creation/editing UI
   - Progress visualization
3. Integration
   - Connect to practice statistics
   - Add menu item (Help > Practice Goals)
   - Display goal status in UI
4. Testing
   - Test goal creation and tracking
   - Test progress calculations
   - Test deadline notifications

### Dependencies
- Practice Statistics backend
- AudioEngine for session tracking

### Reference
- FEATURE_COMPARISON_ORIG_VS_QML.md section 11
- AudioBrowserOrig `.practice_goals.json` format
- Phase 8 implementation plan

---

## Issue 5: [MEDIUM-HIGH PRIORITY] Implement Setlist Builder

**Labels**: `enhancement`, `qml-migration`, `medium-high-priority`, `phase-9`

### Overview
Implement setlist builder for organizing and practicing performance material.

### Missing Features
- [ ] Create/edit/delete setlists
- [ ] Add songs from any folder to setlist
- [ ] Reorder songs in setlist
- [ ] Practice mode (play through setlist)
- [ ] Export setlist to text/PDF
- [ ] Setlist notes and metadata
- [ ] Validation (missing files warning)

### Technical Details
- **Estimated Lines of Code**: ~2,000 lines
- **Complexity**: High (complex UI, file references, practice mode)
- **Priority**: Medium-High (band practice feature)
- **Phase**: Phase 9
- **Estimated Effort**: 2 weeks

### Implementation Plan
1. Create backend module
   - Create `backend/setlist_manager.py` (~700 lines)
   - Setlist CRUD operations
   - File reference management
   - Practice mode logic
2. Create QML dialog
   - `qml/dialogs/SetlistBuilderDialog.qml` (~800 lines)
   - Three-tab interface (Manage, Practice, Export)
   - Drag-and-drop song ordering
3. Integration
   - Add menu item (Tools > Setlist Builder)
   - Practice mode highlights in file tree
   - Persist to `.setlists.json`
4. Testing
   - Test setlist management
   - Test practice mode
   - Test export functionality

### Dependencies
- FileManager for file references
- AudioEngine for practice mode playback

### Reference
- FEATURE_COMPARISON_ORIG_VS_QML.md section 11
- AudioBrowserOrig `.setlists.json` format
- VISUAL_GUIDE_SETLIST_BUILDER.md
- Phase 9 implementation plan

---

## Issue 6: [MEDIUM PRIORITY] Implement Tempo/BPM Features

**Labels**: `enhancement`, `qml-migration`, `medium-priority`, `phase-9`

### Overview
Implement tempo tracking and BPM features for timing analysis.

### Missing Features
- [ ] BPM/Tempo column in Library tab
- [ ] Tempo markers on waveform (measure lines)
- [ ] Manual tempo entry
- [ ] Automatic tempo detection (optional)
- [ ] Time signature support
- [ ] Tempo persistence in `.tempo.json`

### Technical Details
- **Estimated Lines of Code**: ~1,000 lines
- **Complexity**: Medium (waveform integration, tempo detection)
- **Priority**: Medium
- **Phase**: Phase 9
- **Estimated Effort**: 1.5 weeks

### Implementation Plan
1. Create backend module
   - Create `backend/tempo_manager.py` (~400 lines)
   - Tempo tracking and persistence
   - Optional: tempo detection algorithm
2. Update waveform display
   - Add tempo marker rendering to WaveformView
   - Calculate measure positions based on BPM
3. Update Library tab
   - Add BPM/Tempo column
   - Add tempo editing dialog
4. Testing
   - Test tempo entry and persistence
   - Test measure marker display
   - Test tempo detection (if implemented)

### Dependencies
- WaveformEngine and WaveformView
- FileManager for metadata

### Reference
- FEATURE_COMPARISON_ORIG_VS_QML.md sections 3, 5, 11
- AudioBrowserOrig `.tempo.json` format
- TEMPO_FEATURE_GUIDE.md
- Phase 9 implementation plan

---

## Issue 7: [MEDIUM PRIORITY] Implement Spectrogram Overlay

**Labels**: `enhancement`, `qml-migration`, `medium-priority`, `phase-9`

### Overview
Add spectrogram overlay visualization to waveform display for frequency analysis.

### Missing Features
- [ ] Spectrogram rendering (60-8000 Hz)
- [ ] Toggle spectrogram on/off
- [ ] Spectrogram opacity control
- [ ] Color gradient for frequency intensity
- [ ] Integration with zoom controls

### Technical Details
- **Estimated Lines of Code**: ~800 lines
- **Complexity**: Medium-High (FFT analysis, rendering)
- **Priority**: Medium (advanced visualization)
- **Phase**: Phase 9
- **Estimated Effort**: 1.5 weeks

### Implementation Plan
1. Extend WaveformEngine
   - Add FFT analysis for spectral data
   - Generate spectrogram data
   - Cache spectrogram for performance
2. Update WaveformView
   - Add spectrogram rendering layer
   - Implement color gradient mapping
   - Add opacity blending
3. Add UI controls
   - Toggle button in Annotations tab
   - Opacity slider (optional)
4. Testing
   - Test spectrogram accuracy
   - Test performance with large files
   - Test zoom and scroll integration

### Dependencies
- WaveformEngine and WaveformView
- NumPy for FFT (already used)

### Reference
- FEATURE_COMPARISON_ORIG_VS_QML.md section 5
- AudioBrowserOrig spectrogram implementation
- IMPLEMENTATION_SUMMARY_SPECTRAL_ANALYSIS.md
- Phase 9 implementation plan

---

## Issue 8: [MEDIUM PRIORITY] Implement Audio Fingerprinting

**Labels**: `enhancement`, `qml-migration`, `medium-priority`, `phase-10`

### Overview
Implement audio fingerprinting for song identification and duplicate detection.

### Missing Features
- [ ] Generate audio fingerprints (multiple algorithms)
- [ ] Match songs across folders
- [ ] Detect duplicates
- [ ] Auto-generate in background
- [ ] Fingerprints tab with search UI
- [ ] Cache fingerprints in `.audio_fingerprints.json`

### Technical Details
- **Estimated Lines of Code**: ~2,000 lines
- **Complexity**: High (FFT analysis, fingerprint algorithms)
- **Priority**: Medium (advanced feature)
- **Phase**: Phase 10
- **Estimated Effort**: 3 weeks

### Implementation Plan
1. Create backend module
   - Create `backend/fingerprint_engine.py` (~800 lines)
   - Implement multiple fingerprint algorithms
   - Background generation with threading
   - Cross-folder matching
2. Create Fingerprints tab
   - `qml/tabs/FingerprintsTab.qml` (~400 lines)
   - Search and match UI
   - Results table
3. Integration
   - Auto-generate on folder load
   - Progress tracking
   - Cache management
4. Testing
   - Test fingerprint accuracy
   - Test duplicate detection
   - Test cross-folder matching

### Dependencies
- NumPy for FFT analysis
- WaveformEngine for audio data
- Threading for background generation

### Reference
- FEATURE_COMPARISON_ORIG_VS_QML.md section 7
- AUDIO_FINGERPRINTING.md
- AudioBrowserOrig fingerprinting implementation
- Phase 10 implementation plan

---

## Issue 9: [LOW-MEDIUM PRIORITY] Implement Backup System

**Labels**: `enhancement`, `qml-migration`, `low-medium-priority`, `phase-10`

### Overview
Implement automatic backup and restore functionality for data safety.

### Missing Features
- [ ] Automatic backups before modifications
- [ ] Timestamped backup folders (`.backup/YYYY-MM-DD-###/`)
- [ ] Restore from backup dialog
- [ ] Preview before restoring
- [ ] Backup cleanup (old backups)

### Technical Details
- **Estimated Lines of Code**: ~800 lines
- **Complexity**: Medium (file operations, dialog UI)
- **Priority**: Low-Medium (safety feature)
- **Phase**: Phase 10
- **Estimated Effort**: 1 week

### Implementation Plan
1. Create backend module
   - Create `backend/backup_manager.py` (~400 lines)
   - Automatic backup triggering
   - Backup creation and restoration
   - Cleanup old backups
2. Create restore dialog
   - `qml/dialogs/BackupSelectionDialog.qml` (~200 lines)
   - List available backups
   - Preview backup contents
3. Integration
   - Trigger backups before batch operations
   - Add menu item (File > Restore from Backup)
4. Testing
   - Test backup creation
   - Test restoration
   - Test error handling

### Dependencies
- FileManager for file operations
- QSettings for backup preferences

### Reference
- FEATURE_COMPARISON_ORIG_VS_QML.md section 9
- AudioBrowserOrig backup implementation
- Phase 10 implementation plan

---

## Issue 10: [LOW-MEDIUM PRIORITY] Implement Workspace Layouts

**Labels**: `enhancement`, `qml-migration`, `low-medium-priority`, `phase-10`

### Overview
Add workspace layout save/restore for window size and panel positions.

### Missing Features
- [ ] Save window geometry and state
- [ ] Save splitter positions
- [ ] Restore saved layout
- [ ] Reset to default layout
- [ ] Multiple named layouts (optional)

### Technical Details
- **Estimated Lines of Code**: ~400 lines
- **Complexity**: Low-Medium (QML state management)
- **Priority**: Low-Medium (power user feature)
- **Phase**: Phase 10
- **Estimated Effort**: 3 days

### Implementation Plan
1. Extend SettingsManager
   - Add layout persistence methods
   - Store window geometry, state, splitter positions
2. Add QML controls
   - Save/Restore layout menu items
   - Reset to default option
3. Integration
   - Auto-save layout on close
   - Auto-restore on launch (optional)
4. Testing
   - Test save and restore
   - Test across different screen sizes

### Dependencies
- SettingsManager backend
- QML Window and SplitView properties

### Reference
- FEATURE_COMPARISON_ORIG_VS_QML.md section 12
- AudioBrowserOrig workspace implementation
- Phase 10 implementation plan

---

## Issue 11: [LOW-MEDIUM PRIORITY] Implement Recent Folders Menu

**Labels**: `enhancement`, `qml-migration`, `low-medium-priority`, `phase-8`

### Overview
Add recent folders menu for quick folder switching.

### Missing Features
- [ ] Track recently opened folders (up to 10)
- [ ] Display in File menu
- [ ] Click to switch folders
- [ ] Clear recent folders option
- [ ] Persistence across sessions

### Technical Details
- **Estimated Lines of Code**: ~300 lines
- **Complexity**: Low (QSettings persistence, menu UI)
- **Priority**: Low-Medium (convenience feature)
- **Phase**: Phase 8
- **Estimated Effort**: 2 days

### Implementation Plan
1. Extend SettingsManager
   - Add recent folders tracking
   - Limit to 10 most recent
2. Update File menu
   - Add Recent Folders submenu
   - Populate with recent paths
   - Add clear option
3. Integration
   - Update on folder change
   - Connect to FileManager
4. Testing
   - Test folder tracking
   - Test menu population
   - Test persistence

### Dependencies
- SettingsManager backend
- FileManager for folder changes

### Reference
- FEATURE_COMPARISON_ORIG_VS_QML.md sections 2, 12
- AudioBrowserOrig recent folders implementation
- Phase 8 implementation plan

---

## Issue 12: [LOW-MEDIUM PRIORITY] Add Missing Keyboard Shortcuts

**Labels**: `enhancement`, `qml-migration`, `low-medium-priority`, `phase-8`

### Overview
Implement remaining keyboard shortcuts from original version.

### Missing Shortcuts
- [ ] Ctrl+Z - Undo (requires undo system)
- [ ] Ctrl+Y - Redo (requires undo system)
- [ ] Ctrl+Shift+L - Save workspace layout
- [ ] Ctrl+Shift+R - Restore workspace layout
- [ ] Ctrl+Shift+T - Setlist builder
- [ ] Ctrl+Shift+S - Practice statistics
- [ ] Ctrl+Shift+G - Practice goals
- [ ] Ctrl+Shift+H - Documentation browser
- [ ] Ctrl+H - Keyboard shortcuts help
- [ ] Additional navigation shortcuts

### Technical Details
- **Estimated Lines of Code**: ~200 lines
- **Complexity**: Low (shortcut registration)
- **Priority**: Low-Medium (power user feature)
- **Phase**: Phase 8
- **Estimated Effort**: 2 days

### Implementation Plan
1. Update main.qml
   - Add missing shortcut definitions
   - Connect to backend actions
2. Create shortcuts help dialog
   - `qml/dialogs/KeyboardShortcutsDialog.qml`
   - Display all shortcuts
3. Documentation
   - Update KEYBOARD_SHORTCUTS.md
4. Testing
   - Test all shortcuts
   - Test conflict resolution

### Dependencies
- Various backend managers
- Dialog implementations

### Reference
- FEATURE_COMPARISON_ORIG_VS_QML.md section 12
- AudioBrowserOrig keyboard shortcuts
- KEYBOARD_SHORTCUTS.md

---

## Issue 13: [LOW PRIORITY] Implement Google Drive Sync

**Labels**: `enhancement`, `qml-migration`, `low-priority`, `phase-11`

### Overview
Implement Google Drive synchronization for cloud backup and multi-user collaboration.

### Missing Features
- [ ] OAuth authentication
- [ ] Upload/download audio files
- [ ] Upload/download metadata
- [ ] Version tracking
- [ ] Conflict resolution
- [ ] Sync history viewer
- [ ] Sync rules configuration
- [ ] Multi-user annotation sync

### Technical Details
- **Estimated Lines of Code**: ~3,000 lines
- **Complexity**: Very High (OAuth, API integration, conflict resolution)
- **Priority**: Low (optional feature)
- **Phase**: Phase 11
- **Estimated Effort**: 4+ weeks

### Implementation Plan
1. Port gdrive_sync.py
   - Adapt existing gdrive_sync.py module
   - Update for QML integration
2. Create sync dialogs
   - `qml/dialogs/SyncDialog.qml`
   - `qml/dialogs/ConflictResolutionDialog.qml`
   - `qml/dialogs/SyncHistoryDialog.qml`
   - `qml/dialogs/SyncRulesDialog.qml`
3. Integration
   - Add sync button to toolbar
   - Add sync menu items
   - Background sync capability
4. Testing
   - Test OAuth flow
   - Test upload/download
   - Test conflict resolution
   - Test multi-user sync

### Dependencies
- Google Drive API credentials
- OAuth libraries
- Network connectivity

### Reference
- FEATURE_COMPARISON_ORIG_VS_QML.md section 10
- AudioBrowserOrig/gdrive_sync.py
- GOOGLE_DRIVE_SETUP.md
- SYNC_README.md
- Phase 11 implementation plan

---

## Issue 14: [LOW PRIORITY] Implement Export Annotations

**Labels**: `enhancement`, `qml-migration`, `low-priority`, `phase-8`

### Overview
Add annotation export functionality to save annotations as text files.

### Missing Features
- [ ] Export all annotations to text file
- [ ] Export filtered annotations
- [ ] Choose export format (plain text, CSV, Markdown)
- [ ] Include timestamp, text, category, user
- [ ] Export folder notes

### Technical Details
- **Estimated Lines of Code**: ~300 lines
- **Complexity**: Low (text formatting, file I/O)
- **Priority**: Low (occasional use)
- **Phase**: Phase 8
- **Estimated Effort**: 2 days

### Implementation Plan
1. Extend AnnotationManager
   - Add export methods
   - Support multiple formats
2. Create export dialog
   - `qml/dialogs/ExportAnnotationsDialog.qml`
   - Format selection
   - Filter options
3. Integration
   - Add menu item (File > Export Annotations)
   - Add button in Annotations tab
4. Testing
   - Test export formats
   - Test filtering
   - Test file creation

### Dependencies
- AnnotationManager backend

### Reference
- FEATURE_COMPARISON_ORIG_VS_QML.md section 4
- AudioBrowserOrig export implementation

---

## Issue 15: [LOW PRIORITY] Implement Documentation Browser

**Labels**: `enhancement`, `qml-migration`, `low-priority`, `phase-11`

### Overview
Add in-app documentation browser for viewing markdown docs.

### Missing Features
- [ ] Browse documentation files
- [ ] Search documentation
- [ ] Markdown rendering
- [ ] Category organization
- [ ] Navigate between docs

### Technical Details
- **Estimated Lines of Code**: ~600 lines
- **Complexity**: Medium (markdown rendering, navigation)
- **Priority**: Low (users can read docs externally)
- **Phase**: Phase 11
- **Estimated Effort**: 1 week

### Implementation Plan
1. Create documentation browser
   - `qml/dialogs/DocumentationBrowserDialog.qml`
   - Markdown rendering (Qt TextArea or WebView)
   - Navigation tree
   - Search functionality
2. Integration
   - Add menu item (Help > Documentation Browser)
   - Keyboard shortcut (Ctrl+Shift+H)
3. Testing
   - Test markdown rendering
   - Test navigation
   - Test search

### Dependencies
- Qt markdown rendering (TextArea or QtWebView)
- Access to docs/ folder

### Reference
- FEATURE_COMPARISON_ORIG_VS_QML.md section 12
- AudioBrowserOrig documentation browser
- docs/INDEX.md

---

## Issue 16: [LOW PRIORITY] Implement Now Playing Panel

**Labels**: `enhancement`, `qml-migration`, `low-priority`, `future`

### Overview
Add persistent Now Playing panel with compact controls and mini-waveform.

### Missing Features
- [ ] Compact playback controls
- [ ] Mini-waveform display
- [ ] Current file display
- [ ] Quick annotation entry
- [ ] Collapsible with toggle button
- [ ] State persistence

### Technical Details
- **Estimated Lines of Code**: ~500 lines
- **Complexity**: Medium (layout, waveform rendering)
- **Priority**: Low (main controls sufficient)
- **Phase**: Future (post Phase 11)
- **Estimated Effort**: 1 week

### Implementation Plan
1. Create Now Playing panel
   - `qml/components/NowPlayingPanel.qml` (~300 lines)
   - Mini-waveform widget
   - Compact controls
2. Integration
   - Add to main.qml layout
   - Toggle button
   - Persist state
3. Testing
   - Test all controls
   - Test persistence
   - Test layout responsiveness

### Dependencies
- AudioEngine
- WaveformEngine
- SettingsManager

### Reference
- FEATURE_COMPARISON_ORIG_VS_QML.md sections 12, "Features Removed for Simplification"
- AudioBrowserOrig NowPlayingPanel class

---

## Issue 17: [LOW PRIORITY] Implement Undo/Redo System

**Labels**: `enhancement`, `qml-migration`, `low-priority`, `future`

### Overview
Implement undo/redo functionality for file operations and annotations.

### Missing Features
- [ ] Undo/Redo for annotations (add, edit, delete)
- [ ] Undo/Redo for provided name changes
- [ ] Undo/Redo for batch operations
- [ ] Undo/Redo for take marking
- [ ] Configurable undo limit
- [ ] Toolbar buttons and keyboard shortcuts

### Technical Details
- **Estimated Lines of Code**: ~1,000 lines
- **Complexity**: High (command pattern, state management)
- **Priority**: Low (not critical for initial release)
- **Phase**: Future (post Phase 11)
- **Estimated Effort**: 2 weeks

### Implementation Plan
1. Create undo system
   - Create `backend/undo_manager.py`
   - Implement command pattern
   - Support multiple command types
2. Integration
   - Connect to all modifying operations
   - Add toolbar buttons
   - Add keyboard shortcuts (Ctrl+Z, Ctrl+Y)
3. Testing
   - Test undo/redo for each operation type
   - Test undo limit
   - Test state consistency

### Dependencies
- All backend managers that perform modifications
- SettingsManager for undo limit

### Reference
- FEATURE_COMPARISON_ORIG_VS_QML.md sections 12, 14, "Features Removed for Simplification"
- AudioBrowserOrig undo/redo implementation

---

## Issue 18: [LOW PRIORITY] Enhanced Preferences Dialog

**Labels**: `enhancement`, `qml-migration`, `low-priority`, `phase-8`

### Overview
Expand preferences dialog with all settings from original version.

### Missing Preferences
- [ ] Undo limit (10-1000)
- [ ] Parallel workers (0-16)
- [ ] Auto-waveform generation toggle
- [ ] Auto-fingerprint generation toggle
- [ ] Pagination settings (if implemented)
- [ ] Default zoom level
- [ ] Waveform rendering quality

### Technical Details
- **Estimated Lines of Code**: ~200 lines
- **Complexity**: Low (UI and settings integration)
- **Priority**: Low (basic settings work)
- **Phase**: Phase 8
- **Estimated Effort**: 2 days

### Implementation Plan
1. Expand PreferencesDialog
   - Add missing setting controls
   - Organize into tabs/sections
2. Update SettingsManager
   - Add new settings persistence
3. Integration
   - Connect settings to backend behavior
4. Testing
   - Test all settings
   - Test persistence
   - Test defaults

### Dependencies
- SettingsManager backend

### Reference
- FEATURE_COMPARISON_ORIG_VS_QML.md section 12
- AudioBrowserOrig PreferencesDialog class

---

## Issue 19: [LOW PRIORITY] Implement Export Best Takes Package

**Labels**: `enhancement`, `qml-migration`, `low-priority`, `phase-10`

### Overview
Add feature to export all Best Take files as a package.

### Missing Features
- [ ] Select all files marked as Best Take
- [ ] Export to ZIP or folder
- [ ] Include metadata
- [ ] Optional format conversion
- [ ] Progress tracking

### Technical Details
- **Estimated Lines of Code**: ~400 lines
- **Complexity**: Low-Medium (file operations, ZIP)
- **Priority**: Low (occasional use)
- **Phase**: Phase 10
- **Estimated Effort**: 3 days

### Implementation Plan
1. Create export functionality
   - Add method to FileManager
   - ZIP creation or folder copy
2. Create export dialog
   - `qml/dialogs/ExportBestTakesDialog.qml`
   - Destination selection
   - Format options
3. Integration
   - Add menu item (File > Export Best Takes Package)
   - Requires Best Take indicators
4. Testing
   - Test package creation
   - Test format conversion
   - Test error handling

### Dependencies
- FileManager backend
- Best Take indicators (Issue #2)

### Reference
- FEATURE_COMPARISON_ORIG_VS_QML.md sections 12, 13
- HOWTO_NEW_FEATURES.md (Export Best Takes section)

---

## Priority Summary

### High Priority (Phase 7-8) - 2 issues (1 completed)
1. Issue #1: Batch Operations (2 weeks)
2. ✅ Issue #2: Best/Partial Take Indicators (COMPLETED)

### Medium-High Priority (Phase 8) - 3 issues
3. Issue #3: Practice Statistics (1.5 weeks)
4. Issue #4: Practice Goals (1.5 weeks)
5. Issue #5: Setlist Builder (2 weeks) - Phase 9

### Medium Priority (Phase 9-10) - 3 issues
6. Issue #6: Tempo/BPM Features (1.5 weeks)
7. Issue #7: Spectrogram Overlay (1.5 weeks)
8. Issue #8: Audio Fingerprinting (3 weeks)

### Low-Medium Priority (Phase 8-10) - 4 issues
9. Issue #9: Backup System (1 week)
10. Issue #10: Workspace Layouts (3 days)
11. Issue #11: Recent Folders Menu (2 days)
12. Issue #12: Missing Keyboard Shortcuts (2 days)

### Low Priority (Phase 8-11+) - 7 issues
13. Issue #13: Google Drive Sync (4+ weeks)
14. Issue #14: Export Annotations (2 days)
15. Issue #15: Documentation Browser (1 week)
16. Issue #16: Now Playing Panel (1 week)
17. Issue #17: Undo/Redo System (2 weeks)
18. Issue #18: Enhanced Preferences Dialog (2 days)
19. Issue #19: Export Best Takes Package (3 days)

### Total Estimated Effort
- High Priority: 3 weeks
- Medium-High Priority: 7 weeks
- Medium Priority: 9 weeks
- Low-Medium Priority: 2.5 weeks
- Low Priority: 8+ weeks
- **Total: ~30 weeks (7.5 months) for full feature parity**

---

## Creating the Issues

To create these issues in GitHub:

1. **Using GitHub CLI** (if available):
   ```bash
   # For each issue, run:
   gh issue create --title "[TITLE]" --label "[LABELS]" --body "[BODY]"
   ```

2. **Using GitHub Web UI**:
   - Go to https://github.com/TheMikaus/BandTools/issues/new
   - Copy the title and body from each issue above
   - Add the specified labels
   - Submit

3. **Batch Creation**:
   - Use the GitHub API or automation tools
   - See GitHub documentation for batch issue creation

---

## Tracking Progress

Consider creating a GitHub Project board to track these issues:

1. Create project: "QML Migration - Feature Parity"
2. Add columns: Backlog, In Progress, Review, Done
3. Add all issues to the board
4. Track progress by phase

Alternatively, use milestones:
- Milestone: Phase 7 (Batch Operations, etc.)
- Milestone: Phase 8 (Practice Features, etc.)
- Milestone: Phase 9 (Advanced Features)
- Milestone: Phase 10 (Fingerprinting, Backup)
- Milestone: Phase 11 (Cloud Sync)

---

**Document Version**: 1.0  
**Generated**: January 2025  
**Based on**: FEATURE_COMPARISON_ORIG_VS_QML.md
