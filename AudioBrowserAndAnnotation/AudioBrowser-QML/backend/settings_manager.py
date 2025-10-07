"""
Settings Manager for AudioBrowser QML

Centralized configuration management using QSettings.
Extracted and adapted from audio_browser.py ConfigManager class.
"""

from PyQt6.QtCore import QObject, QSettings, pyqtSignal, pyqtSlot
from typing import List, Optional


# Settings keys
SETTINGS_KEY_WINDOW_GEOMETRY = "window/geometry"
SETTINGS_KEY_SPLITTER_STATE = "splitter/state"
SETTINGS_KEY_NOW_PLAYING_COLLAPSED = "now_playing/collapsed"
SETTINGS_KEY_RECENT_FOLDERS = "folders/recent"
SETTINGS_KEY_ROOT = "folders/root"
SETTINGS_KEY_UNDO_CAP = "preferences/undo_limit"
SETTINGS_KEY_THEME = "preferences/theme"
SETTINGS_KEY_VOLUME = "audio/volume"
SETTINGS_KEY_VOLUME_BOOST = "audio/volume_boost"
SETTINGS_KEY_PLAYBACK_SPEED = "audio/playback_speed"
SETTINGS_KEY_CUR_SET = "annotations/current_set"
SETTINGS_KEY_SHOW_ALL = "annotations/show_all_sets"
SETTINGS_KEY_SHOW_ALL_FOLDER_NOTES = "annotations/show_all_folder_notes"
SETTINGS_KEY_AUTO_GEN_WAVEFORMS = "auto_generation/waveforms"
SETTINGS_KEY_AUTO_GEN_FINGERPRINTS = "auto_generation/fingerprints"


class SettingsManager(QObject):
    """
    Centralized configuration management using QSettings.
    
    This class manages application settings and preferences, persisting them
    across application sessions. It provides type-safe access to settings
    and emits signals when settings change.
    
    Phase 1: Core Infrastructure
    """
    
    # Signals for settings changes
    themeChanged = pyqtSignal(str)
    volumeChanged = pyqtSignal(int)
    rootDirChanged = pyqtSignal(str)
    
    def __init__(self, org_name: str = "BandTools", app_name: str = "AudioBrowser-QML"):
        super().__init__()
        self.settings = QSettings(org_name, app_name)
        
        # Check for and migrate legacy settings from old application
        self._migrate_legacy_settings()
    
    # Geometry and layout
    @pyqtSlot(result=bytes)
    def getGeometry(self) -> Optional[bytes]:
        """Get saved window geometry."""
        return self.settings.value(SETTINGS_KEY_WINDOW_GEOMETRY)
    
    @pyqtSlot(bytes)
    def setGeometry(self, geometry: bytes):
        """Save window geometry."""
        self.settings.setValue(SETTINGS_KEY_WINDOW_GEOMETRY, geometry)
    
    @pyqtSlot(result=bytes)
    def getSplitterState(self) -> Optional[bytes]:
        """Get saved splitter state."""
        return self.settings.value(SETTINGS_KEY_SPLITTER_STATE)
    
    @pyqtSlot(bytes)
    def setSplitterState(self, state: bytes):
        """Save splitter state."""
        self.settings.setValue(SETTINGS_KEY_SPLITTER_STATE, state)
    
    @pyqtSlot(result=bool)
    def getNowPlayingCollapsed(self) -> bool:
        """Get whether Now Playing panel is collapsed."""
        collapsed_raw = self.settings.value(SETTINGS_KEY_NOW_PLAYING_COLLAPSED, 0)
        return bool(int(collapsed_raw))
    
    @pyqtSlot(bool)
    def setNowPlayingCollapsed(self, collapsed: bool):
        """Set whether Now Playing panel is collapsed."""
        self.settings.setValue(SETTINGS_KEY_NOW_PLAYING_COLLAPSED, collapsed)
    
    # Recent folders
    @pyqtSlot(result=list)
    def getRecentFolders(self) -> List[str]:
        """Get list of recently accessed folders."""
        folders = self.settings.value(SETTINGS_KEY_RECENT_FOLDERS, [])
        return folders if isinstance(folders, list) else []
    
    @pyqtSlot(str, int)
    def addRecentFolder(self, folder_path: str, max_recent: int = 10):
        """Add a folder to recent folders list."""
        recent = self.getRecentFolders()
        if folder_path in recent:
            recent.remove(folder_path)
        recent.insert(0, folder_path)
        recent = recent[:max_recent]
        self.settings.setValue(SETTINGS_KEY_RECENT_FOLDERS, recent)
    
    @pyqtSlot()
    def clearRecentFolders(self):
        """Clear recent folders list."""
        self.settings.setValue(SETTINGS_KEY_RECENT_FOLDERS, [])
    
    # Root directory
    @pyqtSlot(result=str)
    def getRootDir(self) -> str:
        """Get root directory path."""
        return self.settings.value(SETTINGS_KEY_ROOT, "", type=str)
    
    @pyqtSlot(str)
    def setRootDir(self, path: str):
        """Set root directory path."""
        self.settings.setValue(SETTINGS_KEY_ROOT, path)
        self.rootDirChanged.emit(path)
    
    # Preferences
    @pyqtSlot(result=int)
    def getUndoLimit(self) -> int:
        """Get undo limit."""
        limit_raw = self.settings.value(SETTINGS_KEY_UNDO_CAP, 100)
        return int(limit_raw) if limit_raw is not None else 100
    
    @pyqtSlot(int)
    def setUndoLimit(self, limit: int):
        """Set undo limit."""
        self.settings.setValue(SETTINGS_KEY_UNDO_CAP, int(limit))
    
    @pyqtSlot(result=str)
    def getTheme(self) -> str:
        """Get current theme ('light' or 'dark')."""
        return self.settings.value(SETTINGS_KEY_THEME, "dark")
    
    @pyqtSlot(str)
    def setTheme(self, theme: str):
        """Set current theme ('light' or 'dark')."""
        self.settings.setValue(SETTINGS_KEY_THEME, theme)
        self.themeChanged.emit(theme)
    
    @pyqtSlot(result=int)
    def getVolume(self) -> int:
        """Get playback volume (0-100)."""
        vol_raw = self.settings.value(SETTINGS_KEY_VOLUME, 90)
        return int(vol_raw) if vol_raw is not None else 90
    
    @pyqtSlot(int)
    def setVolume(self, volume: int):
        """Set playback volume (0-100)."""
        self.settings.setValue(SETTINGS_KEY_VOLUME, int(volume))
        self.volumeChanged.emit(volume)
    
    @pyqtSlot(result=int)
    def getVolumeBoost(self) -> int:
        """Get volume boost percentage (100 = no boost)."""
        boost_raw = self.settings.value(SETTINGS_KEY_VOLUME_BOOST, 100)
        return int(boost_raw) if boost_raw is not None else 100
    
    @pyqtSlot(int)
    def setVolumeBoost(self, boost: int):
        """Set volume boost percentage (100 = no boost)."""
        self.settings.setValue(SETTINGS_KEY_VOLUME_BOOST, int(boost))
    
    @pyqtSlot(result=float)
    def getPlaybackSpeed(self) -> float:
        """Get playback speed (1.0 = normal)."""
        speed_raw = self.settings.value(SETTINGS_KEY_PLAYBACK_SPEED, 1.0)
        return float(speed_raw) if speed_raw is not None else 1.0
    
    @pyqtSlot(float)
    def setPlaybackSpeed(self, speed: float):
        """Set playback speed (1.0 = normal)."""
        self.settings.setValue(SETTINGS_KEY_PLAYBACK_SPEED, speed)
    
    # Current annotation set
    @pyqtSlot(result=str)
    def getCurrentSet(self) -> str:
        """Get current annotation set ID."""
        return self.settings.value(SETTINGS_KEY_CUR_SET, "")
    
    @pyqtSlot(str)
    def setCurrentSet(self, set_id: str):
        """Set current annotation set ID."""
        self.settings.setValue(SETTINGS_KEY_CUR_SET, set_id)
    
    # Show all sets
    @pyqtSlot(result=bool)
    def getShowAllSets(self) -> bool:
        """Get whether to show all annotation sets."""
        show_all_raw = self.settings.value(SETTINGS_KEY_SHOW_ALL, 0)
        return bool(int(show_all_raw))
    
    @pyqtSlot(bool)
    def setShowAllSets(self, show_all: bool):
        """Set whether to show all annotation sets."""
        self.settings.setValue(SETTINGS_KEY_SHOW_ALL, int(show_all))
    
    @pyqtSlot(result=bool)
    def getShowAllFolderNotes(self) -> bool:
        """Get whether to show all folder notes."""
        show_all_raw = self.settings.value(SETTINGS_KEY_SHOW_ALL_FOLDER_NOTES, 0)
        return bool(int(show_all_raw))
    
    @pyqtSlot(bool)
    def setShowAllFolderNotes(self, show_all: bool):
        """Set whether to show all folder notes."""
        self.settings.setValue(SETTINGS_KEY_SHOW_ALL_FOLDER_NOTES, int(show_all))
    
    # Auto-generation settings
    @pyqtSlot(result=bool)
    def getAutoWaveforms(self) -> bool:
        """Get whether waveforms are auto-generated."""
        return bool(int(self.settings.value(SETTINGS_KEY_AUTO_GEN_WAVEFORMS, 0)))
    
    @pyqtSlot(bool)
    def setAutoWaveforms(self, enabled: bool):
        """Set whether waveforms are auto-generated."""
        self.settings.setValue(SETTINGS_KEY_AUTO_GEN_WAVEFORMS, int(enabled))
    
    @pyqtSlot(result=bool)
    def getAutoFingerprints(self) -> bool:
        """Get whether fingerprints are auto-generated."""
        return bool(int(self.settings.value(SETTINGS_KEY_AUTO_GEN_FINGERPRINTS, 0)))
    
    @pyqtSlot(bool)
    def setAutoFingerprints(self, enabled: bool):
        """Set whether fingerprints are auto-generated."""
        self.settings.setValue(SETTINGS_KEY_AUTO_GEN_FINGERPRINTS, int(enabled))
    
    # Private helper methods
    def _migrate_legacy_settings(self):
        """
        Migrate settings from legacy "Audio Folder Player" application.
        
        Checks for settings from the old PyQt5-based application and imports
        the root directory if available and not already set.
        """
        # Check if we already have settings (don't overwrite)
        current_root = self.settings.value(SETTINGS_KEY_ROOT, "", type=str)
        if current_root:
            # Already have settings, no need to migrate
            return
        
        # Try to load legacy settings
        legacy_settings = QSettings("YourCompany", "Audio Folder Player")
        legacy_root = legacy_settings.value("root_dir", "", type=str)
        
        if legacy_root:
            # Migrate the root directory setting
            print(f"Migrating legacy root directory: {legacy_root}")
            self.settings.setValue(SETTINGS_KEY_ROOT, legacy_root)
            
            # Optionally migrate other settings that exist
            legacy_theme = legacy_settings.value("theme", "")
            if legacy_theme:
                self.settings.setValue(SETTINGS_KEY_THEME, legacy_theme)
            
            legacy_volume = legacy_settings.value("volume")
            if legacy_volume is not None:
                self.settings.setValue(SETTINGS_KEY_VOLUME, legacy_volume)
