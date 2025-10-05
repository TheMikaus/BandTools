# Practice Goals - User Guide

**Quick Access**: Help menu → "Practice Goals" or press `Ctrl+Shift+G`

---

## What are Practice Goals?

Practice Goals help you stay motivated and focused by setting specific, measurable targets for your practice sessions. Whether you want to practice more consistently, work on specific songs, or achieve performance-ready recordings, Practice Goals provides the structure and accountability you need.

---

## Goal Types

### 1. Weekly Time Goal
**Purpose**: Ensure you're dedicating enough time to practice each week

**Example**: "Practice 300 minutes (5 hours) this week"

**How it works**:
- Set a target time in minutes
- Progress is estimated based on number of recordings in practice folders
- Rough estimate: 3 minutes per audio file
- Perfect for maintaining consistent practice volume

**Best for**:
- Building practice habits
- Ensuring minimum weekly practice time
- Time management

---

### 2. Monthly Time Goal
**Purpose**: Long-term practice time commitment

**Example**: "Practice 1200 minutes (20 hours) this month"

**How it works**:
- Similar to weekly time goal but over a month
- Tracks cumulative practice time across all sessions
- More flexible than weekly goals

**Best for**:
- Long-term planning
- Balancing busy schedules
- Tracking overall practice volume

---

### 3. Weekly Session Count
**Purpose**: Maintain consistent practice frequency

**Example**: "Have 3 practice sessions this week"

**How it works**:
- Counts number of practice folders (sessions) created within date range
- Encourages regular practice rather than cramming
- Helps build consistent habits

**Best for**:
- Beginners building practice routines
- Preventing practice gaps
- Maintaining rhythm between band practices

---

### 4. Monthly Session Count
**Purpose**: Long-term consistency tracking

**Example**: "Have 12 practice sessions this month"

**How it works**:
- Similar to weekly session count but monthly
- Good for planning around schedules
- Tracks practice frequency over time

**Best for**:
- Balanced monthly planning
- Working around irregular schedules
- Long-term habit formation

---

### 5. Song Practice Count
**Purpose**: Ensure specific songs get adequate attention

**Example**: "Practice 'Difficult Song Title' 5 times this month"

**How it works**:
- Tracks how many practice sessions included the specified song
- Counts any session where the song appears (any number of takes)
- Prevents song neglect

**Best for**:
- Working on challenging songs
- Preparing specific songs for performance
- Balanced repertoire development
- Preventing favorite-song bias

---

### 6. Song Best Take Goal
**Purpose**: Achieve a performance-ready recording

**Example**: "Record a Best Take of 'Song Title' by end of month"

**How it works**:
- Binary goal: either achieved or not
- Completes when you mark any recording as "Best Take"
- Target is always 1 (automatic)
- Pushes toward recording-quality performances

**Best for**:
- Preparing songs for live performance
- Building confidence in song mastery
- Creating shareable recordings
- Tracking performance readiness

---

## Using the Practice Goals Interface

### Active Goals Tab

This tab shows all your current practice goals with real-time progress.

**What you'll see**:
- **Goal Cards**: Each goal has its own card showing:
  - Goal title and type
  - Date range (start to end)
  - Progress bar with percentage
  - Current vs target (e.g., "3 of 5 practices")
  - Days remaining
  - Status indicator

**Status Indicators**:
- ✅ **Green Progress Bar**: Goal completed! Celebration message displayed
- ⚠️ **Red Progress Bar**: Goal expired (deadline passed without completion)
- 🔵 **Blue/Orange Progress Bar**: Goal in progress, varying by completion percentage
- ⏰ **Days Remaining**: Countdown to deadline (e.g., "5 days remaining")

**Progress Bar Colors**:
- **Green**: ≥75% complete or goal achieved
- **Orange**: 50-74% complete
- **Blue**: <50% complete
- **Red**: Goal expired

**Auto-Filtering**:
- Goals are automatically hidden 7 days after expiration to keep the view clean
- Completed goals remain visible until 7 days after their end date

---

### Manage Goals Tab

This tab lets you create new goals and manage existing ones.

#### Creating a Goal

1. **Select Goal Type**: Choose from dropdown (6 options)
2. **Enter Song Name** (if applicable): Only enabled for song-specific goals
3. **Set Target**: Spinner adjusts based on goal type
   - Time goals: minutes
   - Session count: number of sessions
   - Practice count: number of practices
   - Best take: automatically set to 1
4. **Choose Date Range**: Use calendar popups to select start and end dates
5. **Click "Create Goal"**: Goal is saved and you're switched to Active Goals tab

**Form Behavior**:
- Fields adapt dynamically based on selected goal type
- Sensible defaults are provided
- Validation prevents invalid inputs

#### Managing Existing Goals

The **Existing Goals** table shows:
- Goal type and target
- Date range
- Current status and progress
- Delete button for each goal

**To Delete a Goal**:
1. Find goal in table
2. Click "Delete" button
3. Confirm deletion in popup dialog
4. Goal is immediately removed

**Note**: Goals cannot currently be edited. To change a goal, delete it and create a new one.

---

## Tips for Effective Goal Setting

### Start Small
- Don't set too many goals at once
- Start with 1-2 goals and add more as you succeed
- Better to achieve modest goals than fail at ambitious ones

### Be Realistic
- Consider your schedule and commitments
- Account for holidays, busy periods, etc.
- It's okay to have lower targets during busy times

### Mix Goal Types
- Combine time goals (quantity) with song goals (quality)
- Use session count goals for consistency
- Use best take goals for achievement milestones

### Review and Adjust
- Check your progress regularly (daily or weekly)
- Adjust future goals based on what worked
- Celebrate achievements!

### Use with Practice Statistics
- Open Practice Statistics (Ctrl+Shift+S) to see your history
- Use statistics to inform realistic goal setting
- Goals complement statistics perfectly

---

## Example Goal Sets

### Beginner Musician
1. Weekly Session Count: 3 sessions per week
2. Song Best Take: One best take this month

**Why**: Focus on consistency and achieving first quality recording

---

### Preparing for Performance
1. Song Practice Count: Practice "Song 1" 5 times
2. Song Practice Count: Practice "Song 2" 5 times
3. Song Best Take: Best take of "Song 1"
4. Song Best Take: Best take of "Song 2"

**Why**: Ensure each song is well-practiced and performance-ready

---

### Building Practice Habits
1. Weekly Session Count: 2 sessions per week
2. Weekly Time Goal: 120 minutes per week

**Why**: Establish regular practice routine with time commitment

---

### Balanced Repertoire Development
1. Song Practice Count: Practice "Difficult Song" 4 times
2. Song Practice Count: Practice "New Song" 3 times
3. Monthly Time Goal: 600 minutes this month

**Why**: Ensure challenging songs get attention while maintaining volume

---

## Frequently Asked Questions

### Q: How is practice time calculated?
**A**: Currently, practice time uses a rough estimate of 3 minutes per audio file. This is an approximation. Actual playback time tracking may be added in a future update.

### Q: Can I edit a goal after creating it?
**A**: Not yet. Currently, you must delete the goal and create a new one. Goal editing may be added in a future update.

### Q: What happens to expired goals?
**A**: Expired goals remain visible for 7 days after expiration, then are automatically hidden. The goals are still saved in the file but don't clutter the interface.

### Q: Are goals shared across different practice folders?
**A**: No. Each root practice folder has its own set of goals stored in `.practice_goals.json`. This allows different projects or bands to have separate goals.

### Q: Can I export or share my goals?
**A**: Not currently, but this could be added in a future update. Goals are stored in a simple JSON file that could be manually shared.

### Q: Do goals sync with Google Drive?
**A**: Goals are stored in the root practice folder, so they would be included in any folder-level sync or backup.

### Q: How often is progress calculated?
**A**: Progress is recalculated every time you open the Practice Goals dialog. It analyzes your practice folders in real-time.

### Q: Can I set goals for past dates?
**A**: Yes, but they will show as expired. This could be useful for tracking whether you met past goals.

### Q: What's the maximum number of goals I can have?
**A**: There's no hard limit, but having too many goals (50+) may make the interface cluttered. Focus on a few meaningful goals.

---

## Keyboard Shortcuts

- **Open Practice Goals**: `Ctrl+Shift+G`
- **Open Practice Statistics**: `Ctrl+Shift+S` (complementary feature)

---

## Technical Details

### Data Storage
- Goals are stored in `.practice_goals.json` in your root practice folder
- JSON format is human-readable and can be manually edited if needed
- Each goal has a unique UUID identifier

### Goal Progress Calculation
- Uses the same statistics engine as Practice Statistics feature
- Analyzes practice folder dates, audio files, and metadata
- Progress calculation happens on-demand (when opening dialog)
- No background tracking or performance impact

### Privacy
- All data is stored locally on your computer
- No data sent to external servers
- Goals are specific to each practice folder

---

## Troubleshooting

### Progress shows 0% but I have practice folders
- Ensure practice folders are within the goal's date range
- Check that folders have audio files
- Verify folders are in the correct root directory

### Goal creation shows validation error
- Ensure end date is after start date
- For song goals, song name field must not be empty
- Check that all required fields are filled

### Goals don't appear after restart
- Check that `.practice_goals.json` exists in root folder
- Ensure file is valid JSON (not corrupted)
- Check file permissions

### Progress calculation seems inaccurate
- Time goals use rough estimates (3 min/file)
- Progress is based on practice folder dates, not individual file dates
- Ensure practice folders follow date naming convention (YYYY-MM-DD)

---

## Future Enhancements

Potential features being considered:
- Actual playback time tracking (instead of estimates)
- Goal editing capability
- Goal templates for common scenarios
- System notifications for goal achievements
- Goal reminders
- Goal history view
- Goal analytics and trends
- Goal sharing/export

---

## Related Features

- **Practice Statistics** (`Ctrl+Shift+S`): View comprehensive practice history and analytics
- **Session State**: Track which files you've reviewed
- **Best Takes**: Mark performance-ready recordings
- **Annotations**: Add notes during practice sessions

---

**Need Help?** Check out the main README.md or open an issue on GitHub!
