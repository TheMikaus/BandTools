# Documentation Organization

This document explains the organization of AudioBrowser documentation and how to maintain it.

## Overview

As of this update, all AudioBrowser documentation has been reorganized into a structured folder hierarchy for better discoverability and maintenance.

## Folder Structure

```
AudioBrowserAndAnnotation/
├── README.md                    # Main application documentation
├── CHANGELOG.md                 # Version history
├── audio_browser.py             # Main application
├── audio_browser.spec           # PyInstaller build specification
└── docs/                        # All documentation organized by type
    ├── INDEX.md                 # Documentation index and navigation guide
    ├── user_guides/             # End-user documentation (16 files)
    │   ├── HOWTO_NEW_FEATURES.md
    │   ├── PRACTICE_GOALS_GUIDE.md
    │   ├── SETLIST_BUILDER_GUIDE.md
    │   ├── TEMPO_FEATURE_GUIDE.md
    │   ├── UI_IMPROVEMENTS.md
    │   ├── VISUAL_GUIDE_*.md
    │   └── ... (other user guides)
    ├── technical/               # Developer/technical documentation (18 files)
    │   ├── BUILD.md
    │   ├── INTERFACE_IMPROVEMENT_IDEAS.md
    │   ├── IMPLEMENTATION_SUMMARY*.md
    │   ├── FEATURE_SUMMARY_*.md
    │   └── ... (other technical docs)
    └── test_plans/              # QA and testing documentation (6 files)
        ├── TEST_PLAN_CLICKABLE_STATUS.md
        ├── TEST_PLAN_PRACTICE_GOALS.md
        ├── TEST_PLAN_SETLIST_BUILDER.md
        └── ... (other test plans)
```

## Category Descriptions

### User Guides (`docs/user_guides/`)

Documentation intended for end users of the application:
- **How-to guides**: Step-by-step instructions for using features
- **Feature guides**: Comprehensive documentation for major features
- **Visual guides**: UI mockups and ASCII diagrams
- **Setup guides**: Configuration and installation instructions

**Target audience**: Musicians, band members, end users

### Technical Documentation (`docs/technical/`)

Documentation for developers and those interested in implementation details:
- **Implementation summaries**: Technical details of how features work
- **Feature summaries**: Overview of feature completion and statistics
- **Build instructions**: How to compile and package the application
- **Architecture docs**: Design decisions and code organization
- **Feature roadmap**: INTERFACE_IMPROVEMENT_IDEAS.md tracks all planned/implemented features

**Target audience**: Developers, contributors, technical users

### Test Plans (`docs/test_plans/`)

Quality assurance and testing documentation:
- **Comprehensive test cases**: Detailed test procedures for each feature
- **Test execution checklists**: Structured testing workflows
- **Bug reporting templates**: Standardized issue reporting
- **Validation criteria**: Success metrics for features

**Target audience**: QA testers, developers, contributors

## Accessing Documentation

### In the Application

1. **Documentation Browser** (Ctrl+Shift+H):
   - Help menu → "Documentation Browser"
   - Browse all docs organized by category
   - Search/filter to find specific documents
   - Read full markdown content in-app

2. **Quick Access**:
   - Help → Keyboard Shortcuts
   - Help → Practice Statistics (Ctrl+Shift+S)
   - Help → Practice Goals (Ctrl+Shift+G)
   - Help → About
   - Help → Changelog

### In the Repository

- Browse the `docs/` folder on GitHub
- Start with `docs/INDEX.md` for a complete overview
- Cross-references use relative paths for easy navigation

### In Releases

Documentation is included in two ways:
1. **In the executable**: The `docs/` folder is bundled with PyInstaller builds
2. **Separate archive**: `AudioAnnotationBrowser-{version}-docs.zip` in releases

## Maintaining Documentation

### Adding New Documentation

When creating new documentation files:

1. **Determine category**:
   - User feature? → `docs/user_guides/`
   - Technical details? → `docs/technical/`
   - Test procedures? → `docs/test_plans/`

2. **Create the file** in the appropriate folder

3. **Update cross-references**:
   - Use relative paths for links
   - From `user_guides/` to README: `../../README.md`
   - From `user_guides/` to technical: `../technical/FILENAME.md`
   - From `user_guides/` to test plans: `../test_plans/FILENAME.md`

4. **Update INDEX.md**:
   - Add the new document to the appropriate section
   - Include a brief description

5. **Update main README.md** (if it's a major feature guide)

6. **Update CHANGELOG.md** with the documentation addition

### Cross-Reference Patterns

**From `user_guides/` to:**
- Root files: `../../README.md`, `../../CHANGELOG.md`
- Technical: `../technical/BUILD.md`
- Test plans: `../test_plans/TEST_PLAN_*.md`

**From `technical/` to:**
- Root files: `../../README.md`, `../../CHANGELOG.md`
- User guides: `../user_guides/HOWTO_NEW_FEATURES.md`
- Test plans: `../test_plans/TEST_PLAN_*.md`

**From `test_plans/` to:**
- Root files: `../../README.md`, `../../CHANGELOG.md`
- User guides: `../user_guides/PRACTICE_GOALS_GUIDE.md`
- Technical: `../technical/IMPLEMENTATION_SUMMARY*.md`

### Documentation Standards

All documentation should follow these conventions:

1. **Markdown format** (`.md` extension)
2. **Clear headers** with hierarchy (# ## ###)
3. **Code examples** in fenced code blocks with language tags
4. **Cross-references** to related documents
5. **Version/date information** where relevant (especially technical docs)
6. **ASCII art** for UI mockups and diagrams (where applicable)

### Naming Conventions

- User guides: Descriptive names (e.g., `PRACTICE_GOALS_GUIDE.md`)
- Technical docs: 
  - `IMPLEMENTATION_SUMMARY_*.md` for feature implementations
  - `FEATURE_SUMMARY_*.md` for feature overviews
  - `FEATURE_COMPLETION_*.md` for completion checklists
- Test plans: `TEST_PLAN_*.md` for all test documentation
- Visual guides: `VISUAL_GUIDE_*.md` for UI-focused documentation

## Build Integration

### PyInstaller Configuration

The `audio_browser.spec` file includes the docs folder:

```python
# Include documentation folder
import os
if os.path.exists('docs'):
    datas += [('docs', 'docs')]
```

This ensures documentation is bundled with the executable.

### GitHub Actions Workflow

The build workflow (`.github/workflows/build-audiobrowser.yml`) creates:
1. Executable with embedded docs
2. Separate documentation archive for releases

### Accessing Docs in Built Executable

The application code uses:

```python
docs_dir = Path(__file__).parent / "docs"
```

This works both when running from source and in PyInstaller builds.

## Migration Notes

### What Changed

**Before**: All markdown files were in the root of `AudioBrowserAndAnnotation/`

**After**: Documentation organized into:
- `docs/user_guides/` - 16 files
- `docs/technical/` - 18 files  
- `docs/test_plans/` - 6 files
- `docs/INDEX.md` - 1 file

**Files that stayed in root**:
- `README.md` - Main documentation entry point
- `CHANGELOG.md` - Version history

### Link Updates

All markdown cross-references were updated to use correct relative paths:
- Internal links within same category: `FILENAME.md`
- Links to other categories: `../category/FILENAME.md`
- Links to root files: `../../README.md`

### Code Changes

1. **audio_browser.py**:
   - Added `QListWidget` and `QListWidgetItem` imports
   - Added `_show_documentation_browser()` method (~130 lines)
   - Added menu item in Help menu with Ctrl+Shift+H shortcut

2. **audio_browser.spec**:
   - Added docs folder to PyInstaller datas

3. **.github/workflows/build-audiobrowser.yml**:
   - Added creation of docs archive
   - Added docs archive to release files

## Future Enhancements

Potential improvements to the documentation system:

1. **Markdown Rendering**: Implement rich markdown rendering with formatting, images, links
2. **Search Improvements**: Full-text search across all documentation
3. **History**: Track recently viewed documents
4. **Favorites**: Bookmark frequently accessed documents
5. **External Links**: Open related files or URLs from documentation
6. **Print Support**: Export documentation to PDF or print
7. **Offline Help**: Context-sensitive help within dialogs

## Questions or Issues

For questions about the documentation organization or to report issues:
- Open an issue on GitHub
- Check the main README.md for general application info
- Review CHANGELOG.md for recent updates

---

**Last Updated**: 2024  
**Related**: See [INDEX.md](INDEX.md) for complete documentation index
