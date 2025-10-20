# Fingerprint Logging Documentation

## Overview

This document describes the comprehensive logging system added to the audio fingerprinting functionality in both AudioBrowserOrig and AudioBrowser-QML applications.

## Problem Statement

The fingerprinting feature was not matching files as expected. To diagnose and fix this issue, detailed logging has been added to show:
- What values are being compared
- What scores are being calculated
- What matches are being selected
- Why certain matches pass or fail the threshold

## Changes Made

### 1. Enhanced `compare_fingerprints()` Function

**Location:**
- `AudioBrowserOrig/audio_browser.py`
- `AudioBrowser-QML/backend/fingerprint_engine.py`

**New Parameter:**
- `debug: bool = False` - When True, logs detailed comparison information

**What Gets Logged (when debug=True):**
- Fingerprint lengths (fp1 and fp2)
- Computed norms (norm1, norm2, dot_product)
- Final similarity score
- Warnings for empty fingerprints or zero norms

**Example Output:**
```
  [FP Compare] Lengths: fp1=144, fp2=144
  [FP Compare] Norms: norm1=3.316625, norm2=3.336165, dot_product=11.060000
  [FP Compare] Similarity: 0.999565
```

### 2. Enhanced `find_best_cross_folder_match()` Function

**Location:**
- `AudioBrowserOrig/audio_browser.py`
- `AudioBrowser-QML/backend/fingerprint_engine.py`

**New Parameter:**
- `debug: bool = False` - When True, logs detailed matching information

**What Gets Logged (when debug=True):**

#### Initial Information:
- Target fingerprint length
- Threshold value
- Number of files to compare against

#### Comparison Results Summary:
- Total number of comparisons performed
- Number of matches above threshold

#### Top 10 Scores:
- Filename and provided name
- Source folder
- Raw score (before weighting)
- Weighted score (after reference boosts)
- Boost percentage applied
- Reference indicator [REF] if from reference folder

#### Scores Near Threshold:
- Files with scores between 50% and 100% of threshold
- Helps identify "almost matches"

#### Selected Match Details:
- Filename
- Provided name
- Raw score
- Weighted score
- Source folder
- Folder count (how many folders have this file)
- Is reference (whether from reference source)

**Example Output:**
```
[FP Match] Starting fingerprint matching
[FP Match] Target fingerprint length: 144
[FP Match] Threshold: 80.00%
[FP Match] Number of files to compare against: 15

[FP Match] Comparison results summary:
[FP Match] Total comparisons: 15
[FP Match] Matches above threshold (80.00%): 3

[FP Match] Top 10 scores (sorted by weighted score):
  1. song3.mp3 -> 'Song Three' from folder2
     Raw score: 0.9996, Weighted: 1.0000 +15% [REF]
  2. song1.mp3 -> 'Song One' from folder1
     Raw score: 0.9996, Weighted: 0.9996
  3. song2.mp3 -> 'Song Two' from folder1
     Raw score: 0.9711, Weighted: 0.9711
  ...

[FP Match] SELECTED MATCH:
  Filename: song3.mp3
  Provided name: 'Song Three'
  Raw score: 0.9996
  Weighted score: 1.0000
  Source folder: /practice/folder2
  Folder count: 1
  Is reference: True
```

### 3. Auto-Label Functions Updated

Both auto-labeling functions now enable debug logging:

**In AudioBrowserOrig:**
- `_auto_label_subsections_with_fingerprints()` - Line ~12016
- `_auto_label_with_fingerprints()` - Line ~13342

**Changes:**
```python
# Before:
match_result = find_best_cross_folder_match(current_fp, fingerprint_map, self.fingerprint_threshold)

# After:
log_print(f"\n[Auto-Label Files] Matching fingerprint for: {audio_file.name}")
match_result = find_best_cross_folder_match(current_fp, fingerprint_map, self.fingerprint_threshold, debug=True)
```

### 4. Added Missing Functions to QML Version

The AudioBrowser-QML version was missing critical functions that existed in AudioBrowserOrig. These have been added to ensure both applications use the same algorithms:

**Added to `AudioBrowser-QML/backend/fingerprint_engine.py`:**
- `collect_fingerprints_from_folders()` - Collects and organizes fingerprints from multiple folders
- `find_best_cross_folder_match()` - Finds the best matching file across folders

These functions are now identical between both applications, ensuring consistent behavior.

## How to Use the Logging

### Viewing Logs in AudioBrowserOrig:
1. Open the application
2. Look at the console/terminal where the application was launched
3. When running Auto-Label Files or Auto-Label Subsections, detailed logs will appear

### Viewing Logs in AudioBrowser-QML:
1. Open the application from terminal
2. When performing fingerprint matching operations, logs will appear in the console

### Understanding the Logs:

**High Similarity Scores (0.95-1.0):**
- Indicates very good match
- Should typically result in correct identification

**Medium Similarity Scores (0.7-0.95):**
- May indicate same song but different recording/quality
- May need threshold adjustment

**Low Similarity Scores (< 0.7):**
- Likely different songs
- May need to check fingerprint algorithm settings

**Reference Folder Boost:**
- Files from reference folders get +15% boost
- Per-folder reference gets +10% boost
- Reference songs get +10% boost
- This helps prioritize known good matches

## Troubleshooting with Logs

### If No Matches Are Found:

1. **Check the threshold:** Look at `[FP Match] Threshold: X%` - may be too high
2. **Check top scores:** Look at the "Top 10 scores" section - see what the actual scores are
3. **Check "Scores just below threshold":** See if there are near-misses
4. **Check fingerprint lengths:** Very different lengths may indicate different algorithms were used

### If Wrong Matches Are Selected:

1. **Check weighted vs raw scores:** Reference boosts may be too aggressive
2. **Check folder count:** Songs in multiple folders may be prioritized differently
3. **Compare scores:** See if the correct match had a lower score

### If Fingerprints Don't Load:

1. **Check target fingerprint length:** If 0, fingerprint wasn't generated or loaded
2. **Check number of files to compare:** If 0, no reference fingerprints available

## Algorithm Consistency

Both applications now use the same fingerprinting algorithms:
- `spectral` - Original spectral band analysis (default)
- `lightweight` - Downsampled STFT with log-spaced bands
- `chromaprint` - Chroma-based fingerprinting
- `audfprint` - Constellation fingerprinting

The logging will warn if fingerprints of very different lengths are being compared, which may indicate different algorithms were used.

## Performance Impact

The logging has minimal performance impact:
- Only enabled when `debug=True`
- Most computation (fingerprint comparison) happens regardless of logging
- Log output is buffered by the OS

For production use, logging can be disabled by passing `debug=False` (the default).

## Future Improvements

Potential enhancements:
- Add logging level control (INFO, DEBUG, VERBOSE)
- Save logs to file for offline analysis
- Add statistics on match success rates
- Add visualization of similarity scores
