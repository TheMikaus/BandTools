#!/usr/bin/env python3
"""
Google Drive sync module for AudioBrowser-QML.

This module provides Google Drive synchronization functionality including:
- OAuth authentication
- Version-based sync tracking
- File upload/download with user confirmation
- Operation logging
- QML integration via Qt signals
"""

from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set, Any
from datetime import datetime
import logging

# PyQt6 imports for QML integration
from PyQt6.QtCore import pyqtSignal, pyqtSlot

# Import base class and shared structures
from .cloud_sync_base import (
    CloudSyncBase, SyncHistory, SyncRules, SyncVersion,
    SYNC_EXCLUDED, VERSION_FILE, SYNC_HISTORY_FILE, SYNC_RULES_FILE, ANNOTATION_PATTERNS
)

# Google Drive API imports (with auto-installation)
def _ensure_gdrive_import():
    """Ensure Google Drive libraries are available, installing if needed."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
        return True
    except ImportError:
        print("Google Drive API not found. Installing google-api-python-client and google-auth...")
        import subprocess
        import sys
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "google-api-python-client", "google-auth-httplib2", "google-auth-oauthlib"])
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
            print("Google Drive API installed successfully")
            return True
        except Exception as e:
            print(f"Failed to install Google Drive API: {e}")
            return False

# Try to import Google Drive API
GDRIVE_AVAILABLE = _ensure_gdrive_import()
if GDRIVE_AVAILABLE:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# Logging setup
logger = logging.getLogger(__name__)

# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive.file']


class GDriveSync(CloudSyncBase):
    """Google Drive synchronization manager with QML integration."""
    
    def __init__(self, credentials_path: Path, token_path: Path, parent=None):
        """
        Initialize Google Drive sync.
        
        Args:
            credentials_path: Path to OAuth credentials file
            token_path: Path to store/load authentication token
            parent: QObject parent (optional)
        """
        super().__init__(parent)
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.creds: Optional[Credentials] = None
        self.service = None
        self.current_user: str = os.getenv('USER') or os.getenv('USERNAME') or 'Unknown'
    
    @pyqtSlot(result=bool)
    def isAvailable(self) -> bool:
        """Check if Google Drive API libraries are available."""
        return GDRIVE_AVAILABLE
    
    @pyqtSlot(result=bool)
    def isAuthenticated(self) -> bool:
        """Check if currently authenticated with Google Drive."""
        return self.service is not None
    
    @pyqtSlot(result=str)
    def getCurrentUser(self) -> str:
        """Get current username for sync operations."""
        return self.current_user
    
    @pyqtSlot(result=bool)
    def authenticate(self) -> bool:
        """
        Authenticate with Google Drive API.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Load existing token if available
            if self.token_path.exists():
                self.creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)
            
            # Refresh or get new credentials if needed
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if not self.credentials_path.exists():
                        error_msg = f"Credentials file not found: {self.credentials_path}"
                        logger.error(error_msg)
                        self.authenticationStatusChanged.emit(False, error_msg)
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.credentials_path), SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)
                
                # Save the credentials for next time
                self.token_path.write_text(self.creds.to_json())
            
            # Build the service
            self.service = build('drive', 'v3', credentials=self.creds)
            logger.info("Successfully authenticated with Google Drive")
            self.authenticationStatusChanged.emit(True, "Successfully authenticated with Google Drive")
            return True
            
        except Exception as e:
            error_msg = f"Authentication failed: {e}"
            logger.error(error_msg)
            self.authenticationStatusChanged.emit(False, error_msg)
            return False
    
    @pyqtSlot(str, result=str)
    def select_remote_folder(self, folder_name: Optional[str] = None) -> Optional[str]:
        """
        Select or create a remote folder for sync.
        
        Args:
            folder_name: Name of folder to find/create
            
        Returns:
            Folder ID if successful, None otherwise
        """
        if not self.service:
            logger.error("Not authenticated")
            return None
        
        try:
            if folder_name:
                # Search for existing folder
                query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
                results = self.service.files().list(
                    q=query,
                    spaces='drive',
                    fields='files(id, name)'
                ).execute()
                
                files = results.get('files', [])
                if files:
                    self.remote_folder_id = files[0]['id']
                    logger.info(f"Found existing folder: {folder_name}")
                    self.folderSelected.emit(self.remote_folder_id, folder_name)
                    return self.remote_folder_id
                
                # Create new folder
                file_metadata = {
                    'name': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                folder = self.service.files().create(
                    body=file_metadata,
                    fields='id'
                ).execute()
                
                self.remote_folder_id = folder.get('id')
                logger.info(f"Created new folder: {folder_name}")
                self.folderSelected.emit(self.remote_folder_id, folder_name)
                return self.remote_folder_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error selecting remote folder: {e}")
            return None
    
    def get_remote_version(self) -> Optional[SyncVersion]:
        """Get version information from remote."""
        if not self.service or not self.remote_folder_id:
            return None
        
        try:
            # Search for version file in remote folder
            query = f"name='{VERSION_FILE}' and '{self.remote_folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            files = results.get('files', [])
            if not files:
                # No version file exists yet
                return SyncVersion(version=0)
            
            # Download and parse version file
            file_id = files[0]['id']
            request = self.service.files().get_media(fileId=file_id)
            
            import io
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            fh.seek(0)
            version_data = json.loads(fh.read().decode('utf-8'))
            return SyncVersion.from_dict(version_data)
            
        except Exception as e:
            logger.error(f"Error reading remote version: {e}")
            return None
    
    def update_remote_version(self, version: SyncVersion) -> bool:
        """Update version file on remote."""
        if not self.service or not self.remote_folder_id:
            return False
        
        try:
            # Search for existing version file
            query = f"name='{VERSION_FILE}' and '{self.remote_folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id)'
            ).execute()
            
            files = results.get('files', [])
            
            # Write version data to temp file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
                json.dump(version.to_dict(), f, indent=2)
                temp_path = f.name
            
            try:
                media = MediaFileUpload(temp_path, mimetype='application/json')
                
                if files:
                    # Update existing file
                    file_id = files[0]['id']
                    self.service.files().update(
                        fileId=file_id,
                        media_body=media
                    ).execute()
                else:
                    # Create new file
                    file_metadata = {
                        'name': VERSION_FILE,
                        'parents': [self.remote_folder_id]
                    }
                    self.service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id'
                    ).execute()
                
                logger.info(f"Updated remote version to {version.version}")
                return True
                
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except:
                    pass
            
        except Exception as e:
            logger.error(f"Error updating remote version: {e}")
            return False
    
    def list_remote_files(self) -> List[Dict[str, Any]]:
        """List all files in the remote folder (non-recursive)."""
        if not self.service or not self.remote_folder_id:
            return []
        
        try:
            query = f"'{self.remote_folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, mimeType, modifiedTime, size)',
                pageSize=1000
            ).execute()
            
            return results.get('files', [])
            
        except Exception as e:
            logger.error(f"Error listing remote files: {e}")
            return []
    
    @pyqtSlot(str, str, result=bool)
    def upload_file(self, local_path: Path, remote_name: Optional[str] = None) -> bool:
        """
        Upload a file to remote folder.
        
        Args:
            local_path: Path to local file (can be string from QML)
            remote_name: Optional different name for remote file
            
        Returns:
            True if successful
        """
        # Convert string path from QML to Path
        if isinstance(local_path, str):
            local_path = Path(local_path)
            
        if not self.service or not self.remote_folder_id:
            self.syncError.emit("Not authenticated or no folder selected")
            return False
        
        if not local_path.exists():
            error_msg = f"Local file not found: {local_path}"
            logger.error(error_msg)
            self.syncError.emit(error_msg)
            return False
        
        try:
            remote_name = remote_name or local_path.name
            
            # Check if file already exists
            query = f"name='{remote_name}' and '{self.remote_folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id)'
            ).execute()
            
            files = results.get('files', [])
            
            # Determine mimetype
            mimetype = 'application/octet-stream'
            if local_path.suffix.lower() == '.json':
                mimetype = 'application/json'
            elif local_path.suffix.lower() in ['.wav', '.mp3']:
                mimetype = f'audio/{local_path.suffix[1:]}'
            
            media = MediaFileUpload(str(local_path), mimetype=mimetype, resumable=True)
            
            if files:
                # Update existing file
                file_id = files[0]['id']
                self.syncProgress.emit(f"Updating: {remote_name}")
                self.service.files().update(
                    fileId=file_id,
                    media_body=media
                ).execute()
                logger.info(f"Updated remote file: {remote_name}")
            else:
                # Create new file
                file_metadata = {
                    'name': remote_name,
                    'parents': [self.remote_folder_id]
                }
                self.syncProgress.emit(f"Uploading: {remote_name}")
                self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                logger.info(f"Uploaded new file: {remote_name}")
            
            return True
            
        except Exception as e:
            error_msg = f"Error uploading file {local_path}: {e}"
            logger.error(error_msg)
            self.syncError.emit(error_msg)
            return False
    
    def download_file(self, remote_name: str, local_path: Path) -> bool:
        """
        Download a file from remote folder.
        
        Args:
            remote_name: Name of file on remote
            local_path: Where to save the file locally
            
        Returns:
            True if successful
        """
        if not self.service or not self.remote_folder_id:
            return False
        
        try:
            # Find the file
            query = f"name='{remote_name}' and '{self.remote_folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, mimeType)'
            ).execute()
            
            files = results.get('files', [])
            if not files:
                logger.error(f"Remote file not found: {remote_name}")
                return False
            
            file_id = files[0]['id']
            
            # Download the file
            request = self.service.files().get_media(fileId=file_id)
            
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            import io
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            # Write to local file
            fh.seek(0)
            local_path.write_bytes(fh.read())
            logger.info(f"Downloaded file: {remote_name} -> {local_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading file {remote_name}: {e}")
            return False
    
    def delete_remote_file(self, remote_name: str) -> bool:
        """Delete a file from remote folder."""
        if not self.service or not self.remote_folder_id:
            return False
        
        try:
            query = f"name='{remote_name}' and '{self.remote_folder_id}' in parents and trashed=false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id)'
            ).execute()
            
            files = results.get('files', [])
            if not files:
                logger.warning(f"File not found for deletion: {remote_name}")
                return True  # Already gone
            
            file_id = files[0]['id']
            self.service.files().delete(fileId=file_id).execute()
            logger.info(f"Deleted remote file: {remote_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting remote file {remote_name}: {e}")
            return False
    
    def delete_remote_folder(self) -> bool:
        """
        Delete entire remote folder and all its contents.
        
        Returns:
            True if successful
        """
        if not self.service or not self.remote_folder_id:
            return False
        
        try:
            self.service.files().delete(fileId=self.remote_folder_id).execute()
            logger.info(f"Deleted remote folder: {self.remote_folder_id}")
            self.remote_folder_id = None
            return True
            
        except Exception as e:
            logger.error(f"Error deleting remote folder: {e}")
            return False
    
    def get_remote_file_names(self) -> Set[str]:
        """
        Get set of filenames that exist on remote.
        
        Returns:
            Set of filenames (not full paths)
        """
        remote_files = self.list_remote_files()
        return {f['name'] for f in remote_files if should_sync_file(f['name'])}
    
    def can_user_modify(self, filename: str) -> bool:
        """
        Check if current user can modify a file.
        
        Users can modify:
        - Their own annotation files
        - Non-user-specific metadata files
        
        Users cannot modify:
        - Other users' annotation files
        """
        # Check if it's a user-specific annotation file
        if filename.startswith('.audio_notes_') and filename.endswith('.json'):
            # Extract username from filename
            username_part = filename[13:-5]  # Remove prefix and suffix
            # User can only modify their own annotations
            return username_part == self.current_user
        
        # All other files can be modified
        return True
    
    @pyqtSlot(str, bool, result=bool)
    def performSync(self, local_directory: str, upload: bool = True) -> bool:
        """
        Perform a sync operation (QML-friendly).
        
        Args:
            local_directory: Path to local directory to sync (string from QML)
            upload: True to upload local changes, False to download remote changes
            
        Returns:
            True if sync initiated successfully
        """
        if not self.isAuthenticated():
            self.syncError.emit("Not authenticated with Google Drive")
            return False
        
        if not self.remote_folder_id:
            self.syncError.emit("No remote folder selected")
            return False
        
        try:
            local_dir = Path(local_directory)
            if not local_dir.exists():
                self.syncError.emit(f"Local directory not found: {local_directory}")
                return False
            
            self.syncProgress.emit("Analyzing files...")
            
            # Get remote files
            remote_files = self.list_remote_files()
            
            # Compare local and remote
            local_only, remote_only, both = compare_files(local_dir, remote_files)
            
            # Perform sync based on direction
            success_count = 0
            total_count = 0
            
            if upload:
                # Upload local files
                files_to_sync = list(local_only) + list(both)
                total_count = len(files_to_sync)
                
                for i, filename in enumerate(files_to_sync):
                    if self.upload_file(local_dir / filename):
                        success_count += 1
                    self.syncProgress.emit(f"Uploading: {i+1}/{total_count}")
                
                self.syncCompleted.emit(True, f"Uploaded {success_count}/{total_count} files", success_count)
            else:
                # Download remote files
                files_to_sync = list(remote_only) + list(both)
                total_count = len(files_to_sync)
                
                for i, filename in enumerate(files_to_sync):
                    if self.download_file(filename, local_dir / filename):
                        success_count += 1
                    self.syncProgress.emit(f"Downloading: {i+1}/{total_count}")
                
                self.syncCompleted.emit(True, f"Downloaded {success_count}/{total_count} files", success_count)
            
            return True
            
        except Exception as e:
            error_msg = f"Sync failed: {e}"
            logger.error(error_msg)
            self.syncError.emit(error_msg)
            return False


def load_local_version(version_path: Path) -> SyncVersion:
    """Load local version file."""
    if version_path.exists():
        try:
            data = json.loads(version_path.read_text())
            return SyncVersion.from_dict(data)
        except Exception as e:
            logger.error(f"Error loading local version: {e}")
    
    return SyncVersion(version=0)


def save_local_version(version_path: Path, version: SyncVersion) -> bool:
    """Save local version file."""
    try:
        version_path.write_text(json.dumps(version.to_dict(), indent=2))
        return True
    except Exception as e:
        logger.error(f"Error saving local version: {e}")
        return False


def should_sync_file(filename: str) -> bool:
    """Check if a file should be synced."""
    # Exclude hidden files except our metadata files
    if filename.startswith('.'):
        # Allow our metadata files
        return any(filename.startswith(pattern) or filename == pattern 
                  for pattern in ANNOTATION_PATTERNS)
    
    # Include audio files
    if filename.lower().endswith(('.wav', '.mp3', '.wave')):
        return True
    
    return False


def get_sync_files(directory: Path) -> Set[str]:
    """
    Get list of files that should be synced from a directory, including subdirectories.
    Returns paths relative to the root directory.
    """
    sync_files = set()
    
    if not directory.exists():
        return sync_files
    
    def scan_directory(current_dir: Path, relative_prefix: str = ""):
        """Recursively scan directory and add syncable files."""
        for item in current_dir.iterdir():
            # Skip excluded directories
            if item.is_dir():
                if item.name not in SYNC_EXCLUDED:
                    # Recursively scan subdirectory
                    subdir_prefix = f"{relative_prefix}{item.name}/" if relative_prefix else f"{item.name}/"
                    scan_directory(item, subdir_prefix)
                continue
            
            # Check if file should be synced
            if should_sync_file(item.name):
                # Add file with relative path from root
                relative_path = f"{relative_prefix}{item.name}"
                sync_files.add(relative_path)
    
    scan_directory(directory)
    return sync_files


def compare_files(local_dir: Path, remote_files: List[Dict]) -> Tuple[Set[str], Set[str], Set[str]]:
    """
    Compare local and remote files.
    
    Returns:
        (local_only, remote_only, both)
    """
    local_files = get_sync_files(local_dir)
    remote_names = {f['name'] for f in remote_files if should_sync_file(f['name'])}
    
    local_only = local_files - remote_names
    remote_only = remote_names - local_files
    both = local_files & remote_names
    
    return local_only, remote_only, both


def deduplicate_operations(operations: List[Dict]) -> List[Dict]:
    """
    Deduplicate operations to get final state.
    
    For each file, only keep the most recent operation.
    """
    # Track the latest operation for each path
    latest_ops: Dict[str, Dict] = {}
    
    for op in operations:
        path = op['path']
        latest_ops[path] = op
    
    return list(latest_ops.values())


def load_sync_history(local_dir: Path) -> SyncHistory:
    """Load sync history from local directory."""
    history_path = local_dir / SYNC_HISTORY_FILE
    if history_path.exists():
        try:
            data = json.loads(history_path.read_text())
            return SyncHistory.from_dict(data)
        except Exception as e:
            logger.error(f"Error loading sync history: {e}")
    
    return SyncHistory()


def save_sync_history(local_dir: Path, history: SyncHistory):
    """Save sync history to local directory."""
    history_path = local_dir / SYNC_HISTORY_FILE
    try:
        history_path.write_text(json.dumps(history.to_dict(), indent=2))
    except Exception as e:
        logger.error(f"Error saving sync history: {e}")


def load_sync_rules(local_dir: Path) -> SyncRules:
    """Load sync rules from local directory."""
    rules_path = local_dir / SYNC_RULES_FILE
    if rules_path.exists():
        try:
            data = json.loads(rules_path.read_text())
            return SyncRules.from_dict(data)
        except Exception as e:
            logger.error(f"Error loading sync rules: {e}")
    
    return SyncRules()


def save_sync_rules(local_dir: Path, rules: SyncRules):
    """Save sync rules to local directory."""
    rules_path = local_dir / SYNC_RULES_FILE
    try:
        rules_path.write_text(json.dumps(rules.to_dict(), indent=2))
    except Exception as e:
        logger.error(f"Error saving sync rules: {e}")
