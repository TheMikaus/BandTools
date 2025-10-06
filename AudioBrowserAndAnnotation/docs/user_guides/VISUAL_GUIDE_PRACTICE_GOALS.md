# Practice Goals - Visual Guide

This document provides a visual description of the Practice Goals feature interface and workflow.

---

## Accessing Practice Goals

### Menu Location
```
Help Menu
├─ Keyboard Shortcuts
├─ Practice Statistics          (Ctrl+Shift+S)
├─ Practice Goals                (Ctrl+Shift+G)  ← NEW!
├─ ─────────────────────
├─ About
└─ Changelog
```

### Keyboard Shortcut
- **Primary**: `Ctrl+Shift+G` - Opens Practice Goals dialog
- **Related**: `Ctrl+Shift+S` - Opens Practice Statistics (complementary feature)

---

## Practice Goals Dialog Layout

### Window Properties
- **Title**: "AudioBrowser - Practice Goals"
- **Size**: 900x700 pixels (resizable)
- **Layout**: Two-tab interface
- **Position**: Center of parent window

### Tab Structure
```
┌─────────────────────────────────────────────────────────────┐
│  AudioBrowser - Practice Goals                        [X]   │
├─────────────────────────────────────────────────────────────┤
│  [Active Goals]  [Manage Goals]                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Tab content area (described below)                         │
│                                                              │
│                                                              │
│                                                              │
│                                                              │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                                        [Close]              │
└─────────────────────────────────────────────────────────────┘
```

---

## Active Goals Tab

### Purpose
Display all current practice goals with real-time progress indicators.

### Layout Description

#### With Goals
```
┌─────────────────────────────────────────────────────────────┐
│  Active Goals                                               │
│                                                              │
│  Active Practice Goals                                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Weekly Goal - Time                                    │  │
│  │ 2025-01-01 to 2025-01-07                             │  │
│  │ [████████████████░░░░] 80% - 240 of 300 minutes      │  │
│  │ ⏰ 3 days remaining                                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Song: My Difficult Song - Practice Count             │  │
│  │ 2025-01-01 to 2025-01-31                             │  │
│  │ [████████░░░░░░░░░░░░░] 40% - 2 of 5 practices       │  │
│  │ ⏰ 15 days remaining                                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Song: Another Song - Best Take                        │  │
│  │ 2025-01-01 to 2025-01-31                             │  │
│  │ [████████████████████] 100% - Best take recorded!     │  │
│  │ ✅ Goal completed! Great work!                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Monthly Goal - Session Count                          │  │
│  │ 2024-12-01 to 2024-12-31                             │  │
│  │ [██████░░░░░░░░░░░░░░░] 30% - 3 of 10 sessions       │  │
│  │ ⚠️ Goal expired (5 days ago)                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

#### Without Goals (Empty State)
```
┌─────────────────────────────────────────────────────────────┐
│  Active Goals                                               │
│                                                              │
│  Active Practice Goals                                       │
│                                                              │
│  No practice goals set. Use the 'Manage Goals' tab to      │
│  create your first goal!                                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Goal Card Components

Each goal card contains:

1. **Goal Title** (Bold text)
   - Format depends on goal type:
     - Time/Session goals: "Weekly Goal - Time" or "Monthly Goal - Session Count"
     - Song goals: "Song: {song_name} - Practice Count" or "Song: {song_name} - Best Take"

2. **Date Range** (Italic text)
   - Format: "YYYY-MM-DD to YYYY-MM-DD"
   - Shows the active period for the goal

3. **Progress Bar**
   - Visual representation of completion percentage
   - Text overlay shows: "X% - {detailed message}"
   - Color-coded by status:
     - 🟢 Green: ≥75% complete or goal achieved
     - 🟠 Orange: 50-74% complete
     - 🔵 Blue: <50% complete
     - 🔴 Red: Goal expired

4. **Status Message**
   - ✅ "Goal completed! Great work!" (Green bar)
   - ⚠️ "Goal expired (X days ago)" (Red bar)
   - ⏰ "X days remaining" (Blue/Orange bar)

### Progress Bar Examples

**In Progress (Low)**:
```
[████░░░░░░░░░░░░░░░░░] 20% - 1 of 5 practices
```

**In Progress (Medium)**:
```
[████████████░░░░░░░░░] 60% - 180 of 300 minutes
```

**Near Completion**:
```
[██████████████████░░░] 90% - 9 of 10 sessions
```

**Completed**:
```
[████████████████████] 100% - Best take recorded!
```

**Expired**:
```
[████░░░░░░░░░░░░░░░░░] 20% - 2 of 10 sessions
⚠️ Goal expired (3 days ago)
```

---

## Manage Goals Tab

### Purpose
Create new goals and manage existing ones.

### Layout Description

```
┌─────────────────────────────────────────────────────────────┐
│  Manage Goals                                               │
│                                                              │
│  Manage Practice Goals                                       │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Create New Goal                                      │  │
│  │                                                        │  │
│  │  Goal Type: [Weekly Time Goal          ▼]            │  │
│  │                                                        │  │
│  │  Song Name: [_________________________]               │  │
│  │                                                        │  │
│  │  Target: [300] minutes                                │  │
│  │                                                        │  │
│  │  Start Date: [2025-01-01 📅]  End Date: [2025-01-07 📅] │
│  │                                                        │  │
│  │                              [Create Goal]            │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  Existing Goals                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Type           │Target│Start Date│End Date │Status    │  │
│  ├────────────────┼──────┼──────────┼─────────┼─────────┤  │
│  │ Weekly - Time  │300min│2025-01-01│2025-01-07│80% (...)│  │
│  │                │      │          │         │[Delete] │  │
│  ├────────────────┼──────┼──────────┼─────────┼─────────┤  │
│  │ Song: My Song  │  5   │2025-01-01│2025-01-31│40% (...)│  │
│  │                │      │          │         │[Delete] │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Goal Creation Form

#### Form Fields

1. **Goal Type Dropdown**
   ```
   Goal Type: [Weekly Time Goal          ▼]
   
   Options:
   - Weekly Time Goal
   - Monthly Time Goal
   - Weekly Session Count
   - Monthly Session Count
   - Song Practice Count
   - Song Best Take
   ```

2. **Song Name Input** (Conditional)
   ```
   Song Name: [Enter song name (for song-specific goals)]
   
   States:
   - Disabled: For Weekly/Monthly Time/Session Count goals
   - Enabled: For Song Practice Count and Song Best Take goals
   - Required: Must have text for song goals
   ```

3. **Target Spinner**
   ```
   Target: [300] minutes
   
   Adapts based on goal type:
   - Time goals: [300] minutes (default)
   - Session count: [3] sessions (default)
   - Practice count: [5] practices (default)
   - Best take: [1] (disabled, always 1)
   
   Range: 1 to 10,000
   ```

4. **Date Pickers**
   ```
   Start Date: [2025-01-01 📅]  End Date: [2025-01-07 📅]
   
   Features:
   - Calendar popup on click
   - Manual text entry
   - Format: YYYY-MM-DD
   - Auto-suggestions based on goal type:
     * Weekly goals: +7 days
     * Monthly goals: +30 days
   ```

5. **Create Goal Button**
   ```
   [Create Goal]
   
   Actions:
   1. Validates input
   2. Creates goal with unique ID
   3. Saves to .practice_goals.json
   4. Shows success message
   5. Switches to Active Goals tab
   6. Refreshes existing goals table
   ```

### Existing Goals Table

#### Table Structure
```
┌─────────────────────────────────────────────────────────────┐
│ Type                    │Target │Start Date│End Date │Status│Actions│
├─────────────────────────┼───────┼──────────┼─────────┼──────┼───────┤
│ Weekly - Time           │300 min│2025-01-01│2025-01-07│80% (in_progress)│[Delete]│
│ Song: Difficult Song    │  5    │2025-01-01│2025-01-31│40% (in_progress)│[Delete]│
│ Monthly - Session Count │  10   │2025-01-01│2025-01-31│100% (complete)  │[Delete]│
│ Song: Another Song      │  1    │2024-12-01│2024-12-31│0% (expired)     │[Delete]│
└─────────────────────────────────────────────────────────────┘
```

#### Table Columns

1. **Type**: Full description of goal type
   - Format for time/session: "{Period} - {Type}"
   - Format for song: "Song: {song_name}"

2. **Target**: Goal target value with units
   - Time: "X min"
   - Sessions/Practices: Just the number
   - Best take: Always "1"

3. **Start Date**: Goal start date (YYYY-MM-DD)

4. **End Date**: Goal end date (YYYY-MM-DD)

5. **Status**: Current progress and status
   - Format: "X% (status_name)"
   - Examples: "80% (in_progress)", "100% (complete)", "30% (expired)"

6. **Actions**: Delete button for each goal
   ```
   [Delete]
   
   Click sequence:
   1. Click Delete button
   2. Confirmation dialog appears:
      "Are you sure you want to delete this goal?"
   3. Click Yes to confirm or No to cancel
   4. Goal removed from table and file
   ```

---

## Form Behavior Examples

### Example 1: Creating Weekly Time Goal

**Initial State** (Weekly Time Goal selected):
```
Goal Type: [Weekly Time Goal          ▼]
Song Name: [________________________]  ← Disabled (grayed out)
Target: [300] minutes                  ← Default for time goals
Start Date: [2025-01-05 📅]            ← Today
End Date: [2025-01-12 📅]              ← Auto-set to +7 days
```

### Example 2: Switching to Song Practice Count

**After Switching**:
```
Goal Type: [Song Practice Count        ▼]
Song Name: [Enter song name...]        ← Enabled!
Target: [5] practices                  ← Default changed
Start Date: [2025-01-05 📅]            ← Unchanged
End Date: [2025-01-12 📅]              ← Auto-set to +7 days
```

### Example 3: Song Best Take Goal

**Special Behavior**:
```
Goal Type: [Song Best Take            ▼]
Song Name: [My Song Title]             ← Enabled, required
Target: [1]                            ← Disabled, always 1
Start Date: [2025-01-05 📅]
End Date: [2025-02-05 📅]              ← Auto-set to +30 days
```

---

## Validation Messages

### Missing Song Name
```
┌────────────────────────────────────┐
│  Invalid Input                 [X]│
├────────────────────────────────────┤
│  Please enter a song name for     │
│  song-specific goals.              │
├────────────────────────────────────┤
│                         [OK]       │
└────────────────────────────────────┘
```

### Invalid Date Range
```
┌────────────────────────────────────┐
│  Invalid Date Range            [X]│
├────────────────────────────────────┤
│  End date must be after start date.│
├────────────────────────────────────┤
│                         [OK]       │
└────────────────────────────────────┘
```

### Success Message
```
┌────────────────────────────────────┐
│  Goal Created                  [X]│
├────────────────────────────────────┤
│  Your practice goal has been       │
│  created successfully!             │
├────────────────────────────────────┤
│                         [OK]       │
└────────────────────────────────────┘
```

### Delete Confirmation
```
┌────────────────────────────────────┐
│  Delete Goal                   [X]│
├────────────────────────────────────┤
│  Are you sure you want to delete   │
│  this goal?                         │
├────────────────────────────────────┤
│              [Yes]        [No]     │
└────────────────────────────────────┘
```

---

## Workflow Visualizations

### Creating Your First Goal

```
1. Open Practice Goals
   [Help] → [Practice Goals] or Ctrl+Shift+G
   
2. Switch to Manage Goals Tab
   Click [Manage Goals] tab
   
3. Select Goal Type
   Choose from dropdown (e.g., "Weekly Time Goal")
   
4. Configure Goal
   - Set target: 300 minutes
   - Adjust date range if needed
   - Click [Create Goal]
   
5. View Progress
   Automatically switched to [Active Goals] tab
   See your new goal with current progress!
```

### Checking Progress

```
1. Open Practice Goals
   Ctrl+Shift+G
   
2. View Active Goals Tab
   (Opens to this tab by default)
   
3. Review Goal Cards
   - Check progress bars
   - Read status messages
   - Note days remaining
   
4. Take Action
   - Practice more if behind
   - Celebrate if complete!
   - Adjust future goals as needed
```

### Deleting a Completed Goal

```
1. Open Practice Goals
   Ctrl+Shift+G
   
2. Go to Manage Goals Tab
   Click [Manage Goals]
   
3. Find Goal in Table
   Locate the completed or expired goal
   
4. Delete Goal
   - Click [Delete] in Actions column
   - Confirm deletion in popup
   - Goal removed from both tabs
```

---

## Visual Indicators Summary

### Progress Bar Colors
- 🟢 **Green**: Goal complete or nearly complete (≥75%)
- 🟠 **Orange**: Good progress (50-74%)
- 🔵 **Blue**: Getting started (<50%)
- 🔴 **Red**: Goal expired (past deadline)

### Status Emojis
- ✅ **Checkmark**: Goal completed successfully
- ⚠️ **Warning**: Goal expired without completion
- ⏰ **Clock**: Days remaining countdown

### Card Styling
- **Background**: Light gray (#f0f0f0)
- **Border**: Subtle gray (#ccc)
- **Rounded corners**: 5px radius
- **Padding**: 10px internal spacing
- **Margin**: 5px between cards

---

## Keyboard Navigation

While no explicit keyboard shortcuts exist within the dialog:

- **Tab**: Navigate between form fields
- **Enter**: Activate buttons (Create Goal, Delete, Close)
- **Arrow Keys**: Navigate dropdowns and date pickers
- **Ctrl+Tab**: Switch between dialog tabs (standard Qt behavior)

---

## Data File Location

Goals are stored in your root practice folder:

```
Your Practice Folder/
├─ 2025-01-01-Practice/
│  ├─ song1.mp3
│  └─ song2.wav
├─ 2025-01-08-Practice/
│  └─ ...
└─ .practice_goals.json  ← Goals stored here
```

---

## Related Features Flow

```
Practice Workflow:
1. Record practice session → Audio files in dated folder
2. Mark best takes → Best Take metadata saved
3. Check statistics → Ctrl+Shift+S (Practice Statistics)
4. Set goals → Ctrl+Shift+G (Practice Goals)
5. Track progress → Return to Practice Goals regularly
6. Adjust and repeat!
```

---

## Tips for Using the Interface

### Efficient Goal Management
1. Start with 1-2 goals, not 10
2. Check progress weekly
3. Delete completed goals to keep clean
4. Use Active Goals tab for quick checks
5. Use Manage Goals tab for adjustments

### Visual Cues
- **Green bars** = Celebrate! 🎉
- **Red bars** = Review what went wrong
- **Orange/Blue bars** = Keep practicing!
- **Days remaining** = Plan your schedule

### Best Practices
- Create goals on Monday for weekly tracking
- Create goals on 1st of month for monthly tracking
- Check progress before practice to stay motivated
- Adjust targets based on what's achievable

---

This visual guide should help you understand the Practice Goals interface without needing screenshots. The actual implementation provides all these features with proper Qt styling and interactivity!
