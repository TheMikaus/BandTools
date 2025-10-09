#!/usr/bin/env python3
"""
Dropbox sync module for AudioBrowser-QML.

This module provides Dropbox synchronization functionality.
"""

from __future__ import annotations
import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

from PyQt6.QtCore import pyqtSlot

from cloud_sync_base import (
    CloudSyncBase, SyncHistory, SyncRules, SyncVersion,
    SYNC_EXCLUDED, VERSION_FILE, SYNC_HISTORY_FILE, SYNC_RULES_FILE
)

# Dropbox SDK imports (will be auto-installed if needed)
try:
    import dropbox
    from dropbox.exceptions import AuthError, ApiError
    from dropbox.files import WriteMode
    DROPBOX_AVAILABLE = True
except ImportError:
    DROPBOX_AVAILABLE = False

# Logging setup
logger = logging.getLogger(__name__)


class DropboxSync(CloudSyncBase):
    """Dropbox synchronization manager with QML integration."""
    
    def __init__(self, token_path: Path, parent=None):
        """
        Initialize Dropbox sync.
        
        Args:
            token_path: Path to store/load Dropbox access token
            parent: QObject parent (optional)
        """
        super().__init__(parent)
        self.token_path = token_path
        self.access_token: Optional[str] = None
        self.dbx: Optional[dropbox.Dropbox] = None
        self.remote_folder_path: Optional[str] = None
        self.current_user: str = os.getenv('USER') or os.getenv('USERNAME') or 'Unknown'
        
        # Try to load existing token
        self._load_token()
    
    def _load_token(self) -> bool:
        """Load access token from file."""
        try:
            if self.token_path.exists():
                with open(self.token_path, 'r') as f:
                    data = json.load(f)
                    self.access_token = data.get('access_token')
                    if self.access_token:
                        self.dbx = dropbox.Dropbox(self.access_token)
                        return True
        except Exception as e:
            logger.error(f"Failed to load Dropbox token: {e}")
        return False
    
    def _save_token(self) -> bool:
        """Save access token to file."""
        try:
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, 'w') as f:
                json.dump({'access_token': self.access_token}, f)
            return True
        except Exception as e:
            logger.error(f"Failed to save Dropbox token: {e}")
            return False
    
    @pyqtSlot(result=bool)
    def isAvailable(self) -> bool:
        """Check if Dropbox SDK is available."""
        return DROPBOX_AVAILABLE
    
    @pyqtSlot(result=bool)
    def isAuthenticated(self) -> bool:
        """Check if authenticated with Dropbox."""
        if not self.dbx:
            return False
        try:
            self.dbx.users_get_current_account()
            return True
        except Exception:
            return False
    
    @pyqtSlot(str, result=bool)
    def setAccessToken(self, token: str) -> bool:
        """
        Set Dropbox access token (called from QML).
        
        Args:
            token: Dropbox access token
            
        Returns:
            bool: True if token is valid, False otherwise
        """
        try:
            self.access_token = token
            self.dbx = dropbox.Dropbox(token)
            
            # Verify token by getting account info
            account = self.dbx.users_get_current_account()
            
            # Save token
            self._save_token()
            
            self.authenticationStatusChanged.emit(True, f"Authenticated as {account.name.display_name}")
            return True
        except Exception as e:
            error_msg = f"Authentication failed: {str(e)}"
            self.authenticationStatusChanged.emit(False, error_msg)
            logger.error(error_msg)
            return False
    
    @pyqtSlot(result=bool)
    def authenticate(self) -> bool:
        """
        Authenticate with Dropbox.
        Note: For Dropbox, user must manually obtain access token from Dropbox App Console.
        This method just checks if already authenticated.
        """
        if self.isAuthenticated():
            try:
                account = self.dbx.users_get_current_account()
                self.authenticationStatusChanged.emit(True, f"Already authenticated as {account.name.display_name}")
                return True
            except Exception:
                pass
        
        self.authenticationStatusChanged.emit(
            False, 
            "Please set access token using 'Set Access Token' button"
        )
        return False
    
    @pyqtSlot(str, result=str)
    def select_remote_folder(self, folder_name: Optional[str] = None) -> Optional[str]:
        """
        Select or create a remote folder on Dropbox.
        
        Args:
            folder_name: Name of folder (will be created in /Apps/AudioBrowser/)
            
        Returns:
            str: Folder path if successful, None otherwise
        """
        if not self.isAuthenticated():
            self.syncError.emit("Not authenticated with Dropbox")
            return None
        
        try:
            # Dropbox folder structure: /Apps/AudioBrowser/[folder_name]
            folder_path = f"/Apps/AudioBrowser/{folder_name}" if folder_name else "/Apps/AudioBrowser"
            
            # Try to create folder (will fail silently if exists)
            try:
                self.dbx.files_create_folder_v2(folder_path)
            except ApiError as e:
                if e.error.is_path() and e.error.get_path().is_conflict():
                    # Folder already exists, that's fine
                    pass
                else:
                    raise
            
            self.remote_folder_path = folder_path
            self.folderSelected.emit(folder_name or "AudioBrowser", folder_path)
            return folder_path
            
        except Exception as e:
            error_msg = f"Failed to select/create folder: {str(e)}"
            self.syncError.emit(error_msg)
            logger.error(error_msg)
            return None
    
    def upload_file(self, local_path: Path, remote_name: Optional[str] = None) -> bool:
        """Upload a file to Dropbox."""
        if not self.isAuthenticated() or not self.remote_folder_path:
            return False
        
        try:
            if not local_path.exists():
                return False
            
            remote_name = remote_name or local_path.name
            remote_path = f"{self.remote_folder_path}/{remote_name}"
            
            # Read file and upload
            with open(local_path, 'rb') as f:
                file_data = f.read()
            
            # Upload with overwrite mode
            self.dbx.files_upload(
                file_data,
                remote_path,
                mode=WriteMode('overwrite')
            )
            
            self.syncProgress.emit(f"Uploaded: {remote_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload {local_path}: {e}")
            return False
    
    def download_file(self, remote_name: str, local_path: Path) -> bool:
        """Download a file from Dropbox."""
        if not self.isAuthenticated() or not self.remote_folder_path:
            return False
        
        try:
            remote_path = f"{self.remote_folder_path}/{remote_name}"
            
            # Download file
            metadata, response = self.dbx.files_download(remote_path)
            
            # Save to local path
            local_path.parent.mkdir(parents=True, exist_ok=True)
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            self.syncProgress.emit(f"Downloaded: {remote_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download {remote_name}: {e}")
            return False
    
    def list_remote_files(self) -> List[Dict[str, Any]]:
        """List all files in the remote Dropbox folder."""
        if not self.isAuthenticated() or not self.remote_folder_path:
            return []
        
        try:
            files = []
            result = self.dbx.files_list_folder(self.remote_folder_path)
            
            while True:
                for entry in result.entries:
                    if hasattr(entry, 'name'):  # Is a file
                        files.append({
                            'name': entry.name,
                            'size': getattr(entry, 'size', 0),
                            'modified_time': getattr(entry, 'client_modified', None),
                            'id': getattr(entry, 'id', '')
                        })
                
                if not result.has_more:
                    break
                result = self.dbx.files_list_folder_continue(result.cursor)
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to list remote files: {e}")
            return []
    
    def get_remote_file_names(self):
        """Get set of filenames that exist on remote (for compatibility)."""
        remote_files = self.list_remote_files()
        return {f['name'] for f in remote_files}
    
    @pyqtSlot(str, bool, result=bool)
    def performSync(self, directory: str, upload: bool) -> bool:
        """Perform sync operation (upload or download)."""
        if not self.isAuthenticated() or not self.remote_folder_path:
            self.syncError.emit("Not authenticated or no folder selected")
            return False
        
        try:
            local_dir = Path(directory)
            if not local_dir.exists():
                self.syncError.emit("Local directory does not exist")
                return False
            
            # Load sync rules
            rules_file = local_dir / SYNC_RULES_FILE
            if rules_file.exists():
                with open(rules_file, 'r') as f:
                    rules = SyncRules.from_dict(json.load(f))
            else:
                rules = SyncRules()
            
            files_synced = 0
            
            if upload:
                # Upload local files to Dropbox
                for file_path in local_dir.rglob('*'):
                    if file_path.is_file() and self._should_sync_file(file_path, rules):
                        relative_path = file_path.relative_to(local_dir)
                        if self.upload_file(file_path, str(relative_path)):
                            files_synced += 1
            else:
                # Download files from Dropbox
                remote_files = self.list_remote_files()
                for file_info in remote_files:
                    remote_name = file_info['name']
                    local_path = local_dir / remote_name
                    if self.download_file(remote_name, local_path):
                        files_synced += 1
            
            # Update sync history
            history_file = local_dir / SYNC_HISTORY_FILE
            if history_file.exists():
                with open(history_file, 'r') as f:
                    history = SyncHistory.from_dict(json.load(f))
            else:
                history = SyncHistory()
            
            operation = 'upload' if upload else 'download'
            history.add_entry(operation, files_synced, self.current_user)
            
            with open(history_file, 'w') as f:
                json.dump(history.to_dict(), f, indent=2)
            
            success_msg = f"Sync completed: {files_synced} files {operation}ed"
            self.syncCompleted.emit(True, success_msg, files_synced)
            return True
            
        except Exception as e:
            error_msg = f"Sync failed: {str(e)}"
            self.syncError.emit(error_msg)
            logger.error(error_msg)
            return False
