# Enhanced Auto-Labeling Preview Feature

## Overview

The Enhanced Auto-Labeling Preview feature improves the fingerprint-based auto-labeling workflow by providing visual feedback, confidence scores, and selective application of suggestions. This makes the auto-labeling process more transparent and gives users fine-grained control over which suggestions to accept.

## Key Features

### 1. Visual Preview in Library Table

When auto-labeling is triggered, the Library table is enhanced with additional columns:
- **File** - Original filename
- **Reviewed** - Review status checkbox
- **Best Take** - Best take indicator
- **Partial Take** - Partial take indicator
- **Provided Name (editable)** - Shows the suggested name (highlighted in light yellow)
- **Apply?** - Checkbox to select/deselect this suggestion
- **Confidence** - Confidence score (color-coded by level)

### 2. Confidence Scores

Each suggestion includes a confidence score showing how closely the fingerprint matched:
- **90%+ (Dark Green)** - Very high confidence match
- **80-89% (Yellow-Green)** - High confidence match
- **70-79% (Orange)** - Medium confidence match
- **<70% (Red)** - Low confidence match

Confidence scores help users quickly identify which suggestions are most reliable.

### 3. Selective Application

Users have multiple ways to control which suggestions are applied:

#### Individual Selection
- Each suggestion has a checkbox in the "Apply?" column
- Check/uncheck individual suggestions to apply only what you want
- All suggestions default to checked (selected)

#### Confidence Threshold Filtering
- Adjust the confidence threshold slider (0-100%)
- Click "Select All ≥X%" to automatically select suggestions meeting the threshold
- Quickly filter out low-confidence matches

#### Apply Selected
- Click "Apply Selected" to save only the checked suggestions
- Unchecked suggestions are discarded
- Confirmation dialog shows how many suggestions were applied

### 4. Source Information

Hover over a confidence score to see which folder the match came from. This provides transparency about where the suggested name originated.

## Workflow

### Step 1: Generate Fingerprints
1. Select a practice folder in the file tree
2. Go to the Library tab
3. Click "Generate Fingerprints" to create fingerprints for audio files

### Step 2: Run Auto-Label
1. Click "Auto-Label from Practice Folders"
2. The application scans all practice folders for matching fingerprints
3. A progress dialog shows the matching process

### Step 3: Review Suggestions
The Library table now shows:
- Suggested names highlighted in light yellow background
- Confidence scores for each suggestion
- Checkboxes to selectively apply suggestions
- Source folder information in tooltips

### Step 4: Filter and Select
1. Adjust the confidence threshold slider if desired (e.g., 80%)
2. Click "Select All ≥80%" to automatically select high-confidence matches
3. Manually check/uncheck individual suggestions as needed
4. Review the suggested names before applying

### Step 5: Apply or Cancel
- **Apply Selected**: Saves only the checked suggestions to provided names
- **Cancel**: Discards all suggestions and reverts to previous state

## Use Cases

### Use Case 1: High-Confidence Quick Apply
You have a new practice session with 20 recordings of songs you've practiced before:
1. Run auto-label
2. Click "Select All ≥90%" to select only very high confidence matches
3. Review the 15 high-confidence suggestions
4. Click "Apply Selected"
5. Manually name the remaining 5 files

### Use Case 2: Careful Review with Low Threshold
You have recordings with varying quality and want to be cautious:
1. Run auto-label
2. Review all suggestions (default threshold 80%)
3. Uncheck any suggestions that don't look correct
4. Manually edit suggested names if needed (before applying)
5. Click "Apply Selected"

### Use Case 3: Selective Application
You have mixed recordings - some new songs, some familiar:
1. Run auto-label
2. Review suggestions
3. Uncheck suggestions for files you want to name manually
4. Check only suggestions for songs you recognize
5. Click "Apply Selected"
6. Manually name the remaining files

## Benefits

### Transparency
- See exactly what will be changed before committing
- Confidence scores help assess match quality
- Source folder information provides context

### Control
- Fine-grained control over which suggestions to accept
- Easy to exclude low-confidence or incorrect matches
- No need to accept all-or-nothing

### Efficiency
- Quickly apply high-confidence matches with one click
- Manual override for uncertain matches
- Reduces time spent on repetitive naming tasks

### Trust
- Visual feedback builds confidence in the auto-labeling system
- Clear indication of match quality
- Easy to verify and correct mistakes

## Technical Details

### Data Structure
Suggestions are stored in a dictionary with this structure:
```python
auto_label_suggestions = {
    "filename.wav": {
        'suggested_name': "My Song",
        'confidence': 0.85,
        'selected': True,
        'source_folder': "practice_2024_01",
        'matched_file': "01_My_Song.wav"
    }
}
```

### UI Updates
- Library table dynamically adjusts column count when in preview mode
- Normal mode: 5 columns
- Preview mode: 7 columns (adds "Apply?" and "Confidence")
- Table headers and resize modes automatically adjusted

### State Management
- `auto_label_in_progress` flag tracks whether preview mode is active
- `auto_label_backup_names` stores original names for cancel operation
- `auto_label_suggestions` stores all suggestion data
- State is cleared after apply or cancel

## Related Features

- **Fingerprint Generation** - Creates audio fingerprints for matching
- **Cross-Folder Matching** - Searches all practice folders for matches
- **Reference Folder** - Prioritize matches from a designated reference folder
- **Multi-Algorithm Support** - Choose from multiple fingerprinting algorithms

## Future Enhancements

Potential improvements mentioned in INTERFACE_IMPROVEMENT_IDEAS.md:
- Multi-algorithm consensus (run multiple algorithms, show agreement)
- Warning when algorithms disagree
- Allow user to specify which algorithms to use
- Batch edit suggested names before applying

## Troubleshooting

### No Suggestions Appear
- Ensure you've generated fingerprints for current folder
- Verify other practice folders have fingerprints
- Check that files are actually unlabeled (no provided names)
- Lower the fingerprint threshold if needed

### Low Confidence Scores
- Audio quality may be different between recordings
- Background noise or processing can affect matching
- Try different fingerprint algorithms
- Consider using reference folder for more consistent matches

### Incorrect Suggestions
- Uncheck incorrect suggestions individually
- Adjust confidence threshold to exclude low-quality matches
- Regenerate fingerprints if files have been modified
- Use manual naming for problematic files

---

**Implementation Note**: This feature was implemented to address Section 2.2 of the INTERFACE_IMPROVEMENT_IDEAS.md document, providing the preview mode and partial application capabilities requested by users.
