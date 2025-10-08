#!/usr/bin/env python3
"""
Unified sync manager for AudioBrowser-QML.

This module provides a unified interface for managing multiple cloud sync providers.
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Optional
import logging

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from .cloud_sync_base import CloudSyncBase
from .gdrive_sync import GDriveSync
from .dropbox_sync import DropboxSync
from .webdav_sync import WebDAVSync

# Logging setup
logger = logging.getLogger(__name__)


class SyncManager(QObject):
    """
    Unified sync manager that handles multiple cloud providers.
    
    Provides a single interface for QML to interact with different sync backends.
    """
    
    # Forward signals from active provider
    authenticationStatusChanged = pyqtSignal(bool, str)
    syncProgress = pyqtSignal(str)
    syncCompleted = pyqtSignal(bool, str, int)
    syncError = pyqtSignal(str)
    folderSelected = pyqtSignal(str, str)
    providerChanged = pyqtSignal(str)  # New signal for provider changes
    
    def __init__(self, config_dir: Path, parent=None):
        """
        Initialize sync manager.
        
        Args:
            config_dir: Directory for storing sync configurations
            parent: QObject parent (optional)
        """
        super().__init__(parent)
        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize all providers
        self.providers = {
            'gdrive': GDriveSync(
                credentials_path=config_dir / 'credentials.json',
                token_path=config_dir / 'token.json',
                parent=self
            ),
            'dropbox': DropboxSync(
                token_path=config_dir / 'dropbox_token.json',
                parent=self
            ),
            'webdav': WebDAVSync(
                config_path=config_dir / 'webdav_config.json',
                parent=self
            )
        }
        
        # Active provider (default to Google Drive)
        self.active_provider_name = 'gdrive'
        self.active_provider = self.providers['gdrive']
        
        # Connect signals from active provider
        self._connect_provider_signals()
    
    def _connect_provider_signals(self):
        """Connect signals from the active provider."""
        if self.active_provider:
            self.active_provider.authenticationStatusChanged.connect(self.authenticationStatusChanged)
            self.active_provider.syncProgress.connect(self.syncProgress)
            self.active_provider.syncCompleted.connect(self.syncCompleted)
            self.active_provider.syncError.connect(self.syncError)
            self.active_provider.folderSelected.connect(self.folderSelected)
    
    def _disconnect_provider_signals(self):
        """Disconnect signals from the active provider."""
        if self.active_provider:
            try:
                self.active_provider.authenticationStatusChanged.disconnect(self.authenticationStatusChanged)
                self.active_provider.syncProgress.disconnect(self.syncProgress)
                self.active_provider.syncCompleted.disconnect(self.syncCompleted)
                self.active_provider.syncError.disconnect(self.syncError)
                self.active_provider.folderSelected.disconnect(self.folderSelected)
            except Exception as e:
                logger.warning(f"Failed to disconnect signals: {e}")
    
    @pyqtSlot(str, result=bool)
    def setProvider(self, provider_name: str) -> bool:
        """
        Set the active cloud provider.
        
        Args:
            provider_name: Name of provider ('gdrive', 'dropbox', 'webdav')
            
        Returns:
            bool: True if provider was set successfully
        """
        provider_name = provider_name.lower()
        
        if provider_name not in self.providers:
            logger.error(f"Unknown provider: {provider_name}")
            return False
        
        if provider_name == self.active_provider_name:
            return True  # Already active
        
        # Disconnect old provider
        self._disconnect_provider_signals()
        
        # Set new provider
        self.active_provider_name = provider_name
        self.active_provider = self.providers[provider_name]
        
        # Connect new provider
        self._connect_provider_signals()
        
        self.providerChanged.emit(provider_name)
        logger.info(f"Switched to provider: {provider_name}")
        return True
    
    @pyqtSlot(result=str)
    def getProvider(self) -> str:
        """Get the name of the active provider."""
        return self.active_provider_name
    
    @pyqtSlot(result=str)
    def getProviderDisplayName(self) -> str:
        """Get display name of the active provider."""
        names = {
            'gdrive': 'Google Drive',
            'dropbox': 'Dropbox',
            'webdav': 'WebDAV/Nextcloud'
        }
        return names.get(self.active_provider_name, 'Unknown')
    
    @pyqtSlot(str, result=bool)
    def isProviderAvailable(self, provider_name: str) -> bool:
        """Check if a provider's libraries are available."""
        provider_name = provider_name.lower()
        if provider_name in self.providers:
            return self.providers[provider_name].isAvailable()
        return False
    
    # Delegate methods to active provider
    
    @pyqtSlot(result=bool)
    def isAvailable(self) -> bool:
        """Check if active provider is available."""
        return self.active_provider.isAvailable()
    
    @pyqtSlot(result=bool)
    def isAuthenticated(self) -> bool:
        """Check if authenticated with active provider."""
        return self.active_provider.isAuthenticated()
    
    @pyqtSlot(result=bool)
    def authenticate(self) -> bool:
        """Authenticate with active provider."""
        return self.active_provider.authenticate()
    
    @pyqtSlot(str, result=str)
    def select_remote_folder(self, folder_name: Optional[str] = None) -> Optional[str]:
        """Select/create remote folder on active provider."""
        return self.active_provider.select_remote_folder(folder_name)
    
    @pyqtSlot(str, bool, result=bool)
    def performSync(self, directory: str, upload: bool) -> bool:
        """Perform sync with active provider."""
        return self.active_provider.performSync(directory, upload)
    
    # Provider-specific methods (forwarded based on active provider)
    
    @pyqtSlot(str, result=bool)
    def dropbox_setAccessToken(self, token: str) -> bool:
        """Set Dropbox access token (only works when Dropbox is active)."""
        if self.active_provider_name == 'dropbox':
            return self.providers['dropbox'].setAccessToken(token)
        return False
    
    @pyqtSlot(str, str, str, result=bool)
    def webdav_setCredentials(self, hostname: str, username: str, password: str) -> bool:
        """Set WebDAV credentials (only works when WebDAV is active)."""
        if self.active_provider_name == 'webdav':
            return self.providers['webdav'].setCredentials(hostname, username, password)
        return False
    
    @pyqtSlot(result=list)
    def getAvailableProviders(self) -> list:
        """Get list of available providers with their status."""
        result = []
        for name, provider in self.providers.items():
            display_names = {
                'gdrive': 'Google Drive',
                'dropbox': 'Dropbox',
                'webdav': 'WebDAV/Nextcloud'
            }
            result.append({
                'name': name,
                'displayName': display_names.get(name, name),
                'available': provider.isAvailable(),
                'authenticated': provider.isAuthenticated()
            })
        return result
