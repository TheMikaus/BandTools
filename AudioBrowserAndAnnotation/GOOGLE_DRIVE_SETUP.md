# Google Drive Integration Setup

The AudioBrowser now supports syncing annotations to Google Drive for backup and collaboration. This feature allows band members to share annotation files automatically.

## Setup Instructions

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Drive API for your project

### 2. Create OAuth 2.0 Credentials

1. Go to "Credentials" in the Google Cloud Console
2. Click "Create Credentials" → "OAuth 2.0 Client IDs"
3. Choose "Desktop application" as the application type
4. Note down your Client ID and Client Secret

### 3. Configure Environment Variables

Set these environment variables before starting the application:

```bash
export GDRIVE_CLIENT_ID="your-client-id.googleusercontent.com"
export GDRIVE_CLIENT_SECRET="your-client-secret"
```

Or on Windows:
```cmd
set GDRIVE_CLIENT_ID=your-client-id.googleusercontent.com
set GDRIVE_CLIENT_SECRET=your-client-secret
```

### 4. Setup in Application

1. Start the AudioBrowser application
2. Click "Setup Google Drive…" in the toolbar
3. Follow the OAuth authentication flow in your web browser
4. Enter the Google Drive folder ID where you want to store annotations
5. Enable "Sync on startup" if desired

## Finding Google Drive Folder ID

1. Open Google Drive in your web browser
2. Navigate to the folder where you want to store annotations
3. Look at the URL - the folder ID is the long string after `/folders/`
   - Example: `https://drive.google.com/drive/folders/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74mMjNhFlrI`
   - Folder ID: `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74mMjNhFlrI`

## Features

- **Automatic sync on startup**: Optionally sync annotations when the app starts
- **Manual sync**: Click "Sync Annotations" to sync immediately  
- **Conflict resolution**: Compares file modification times to determine sync direction
- **Credential management**: Easily setup or clear Google Drive authentication

## Security Notes

- OAuth credentials are stored securely using Qt's QSettings
- Only files in the specified Google Drive folder are accessed
- The application uses minimal Google Drive API permissions (`drive.file` scope)

## Troubleshooting

### "Google Drive (Not Available)"
- Make sure you've installed the Google API dependencies:
  ```bash
  pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
  ```

### "OAuth Configuration Required"
- Set the environment variables `GDRIVE_CLIENT_ID` and `GDRIVE_CLIENT_SECRET`
- Make sure you've enabled the Google Drive API in your Google Cloud project

### "Failed to authenticate"
- Check your internet connection
- Verify your OAuth credentials are correct
- Make sure the Google Drive API is enabled for your project

### "Cannot access folder"
- Verify the folder ID is correct
- Make sure you have write access to the folder
- Check that you're authenticated with the correct Google account