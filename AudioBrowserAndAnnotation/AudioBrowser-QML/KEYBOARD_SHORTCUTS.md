# AudioBrowser QML - Keyboard Shortcuts

This document lists all keyboard shortcuts available in the AudioBrowser QML application.

## Playback Controls

| Shortcut | Action | Description |
|----------|--------|-------------|
| **Space** | Toggle Play/Pause | Play or pause the current audio file |
| **Escape** | Stop | Stop playback and reset to beginning |
| **+** | Volume Up | Increase volume by 5% |
| **-** | Volume Down | Decrease volume by 5% |

## Navigation

| Shortcut | Action | Description |
|----------|--------|-------------|
| **Ctrl+1** | Library Tab | Switch to Library tab |
| **Ctrl+2** | Annotations Tab | Switch to Annotations tab |
| **Ctrl+3** | Clips Tab | Switch to Clips tab |

## Interface

| Shortcut | Action | Description |
|----------|--------|-------------|
| **Ctrl+T** | Toggle Theme | Switch between light and dark themes |

## Future Shortcuts (Planned)

These shortcuts will be implemented in future phases:

| Shortcut | Action | Description |
|----------|--------|-------------|
| **Left Arrow** | Seek Backward | Skip backward 5 seconds |
| **Right Arrow** | Seek Forward | Skip forward 5 seconds |
| **Ctrl+Left** | Previous File | Play previous file in list |
| **Ctrl+Right** | Next File | Play next file in list |
| **Ctrl+O** | Open Directory | Open directory picker dialog |
| **Ctrl+F** | Find Files | Focus file filter field |
| **Ctrl+A** | Add Annotation | Create new annotation at current position |
| **Ctrl+S** | Save | Save current workspace/annotations |
| **F11** | Fullscreen | Toggle fullscreen mode |

## Notes

- Shortcuts are case-insensitive
- Ctrl on Windows/Linux, Cmd on macOS (handled automatically by Qt)
- Shortcuts work globally within the application window
- Some shortcuts may be disabled when certain dialogs are open

## Customization

Keyboard shortcuts can be customized in future versions through the preferences dialog (Phase 2+ feature).

---

*Last updated: Phase 1 Implementation*
