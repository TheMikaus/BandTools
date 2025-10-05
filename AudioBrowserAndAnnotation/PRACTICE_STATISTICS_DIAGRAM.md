# Practice Statistics Flow Diagram

## How Practice Statistics Are Tracked

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       PRACTICE STATISTICS SYSTEM                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 1: Open/Switch to Practice Folder                                 │
│  ─────────────────────────────────────────────────────────────          │
│  User Action: Select a folder containing audio files                     │
│                                                                           │
│  System Action:                                                           │
│    • Loads .practice_stats.json (or creates if new)                     │
│    • Starts new session timer                                            │
│    • Records session start time: datetime.now()                          │
│                                                                           │
│  Result: Session is now active and tracking begins                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 2: Play Audio Files                                               │
│  ──────────────────────────                                             │
│  User Action: Click play on any audio file                              │
│                                                                           │
│  System Action (per playback):                                           │
│    • Records playback start time                                         │
│    • Records filename being played                                       │
│    • When playback stops/pauses:                                         │
│      - Calculates duration = stop_time - start_time                     │
│      - If duration >= 1 second:                                          │
│        * Updates song's total_time                                       │
│        * Increments song's play_count                                    │
│        * Records song's last_played timestamp                            │
│        * Saves to .practice_stats.json                                  │
│                                                                           │
│  Example Song Entry:                                                     │
│    "Take_5.wav": {                                                       │
│      "total_time": 245.3,      ← Cumulative seconds played             │
│      "play_count": 3,           ← Number of times played                │
│      "last_played": "2024-01-15T12:00:00"                               │
│    }                                                                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 3: End Session (Triggered Automatically)                          │
│  ──────────────────────────────────────────                             │
│  Triggers:                                                               │
│    • User closes the application                                         │
│    • User switches to a different practice folder                        │
│                                                                           │
│  System Action:                                                           │
│    • Calculates session_duration = end_time - start_time                │
│    • If session_duration >= 60 seconds:                                 │
│      - Creates session record with:                                      │
│        * start_time                                                      │
│        * end_time                                                        │
│        * duration (in seconds)                                           │
│        * folder name                                                     │
│        * reviewed_count (# of files marked reviewed)                    │
│      - Appends to sessions array                                         │
│      - Saves to .practice_stats.json                                    │
│                                                                           │
│  Example Session Entry:                                                  │
│    {                                                                     │
│      "start_time": "2024-01-15T10:30:00",                               │
│      "end_time": "2024-01-15T12:15:00",                                 │
│      "duration": 6300,          ← Total seconds = 105 minutes           │
│      "folder": "2024-01-15-Practice",                                   │
│      "reviewed_count": 8        ← Files marked as reviewed              │
│    }                                                                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 4: View Statistics Dashboard                                      │
│  ───────────────────────────────                                        │
│  User Action: Help → "Practice Statistics" (or Ctrl+Shift+S)            │
│                                                                           │
│  System Calculations:                                                    │
│    • Total Practice Time:                                                │
│        sum(all session durations)                                        │
│                                                                           │
│    • Current Session:                                                    │
│        datetime.now() - session_start_time                              │
│                                                                           │
│    • Practice Consistency:                                               │
│        average(days between consecutive session dates)                   │
│                                                                           │
│    • Most Practiced Songs:                                               │
│        sort songs by total_time (descending), take top 5                │
│                                                                           │
│    • Least Practiced Songs:                                              │
│        sort songs by total_time (ascending), take bottom 5              │
│                                                                           │
│    • Recent Sessions:                                                    │
│        last 10 sessions (most recent first)                             │
│                                                                           │
│  Displays: HTML-formatted dialog with all statistics                     │
└─────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                        DATA STORAGE STRUCTURE
═══════════════════════════════════════════════════════════════════════════

File: .practice_stats.json (one per practice folder)
Location: Root of each practice folder

{
  "sessions": [
    {
      "start_time": "2024-01-10T14:00:00",
      "end_time": "2024-01-10T15:30:00",
      "duration": 5400,
      "folder": "2024-01-10-Practice",
      "reviewed_count": 10
    },
    {
      "start_time": "2024-01-12T10:00:00",
      "end_time": "2024-01-12T11:45:00",
      "duration": 6300,
      "folder": "2024-01-12-Practice",
      "reviewed_count": 8
    }
  ],
  "songs": {
    "Autumn_Leaves.wav": {
      "total_time": 423.5,
      "play_count": 5,
      "last_played": "2024-01-12T11:30:00"
    },
    "Blue_Bossa.wav": {
      "total_time": 189.2,
      "play_count": 2,
      "last_played": "2024-01-10T15:00:00"
    }
  }
}


═══════════════════════════════════════════════════════════════════════════
                           KEY BEHAVIORS
═══════════════════════════════════════════════════════════════════════════

✓ Automatic Tracking
  • No manual start/stop required
  • Runs transparently in background
  • Saves after each playback

✓ Independent Per Folder
  • Each practice folder has its own .practice_stats.json
  • Different projects/time periods tracked separately
  • No cross-folder contamination

✓ Minimum Thresholds
  • Playback: >= 1 second to count
  • Session: >= 60 seconds to be recorded
  • Prevents noise from accidental clicks

✓ Real-Time Updates
  • Statistics saved immediately after each playback
  • No data loss if application crashes
  • Current session time updates live in dashboard

✓ Cumulative Tracking
  • Song times accumulate across all sessions
  • Play counts increment with each playback
  • Session history preserved indefinitely


═══════════════════════════════════════════════════════════════════════════
                        EXAMPLE USAGE TIMELINE
═══════════════════════════════════════════════════════════════════════════

Monday 10:00 AM
  ├─ Open folder "2024-01-Week1-Practice"
  │  └─> Session starts, timer begins
  │
  ├─ Play "Song_A.wav" for 3:30 (210 seconds)
  │  └─> Song_A: total_time=210s, play_count=1
  │
  ├─ Play "Song_B.wav" for 2:45 (165 seconds)
  │  └─> Song_B: total_time=165s, play_count=1
  │
  ├─ Play "Song_A.wav" again for 1:50 (110 seconds)
  │  └─> Song_A: total_time=320s, play_count=2
  │
  └─ Close application
     └─> Session recorded: duration=8 minutes, reviewed_count=0

Tuesday 2:00 PM
  ├─ Open folder "2024-01-Week1-Practice"
  │  └─> New session starts (previous session ended)
  │
  ├─ Play "Song_C.wav" for 4:00 (240 seconds)
  │  └─> Song_C: total_time=240s, play_count=1
  │
  ├─ Mark Song_C as "Reviewed"
  │
  └─ Switch to folder "2024-01-Week2-Practice"
     └─> Week1 session recorded: duration=5 minutes, reviewed_count=1
     └─> Week2 session starts (fresh statistics file)

Friday 4:00 PM
  ├─ Open Practice Statistics (Ctrl+Shift+S)
  │
  └─> Dashboard shows:
      • Total Practice Time: 13 minutes
      • Current Session: 0 minutes (no session active)
      • Most Practiced: Song_A (320s), Song_C (240s), Song_B (165s)
      • Recent Sessions: 2 sessions listed
      • Practice Consistency: 2.0 days average


═══════════════════════════════════════════════════════════════════════════
For complete documentation, see PRACTICE_STATISTICS.md
═══════════════════════════════════════════════════════════════════════════
