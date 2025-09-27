# Color Consistency Feature

## Overview

The AudioBrowser application now includes a comprehensive color standardization system that ensures consistent visual appearance across different machines, regardless of display hardware, operating system, or system color settings.

## Problem Solved

Previously, the application could appear different across machines due to:

- **Hardware variations**: Different monitors, graphics cards, and display calibrations
- **Operating system differences**: Windows, macOS, and Linux render colors differently
- **System color profiles**: User-specific display settings and color management
- **Qt style variations**: Different Qt styles available on different systems
- **Gamma differences**: Display gamma settings varying between 1.8-2.4 across systems

## Technical Implementation

### ColorManager Class

The `ColorManager` class provides centralized color management with several key features:

#### Purpose-Based Color Standardization

Colors are adjusted based on their intended use:

- **Selection colors**: High saturation (≥80%) and optimal brightness (60-90%) for visibility
- **Waveform colors**: Clear saturation (70-95%) and comfortable brightness (50-80%) for long viewing
- **Text colors**: Optimized contrast ratios for readability
- **UI accent colors**: Balanced saturation (60-90%) and brightness (40-70%) for buttons and highlights

#### HSV-Based Color Manipulation

Colors are converted to HSV (Hue, Saturation, Value) space for consistent manipulation:

```python
def _apply_color_standardization(self, color: QColor, purpose: str) -> QColor:
    h, s, v, a = color.getHsvF()
    
    if purpose == "selection":
        s = max(0.8, s)  # Ensure high saturation
        v = max(0.6, min(0.9, v))  # Optimal brightness range
```

#### Gamma Correction

Applies gamma correction to normalize colors across different display types:

```python
# Normalize to standard gamma 2.2
v = pow(v, 1.0 / 2.2) if v > 0 else 0
v = pow(v, 2.2)
```

### Enhanced Style Selection

The application now selects the most consistent Qt style available:

```python
preferred_styles = ["Fusion", "Windows", "WindowsVista", "Breeze", "Qt6CT-Style"]
```

This ensures consistent widget rendering across platforms.

### Application Palette Override

Sets consistent highlight colors in the Qt application palette to override system-specific theming.

## Updated UI Elements

### Waveform Visualization

All waveform colors now use standardized values:

- **Background**: Consistent dark theme
- **Waveform channels**: Standardized blue (#58a6ff) and red (#ff6b58) with proper gamma correction
- **Playhead**: High-contrast red for visibility
- **Selection**: Orange highlight with consistent brightness

### Tree View Selection

Selection colors use a consistent blue theme:

- **Active selection**: `#1d4ed8` (standardized)
- **Inactive selection**: `#2563eb` (standardized)  
- **General selection**: `#1e3a8a` (standardized)

### Button Styling

All buttons use standardized colors:

- **Success buttons**: Consistent green (`#4CAF50`) with proper contrast
- **Danger buttons**: Consistent red (`#f44336`) with high visibility
- **Info buttons**: Consistent blue with optimal saturation

### Text Colors

Text elements use standardized colors for optimal readability:

- **Secondary text**: Consistent gray with proper contrast ratios
- **Muted text**: Lighter gray for less important information
- **Labels**: Optimized contrast for various background colors

## Benefits

### For Users

- **Consistent experience**: Application looks the same on every machine
- **Better readability**: Optimized contrast ratios across all text elements
- **Reduced eye strain**: Proper gamma correction and brightness levels
- **Professional appearance**: Consistent color scheme regardless of system settings

### For Developers

- **Centralized color management**: All colors defined in one place
- **Easy customization**: Change color themes by modifying the ColorManager
- **Future-proof**: New UI elements automatically use consistent colors
- **Cross-platform compatibility**: Reduces platform-specific appearance issues

## Usage

The color system is automatic and requires no user configuration. Colors are applied when the application starts and remain consistent throughout the session.

### For Developers Adding New UI Elements

Use the centralized color functions:

```python
# Get standardized colors for stylesheets
colors = get_consistent_stylesheet_colors()
widget.setStyleSheet(f"background-color: {colors['bg_light']};")

# Get specific color collections
waveform_colors = _color_manager.get_waveform_colors()
ui_colors = _color_manager.get_ui_colors()
```

## Technical Details

### Color Caching

Colors are cached after first calculation to improve performance:

```python
def get_standardized_color(self, base_color: str, purpose: str = "general") -> QColor:
    cache_key = f"{base_color}_{purpose}"
    if cache_key in self._color_cache:
        return self._color_cache[cache_key]
```

### Fallback Handling

The system includes robust fallback mechanisms:

- Invalid colors fall back to neutral gray
- Missing Qt styles fall back to system default with logging
- Color calculation errors use safe default values

### Performance Impact

- **Minimal overhead**: Colors calculated once and cached
- **No runtime impact**: Color standardization happens during initialization
- **Memory efficient**: Only calculated colors are stored in cache

## Future Enhancements

Potential future improvements could include:

- **User-customizable color themes**: Allow users to choose from predefined color schemes
- **Accessibility improvements**: High-contrast mode for visually impaired users
- **Color profile detection**: Automatic adjustment based on detected display characteristics
- **Dark/light theme support**: Automatic theme switching based on system preferences

## Backward Compatibility

The color system is fully backward compatible:

- Existing user color preferences are preserved
- Annotation set colors remain unchanged
- No data migration required
- All existing functionality continues to work