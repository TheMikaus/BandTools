#!/usr/bin/env python3
"""
Data Models Module

QML-exposed data models for the AudioBrowser application.
Provides list and table models for file lists, annotations, and clips.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from PyQt6.QtCore import (
    Qt, QAbstractListModel, QAbstractTableModel, QModelIndex,
    pyqtSignal, pyqtSlot
)


class FileListModel(QAbstractListModel):
    """
    List model for audio files.
    
    Exposes a list of audio files to QML with metadata like filename,
    path, size, and duration.
    """
    
    # Custom roles for QML access
    FilePathRole = Qt.ItemDataRole.UserRole + 1
    FileNameRole = Qt.ItemDataRole.UserRole + 2
    BasNameRole = Qt.ItemDataRole.UserRole + 3
    FileSizeRole = Qt.ItemDataRole.UserRole + 4
    DurationRole = Qt.ItemDataRole.UserRole + 5
    ExtensionRole = Qt.ItemDataRole.UserRole + 6
    IsBestTakeRole = Qt.ItemDataRole.UserRole + 7
    IsPartialTakeRole = Qt.ItemDataRole.UserRole + 8
    BPMRole = Qt.ItemDataRole.UserRole + 9
    
    # Signals
    filesChanged = pyqtSignal()
    
    def __init__(self, parent=None, file_manager=None, tempo_manager=None):
        """
        Initialize the file list model.
        
        Args:
            parent: Parent QObject
            file_manager: Optional FileManager for extracting file metadata
            tempo_manager: Optional TempoManager for BPM data
        """
        super().__init__(parent)
        self._files: List[Dict[str, Any]] = []
        self._file_manager = file_manager
        self._tempo_manager = tempo_manager
    
    def rowCount(self, parent=QModelIndex()) -> int:
        """Return the number of files in the model."""
        if parent.isValid():
            return 0
        return len(self._files)
    
    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Return data for the specified role at the given index."""
        if not index.isValid() or not (0 <= index.row() < len(self._files)):
            return None
        
        file_data = self._files[index.row()]
        
        if role == Qt.ItemDataRole.DisplayRole or role == self.FileNameRole:
            return file_data.get("filename", "")
        elif role == self.FilePathRole:
            return file_data.get("filepath", "")
        elif role == self.BasNameRole:
            return file_data.get("basename", "")
        elif role == self.FileSizeRole:
            return file_data.get("filesize", 0)
        elif role == self.DurationRole:
            return file_data.get("duration", 0)
        elif role == self.ExtensionRole:
            return file_data.get("extension", "")
        elif role == self.IsBestTakeRole:
            return file_data.get("isBestTake", False)
        elif role == self.IsPartialTakeRole:
            return file_data.get("isPartialTake", False)
        elif role == self.BPMRole:
            return file_data.get("bpm", 0)
        
        return None
    
    def roleNames(self) -> Dict[int, bytes]:
        """Return the role names for QML access."""
        return {
            Qt.ItemDataRole.DisplayRole: b"display",
            self.FilePathRole: b"filepath",
            self.FileNameRole: b"filename",
            self.BasNameRole: b"basename",
            self.FileSizeRole: b"filesize",
            self.DurationRole: b"duration",
            self.ExtensionRole: b"extension",
            self.IsBestTakeRole: b"isBestTake",
            self.IsPartialTakeRole: b"isPartialTake",
            self.BPMRole: b"bpm",
        }
    
    # ========== QML-accessible methods ==========
    
    @pyqtSlot(list)
    def setFiles(self, file_paths: List[str]) -> None:
        """
        Set the list of files in the model.
        
        Args:
            file_paths: List of file paths
        """
        self.beginResetModel()
        
        self._files = []
        for file_path in file_paths:
            try:
                path = Path(file_path)
                
                # Extract duration if file_manager is available
                # Try cached duration first, then extract from audio file
                duration_ms = 0
                if self._file_manager is not None:
                    # Try to get cached duration from .duration_cache.json
                    duration_ms = self._file_manager.getCachedDuration(file_path)
                    # If not cached, extract from audio file
                    if duration_ms == 0:
                        duration_ms = self._file_manager.getAudioDuration(file_path)
                
                # Get provided name from .provided_names.json if available
                display_name = path.name
                if self._file_manager is not None:
                    provided_name = self._file_manager.getProvidedName(file_path)
                    if provided_name:
                        display_name = provided_name
                
                # Get best/partial take status
                is_best_take = False
                is_partial_take = False
                if self._file_manager is not None:
                    is_best_take = self._file_manager.isBestTake(file_path)
                    is_partial_take = self._file_manager.isPartialTake(file_path)
                
                # Get BPM from tempo manager
                bpm = 0
                if self._tempo_manager is not None:
                    bpm = self._tempo_manager.getBPM(path.name)
                
                file_info = {
                    "filepath": str(path),
                    "filename": display_name,  # Use provided name if available
                    "basename": path.stem,
                    "extension": path.suffix,
                    "filesize": path.stat().st_size if path.exists() else 0,
                    "duration": duration_ms,
                    "isBestTake": is_best_take,
                    "isPartialTake": is_partial_take,
                    "bpm": bpm,
                }
                self._files.append(file_info)
            except Exception:
                # Skip files that can't be processed
                continue
        
        self.endResetModel()
        self.filesChanged.emit()
    
    @pyqtSlot()
    def clear(self) -> None:
        """Clear all files from the model."""
        self.beginResetModel()
        self._files.clear()
        self.endResetModel()
        self.filesChanged.emit()
    
    @pyqtSlot(int, result=str)
    def getFilePath(self, row: int) -> str:
        """
        Get the file path at the specified row.
        
        Args:
            row: Row index
            
        Returns:
            File path or empty string if invalid row
        """
        if 0 <= row < len(self._files):
            return self._files[row].get("filepath", "")
        return ""
    
    @pyqtSlot(result=int)
    def count(self) -> int:
        """
        Get the number of files in the model.
        
        Returns:
            File count
        """
        return len(self._files)
    
    @pyqtSlot(str, result=int)
    def findFileIndex(self, file_path: str) -> int:
        """
        Find the index of a file by its path.
        
        Args:
            file_path: File path to search for
            
        Returns:
            Row index or -1 if not found
        """
        for i, file_data in enumerate(self._files):
            if file_data.get("filepath") == file_path:
                return i
        return -1
    
    @pyqtSlot(str, bool)
    def sortBy(self, field: str, ascending: bool = True) -> None:
        """
        Sort files by a specific field.
        
        Args:
            field: Field name to sort by ("filename", "filesize", "duration")
            ascending: True for ascending order, False for descending
        """
        self.beginResetModel()
        
        try:
            # Map field names to dict keys
            field_map = {
                "filename": "filename",
                "name": "filename",
                "size": "filesize",
                "filesize": "filesize",
                "duration": "duration",
            }
            
            sort_key = field_map.get(field.lower(), "filename")
            
            # Sort the files
            self._files.sort(
                key=lambda f: f.get(sort_key, 0) if sort_key != "filename" else f.get(sort_key, "").lower(),
                reverse=not ascending
            )
            
        except Exception as e:
            print(f"Error sorting files: {e}")
        
        self.endResetModel()
        self.filesChanged.emit()


class FolderTreeModel(QAbstractListModel):
    """
    List model for folder tree.
    
    Exposes a hierarchical folder structure to QML with folders
    that can be expanded to show subfolders and their audio files.
    """
    
    # Custom roles for QML access
    PathRole = Qt.ItemDataRole.UserRole + 1
    NameRole = Qt.ItemDataRole.UserRole + 2
    ParentRole = Qt.ItemDataRole.UserRole + 3
    HasAudioRole = Qt.ItemDataRole.UserRole + 4
    AudioCountRole = Qt.ItemDataRole.UserRole + 5
    IsRootRole = Qt.ItemDataRole.UserRole + 6
    LevelRole = Qt.ItemDataRole.UserRole + 7
    
    # Signals
    foldersChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the folder tree model."""
        super().__init__(parent)
        self._folders: List[Dict[str, Any]] = []
    
    def rowCount(self, parent=QModelIndex()) -> int:
        """Return the number of folders in the model."""
        if parent.isValid():
            return 0
        return len(self._folders)
    
    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Return data for the specified role at the given index."""
        if not index.isValid() or not (0 <= index.row() < len(self._folders)):
            return None
        
        folder_data = self._folders[index.row()]
        
        if role == Qt.ItemDataRole.DisplayRole or role == self.NameRole:
            return folder_data.get("name", "")
        elif role == self.PathRole:
            return folder_data.get("path", "")
        elif role == self.ParentRole:
            return folder_data.get("parent", "")
        elif role == self.HasAudioRole:
            return folder_data.get("hasAudio", False)
        elif role == self.AudioCountRole:
            return folder_data.get("audioCount", 0)
        elif role == self.IsRootRole:
            return folder_data.get("isRoot", False)
        elif role == self.LevelRole:
            return folder_data.get("level", 0)
        
        return None
    
    def roleNames(self) -> Dict[int, bytes]:
        """Return the role names for QML access."""
        return {
            Qt.ItemDataRole.DisplayRole: b"display",
            self.PathRole: b"path",
            self.NameRole: b"name",
            self.ParentRole: b"parent",
            self.HasAudioRole: b"hasAudio",
            self.AudioCountRole: b"audioCount",
            self.IsRootRole: b"isRoot",
            self.LevelRole: b"level",
        }
    
    @pyqtSlot(list)
    def setFolders(self, folders: List[Dict[str, Any]]) -> None:
        """
        Set the list of folders in the model.
        
        Args:
            folders: List of folder dictionaries
        """
        self.beginResetModel()
        
        self._folders = []
        for folder in folders:
            # Calculate level based on path depth relative to root
            path_str = folder.get('path', '')
            parent_str = folder.get('parent', '')
            
            level = 0
            if not folder.get('isRoot', False):
                # Count path separators to determine level
                if parent_str:
                    level = path_str.count('/') - parent_str.count('/')
                else:
                    level = 1
            
            folder_info = {
                "path": path_str,
                "name": folder.get("name", ""),
                "parent": parent_str,
                "hasAudio": folder.get("hasAudio", False),
                "audioCount": folder.get("audioCount", 0),
                "isRoot": folder.get("isRoot", False),
                "level": level,
            }
            self._folders.append(folder_info)
        
        self.endResetModel()
        self.foldersChanged.emit()
    
    @pyqtSlot()
    def clear(self) -> None:
        """Clear all folders from the model."""
        self.beginResetModel()
        self._folders.clear()
        self.endResetModel()
        self.foldersChanged.emit()
    
    @pyqtSlot(result=int)
    def count(self) -> int:
        """Get the number of folders in the model."""
        return len(self._folders)
    
    @pyqtSlot(int, result=str)
    def getFolderPath(self, row: int) -> str:
        """Get the folder path at the specified row."""
        if 0 <= row < len(self._folders):
            return self._folders[row].get("path", "")
        return ""


class AnnotationsModel(QAbstractTableModel):
    """
    Table model for annotations.
    
    Exposes annotations data to QML with columns for timestamp,
    category, text, importance, etc.
    Supports merged view with annotation set name column.
    """
    
    # Column indices (single set view)
    COL_TIMESTAMP = 0
    COL_CATEGORY = 1
    COL_TEXT = 2
    COL_USER = 3
    COL_IMPORTANCE = 4
    COL_COUNT = 5
    
    # Column indices (merged view - with set column)
    COL_MERGED_SET = 0
    COL_MERGED_TIMESTAMP = 1
    COL_MERGED_CATEGORY = 2
    COL_MERGED_TEXT = 3
    COL_MERGED_USER = 4
    COL_MERGED_IMPORTANCE = 5
    COL_MERGED_COUNT = 6
    
    # Custom roles
    TimestampRole = Qt.ItemDataRole.UserRole + 1
    CategoryRole = Qt.ItemDataRole.UserRole + 2
    TextRole = Qt.ItemDataRole.UserRole + 3
    UserRole = Qt.ItemDataRole.UserRole + 4
    ImportanceRole = Qt.ItemDataRole.UserRole + 5
    ColorRole = Qt.ItemDataRole.UserRole + 6
    SetNameRole = Qt.ItemDataRole.UserRole + 7  # For merged view
    SetColorRole = Qt.ItemDataRole.UserRole + 8  # For merged view
    
    # Signals
    annotationsChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the annotations model."""
        super().__init__(parent)
        self._annotations: List[Dict[str, Any]] = []
        self._headers = ["Time", "Category", "Text", "User", "Important"]
        self._merged_headers = ["Set", "Time", "Category", "Text", "User", "Important"]
        self._show_merged = False  # Whether we're in merged view mode
    
    def rowCount(self, parent=QModelIndex()) -> int:
        """Return the number of annotations."""
        if parent.isValid():
            return 0
        return len(self._annotations)
    
    def columnCount(self, parent=QModelIndex()) -> int:
        """Return the number of columns."""
        if parent.isValid():
            return 0
        return self.COL_MERGED_COUNT if self._show_merged else self.COL_COUNT
    
    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Return data for the specified role at the given index."""
        if not index.isValid() or not (0 <= index.row() < len(self._annotations)):
            return None
        
        annotation = self._annotations[index.row()]
        col = index.column()
        
        if role == Qt.ItemDataRole.DisplayRole:
            if self._show_merged:
                # Merged view columns
                if col == self.COL_MERGED_SET:
                    return annotation.get("_set_name", "")
                elif col == self.COL_MERGED_TIMESTAMP:
                    return self._format_timestamp(annotation.get("timestamp_ms", 0))
                elif col == self.COL_MERGED_CATEGORY:
                    return annotation.get("category", "")
                elif col == self.COL_MERGED_TEXT:
                    return annotation.get("text", "")
                elif col == self.COL_MERGED_USER:
                    return annotation.get("user", "default_user")
                elif col == self.COL_MERGED_IMPORTANCE:
                    return "✓" if annotation.get("important", False) else ""
            else:
                # Single set view columns
                if col == self.COL_TIMESTAMP:
                    return self._format_timestamp(annotation.get("timestamp_ms", 0))
                elif col == self.COL_CATEGORY:
                    return annotation.get("category", "")
                elif col == self.COL_TEXT:
                    return annotation.get("text", "")
                elif col == self.COL_USER:
                    return annotation.get("user", "default_user")
                elif col == self.COL_IMPORTANCE:
                    return "✓" if annotation.get("important", False) else ""
        
        elif role == self.TimestampRole:
            return annotation.get("timestamp_ms", 0)
        elif role == self.CategoryRole:
            return annotation.get("category", "")
        elif role == self.TextRole:
            return annotation.get("text", "")
        elif role == self.UserRole:
            return annotation.get("user", "default_user")
        elif role == self.ImportanceRole:
            return annotation.get("important", False)
        elif role == self.ColorRole:
            return annotation.get("color", "#ffffff")
        elif role == self.SetNameRole:
            return annotation.get("_set_name", "")
        elif role == self.SetColorRole:
            return annotation.get("_set_color", "#ffffff")
        
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Return header data for the table."""
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            headers = self._merged_headers if self._show_merged else self._headers
            if 0 <= section < len(headers):
                return headers[section]
        return None
    
    def roleNames(self) -> Dict[int, bytes]:
        """Return the role names for QML access."""
        return {
            Qt.ItemDataRole.DisplayRole: b"display",
            self.TimestampRole: b"timestamp",
            self.CategoryRole: b"category",
            self.TextRole: b"text",
            self.UserRole: b"user",
            self.ImportanceRole: b"important",
            self.ColorRole: b"color",
            self.SetNameRole: b"setName",
            self.SetColorRole: b"setColor",
        }
    
    # ========== QML-accessible methods ==========
    
    @pyqtSlot(list)
    def setAnnotations(self, annotations: List[Dict[str, Any]]) -> None:
        """
        Set the list of annotations in the model.
        Automatically detects merged view if annotations contain _set_name.
        
        Args:
            annotations: List of annotation dictionaries
        """
        self.beginResetModel()
        self._annotations = annotations.copy()
        
        # Auto-detect merged view mode
        self._show_merged = any("_set_name" in a for a in annotations)
        
        self.endResetModel()
        self.annotationsChanged.emit()
    
    @pyqtSlot()
    def clear(self) -> None:
        """Clear all annotations from the model."""
        self.beginResetModel()
        self._annotations.clear()
        self.endResetModel()
        self.annotationsChanged.emit()
    
    @pyqtSlot(result=int)
    def count(self) -> int:
        """
        Get the number of annotations in the model.
        
        Returns:
            Annotation count
        """
        return len(self._annotations)
    
    # ========== Helper methods ==========
    
    def _format_timestamp(self, ms: int) -> str:
        """
        Format a timestamp in milliseconds as MM:SS.mmm
        
        Args:
            ms: Timestamp in milliseconds
            
        Returns:
            Formatted timestamp string
        """
        total_seconds = ms / 1000.0
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        milliseconds = int((total_seconds % 1) * 1000)
        
        return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
