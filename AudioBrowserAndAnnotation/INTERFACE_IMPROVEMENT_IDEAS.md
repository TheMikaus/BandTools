# AudioBrowser Interface Improvement Ideas

This document contains brainstormed ideas for improving the AudioBrowser interface, reducing mouse movement, enhancing workflows, and adding practice-focused features. These are suggestions for future consideration, not immediate implementation tasks.

**Status Legend:**
- ✅ **IMPLEMENTED** - Feature has been completed and is available in the application
- 🚧 **IN PROGRESS** - Feature is currently being worked on
- ⏳ **PLANNED** - Feature is scheduled for implementation
- 💡 **IDEA** - Feature is a suggestion for future consideration (default)

---

## 1. Interface Improvements & Mouse Movement Reduction

### 1.1 Keyboard Navigation Enhancements ✅ **IMPLEMENTED**

**Current State:**
- Some keyboard shortcuts exist (Undo/Redo, Alt+Up)
- Most operations require mouse clicks through menus or toolbar

**Improvement Ideas:**

1. **Global Keyboard Shortcuts:**
   - `Space` - Play/Pause (like video players)
   - `Left/Right Arrow` - Skip backward/forward by 5-10 seconds
   - `Up/Down Arrow` - Previous/Next file in list
   - `J/K/L` - Rewind/Pause/Fast-forward (video editing standard)
   - `M` - Toggle mute
   - `N` - Add annotation at current playback position
   - `B` - Mark as best take
   - `P` - Mark as partial take
   - `Ctrl+Shift+R` - Batch rename
   - `Ctrl+E` - Export annotations
   - `Ctrl+F` - Focus search/filter box (see 1.2)
   - `1-9` - Jump to 10%, 20%, ... 90% of current song
   - `0` - Jump to beginning
   - `[` / `]` - Set clip start/end markers

2. **Tab Navigation:**
   - `Ctrl+Tab` / `Ctrl+Shift+Tab` - Cycle through tabs
   - `Ctrl+1/2/3/4` - Jump directly to specific tabs
   - `F2` - Rename currently selected file's provided name

3. **Annotation Shortcuts:**
   - `Enter` - Add annotation (when annotation text is focused)
   - `Ctrl+Enter` - Add "important" annotation
   - `Delete` - Delete selected annotation
   - `Alt+I` - Toggle annotation "important" flag

**Why:** Reduces hand travel between keyboard and mouse, speeds up repetitive tasks during long review sessions.

---

### 1.2 Quick Filter/Search Box ✅ **IMPLEMENTED**

**Current State:**
- No way to filter files by name or quickly jump to a song
- Must scroll through file tree manually

**Improvement Ideas:**

1. **File Tree Filter:**
   - Add search box above file tree
   - Filter files as you type (fuzzy matching preferred)
   - Show match count (e.g., "3 of 45 files")
   - `Esc` to clear filter
   - Highlight matching text in file names

2. **Quick Jump:**
   - Type song name prefix to jump to file
   - Similar to "quick open" in IDEs
   - Could work in Library table too

3. **Filter Options:**
   - Show only Best Takes checkbox
   - Show only Partial Takes checkbox
   - Show only files with annotations
   - Show only files without provided names
   - Combine filters with AND/OR logic

**Why:** Finding specific files in large practice sessions (15-30+ songs) requires excessive scrolling and visual scanning.

---

### 1.3 Context-Aware Right-Click Menus ✅ **IMPLEMENTED**

**Current State:**
- Right-click context menu exists but could be more comprehensive
- Some operations only accessible through top menu or Library tab

**Improvement Ideas:**

1. **Enhanced File Tree Context Menu:**
   - "Play" (instead of single-click)
   - "Play from here" (queue multiple files)
   - "Add annotation at 0:00"
   - "Quick rename" (inline edit of provided name)
   - "Copy filename to provided name"
   - "Export this file with boost"
   - Submenu: "Mark as..." → Best Take, Partial Take, Reference Song
   - "Jump to in Library tab"
   - "Jump to in Annotations tab"

2. **Waveform Right-Click:**
   - "Add annotation here"
   - "Set clip start"
   - "Set clip end"
   - "Zoom to selection"
   - "Export selection"

3. **Library Table Right-Click:**
   - "Play"
   - "Reveal in file tree"
   - "Copy provided name to clipboard"
   - "Auto-suggest name from fingerprint"

**Why:** Reduces need to switch tabs or navigate to toolbar; operations are where you need them.

---

### 1.4 Unified "Now Playing" Panel

**Current State:**
- Player controls, waveform, and annotation controls spread across interface
- Must scroll in Annotations tab to see waveform when adding annotations

**Improvement Ideas:**

1. **Persistent Now Playing Section:**
   - Always-visible compact panel at top or bottom
   - Shows: Thumbnail waveform, current time, play/pause, quick annotation button
   - Could be collapsible/expandable
   - Accessible from any tab without switching

2. **Quick Annotation Entry:**
   - Small text box in Now Playing panel: "Type note + Enter to annotate at current position"
   - Reduces tab switching during review workflow

**Why:** Keeps critical playback and annotation functions always accessible, reducing tab switching.

---

### 1.5 Visual Hierarchy & Clutter Reduction ✅ **IMPLEMENTED** (Collapsible Sections, Toolbar Simplification)

**Current State:**
- Toolbar has many controls (Undo/Redo, Undo limit spinner, Auto-switch checkbox)
- Fingerprinting section takes significant space in Library tab
- Many buttons and controls compete for attention

**Improvement Ideas:**

1. **Collapsible Sections:** ✅ **IMPLEMENTED**
   - Fingerprinting section should be collapsible accordion
   - "Advanced Settings" section for less-common controls
   - Expanded/collapsed state persisted in settings

2. **Toolbar Simplification:** ✅ **IMPLEMENTED**
   - Move Undo Limit spinner to Preferences dialog

3. **Status Bar Improvements:** ✅ **IMPLEMENTED** (Enhanced Statistics)
   - ✅ Show more context: "12 files | 5 reviewed | 3 without names | 2 best takes | 1 partial take"
   - ✅ Automatically updates when files are marked, named, or reviewed
   - ✅ Comprehensive file statistics at a glance
   
**Future Enhancements:**
   - 💡 Show current operation progress (waveform generation, fingerprinting)
   - 💡 Clickable status items to filter/navigate

**Why:** Reduces cognitive load for new users; power users can enable advanced features.

---

## 2. Workflow Improvements

### 2.1 Batch Operations ✅ **IMPLEMENTED** (Multi-Select)

**Current State:**
- Batch rename exists
- WAV→MP3 conversion exists
- Most operations are one-at-a-time

**Improvement Ideas:**

1. **Multi-Select Operations:**
   - Allow Ctrl+Click / Shift+Click in Library table to select multiple files
   - Batch set provided name (e.g., all variations of "Song Title - Take 1, Take 2...")
   - Batch mark as Best/Partial
   - Batch export clips
   - Batch generate fingerprints for selected files only
   - Batch delete files

2. **Templates & Presets:**
   - Save annotation templates (e.g., "Timing issue", "Good energy", "Needs work")
   - Quick-insert template annotations with one click

3. **Smart Batch Rename Patterns:**
   - Pattern: `{date}_{number}_{name}.{ext}`
   - Pattern: `{number}_{song}_{take}.{ext}`
   - Pattern: `{band}_{song}_{take}.{ext}`
   - Renaming should still follow the best take and partial take naming
   - Preview before applying
   - Undo batch rename as single operation

**Why:** Reduces repetitive actions when processing large practice sessions.

---

### 2.2 Improved Auto-Labeling Workflow ✅ **IMPLEMENTED**

**Current State:**
- Auto-labeling with preview, confidence scores, and selective application implemented
- Visual preview in Library table with color highlighting
- Individual checkboxes for selective application

**Implemented Features:**

1. **Preview Mode:** ✅
   - Show suggested names in Library table with different color/icon (light yellow background)
   - Confidence score displayed for each suggestion (color-coded by confidence level)
   - Suggestions default to selected, allowing easy deselection

2. **Partial Application:** ✅
   - Checkboxes next to each suggestion for selective application
   - Apply only selected suggestions via "Apply Selected" button
   - "Select All ≥X% confidence" button with adjustable confidence threshold slider
   - Confidence threshold control (0-100%) to filter suggestions

3. **Multi-Algorithm Consensus:**
   - 💡 Run many algorithms, show when they agree (future enhancement)
   - 💡 Higher confidence when multiple algorithms agree (future enhancement)
   - 💡 Warning when algorithms disagree (future enhancement)
   - 💡 Allow the user to specify which algorithms to use at one time (future enhancement)

**Why:** Makes auto-labeling less all-or-nothing; builds trust through transparency.

---

### 2.3 Session Management ✅ **IMPLEMENTED** (Reviewed Tracking, Recent Folders)

**Current State:**
- Each practice folder is independent
- No concept of "current session" or work-in-progress

**Improvement Ideas:**

1. **Session State:** ✅ **IMPLEMENTED**
   - Remember which files reviewed (checkbox: "Reviewed")
   - Save playback position per file
   - "Resume last session" on startup
   - Show progress: "Reviewed 8 of 15 songs"

2. **Recent Folders:** ✅ **IMPLEMENTED**
   - Quick access menu: "Recent practice folders"
   - Pin favorite folders to top (accessible via submenu)
   - Show last modified date (shown in tooltip)

3. **Workspace Layouts:**
   - Save tab positions, splitter sizes, visible columns
   - "Band practice layout" vs "Solo review layout"
   - Quick switch between layouts

**Why:** Supports the weekly review workflow; reduces setup time when returning to work.

---

### 2.4 Annotation Enhancements ✅ **IMPLEMENTED** (Categories/Tags)

**Current State:**
- Can add point annotations and clip annotations
- Can mark as "important"
- Export to text file
- Categories/tags system with four predefined categories
- Color-coded category badges in annotation table
- Category filtering

**Implemented Features:**

1. **Annotation Categories:** ✅
   - Four predefined categories: ⏱️ Timing, ⚡ Energy, 🎵 Harmony, 📊 Dynamics
   - Quick-access category buttons in Annotations tab
   - Filter by category in table via dropdown
   - Color-coded category badges (unique color per category)
   - Category column in annotation table with icons and labels
   - Categories persist in metadata and included in exports

**Future Enhancement Ideas:**

2. **Annotation Linking:**
   - 💡 Link annotation to similar moment in another take
   - 💡 "Compare with Take 2 at 1:30" button
   - 💡 Visual connection on waveform

3. **Timestamp Formats:**
   - 💡 Show timestamp in measures/beats if tempo known
   - 💡 "Measure 2, Bar 4" as well as the time "2:15"
   - 💡 Would require tempo/structure input (note: the "sections" specification in the meta data is the "structure" of the song, verse, verse2, chorus, prechorus, etc...)

4. **Annotation Export Formats:**
   - 💡 Export to PDF
   - 💡 Export to HTML with embedded player

**Why:** Annotations are core feature; making them more powerful enhances the review process.

---

### 2.5 Cloud Sync Improvements

**Current State:**
- Manual sync with Google Drive
- Version-based conflict detection
- Preview changes before applying

**Improvement Ideas:**

1. **Auto-Sync Mode:**
   - Checkbox: "Auto-sync when files change"
   - Show sync status icon (synced, syncing, conflicts)

2. **Conflict Resolution UI:**
   - Side-by-side diff view for conflicting annotations
   - "Keep mine / Keep theirs / Merge" options
   - Preview merged result

3. **Sync History:**
   - Timeline view of all sync operations
   - Rollback to previous sync state
   - Show who uploaded what when

4. **Selective Sync Rules:**
   - "Never sync files larger than 100MB"
   - "Only sync my annotation files"
   - "Auto-download Best Takes only"

5. **Alternative Cloud Providers:**
   - Dropbox support
   - OneDrive support
   - Generic WebDAV support
   - Self-hosted options (Nextcloud)

**Why:** Reduces friction in band collaboration; makes sync more automatic and reliable.

---

## 3. Practice-Focused Features

### 3.1 Practice Goals & Tracking ✅ **IMPLEMENTED** (Practice Statistics Dashboard)

**Current State:**
- Practice statistics tracking implemented
- Session history and song practice metrics available
- Accessible via Help menu and Ctrl+Shift+S shortcut

**Implemented Features:**

1. **Practice Statistics:**
   - ✅ Total practice time across all sessions
   - ✅ Current session duration tracking
   - ✅ Most practiced songs (top 5) with play count and last played date
   - ✅ Least practiced songs (bottom 5) with play count and last played date
   - ✅ Practice consistency metric (average days between sessions)
   - ✅ Recent sessions list (last 10) with date, duration, folder, and files reviewed
   - ✅ Automatic session tracking when changing folders or closing application
   - ✅ Per-file playback time tracking

**Future Enhancements:**

2. **Practice Goals:**
   - 💡 Set weekly/monthly practice time goals
   - 💡 Track goal progress with visual indicators
   - 💡 Notifications when goals are met or missed
   - 💡 Per-song practice goals (e.g., "Practice this song 5 times this week")

**Why:** Transforms tool from passive review to active practice management; motivates consistent practice.

---

### 3.2 Setlist Builder

**Current State:**
- No setlist concept
- Can mark Best Takes but no organization for performance

**Improvement Ideas:**

1. **Setlist Management:**
   - Create named setlists: "Summer Tour 2024"
   - Drag Best Takes into setlist order
   - Show total duration
   - Export setlist to print/PDF

2. **Setlist Preparation:**
   - Highlight songs in setlist in file tree
   - "Practice mode": Play only setlist songs in order
   - Review all annotations for setlist songs
   - Check: All setlist songs have Best Take?
   - Check: All setlist songs need to be Reference Library?

3. **Performance Notes:**
   - Per-setlist notes: "Key change in Song X"
   - BPM reference
   - Tuning notes
   - Gear requirements

**Why:** Bridges practice and performance; helps bands prepare for shows.

---

### 3.3 Tempo & Metronome Integration

**Current State:**
- No tempo awareness
- PolyRhythmMetronome is separate app

**Improvement Ideas:**

1. **Tempo Detection:**
   - Auto-detect BPM of recordings
   - Manual BPM entry per song
   - Show tempo on waveform (measure markers)

2. **Tempo Analysis:**
   - Detect tempo drift during song
   - Visualize tempo changes as overlay

3. **Click Track Sync:**
   - Play metronome alongside recording
   - Adjust click tempo to match recording
   - Export recording with click mixed in


**Why:** Timing is critical for bands; integrated tempo tools aid practice.

---

### 3.4 Looping & Practice Sections ✅ **IMPLEMENTED** (A-B Loop Markers, Playback Speed)

**Current State:**
- A-B loop markers allow setting specific practice sections
- Playback speed control (0.5x to 2.0x) for slow practice
- Loop markers saved per song

**Implemented Features:**

1. **Section Looping:**
   - ✅ Set A-B loop points on waveform with keyboard shortcuts (L, Shift+L)
   - ✅ Loop specific section (verse, chorus, bridge)
   - ✅ Visual markers on waveform (cyan "A" and "B" labels)
   - ✅ Save loop points per song in `.loop_markers.json`

2. **Slow Playback:**
   - ✅ Playback speed slider (0.5x to 2.0x)
   - ⚠️ Uses Qt's native speed control (pitch changes with speed - pitch preservation not yet implemented)
   - ✅ Useful for learning fast passages

**Future Enhancements:**

3. **Practice Marks:**
   - 💡 Mark "trouble spots" on waveform
   - 💡 "Focus practice" mode: Play only trouble spots in loop
   - 💡 Countdown before loop starts
   - 💡 Configurable loop count

4. **Multi-Take Loop Comparison:**
   - 💡 Loop same section across multiple takes simultaneously
   - 💡 Quickly A/B compare different performances
   - 💡 Vote on best version of specific section

5. **Pitch-Preserved Time Stretching:**
   - 💡 Maintain pitch when slowing down playback (requires audio processing library like pydub or librosa)
   - 💡 More natural sound for slow practice

**Why:** Targeted practice on difficult sections improves faster than full run-throughs.

---

### 3.6 Comparison & Reference Tools

**Current State:**
- Fingerprinting for identification
- Can play files one at a time

**Improvement Ideas:**

1. **Reference Library:**
   - Import original recordings of songs
   - Mark files as "Reference" vs "Practice"
   - Quick switch: "Listen to original"

2. **Multi-Track View:**
   - If band records individual instruments
     - the band doesnt currently recording individual instruments. How would you recommend this be handled to make it effective for you.
   - Show all tracks aligned
   - Mute/solo individual tracks
   - See who made the mistake

**Why:** Learning by comparison is powerful; helps identify exactly what needs improvement.

---

### 3.7 Export & Sharing for Practice ✅ **IMPLEMENTED** (Best Takes Package Export)

**Current State:**
- Export audio with boost
- Export annotations to text
- Sync to Google Drive
- Export Best Takes Package as ZIP

**Implemented Features:**

1. **Best Takes Package Export:** ✅ **IMPLEMENTED**
   - Export folder as ZIP with:
     - All Best Take audio files
     - All annotation files
     - Summary document (SUMMARY.txt) with song list and annotations
   - Accessible via File menu → "Export Best Takes Package…"
   - Progress dialog during export
   - Organized structure within ZIP (audio/, annotations/ folders)

**Future Enhancement Ideas:**

2. **Practice Mix Exports:**
   - 💡 "Export with click track"
   - 💡 Automatic normalization across tracks
 
**Why:** Makes it easier to take work out of the app and into practice situations.

---

## 4. User Interface Modernization

### 4.1 Visual Design Updates ✅ **IMPLEMENTED** (Dark Mode)

**Current State:**
- Functional Qt-based interface
- Uses consistent color scheme
- Dark mode theme available

**Improvement Ideas:**

1. **Modern UI Framework:**
   - Consider Qt Quick/QML for more modern look
   - Smoother animations and transitions
   - Custom-styled controls

2. **Dark Mode:** ✅ **IMPLEMENTED**
   - Full dark theme option (light/dark selection in Preferences)
   - Theme applies to all UI elements and waveforms
   - Separate waveform colors for dark mode
   - 💡 Auto-switch based on OS preference (future enhancement)

3. **Customizable Themes:**
   - User-selectable color schemes
   - Band-specific branding (logo, colors)
   - High-contrast accessibility mode

4. **Icons & Visual Feedback:**
   - Modern icon set (Feather, Material Design, etc.)
   - Hover animations
   - Visual feedback for all actions
   - Progress indicators for long operations

**Why:** Professional appearance builds trust; modern UI feels more polished.

---

### 4.3 Accessibility Improvements

**Current State:**
- Keyboard shortcuts exist but incomplete
- No screen reader optimization
- Visual interface only

**Improvement Ideas:**

1. **Screen Reader Support:**
   - Proper ARIA labels for all controls
   - Keyboard-navigable waveform
   - Audio feedback for annotations

2. **Visual Accessibility:**
   - Scalable UI (zoom interface)
   - High-contrast mode
   - Colorblind-friendly palette options
   - Larger click targets for touchscreens

3. **Alternative Input:**
   - MIDI controller support (jog wheel for scrubbing)
   - Game controller support (Xbox/PS controller)
   - Foot pedal support (hands-free play/pause)

**Why:** Musicians with disabilities should have full access to practice tools.

---

## 5. Performance & Technical Improvements

### 5.1 Faster Startup & Loading

**Current State:**
- Waveform generation can be slow
- Fingerprinting is CPU-intensive
- Auto-generation at boot or folder selection

**Improvement Ideas:**

1. **Lazy Loading:**
   - Don't generate waveforms until needed
   - Generate only visible portion first
   - Background generation for rest

2. **Incremental Processing:**
   - Process new files only
   - Skip already-fingerprinted files
   - Show progress: "Processing 3 of 15 new files"

3. **Caching Strategy:**
   - More aggressive caching
   - Cache fingerprints at multiple thresholds
   - LRU eviction for old cache entries

4. **Parallel Processing:**
   - Multi-threaded waveform generation
   - GPU acceleration for fingerprinting (if CUDA/OpenCL available)

**Why:** Faster tool = used more often; reduces waiting time during workflow.

---

### 5.2 Large Library Support

**Current State:**
- Works well with dozens of files
- Hundreds of files might cause slowdown

**Improvement Ideas:**

1. **Virtual Scrolling:**
   - Render only visible table rows
   - Dramatically improves performance with 1000+ files

2. **Database Backend:** (Low Priority)
   - SQLite for annotations and metadata
   - Full-text search across all annotations
   - Complex queries: "All timing issues from last month"
   - How would SQLite be able to be multi-user mergable? i.e. how do current metadata files fit in this new SQLite version

3. **Folder Indexing:**
   - Background indexer for entire library
   - Global search across all practice folders
   - "Find all recordings of Song X"

**Why:** Bands with years of recordings need performant tools for large libraries.

---



## 6. Advanced Features

### 6.1 Advanced Audio Analysis

**Improvement Ideas:**

1. **Spectral Analysis:**
   - Spectrogram view alongside waveform
   - Identify frequency issues
   - EQ suggestions

**Why:** Visual feedback helps musicians understand technical aspects of recordings.

---

## 7. Summary of High-Impact Ideas

Based on potential impact vs. implementation effort, here are top recommendations:

### Quick Wins (High Impact, Lower Effort):
1. ✅ **Keyboard shortcuts** for play/pause, skip, annotate (Section 1.1) - **IMPLEMENTED**
2. ✅ **Quick filter box** for file tree (Section 1.2) - **IMPLEMENTED**
3. ✅ **Context menu enhancements** (Section 1.3) - **IMPLEMENTED**
4. ✅ **Collapsible fingerprinting section** (Section 1.5) - **IMPLEMENTED**
5. ✅ **Session state** (remember reviewed files, resume position) (Section 2.3) - **IMPLEMENTED**
6. ✅ **Recent folders menu** for quick folder access (Section 2.3.2) - **IMPLEMENTED**
7. ✅ **Toolbar simplification** (move undo limit to preferences) (Section 1.5.2) - **IMPLEMENTED**
8. ✅ **Dark mode theme** for better visibility in low-light conditions (Section 4.1.2) - **IMPLEMENTED**

### Medium-Term Improvements (High Impact, Medium Effort):
1. ✅ **Multi-select batch operations** (Section 2.1) - **IMPLEMENTED**
2. ✅ **A-B loop sections** for targeted practice (Section 3.4) - **IMPLEMENTED**
3. ✅ **Practice statistics dashboard** (Section 3.1) - **IMPLEMENTED**
4. ✅ **Improved auto-labeling preview** (Section 2.2) - **IMPLEMENTED**
5. ✅ **Annotation categories/tags** (Section 2.4) - **IMPLEMENTED**
6. ✅ **Export best takes package** for easy sharing/archiving (Section 3.7.2) - **IMPLEMENTED**

### Long-Term Features (High Impact, Higher Effort):
1. **Setlist builder** for performance prep (Section 3.2)
2. **Side-by-side comparison** tool (Section 3.6)
4. **Tempo detection & metronome integration** (Section 3.3)

### Experimental/Advanced (Interesting, Needs Research):
3. **Multi-track view** for individual instruments (Section 3.6)
4. **MIDI controller support** (Section 4.3)

---

## 10. Conclusion

The AudioBrowser already has a strong foundation for band practice workflow. These ideas focus on:

- **Reducing friction**: Less clicking, more keyboard shortcuts
- **Enhancing collaboration**: Better multi-user features
- **Improving practice**: Tools focused on actual improvement, not just review
- **Scaling**: Support for years of recordings
- **Accessibility**: More ways to interact with the tool

Many of these ideas can be implemented incrementally, enhancing the existing workflow without disrupting current users. The key is maintaining the tool's focus: making weekly band practice review easier and more productive.

The most impactful improvements are those that reduce repetitive actions (keyboard shortcuts, batch operations, quick filters) and those that transform passive review into active practice management (goals, metrics, looping).

---

*This document was created as a brainstorming exercise. Not all ideas are recommended for implementation. Prioritization should be based on user feedback, development resources, and alignment with the project's core mission.*
