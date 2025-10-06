# Phase 7 QML Migration - Additional Features Plan

## Overview

**Status**: 🚧 **IN PROGRESS**  
**Date**: December 2024  
**Focus**: Additional features and functionality to approach feature parity with original audio_browser.py

Phase 7 builds on the completed Phases 1-6 by adding important features that were present in the original PyQt6 Widgets application but not yet implemented in the QML version.

---

## Current Status Summary

### Completed Phases

| Phase | Status | Features |
|-------|--------|----------|
| Phase 0 | ✅ Complete | Project setup and infrastructure |
| Phase 1 | ✅ Complete | Core infrastructure, backend modules, basic UI |
| Phase 2 | ✅ Complete | Waveform display with zoom and interaction |
| Phase 3 | ✅ Complete | Annotation system with markers |
| Phase 5 | ✅ Complete | Clips system with export |
| Phase 6 | ✅ 85% Complete | Keyboard shortcuts and polish |

**Note**: Phase 4 was skipped in favor of implementing clips (Phase 5) first.

### What's Working Now

- ✅ Audio file browsing and playback
- ✅ Waveform visualization with zoom
- ✅ Annotation creation, editing, deletion with visual markers
- ✅ Clip creation, editing, export with visual boundaries
- ✅ Keyboard shortcuts (playback, navigation, annotations, clips)
- ✅ Theme switching (dark/light)
- ✅ File filtering and search
- ✅ Volume control and seeking

---

## Phase 7 Objectives

Implement additional features to improve usability and approach feature parity with the original application.

### Priority 1: Essential Features (Week 1)

1. **Folder Notes Tab**
   - Add a dedicated tab for folder-level notes
   - Persistent notes per audio directory
   - Rich text editing support
   - Auto-save on changes

2. **File Context Menus**
   - Right-click context menu on files in Library tab
   - Quick actions: Play, Add Annotation, Create Clip, Show in Explorer
   - Copy file path to clipboard
   - File properties display

3. **Enhanced File List**
   - Show file duration in file list
   - Show file size in file list
   - Sortable columns (name, duration, size, date)
   - Multi-selection support

### Priority 2: Batch Operations (Week 2)

4. **Batch Operations Backend**
   - Create `backend/batch_operations.py` module
   - Batch rename files (with pattern support)
   - Batch convert audio formats (WAV ↔ MP3)
   - Progress tracking for long operations
   - Error handling and rollback support

5. **Batch Operations UI**
   - Add "Batch Operations" toolbar button
   - Batch rename dialog with preview
   - Batch convert dialog with format selection
   - Progress dialog for operations
   - Results summary after completion

### Priority 3: Enhancements (Week 3)

6. **Practice Statistics**
   - Display practice session statistics
   - Show time spent per song/folder
   - Track annotation activity
   - Simple statistics panel in status bar or dedicated view

7. **File Metadata Display**
   - Show extended file information
   - Audio format, sample rate, bitrate
   - File creation/modification dates
   - Provided name (custom song name) display and editing

8. **Additional Shortcuts**
   - Delete file (with confirmation)
   - Rename file (quick rename dialog)
   - Open file location in system file manager
   - Copy file to clipboard

### Priority 4: Polish and Testing (Week 4)

9. **UI Improvements**
   - Add more tooltips throughout interface
   - Improve loading indicators
   - Better error messages with user guidance
   - Confirmation dialogs for destructive actions

10. **Documentation and Testing**
    - Create PHASE_7_SUMMARY.md with implementation details
    - Update KEYBOARD_SHORTCUTS.md with new shortcuts
    - Update README.md with Phase 7 features
    - Manual testing of all new features
    - Update TESTING_GUIDE.md

---

## Implementation Plan

### Week 1: Folder Notes + Context Menus

#### Day 1-2: Folder Notes Backend
- Create `backend/folder_notes_manager.py`
- JSON-based persistence per folder
- CRUD operations for notes
- Auto-save functionality
- Expose to QML via context property

#### Day 3-4: Folder Notes UI
- Create `qml/tabs/FolderNotesTab.qml`
- TextArea for note editing
- Auto-save indicator
- Theme-aware styling
- Add tab to main.qml

#### Day 5: File Context Menus
- Add right-click detection to LibraryTab file list
- Create `qml/components/FileContextMenu.qml`
- Implement menu actions
- Connect to existing functionality (play, annotate, etc.)
- Add "Show in Explorer" functionality

### Week 2: Batch Operations

#### Day 6-8: Batch Operations Backend
- Create `backend/batch_operations.py`
- Implement batch rename with pattern support
- Implement batch convert (WAV ↔ MP3)
- Add progress tracking signals
- Error handling and validation
- Thread-based execution for long operations

#### Day 9-10: Batch Operations UI
- Create `qml/dialogs/BatchRenameDialog.qml`
- Create `qml/dialogs/BatchConvertDialog.qml`
- Add progress dialog component
- Add toolbar button for batch operations
- Add results summary display

### Week 3: Enhancements

#### Day 11-13: File Metadata
- Extend FileManager with metadata extraction
- Add metadata display to LibraryTab
- Implement provided name editing
- Add sortable columns to file list
- Show duration, size, format in list

#### Day 14-15: Practice Statistics
- Create basic statistics tracking
- Display session duration
- Show annotation count
- Add simple statistics panel
- Consider dedicated statistics view

### Week 4: Polish and Documentation

#### Day 16-18: Polish
- Add missing tooltips
- Improve loading indicators
- Better error messages
- Add confirmation dialogs
- UI/UX refinements

#### Day 19-20: Documentation
- Write PHASE_7_SUMMARY.md
- Update README.md
- Update KEYBOARD_SHORTCUTS.md
- Update TESTING_GUIDE.md
- Manual testing of all features
- Bug fixes

---

## Technical Considerations

### Backend Modules to Create

1. **FolderNotesManager** (~200 lines)
   - JSON persistence per folder
   - CRUD operations
   - Auto-save support
   - Signal emissions for UI updates

2. **BatchOperations** (~400 lines)
   - Batch rename engine
   - Batch convert engine
   - Pattern matching and validation
   - Progress tracking
   - Thread-based execution

### QML Components to Create

1. **FolderNotesTab.qml** (~150 lines)
   - TextArea for notes
   - Auto-save indicator
   - Theme styling

2. **FileContextMenu.qml** (~100 lines)
   - Menu items for file actions
   - Icon support
   - Keyboard shortcuts display

3. **BatchRenameDialog.qml** (~250 lines)
   - Pattern input
   - File list preview
   - Rename preview
   - Validation feedback

4. **BatchConvertDialog.qml** (~200 lines)
   - Format selection
   - Quality settings
   - File list selection
   - Progress display

5. **ProgressDialog.qml** (~150 lines)
   - Progress bar
   - Status text
   - Cancel button
   - Results summary

---

## Success Criteria

Phase 7 will be considered complete when:

- ✅ Folder Notes tab is functional with persistence
- ✅ File context menus work with all actions
- ✅ Batch rename and convert operations are working
- ✅ File metadata is displayed correctly
- ✅ All new features are documented
- ✅ Manual testing is complete
- ✅ No critical bugs remain
- ✅ Code quality is maintained (type hints, docstrings)

---

## Out of Scope for Phase 7

The following features are planned for future phases:

- **Phase 8**: Audio Fingerprinting
  - Fingerprint generation
  - Cross-folder matching
  - Automatic song identification

- **Phase 9**: Advanced Features
  - Practice Goals system
  - Setlist Builder
  - Google Drive sync
  - Best Take indicators
  - Partial Take indicators

- **Phase 10**: Feature Parity
  - Remaining features from original audio_browser.py
  - Advanced audio processing
  - Backup and restore functionality
  - Multi-user collaboration features

---

## Estimated Effort

| Item | Estimated Time |
|------|----------------|
| Folder Notes | 2 days |
| Context Menus | 1 day |
| Batch Operations Backend | 3 days |
| Batch Operations UI | 2 days |
| File Metadata | 3 days |
| Practice Statistics | 2 days |
| Polish and Testing | 3 days |
| Documentation | 2 days |
| **Total** | **~18 days** |

**Calendar Time**: 4 weeks with testing and iteration

---

## Dependencies

- PyQt6 >= 6.5.0
- All Phase 1-6 features working
- Existing backend modules (AudioEngine, FileManager, etc.)
- Existing QML components

---

## Risk Assessment

### Low Risk
- Folder Notes tab (straightforward implementation)
- File context menus (standard QML feature)
- File metadata display (FileManager extension)

### Medium Risk
- Batch operations (requires careful testing for data safety)
- Batch rename patterns (need good validation)
- Multi-file operations (need progress tracking)

### Mitigation Strategies
1. Implement extensive validation before file operations
2. Add preview functionality for batch operations
3. Implement rollback for failed operations
4. Comprehensive testing with test files
5. Clear error messages and user guidance

---

## Next Steps

1. Create FolderNotesManager backend module
2. Create FolderNotesTab QML component
3. Integrate into main.py and main.qml
4. Test folder notes functionality
5. Move to context menus implementation
6. Continue with batch operations

---

**Document Status**: 📋 Planning Complete  
**Last Updated**: December 2024  
**Next Milestone**: Begin Phase 7 implementation

---

*AudioBrowser QML - Phase 7 Implementation Plan*
