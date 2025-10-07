# Google Drive Sync - Example Workflow

This document walks through a typical sync workflow for a band using AudioBrowser.

## Scenario: Three Band Members Sharing Practice Sessions

**Band Members:**
- Alice (drummer) - sets up the sync folder
- Bob (guitarist) - joins and adds annotations
- Charlie (bassist) - joins and downloads sessions

## Initial Setup (Alice - First Time)

1. **Set up Google Drive API credentials**
   - Follow `GOOGLE_DRIVE_SETUP.md`
   - Download `credentials.json` to AudioBrowserAndAnnotation folder

2. **Authorize and create sync folder**
   ```
   - Open AudioBrowser
   - Click "☁ Sync" button
   - Browser opens for Google authorization
   - Sign in and grant permissions
   - Enter folder name: "BandPracticeSessions"
   - App creates folder in Google Drive
   ```

3. **First sync - Upload practice session**
   ```
   Local folder: /Practices/2024-01-15/
   Contains:
     - 01_WarmUp.wav
     - 02_NewSong.wav
     - 03_OldFavorite.wav
     - .audio_notes_Alice.json (Alice's annotations)
     - .provided_names.json (song names)
   
   Sync workflow:
   - Click "☁ Sync"
   - Click "No" for upload option
   - Review dialog shows:
     ☑ .audio_notes_Alice.json (auto-checked)
     ☑ .provided_names.json (auto-checked)
     ☑ 01_WarmUp.wav
     ☑ 02_NewSong.wav
     ☑ 03_OldFavorite.wav
   - Click "Upload Selected"
   - Progress shown: Uploading 5 files...
   - Version updated: Local v1 → Remote v1
   ```

## Bob Joins (First Time)

1. **Set up credentials** (same as Alice)

2. **Authorize with his Google account**

3. **Download practice session**
   ```
   Local folder: /MyPractices/2024-01-15/ (empty)
   
   Sync workflow:
   - Click "☁ Sync"
   - Enter same folder name: "BandPracticeSessions"
   - Status shows: Local v0, Remote v1
   - Click "Yes" for download option
   - Review dialog shows:
     ☑ .audio_notes_Alice.json (auto-checked)
     ☑ .provided_names.json (auto-checked)
     ☐ 01_WarmUp.wav
     ☐ 02_NewSong.wav
     ☐ 03_OldFavorite.wav
   - Bob checks the audio files he wants
   - Click "Download Selected"
   - Files downloaded to local folder
   - Version updated: Local v1
   ```

4. **Bob adds his annotations**
   ```
   - Listens to recordings
   - Adds notes: "Guitar solo at 1:30 needs work"
   - Marks 02_NewSong as "Best Take"
   - Creates file: .audio_notes_Bob.json
   ```

5. **Bob syncs his annotations**
   ```
   - Click "☁ Sync"
   - Click "No" for upload
   - Review shows:
     ☑ .audio_notes_Bob.json (auto-checked, new file)
   - Click "Upload Selected"
   - Version updated: Local v2, Remote v2
   ```

## Alice Gets Bob's Annotations

1. **Check for updates**
   ```
   - Click "☁ Sync"
   - Status shows: Local v1, Remote v2
   - Click "Yes" for download
   - Review shows:
     ☑ .audio_notes_Bob.json (auto-checked)
   - Click "Download Selected"
   - Alice can now see Bob's annotations in different color
   - Version updated: Local v2
   ```

## Charlie Downloads Everything (New Member)

1. **Set up and authorize**

2. **Download full session**
   ```
   - Click "☁ Sync"
   - Enter: "BandPracticeSessions"
   - Status: Local v0, Remote v2
   - Click "Yes" for download
   - Review shows all files from Alice and Bob
   - Select all audio files he wants
   - Downloads metadata + selected audio
   - Version: Local v2
   ```

## Regular Practice Workflow

### After Each Practice:

1. **Alice records new session**
   ```
   Creates: /Practices/2024-01-22/
     - 01_NewSongV2.wav
     - 02_CoverSong.wav
     - .audio_notes_Alice.json
     - .provided_names.json
   ```

2. **Alice uploads**
   ```
   - Click "☁ Sync"
   - Upload new files
   - Remote v3
   ```

3. **Bob and Charlie sync**
   ```
   - Click "☁ Sync"
   - Download new metadata (auto)
   - Choose which recordings to download
   - Add their annotations
   - Upload annotations
   - Remote v4, v5
   ```

## Common Scenarios

### Scenario: Alice Deletes a File Locally
```
- Alice deletes 03_OldFavorite.wav
- On next sync: NOT automatically deleted from remote
- Currently: Only additions are synced
- Manual cleanup needed on Google Drive if desired
```

### Scenario: Bob Tries to Modify Alice's Annotations
```
- Bob opens .audio_notes_Alice.json locally
- Bob modifies and tries to upload
- Review dialog: 
  ☐ .audio_notes_Alice.json (disabled, grayed out)
  Note: "Cannot modify other users' files"
- Upload blocked for that file
```

### Scenario: Version Conflict Prevention
```
Situation: 
- Alice has Local v2, Remote v3
- Alice tries to upload without downloading first

Current behavior:
- Alice clicks "☁ Sync"
- Status shows: Local v2, Remote v3 (remote ahead)
- Alice can choose Upload or Download
- If Upload: New version created (v4)
- If Download first: Gets to v3, then can upload as v4

Future improvement:
- Could add automatic merge or conflict detection
```

### Scenario: Multiple Folders
```
Each practice folder has its own .sync_version.json:
- /Practices/2024-01-15/.sync_version.json (v3)
- /Practices/2024-01-22/.sync_version.json (v2)
- Each syncs independently
- Need to be in the folder when syncing
```

## Tips and Best Practices

1. **Sync Often**
   - Download before adding annotations
   - Upload after adding annotations
   - Reduces version conflicts

2. **Communicate with Band**
   - Let others know when you upload new recordings
   - Use folder notes to leave messages

3. **Selective Download**
   - Metadata syncs automatically (small files)
   - Choose which audio files to download (large files)
   - Save bandwidth and disk space

4. **Backup Locally**
   - Google Drive sync is NOT a backup system
   - Keep local backups of important recordings
   - App has built-in .backup/ system for metadata

5. **Check Status First**
   - Before syncing, check version numbers
   - "Remote ahead" = new changes available
   - "Local ahead" = you have unpushed changes

6. **Handle Large Files**
   - Audio files can be large (especially WAV)
   - Consider converting to MP3 before uploading
   - Or upload selectively (just the best takes)

## Troubleshooting Common Issues

### "Authentication Failed"
```
Solution:
1. Delete token.json
2. Click "☁ Sync" again
3. Re-authorize in browser
```

### "Cannot Find Folder"
```
Solution:
1. Check folder name spelling
2. Or create new folder with different name
3. Update SETTINGS_KEY_GDRIVE_FOLDER if needed
```

### "Upload Failed"
```
Possible causes:
- Network connection issues
- File in use (close audio player)
- Insufficient Google Drive storage

Solution:
- Check log file: audiobrowser.log
- Try individual files
- Check Google Drive quota
```

### "Version Mismatch"
```
If versions seem wrong:
- Check .sync_version.json in folder
- Manually edit if needed (last resort)
- Or delete and start fresh (recreate from v0)
```

## Privacy Considerations

- **What's Shared**: Only files you explicitly select
- **What's Private**: Your local backups, waveform cache
- **Annotations**: Each user has their own file
- **Google Drive**: Files are in your band's shared folder
- **Access Control**: Managed by Google Drive sharing settings

## Advanced: Service Account Setup

For automated/headless sync (e.g., on a server):

1. Use service account instead of OAuth
2. Download `service_account.json`
3. Share Drive folder with service account email
4. App will use service account automatically if found

See `GOOGLE_DRIVE_SETUP.md` Method 2 for details.
