# Best/Partial Take Indicators

## Overview

The Best/Partial Take Indicators feature allows users to mark audio files as "Best Takes" or "Partial Takes" for easy identification during practice sessions and recording workflows.

## Features

### Visual Indicators

- **Best Take**: Gold star icon (★)
- **Partial Take**: Half-filled star icon (◐)

Both indicators appear in a dedicated "Take" column in the Library tab's file list.

### Marking Files

There are two ways to mark files:

1. **Click on Indicators**: Click directly on the star icons in the file list to toggle best/partial take status
2. **Context Menu**: Right-click on any file and select:
   - "★ Mark as Best Take" / "★ Unmark Best Take"
   - "◐ Mark as Partial Take" / "◐ Unmark Partial Take"

### Filtering

Use the toolbar buttons to filter the file list:
- **★ Best Takes**: Show only files marked as best takes
- **◐ Partial Takes**: Show only files marked as partial takes

Both filters can be active simultaneously.

## Data Persistence

Take status is automatically saved to `.takes_metadata.json` in each directory, ensuring your markings persist across sessions.

### File Format

```json
{
  "best_takes": [
    "song_take1.wav",
    "solo_take3.wav"
  ],
  "partial_takes": [
    "verse_take2.wav"
  ]
}
```

## Implementation Details

### Backend (Python)

**FileManager** (`backend/file_manager.py`):
- `markAsBestTake(file_path)` - Mark a file as best take
- `unmarkAsBestTake(file_path)` - Unmark a file as best take
- `markAsPartialTake(file_path)` - Mark a file as partial take
- `unmarkAsPartialTake(file_path)` - Unmark a file as partial take
- `isBestTake(file_path)` - Check if file is marked as best take
- `isPartialTake(file_path)` - Check if file is marked as partial take
- `getBestTakes()` - Get list of all best takes
- `getPartialTakes()` - Get list of all partial takes

**FileListModel** (`backend/models.py`):
- Added `IsBestTakeRole` and `IsPartialTakeRole` for QML access
- Automatically loads take status when displaying files

### Frontend (QML)

**Components**:
- `BestTakeIndicator.qml` - Gold star indicator with click handling
- `PartialTakeIndicator.qml` - Half-filled star indicator with click handling

**Integration**:
- `LibraryTab.qml` - Displays indicators in file list, provides filter buttons
- `FileContextMenu.qml` - Provides mark/unmark menu items

## Usage Example

1. Browse to your audio directory
2. Click on the gold star next to your best recording
3. Click on the half-star next to recordings that are partially complete
4. Use the filter buttons to view only best or partial takes
5. Your selections are automatically saved

## Testing

Run the test suite:

```bash
cd AudioBrowserAndAnnotation/AudioBrowser-QML
python test_take_indicators.py
```

Tests verify:
- ✓ Marking and unmarking functionality
- ✓ JSON persistence
- ✓ Loading from metadata
- ✓ Model integration
- ✓ QML component existence

## Technical Notes

- Metadata is stored per-directory, not globally
- Filenames are used for identification (not full paths)
- Loading a new directory automatically loads take metadata for that directory
- Thread-safe operations through Qt signals/slots

## Future Enhancements

Potential improvements:
- Export list of best takes
- Batch mark/unmark operations
- Statistics on best vs partial take ratios
- Integration with practice statistics
- Color customization for indicators
