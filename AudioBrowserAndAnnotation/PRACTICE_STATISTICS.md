# Practice Statistics Documentation

## Overview

The Practice Statistics feature helps you track and analyze your band practice sessions. It automatically monitors your practice time, shows which songs you're working on most (and least), and helps you maintain consistent practice habits.

## What Gets Tracked?

### Session-Level Tracking
- **Total Practice Time**: Cumulative time spent across all practice sessions
- **Current Session Duration**: Live tracking of your active practice session
- **Session Count**: Number of distinct practice sessions recorded
- **Practice Consistency**: Average number of days between practice sessions
- **Files Reviewed**: How many files you marked as "reviewed" during each session

### Song-Level Tracking
- **Total Playback Time**: How long you've spent listening to each song
- **Play Count**: Number of times each song has been played
- **Last Played Date**: When you last listened to each song

## How It Works

### Automatic Tracking

Practice statistics are tracked **automatically** in the background:

1. **Session Start**: When you open a practice folder, a new session begins
2. **Playback Tracking**: Every time you play an audio file, the playback time is recorded
3. **Session End**: When you close the app or switch to a different practice folder, the session ends
4. **Auto-Save**: Statistics are saved continuously as you use the application

> 💡 **Visual Learner?** See [PRACTICE_STATISTICS_DIAGRAM.md](PRACTICE_STATISTICS_DIAGRAM.md) for a detailed flow diagram and examples.

### Data Storage

- Statistics are stored in `.practice_stats.json` files
- **One file per practice folder** - each folder has its own independent statistics
- Located in the root of each practice folder alongside your audio files
- JSON format for easy backup and portability

### What Counts as Practice Time?

- **Minimum session duration**: 1 minute - Sessions shorter than this aren't recorded
- **Minimum playback duration**: 1 second - Very brief plays aren't counted
- **Active time only**: Only actual playback time is counted, not pause time or time browsing files

## How to View Statistics

### Opening the Dashboard

There are two ways to access your practice statistics:

1. **Menu**: Help → "Practice Statistics"
2. **Keyboard Shortcut**: `Ctrl+Shift+S`

### What You'll See

The Practice Statistics dashboard displays:

#### Session Summary
- **Total Sessions**: How many practice sessions you've completed
- **Total Practice Time**: Cumulative time in hours and minutes (e.g., "5h 42m")
- **Current Session**: Duration of your active session
- **Practice Consistency**: Average days between sessions (e.g., "3.5 days average between sessions")

#### Recent Sessions Table
Shows your last 10 practice sessions with:
- **Date**: When the session occurred (YYYY-MM-DD HH:MM)
- **Duration**: How long the session lasted
- **Folder**: Which practice folder you worked in
- **Files Reviewed**: How many files you marked as reviewed

#### Most Practiced Songs
Top 5 songs you've spent the most time on:
- **Song**: File name or provided song name
- **Total Time**: Cumulative playback time
- **Play Count**: Number of times played
- **Last Played**: When you last played it (e.g., "Today", "3 days ago")

#### Least Practiced Songs
Bottom 5 songs that might need more attention:
- Same metrics as "Most Practiced Songs"
- Helps identify neglected songs that need work

## Practical Use Cases

### 1. **Track Practice Goals**
**Use Case**: You want to practice 5 hours per week.

**How to Use**:
- Check "Total Practice Time" at the start and end of each week
- Monitor "Current Session" to stay motivated during practice
- Review "Recent Sessions" to see your weekly progress

### 2. **Balance Song Practice**
**Use Case**: You need to work on all songs equally before a performance.

**How to Use**:
- Check "Least Practiced Songs" to identify which songs need attention
- Focus your practice on songs with low play counts
- Use "Last Played" to ensure you're not neglecting any songs

### 3. **Maintain Consistent Practice Habits**
**Use Case**: You want to practice regularly, not just cram before shows.

**How to Use**:
- Monitor "Practice Consistency" metric
- Aim for consistent day gaps (e.g., practice every 2-3 days)
- Review "Recent Sessions" to spot gaps in your schedule

### 4. **Review Problem Songs**
**Use Case**: Some songs need extra attention and you want to track progress.

**How to Use**:
- Check which songs have high "Play Count" - these might be challenging songs
- Compare "Total Time" vs "Play Count" - high time/count ratio means you're spending more time per playback
- Use this data to identify songs that need focused practice

### 5. **Session Planning**
**Use Case**: You have 2 hours for practice and want to review progress.

**How to Use**:
- Check "Files Reviewed" in recent sessions to continue where you left off
- Review "Least Practiced Songs" to plan which files to focus on
- Monitor "Current Session" time to pace your practice

## Tips and Best Practices

### Getting Accurate Statistics

1. **Keep playing to completion**: Stats are only recorded if you play for at least 1 second
2. **Mark files as reviewed**: This helps track your progress through each session
3. **Use consistent practice folders**: Each folder tracks its own statistics
4. **Don't delete `.practice_stats.json`**: This is where your history is stored

### Understanding the Metrics

- **High play count + short total time**: You're playing many short segments (good for spot-checking specific parts)
- **Low play count + long total time**: You're doing deep listening sessions (good for comprehensive review)
- **Large gaps in "Recent Sessions"**: Inconsistent practice schedule
- **Many sessions, short durations**: Frequent but brief practice (consider longer sessions)

### Common Questions

**Q: Why doesn't my session appear in the statistics?**
- A: Sessions shorter than 1 minute aren't recorded. Make sure you're actively using the app.

**Q: Why is a song's total time less than I expected?**
- A: Only actual playback time is counted, not pause time or time with the song selected but not playing.

**Q: Can I reset or edit statistics?**
- A: Statistics are stored in `.practice_stats.json` in each practice folder. You can delete this file to reset (but you'll lose all history). Alternatively, edit the JSON file directly for manual adjustments.

**Q: Do statistics sync across computers?**
- A: No, practice statistics are intentionally local-only (not synced via Google Drive). This allows each band member to track their own practice time independently. If you want to share statistics, you can manually copy the `.practice_stats.json` file.

**Q: What if I practice in multiple folders?**
- A: Each practice folder maintains independent statistics. This is intentional - you might have separate projects or time periods you want to track separately.

**Q: Can I export or backup my statistics?**
- A: Yes! The `.practice_stats.json` file is a simple JSON file you can copy, backup, or analyze with other tools.

## Technical Details

### JSON Structure

The `.practice_stats.json` file contains:

```json
{
  "sessions": [
    {
      "start_time": "2024-01-15T10:30:00",
      "end_time": "2024-01-15T12:15:00",
      "duration": 6300,
      "folder": "2024-01-15-Practice",
      "reviewed_count": 8
    }
  ],
  "songs": {
    "Take_5.wav": {
      "total_time": 245.3,
      "play_count": 3,
      "last_played": "2024-01-15T12:00:00"
    }
  }
}
```

### Session Lifecycle

1. **Session Start**: Triggered when you select a practice folder
2. **Continuous Tracking**: Playback events update song statistics in real-time
3. **Session End**: Triggered by:
   - Switching to a different practice folder
   - Closing the application
4. **Data Persistence**: Stats saved to disk immediately after each playback and at session end

## Related Features

- **Reviewed Tracking**: Mark files as reviewed to track progress (session state)
- **Best Take Marking**: Identify your best recordings for quick reference
- **Annotations**: Leave timestamped notes to document what needs work
- **Status Bar Statistics**: See file counts at a glance in the status bar

## Future Enhancements

Planned improvements to practice statistics (see `INTERFACE_IMPROVEMENT_IDEAS.md`):

- Set weekly/monthly practice time goals
- Track goal progress with visual indicators
- Notifications when goals are met or missed
- Per-song practice goals (e.g., "Practice this song 5 times this week")
- Export statistics to CSV for external analysis
- Practice time charts and visualizations

---

**Need help?** Open an issue on GitHub or check the main [README.md](README.md) for general application usage.
