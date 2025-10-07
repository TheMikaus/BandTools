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
| **Ctrl+4** | Folder Notes Tab | Switch to Folder Notes tab |

## Interface

| Shortcut | Action | Description |
|----------|--------|-------------|
| **Ctrl+T** | Toggle Theme | Switch between light and dark themes |

## Navigation (Extended)

| Shortcut | Action | Description |
|----------|--------|-------------|
| **Left Arrow** | Seek Backward | Skip backward 5 seconds |
| **Right Arrow** | Seek Forward | Skip forward 5 seconds |

## Annotations

| Shortcut | Action | Description |
|----------|--------|-------------|
| **Ctrl+A** | Add Annotation | Create new annotation at current playback position |

## Clips

| Shortcut | Action | Description |
|----------|--------|-------------|
| **[** | Set Clip Start | Set clip start marker at current playback position |
| **]** | Set Clip End | Set clip end marker at current playback position |

**Clip Marker Workflow:**
1. Play audio and press `[` at desired clip start position
2. Continue playing and press `]` at desired clip end position
3. Clip dialog automatically opens with both timestamps pre-filled
4. Fill in name and notes, then click OK to create the clip

## Folder Notes

| Shortcut | Action | Description |
|----------|--------|-------------|
| **Ctrl+S** | Save Notes | Manually save folder notes (when auto-save is off) |

## Context Menu (Right-Click on Files)

The following actions are available via right-click context menu:

| Action | Description |
|--------|-------------|
| **Play** | Load and play the selected file |
| **Add Annotation...** | Switch to Annotations tab for quick annotation |
| **Create Clip...** | Switch to Clips tab for quick clip creation |
| **Show in Explorer** | Open file location in system file manager |
| **Copy Path** | Copy file path to clipboard |
| **Properties** | Show file properties dialog |

## Future Shortcuts (Planned)

These shortcuts will be implemented in future phases:

| Shortcut | Action | Description |
|----------|--------|-------------|
| **Ctrl+Left** | Previous File | Play previous file in list |
| **Ctrl+Right** | Next File | Play next file in list |
| **Ctrl+O** | Open Directory | Open directory picker dialog |
| **Ctrl+F** | Find Files | Focus file filter field |
| **Ctrl+L** | Open Location | Show current file in file manager |
| **Delete** | Delete File | Delete selected file (with confirmation) |
| **F2** | Rename File | Quick rename dialog for selected file |
| **F11** | Fullscreen | Toggle fullscreen mode |

## Notes

- Shortcuts are case-insensitive
- Ctrl on Windows/Linux, Cmd on macOS (handled automatically by Qt)
- Shortcuts work globally within the application window
- Some shortcuts may be disabled when certain dialogs are open
- **Context-aware shortcuts**: Space, Ctrl+A, [, and ] are disabled when text fields have focus to prevent accidental triggering while typing

## Customization

Keyboard shortcuts can be customized in future versions through the preferences dialog (Phase 2+ feature).

---

*Last updated: Phase 7 Implementation*
