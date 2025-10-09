# Dropbox Sync Setup Guide

This guide explains how to set up and use Dropbox synchronization in AudioBrowser-QML.

---

## Prerequisites

1. **Python Packages** (auto-installed if missing):
   - dropbox

2. **Dropbox Account** (free or paid)

3. **Dropbox App** with access token (see setup below)

---

## Setup Instructions

### Step 1: Create Dropbox App

1. Go to [Dropbox App Console](https://www.dropbox.com/developers/apps)

2. Click **"Create app"**

3. Choose settings:
   - **API**: Scoped access
   - **Type of access**: Full Dropbox
   - **Name**: "AudioBrowser" (or any unique name)

4. Click **"Create app"**

### Step 2: Generate Access Token

1. In your app's settings page, scroll to **"OAuth 2"** section

2. Under **"Generated access token"**, click **"Generate"**

3. Copy the access token (it's a long string starting with "sl...")

4. **Important**: Save this token securely - you won't be able to see it again!

### Step 3: Set Permissions (Optional but Recommended)

1. Go to **"Permissions"** tab in your app settings

2. Enable these permissions:
   - files.metadata.write
   - files.metadata.read
   - files.content.write
   - files.content.read

3. Click **"Submit"** to save permissions

---

## Using Dropbox Sync

### First-Time Authentication

1. Launch AudioBrowser-QML

2. Open Sync Dialog:
   - Menu: **Edit** → **Cloud Sync...**

3. Select **"Dropbox"** from the provider dropdown

4. Click **"Set Access Token"** button

5. Paste your Dropbox access token

6. Click **"Connect"**

7. You'll see "Authenticated as [Your Name]" message

8. Token is automatically saved to `~/.audiobrowser/dropbox_token.json` for future use

### Selecting a Sync Folder

1. Enter folder name in "Remote Folder" field
   - Example: "BandPracticeSessions"
   - Folder will be created at: `/Apps/AudioBrowser/BandPracticeSessions`
   - Any name you want - it will be created if it doesn't exist

2. Click **"Select/Create"** button
   - Folder is created in your Dropbox
   - Path: `/Apps/AudioBrowser/[YourFolderName]`
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
- Files from Dropbox are downloaded to current folder
- Existing local files may be overwritten
- New remote files are added locally

---

## Dropbox Folder Structure

Your files are organized in Dropbox like this:

```
/Apps/
  └── AudioBrowser/
      ├── BandPracticeSessions/    (your folder)
      │   ├── song1.wav
      │   ├── song2.mp3
      │   ├── .audio_notes_user1.json
      │   └── .provided_names.json
      └── RehearsalRecordings/     (another folder)
          └── ...
```

**Note**: All AudioBrowser files go in `/Apps/AudioBrowser/` in your Dropbox root.

---

## Multi-User Collaboration

Dropbox Sync supports multiple users working on the same practice sessions.

### Sharing a Folder

1. In Dropbox web or desktop app, navigate to `/Apps/AudioBrowser/YourFolder`

2. Right-click the folder and select **"Share"**

3. Invite band members by email

4. They'll need to:
   - Accept the share invitation
   - Create their own Dropbox app and access token
   - Use the same folder name in AudioBrowser

### How Multi-User Works

**Each user has their own annotation file:**
- `.audio_notes_USER.json` where USER is your username
- Your annotations are separate from others
- All users' annotations are synced

**Shared metadata:**
- File names, durations, tempo info
- These are shared across all users

**Conflict prevention:**
- You can only modify YOUR annotation files
- Other users' annotations are read-only to you
- Shared metadata uses "last write wins"

### Multi-User Workflow

**Band Member A:**
1. Creates Dropbox app and gets access token
2. Opens practice folder in AudioBrowser
3. Creates annotations during practice
4. Uploads to Dropbox
5. Annotations saved as `.audio_notes_memberA.json`

**Band Member B:**
1. Creates their own Dropbox app and token
2. Accesses shared Dropbox folder
3. Downloads from Dropbox in AudioBrowser
4. Sees Member A's annotations (read-only)
5. Creates their own annotations
6. Uploads to Dropbox
7. Annotations saved as `.audio_notes_memberB.json`

---

## Troubleshooting

### "Dropbox SDK not available"

**Solution**: Install the Dropbox package:
```bash
pip install dropbox
```

### "Authentication failed"

**Possible causes:**
1. Invalid access token
2. Token has expired
3. App permissions not set correctly

**Solutions:**
1. Generate a new access token from Dropbox App Console
2. Check that your app has correct permissions
3. Re-enter the token in AudioBrowser

### "Upload failed" / "Download failed"

**Possible causes:**
1. No internet connection
2. Dropbox storage quota exceeded
3. File too large (Dropbox has 50 GB upload limit per file)
4. Permission issues with shared folders

**Solutions:**
1. Check internet connection
2. Check Dropbox storage space in your account
3. Try with smaller files
4. Verify folder sharing permissions

### "Folder not found"

**Solution**: Try creating a new folder with a different name

### Access Token Security

**Important**: Your access token provides full access to your Dropbox!

**Best practices:**
- Don't share your access token with anyone
- Keep it secure
- If compromised, revoke it in Dropbox App Console and generate a new one
- Consider setting shorter expiration times in app settings

---

## Advanced Usage

### Revoking Access

If you want to revoke AudioBrowser's access to Dropbox:

1. Go to [Dropbox App Console](https://www.dropbox.com/developers/apps)
2. Find your AudioBrowser app
3. Delete the app or revoke the access token
4. In AudioBrowser, delete `~/.audiobrowser/dropbox_token.json`

### Using Dropbox Business

Dropbox Business accounts work the same way:

1. Create app in your Dropbox Business account
2. Generate access token
3. Use in AudioBrowser as normal
4. Files go in your Business Dropbox

**Note**: Business accounts may have additional security restrictions.

### Selective Sync

To customize what gets synced:

1. Create `.sync_rules.json` in your practice folder
2. Edit settings (see example below)

**Example `.sync_rules.json`:**
```json
{
  "max_file_size_mb": 100,
  "sync_audio_files": true,
  "sync_annotations_only": false
}
```

---

## Comparing Dropbox to Other Providers

### vs Google Drive:
- **Easier setup**: No OAuth flow needed
- **Simpler**: Just paste a token
- **Less storage**: 2 GB free vs 15 GB
- **Faster**: Generally faster upload/download speeds

### vs WebDAV/Nextcloud:
- **More convenient**: No need for self-hosting
- **Less control**: Your data is on Dropbox servers
- **Easier**: No server configuration needed

---

## FAQ

**Q: Do I need Dropbox desktop app installed?**  
A: No! AudioBrowser connects directly to Dropbox via the API.

**Q: Can I use my existing Dropbox folders?**  
A: Files must be in `/Apps/AudioBrowser/` directory, but you can organize however you want within that.

**Q: What if I run out of Dropbox storage?**  
A: Upgrade to Dropbox Plus/Professional, or use selective sync rules to sync only annotations.

**Q: Can I use the same token on multiple computers?**  
A: Yes! Copy `~/.audiobrowser/dropbox_token.json` to other computers.

**Q: Is this secure?**  
A: Yes, as long as you keep your access token private. Dropbox uses HTTPS for all transfers.

**Q: Can I share with non-Dropbox users?**  
A: No, all band members need Dropbox accounts. Consider WebDAV/Nextcloud for more flexibility.

**Q: How long does the access token last?**  
A: By default, tokens don't expire. You can set expiration in app settings.

---

## Support

For issues or questions:
1. Check this guide's Troubleshooting section
2. Read [Cloud Sync Setup Guide](CLOUD_SYNC_SETUP.md) for general sync info
3. Check Dropbox API status: [Dropbox Status](https://status.dropbox.com/)
4. File an issue on GitHub: [BandTools Issues](https://github.com/TheMikaus/BandTools/issues)

---

**Last Updated**: January 2025  
**Version**: 1.0  
**Status**: Production Ready
