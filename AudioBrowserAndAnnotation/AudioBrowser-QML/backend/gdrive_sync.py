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
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

# Google Drive API imports (will be auto-installed if needed)
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    GDRIVE_AVAILABLE = True
except ImportError:
    GDRIVE_AVAILABLE = False

# Logging setup
logger = logging.getLogger(__name__)

# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Version file name
VERSION_FILE = '.sync_version.json'

# Sync history file name
SYNC_HISTORY_FILE = '.sync_history.json'

# Sync rules configuration file name
SYNC_RULES_FILE = '.sync_rules.json'

# Files and directories that should never be synced
SYNC_EXCLUDED = {'.backup', '.backups', '.waveforms', '.git', '__pycache__'}

# Annotation file patterns that user can modify
ANNOTATION_PATTERNS = ['.audio_notes_', '.provided_names.json', '.duration_cache.json', 
                       '.audio_fingerprints.json', '.user_colors.json', '.song_renames.json']


class SyncHistory:
    """Manages sync history tracking."""
    
    def __init__(self, entries: Optional[List[Dict]] = None):
        self.entries = entries or []
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SyncHistory':
        """Load history from dictionary."""
        return cls(entries=data.get('entries', []))
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {'entries': self.entries}
    
    def add_entry(self, operation_type: str, files_count: int, user: str, 
                  timestamp: Optional[str] = None, details: Optional[str] = None):
        """Add a sync history entry."""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        self.entries.append({
            'operation': operation_type,  # 'upload', 'download', 'conflict_resolved'
            'files_count': files_count,
            'user': user,
            'timestamp': timestamp,
            'details': details
        })
        
        # Keep only last 100 entries to prevent file bloat
        if len(self.entries) > 100:
            self.entries = self.entries[-100:]
    
    def get_recent_entries(self, count: int = 10) -> List[Dict]:
        """Get most recent sync entries."""
        return self.entries[-count:] if self.entries else []


class SyncRules:
    """Manages selective sync rules."""
    
    def __init__(self, max_file_size_mb: float = 0, 
                 sync_audio_files: bool = True,
                 sync_annotations_only: bool = False,
                 auto_sync_enabled: bool = False,
                 auto_download_best_takes: bool = False):
        self.max_file_size_mb = max_file_size_mb  # 0 = no limit
        self.sync_audio_files = sync_audio_files
        self.sync_annotations_only = sync_annotations_only
        self.auto_sync_enabled = auto_sync_enabled
        self.auto_download_best_takes = auto_download_best_takes
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SyncRules':
        """Load rules from dictionary."""
        return cls(
            max_file_size_mb=data.get('max_file_size_mb', 0),
            sync_audio_files=data.get('sync_audio_files', True),
            sync_annotations_only=data.get('sync_annotations_only', False),
            auto_sync_enabled=data.get('auto_sync_enabled', False),
            auto_download_best_takes=data.get('auto_download_best_takes', False)
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'max_file_size_mb': self.max_file_size_mb,
            'sync_audio_files': self.sync_audio_files,
            'sync_annotations_only': self.sync_annotations_only,
            'auto_sync_enabled': self.auto_sync_enabled,
            'auto_download_best_takes': self.auto_download_best_takes
        }
    
    def should_sync_file(self, file_path: Path, file_size_bytes: int = 0) -> bool:
        """Check if a file should be synced based on rules."""
        # Check file size limit
        if self.max_file_size_mb > 0:
            size_mb = file_size_bytes / (1024 * 1024)
            if size_mb > self.max_file_size_mb:
                return False
        
        # Check if annotations only
        if self.sync_annotations_only:
            # Only sync metadata/annotation files
            is_annotation = any(pattern in file_path.name for pattern in ANNOTATION_PATTERNS)
            is_annotation = is_annotation or file_path.name in [VERSION_FILE, SYNC_HISTORY_FILE, SYNC_RULES_FILE]
            return is_annotation
        
        # Check if audio files should be synced
        if not self.sync_audio_files:
            audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
            if file_path.suffix.lower() in audio_extensions:
                return False
        
        return True


class SyncVersion:
    """Manages sync version tracking and operations."""
    
    def __init__(self, version: int = 0, operations: Optional[List[Dict]] = None):
        self.version = version
        self.operations = operations or []
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SyncVersion':
        """Load version info from dictionary."""
        return cls(
            version=data.get('version', 0),
            operations=data.get('operations', [])
        )
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'version': self.version,
            'operations': self.operations
        }
    
    def add_operation(self, op_type: str, file_path: str, timestamp: Optional[str] = None):
        """Add an operation to the current version."""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        self.operations.append({
            'type': op_type,  # 'add', 'update', 'delete', 'rename'
            'path': file_path,
            'timestamp': timestamp
        })
    
    def get_operations_since(self, since_version: int) -> List[Dict]:
        """Get all operations since a specific version."""
        # For now, return all operations if version is newer
        # In a more complex implementation, we'd track operations per version
        if self.version > since_version:
            return self.operations
        return []


class GDriveSync(QObject):
    """Google Drive synchronization manager with QML integration."""
    
    # Qt Signals for QML integration
    authenticationStatusChanged = pyqtSignal(bool, str)  # success, message
    syncProgress = pyqtSignal(str)  # progress message
    syncCompleted = pyqtSignal(bool, str, int)  # success, message, files_count
    syncError = pyqtSignal(str)  # error message
    folderSelected = pyqtSignal(str, str)  # folder_id, folder_name
    
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
        self.remote_folder_id: Optional[str] = None
        self.current_user: str = os.getenv('USER') or os.getenv('USERNAME') or 'Unknown'
    
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
    
    def upload_file(self, local_path: Path, remote_name: Optional[str] = None) -> bool:
        """
        Upload a file to remote folder.
        
        Args:
            local_path: Path to local file
            remote_name: Optional different name for remote file
            
        Returns:
            True if successful
        """
        if not self.service or not self.remote_folder_id:
            return False
        
        if not local_path.exists():
            logger.error(f"Local file not found: {local_path}")
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
                self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                logger.info(f"Uploaded new file: {remote_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error uploading file {local_path}: {e}")
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
