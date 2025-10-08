#!/usr/bin/env python3
"""
Base class for cloud synchronization providers.

Defines the common interface and data structures for all cloud sync implementations.
"""

from __future__ import annotations
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# PyQt6 imports for QML integration
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

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
        if self.version > since_version:
            return self.operations
        return []


class CloudSyncBase(QObject, ABC):
    """
    Abstract base class for cloud synchronization providers.
    
    All cloud sync implementations should inherit from this class and implement
    the required abstract methods.
    """
    
    # Qt Signals for QML integration
    authenticationStatusChanged = pyqtSignal(bool, str)  # success, message
    syncProgress = pyqtSignal(str)  # progress message
    syncCompleted = pyqtSignal(bool, str, int)  # success, message, files_count
    syncError = pyqtSignal(str)  # error message
    folderSelected = pyqtSignal(str, str)  # folder_name, folder_id
    
    def __init__(self, parent=None):
        """Initialize base cloud sync."""
        super().__init__(parent)
        self.remote_folder_id: Optional[str] = None
    
    @abstractmethod
    @pyqtSlot(result=bool)
    def isAvailable(self) -> bool:
        """Check if the cloud provider API libraries are available."""
        pass
    
    @abstractmethod
    @pyqtSlot(result=bool)
    def isAuthenticated(self) -> bool:
        """Check if user is authenticated with the cloud provider."""
        pass
    
    @abstractmethod
    @pyqtSlot(result=bool)
    def authenticate(self) -> bool:
        """
        Authenticate with the cloud provider.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        pass
    
    @abstractmethod
    @pyqtSlot(str, result=str)
    def select_remote_folder(self, folder_name: Optional[str] = None) -> Optional[str]:
        """
        Select or create a remote folder for synchronization.
        
        Args:
            folder_name: Name of the folder to select/create
            
        Returns:
            str: Folder ID if successful, None otherwise
        """
        pass
    
    @abstractmethod
    def upload_file(self, local_path: Path, remote_name: Optional[str] = None) -> bool:
        """
        Upload a single file to the remote folder.
        
        Args:
            local_path: Path to local file
            remote_name: Optional custom name for remote file
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def download_file(self, remote_name: str, local_path: Path) -> bool:
        """
        Download a single file from the remote folder.
        
        Args:
            remote_name: Name of file on remote
            local_path: Path to save file locally
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def list_remote_files(self) -> List[Dict[str, Any]]:
        """
        List all files in the remote folder.
        
        Returns:
            List of dicts with file information (name, size, modified_time, etc.)
        """
        pass
    
    @abstractmethod
    @pyqtSlot(str, bool, result=bool)
    def performSync(self, directory: str, upload: bool) -> bool:
        """
        Perform synchronization operation.
        
        Args:
            directory: Local directory path
            upload: True for upload, False for download
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @pyqtSlot(result=str)
    def getProviderName(self) -> str:
        """Get the name of the cloud provider (e.g., 'Google Drive', 'Dropbox')."""
        return self.__class__.__name__.replace('Sync', '').replace('sync', '')
    
    def _should_sync_file(self, file_path: Path, rules: SyncRules) -> bool:
        """Check if file should be synced based on rules and exclusions."""
        # Check if file/dir is excluded
        for part in file_path.parts:
            if part in SYNC_EXCLUDED:
                return False
        
        # Apply sync rules
        try:
            file_size = file_path.stat().st_size if file_path.exists() else 0
            return rules.should_sync_file(file_path, file_size)
        except Exception:
            return False
