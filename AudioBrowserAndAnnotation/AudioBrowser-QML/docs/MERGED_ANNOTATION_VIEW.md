# Merged Annotation View - Multi-User Support

## Overview

The merged annotation view feature allows multiple users to create annotations on the same audio files and view them together in a unified interface. This is useful for collaborative music practice, teaching scenarios, or when reviewing recordings with multiple band members.

**Status**: ✅ Implemented (Phase 11)

## Features

### 1. Multi-User Annotation Support
- Each annotation is tagged with the username of its creator
- Users can be identified by their unique username
- Annotations are stored with user metadata in JSON format

### 2. User Column in Annotations Table
- Annotations table displays a "User" column showing who created each annotation
- Column appears between "Text" and "Important" columns
- Shows username for each annotation (defaults to "default_user")

### 3. User Filter
- Dropdown filter to view annotations from specific users or all users
- Filter options:
  - "All Users" - Shows all annotations regardless of creator
  - Individual usernames - Shows only annotations from that user
- Filter dynamically updates when switching files

### 4. Combined with Existing Filters
- User filter works in combination with:
  - Category filter (timing, energy, harmony, etc.)
  - Important only checkbox
- All filters can be applied simultaneously for precise annotation views

## Usage

### Setting Your Username

Your username is used to tag all annotations you create. To set your username:

1. Open Preferences (File menu or Ctrl+,)
2. Enter your desired username in the "User Name" field
3. Click "Save"

All future annotations will be tagged with this username.

### Viewing Annotations from All Users

By default, the annotation view shows all annotations from all users:

1. Open the Annotations tab
2. The user filter dropdown shows "All Users"
3. All annotations are displayed with their respective creators in the "User" column

### Filtering by Specific User

To view annotations from a specific user:

1. Click the "User:" dropdown in the Annotations tab
2. Select the desired username from the list
3. Only annotations from that user will be displayed

The dropdown automatically populates with all users who have created annotations for the current file.

### Creating Multi-User Annotations

**Scenario: Band practice with multiple members**

1. Guitarist opens audio file and sets username to "guitar_player"
2. Creates annotations: "Solo starts here", "Change to D chord"
3. Drummer opens same file and sets username to "drummer"
4. Creates annotations: "Speed up tempo", "Add cymbal crash"
5. Both can now view all annotations or filter by user

## Technical Implementation

### Backend (Python)

**AnnotationManager** (`backend/annotation_manager.py`):
- `getAllUsers()` - Returns list of unique usernames for current file
- `getAnnotationsForUser(username)` - Returns annotations filtered by user
  - Empty string returns all annotations
  - Specific username returns only that user's annotations

**AnnotationsModel** (`backend/models.py`):
- Added `COL_USER` column (index 3)
- Added `UserRole` for QML access
- Updated `roleNames()` to include 'user' role
- Column count increased to 5

### Frontend (QML)

**AnnotationsTab** (`qml/tabs/AnnotationsTab.qml`):
- User filter ComboBox with dropdown
- `updateUserFilter()` function to populate user list
- Updated `refreshAnnotations()` to apply user filter
- Auto-updates user list when file or annotations change

### Data Storage

Annotations are stored in JSON format with user metadata:

```json
{
  "timestamp_ms": 1500,
  "text": "Great solo here",
  "category": "energy",
  "important": true,
  "color": "#3498db",
  "user": "guitar_player",
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-15T10:30:00"
}
```

## Benefits

### For Individual Users
- Track your own annotations separately
- Review annotations you created over time
- Distinguish your notes from imported/shared annotations

### For Collaborative Practice
- Band members can each annotate the same recording
- View combined feedback from all members
- Filter to see specific member's notes
- Teaching: instructor and student annotations side-by-side

### For Music Education
- Teacher creates annotations for students
- Students add their own observations
- Both can view merged or filtered views
- Helps track learning progress

## Examples

### Example 1: Solo Practice Review
- User "guitarist" practices solo
- Creates annotations marking difficult sections
- Later reviews only their annotations to track progress

### Example 2: Band Rehearsal
- After recording rehearsal, each member reviews:
  - Guitarist filters to see their notes
  - Drummer filters to see their notes
  - Producer views "All Users" for complete picture

### Example 3: Teaching Session
- Teacher "instructor" annotates: "Watch rhythm here"
- Student "learner" annotates: "Need to practice this part"
- Both can switch between views or see merged annotations

## Compatibility

- ✅ Backward compatible with existing annotations
- ✅ Default user is "default_user" for legacy annotations
- ✅ Works with existing import/export features
- ✅ Integrates with all existing annotation features (categories, importance, colors)

## Future Enhancements

Potential future additions:
- Color-code annotations by user
- User-specific annotation colors
- Show user avatar/icon in table
- Export filtered by user
- Annotation statistics per user

## Testing

Run the test suite to verify implementation:

```bash
cd AudioBrowser-QML
python3 test_merged_annotation_syntax.py
```

Tests verify:
- Backend methods exist and work correctly
- Model includes user column
- QML UI has user filter
- Integration between components

## Summary

The merged annotation view brings powerful multi-user collaboration to AudioBrowser-QML:
- ✅ Track annotation creators
- ✅ Filter by user or view all
- ✅ User column in table
- ✅ Seamless integration with existing features
- ✅ Simple, intuitive UI

**Feature Parity**: This completes the partial implementation of merged annotation view from the original AudioBrowser, advancing QML version from 88% to 89% feature parity.

---

**Document Version**: 1.0  
**Last Updated**: January 2025  
**Implementation Phase**: Phase 11  
**Status**: ✅ Complete
