# Fingerprint Logging - Example Output

## What You'll See When Running Auto-Label

When you run the "Auto-Label Files" or "Auto-Label Subsections" feature with the new logging, you'll see detailed output in the console showing exactly what's happening during fingerprint matching.

## Example Console Output

### For Each File Being Matched:

```
[Auto-Label Files] Matching fingerprint for: 01_recording.wav

[FP Match] Starting fingerprint matching
[FP Match] Target fingerprint length: 144
[FP Match] Threshold: 80.00%
[FP Match] Number of files to compare against: 25

[FP Match] Comparison results summary:
[FP Match] Total comparisons: 25
[FP Match] Matches above threshold (80.00%): 3

[FP Match] Top 10 scores (sorted by weighted score):
  1. chorus_take3.mp3 -> 'My Song Title' from 2024-01-15_Practice
     Raw score: 0.9856, Weighted: 1.0000 +15% [REF]
  2. verse_final.wav -> 'My Song Title' from 2024-01-20_Practice
     Raw score: 0.9234, Weighted: 0.9234
  3. bridge_v2.mp3 -> 'Bridge Section' from 2024-01-15_Practice
     Raw score: 0.8543, Weighted: 0.8543
  4. intro_raw.wav -> 'Intro' from 2024-01-10_Practice
     Raw score: 0.7821, Weighted: 0.7821
  5. outro_mix.mp3 -> 'Outro' from 2024-01-20_Practice
     Raw score: 0.7456, Weighted: 0.7456
  ...

[FP Match] Scores just below threshold (≥50% of threshold, <threshold):
  drums_only.wav -> 'Drum Track': 0.7523
  bass_line.mp3 -> 'Bass': 0.7012

[FP Match] SELECTED MATCH:
  Filename: chorus_take3.mp3
  Provided name: 'My Song Title'
  Raw score: 0.9856
  Weighted score: 1.0000
  Source folder: /path/to/practice/2024-01-15_Practice
  Folder count: 1
  Is reference: True
```

## What Each Section Means

### Initial Information
```
[FP Match] Target fingerprint length: 144
[FP Match] Threshold: 80.00%
[FP Match] Number of files to compare against: 25
```
- **Target fingerprint length**: How many data points are in the fingerprint being matched
- **Threshold**: Minimum similarity score required for a match (set in preferences)
- **Number of files**: How many reference files are being compared against

### Comparison Summary
```
[FP Match] Total comparisons: 25
[FP Match] Matches above threshold (80.00%): 3
```
- **Total comparisons**: Every reference file was compared
- **Matches above threshold**: Only 3 files scored high enough to be considered matches

### Top 10 Scores
```
  1. chorus_take3.mp3 -> 'My Song Title' from 2024-01-15_Practice
     Raw score: 0.9856, Weighted: 1.0000 +15% [REF]
```
- **Filename**: The reference file that was matched
- **Provided name**: What that file is labeled as (this is what will be copied)
- **Source folder**: Which practice folder it came from
- **Raw score**: Similarity score before any boosts (0.0 to 1.0, higher is more similar)
- **Weighted score**: Score after applying reference folder boosts
- **+15% [REF]**: This file got a 15% boost because it's from a reference folder
  - Files from global reference folder: +15%
  - Files from folder marked as reference: +10%
  - Files marked as reference songs: +10%

### Scores Near Threshold
```
[FP Match] Scores just below threshold (≥50% of threshold, <threshold):
  drums_only.wav -> 'Drum Track': 0.7523
```
This shows "near misses" - files that almost matched but didn't quite make the threshold. This helps you understand if you need to adjust your threshold.

### Selected Match
```
[FP Match] SELECTED MATCH:
  Filename: chorus_take3.mp3
  Provided name: 'My Song Title'
  Raw score: 0.9856
  Weighted score: 1.0000
  Source folder: /path/to/practice/2024-01-15_Practice
  Folder count: 1
  Is reference: True
```
This is the final match that was selected. The file being processed will be labeled with the "Provided name" shown here.

## Understanding Scores

### Excellent Match (0.95 - 1.0)
- Almost certainly the same recording or very close variant
- Expected for: Same song, same arrangement, slightly different takes

### Good Match (0.85 - 0.95)
- Likely the same song, possibly different recording quality or environment
- Expected for: Same song recorded on different days, different room acoustics

### Fair Match (0.75 - 0.85)
- Might be the same song, or might be different
- Consider: Different arrangements, live vs studio, instrumental vs full band

### Poor Match (< 0.75)
- Probably different songs
- May need to adjust fingerprinting algorithm or settings

## When No Matches Are Found

```
[FP Match] Comparison results summary:
[FP Match] Total comparisons: 25
[FP Match] Matches above threshold (80.00%): 0

[FP Match] Top 10 scores (sorted by weighted score):
  1. some_file.mp3 -> 'Some Song' from folder
     Raw score: 0.6543, Weighted: 0.6543
  ...

[FP Match] No matches found above threshold 80.00%
```

If you see this:
1. Look at the top scores - are any close to your threshold?
2. If top score is 0.65-0.75, consider lowering threshold to 70%
3. If top score is < 0.50, this is likely a new/unrecognized song
4. Check if reference fingerprints exist for the expected song

## Troubleshooting Tips

### All Scores Are Low (< 0.5)
- No similar recordings found in reference folders
- Check that reference folders are configured correctly
- Generate fingerprints for expected reference recordings

### Scores Are Good But Wrong Song Selected
- Multiple songs with similar audio characteristics
- Consider marking the correct recordings as reference songs
- Check if reference folder boost is working (should see [REF] and +15%)

### Inconsistent Matching
- Different fingerprinting algorithms may have been used
- Look for warning: "Comparing fingerprints of very different lengths"
- Regenerate all fingerprints using the same algorithm

### Target Fingerprint Length is 0
- Fingerprint wasn't generated for this file
- Check if file is valid audio
- Try manually generating fingerprint for this folder

## Additional Logging from compare_fingerprints

When comparing two specific fingerprints, you may see:
```
  [FP Compare] Lengths: fp1=144, fp2=144
  [FP Compare] Norms: norm1=3.316625, norm2=3.336165, dot_product=11.060000
  [FP Compare] Similarity: 0.999565
```

This shows the mathematical details of the comparison:
- **Lengths**: Number of data points in each fingerprint
- **Norms**: Magnitude of each fingerprint vector
- **Dot product**: How aligned the two fingerprints are
- **Similarity**: Final cosine similarity score

This detailed output is only shown when specifically debugging the comparison function.
