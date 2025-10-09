# UI Changes for Multi-Cloud Sync

## Overview

This document describes the user interface changes made to support multiple cloud storage providers in AudioBrowser-QML.

---

## Main Menu Changes

### Before
```
Edit Menu:
├── ...
├── Google Drive Sync...
└── ...
```

### After
```
Edit Menu:
├── ...
├── Cloud Sync...    <-- CHANGED
└── ...
```

**Change**: Menu item renamed from "Google Drive Sync..." to "Cloud Sync..." to reflect support for multiple providers.

---

## Sync Dialog Changes

### Dialog Title

**Before**: "Google Drive Sync"  
**After**: "Cloud Sync"

### New: Provider Selection Section

A new section has been added at the top of the dialog:

```
┌─────────────────────────────────────────────────────────────┐
│  Cloud Synchronization              Provider: [Dropdown ▼]  │
│                                                               │
│  Dropdown options:                                           │
│  • Google Drive                                              │
│  • Dropbox                                                   │
│  • WebDAV/Nextcloud                                          │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Provider dropdown in top-right corner
- Title changed from "Google Drive Synchronization" to "Cloud Synchronization"
- Dropdown shows all available providers
- Disabled during sync operations
- Selection persists across dialog openings

### Provider-Specific Authentication

The authentication section adapts based on selected provider:

#### Google Drive (Default)
```
┌─ Status ──────────────────────────────────────────────────┐
│ Authentication: ⚠ Not authenticated    [Authenticate]      │
│                                                             │
│ • Click "Authenticate" button                              │
│ • Browser opens for OAuth flow                             │
│ • Grant permissions                                         │
│ • Return to AudioBrowser                                    │
└─────────────────────────────────────────────────────────────┘
```

#### Dropbox
```
┌─ Status ──────────────────────────────────────────────────┐
│ Authentication: ⚠ Not authenticated                        │
│                                                             │
│ Access Token: [________________________]                   │
│                         [Set Access Token]                  │
│                                                             │
│ • Get token from Dropbox App Console                       │
│ • Paste token in field above                               │
│ • Click "Set Access Token"                                 │
└─────────────────────────────────────────────────────────────┘
```

#### WebDAV/Nextcloud
```
┌─ Status ──────────────────────────────────────────────────┐
│ Authentication: ⚠ Not authenticated                        │
│                                                             │
│ Server URL: [___________________________________]          │
│ Username:   [___________________________________]          │
│ Password:   [___________________________________]          │
│                         [Set Credentials]                   │
│                                                             │
│ • Enter your WebDAV server details                         │
│ • For Nextcloud: .../remote.php/dav/files/username/       │
│ • Click "Set Credentials"                                  │
└─────────────────────────────────────────────────────────────┘
```

**Note**: The actual implementation in this phase uses the existing authentication button, with provider-specific UI to be added in future updates. The current implementation focuses on backend support.

### Rest of Dialog (Unchanged)

The following sections remain the same for all providers:
- Folder selection
- Sync operations (Upload/Download)
- Progress log
- Status messages

---

## Visual Layout

### Full Dialog Layout (Current Implementation)

```
┌──────────────────── Cloud Sync ───────────────────────┐
│                                                         │
│  Cloud Synchronization         Provider: [Google ▼]   │
│                                                         │
│  ┌─ Status ──────────────────────────────────────────┐ │
│  │ Authentication: ⚠ Not authenticated  [Authenticate]│ │
│  │ Folder: (not selected)                            │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  ┌─ Folder Selection ───────────────────────────────┐  │
│  │ Remote Folder: [___________________]              │  │
│  │                          [Select/Create]           │  │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  ┌─ Sync Operations ────────────────────────────────┐  │
│  │ Choose sync direction:                           │  │
│  │  [⬆ Upload Local Changes] [⬇ Download Remote Changes]│
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  ┌─ Progress Log ──────────────────────────────────┐   │
│  │                                                   │   │
│  │  (sync progress messages appear here)            │   │
│  │                                                   │   │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
│  Status: Ready                                          │
│                                                         │
│                                      [Close]            │
└─────────────────────────────────────────────────────────┘
```

---

## Provider Switching Behavior

When user selects a different provider from dropdown:

1. **Provider Changes**
   - Backend switches to selected provider
   - Authentication status updates
   - Status message shows: "Provider changed to: [Provider Name]"

2. **State Reset**
   - Authentication status re-checked for new provider
   - Folder selection cleared (if not authenticated)
   - Ready for new provider setup

3. **Progress Preserved**
   - Progress log maintained
   - Previous messages remain visible
   - New operations append to log

---

## Color Coding

The dialog uses the application's theme colors:

- **Success** (Green): ✓ Authenticated, successful operations
- **Warning** (Orange): ⚠ Not authenticated, pending actions
- **Error** (Red): ✗ Failed operations, errors
- **Info** (Blue): Progress messages, informational text

---

## Responsive Behavior

- **During Sync**: Provider dropdown disabled to prevent switching mid-operation
- **Long Operations**: Progress log scrolls automatically
- **Errors**: Clear error messages with troubleshooting hints
- **Success**: Confirmation messages with operation details

---

## Accessibility

- **Keyboard Navigation**: All controls accessible via Tab key
- **Screen Readers**: Labels properly associated with controls
- **Clear Labels**: All buttons and fields clearly labeled
- **Status Updates**: Real-time feedback for all operations

---

## Future UI Enhancements (Not Yet Implemented)

Planned improvements for future updates:

### 1. Provider-Specific Authentication UI
- Custom input fields for Dropbox token
- Custom form for WebDAV credentials
- Better visual differentiation between providers

### 2. Provider Status Indicators
- Icons showing which providers are available
- Visual indicators for authentication status
- Quick provider comparison

### 3. Advanced Settings
- Sync rules configuration dialog
- Sync history viewer
- Conflict resolution UI

### 4. Provider Information
- Help buttons linking to setup guides
- Quick tips for each provider
- Storage usage indicators

---

## Testing Checklist

When testing the UI:

- [ ] Menu item shows "Cloud Sync..." not "Google Drive Sync..."
- [ ] Dialog title shows "Cloud Sync" not "Google Drive Sync"
- [ ] Provider dropdown appears in top-right
- [ ] Can select different providers from dropdown
- [ ] Dropdown disabled during sync operations
- [ ] Authentication status updates when switching providers
- [ ] Status messages update appropriately
- [ ] All providers can authenticate successfully
- [ ] Folder selection works for all providers
- [ ] Upload/download works for all providers
- [ ] Progress log shows all operations clearly
- [ ] Theme colors applied correctly
- [ ] Dialog layout responsive to different sizes

---

## Screenshots Needed

For documentation, capture screenshots showing:

1. **Menu**: Edit menu with "Cloud Sync..." item
2. **Dialog - Google Drive**: With Google Drive selected
3. **Dialog - Dropbox**: With Dropbox selected
4. **Dialog - WebDAV**: With WebDAV/Nextcloud selected
5. **Provider Dropdown**: Showing all provider options
6. **Sync in Progress**: With progress log showing activity
7. **Successful Sync**: With completion message

---

**Last Updated**: January 2025  
**Implementation Status**: Complete (provider selection UI implemented, provider-specific authentication UI pending)
