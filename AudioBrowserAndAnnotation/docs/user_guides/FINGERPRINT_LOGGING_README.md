# Fingerprint Logging Implementation - Quick Start

## Problem Addressed

Issue: "AudioBrowserOrig - finger printing doesn't match anything ever. Can you add logging that shows the values of matches for stuff? What got selected? Both applications Orig, and QML should have the same logs and algorithms too."

## Solution Implemented

Added comprehensive logging to both AudioBrowserOrig and AudioBrowser-QML applications to show:
- ✅ All similarity scores for all comparisons
- ✅ What files were compared
- ✅ What match was selected and why
- ✅ Threshold values being used
- ✅ Reference folder boosts applied
- ✅ Both applications now use identical algorithms

## How to Use

### Step 1: Run the Application Normally

For **AudioBrowserOrig**:
```bash
cd AudioBrowserAndAnnotation/AudioBrowserOrig
python audio_browser.py
```

For **AudioBrowser-QML**:
```bash
cd AudioBrowserAndAnnotation/AudioBrowser-QML
python main.py
```

### Step 2: Use Auto-Label Feature

1. Set your fingerprint threshold in Preferences (default is 80%)
2. Click "Auto-Label Files" or "Auto-Label Subsections"
3. Watch the console/terminal for detailed logging output

### Step 3: Interpret the Logs

Look for output like this in your console:

```
[Auto-Label Files] Matching fingerprint for: 01_recording.wav

[FP Match] Starting fingerprint matching
[FP Match] Target fingerprint length: 144
[FP Match] Threshold: 80.00%
[FP Match] Number of files to compare against: 25

[FP Match] Top 10 scores (sorted by weighted score):
  1. reference_take.mp3 -> 'My Song' from practice_folder
     Raw score: 0.9856, Weighted: 1.0000 +15% [REF]
  2. other_take.wav -> 'My Song' from another_folder
     Raw score: 0.8543, Weighted: 0.8543
  ...

[FP Match] SELECTED MATCH:
  Filename: reference_take.mp3
  Provided name: 'My Song'
  Raw score: 0.9856
```

## Key Features

### 1. See All Comparison Scores
Every file comparison now shows its similarity score (0.0 to 1.0, higher is better).

### 2. Understand Why Matches Failed
If no match is found, you'll see:
- The top scores that were calculated
- How far below the threshold they were
- Suggestions for files that were "close" (within 50% of threshold)

### 3. Reference Folder Boosts Visible
Files from reference folders show:
- `+15% [REF]` for global reference folder
- `+10%` for per-folder reference
- This helps prioritize known good matches

### 4. Consistent Algorithms
Both AudioBrowserOrig and AudioBrowser-QML now use the same:
- Fingerprinting algorithms
- Matching logic
- Logging output

## Files Changed

1. **AudioBrowserOrig/audio_browser.py**
   - Enhanced `compare_fingerprints()` with debug logging
   - Enhanced `find_best_cross_folder_match()` with debug logging
   - Enabled debug logging in auto-label functions

2. **AudioBrowser-QML/backend/fingerprint_engine.py**
   - Enhanced `compare_fingerprints()` with debug logging
   - Added `collect_fingerprints_from_folders()` function (was missing!)
   - Added `find_best_cross_folder_match()` function (was missing!)
   - Both functions now match AudioBrowserOrig implementation

## Documentation

- **FINGERPRINT_LOGGING.md** - Technical documentation of the logging system
- **FINGERPRINT_LOGGING_EXAMPLE.md** - Example output with explanations
- **CHANGELOG.md** - Updated with changes

## Testing

A test script verified the logging works correctly:
- ✅ Compare fingerprints shows detailed similarity calculations
- ✅ Find best match shows all scores and selection logic
- ✅ Threshold filtering works as expected
- ✅ Reference folder boosts are applied correctly

## Next Steps

1. **Run the application** and try the Auto-Label feature
2. **Check the console output** to see the detailed logs
3. **Adjust your threshold** if needed based on the scores you see
4. **Mark reference folders** to boost matching accuracy

## Troubleshooting

### If you don't see logs:
- Make sure you're running the application from a terminal/console
- Logs appear in the terminal where you launched the application
- Logs only appear when using Auto-Label features

### If matches still aren't working:
- Check the "Top 10 scores" section in the logs
- If all scores are < 0.5, you may not have matching reference files
- If scores are 0.7-0.8, consider lowering your threshold
- Check that reference folders are configured correctly

### If wrong matches are selected:
- Look at the weighted vs raw scores
- Check if the correct file has a reference folder boost
- Consider marking the correct recordings as reference songs

## For Developers

The logging is implemented with minimal performance impact:
- Only activates when `debug=True` parameter is passed
- No performance cost during normal operation
- Easy to extend with additional logging points

To add more logging:
```python
# In any fingerprint function
if debug:
    log_print(f"[Debug Info] Your message here")
```

## Questions?

See the detailed documentation:
- **FINGERPRINT_LOGGING.md** for technical details
- **FINGERPRINT_LOGGING_EXAMPLE.md** for example output
