# StyledButton Component Variants

## Overview

The StyledButton component supports multiple visual variants through boolean properties. Each variant uses a specific accent color from the Theme singleton.

## Available Variants

### Default (No Variant)
```qml
StyledButton {
    text: "Default Button"
}
```
- **Background**: Theme.backgroundLight (gray)
- **Text**: Theme.textSecondary (dimmed)
- **Border**: 1px, Theme.borderColor
- **Use Case**: Standard actions, less emphasis

### Primary Variant
```qml
StyledButton {
    text: "Primary Action"
    primary: true
}
```
- **Background**: #2563eb (royal blue)
- **Text**: White (#ffffff)
- **Border**: None
- **Use Case**: Main actions, call-to-action buttons

### Success Variant
```qml
StyledButton {
    text: "Success Action"
    success: true
}
```
- **Background**: #4ade80 (green)
- **Text**: White (#ffffff)
- **Border**: None
- **Use Case**: Positive actions, confirmation, completion

### Danger Variant
```qml
StyledButton {
    text: "Delete"
    danger: true
}
```
- **Background**: #ef5350 (red)
- **Text**: White (#ffffff)
- **Border**: None
- **Use Case**: Destructive actions, warnings, deletion

### Info Variant ✨ **NEW**
```qml
StyledButton {
    text: "More Info"
    info: true
}
```
- **Background**: #42a5f5 (light blue)
- **Text**: White (#ffffff)
- **Border**: None
- **Use Case**: Informational actions, help buttons, feature discovery

## Interactive States

All variants support hover and pressed states with automatic color adjustments:

### Hover State
- Background becomes 10% lighter: `Qt.lighter(color, 1.1)`
- Smooth color transition (150ms)
- Cursor changes to pointing hand

### Pressed State
- Background becomes 30% darker: `Qt.darker(color, 1.3)`
- Immediate visual feedback
- Text remains white

### Disabled State
- Background: Theme.backgroundMedium (gray)
- Text: Theme.textMuted (very dimmed)
- Border: Theme.borderColor
- Cursor changes to forbidden symbol

## Color Reference

| Variant   | Color Name         | Hex Code  | RGB Values       |
|-----------|-------------------|-----------|------------------|
| Primary   | accentPrimary     | #2563eb   | rgb(37, 99, 235) |
| Success   | accentSuccess     | #4ade80   | rgb(74, 222, 128)|
| Danger    | accentDanger      | #ef5350   | rgb(239, 83, 80) |
| Info      | accentInfo        | #42a5f5   | rgb(66, 165, 245)|
| Default   | backgroundLight   | (varies)  | Theme dependent  |

## Usage Examples in AudioBrowser-QML

### LibraryTab.qml

1. **Batch Operations**:
   ```qml
   StyledButton {
       text: "Batch Rename"
       info: true
       enabled: fileListModel.count() > 0
   }
   ```

2. **Filter Toggles**:
   ```qml
   StyledButton {
       text: filterBestTakes ? "★ Best Takes ✓" : "★ Best Takes"
       info: filterBestTakes
   }
   ```

3. **Feature Discovery**:
   ```qml
   StyledButton {
       text: "📊 Practice Stats"
       info: true
   }
   ```

## Design Rationale

### Why Info Variant?

The `info` variant was added to provide a distinct visual style for:
- **Informational actions** - Buttons that provide information rather than modify data
- **Feature discovery** - Help users discover less-critical but useful features
- **Non-destructive operations** - Actions that are safe to explore
- **Visual hierarchy** - Distinguish between primary actions and secondary information

### Color Choice

Light blue (#42a5f5) was chosen because:
- Clearly distinct from primary blue (#2563eb - darker, more saturated)
- Universally associated with information and communication
- Good contrast with white text (WCAG AA compliant)
- Visually harmonious with other accent colors

## Accessibility

All button variants meet WCAG 2.1 Level AA contrast requirements:
- **Accent buttons** (primary, success, danger, info): White text on colored background
- **Default buttons**: Dark text on light background in light theme, light text on dark background in dark theme
- **Disabled buttons**: Reduced contrast to indicate inactive state

## Implementation Details

The info property is implemented identically to primary, danger, and success:

```qml
Button {
    property bool primary: false
    property bool danger: false
    property bool success: false
    property bool info: false  // ✨ NEW
    
    background: Rectangle {
        color: {
            // ... other logic ...
            if (info) return Theme.accentInfo
            // ... fallback ...
        }
    }
}
```

All color logic checks follow the same pattern:
- `if (primary || danger || success || info)` - for text color
- Individual `if (info)` checks for each state (normal, hover, pressed)
- Border width exclusion: `primary || danger || success || info ? 0 : 1`

## Testing

To test the info variant:
1. Run the application: `python3 main.py`
2. Navigate to the Library tab
3. Look for info-styled buttons (light blue background):
   - "Batch Rename"
   - "★ Best Takes" (when active)
   - "◐ Partial Takes" (when active)
   - "📊 Practice Stats"
   - "🎯 Practice Goals"
   - "🎵 Setlist Builder"
4. Hover over buttons to see lighter blue
5. Click to see darker blue pressed state

## Related Documentation

- [QML_COMPILATION_FIX.md](QML_COMPILATION_FIX.md) - Implementation details of the info property fix
- [../qml/components/StyledButton.qml](../qml/components/StyledButton.qml) - Component source code
- [../qml/styles/Theme.qml](../qml/styles/Theme.qml) - Theme color definitions
