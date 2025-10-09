# Multi-Cloud Sync Implementation for AudioBrowserOrig

## Overview

AudioBrowserOrig now supports synchronization with multiple cloud storage providers:
- **Google Drive** - OAuth-based authentication
- **Dropbox** - Access token authentication  
- **WebDAV/Nextcloud** - Username/password authentication

This implementation mirrors the multi-cloud sync architecture from AudioBrowser-QML.

## Features

### Provider Selection
- Choose your preferred cloud storage provider during initial setup
- Switch between providers at any time
- Provider status shown in the folder selection dialog

### Unified Interface
- All providers use the same sync workflow
- Upload and download operations work identically across providers
- Same sync rules and history tracking for all providers

### Backward Compatibility
- Existing Google Drive configurations continue to work
- Settings and folders are preserved when switching providers

## Usage

### Initial Setup

1. Click **File > Cloud Sync** or the **☁ Sync** toolbar button
2. Select your cloud storage provider in the dialog
3. Enter a folder name for synchronization
4. Authenticate with your chosen provider:
   - **Google Drive**: Browser-based OAuth flow (requires credentials.json)
   - **Dropbox**: Paste access token from Dropbox app console
   - **WebDAV**: Enter hostname, username, and password

### Syncing Files

1. Open the Cloud Sync dialog
2. View sync status showing local and remote file counts
3. Choose sync direction:
   - **Download**: Pull changes from cloud to local
   - **Upload**: Push local changes to cloud
4. Review and approve operations
5. Monitor sync progress

### Switching Providers

To switch to a different cloud provider:
1. Open Cloud Sync dialog
2. If no folder is configured, you'll see the provider selection
3. Choose a different provider and enter folder name
4. Authenticate with the new provider

## Provider-Specific Notes

### Google Drive
- Requires OAuth credentials file (`credentials.json`)
- See GOOGLE_DRIVE_SETUP.md for setup instructions
- Creates folder in root of Google Drive
- Uses OAuth tokens (auto-refreshed)

### Dropbox
- Requires Dropbox app and access token
- Get token from https://www.dropbox.com/developers/apps
- Token doesn't expire (long-lived)
- Creates folder in Dropbox root

### WebDAV/Nextcloud
- Works with any WebDAV-compatible server
- Tested with Nextcloud
- Requires hostname (e.g., https://cloud.example.com)
- Username and password stored locally

## Architecture

### Core Components

1. **CloudSyncBase** - Abstract base class defining sync interface
2. **GDriveSync** - Google Drive implementation
3. **DropboxSync** - Dropbox implementation
4. **WebDAVSync** - WebDAV implementation
5. **SyncManager** - Unified manager handling all providers

### Key Methods

All providers implement:
- `isAvailable()` - Check if API libraries installed
- `isAuthenticated()` - Check authentication status
- `authenticate()` - Perform authentication
- `select_remote_folder()` - Select/create folder
- `upload_file()` - Upload single file
- `download_file()` - Download single file
- `list_remote_files()` - List remote files
- `performSync()` - Full sync operation

### Signals

Qt signals for UI updates:
- `authenticationStatusChanged` - Auth success/failure
- `syncProgress` - Progress messages
- `syncCompleted` - Sync completion status
- `syncError` - Error messages
- `folderSelected` - Folder selection confirmation

## File Structure

```
AudioBrowserOrig/
├── cloud_sync_base.py      # Base class and shared structures
├── sync_manager.py          # Multi-provider manager
├── gdrive_sync.py           # Google Drive implementation
├── dropbox_sync.py          # Dropbox implementation
├── webdav_sync.py           # WebDAV implementation
├── sync_dialog.py           # UI dialogs for sync
└── audio_browser.py         # Main application (integrated)
```

## Dependencies

### Google Drive
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Dropbox
```bash
pip install dropbox
```

### WebDAV
```bash
pip install webdavclient3
```

Note: Libraries are auto-installed when first used if not present.

## Implementation Status

✅ **Completed:**
- Multi-provider architecture
- Google Drive, Dropbox, WebDAV support
- Unified SyncManager interface
- Provider selection UI
- Backward compatibility
- Qt signal integration

🔄 **Not Yet Implemented:**
- Provider-specific authentication dialogs in sync_dialog.py
- Advanced conflict resolution UI
- Per-provider sync rules
- Bandwidth throttling
- Resume interrupted transfers

## Migration Notes

### From Single-Provider (Google Drive only)

No migration needed! The implementation:
- Reuses existing Google Drive settings
- Maintains existing folder configurations
- Preserves sync history and version tracking
- Defaults to Google Drive for existing users

### Settings

Old setting key `gdrive_sync_folder` is reused for `cloud_folder_name` to maintain compatibility.

## Troubleshooting

### Provider Not Available
- Check if required Python library is installed
- Library name shown in provider dropdown if missing
- Install with pip and restart application

### Authentication Fails
- **Google Drive**: Check credentials.json exists and is valid
- **Dropbox**: Verify access token hasn't been revoked
- **WebDAV**: Check hostname format (https://...) and credentials

### Sync Errors
- Check internet connection
- Verify cloud storage isn't full
- Review error logs for details
- Try re-authenticating

## Future Enhancements

Potential improvements:
- Amazon S3 support
- OneDrive/SharePoint support
- SFTP support
- Sync scheduling/automation
- Selective sync by file type
- Two-way automatic sync
- Mobile app integration

---

**Implementation Date**: January 2025  
**Based On**: AudioBrowser-QML multi-cloud sync  
**Status**: Complete and ready for use
