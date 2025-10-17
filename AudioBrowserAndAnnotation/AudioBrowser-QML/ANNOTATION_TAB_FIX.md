# Annotation Tab Population Fix

## Issue
The Annotations tab in AudioBrowserQML did not populate when selecting a song in the Library tab. Users would click on a song, but the annotations table would remain empty even when annotations existed for that file.

## Root Cause
The `AnnotationManager` class maintains two separate storage systems:

1. **Legacy System**: `_annotations` dict mapping file paths to annotation lists
   - Used by `_load_annotations()` when reading from per-file `.{filename}_annotations.json` files
   - Populated automatically when `setCurrentFile()` is called

2. **New System**: `_annotation_sets` list containing annotation sets with per-file data
   - Used for multi-user annotation support
   - Loaded from directory-level `.{username}_notes.json` files
   - Each set contains a `files` dict with annotations organized by filename

The bug occurred because:
- `getAnnotations()` only read from `_annotation_sets`
- `setCurrentFile()` only populated `_annotations` (legacy system)
- Result: Empty annotation list even when annotations existed

## Solution
Modified `getAnnotations()` to implement a fallback strategy:

```python
@pyqtSlot(result=list)
def getAnnotations(self) -> List[Dict[str, Any]]:
    """Get all annotations for the current file."""
    if not self._current_file:
        return []
    
    # Try annotation sets first (if available)
    if has_annotation_sets and data_in_sets:
        return annotations_from_sets
    
    # Fallback to legacy format
    return self._annotations.get(self._current_file, [])
```

This ensures:
- Annotation sets are used when available (multi-user scenario)
- Legacy per-file annotations are used as fallback
- Both storage systems are supported seamlessly
- No data is lost during the transition

Also updated `getAnnotationCount()` to use `getAnnotations()` internally, ensuring consistency.

## Technical Details

### Files Modified
- `backend/annotation_manager.py`:
  - `getAnnotations()` method (lines 398-465)
  - `getAnnotationCount()` method (lines 469-482)
  - `getAnnotation()` method (lines 464-483)

### Backward Compatibility
The fix maintains full backward compatibility with:
- Existing per-file annotation files (`.{filename}_annotations.json`)
- New annotation sets files (`.{username}_notes.json`)
- Mixed environments where both formats exist

### Testing
Created comprehensive test suites:

1. **test_annotation_population.py**
   - Unit tests for annotation loading
   - Verifies count consistency
   - Tests filtering and edge cases

2. **test_annotation_tab_integration.py**
   - Integration test simulating user workflow
   - Tests song selection and annotation display
   - Verifies switching between songs
   - Tests model population

All tests pass successfully.

## User Impact
After this fix:
- ✓ Selecting a song in Library tab immediately populates Annotations tab
- ✓ Switching between songs updates annotations correctly
- ✓ Both legacy and new annotation storage systems work
- ✓ No data migration required
- ✓ No user action needed

## Related Components
The fix affects the data flow between:
- `LibraryTab.qml` → User clicks on song
- `AudioEngine` → Emits `currentFileChanged` signal
- `AnnotationsTab.qml` → Receives signal via `Connections` block
- `AnnotationManager` → Loads and returns annotations
- `AnnotationsModel` → Displays in table view

## Future Considerations
The dual storage system indicates ongoing migration to annotation sets. Future work should:
1. Complete migration to annotation sets for all scenarios
2. Deprecate legacy per-file format after transition period
3. Add migration utility to convert old annotations to new format
4. Update documentation to clarify storage format

## Testing Recommendations
When testing this fix:
1. Create annotations using the old format (per-file JSON)
2. Select songs and verify annotations appear
3. Create new annotations via the UI
4. Switch between songs with different annotation counts
5. Test with empty files (no annotations)
6. Verify important annotation indicators work
