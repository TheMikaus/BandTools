# Cloud Sync Setup Guide

AudioBrowser-QML supports synchronization with multiple cloud storage providers, allowing you to backup your practice sessions and collaborate with band members.

---

## Supported Cloud Providers

### Google Drive
- **Status**: Fully supported with OAuth authentication
- **Best for**: Users with Google accounts
- **Features**: Automatic authentication flow, folder management
- **Setup Complexity**: Medium (requires Google Cloud Console setup)
- **See**: [Google Drive Sync Setup](../GOOGLE_DRIVE_SYNC_README.md)

### Dropbox
- **Status**: Fully supported with access token authentication
- **Best for**: Dropbox users
- **Features**: Simple token-based authentication
- **Setup Complexity**: Low (just need access token)
- **See**: [Dropbox Sync Setup](DROPBOX_SYNC_SETUP.md)

### WebDAV/Nextcloud
- **Status**: Fully supported with basic authentication
- **Best for**: Self-hosted solutions, privacy-conscious users
- **Features**: Works with Nextcloud, ownCloud, and any WebDAV server
- **Setup Complexity**: Low (just server URL and credentials)
- **See**: [WebDAV Sync Setup](WEBDAV_SYNC_SETUP.md)

---

## Choosing a Provider

### Consider These Factors:

**Storage Space**:
- Google Drive: 15 GB free
- Dropbox: 2 GB free
- Nextcloud: Depends on your server

**Privacy**:
- Google Drive: Data stored on Google servers
- Dropbox: Data stored on Dropbox servers
- WebDAV/Nextcloud: You control the server (best privacy)

**Collaboration**:
- All providers support folder sharing
- Google Drive has best integration with Google accounts
- Nextcloud has excellent collaboration features

**Setup Difficulty**:
- Easiest: Dropbox (just get a token)
- Medium: Google Drive (requires Cloud Console setup)
- Medium: WebDAV (need server URL and credentials)

---

## Quick Start

### Using the Sync Dialog

1. Launch AudioBrowser-QML

2. Open the Sync Dialog:
   - Menu: **Edit** → **Cloud Sync...**

3. Select your preferred provider from the dropdown

4. Follow provider-specific setup instructions:
   - **Google Drive**: Click "Authenticate" and follow browser flow
   - **Dropbox**: Enter your access token
   - **WebDAV**: Enter server URL, username, and password

5. Select or create a remote folder

6. Upload or download files

---

## Common Features

All cloud providers support these features:

### Selective Sync
- Control what gets synced (audio files, annotations, metadata)
- Set maximum file size limits
- Annotations-only mode for low bandwidth

### Multi-User Collaboration
- Each user has separate annotation files
- Shared metadata across all users
- Prevent conflicts with user-specific files

### Sync History
- Track all sync operations
- View when files were uploaded/downloaded
- See which user performed each sync

### Version Tracking
- Backend tracks sync versions
- Helps detect conflicts
- Shows what changed between syncs

---

## Switching Between Providers

You can switch between cloud providers at any time:

1. Open the Sync Dialog
2. Select a different provider from the dropdown
3. Authenticate with the new provider
4. Select a folder on the new provider
5. Sync files

**Note**: Each provider stores files independently. Switching providers doesn't automatically migrate your files.

---

## Security & Privacy

### What Gets Synced:
- Audio files (.wav, .mp3, etc.)
- Annotation files (.audio_notes_*.json)
- Metadata files (.provided_names.json, etc.)

### What Never Gets Synced:
- Backup folders (.backup)
- Waveform cache (.waveforms)
- Git repositories (.git)
- Python cache (__pycache__)

### Authentication:
- **Google Drive**: OAuth 2.0 tokens stored locally
- **Dropbox**: Access tokens stored locally
- **WebDAV**: Credentials stored locally (encrypted recommended)

### Data Storage:
- Your files are stored according to each provider's terms
- WebDAV gives you full control if self-hosted
- All providers use HTTPS for transfer security

---

## Troubleshooting

### "Provider not available"
**Solution**: Install required Python packages:
```bash
# For Google Drive
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

# For Dropbox
pip install dropbox

# For WebDAV
pip install webdavclient3
```

### "Authentication failed"
- **Google Drive**: Check credentials.json file location
- **Dropbox**: Verify access token is correct
- **WebDAV**: Check server URL, username, and password

### "No internet connection"
- Sync requires active internet connection
- Check your network settings
- Try again when online

### Sync is slow
- Large audio files take time to upload
- Consider using "annotations only" mode
- Set file size limits in sync rules

---

## FAQ

**Q: Can I use multiple providers?**  
A: Yes! You can switch between providers anytime.

**Q: Will my files be duplicated?**  
A: No. Each provider stores files independently.

**Q: Can I sync the same folder to multiple providers?**  
A: Yes, but you'll need to manually switch providers and sync.

**Q: Is my data safe?**  
A: Data is as safe as your cloud provider's security. WebDAV/Nextcloud gives you full control.

**Q: Can I sync offline?**  
A: No. Sync requires internet connection.

**Q: How much does it cost?**  
A: AudioBrowser sync is free. Cloud storage may have costs:
- Google Drive: 15 GB free, then paid plans
- Dropbox: 2 GB free, then paid plans
- Nextcloud: Free if self-hosted, or various paid hosting options

**Q: Which provider is recommended?**  
A: 
- For ease of use: **Dropbox**
- For Google users: **Google Drive**
- For privacy/control: **WebDAV/Nextcloud**

---

## Getting Help

For provider-specific help, see the individual setup guides:
- [Google Drive Sync Setup](../GOOGLE_DRIVE_SYNC_README.md)
- [Dropbox Sync Setup](DROPBOX_SYNC_SETUP.md)
- [WebDAV Sync Setup](WEBDAV_SYNC_SETUP.md)

For issues or questions:
1. Check the Troubleshooting section above
2. Read the provider-specific guide
3. File an issue on GitHub: [BandTools Issues](https://github.com/TheMikaus/BandTools/issues)

---

**Last Updated**: January 2025  
**Version**: 1.0  
**Status**: Production Ready
