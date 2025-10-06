# Practice Statistics Documentation

## Overview

The Practice Statistics feature analyzes your band practice folders and recordings to provide insights into your practice history. It automatically scans your practice folders, analyzes audio files, and generates statistics showing which songs you've practiced, how often, and when.

## What Gets Analyzed?

### Practice Session Analysis
- **Total Practice Sessions**: Number of practice folders analyzed
- **Total Recordings**: Total count of audio files across all practices
- **Unique Songs**: Number of distinct songs identified
- **Date Range**: Time span from first to last practice session
- **Practice Consistency**: Average number of days between practice sessions

### Song-Level Analysis
- **Times Practiced**: How many practice sessions included this song
- **Total Takes**: Total number of recordings of this song
- **Best Takes**: Count of recordings marked as "Best Take"
- **Last Practiced**: When this song was last practiced

## How It Works

### Folder-Based Analysis

Practice statistics are generated **on-demand** by analyzing your practice folders:

1. **Folder Discovery**: Scans your band practice directory for folders containing audio files
2. **Date Detection**: Extracts practice dates from folder names (e.g., "2024-01-15-Practice") or folder timestamps
3. **File Analysis**: Examines audio files, provided names, and annotations in each folder
4. **Statistics Generation**: Compiles data into meaningful statistics when you open the dashboard

### Folder Naming Convention

For accurate date tracking, use dated folder names like:
- `2024-01-15-Practice`
- `2024-01-15-Rehearsal`
- `2024-01-15` (any format starting with YYYY-MM-DD)

If folders don't follow this pattern, the system uses folder modification timestamps.

### What Gets Analyzed?

The system examines:
- **Audio files**: `.wav` and `.mp3` files in each practice folder
- **Provided names**: Song names from `.provided_names.json`
- **Annotations**: Best Take and Partial Take markers from `.audio_notes_*.json`
- **Folder metadata**: Creation/modification dates for session dating

## How to View Statistics

### Opening the Dashboard

There are two ways to access your practice statistics:

1. **Menu**: Help → "Practice Statistics"
2. **Keyboard Shortcut**: `Ctrl+Shift+S`

### What You'll See

The Practice Statistics dashboard displays:

#### Overall Summary
- **Total Practice Sessions**: Number of practice folders found
- **Total Recordings**: Count of all audio files
- **Unique Songs**: Number of different songs identified
- **Date Range**: Time span of your practices (e.g., "2024-01-10 to 2024-03-15")
- **Practice Consistency**: Average days between practices (e.g., "3.5 days average between practices")

#### Recent Practice Sessions Table
Shows your last 10 practice sessions with:
- **Date**: When the practice occurred (extracted from folder name or timestamp)
- **Folder**: Practice folder name
- **Files**: Number of audio files recorded in that session
- **Songs**: Number of unique songs practiced
- **Best Takes**: How many recordings were marked as Best Take

#### Most Practiced Songs
Top 5 songs by practice count:
- **Song**: Song name (from provided names or filename)
- **Times Practiced**: How many practice sessions included this song
- **Total Takes**: Total number of recordings across all sessions
- **Best Takes**: How many recordings were marked as Best Take
- **Last Practiced**: When you last worked on this song (e.g., "Today", "3 days ago")

#### Least Practiced Songs
Bottom 5 songs that might need more attention:
- Same metrics as "Most Practiced Songs"
- Helps identify songs that haven't been practiced recently

## Practical Use Cases

### 1. **Monitor Practice Frequency**
**Use Case**: You want to ensure your band practices regularly.

**How to Use**:
- Check "Total Practice Sessions" and "Date Range" to see overall activity
- Monitor "Practice Consistency" to see if you're meeting your practice schedule
- Review "Recent Practice Sessions" to identify gaps in your practice schedule

### 2. **Balance Song Practice**
**Use Case**: You need to work on all songs equally before a performance.

**How to Use**:
- Check "Least Practiced Songs" to identify which songs need more takes
- Focus your next practice on songs with low "Times Practiced" counts
- Use "Last Practiced" to ensure you're not neglecting any songs for too long

### 3. **Track Song Development**
**Use Case**: You want to see how much work has gone into each song.

**How to Use**:
- Review "Total Takes" to see how many recordings you've made of each song
- Compare "Times Practiced" vs "Total Takes" to see which songs get multiple takes per session
- Check "Best Takes" count to see which songs have strong recordings ready

### 4. **Identify Problem Songs**
**Use Case**: Some songs require more attempts to get right.

**How to Use**:
- Look for songs with high "Total Takes" but low "Best Takes" - these need more work
- Songs with many takes across multiple sessions likely have challenging parts
- Use this data to plan focused practice sessions on difficult material

### 5. **Prepare for Performances**
**Use Case**: You need to review your setlist before a show.

**How to Use**:
- Check when setlist songs were "Last Practiced" - refresh anything that's stale
- Verify all performance songs have at least one "Best Take" marked
- Review "Recent Practice Sessions" to see if you've covered all necessary material

## Tips and Best Practices

### Getting Accurate Statistics

1. **Use dated folder names**: Name folders like "2024-01-15-Practice" for accurate session dating
2. **Provide song names**: Fill in the "Provided Name" column so songs are properly identified
3. **Mark best takes**: Mark your best recordings so statistics can track quality progress
4. **Organize by practice session**: Keep each practice session in its own dated folder

### Understanding the Metrics

- **High "Total Takes" + High "Best Takes"**: Song is well-rehearsed with multiple good recordings
- **High "Total Takes" + Low "Best Takes"**: Song needs more work - many attempts but few successes
- **High "Times Practiced"**: Song appears in many sessions - core repertoire material
- **Large gaps between practices**: Consider more frequent practice sessions
- **Many songs, few takes each**: Covering a lot of material - good for variety

### Common Questions

**Q: Why doesn't my practice folder appear in the statistics?**
- A: Make sure the folder contains `.wav` or `.mp3` audio files. Empty folders are skipped.

**Q: How does it determine practice dates?**
- A: First, it looks for YYYY-MM-DD patterns in folder names (e.g., "2024-01-15-Practice"). If not found, it uses the folder's modification timestamp.

**Q: Can I regenerate statistics?**
- A: Yes! Statistics are generated fresh each time you open the dashboard - they're not stored anywhere. Just click "Practice Statistics" again to update.

**Q: What if song names aren't showing correctly?**
- A: Statistics use the "Provided Name" from each file. If you haven't set provided names, it will use filenames instead. Fill in the "Provided Name" column to improve accuracy.

**Q: Do statistics include all band members' annotations?**
- A: Yes! The system scans all `.audio_notes_*.json` files, so Best Take markings from any band member are counted.

**Q: Can I analyze practices from different projects separately?**
- A: Statistics include all practice folders under your Band Practice Directory. To analyze different projects, set different root directories for each project.

**Q: How does it handle duplicate song names across folders?**
- A: Songs with the same name are treated as the same song. The system aggregates takes, practice counts, and dates across all folders.

## Technical Details

### How Statistics Are Generated

When you open the Practice Statistics dialog:

1. **Folder Discovery**: Scans the Band Practice Directory for all subdirectories containing `.wav` or `.mp3` files
2. **Date Extraction**: Attempts to parse dates from folder names using YYYY-MM-DD pattern, falls back to folder timestamps
3. **File Analysis**: For each practice folder:
   - Counts audio files
   - Loads `.provided_names.json` to identify song names
   - Scans `.audio_notes_*.json` files for Best Take and Partial Take markers
4. **Aggregation**: Combines data across all folders to generate overall statistics
5. **Display**: Formats and displays in HTML dialog

### Performance

Statistics generation is fast even with large practice histories:
- Folders are scanned recursively only when needed
- Only metadata files are read (not audio file contents)
- Results are generated on-demand (not cached)
- Typical generation time: < 1 second for 100+ practice folders

## Related Features

- **Reviewed Tracking**: Mark files as reviewed to track progress (session state)
- **Best Take Marking**: Identify your best recordings for quick reference
- **Annotations**: Leave timestamped notes to document what needs work
- **Status Bar Statistics**: See file counts at a glance in the status bar

## Future Enhancements

Planned improvements to practice statistics (see `INTERFACE_IMPROVEMENT_IDEAS.md`):

- Set practice frequency goals (e.g., "Practice 3 times per week")
- Track goal progress with visual indicators
- Export statistics to CSV for external analysis
- Practice history charts and visualizations
- Filter statistics by date range
- Compare statistics across time periods

---

**Need help?** Open an issue on GitHub or check the main [README.md](../../README.md) for general application usage.
