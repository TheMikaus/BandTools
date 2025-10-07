# Repository Reorganization

## Overview

This document describes the repository structure reorganization completed in December 2024 to better organize the two versions of AudioBrowser and their documentation.

## Goals

1. Clearly separate the original AudioBrowser from the QML version
2. Organize documentation for better discoverability
3. Maintain all existing documentation and code
4. Make the repository structure more maintainable

## Changes Made

### 1. Created AudioBrowserOrig Folder

All files for the original PyQt6 widgets-based AudioBrowser were moved to a dedicated folder:

```
AudioBrowserAndAnnotation/
└── AudioBrowserOrig/          (NEW)
    ├── README_ORIG.md         (NEW - explains this version)
    ├── audio_browser.py       (MOVED)
    ├── version.py             (MOVED)
    ├── audio_browser.spec     (MOVED)
    ├── build_exe.sh           (MOVED)
    ├── build_exe.bat          (MOVED)
    ├── make_icon.py           (MOVED)
    ├── app_icon.png           (MOVED)
    ├── app_icon.ico           (MOVED)
    ├── gdrive_sync.py         (MOVED)
    ├── sync_dialog.py         (MOVED)
    ├── credentials.json.example (MOVED)
    └── docs/                  (MOVED - entire folder)
        ├── INDEX.md
        ├── DOCUMENTATION_ORGANIZATION.md
        ├── user_guides/       (16 files)
        ├── technical/         (18 files)
        └── test_plans/        (6 files)
```

### 2. Organized AudioBrowser-QML Documentation

Created a structured documentation hierarchy for the QML version:

```
AudioBrowserAndAnnotation/
└── AudioBrowser-QML/
    ├── README.md              (UNCHANGED - stays in root)
    └── docs/                  (NEW)
        ├── INDEX.md           (NEW - documentation index)
        ├── user_guides/       (NEW - 4 files)
        │   ├── ANNOTATION_GUIDE.md
        │   ├── KEYBOARD_SHORTCUTS.md
        │   ├── QUICK_START.md
        │   └── WAVEFORM_GUIDE.md
        ├── technical/         (NEW - 11 files)
        │   ├── DEVELOPER_GUIDE.md
        │   ├── PROJECT_STRUCTURE.md
        │   ├── TESTING_GUIDE.md
        │   ├── IMPLEMENTATION_SUMMARY.md
        │   ├── BINDING_LOOP_FIXES.md
        │   ├── FIX_SUMMARY.md
        │   ├── FOLDER_SELECTION_FIX.md
        │   ├── QML_CONTROLS_BASIC_FIX.md
        │   ├── SESSION_ENHANCED_FILE_LIST.md
        │   ├── SESSION_SUMMARY.md
        │   └── VERIFICATION_SUMMARY.md
        └── phase_reports/     (NEW - 13 files)
            ├── PHASE_1_COMPLETION_REPORT.md
            ├── PHASE_1_SUMMARY.md
            ├── PHASE_2_COMPLETE.md
            ├── PHASE_2_SUMMARY.md
            ├── PHASE_3_COMPLETE.md
            ├── PHASE_5_CLIPS_SUMMARY.md
            ├── PHASE_5_TESTING_RESULTS.md
            ├── PHASE_6_KEYBOARD_SHORTCUTS_IMPLEMENTATION.md
            ├── PHASE_6_PROGRESS.md
            ├── PHASE_6_SUMMARY.md
            ├── PHASE_7_PLAN.md
            ├── PHASE_7_SESSION_COMPLETE.md
            └── PHASE_7_SUMMARY.md
```

### 3. Updated Documentation References

Updated the main `README.md` to reflect the new structure:
- Changed all documentation links to point to `AudioBrowserOrig/docs/`
- Added section explaining the two versions
- Maintained all existing content

## Benefits

### Better Organization
- Clear separation between original and QML versions
- Each version has its own self-contained folder
- Documentation is organized by type (user guides, technical, test plans, phase reports)

### Improved Discoverability
- New users can easily find the stable version (AudioBrowserOrig)
- Developers can find QML development documentation quickly
- Index files provide quick navigation to relevant docs

### Maintainability
- Changes to one version don't affect the other
- Each version's documentation is self-contained
- Easier to add new documentation in the appropriate category

### Clarity
- Repository structure clearly shows two separate applications
- Documentation organization matches the application structure
- New README files explain each version's purpose

## File Counts

**AudioBrowserOrig:**
- 11 application files
- 41 documentation files (organized in docs/)

**AudioBrowser-QML:**
- Main application + backend + QML files
- 28 documentation files (organized in docs/)

**Total:** 101 files moved or organized

## Documentation Categories

### User Guides
End-user focused documentation including how-to guides, feature guides, and visual guides.

### Technical Documentation
Developer and technical documentation including architecture, implementation details, and fix summaries.

### Test Plans
Quality assurance and testing documentation for various features.

### Phase Reports
Development phase reports and progress tracking for the QML migration project.

## Navigation

All documentation includes relative links for easy navigation between categories:

**From user guides:**
- To technical: `../technical/FILENAME.md`
- To phase reports: `../phase_reports/FILENAME.md`
- To root: `../../README.md`

**From technical docs:**
- To user guides: `../user_guides/FILENAME.md`
- To phase reports: `../phase_reports/FILENAME.md`

**From phase reports:**
- To user guides: `../user_guides/FILENAME.md`
- To technical: `../technical/FILENAME.md`

## No Breaking Changes

This reorganization:
- ✅ Maintains all existing code
- ✅ Preserves all documentation content
- ✅ Keeps git history for all files
- ✅ Uses `git mv` for proper tracking
- ✅ Updates all cross-references

## Future Work

This reorganization sets up a clean structure for:
- Continued QML development
- Maintenance of the original version
- Addition of new documentation
- Potential future versions or variants

---

**Date**: December 2024  
**Git Operations**: 101 file moves + 3 new files  
**Status**: ✅ Complete
