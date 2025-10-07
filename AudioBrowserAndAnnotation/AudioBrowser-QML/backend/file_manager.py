#!/usr/bin/env python3
"""
File Manager Backend Module

Handles file system operations for the AudioBrowser QML application.
Provides file discovery, filtering, and metadata access.
"""

import os
import wave
from pathlib import Path
from typing import List, Dict, Optional, Set
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

# Try to import optional dependencies for MP3 support
try:
    from pydub import AudioSegment
    HAVE_PYDUB = True
except ImportError:
    HAVE_PYDUB = False


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
    
    @pyqtSlot(str)
    def openInFileManager(self, file_path: str) -> None:
        """
        Open the file's location in the system file manager.
        
        Args:
            file_path: Path to the file
        """
        try:
            import subprocess
            import platform
            
            path = Path(file_path)
            if not path.exists():
                self.errorOccurred.emit(f"File not found: {file_path}")
                return
            
            # Get the directory containing the file
            directory = path.parent if path.is_file() else path
            
            system = platform.system()
            if system == "Windows":
                # Open Windows Explorer and select the file
                subprocess.Popen(['explorer', '/select,', str(path)])
            elif system == "Darwin":  # macOS
                # Open Finder and select the file
                subprocess.Popen(['open', '-R', str(path)])
            else:  # Linux and others
                # Open the directory in the default file manager
                subprocess.Popen(['xdg-open', str(directory)])
                
        except Exception as e:
            self.errorOccurred.emit(f"Error opening file manager: {e}")
    
    @pyqtSlot(str, result=str)
    def getFileProperties(self, file_path: str) -> str:
        """
        Get file properties as a formatted string.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Formatted string with file properties
        """
        try:
            import datetime
            
            path = Path(file_path)
            if not path.exists():
                return "File not found"
            
            stat = path.stat()
            
            # Format properties
            props = []
            props.append(f"Name: {path.name}")
            props.append(f"Path: {path.parent}")
            props.append(f"Size: {self.formatFileSize(file_path)}")
            props.append(f"Extension: {path.suffix}")
            
            # Modification time
            mtime = datetime.datetime.fromtimestamp(stat.st_mtime)
            props.append(f"Modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Creation time (if available)
            try:
                ctime = datetime.datetime.fromtimestamp(stat.st_ctime)
                props.append(f"Created: {ctime.strftime('%Y-%m-%d %H:%M:%S')}")
            except:
                pass
            
            return "\n".join(props)
            
        except Exception as e:
            return f"Error getting properties: {e}"
    
    @pyqtSlot(str, result=int)
    def getAudioDuration(self, file_path: str) -> int:
        """
        Get the duration of an audio file in milliseconds.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Duration in milliseconds, or 0 on error
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return 0
            
            suffix = path.suffix.lower()
            
            # Handle WAV files
            if suffix in ['.wav', '.wave']:
                try:
                    with wave.open(str(path), 'rb') as wf:
                        frames = wf.getnframes()
                        rate = wf.getframerate()
                        duration_ms = int((frames / rate) * 1000)
                        return duration_ms
                except Exception:
                    return 0
            
            # Handle MP3 files (if pydub is available)
            elif suffix == '.mp3' and HAVE_PYDUB:
                try:
                    audio = AudioSegment.from_mp3(str(path))
                    return len(audio)  # pydub returns duration in milliseconds
                except Exception:
                    return 0
            
            return 0
            
        except Exception:
            return 0
    
    @pyqtSlot(str, result=str)
    def formatDuration(self, duration_ms: int) -> str:
        """
        Format duration in human-readable form (MM:SS or HH:MM:SS).
        
        Args:
            duration_ms: Duration in milliseconds
            
        Returns:
            Formatted duration string
        """
        try:
            total_seconds = duration_ms // 1000
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            
            if hours > 0:
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                return f"{minutes:02d}:{seconds:02d}"
                
        except Exception:
            return "00:00"
    
    # ========== Metadata loading from original AudioBrowser ==========
    
    def _load_provided_names(self, directory: Path) -> Dict[str, str]:
        """
        Load provided names from .provided_names.json file.
        
        Args:
            directory: Directory to check for metadata
            
        Returns:
            Dictionary mapping filenames to provided names
        """
        try:
            import json
            names_file = directory / ".provided_names.json"
            if names_file.exists():
                with open(names_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load provided names: {e}")
        return {}
    
    def _load_duration_cache(self, directory: Path) -> Dict[str, int]:
        """
        Load duration cache from .duration_cache.json file.
        
        Args:
            directory: Directory to check for metadata
            
        Returns:
            Dictionary mapping filenames to durations in milliseconds
        """
        try:
            import json
            cache_file = directory / ".duration_cache.json"
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert seconds to milliseconds if needed
                    if data and isinstance(next(iter(data.values())), (int, float)):
                        return {k: int(v * 1000) if v < 10000 else int(v) for k, v in data.items()}
                    return data
        except Exception as e:
            print(f"Warning: Could not load duration cache: {e}")
        return {}
    
    @pyqtSlot(str, result=str)
    def getProvidedName(self, file_path: str) -> str:
        """
        Get the provided name for a file from metadata.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Provided name if available, otherwise empty string
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return ""
            
            directory = path.parent
            provided_names = self._load_provided_names(directory)
            
            # Try both with and without extension
            filename = path.name
            if filename in provided_names:
                return provided_names[filename]
            
            # Try stem (without extension)
            stem = path.stem
            if stem in provided_names:
                return provided_names[stem]
                
        except Exception as e:
            print(f"Error getting provided name: {e}")
        
        return ""
    
    @pyqtSlot(str, result=int)
    def getCachedDuration(self, file_path: str) -> int:
        """
        Get cached duration for a file from metadata.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Cached duration in milliseconds, or 0 if not available
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return 0
            
            directory = path.parent
            duration_cache = self._load_duration_cache(directory)
            
            # Try both with and without extension
            filename = path.name
            if filename in duration_cache:
                return duration_cache[filename]
            
            # Try stem (without extension)
            stem = path.stem
            if stem in duration_cache:
                return duration_cache[stem]
                
        except Exception as e:
            print(f"Error getting cached duration: {e}")
        
        return 0
