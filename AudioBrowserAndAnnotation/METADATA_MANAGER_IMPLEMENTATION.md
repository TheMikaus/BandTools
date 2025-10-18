# Shared Metadata Manager Implementation

## Overview

This implementation addresses the requirement to share metadata handling code between AudioBrowserOrig and AudioBrowser-QML applications. The metadata manager provides centralized handling of annotations, including fetching, setting, backups, and file I/O operations.

## Problem Statement

Previously, both AudioBrowser applications had duplicate implementations of metadata file operations:
- Annotation file path resolution
- Loading annotation data from disk
- Saving annotation data with backups
- Migrating legacy formats
- JSON I/O operations

This duplication meant:
- Bug fixes needed to be applied twice
- Implementations could drift apart
- More code to maintain
- Risk of inconsistent behavior

## Solution: Shared MetadataManager

Created `shared/metadata_manager.py` - a comprehensive metadata management module that both applications now use.

### Key Features

1. **Centralized File Path Resolution**
   - `get_annotation_sets_file_path()` - User-specific annotation sets
   - `get_annotation_file_path()` - Legacy per-file annotations
   - Consistent naming across both applications

2. **Annotation Loading/Saving**
   - `load_annotation_sets()` - Load multi-set annotation data
   - `save_annotation_sets()` - Save with automatic backup
   - `load_legacy_annotations()` - Load old format
   - `save_legacy_annotations()` - Save old format

3. **Automatic Backup Integration**
   - Uses existing `backup_utils` module
   - Automatic backup before modifications
   - Can be disabled for batch operations
   - Seamlessly integrated with both applications

4. **Legacy Migration Support**
   - `migrate_legacy_to_sets()` - Convert old format to new
   - Preserves all data during migration
   - Handles multiple legacy formats

5. **Discovery Utilities**
   - `discover_annotation_files()` - Find all annotation files
   - `get_annotation_count()` - Count annotations per user/directory

6. **JSON I/O**
   - `load_json()` - Load with error handling
   - `save_json()` - Save with optional backup
   - Consistent error handling

## Implementation Details

### Module Structure

```
shared/
├── __init__.py              (v1.1.0)
├── metadata_manager.py      (NEW - 430 lines)
├── metadata_constants.py
├── backup_utils.py
├── file_utils.py
├── audio_workers.py
└── README.md               (Updated with MetadataManager docs)
```

### Changes to AudioBrowser-QML

**File**: `AudioBrowser-QML/backend/annotation_manager.py`

Changes:
- Added import of `MetadataManager`
- Initialized `_metadata_manager` in `__init__`
- Updated `setCurrentUser()` to sync username with manager
- Replaced `_load_annotations()` with calls to `manager.load_legacy_annotations()`
- Replaced `_save_annotations()` with calls to `manager.save_legacy_annotations()`
- Replaced `_load_annotation_sets()` with calls to `manager.load_annotation_sets()`
- Replaced `_save_annotation_sets()` with calls to `manager.save_annotation_sets()`
- Replaced `_get_annotation_sets_file_path()` with calls to manager
- Removed obsolete `_get_annotation_file_path()` method

**Lines changed**: ~80 lines simplified, net reduction of ~21 lines

### Changes to AudioBrowserOrig

**File**: `AudioBrowserOrig/audio_browser.py`

Changes:
- Added import of `MetadataManager`
- Initialized `_metadata_manager` in `__init__` with user-specific configuration
- Updated `_load_notes()` to use `manager.load_annotation_sets()`
- Updated `_load_notes()` to use `manager.migrate_legacy_to_sets()` for migration
- Updated `_save_notes()` to use `manager.save_annotation_sets()`
- Preserved complex features (external sets, file watching, UI integration)

**Lines changed**: ~40 lines modified, improved consistency and maintainability

## Testing

### Test Suite

Created `test_metadata_manager.py` with comprehensive tests:

1. **test_metadata_manager_init** - Initialization and username management
2. **test_annotation_file_paths** - File path resolution
3. **test_json_io** - JSON load/save operations
4. **test_annotation_sets_operations** - Annotation sets I/O
5. **test_legacy_annotations** - Legacy format handling
6. **test_legacy_migration** - Migration to modern format
7. **test_discover_annotation_files** - File discovery
8. **test_backup_integration** - Automatic backup creation

**All 8 tests pass successfully**

### Validation

- ✅ Syntax validation for both applications
- ✅ All existing tests continue to pass
- ✅ Backward compatibility maintained
- ✅ No breaking changes to existing functionality

## Benefits

### 1. Single Source of Truth

**Before**: Two separate implementations of annotation I/O
```python
# AudioBrowserOrig
with open(annotation_file, 'r') as f:
    data = json.load(f)

# AudioBrowser-QML  
with open(annotation_file, 'r', encoding='utf-8') as f:
    data = json.load(f)
```

**After**: Single implementation
```python
# Both applications
data = self._metadata_manager.load_annotation_sets(directory)
```

### 2. Automatic Backups

**Before**: Manual backup calls scattered throughout code
```python
self._create_backup_if_needed()
save_json(path, data)
```

**After**: Automatic backup in manager
```python
manager.save_annotation_sets(directory, data, create_backup=True)
```

### 3. Consistent Error Handling

All metadata operations use consistent error handling patterns, reducing edge cases and unexpected behavior.

### 4. Easier Maintenance

Bug fixes and improvements to annotation handling now benefit both applications immediately.

### 5. Better Testing

Shared code has dedicated test suite, improving overall code quality.

## Usage Examples

### AudioBrowserOrig

```python
from shared.metadata_manager import MetadataManager

class AudioBrowser(QMainWindow):
    def __init__(self):
        # Initialize with user-specific configuration
        self._metadata_manager = MetadataManager(
            username=self._resolve_user_display_name()
        )
    
    def _load_notes(self):
        # Use shared manager for loading
        data = self._metadata_manager.load_annotation_sets(
            self.current_practice_folder,
            username=self._resolve_user_display_name()
        )
        # Process data...
    
    def _save_notes(self):
        # Use shared manager for saving
        success = self._metadata_manager.save_annotation_sets(
            self.current_practice_folder,
            payload,
            username=self._resolve_user_display_name(),
            create_backup=False  # Manual backup already done
        )
```

### AudioBrowser-QML

```python
from shared.metadata_manager import MetadataManager

class AnnotationManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._metadata_manager = MetadataManager(username=self._current_user)
    
    def _load_annotation_sets(self):
        data = self._metadata_manager.load_annotation_sets(
            self._current_directory,
            username=self._current_user
        )
        # Process data...
    
    def _save_annotation_sets(self):
        success = self._metadata_manager.save_annotation_sets(
            self._current_directory,
            data,
            username=self._current_user,
            create_backup=True
        )
```

## Code Statistics

### Shared Module
- **New file**: `metadata_manager.py` (430 lines)
- **New tests**: `test_metadata_manager.py` (380 lines)
- **Updated docs**: `shared/README.md` (expanded significantly)

### AudioBrowser-QML
- **Modified**: `backend/annotation_manager.py`
- **Lines changed**: ~80
- **Net reduction**: ~21 lines
- **Complexity**: Reduced

### AudioBrowserOrig
- **Modified**: `audio_browser.py`
- **Lines changed**: ~40
- **Net change**: Minimal
- **Complexity**: Maintained, consistency improved

### Total Impact
- **Lines added (shared)**: 810 (reusable across applications)
- **Lines modified (apps)**: ~120
- **Net benefit**: Single source of truth for metadata operations
- **Duplicate code removed**: ~100 lines
- **Test coverage**: +8 comprehensive tests

## Backward Compatibility

✅ **Full backward compatibility maintained**

- Both applications work with existing annotation files
- No breaking changes to file formats
- Existing backups remain accessible
- External annotation sets still supported (AudioBrowserOrig)
- File watching still functional (AudioBrowserOrig)
- All QML signals/slots preserved (AudioBrowser-QML)

## Future Enhancements

Potential improvements to the metadata manager:

1. **Batch Operations**: Optimize for bulk annotation operations
2. **Caching**: Add in-memory caching for frequently accessed data
3. **Validation**: Add schema validation for annotation data
4. **Compression**: Compress large annotation files
5. **Async I/O**: Support async file operations for better performance
6. **Change Tracking**: Track modifications for sync purposes

## Documentation

Comprehensive documentation added:

1. **shared/README.md**: Updated with full MetadataManager API docs
2. **test_metadata_manager.py**: Docstrings explain each test
3. **metadata_manager.py**: Detailed docstrings for all methods
4. **Code examples**: Usage examples for both applications

## Conclusion

The shared metadata manager successfully achieves the goal of centralizing annotation handling code between both AudioBrowser applications. This implementation:

✅ Eliminates code duplication
✅ Provides automatic backup support
✅ Maintains full backward compatibility
✅ Improves code maintainability
✅ Adds comprehensive test coverage
✅ Preserves all existing functionality

Both applications now benefit from a single, well-tested, documented source of truth for all metadata operations.
