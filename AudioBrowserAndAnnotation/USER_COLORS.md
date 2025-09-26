# User Color Consistency Feature

## Overview
This feature ensures that annotation sets created by the same user have consistent colors across different practices and sessions.

## How It Works

### User Color Assignment
- Each user gets a unique, consistent color that persists across sessions
- Colors are stored in `.user_colors.json` in the audio folder
- 12 predefined colors are available for the first 12 users
- Additional users get hash-based colors generated from their username

### Color Rules
1. **User-named annotation sets**: When creating a set with your username, the system automatically assigns your consistent user color
2. **Custom-named annotation sets**: When creating sets with custom names, you can choose any color via the color picker dialog
3. **External annotation sets**: Sets from other users (shown as `[Username] Set Name`) maintain the original user's consistent color

### Files Created
- `.user_colors.json`: Global mapping of usernames to colors (shared across all practices)
- `.audio_notes_<username>.json`: Individual user annotation files

## Benefits
- ✅ Visual consistency: Same user always appears in the same color
- ✅ Easy identification: Quickly distinguish between different users' annotations
- ✅ Automatic assignment: No manual color management required
- ✅ Backwards compatible: Existing annotation sets continue to work
- ✅ Scalable: Supports unlimited users

## Examples

### Scenario 1: Alice creates multiple sets
- Set named "Alice": Gets Alice's consistent color (e.g., green)
- Another set named "Alice": Gets the same green color
- Set named "Best Takes": Alice can choose custom color (e.g., orange)

### Scenario 2: Bob joins the project
- Set named "Bob": Gets Bob's consistent color (e.g., red)  
- Bob's color is different from Alice's color automatically

### Scenario 3: Cross-user visibility
- Alice sees Bob's external set as "[Bob] Set"
- This external set appears in Bob's consistent red color
- Alice immediately knows it's Bob's annotations

## Technical Details
- Uses SHA-256 hashing for secure color generation
- Persistent storage in JSON format
- Thread-safe color assignment
- Graceful fallback for edge cases