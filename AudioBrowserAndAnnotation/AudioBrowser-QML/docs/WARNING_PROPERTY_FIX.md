# Warning Property Fix - QML Compilation Error

## Problem Summary

The AudioBrowser-QML application failed to load with two additional QML property errors after the initial info property fix:

```
Type LibraryTab unavailable
file:///c:/Work/ToolDev/BandTools/AudioBrowserAndAnnotation/AudioBrowser-QML/qml/tabs/LibraryTab.qml:124:21: Cannot assign to non-existent property "warning"

Type PracticeGoalsDialog unavailable
file:///c:/Work/ToolDev/BandTools/AudioBrowserAndAnnotation/AudioBrowser-QML/qml/dialogs/PracticeGoalsDialog.qml:186:45: Cannot assign to non-existent property "destructive"
```

## Root Causes

### Error 1: Missing Warning Property in StyledButton.qml

**Issue**: LibraryTab.qml used `warning: true` on a StyledButton component (line 124), but StyledButton didn't have a `warning` property defined.

**Location**: `qml/components/StyledButton.qml`

```qml
// ❌ BEFORE (lines 31-35)
// Custom properties
property bool primary: false
property bool danger: false
property bool success: false
property bool info: false
// Missing: property bool warning: false
```

**Usage in LibraryTab.qml (Line 124)**:
```qml
StyledButton {
    text: "Convert WAV→MP3"
    warning: true  // ← Property doesn't exist
    enabled: fileListModel.count() > 0
    onClicked: {
        // Convert audio files
    }
}
```

### Error 2: Typo Using "destructive" Instead of "danger"

**Issue**: PracticeGoalsDialog.qml used `destructive: true` instead of the correct property name `danger: true`.

**Location**: `qml/dialogs/PracticeGoalsDialog.qml`

```qml
// ❌ BEFORE (line 186)
StyledButton {
    Layout.alignment: Qt.AlignRight
    text: "Delete Goal"
    destructive: true  // ← Should be "danger: true"
    visible: model.status === "complete" || model.status === "expired"
    onClicked: {
        deleteGoal(model.category, model.goalId)
    }
}
```

## Solutions Implemented

### Fix 1: Add Warning Property with Full Styling Support

**Modified File**: `qml/components/StyledButton.qml`

Added the warning property declaration:
```qml
// ✅ AFTER (lines 31-36)
// Custom properties
property bool primary: false
property bool danger: false
property bool success: false
property bool info: false
property bool warning: false  // ← Added
```

Integrated warning property in all color/style logic:

1. **Text Color** (Line 56):
```qml
if (primary || danger || success || info || warning) {  // ← Added warning
    return "#ffffff"
}
```

2. **Background - Pressed State** (Line 77):
```qml
if (warning) return Qt.darker(Theme.accentWarning, 1.3)  // ← Added
```

3. **Background - Hover State** (Line 85):
```qml
if (warning) return Qt.lighter(Theme.accentWarning, 1.1)  // ← Added
```

4. **Background - Normal State** (Line 92):
```qml
if (warning) return Theme.accentWarning  // ← Added
```

5. **Border Color** (Line 104):
```qml
if (warning) return Theme.accentWarning  // ← Added
```

6. **Border Width** (Line 109):
```qml
border.width: primary || danger || success || info || warning ? 0 : 1  // ← Added warning
```

### Fix 2: Correct Property Name in PracticeGoalsDialog

**Modified File**: `qml/dialogs/PracticeGoalsDialog.qml`

Changed the typo from `destructive` to the correct `danger` property:
```qml
// ✅ AFTER (line 186)
StyledButton {
    Layout.alignment: Qt.AlignRight
    text: "Delete Goal"
    danger: true  // ← Changed from "destructive: true"
    visible: model.status === "complete" || model.status === "expired"
    onClicked: {
        deleteGoal(model.category, model.goalId)
    }
}
```

## Visual Result

### Warning Button Styling

Buttons with `warning: true` now display with:
- **Background**: Yellow/Orange (#fbbf24 - Theme.accentWarning)
- **Text**: White (#ffffff)
- **Border**: None (consistent with other accent buttons)
- **Hover**: Slightly lighter yellow/orange
- **Pressed**: Slightly darker yellow/orange

This is appropriate for actions that require user caution, such as file format conversions.

### Button Variant Summary

| Variant | Color | Hex | Use Case |
|---------|-------|-----|----------|
| Default | Gray | Theme-dependent | Standard actions |
| Primary | Blue | #2563eb | Main actions |
| Success | Green | #4ade80 | Positive actions |
| Danger | Red | #ef5350 | Destructive actions |
| Info | Light Blue | #42a5f5 | Informational actions |
| **Warning** ✨ | **Yellow/Orange** | **#fbbf24** | **Cautionary actions** |

## Files Modified

1. `qml/components/StyledButton.qml` - Added warning property with full styling
2. `qml/dialogs/PracticeGoalsDialog.qml` - Fixed property name typo

## Verification

### Automated Validation

Run validation to confirm fixes:
```bash
cd AudioBrowserAndAnnotation/AudioBrowser-QML
QT_QPA_PLATFORM=offscreen python3 test_qml_syntax.py
```

Expected output:
```
Testing: qml/components/StyledButton.qml
  ✓ PASSED

Testing: qml/tabs/LibraryTab.qml
  ✓ PASSED

Testing: qml/dialogs/PracticeGoalsDialog.qml
  ✓ PASSED

============================================================
✓ All QML files passed syntax check!
============================================================
```

### Manual Verification

The application should now:
1. Start without QML compilation errors related to "warning" or "destructive" properties
2. Display the Library tab with the "Convert WAV→MP3" button styled in yellow/orange
3. Display the Practice Goals dialog with the "Delete Goal" button styled in red (danger)

## Impact

- ✅ Application loads without property-related QML compilation errors
- ✅ Warning-styled button (yellow/orange) available for cautionary actions
- ✅ All button variants work correctly with proper semantic naming
- ✅ No breaking changes to existing code
- ✅ Consistent button styling across the application

## Related Documentation

- [QML_COMPILATION_FIX.md](QML_COMPILATION_FIX.md) - Original info property fix
- [STYLED_BUTTON_VARIANTS.md](STYLED_BUTTON_VARIANTS.md) - Complete button variant documentation
- [../qml/components/StyledButton.qml](../qml/components/StyledButton.qml) - Component source code
- [../qml/styles/Theme.qml](../qml/styles/Theme.qml) - Theme color definitions
