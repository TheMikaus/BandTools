# Google Drive Sync Setup Guide

This guide explains how to set up and use Google Drive synchronization in AudioBrowser-QML.

---

## Prerequisites

1. **Python Packages** (auto-installed if missing):
   - google-auth
   - google-auth-oauthlib
   - google-auth-httplib2
   - google-api-python-client

2. **Google Account** with access to Google Drive

3. **Google Cloud Project** with Drive API enabled (see setup below)

---

## Setup Instructions

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)

2. Click "Create Project" or select existing project

3. Enter project name (e.g., "AudioBrowser Sync")

4. Click "Create"

### Step 2: Enable Google Drive API

1. In your project, go to "APIs & Services" > "Library"

2. Search for "Google Drive API"

3. Click on "Google Drive API"

4. Click "Enable"

### Step 3: Create OAuth Credentials

1. Go to "APIs & Services" > "Credentials"

2. Click "Create Credentials" > "OAuth client ID"

3. If prompted, configure OAuth consent screen:
   - Choose "External" user type (unless you have Google Workspace)
   - Fill in app name: "AudioBrowser"
   - Add your email as developer contact
   - Skip optional scopes for now
   - Add test users (your email)
   - Click "Save and Continue"

4. Back to "Create OAuth client ID":
   - Application type: "Desktop app"
   - Name: "AudioBrowser Desktop Client"
   - Click "Create"

5. Download the credentials:
   - Click "Download JSON" on the credentials you just created
   - Save as `credentials.json`

### Step 4: Install Credentials

1. Create AudioBrowser config directory:
   ```bash
   mkdir -p ~/.audiobrowser
   ```

2. Copy credentials file:
   ```bash
   cp /path/to/credentials.json ~/.audiobrowser/
   ```

3. Verify file exists:
   ```bash
   ls -la ~/.audiobrowser/credentials.json
   ```

---

## Using Google Drive Sync

### First-Time Authentication

1. Launch AudioBrowser-QML

2. Open Sync Dialog:
   - Menu: **Edit** → **Google Drive Sync...**

3. Click **"Authenticate"** button
   - Browser window opens automatically
   - Sign in to your Google account
   - Grant permissions to AudioBrowser
   - You'll see "Authentication successful" message

4. Token is saved to `~/.audiobrowser/token.json` for future use

### Selecting a Sync Folder

1. Enter folder name in "Remote Folder" field
   - Example: "BandPracticeSessions"
   - Any name you want - it will be created if it doesn't exist

2. Click **"Select/Create"** button
   - Folder is created in your Google Drive root
   - Folder ID is saved for this session

### Uploading Files

1. Make sure you have a folder open in AudioBrowser
   - File → Open Folder...
   - Browse to your practice session folder

2. Click **"⬆ Upload Local Changes"**
   - Files are analyzed
   - Upload progress shown in log
   - Completion message displayed

**What gets uploaded:**
- Audio files (.wav, .mp3, etc.)
- Annotation files (.audio_notes_*.json)
- Metadata files (.provided_names.json, .duration_cache.json, etc.)

**What does NOT get uploaded:**
- Backup folders (.backup)
- Waveform cache (.waveforms)
- Git folders (.git)
- Python cache (__pycache__)

### Downloading Files

1. Click **"⬇ Download Remote Changes"**
   - Remote files are listed
   - Download progress shown in log
   - Completion message displayed

**What happens:**
- Files from Google Drive are downloaded to current folder
- Existing local files may be overwritten
- New remote files are added locally

---

## Multi-User Collaboration

Google Drive Sync supports multiple users working on the same practice sessions.

### How It Works

1. **Each user has their own annotation file:**
   - `.audio_notes_USER.json` where USER is your username
   - Your annotations are separate from others
   - All users' annotations are synced

2. **Shared metadata:**
   - File names, durations, tempo info
   - These are shared across all users

3. **Conflict prevention:**
   - You can only modify YOUR annotation files
   - Other users' annotations are read-only to you
   - Shared metadata uses "last write wins"

### Multi-User Workflow

**Band Member A:**
1. Opens practice folder
2. Creates annotations during practice
3. Uploads to Google Drive
4. Annotations saved as `.audio_notes_memberA.json`

**Band Member B:**
1. Downloads from Google Drive
2. Sees Member A's annotations (read-only)
3. Creates their own annotations
4. Uploads to Google Drive
5. Annotations saved as `.audio_notes_memberB.json`

**Both members see:**
- All audio files
- All users' annotations (color-coded)
- Shared metadata

---

## Troubleshooting

### "Google Drive API not available"

**Solution:** Install required packages:
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### "Credentials file not found"

**Solution:** Check credentials file location:
```bash
ls -la ~/.audiobrowser/credentials.json
```

If missing, repeat Step 4 above.

### "Authentication failed"

**Possible causes:**
1. Invalid credentials.json file
2. OAuth consent screen not configured
3. App not added to test users

**Solution:** Re-download credentials from Google Cloud Console

### "Upload failed" / "Download failed"

**Possible causes:**
1. No internet connection
2. Google Drive quota exceeded
3. File too large
4. Permission issues

**Solution:**
1. Check internet connection
2. Check Google Drive storage space
3. Try with smaller files
4. Re-authenticate if needed

### "Folder not found"

**Solution:** Try creating a new folder with a different name

---

## Advanced Usage

### Selective Sync

The backend supports selective sync rules (not yet in UI):

**Default behavior:**
- Syncs audio files (.wav, .mp3, etc.)
- Syncs all metadata and annotation files
- Excludes backups and caches

**To customize** (requires code changes):
- Edit `backend/gdrive_sync.py`
- Modify `SyncRules` class
- Set max file size, audio-only mode, etc.

### Version Tracking

Version tracking is implemented in the backend but not exposed in UI.

**Backend support:**
- `.sync_version.json` tracks sync version number
- Operations list shows what changed
- Can be used for conflict detection

**To use** (requires code):
- Call `get_remote_version()` method
- Compare with local version
- Implement custom conflict resolution

### Sync History

History tracking is built-in but not visible in UI.

**Backend support:**
- `.sync_history.json` logs all sync operations
- Tracks user, timestamp, file count
- Keeps last 100 entries

**To view** (requires code):
- Load sync history from local file
- Call `get_recent_entries()`
- Display in custom dialog

---

## Security & Privacy

### Data Stored on Google Drive

- **Audio files:** Your practice recordings (if synced)
- **Annotations:** Your personal notes and markers
- **Metadata:** File names, durations, tempo info
- **No personal data:** No passwords, no payment info

### OAuth Tokens

- **Stored locally:** `~/.audiobrowser/token.json`
- **Never uploaded:** Tokens stay on your computer
- **Secure:** Standard OAuth 2.0 protocol
- **Revocable:** Can revoke in Google account settings

### Permissions Requested

- **Google Drive file access:** Read/write files created by AudioBrowser
- **No full Drive access:** Can't see other apps' files
- **No email access:** Doesn't read your Gmail
- **No calendar access:** Only Drive API

### Revoking Access

If you want to revoke AudioBrowser's access:

1. Go to [Google Account - Security](https://myaccount.google.com/security)
2. Click "Third-party apps with account access"
3. Find "AudioBrowser" in the list
4. Click "Remove Access"

---

## FAQ

**Q: Do I need to sync every time I make changes?**  
A: No. Sync when you want to share with others or backup to cloud.

**Q: Can I use multiple Google accounts?**  
A: Yes, but you'll need separate credentials for each account.

**Q: What happens if two users edit the same file simultaneously?**  
A: Last upload wins. User-specific annotations are kept separate.

**Q: Is there a file size limit?**  
A: Google Drive has limits (typically 5GB per file). AudioBrowser has no limits.

**Q: Can I sync to a shared folder?**  
A: Yes, share the Google Drive folder with other users.

**Q: Does it work offline?**  
A: No. Sync requires internet connection.

**Q: Can I schedule automatic syncs?**  
A: Not yet. Manual sync only in this version.

**Q: Where are my files on Google Drive?**  
A: In the root of your Drive, in the folder you specified.

**Q: Can I see sync progress?**  
A: Yes, progress is shown in the log area of the sync dialog.

---

## Support

For issues or questions:

1. Check this guide's Troubleshooting section
2. Read PHASE_16_SUMMARY.md for technical details
3. Check the Google Cloud Console for API quotas
4. File an issue on GitHub: [BandTools Issues](https://github.com/TheMikaus/BandTools/issues)

---

**Last Updated:** January 2025  
**Version:** 1.0 (Phase 16)  
**Status:** Production Ready
