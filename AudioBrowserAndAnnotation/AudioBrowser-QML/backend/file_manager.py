#!/usr/bin/env python3
"""
File Manager Backend Module

Handles file system operations for the AudioBrowser QML application.
Provides file discovery, filtering, and metadata access.
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Set
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot


# Audio file extensions
AUDIO_EXTENSIONS = {".wav", ".wave", ".mp3"}


class FileManager(QObject):
    """
    File manager for audio file operations.
    
    Provides file discovery, filtering, and metadata access
    with signals for QML integration.
    """
    
    # Signals for state changes
    filesDiscovered = pyqtSignal(list)  # List of discovered file paths
    currentDirectoryChanged = pyqtSignal(str)  # Current directory path
    errorOccurred = pyqtSignal(str)  # Error message
    scanProgress = pyqtSignal(int, int)  # (current, total) for progress tracking
    
    def __init__(self, parent=None):
        """Initialize the file manager."""
        super().__init__(parent)
        
        self._current_directory: Optional[Path] = None
        self._discovered_files: List[Path] = []
        self._audio_extensions = AUDIO_EXTENSIONS
    
    # ========== QML-accessible methods ==========
    
    @pyqtSlot(str)
    def setCurrentDirectory(self, directory: str) -> None:
        """
        Set the current working directory.
        
        Args:
            directory: Path to the directory
        """
        try:
            path = Path(directory)
            if not path.exists():
                self.errorOccurred.emit(f"Directory not found: {directory}")
                return
            
            if not path.is_dir():
                self.errorOccurred.emit(f"Not a directory: {directory}")
                return
            
            self._current_directory = path
            self.currentDirectoryChanged.emit(str(path))
            
            # Automatically discover files in the new directory
            self.discoverAudioFiles(str(path))
            
        except Exception as e:
            self.errorOccurred.emit(f"Error setting directory: {e}")
    
    @pyqtSlot(str)
    def discoverAudioFiles(self, directory: str = None) -> None:
        """
        Discover audio files in the specified directory.
        
        Args:
            directory: Directory to scan (uses current directory if None)
        """
        try:
            if directory is None:
                if self._current_directory is None:
                    self.errorOccurred.emit("No directory set")
                    return
                scan_path = self._current_directory
            else:
                scan_path = Path(directory)
            
            if not scan_path.exists() or not scan_path.is_dir():
                self.errorOccurred.emit(f"Invalid directory: {scan_path}")
                return
            
            # Discover audio files
            files = []
            for ext in self._audio_extensions:
                files.extend(scan_path.glob(f"*{ext}"))
            
            # Sort files by name
            files.sort(key=lambda p: p.name.lower())
            
            self._discovered_files = files
            
            # Emit list of file paths as strings
            file_paths = [str(f) for f in files]
            self.filesDiscovered.emit(file_paths)
            
        except Exception as e:
            self.errorOccurred.emit(f"Error discovering files: {e}")
    
    @pyqtSlot(str, result=bool)
    def isAudioFile(self, file_path: str) -> bool:
        """
        Check if a file is an audio file based on extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file has an audio extension
        """
        try:
            path = Path(file_path)
            return path.suffix.lower() in self._audio_extensions
        except Exception:
            return False
    
    @pyqtSlot(str, result=bool)
    def fileExists(self, file_path: str) -> bool:
        """
        Check if a file exists.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file exists
        """
        try:
            return Path(file_path).exists()
        except Exception:
            return False
    
    @pyqtSlot(str, result=int)
    def getFileSize(self, file_path: str) -> int:
        """
        Get the size of a file in bytes.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File size in bytes, or 0 on error
        """
        try:
            path = Path(file_path)
            if path.exists():
                return path.stat().st_size
            return 0
        except Exception:
            return 0
    
    @pyqtSlot(str, result=str)
    def getFileName(self, file_path: str) -> str:
        """
        Get the name of a file (without directory).
        
        Args:
            file_path: Path to the file
            
        Returns:
            File name
        """
        try:
            return Path(file_path).name
        except Exception:
            return ""
    
    @pyqtSlot(str, result=str)
    def getFileBaseName(self, file_path: str) -> str:
        """
        Get the base name of a file (without extension).
        
        Args:
            file_path: Path to the file
            
        Returns:
            File base name
        """
        try:
            return Path(file_path).stem
        except Exception:
            return ""
    
    @pyqtSlot(str, result=str)
    def getFileExtension(self, file_path: str) -> str:
        """
        Get the extension of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File extension (including the dot)
        """
        try:
            return Path(file_path).suffix
        except Exception:
            return ""
    
    @pyqtSlot(str, result=str)
    def getFileDirectory(self, file_path: str) -> str:
        """
        Get the directory containing a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Directory path
        """
        try:
            return str(Path(file_path).parent)
        except Exception:
            return ""
    
    @pyqtSlot(result=list)
    def getDiscoveredFiles(self) -> List[str]:
        """
        Get the list of discovered audio files.
        
        Returns:
            List of file paths as strings
        """
        return [str(f) for f in self._discovered_files]
    
    @pyqtSlot(result=str)
    def getCurrentDirectory(self) -> str:
        """
        Get the current directory.
        
        Returns:
            Current directory path or empty string if not set
        """
        return str(self._current_directory) if self._current_directory else ""
    
    @pyqtSlot(result=int)
    def getFileCount(self) -> int:
        """
        Get the count of discovered audio files.
        
        Returns:
            Number of discovered files
        """
        return len(self._discovered_files)
    
    @pyqtSlot(str, str, result=list)
    def findFilesWithPattern(self, directory: str, pattern: str) -> List[str]:
        """
        Find files matching a glob pattern.
        
        Args:
            directory: Directory to search
            pattern: Glob pattern (e.g., "*.wav")
            
        Returns:
            List of matching file paths
        """
        try:
            path = Path(directory)
            if not path.exists() or not path.is_dir():
                return []
            
            files = list(path.glob(pattern))
            return [str(f) for f in sorted(files, key=lambda p: p.name.lower())]
            
        except Exception as e:
            self.errorOccurred.emit(f"Error finding files: {e}")
            return []
    
    @pyqtSlot(str, result=list)
    def getSubdirectories(self, directory: str = None) -> List[str]:
        """
        Get subdirectories of a directory.
        
        Args:
            directory: Directory to scan (uses current directory if None)
            
        Returns:
            List of subdirectory paths
        """
        try:
            if directory is None:
                if self._current_directory is None:
                    return []
                scan_path = self._current_directory
            else:
                scan_path = Path(directory)
            
            if not scan_path.exists() or not scan_path.is_dir():
                return []
            
            subdirs = [d for d in scan_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
            subdirs.sort(key=lambda d: d.name.lower())
            
            return [str(d) for d in subdirs]
            
        except Exception as e:
            self.errorOccurred.emit(f"Error getting subdirectories: {e}")
            return []
    
    # ========== File filtering methods ==========
    
    @pyqtSlot(str, result=list)
    def filterFilesByName(self, filter_text: str) -> List[str]:
        """
        Filter discovered files by name.
        
        Args:
            filter_text: Text to filter by (case-insensitive)
            
        Returns:
            List of matching file paths
        """
        if not filter_text:
            return [str(f) for f in self._discovered_files]
        
        filter_lower = filter_text.lower()
        filtered = [f for f in self._discovered_files if filter_lower in f.name.lower()]
        
        return [str(f) for f in filtered]
    
    @pyqtSlot(str, result=list)
    def filterFilesByExtension(self, extension: str) -> List[str]:
        """
        Filter discovered files by extension.
        
        Args:
            extension: File extension (e.g., ".wav" or "wav")
            
        Returns:
            List of matching file paths
        """
        if not extension.startswith('.'):
            extension = '.' + extension
        
        extension_lower = extension.lower()
        filtered = [f for f in self._discovered_files if f.suffix.lower() == extension_lower]
        
        return [str(f) for f in filtered]
    
    # ========== Utility methods ==========
    
    @pyqtSlot(str, result=str)
    def formatFileSize(self, file_path: str) -> str:
        """
        Format file size in human-readable form.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Formatted file size (e.g., "1.5 MB")
        """
        try:
            size = self.getFileSize(file_path)
            
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            elif size < 1024 * 1024 * 1024:
                return f"{size / (1024 * 1024):.1f} MB"
            else:
                return f"{size / (1024 * 1024 * 1024):.1f} GB"
                
        except Exception:
            return "0 B"
