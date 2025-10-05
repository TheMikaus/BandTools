# Annotation Categories Documentation

## Overview

The Annotation Categories feature allows you to tag your annotations with predefined categories, making it easier to organize, filter, and analyze your practice feedback. This is especially useful when reviewing recordings with multiple types of issues or notes.

## Available Categories

AudioBrowser provides four predefined categories, each with a unique icon and color:

1. **⏱️ Timing** (Red: #FF6B6B)
   - Use for tempo issues, rushing, dragging
   - Notes about staying with the beat
   - Synchronization problems between band members

2. **⚡ Energy** (Teal: #4ECDC4)
   - Performance energy levels
   - Dynamics that need more power or restraint
   - Emotional intensity of the performance

3. **🎵 Harmony** (Green: #95E1D3)
   - Pitch issues, wrong notes
   - Chord voicing problems
   - Harmonization between instruments/vocals

4. **📊 Dynamics** (Yellow: #FFE66D)
   - Volume balance issues
   - Dynamic range concerns
   - Mix problems (too loud/quiet)

## How to Use Categories

### Adding a Categorized Annotation

1. **Play your audio file** and navigate to the **Annotations** tab

2. **Select a category** by clicking one of the category buttons at the top:
   - ⏱️ Timing
   - ⚡ Energy
   - 🎵 Harmony
   - 📊 Dynamics

3. **The selected button will highlight** with its category color

4. **Create your annotation** as usual:
   - Type your note in the text field
   - Press Enter to add the annotation

5. **The category is automatically saved** with the annotation

6. **The category selection clears** after adding the annotation, ready for your next note

### Clearing Category Selection

If you've selected a category but want to create an annotation without a category:
- Click the **❌ None** button to clear the selection
- Or click the same category button again to deselect it

### Viewing Categories in the Table

In the annotation table, you'll see a **Category** column that displays:
- The category icon and label (e.g., "⏱️ Timing")
- A colored background matching the category
- Empty cell for annotations without a category

The category column appears between the **Time** and **Note** columns.

## Filtering Annotations by Category

### Using the Category Filter

1. In the **Annotations** tab, locate the filter row above the annotation table

2. Find the **Category:** dropdown (to the right of the Show: dropdown)

3. Select a category filter option:
   - **All** - Show all annotations regardless of category
   - **⏱️ Timing** - Show only timing-related annotations
   - **⚡ Energy** - Show only energy-related annotations
   - **🎵 Harmony** - Show only harmony-related annotations
   - **📊 Dynamics** - Show only dynamics-related annotations
   - **No Category** - Show only annotations without any category

4. The annotation table updates immediately to show only matching annotations

### Combining Filters

You can use the category filter together with the annotation type filter:
- **Show:** All/Points/Clips/Sub-sections
- **Category:** All/Timing/Energy/Harmony/Dynamics/No Category

For example, you can filter to show only "Clip annotations with Timing issues".

## Exporting Annotations with Categories

When you export annotations to a text file (File → Export Annotations), categories are included automatically:

```
SongTitle.wav
== Set: YourName ==
Overview: Great energy overall but some timing issues in the bridge

0:15 [⏱️ Timing] Dragging slightly behind the beat
0:42 [⚡ Energy] Need more intensity in the chorus
1:23 [🎵 Harmony] Guitar slightly out of tune
2:05 [📊 Dynamics] Vocals too quiet in the mix
```

This makes it easy to review categorized feedback outside the application.

## Use Cases

### 1. **Focused Practice Sessions**
**Scenario:** You want to work specifically on timing issues this week.

**How to Use:**
1. Filter annotations by **⏱️ Timing** category
2. Review all timing-related notes across your practice files
3. Focus practice time on these specific issues
4. Mark files as "reviewed" once timing is improved

### 2. **Pre-Performance Review**
**Scenario:** Before a performance, check if there are any critical issues.

**How to Use:**
1. Load your setlist songs one by one
2. Check for **⏱️ Timing** and **🎵 Harmony** annotations
3. These are typically the most noticeable issues to audiences
4. Run through problem spots one more time

### 3. **Post-Recording Analysis**
**Scenario:** After a band practice, categorize all feedback by type.

**How to Use:**
1. Listen to each song and add annotations with appropriate categories
2. Use **Category** filter to see patterns (e.g., lots of timing issues on one song)
3. Identify which areas need the most work
4. Share categorized feedback with band members

### 4. **Mix and Production Notes**
**Scenario:** Preparing audio for mixing/mastering.

**How to Use:**
1. Use **📊 Dynamics** category for mix notes
2. Add annotations for volume balance issues
3. Filter by Dynamics to create a comprehensive mix notes document
4. Export annotations to share with sound engineer

### 5. **Instrument-Specific Feedback**
**Scenario:** Different band members working on different aspects.

**How to Use:**
1. **Timing** - Drummer and bass player focus
2. **Harmony** - Guitarists and vocalists focus
3. **Energy** - Everyone's concern, especially lead vocals
4. **Dynamics** - More for recording/mix engineers

Each member can filter to see feedback relevant to their role.

## Tips and Best Practices

### Choosing the Right Category

- **When in doubt, use no category** - It's better to have the note than to stress about categorization
- **Timing** is for rhythm and synchronization issues
- **Energy** is for performance feel and intensity
- **Harmony** is for pitch and note accuracy
- **Dynamics** is for volume and balance

### Consistency

- Try to be consistent with your categorization within a practice session
- Categories are subjective - what matters is that they're useful to you
- You can always filter by "No Category" to find uncategorized annotations and tag them later

### Workflow Integration

1. **First pass:** Add all annotations without categories (fast note-taking)
2. **Second pass:** Go back and categorize important annotations
3. **Third pass:** Filter by category to identify patterns

Or, if you prefer:
1. **As you go:** Select category before each annotation (more organized upfront)
2. **Review:** Use filters to verify you've covered all aspects

## Technical Details

### Storage Format

Categories are stored in your annotation metadata files (`.meta.json` and `.meta_[username].json`) as part of each annotation entry:

```json
{
  "uid": 123,
  "ms": 15000,
  "text": "Dragging slightly behind the beat",
  "important": false,
  "category": "timing"
}
```

### Backward Compatibility

- Annotations without a category simply don't have the `category` field
- Older annotation files work perfectly fine - they just show no category
- You can mix categorized and uncategorized annotations freely

### Multi-User Support

- Each user's annotations can have independent categories
- Categories are visible to all users but only editable by the creator
- This works seamlessly with the existing multi-user annotation system

## Related Features

- **Important Flag** (!) - Mark critical annotations regardless of category
- **Annotation Sets** - Organize annotations by user/band member
- **Annotation Filters** - Filter by type (Points/Clips/Sub-sections)
- **Annotation Export** - Share feedback as text files with categories

## Future Enhancements

Potential future improvements (see `INTERFACE_IMPROVEMENT_IDEAS.md`):

- Custom categories (user-defined beyond the four defaults)
- Category statistics (count annotations by category)
- Color customization for categories
- Multi-category tagging (one annotation with multiple categories)
- Category-based waveform coloring

---

**Questions or suggestions?** Open an issue on GitHub or check the main [README.md](README.md) for general application usage.
