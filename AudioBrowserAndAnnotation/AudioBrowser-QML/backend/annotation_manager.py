#!/usr/bin/env python3
"""
Annotation Manager Module

Manages annotations for audio files with CRUD operations, persistence,
and multi-user support. Provides QML integration via signals and slots.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot


class AnnotationManager(QObject):
    """
    Manages annotations for audio files.
    
    Provides CRUD operations, JSON persistence, multi-user support,
    and signals for QML integration.
    
    Features:
    - Create, read, update, delete annotations
    - JSON file-based storage (per audio file)
    - Multi-user support with username tracking
    - Category-based organization
    - Importance flagging
    - Automatic timestamp tracking
    - Signal emissions for UI updates
    """
    
    # Signals for state changes
    annotationsChanged = pyqtSignal(str)  # Emitted when annotations change (file path)
    annotationAdded = pyqtSignal(str, dict)  # file path, annotation data
    annotationUpdated = pyqtSignal(str, int)  # file path, annotation index
    annotationDeleted = pyqtSignal(str, int)  # file path, annotation index
    currentFileChanged = pyqtSignal(str)  # Current file path
    errorOccurred = pyqtSignal(str)  # Error message
    
    def __init__(self, parent=None):
        """Initialize the annotation manager."""
        super().__init__(parent)
        self._current_file: str = ""
        self._current_user: str = "default_user"
        self._annotations: Dict[str, List[Dict[str, Any]]] = {}  # filepath -> annotations
        self._categories = ["timing", "energy", "harmony", "dynamics", "notes"]
        
    # ========== QML-accessible methods ==========
    
    @pyqtSlot(str)
    def setCurrentFile(self, file_path: str) -> None:
        """
        Set the current audio file for annotation management.
        
        Args:
            file_path: Path to the audio file
        """
        if file_path != self._current_file:
            self._current_file = file_path
            self.currentFileChanged.emit(file_path)
            
            # Load annotations for this file if not already loaded
            if file_path and file_path not in self._annotations:
                self._load_annotations(file_path)
    
    @pyqtSlot(result=str)
    def getCurrentFile(self) -> str:
        """Get the current file path."""
        return self._current_file
    
    @pyqtSlot(str)
    def setCurrentUser(self, username: str) -> None:
        """
        Set the current user for annotation creation.
        
        Args:
            username: Username for annotation attribution
        """
        self._current_user = username if username else "default_user"
    
    @pyqtSlot(result=str)
    def getCurrentUser(self) -> str:
        """Get the current username."""
        return self._current_user
    
    @pyqtSlot(int, str, str, bool, str)
    def addAnnotation(self, timestamp_ms: int, text: str, category: str = "",
                     important: bool = False, color: str = "#3498db") -> None:
        """
        Add a new annotation to the current file.
        
        Args:
            timestamp_ms: Timestamp in milliseconds
            text: Annotation text
            category: Category (e.g., "timing", "energy")
            important: Whether this is an important annotation
            color: Color for the marker (hex format)
        """
        if not self._current_file:
            self.errorOccurred.emit("No file selected")
            return
        
        if not text.strip():
            self.errorOccurred.emit("Annotation text cannot be empty")
            return
        
        annotation = {
            "timestamp_ms": timestamp_ms,
            "text": text.strip(),
            "category": category,
            "important": important,
            "color": color,
            "user": self._current_user,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Ensure file has annotation list
        if self._current_file not in self._annotations:
            self._annotations[self._current_file] = []
        
        # Add annotation
        self._annotations[self._current_file].append(annotation)
        
        # Sort by timestamp
        self._annotations[self._current_file].sort(key=lambda a: a["timestamp_ms"])
        
        # Save to disk
        self._save_annotations(self._current_file)
        
        # Emit signals
        self.annotationAdded.emit(self._current_file, annotation)
        self.annotationsChanged.emit(self._current_file)
    
    @pyqtSlot(int, int, str, str, bool, str)
    def updateAnnotation(self, index: int, timestamp_ms: int, text: str,
                        category: str = "", important: bool = False,
                        color: str = "#3498db") -> None:
        """
        Update an existing annotation.
        
        Args:
            index: Index of the annotation to update
            timestamp_ms: New timestamp in milliseconds
            text: New annotation text
            category: New category
            important: New importance flag
            color: New color
        """
        if not self._current_file:
            self.errorOccurred.emit("No file selected")
            return
        
        if self._current_file not in self._annotations:
            self.errorOccurred.emit("No annotations for current file")
            return
        
        annotations = self._annotations[self._current_file]
        if not (0 <= index < len(annotations)):
            self.errorOccurred.emit(f"Invalid annotation index: {index}")
            return
        
        if not text.strip():
            self.errorOccurred.emit("Annotation text cannot be empty")
            return
        
        # Update annotation
        annotation = annotations[index]
        annotation["timestamp_ms"] = timestamp_ms
        annotation["text"] = text.strip()
        annotation["category"] = category
        annotation["important"] = important
        annotation["color"] = color
        annotation["updated_at"] = datetime.now().isoformat()
        
        # Re-sort by timestamp
        annotations.sort(key=lambda a: a["timestamp_ms"])
        
        # Save to disk
        self._save_annotations(self._current_file)
        
        # Emit signals
        self.annotationUpdated.emit(self._current_file, index)
        self.annotationsChanged.emit(self._current_file)
    
    @pyqtSlot(int)
    def deleteAnnotation(self, index: int) -> None:
        """
        Delete an annotation by index.
        
        Args:
            index: Index of the annotation to delete
        """
        if not self._current_file:
            self.errorOccurred.emit("No file selected")
            return
        
        if self._current_file not in self._annotations:
            self.errorOccurred.emit("No annotations for current file")
            return
        
        annotations = self._annotations[self._current_file]
        if not (0 <= index < len(annotations)):
            self.errorOccurred.emit(f"Invalid annotation index: {index}")
            return
        
        # Delete annotation
        del annotations[index]
        
        # Save to disk
        self._save_annotations(self._current_file)
        
        # Emit signals
        self.annotationDeleted.emit(self._current_file, index)
        self.annotationsChanged.emit(self._current_file)
    
    @pyqtSlot()
    def clearAnnotations(self) -> None:
        """Clear all annotations for the current file."""
        if not self._current_file:
            return
        
        if self._current_file in self._annotations:
            self._annotations[self._current_file].clear()
            self._save_annotations(self._current_file)
            self.annotationsChanged.emit(self._current_file)
    
    @pyqtSlot(result=list)
    def getAnnotations(self) -> List[Dict[str, Any]]:
        """
        Get all annotations for the current file.
        
        Returns:
            List of annotation dictionaries
        """
        if not self._current_file:
            return []
        
        return self._annotations.get(self._current_file, [])
    
    @pyqtSlot(int, result='QVariantMap')
    def getAnnotation(self, index: int) -> Dict[str, Any]:
        """
        Get a specific annotation by index.
        
        Args:
            index: Annotation index
            
        Returns:
            Annotation dictionary or empty dict if invalid
        """
        if not self._current_file:
            return {}
        
        annotations = self._annotations.get(self._current_file, [])
        if 0 <= index < len(annotations):
            return annotations[index]
        
        return {}
    
    @pyqtSlot(result=int)
    def getAnnotationCount(self) -> int:
        """
        Get the number of annotations for the current file.
        
        Returns:
            Annotation count
        """
        if not self._current_file:
            return 0
        
        return len(self._annotations.get(self._current_file, []))
    
    @pyqtSlot(result=list)
    def getAllUsers(self) -> List[str]:
        """
        Get a list of all users who have created annotations for the current file.
        
        Returns:
            List of unique usernames
        """
        if not self._current_file:
            return []
        
        annotations = self._annotations.get(self._current_file, [])
        users = set()
        for annotation in annotations:
            user = annotation.get("user", "default_user")
            users.add(user)
        
        return sorted(list(users))
    
    @pyqtSlot(str, result=list)
    def getAnnotationsForUser(self, username: str) -> List[Dict[str, Any]]:
        """
        Get annotations for a specific user.
        
        Args:
            username: Username to filter by, or empty string for all users
            
        Returns:
            List of annotation dictionaries
        """
        if not self._current_file:
            return []
        
        annotations = self._annotations.get(self._current_file, [])
        
        # If username is empty, return all annotations
        if not username:
            return annotations
        
        # Filter by user
        return [a for a in annotations if a.get("user", "default_user") == username]
    
    @pyqtSlot(int, result=int)
    def findAnnotationAtTime(self, timestamp_ms: int, tolerance_ms: int = 500) -> int:
        """
        Find an annotation near the given timestamp.
        
        Args:
            timestamp_ms: Target timestamp in milliseconds
            tolerance_ms: Time tolerance in milliseconds
            
        Returns:
            Index of the nearest annotation within tolerance, or -1 if none found
        """
        if not self._current_file:
            return -1
        
        annotations = self._annotations.get(self._current_file, [])
        
        for i, annotation in enumerate(annotations):
            time_diff = abs(annotation["timestamp_ms"] - timestamp_ms)
            if time_diff <= tolerance_ms:
                return i
        
        return -1
    
    @pyqtSlot(str, result=list)
    def filterByCategory(self, category: str) -> List[Dict[str, Any]]:
        """
        Get annotations filtered by category.
        
        Args:
            category: Category to filter by
            
        Returns:
            List of matching annotations
        """
        if not self._current_file:
            return []
        
        annotations = self._annotations.get(self._current_file, [])
        
        if not category:
            return annotations
        
        return [a for a in annotations if a.get("category") == category]
    
    @pyqtSlot(result=list)
    def getImportantAnnotations(self) -> List[Dict[str, Any]]:
        """
        Get all important annotations for the current file.
        
        Returns:
            List of important annotations
        """
        if not self._current_file:
            return []
        
        annotations = self._annotations.get(self._current_file, [])
        return [a for a in annotations if a.get("important", False)]
    
    @pyqtSlot(result=list)
    def getCategories(self) -> List[str]:
        """
        Get the list of available categories.
        
        Returns:
            List of category names
        """
        return self._categories.copy()
    
    @pyqtSlot(str)
    def addCategory(self, category: str) -> None:
        """
        Add a new category to the available list.
        
        Args:
            category: Category name to add
        """
        if category and category not in self._categories:
            self._categories.append(category)
    
    @pyqtSlot(str)
    def loadAnnotations(self, file_path: str) -> None:
        """
        Explicitly load annotations for a file.
        
        Args:
            file_path: Path to the audio file
        """
        self._load_annotations(file_path)
        self.annotationsChanged.emit(file_path)
    
    @pyqtSlot(str)
    def saveAnnotations(self, file_path: str) -> None:
        """
        Explicitly save annotations for a file.
        
        Args:
            file_path: Path to the audio file
        """
        self._save_annotations(file_path)
    
    # ========== Internal methods ==========
    
    def _get_annotation_file_path(self, audio_file_path: str) -> Path:
        """
        Get the path to the annotation file for a given audio file.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Path to the annotation JSON file
        """
        audio_path = Path(audio_file_path)
        annotation_file = audio_path.parent / f".{audio_path.stem}_annotations.json"
        return annotation_file
    
    def _load_annotations(self, file_path: str) -> None:
        """
        Load annotations from disk for a file.
        
        Args:
            file_path: Path to the audio file
        """
        if not file_path:
            return
        
        annotation_file = self._get_annotation_file_path(file_path)
        
        if annotation_file.exists():
            try:
                with open(annotation_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Support both old and new formats
                if isinstance(data, list):
                    self._annotations[file_path] = data
                elif isinstance(data, dict):
                    # Multi-user format: {"users": {"user1": [...], "user2": [...]}}
                    # For now, merge all users' annotations
                    all_annotations = []
                    if "users" in data:
                        for user, user_annotations in data["users"].items():
                            for annotation in user_annotations:
                                annotation["user"] = user
                                all_annotations.append(annotation)
                    elif "annotations" in data:
                        all_annotations = data["annotations"]
                    
                    self._annotations[file_path] = all_annotations
                    
                # Sort by timestamp
                self._annotations[file_path].sort(key=lambda a: a.get("timestamp_ms", 0))
                
            except Exception as e:
                self.errorOccurred.emit(f"Failed to load annotations: {str(e)}")
                self._annotations[file_path] = []
        else:
            self._annotations[file_path] = []
    
    def _save_annotations(self, file_path: str) -> None:
        """
        Save annotations to disk for a file.
        
        Args:
            file_path: Path to the audio file
        """
        if not file_path or file_path not in self._annotations:
            return
        
        annotation_file = self._get_annotation_file_path(file_path)
        
        try:
            # Create parent directory if it doesn't exist
            annotation_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save as simple list format
            with open(annotation_file, 'w', encoding='utf-8') as f:
                json.dump(self._annotations[file_path], f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.errorOccurred.emit(f"Failed to save annotations: {str(e)}")
    
    # ========== Export methods ==========
    
    @pyqtSlot(str, str, result=bool)
    def exportAnnotations(self, export_path: str, export_format: str = "text") -> bool:
        """
        Export annotations to a file in the specified format.
        
        Args:
            export_path: Path to save the export file
            export_format: Export format - "text", "csv", or "markdown"
            
        Returns:
            True if export was successful, False otherwise
        """
        if not self._current_file:
            self.errorOccurred.emit("No file selected")
            return False
        
        annotations = self._annotations.get(self._current_file, [])
        if not annotations:
            self.errorOccurred.emit("No annotations to export")
            return False
        
        try:
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            if export_format == "csv":
                self._export_csv(export_file, annotations)
            elif export_format == "markdown":
                self._export_markdown(export_file, annotations)
            else:  # default to text
                self._export_text(export_file, annotations)
            
            return True
            
        except Exception as e:
            self.errorOccurred.emit(f"Failed to export annotations: {str(e)}")
            return False
    
    def _export_text(self, export_file: Path, annotations: List[Dict[str, Any]]) -> None:
        """Export annotations as plain text."""
        with open(export_file, 'w', encoding='utf-8') as f:
            f.write(f"Annotations for: {Path(self._current_file).name}\n")
            f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            for i, annotation in enumerate(annotations, 1):
                timestamp_ms = annotation.get("timestamp_ms", 0)
                minutes = timestamp_ms // 60000
                seconds = (timestamp_ms % 60000) / 1000
                
                f.write(f"[{i}] {minutes:02.0f}:{seconds:06.3f}\n")
                f.write(f"    Category: {annotation.get('category', 'notes')}\n")
                f.write(f"    User: {annotation.get('user', 'unknown')}\n")
                
                if annotation.get("important", False):
                    f.write(f"    ⭐ IMPORTANT\n")
                
                f.write(f"    Text: {annotation.get('text', '')}\n")
                f.write("\n")
    
    def _export_csv(self, export_file: Path, annotations: List[Dict[str, Any]]) -> None:
        """Export annotations as CSV."""
        import csv
        
        with open(export_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['Timestamp', 'Time (MM:SS.mmm)', 'Category', 'User', 'Important', 'Text'])
            
            # Write annotations
            for annotation in annotations:
                timestamp_ms = annotation.get("timestamp_ms", 0)
                minutes = timestamp_ms // 60000
                seconds = (timestamp_ms % 60000) / 1000
                time_str = f"{minutes:02.0f}:{seconds:06.3f}"
                
                writer.writerow([
                    timestamp_ms,
                    time_str,
                    annotation.get('category', 'notes'),
                    annotation.get('user', 'unknown'),
                    'Yes' if annotation.get('important', False) else 'No',
                    annotation.get('text', '')
                ])
    
    def _export_markdown(self, export_file: Path, annotations: List[Dict[str, Any]]) -> None:
        """Export annotations as Markdown."""
        with open(export_file, 'w', encoding='utf-8') as f:
            f.write(f"# Annotations for {Path(self._current_file).name}\n\n")
            f.write(f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total annotations:** {len(annotations)}\n\n")
            f.write("---\n\n")
            
            for i, annotation in enumerate(annotations, 1):
                timestamp_ms = annotation.get("timestamp_ms", 0)
                minutes = timestamp_ms // 60000
                seconds = (timestamp_ms % 60000) / 1000
                
                important_marker = "⭐ " if annotation.get("important", False) else ""
                
                f.write(f"## {important_marker}[{i}] {minutes:02.0f}:{seconds:06.3f}\n\n")
                f.write(f"- **Category:** {annotation.get('category', 'notes')}\n")
                f.write(f"- **User:** {annotation.get('user', 'unknown')}\n")
                f.write(f"\n{annotation.get('text', '')}\n\n")
                f.write("---\n\n")
