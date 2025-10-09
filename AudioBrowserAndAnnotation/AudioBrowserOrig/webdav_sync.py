#!/usr/bin/env python3
"""
WebDAV sync module for AudioBrowser-QML.

This module provides WebDAV synchronization functionality (compatible with 
Nextcloud, ownCloud, and other WebDAV servers).
"""

from __future__ import annotations
import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

from PyQt6.QtCore import pyqtSlot

from .cloud_sync_base import (
    CloudSyncBase, SyncHistory, SyncRules, SyncVersion,
    SYNC_EXCLUDED, VERSION_FILE, SYNC_HISTORY_FILE, SYNC_RULES_FILE
)

# WebDAV client imports (will be auto-installed if needed)
try:
    from webdav3.client import Client
    WEBDAV_AVAILABLE = True
except ImportError:
    WEBDAV_AVAILABLE = False

# Logging setup
logger = logging.getLogger(__name__)


class WebDAVSync(CloudSyncBase):
    """WebDAV synchronization manager with QML integration."""
    
    def __init__(self, config_path: Path, parent=None):
        """
        Initialize WebDAV sync.
        
        Args:
            config_path: Path to store/load WebDAV configuration
            parent: QObject parent (optional)
        """
        super().__init__(parent)
        self.config_path = config_path
        self.client: Optional[Client] = None
        self.remote_folder_path: Optional[str] = None
        self.current_user: str = os.getenv('USER') or os.getenv('USERNAME') or 'Unknown'
        
        # Try to load existing config
        self._load_config()
    
    def _load_config(self) -> bool:
        """Load WebDAV configuration from file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    
                options = {
                    'webdav_hostname': config.get('hostname'),
                    'webdav_login': config.get('username'),
                    'webdav_password': config.get('password')
                }
                
                if all(options.values()):
                    self.client = Client(options)
                    return True
        except Exception as e:
            logger.error(f"Failed to load WebDAV config: {e}")
        return False
    
    def _save_config(self, hostname: str, username: str, password: str) -> bool:
        """Save WebDAV configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump({
                    'hostname': hostname,
                    'username': username,
                    'password': password
                }, f)
            return True
        except Exception as e:
            logger.error(f"Failed to save WebDAV config: {e}")
            return False
    
    @pyqtSlot(result=bool)
    def isAvailable(self) -> bool:
        """Check if WebDAV client library is available."""
        return WEBDAV_AVAILABLE
    
    @pyqtSlot(result=bool)
    def isAuthenticated(self) -> bool:
        """Check if authenticated with WebDAV server."""
        if not self.client:
            return False
        try:
            return self.client.check()
        except Exception:
            return False
    
    @pyqtSlot(str, str, str, result=bool)
    def setCredentials(self, hostname: str, username: str, password: str) -> bool:
        """
        Set WebDAV credentials (called from QML).
        
        Args:
            hostname: WebDAV server URL (e.g., https://nextcloud.example.com/remote.php/dav/files/username/)
            username: WebDAV username
            password: WebDAV password
            
        Returns:
            bool: True if credentials are valid, False otherwise
        """
        try:
            options = {
                'webdav_hostname': hostname,
                'webdav_login': username,
                'webdav_password': password
            }
            
            self.client = Client(options)
            
            # Verify credentials by checking connection
            if self.client.check():
                # Save config
                self._save_config(hostname, username, password)
                self.authenticationStatusChanged.emit(True, f"Connected to {hostname}")
                return True
            else:
                self.authenticationStatusChanged.emit(False, "Connection failed")
                return False
                
        except Exception as e:
            error_msg = f"Authentication failed: {str(e)}"
            self.authenticationStatusChanged.emit(False, error_msg)
            logger.error(error_msg)
            return False
    
    @pyqtSlot(result=bool)
    def authenticate(self) -> bool:
        """
        Authenticate with WebDAV server.
        Note: For WebDAV, user must set credentials manually.
        This method just checks if already authenticated.
        """
        if self.isAuthenticated():
            self.authenticationStatusChanged.emit(True, "Already connected to WebDAV server")
            return True
        
        self.authenticationStatusChanged.emit(
            False,
            "Please set WebDAV credentials using 'Set Credentials' button"
        )
        return False
    
    @pyqtSlot(str, result=str)
    def select_remote_folder(self, folder_name: Optional[str] = None) -> Optional[str]:
        """
        Select or create a remote folder on WebDAV server.
        
        Args:
            folder_name: Name of folder (will be created in /AudioBrowser/)
            
        Returns:
            str: Folder path if successful, None otherwise
        """
        if not self.isAuthenticated():
            self.syncError.emit("Not connected to WebDAV server")
            return None
        
        try:
            # WebDAV folder structure: /AudioBrowser/[folder_name]
            folder_path = f"/AudioBrowser/{folder_name}" if folder_name else "/AudioBrowser"
            
            # Try to create folder (will fail if exists, which is fine)
            try:
                self.client.mkdir(folder_path)
            except Exception:
                # Folder might already exist
                pass
            
            # Verify folder exists
            if not self.client.check(folder_path):
                raise Exception("Failed to create or access folder")
            
            self.remote_folder_path = folder_path
            self.folderSelected.emit(folder_name or "AudioBrowser", folder_path)
            return folder_path
            
        except Exception as e:
            error_msg = f"Failed to select/create folder: {str(e)}"
            self.syncError.emit(error_msg)
            logger.error(error_msg)
            return None
    
    def upload_file(self, local_path: Path, remote_name: Optional[str] = None) -> bool:
        """Upload a file to WebDAV server."""
        if not self.isAuthenticated() or not self.remote_folder_path:
            return False
        
        try:
            if not local_path.exists():
                return False
            
            remote_name = remote_name or local_path.name
            remote_path = f"{self.remote_folder_path}/{remote_name}"
            
            # Upload file
            self.client.upload_sync(remote_path, str(local_path))
            
            self.syncProgress.emit(f"Uploaded: {remote_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload {local_path}: {e}")
            return False
    
    def download_file(self, remote_name: str, local_path: Path) -> bool:
        """Download a file from WebDAV server."""
        if not self.isAuthenticated() or not self.remote_folder_path:
            return False
        
        try:
            remote_path = f"{self.remote_folder_path}/{remote_name}"
            
            # Download file
            local_path.parent.mkdir(parents=True, exist_ok=True)
            self.client.download_sync(remote_path, str(local_path))
            
            self.syncProgress.emit(f"Downloaded: {remote_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download {remote_name}: {e}")
            return False
    
    def list_remote_files(self) -> List[Dict[str, Any]]:
        """List all files in the remote WebDAV folder."""
        if not self.isAuthenticated() or not self.remote_folder_path:
            return []
        
        try:
            files = []
            items = self.client.list(self.remote_folder_path)
            
            for item in items:
                if not item.endswith('/'):  # Is a file (not directory)
                    item_path = f"{self.remote_folder_path}/{item}"
                    info = self.client.info(item_path)
                    files.append({
                        'name': item,
                        'size': int(info.get('size', 0)),
                        'modified_time': info.get('modified'),
                        'id': item_path
                    })
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to list remote files: {e}")
            return []
    
    @pyqtSlot(str, bool, result=bool)
    def performSync(self, directory: str, upload: bool) -> bool:
        """Perform sync operation (upload or download)."""
        if not self.isAuthenticated() or not self.remote_folder_path:
            self.syncError.emit("Not connected or no folder selected")
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
                # Upload local files to WebDAV
                for file_path in local_dir.rglob('*'):
                    if file_path.is_file() and self._should_sync_file(file_path, rules):
                        relative_path = file_path.relative_to(local_dir)
                        if self.upload_file(file_path, str(relative_path)):
                            files_synced += 1
            else:
                # Download files from WebDAV
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
