# WebDAV/Nextcloud Sync Setup Guide

This guide explains how to set up and use WebDAV synchronization in AudioBrowser-QML. This works with Nextcloud, ownCloud, and any WebDAV-compatible server.

---

## Prerequisites

1. **Python Packages** (auto-installed if missing):
   - webdavclient3

2. **WebDAV Server** - one of:
   - Nextcloud (self-hosted or hosted)
   - ownCloud (self-hosted or hosted)
   - Any WebDAV server
   - Apache with mod_dav
   - nginx with WebDAV module

3. **WebDAV Credentials**:
   - Server URL
   - Username
   - Password (or app password)

---

## Setup Instructions

### Option A: Using Nextcloud

#### Step 1: Get Your WebDAV URL

1. Log into your Nextcloud instance

2. Click your profile picture → **Settings**

3. In the left sidebar, click **Security**

4. Scroll to **Devices & sessions**

5. Your WebDAV URL will be shown as:
   ```
   https://your-nextcloud-server.com/remote.php/dav/files/your-username/
   ```

6. Copy this URL

#### Step 2: Create App Password (Recommended)

For better security, use an app password instead of your main password:

1. Still in **Settings** → **Security**

2. Under **Devices & sessions**, enter app name: "AudioBrowser"

3. Click **Create new app password**

4. Copy the generated password (you won't see it again!)

5. Use this password in AudioBrowser instead of your main password

### Option B: Using ownCloud

#### Step 1: Get Your WebDAV URL

1. Log into your ownCloud instance

2. Click on your username in top-right corner

3. Select **Settings**

4. In the bottom left, you'll see **WebDAV** section

5. Your WebDAV URL will be:
   ```
   https://your-owncloud-server.com/remote.php/dav/files/your-username/
   ```

#### Step 2: Use Regular Password or App Password

- You can use your regular ownCloud password
- Or create an app password in Settings → Personal → Security

### Option C: Generic WebDAV Server

If you're using a generic WebDAV server:

1. Get the WebDAV URL from your server administrator

2. Common formats:
   ```
   https://server.com/webdav/
   https://server.com/dav/
   https://server.com/remote.php/webdav/
   ```

3. Get your username and password

---

## Using WebDAV Sync in AudioBrowser

### First-Time Configuration

1. Launch AudioBrowser-QML

2. Open Sync Dialog:
   - Menu: **Edit** → **Cloud Sync...**

3. Select **"WebDAV/Nextcloud"** from the provider dropdown

4. Click **"Set Credentials"** button

5. Enter your details:
   - **Server URL**: Your WebDAV URL (see above)
   - **Username**: Your username
   - **Password**: Your password or app password

6. Click **"Connect"**

7. You'll see "Connected to [Server URL]" message

8. Credentials are saved to `~/.audiobrowser/webdav_config.json` for future use

**Example Nextcloud URL:**
```
https://cloud.example.com/remote.php/dav/files/bandmember1/
```

**Example ownCloud URL:**
```
https://mycloud.com/remote.php/dav/files/username/
```

### Selecting a Sync Folder

1. Enter folder name in "Remote Folder" field
   - Example: "BandPracticeSessions"
   - Folder will be created at: `/AudioBrowser/BandPracticeSessions`
   - Any name you want - it will be created if it doesn't exist

2. Click **"Select/Create"** button
   - Folder is created on your WebDAV server
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
- Files from WebDAV server are downloaded to current folder
- Existing local files may be overwritten
- New remote files are added locally

---

## WebDAV Server Folder Structure

Your files are organized on the server like this:

```
/AudioBrowser/                     (created by AudioBrowser)
  ├── BandPracticeSessions/       (your folder)
  │   ├── song1.wav
  │   ├── song2.mp3
  │   ├── .audio_notes_user1.json
  │   └── .provided_names.json
  └── RehearsalRecordings/        (another folder)
      └── ...
```

**Note**: The `/AudioBrowser/` folder is created in your WebDAV root (user home directory).

---

## Multi-User Collaboration

WebDAV/Nextcloud Sync supports multiple users working on the same practice sessions.

### Sharing a Folder in Nextcloud

1. In Nextcloud web interface, navigate to `/AudioBrowser/YourFolder`

2. Click the **Share** icon for the folder

3. Enter band member usernames or emails

4. Set permissions:
   - **Read**: Can download files
   - **Write**: Can upload files
   - **Share**: Can share with others
   - **Delete**: Can delete files

5. Click **Share**

### Sharing in ownCloud

Similar to Nextcloud:
1. Navigate to folder
2. Click Share icon
3. Add users
4. Set permissions

### How Multi-User Works

**Each user has their own annotation file:**
- `.audio_notes_USER.json` where USER is their username
- Your annotations are separate from others
- All users' annotations are synced

**Shared metadata:**
- File names, durations, tempo info
- These are shared across all users

**Conflict prevention:**
- You can only modify YOUR annotation files
- Other users' annotations are read-only to you
- Shared metadata uses "last write wins"

---

## Troubleshooting

### "WebDAV client not available"

**Solution**: Install the WebDAV client package:
```bash
pip install webdavclient3
```

### "Authentication failed"

**Possible causes:**
1. Incorrect server URL
2. Wrong username or password
3. SSL certificate issues
4. Server not accessible

**Solutions:**
1. **Check URL format**:
   - Must end with trailing slash: `.../files/username/`
   - Include protocol: `https://` (not `http://` for security)
   - Don't include folder paths after username
   
2. **Verify credentials**:
   - Try logging into web interface with same credentials
   - Use app password if available
   
3. **Test server connection**:
   ```bash
   curl -u username:password https://your-server.com/remote.php/dav/files/username/
   ```

4. **Check server logs** (if you have access)

### "Connection failed" or "SSL Error"

For self-signed certificates (not recommended for production):

1. You may need to configure certificate validation
2. Consider using Let's Encrypt for proper certificates
3. Contact your server administrator

### "Upload failed" / "Download failed"

**Possible causes:**
1. No internet connection
2. Server storage quota exceeded
3. File too large (depends on server config)
4. Permission issues with shared folders
5. Server timeout (large files)

**Solutions:**
1. Check internet connection
2. Check server storage quota (Nextcloud: Settings → Personal → Storage)
3. Increase server limits if you control the server
4. Verify folder permissions
5. Try smaller files first

### "Folder not found"

**Solution**: 
- Check that you have write permission on the server
- Try creating the folder manually in web interface first
- Verify folder name doesn't have special characters

### Performance Issues

If sync is slow:

1. **Check server performance**:
   - Server might be overloaded
   - Network connection might be slow
   - Check with other WebDAV clients

2. **Optimize sync**:
   - Use "annotations only" mode for metadata sync
   - Set file size limits
   - Sync during off-peak hours

---

## Advanced Usage

### Self-Hosting Nextcloud

If you want to self-host Nextcloud:

1. **System Requirements**:
   - Linux server (Ubuntu, Debian, etc.)
   - PHP 8.0+
   - MySQL/PostgreSQL
   - 512 MB RAM minimum (2 GB+ recommended)

2. **Installation Options**:
   - Docker: `docker run -d nextcloud`
   - Snap: `snap install nextcloud`
   - Manual: Follow [official guide](https://docs.nextcloud.com/server/latest/admin_manual/installation/)

3. **Configure for AudioBrowser**:
   - Enable PHP fileinfo extension
   - Set upload limits in php.ini:
     ```ini
     upload_max_filesize = 512M
     post_max_size = 512M
     max_execution_time = 300
     ```
   - Configure .htaccess for large files

### Server Configuration

For optimal performance with audio files:

**nginx.conf** (if using nginx):
```nginx
client_max_body_size 512M;
client_body_timeout 300;
```

**Apache .htaccess** (if using Apache):
```apache
php_value upload_max_filesize 512M
php_value post_max_size 512M
php_value max_execution_time 300
```

### Using External Storage

Nextcloud supports external storage backends:
- Amazon S3
- OpenStack Object Storage
- SMB/CIFS
- FTP
- Google Drive (as backend)

Configure in: **Settings** → **Administration** → **External storages**

### Encryption

Nextcloud supports encryption at rest:

1. Enable in: **Settings** → **Administration** → **Security** → **Server-side encryption**
2. Files are encrypted on server
3. Transparent to AudioBrowser
4. Requires additional server resources

---

## Security Best Practices

### Use HTTPS
- Always use `https://` URLs, never `http://`
- Use valid SSL certificates (Let's Encrypt is free)
- Avoid self-signed certificates in production

### App Passwords
- Use app passwords instead of main password
- Revoke app password if device is lost
- Different password for each device

### Two-Factor Authentication
- Enable 2FA on your Nextcloud/ownCloud account
- App passwords work with 2FA
- Protects your account even if password is compromised

### Regular Backups
- Backup your server regularly
- Test restore procedures
- Keep backups in different location

### Server Updates
- Keep Nextcloud/ownCloud updated
- Apply security patches promptly
- Subscribe to security mailing lists

---

## Comparing WebDAV to Other Providers

### vs Google Drive:
- **More control**: You own the server and data
- **Better privacy**: Data doesn't leave your server
- **More complex**: Requires server setup/maintenance
- **Flexible storage**: Unlimited if self-hosted

### vs Dropbox:
- **More privacy**: Your data, your server
- **More work**: Need to manage server
- **Better for teams**: Nextcloud has excellent collaboration features
- **Cost-effective**: Free if self-hosted

### Advantages:
- Full control over your data
- No storage limits (if self-hosted)
- Works with any WebDAV server
- Great for privacy-conscious users
- Nextcloud has many additional features (calendar, contacts, etc.)

### Disadvantages:
- Requires server setup/maintenance
- Need technical knowledge or hosting provider
- Responsible for backups and security
- Slower if server has poor internet connection

---

## FAQ

**Q: Do I need to run my own server?**  
A: No! You can use hosted Nextcloud providers. See [Nextcloud Providers](https://nextcloud.com/providers/).

**Q: Can I use Nextcloud's desktop sync and AudioBrowser together?**  
A: Yes, but be careful with conflicts. AudioBrowser syncs to `/AudioBrowser/` folder, so keep that separate from desktop sync.

**Q: What if my server goes down?**  
A: You still have local files. Sync when server is back up.

**Q: Can I use this with my company's WebDAV server?**  
A: Yes, as long as you have access and appropriate permissions.

**Q: Is this secure?**  
A: As secure as your server configuration. Use HTTPS, strong passwords, and keep software updated.

**Q: Can I sync the same folder to both Nextcloud and Google Drive?**  
A: Yes, but you'll need to manually switch providers in AudioBrowser and sync separately to each.

**Q: What's the maximum file size?**  
A: Depends on your server configuration. Default Nextcloud allows 512 MB, but this can be increased.

---

## Support

For issues or questions:
1. Check this guide's Troubleshooting section
2. Read [Cloud Sync Setup Guide](CLOUD_SYNC_SETUP.md) for general sync info
3. Check Nextcloud documentation: [Nextcloud Docs](https://docs.nextcloud.com/)
4. Check your server logs (if self-hosted)
5. File an issue on GitHub: [BandTools Issues](https://github.com/TheMikaus/BandTools/issues)

---

**Last Updated**: January 2025  
**Version**: 1.0  
**Status**: Production Ready
