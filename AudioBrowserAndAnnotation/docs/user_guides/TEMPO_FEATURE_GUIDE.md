# Tempo & Metronome Integration - User Guide

## Quick Start

The Tempo & Metronome Integration feature allows you to set BPM (Beats Per Minute) for each song and visualize measure boundaries on the waveform.

### Setting BPM for a Song

1. Open a practice folder with audio files
2. Navigate to the **Library** tab
3. Find the **BPM** column (between "Partial Take" and "Provided Name")
4. **Double-click** the BPM cell for your song
5. Type the BPM value (e.g., "120")
6. Press **Enter** to save

```
Library Table View:
┌─────────────────┬──────────┬───────────┬──────────────┬─────┬─────────────────────┐
│ File            │ Reviewed │ Best Take │ Partial Take │ BPM │ Provided Name       │
├─────────────────┼──────────┼───────────┼──────────────┼─────┼─────────────────────┤
│ Song 1.mp3      │    ☐     │           │              │ 120 │ Fast Rock Song      │
│ Song 2.mp3      │    ☑     │     ✓     │              │ 90  │ Slow Blues Jam      │
│ Song 3.mp3      │    ☐     │           │      ~       │     │ Experimental Piece  │
└─────────────────┴──────────┴───────────┴──────────────┴─────┴─────────────────────┘
```

### Viewing Tempo Markers

1. Select a song that has a BPM set
2. Switch to the **Annotations** tab
3. The waveform will display **gray dashed vertical lines** at measure boundaries
4. **Measure numbers** (M4, M8, M12, etc.) appear every 4 measures

```
Waveform with Tempo Markers:
┌────────────────────────────────────────────────────────────────┐
│ M4        M8        M12       M16       M20       M24          │
│ ¦         ¦         ¦         ¦         ¦         ¦            │
│ ┊    ▂▃▄▅▆█████▆▅▄▃▂    ┊         ┊    ▄▅▆▇███▇▆▅▄    ┊       │
│ ┊  ▁▃▅▇███████████████▇▅▃▁  ┊         ┊  ▅▇█████████▇▅  ┊     │
│ ┊▂▄▆██████████████████████▆▄▂┊         ┊▃▆███████████████▆▃┊   │
│ ┊████████████████████████████┊         ┊████████████████████┊ │
│ ┊████████████████████████████┊         ┊████████████████████┊ │
│ ┊▁▃▅▇█████████████████████▇▅▃▁┊         ┊▁▄▇███████████▇▄▁┊   │
│ ┊  ▁▂▄▆████████████████▆▄▂▁  ┊         ┊  ▂▄▆█████▆▄▂  ┊     │
│ ┊    ▁▂▃▄▅▆███▆▅▄▃▂▁    ┊         ┊    ▁▂▄▅▄▂▁    ┊       │
│ ¦         ¦         ¦         ¦         ¦         ¦            │
│ 0:00      0:08      0:16      0:24      0:32      0:40         │
└────────────────────────────────────────────────────────────────┘

Legend:
  ┊  = Measure boundary (gray dashed line)
  █  = Waveform
  │  = Annotation marker (colored)
  ▶  = Playhead (dark line)
```

## Use Cases

### 1. Analyzing Timing Consistency

**Scenario**: Your band wants to check if you're maintaining steady tempo throughout a song.

**How to Use**:
1. Set the intended BPM for your song
2. Play the song while watching the waveform
3. Observe if strong beats (downbeats) align with measure markers
4. Identify sections where timing drifts

**Example**: If measure markers show steady spacing but your downbeats gradually shift, you're experiencing tempo drift.

### 2. Identifying Song Structure

**Scenario**: You want to quickly find specific sections (verse, chorus) in your recordings.

**How to Use**:
1. Set BPM for your song
2. Count measures to find structural changes
3. Use measure numbers (M4, M8, etc.) as navigation landmarks

**Example**: "The chorus starts at M16" - easier to reference than "2:08"

### 3. Practice with Visual Guides

**Scenario**: Practicing a song and want visual feedback on timing.

**How to Use**:
1. Set the correct BPM for the song
2. Play along with the recording
3. Watch the measure markers to stay on beat
4. Use waveform peaks at measure boundaries to identify strong beats

### 4. Comparing Takes at Different Tempos

**Scenario**: You recorded multiple versions of a song at different tempos.

**How to Use**:
1. Set different BPM values for each take
2. Compare how measure markers align with the music
3. Identify which tempo feels most comfortable

**Example**:
- Take 1: 120 BPM - feels rushed
- Take 2: 110 BPM - feels perfect
- Take 3: 100 BPM - feels sluggish

## Understanding the Visual Display

### Measure Line Appearance

**Color**: Light gray (#888888)  
**Style**: Dashed lines  
**Width**: 1 pixel (subtle, doesn't obscure waveform)

The subtle appearance ensures tempo markers:
- ✓ Provide visual guidance
- ✓ Don't interfere with viewing the waveform
- ✓ Don't obscure annotation markers
- ✓ Are distinguishable from other UI elements

### Measure Number Labels

**When Displayed**: Every 4 measures (M4, M8, M12, M16...)  
**Why**: Prevents visual clutter while providing navigation landmarks

**Reading Measure Numbers**:
- M4 = Measure 4 (16 beats into the song at 4/4 time)
- M8 = Measure 8 (32 beats)
- M12 = Measure 12 (48 beats)
- etc.

### Calculation

Tempo markers assume **4/4 time signature** (4 beats per measure).

**Formula**:
```
Time per measure = (60 seconds / BPM) × 4 beats
```

**Examples**:
- 120 BPM: 2 seconds per measure
- 90 BPM: 2.67 seconds per measure
- 180 BPM: 1.33 seconds per measure

## Tips & Best Practices

### 1. Finding the Right BPM

**Method 1: Tap Along**
- Play the song
- Tap spacebar or click along with the beat
- Use an online BPM calculator or count taps

**Method 2: Trial and Error**
- Set an approximate BPM (e.g., 120)
- Adjust up or down until measure markers align with downbeats
- Fine-tune by ±5 BPM increments

**Method 3: Reference Original**
- If covering a known song, look up the original BPM online
- Many songs have established BPM values

### 2. Dealing with Tempo Variations

**Slight Variations** (±2-3 BPM):
- Use the average BPM
- Markers will be close enough for reference

**Significant Variations** (tempo changes):
- Set BPM for the main section
- Note that markers won't align perfectly throughout
- Future feature will support multiple tempo zones

### 3. Working with Different Time Signatures

**Current Support**: 4/4 time only (most common in rock/pop)

**Workaround for Other Signatures**:
- 3/4 (waltz): Markers will show 4-beat measures, mentally adjust
- 6/8: Can treat as 2 groups of 3, or use 3/4 equivalent BPM
- Future feature will support variable time signatures

### 4. Organizing by Tempo

**Workflow Suggestion**:
- Add BPM to all songs in a practice session
- Sort Library table by BPM column
- Group songs by tempo ranges
- Practice similar-tempo songs together

## Data Management

### Storage Location

BPM data is stored in `.tempo.json` in each practice folder.

**File Structure**:
```json
{
  "Song 1.mp3": 120,
  "Slow Ballad.mp3": 72,
  "Fast Rocker.mp3": 180
}
```

### Backup & Recovery

- ✅ Included in automatic backup system
- ✅ Can be manually edited in text editor if needed
- ✅ Separate file per practice folder (no mixing)

### File Naming

If you rename a file using the Batch Rename feature:
- ✅ BPM value automatically transfers to new filename
- ✅ No manual update needed

## Keyboard Shortcuts

Currently, no dedicated keyboard shortcuts for BPM entry.

**Workflow**:
1. Click Library tab (or press the tab shortcut if configured)
2. Navigate to BPM cell with Tab key or mouse
3. Press Enter to edit (or double-click)
4. Type BPM value
5. Press Enter to save

## Troubleshooting

### Issue: Tempo markers not appearing

**Possible Causes**:
1. No BPM set for current song → Set BPM in Library tab
2. BPM cell is empty → Double-click and enter value
3. Song is not playing/loaded → Select and play the song
4. Not on Annotations tab → Switch to Annotations tab to see waveform

### Issue: Markers don't align with music

**Possible Causes**:
1. Incorrect BPM value → Adjust BPM up or down
2. Song has tempo changes → Set BPM for dominant tempo
3. Song started with pickup measure → Markers assume song starts at beat 1
4. Recording started before/after actual song → Trim audio or adjust mentally

### Issue: Too many markers (cluttered)

**Possible Causes**:
1. Very high BPM on long song → This is expected, zoom in if needed
2. Very long song (>30 minutes) → Safety limit at 1000 measures

**Solutions**:
- Markers are designed to be subtle (gray dashed)
- Zoom in on specific sections if needed
- Measure numbers only appear every 4 measures to reduce clutter

### Issue: BPM column not visible

**Possible Causes**:
1. Column is too narrow → Drag column border to widen
2. Window is too narrow → Resize window or scroll horizontally
3. Different version of app → Update to latest version

## Integration with Other Features

### With Annotations
- ✅ Tempo markers and annotation markers display together
- ✅ Different visual styles prevent confusion
- ✅ Both remain functional

### With Loop Markers (A-B)
- ✅ Loop regions (cyan) and tempo markers (gray) are distinguishable
- ✅ Can set loops at measure boundaries for practice
- ✅ Both features work independently

### With Best Takes
- ✅ BPM is preserved when marking as Best Take
- ✅ Included in Best Takes Package export
- ✅ Shows BPM when reviewing Best Takes

### With Practice Statistics
- ✅ Can analyze practice by tempo ranges
- ✅ Useful for tracking which tempo ranges need more practice
- ✅ Tempo data available for future analytics features

## Future Enhancements

The following features are planned but not yet implemented:

### Audio Metronome Click
- Play click sound alongside recording
- Adjustable click volume
- Different sounds for downbeat vs. other beats

### Automatic BPM Detection
- Analyze audio to detect BPM automatically
- "Detect BPM" button in Library tab
- Confidence score for detected values

### Variable Time Signatures
- Support for 3/4, 6/8, 5/4, etc.
- Time signature selector in Library tab
- Correct measure calculations per signature

### Tempo Change Support
- Mark tempo change points in song
- Multiple BPM zones within a song
- Visual tempo curve overlay

## Related Documentation

- [TEST_PLAN_TEMPO_METRONOME.md](../test_plans/TEST_PLAN_TEMPO_METRONOME.md) - Comprehensive test plan (31 test cases)
- [IMPLEMENTATION_SUMMARY_TEMPO_METRONOME.md](../technical/IMPLEMENTATION_SUMMARY_TEMPO_METRONOME.md) - Technical implementation details
- [INTERFACE_IMPROVEMENT_IDEAS.md](../technical/INTERFACE_IMPROVEMENT_IDEAS.md) - All feature ideas and status

## Feedback & Support

If you have suggestions for improving the tempo feature or encounter issues:
1. Open an issue on GitHub
2. Describe your use case and desired functionality
3. Include screenshots or recordings if relevant

---

**Version**: 1.0  
**Last Updated**: January 2025  
**Feature Status**: ✅ Implemented and Available
