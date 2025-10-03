# Google Drive Sync Setup Guide

This guide explains how to set up Google Drive sync for the AudioBrowser application.

## Overview

The Google Drive sync feature allows you to synchronize your band practice audio files and annotations with a Google Drive folder. This enables:
- Sharing recordings and annotations with band members
- Backing up your practice sessions to the cloud
- Accessing your files from multiple machines

## Prerequisites

- A Google account
- Python 3.7 or higher
- Internet connection

## Setting Up Google Drive API Access

The AudioBrowser uses a simplified authentication approach that doesn't require app registration. Instead, it uses OAuth 2.0 with local credentials.

### Method 1: Using OAuth Desktop Flow (Recommended)

1. **Visit Google Cloud Console**
   - Go to https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create a New Project**
   - Click "Select a project" at the top
   - Click "New Project"
   - Name it something like "AudioBrowser Sync"
   - Click "Create"

3. **Enable Google Drive API**
   - In the left menu, go to "APIs & Services" > "Library"
   - Search for "Google Drive API"
   - Click on it and press "Enable"

4. **Configure OAuth Consent Screen**
   - Go to "APIs & Services" > "OAuth consent screen"
   - Select "External" user type
   - Click "Create"
   - Fill in the required fields:
     - App name: "AudioBrowser Sync"
     - User support email: Your email
     - Developer contact: Your email
   - Click "Save and Continue"
   - On the Scopes page, click "Add or Remove Scopes"
   - Filter for "Google Drive API" and add:
     - `.../auth/drive.file` (View and manage Google Drive files created by this app)
   - Click "Update" then "Save and Continue"
   - On Test users page, add your Google account email
   - Click "Save and Continue"

5. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Desktop app" as application type
   - Name it "AudioBrowser Desktop Client"
   - Click "Create"
   - Click "Download JSON" to download the credentials file
   - Save this file as `credentials.json` in the AudioBrowserAndAnnotation directory
   - **Note**: See `credentials.json.example` for the expected file format

### Method 2: Using Service Account (Alternative)

This method is useful for automated/headless scenarios:

1. Follow steps 1-3 from Method 1
2. Go to "APIs & Services" > "Credentials"
3. Click "Create Credentials" > "Service Account"
4. Name it "AudioBrowser Service"
5. Click "Create and Continue"
6. Skip optional steps and click "Done"
7. Click on the created service account
8. Go to "Keys" tab
9. Click "Add Key" > "Create new key"
10. Select "JSON" and click "Create"
11. Save the downloaded file as `service_account.json` in the AudioBrowserAndAnnotation directory
12. Share your Google Drive sync folder with the service account email (found in the JSON file)

## Using the Sync Feature

1. **First Time Setup**
   - Place your `credentials.json` file in the AudioBrowserAndAnnotation directory
   - Click the "Sync with Google Drive" button in the toolbar
   - The first time, a browser window will open asking you to authorize the app
   - Sign in and grant permissions
   - A `token.json` file will be created to remember your authorization

2. **Selecting Sync Folder**
   - In the sync dialog, click "Select Google Drive Folder"
   - Browse to or create a folder in your Google Drive
   - This folder will be your remote root folder

3. **Manual Sync**
   - Click "Check for Updates" to compare local and remote files
   - Review the list of changes (additions, deletions, updates)
   - Check the boxes next to changes you want to apply
   - Click "Sync Down" to download changes from Google Drive
   - Click "Sync Up" to upload changes to Google Drive

## What Gets Synced

**Always Synced:**
- Annotation files (`.audio_notes_*.json`)
- Song name mappings (`.provided_names.json`)
- Duration cache (`.duration_cache.json`)
- Audio fingerprints (`.audio_fingerprints.json`)
- User color mappings (`.user_colors.json`)

**User-Selective Sync:**
- Audio files (`.wav`, `.mp3`)
  - You choose which files to upload/download

**Never Synced:**
- Backup folders (`.backup/`)
- Waveform cache folders (`.waveforms/`)
- Temporary files

## User Permissions

- **Annotation Files**: You can only upload/modify your own annotation files (`.audio_notes_<YourName>.json`)
- **Other Users' Annotations**: You can download other users' annotations, but cannot modify them
- **Shared Files**: All other metadata files can be modified by anyone

## Version Tracking

The sync system maintains a `.sync_version.json` file in both local and remote directories:
- Tracks the current version number
- Records all operations performed in each version
- Enables efficient incremental sync
- Prevents conflicts by tracking what changed

## Troubleshooting

### "credentials.json not found"
- Make sure you've downloaded the OAuth credentials from Google Cloud Console
- Place the file in the same directory as audio_browser.py

### "Permission denied" errors
- Re-authorize the app by deleting `token.json` and syncing again
- Make sure the Google Drive API is enabled in your project

### "Service account access denied"
- If using a service account, make sure you've shared the Drive folder with the service account email
- Check that the service account has the correct permissions

### Sync conflicts
- The app will never automatically delete or overwrite files without your confirmation
- Always review the sync changes before applying them
- If in doubt, create a local backup before syncing

## Privacy and Security

- Your Google Drive credentials are stored locally in `token.json` (keep this file secure)
- The app only accesses files in the sync folder you specify
- No data is sent to third parties
- All sync operations are logged for transparency

## Support

For issues or questions:
- Check the GitHub issues: https://github.com/TheMikaus/BandTools/issues
- Review the sync operation logs in `audiobrowser.log`
