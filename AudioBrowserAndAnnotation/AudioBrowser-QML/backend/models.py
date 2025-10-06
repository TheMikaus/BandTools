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
    
    # Signals
    filesChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the file list model."""
        super().__init__(parent)
        self._files: List[Dict[str, Any]] = []
    
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
                file_info = {
                    "filepath": str(path),
                    "filename": path.name,
                    "basename": path.stem,
                    "extension": path.suffix,
                    "filesize": path.stat().st_size if path.exists() else 0,
                    "duration": 0,  # Will be populated later if needed
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


class AnnotationsModel(QAbstractTableModel):
    """
    Table model for annotations.
    
    Exposes annotations data to QML with columns for timestamp,
    category, text, importance, etc.
    """
    
    # Column indices
    COL_TIMESTAMP = 0
    COL_CATEGORY = 1
    COL_TEXT = 2
    COL_IMPORTANCE = 3
    COL_COUNT = 4
    
    # Custom roles
    TimestampRole = Qt.ItemDataRole.UserRole + 1
    CategoryRole = Qt.ItemDataRole.UserRole + 2
    TextRole = Qt.ItemDataRole.UserRole + 3
    ImportanceRole = Qt.ItemDataRole.UserRole + 4
    ColorRole = Qt.ItemDataRole.UserRole + 5
    
    # Signals
    annotationsChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the annotations model."""
        super().__init__(parent)
        self._annotations: List[Dict[str, Any]] = []
        self._headers = ["Time", "Category", "Text", "Important"]
    
    def rowCount(self, parent=QModelIndex()) -> int:
        """Return the number of annotations."""
        if parent.isValid():
            return 0
        return len(self._annotations)
    
    def columnCount(self, parent=QModelIndex()) -> int:
        """Return the number of columns."""
        if parent.isValid():
            return 0
        return self.COL_COUNT
    
    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Return data for the specified role at the given index."""
        if not index.isValid() or not (0 <= index.row() < len(self._annotations)):
            return None
        
        annotation = self._annotations[index.row()]
        col = index.column()
        
        if role == Qt.ItemDataRole.DisplayRole:
            if col == self.COL_TIMESTAMP:
                return self._format_timestamp(annotation.get("timestamp_ms", 0))
            elif col == self.COL_CATEGORY:
                return annotation.get("category", "")
            elif col == self.COL_TEXT:
                return annotation.get("text", "")
            elif col == self.COL_IMPORTANCE:
                return "✓" if annotation.get("important", False) else ""
        
        elif role == self.TimestampRole:
            return annotation.get("timestamp_ms", 0)
        elif role == self.CategoryRole:
            return annotation.get("category", "")
        elif role == self.TextRole:
            return annotation.get("text", "")
        elif role == self.ImportanceRole:
            return annotation.get("important", False)
        elif role == self.ColorRole:
            return annotation.get("color", "#ffffff")
        
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Return header data for the table."""
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            if 0 <= section < len(self._headers):
                return self._headers[section]
        return None
    
    def roleNames(self) -> Dict[int, bytes]:
        """Return the role names for QML access."""
        return {
            Qt.ItemDataRole.DisplayRole: b"display",
            self.TimestampRole: b"timestamp",
            self.CategoryRole: b"category",
            self.TextRole: b"text",
            self.ImportanceRole: b"important",
            self.ColorRole: b"color",
        }
    
    # ========== QML-accessible methods ==========
    
    @pyqtSlot(list)
    def setAnnotations(self, annotations: List[Dict[str, Any]]) -> None:
        """
        Set the list of annotations in the model.
        
        Args:
            annotations: List of annotation dictionaries
        """
        self.beginResetModel()
        self._annotations = annotations.copy()
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
