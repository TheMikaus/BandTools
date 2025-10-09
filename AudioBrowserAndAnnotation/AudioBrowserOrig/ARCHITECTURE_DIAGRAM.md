# Multi-Cloud Sync Architecture Diagram

## Component Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     AudioBrowserOrig                             │
│                     (audio_browser.py)                           │
│                                                                  │
│  Menu: ☁ Cloud Sync...                                          │
│  Toolbar: ☁ Sync                                                │
│  Status: "Connected to Google Drive"                            │
└───────────────────┬─────────────────────────────────────────────┘
                    │
                    │ uses
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SyncManager                                 │
│                   (sync_manager.py)                              │
│                                                                  │
│  • Manages all cloud providers                                  │
│  • Delegates operations to active provider                      │
│  • Forwards Qt signals                                          │
│  • Maintains backward compatibility                             │
│                                                                  │
│  Active Provider: ───────────────┐                              │
│  - gdrive  (default)             │                              │
│  - dropbox                       │                              │
│  - webdav                        │                              │
└──────────────────┬────────────────┴──────────────────────────────┘
                   │
                   │ delegates to
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CloudSyncBase                                 │
│                 (cloud_sync_base.py)                             │
│                 [Abstract Base Class]                            │
│                                                                  │
│  Abstract Methods:                                               │
│  • isAvailable() → bool                                          │
│  • isAuthenticated() → bool                                      │
│  • authenticate() → bool                                         │
│  • select_remote_folder(name) → str                              │
│  • upload_file(local_path, remote_name) → bool                  │
│  • download_file(remote_name, local_path) → bool                │
│  • list_remote_files() → List[Dict]                              │
│  • performSync(directory, upload) → bool                         │
│                                                                  │
│  Qt Signals:                                                     │
│  • authenticationStatusChanged(bool, str)                        │
│  • syncProgress(str)                                             │
│  • syncCompleted(bool, str, int)                                 │
│  • syncError(str)                                                │
│  • folderSelected(str, str)                                      │
│                                                                  │
│  Shared Data Structures:                                         │
│  • SyncHistory - track sync operations                           │
│  • SyncRules - selective sync configuration                      │
│  • SyncVersion - version tracking                                │
└──────────────────┬──────────────┬────────────────┬──────────────┘
                   │              │                │
                   │ implements   │ implements     │ implements
                   ▼              ▼                ▼
┌──────────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│   GDriveSync         │ │  DropboxSync     │ │   WebDAVSync     │
│ (gdrive_sync.py)     │ │(dropbox_sync.py) │ │(webdav_sync.py)  │
│                      │ │                  │ │                  │
│ • OAuth flow         │ │ • Access token   │ │ • Username/pass  │
│ • credentials.json   │ │ • Long-lived     │ │ • WebDAV proto   │
│ • token.json         │ │ • dropbox SDK    │ │ • Nextcloud ✓    │
│ • Google API         │ │ • App console    │ │ • ownCloud ✓     │
│ • Auto-refresh       │ │ • Simple setup   │ │ • Generic ✓      │
└──────────────────────┘ └──────────────────┘ └──────────────────┘
```

## User Interface Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  Step 1: Open Cloud Sync                                        │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  File Menu > ☁ Cloud Sync...                           │    │
│  │  OR                                                     │    │
│  │  Toolbar > ☁ Sync Button                               │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 2: Provider & Folder Selection (first time)              │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Cloud Sync Configuration                              │    │
│  │  ┌──────────────────────────────────────────────────┐  │    │
│  │  │ Cloud Provider: [Google Drive ▼]                 │  │    │
│  │  │                 ├─ Google Drive                   │  │    │
│  │  │                 ├─ Dropbox                        │  │    │
│  │  │                 └─ WebDAV/Nextcloud               │  │    │
│  │  └──────────────────────────────────────────────────┘  │    │
│  │                                                         │    │
│  │  Enter folder name: [BandPracticeSessions_____]        │    │
│  │                                                         │    │
│  │  Note: Folder created in root of cloud storage         │    │
│  │                                                         │    │
│  │  [Select/Create]  [Cancel]                             │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 3: Authentication                                         │
│                                                                 │
│  IF Google Drive:                                               │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Browser opens for OAuth                                │    │
│  │  → Sign in to Google                                    │    │
│  │  → Grant permissions                                    │    │
│  │  → Redirect back to app                                 │    │
│  │  ✓ Token saved to token.json                            │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  IF Dropbox:                                                    │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Enter Access Token: [_________________________]        │    │
│  │  Get from: https://www.dropbox.com/developers/apps      │    │
│  │  ✓ Token saved to dropbox_token.json                    │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  IF WebDAV:                                                     │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Hostname: [https://cloud.example.com____________]      │    │
│  │  Username: [myuser________________________]             │    │
│  │  Password: [••••••••••••••••••••••••••••]               │    │
│  │  ✓ Credentials saved to webdav_config.json              │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 4: Sync Status                                            │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Sync Status                                            │    │
│  │  ┌──────────────────────────────────────────────────┐  │    │
│  │  │  Provider: Google Drive                          │  │    │
│  │  │  Folder: BandPracticeSessions                    │  │    │
│  │  │                                                   │  │    │
│  │  │  Local Version: 15                               │  │    │
│  │  │  Remote Version: 15                              │  │    │
│  │  │                                                   │  │    │
│  │  │  Local Files: 42                                 │  │    │
│  │  │  Remote Files: 42                                │  │    │
│  │  │                                                   │  │    │
│  │  │  Status: ✓ In Sync                               │  │    │
│  │  └──────────────────────────────────────────────────┘  │    │
│  │                                                         │    │
│  │  [Close]                                                │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 5: Choose Sync Direction                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  What would you like to do?                            │    │
│  │                                                         │    │
│  │  Yes: Download changes from [Provider]                 │    │
│  │  No: Upload changes to [Provider]                      │    │
│  │  Cancel: Close without syncing                         │    │
│  │                                                         │    │
│  │  [Yes]  [No]  [Cancel]                                 │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 6: Review & Approve Operations                            │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Review Upload/Download Changes                        │    │
│  │  ┌──────────────────────────────────────────────────┐  │    │
│  │  │ ☑ song1.wav          │ Add      │ 3.2 MB        │  │    │
│  │  │ ☑ song2.wav          │ Add      │ 4.1 MB        │  │    │
│  │  │ ☑ .audio_notes_me    │ Update   │ 1 KB          │  │    │
│  │  │ ☐ old_recording.wav  │ Delete   │ 5.0 MB        │  │    │
│  │  └──────────────────────────────────────────────────┘  │    │
│  │                                                         │    │
│  │  Selected: 3 operations                                │    │
│  │                                                         │    │
│  │  [Start Sync]  [Cancel]                                │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 7: Sync Progress                                          │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  Syncing Files...                                       │    │
│  │  ┌──────────────────────────────────────────────────┐  │    │
│  │  │  Processing 2/3: song2.wav                       │  │    │
│  │  │  [████████████████░░░░░░░░] 67%                  │  │    │
│  │  └──────────────────────────────────────────────────┘  │    │
│  │                                                         │    │
│  │  Uploading to Google Drive...                          │    │
│  │  2.1 MB / 3.2 MB                                       │    │
│  │                                                         │    │
│  │  [Cancel]                                               │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Step 8: Completion                                             │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  ✓ Sync Complete!                                       │    │
│  │                                                         │    │
│  │  Successfully synced 3 files                            │    │
│  │  Provider: Google Drive                                │    │
│  │  Time: 15 seconds                                      │    │
│  │                                                         │    │
│  │  [OK]                                                   │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  Status bar: "Upload complete!" (5 seconds)                    │
└─────────────────────────────────────────────────────────────────┘
```

## Signal Flow

```
User Action
    │
    ▼
AudioBrowser
    │
    │ _show_cloud_sync()
    ▼
SyncManager.authenticate()
    │
    │ delegates to
    ▼
GDriveSync.authenticate()
    │
    │ emits
    ▼
authenticationStatusChanged(True, "Success")
    │
    │ forwarded by SyncManager
    ▼
AudioBrowser receives signal
    │
    ▼
Update UI / Show status
```

## File Organization

```
AudioBrowserOrig/
│
├── Core Sync Files (NEW)
│   ├── cloud_sync_base.py       ← Abstract base + data structures
│   ├── sync_manager.py           ← Multi-provider manager
│   ├── gdrive_sync.py            ← Google Drive (UPDATED)
│   ├── dropbox_sync.py           ← Dropbox (NEW)
│   └── webdav_sync.py            ← WebDAV (NEW)
│
├── UI Files
│   ├── audio_browser.py          ← Main app (UPDATED)
│   └── sync_dialog.py            ← Sync dialogs (UPDATED)
│
├── Documentation (NEW)
│   ├── MULTI_CLOUD_SYNC.md       ← User guide
│   ├── CLOUD_SYNC_IMPLEMENTATION_SUMMARY.md
│   └── ARCHITECTURE_DIAGRAM.md   ← This file
│
└── Configuration (stored at runtime)
    ├── credentials.json          ← Google OAuth (user provides)
    ├── token.json                ← Google tokens (auto-created)
    ├── dropbox_token.json        ← Dropbox token (user provides)
    └── webdav_config.json        ← WebDAV config (user provides)
```

## Data Flow Example: Upload File

```
1. User selects "Upload to Cloud"
   ↓
2. AudioBrowser._show_cloud_sync()
   - Calls SyncManager.list_remote_files()
   - Compares with local files
   - Shows SyncReviewDialog
   ↓
3. User approves operations
   ↓
4. SyncWorker thread starts
   - For each file:
     ↓
   5. SyncWorker calls SyncManager.upload_file()
      ↓
   6. SyncManager delegates to active provider
      (e.g., GDriveSync.upload_file())
      ↓
   7. GDriveSync:
      - Creates MediaFileUpload
      - Calls Google Drive API
      - Emits syncProgress signal
      ↓
   8. Signal received by AudioBrowser
      - Updates progress bar
      - Shows status message
      ↓
   9. On completion:
      - Emits syncCompleted signal
      - Updates local version
      - Refreshes UI
```

---

**Architecture Type**: Delegation Pattern with Abstract Base Class  
**Design Principles**: Single Responsibility, Open/Closed, Dependency Inversion  
**Qt Integration**: Signal/Slot mechanism for async operations  
**Status**: ✅ Complete and functional
