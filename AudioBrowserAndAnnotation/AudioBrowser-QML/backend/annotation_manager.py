#!/usr/bin/env python3
"""
Annotation Manager Module

Manages annotations for audio files with CRUD operations, persistence,
and multi-user support. Provides QML integration via signals and slots.

Enhanced with multi-annotation sets support for feature parity with original application.
"""

import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, pyqtProperty


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
    - Multi-annotation sets with switching and merged view
    - Signal emissions for UI updates
    """
    
    # Signals for state changes
    annotationsChanged = pyqtSignal(str)  # Emitted when annotations change (file path)
    annotationAdded = pyqtSignal(str, dict)  # file path, annotation data
    annotationUpdated = pyqtSignal(str, int)  # file path, annotation index
    annotationDeleted = pyqtSignal(str, int)  # file path, annotation index
    currentFileChanged = pyqtSignal(str)  # Current file path
    errorOccurred = pyqtSignal(str)  # Error message
    
    # Annotation set signals
    annotationSetsChanged = pyqtSignal()  # Emitted when annotation sets change
    currentSetChanged = pyqtSignal(str)  # Emitted when current set changes (set_id)
    showAllSetsChanged = pyqtSignal(bool)  # Emitted when show all sets toggle changes
    
    def __init__(self, parent=None):
        """Initialize the annotation manager."""
        super().__init__(parent)
        self._current_file: str = ""
        self._current_user: str = "default_user"
        self._annotations: Dict[str, List[Dict[str, Any]]] = {}  # filepath -> annotations (legacy single set)
        self._categories = ["timing", "energy", "harmony", "dynamics", "notes"]
        self._next_uid = 1  # Counter for generating unique IDs
        self._undo_manager = None  # Will be set by main app
        self._current_directory: Optional[Path] = None
        
        # Multi-annotation sets support
        self._annotation_sets: List[Dict[str, Any]] = []  # List of annotation sets
        self._current_set_id: Optional[str] = None  # ID of the currently active set
        self._show_all_sets: bool = False  # Whether to show annotations from all visible sets
        
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
    
    def setUndoManager(self, undo_manager):
        """Set the undo manager for recording undoable operations."""
        self._undo_manager = undo_manager
    
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
            "uid": self._next_uid,
            "timestamp_ms": timestamp_ms,
            "text": text.strip(),
            "category": category,
            "important": important,
            "color": color,
            "user": self._current_user,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        self._next_uid += 1
        
        # Ensure file has annotation list
        if self._current_file not in self._annotations:
            self._annotations[self._current_file] = []
        
        # Add annotation
        self._annotations[self._current_file].append(annotation)
        
        # Sort by timestamp
        self._annotations[self._current_file].sort(key=lambda a: a["timestamp_ms"])
        
        # Save to disk
        self._save_annotations(self._current_file)
        
        # Record in undo manager
        if self._undo_manager:
            self._undo_manager.record_annotation_add(self._current_file, annotation)
        
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
        
        # Record old values for undo (only if values changed)
        uid = annotation.get("uid", -1)
        if self._undo_manager and uid >= 0:
            if annotation["timestamp_ms"] != timestamp_ms:
                self._undo_manager.record_annotation_edit(
                    self._current_file, uid, "timestamp_ms", 
                    annotation["timestamp_ms"], timestamp_ms
                )
            if annotation["text"] != text.strip():
                self._undo_manager.record_annotation_edit(
                    self._current_file, uid, "text",
                    annotation["text"], text.strip()
                )
            if annotation["category"] != category:
                self._undo_manager.record_annotation_edit(
                    self._current_file, uid, "category",
                    annotation["category"], category
                )
            if annotation["important"] != important:
                self._undo_manager.record_annotation_edit(
                    self._current_file, uid, "important",
                    annotation["important"], important
                )
            if annotation["color"] != color:
                self._undo_manager.record_annotation_edit(
                    self._current_file, uid, "color",
                    annotation["color"], color
                )
        
        # Apply updates
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
        
        # Save annotation before deleting (for undo)
        deleted_annotation = annotations[index].copy()
        
        # Delete annotation
        del annotations[index]
        
        # Save to disk
        self._save_annotations(self._current_file)
        
        # Record in undo manager
        if self._undo_manager:
            self._undo_manager.record_annotation_delete(self._current_file, deleted_annotation)
        
        # Emit signals
        self.annotationDeleted.emit(self._current_file, index)
        self.annotationsChanged.emit(self._current_file)
    
    def deleteAnnotationByUid(self, file_path: str, uid: int) -> bool:
        """
        Delete an annotation by UID (for undo system).
        
        Args:
            file_path: Path to the audio file
            uid: Unique identifier of the annotation
            
        Returns:
            True if annotation was found and deleted
        """
        if file_path not in self._annotations:
            return False
        
        annotations = self._annotations[file_path]
        for i, annotation in enumerate(annotations):
            if annotation.get('uid') == uid:
                del annotations[i]
                self._save_annotations(file_path)
                self.annotationsChanged.emit(file_path)
                return True
        return False
    
    def addAnnotationDirect(self, file_path: str, annotation: Dict[str, Any]) -> None:
        """
        Add an annotation directly (for undo system).
        This bypasses the normal addAnnotation flow and uses a pre-built annotation dict.
        
        Args:
            file_path: Path to the audio file
            annotation: Complete annotation dictionary
        """
        if file_path not in self._annotations:
            self._annotations[file_path] = []
        
        self._annotations[file_path].append(annotation.copy())
        self._annotations[file_path].sort(key=lambda a: a.get("timestamp_ms", 0))
        self._save_annotations(file_path)
        self.annotationsChanged.emit(file_path)
    
    def updateAnnotationField(self, file_path: str, uid: int, field: str, value: Any) -> bool:
        """
        Update a single field of an annotation (for undo system).
        
        Args:
            file_path: Path to the audio file
            uid: Unique identifier of the annotation
            field: Field name to update
            value: New value for the field
            
        Returns:
            True if annotation was found and updated
        """
        if file_path not in self._annotations:
            return False
        
        annotations = self._annotations[file_path]
        for annotation in annotations:
            if annotation.get('uid') == uid:
                annotation[field] = value
                annotation["updated_at"] = datetime.now().isoformat()
                
                # Re-sort if timestamp changed
                if field == "timestamp_ms":
                    annotations.sort(key=lambda a: a.get("timestamp_ms", 0))
                
                self._save_annotations(file_path)
                self.annotationsChanged.emit(file_path)
                return True
        return False
    
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
    
    # ========== Annotation Sets Management ==========
    
    def setCurrentDirectory(self, directory: Path) -> None:
        """
        Set the current directory and load annotation sets.
        
        Args:
            directory: Path to the current directory
        """
        self._current_directory = directory
        self._load_annotation_sets()
    
    @pyqtSlot(result=list)
    def getAnnotationSets(self) -> List[Dict[str, Any]]:
        """
        Get the list of all annotation sets.
        
        Returns:
            List of annotation set dictionaries with id, name, color, visible
        """
        # Return simplified version for QML
        return [
            {
                "id": aset["id"],
                "name": aset["name"],
                "color": aset["color"],
                "visible": aset.get("visible", True)
            }
            for aset in self._annotation_sets
        ]
    
    @pyqtSlot(result=str)
    def getCurrentSetId(self) -> str:
        """Get the current annotation set ID."""
        return self._current_set_id or ""
    
    @pyqtSlot(str)
    def setCurrentSetId(self, set_id: str) -> None:
        """
        Set the current annotation set.
        
        Args:
            set_id: ID of the annotation set to make current
        """
        if set_id != self._current_set_id:
            self._current_set_id = set_id
            self.currentSetChanged.emit(set_id)
            # Reload annotations for current file with new set context
            if self._current_file:
                self._load_annotations(self._current_file)
                self.annotationsChanged.emit(self._current_file)
    
    @pyqtSlot(result=bool)
    def getShowAllSets(self) -> bool:
        """Get whether to show annotations from all visible sets."""
        return self._show_all_sets
    
    @pyqtSlot(bool)
    def setShowAllSets(self, show_all: bool) -> None:
        """
        Set whether to show annotations from all visible sets (merged view).
        
        Args:
            show_all: True to show all visible sets, False to show only current set
        """
        if show_all != self._show_all_sets:
            self._show_all_sets = show_all
            self.showAllSetsChanged.emit(show_all)
            # Reload annotations to reflect merged view
            if self._current_file:
                self._load_annotations(self._current_file)
                self.annotationsChanged.emit(self._current_file)
    
    @pyqtSlot(str, str, result=str)
    def addAnnotationSet(self, name: str, color: str = "") -> str:
        """
        Create a new annotation set.
        
        Args:
            name: Name for the new set
            color: Color for the set (hex format), or empty to auto-assign
            
        Returns:
            ID of the newly created set
        """
        if not name.strip():
            name = self._get_default_set_name()
        
        if not color:
            color = self._get_color_for_set_name(name)
        
        set_id = uuid.uuid4().hex[:8]
        new_set = {
            "id": set_id,
            "name": name.strip(),
            "color": color,
            "visible": True,
            "files": {}  # Per-file annotations and metadata
        }
        
        self._annotation_sets.append(new_set)
        self._current_set_id = set_id
        
        # Save annotation sets
        self._save_annotation_sets()
        
        # Emit signals
        self.annotationSetsChanged.emit()
        self.currentSetChanged.emit(set_id)
        
        return set_id
    
    @pyqtSlot(str, str)
    def renameAnnotationSet(self, set_id: str, new_name: str) -> None:
        """
        Rename an annotation set.
        
        Args:
            set_id: ID of the set to rename
            new_name: New name for the set
        """
        for aset in self._annotation_sets:
            if aset["id"] == set_id:
                aset["name"] = new_name.strip()
                self._save_annotation_sets()
                self.annotationSetsChanged.emit()
                return
    
    @pyqtSlot(str, result=bool)
    def deleteAnnotationSet(self, set_id: str) -> bool:
        """
        Delete an annotation set.
        
        Args:
            set_id: ID of the set to delete
            
        Returns:
            True if deleted, False if cannot delete (e.g., last set)
        """
        if len(self._annotation_sets) <= 1:
            self.errorOccurred.emit("Cannot delete the last annotation set")
            return False
        
        # Remove the set
        self._annotation_sets = [s for s in self._annotation_sets if s["id"] != set_id]
        
        # If current set was deleted, switch to first set
        if self._current_set_id == set_id:
            self._current_set_id = self._annotation_sets[0]["id"]
            self.currentSetChanged.emit(self._current_set_id)
        
        # Save and notify
        self._save_annotation_sets()
        self.annotationSetsChanged.emit()
        
        return True
    
    @pyqtSlot(str, bool)
    def setAnnotationSetVisibility(self, set_id: str, visible: bool) -> None:
        """
        Set the visibility of an annotation set.
        
        Args:
            set_id: ID of the set
            visible: Whether the set should be visible
        """
        for aset in self._annotation_sets:
            if aset["id"] == set_id:
                aset["visible"] = visible
                self._save_annotation_sets()
                self.annotationSetsChanged.emit()
                # If in merged view, reload annotations
                if self._show_all_sets and self._current_file:
                    self._load_annotations(self._current_file)
                    self.annotationsChanged.emit(self._current_file)
                return
    
    def _get_default_set_name(self) -> str:
        """Get the default name for a new annotation set (based on username)."""
        return self._current_user
    
    def _get_color_for_set_name(self, name: str) -> str:
        """
        Get a consistent color for a set name.
        
        Args:
            name: Set name
            
        Returns:
            Color in hex format
        """
        # Use simple hash-based color assignment for consistency
        colors = [
            "#3498db",  # blue
            "#2ecc71",  # green
            "#e74c3c",  # red
            "#f39c12",  # orange
            "#9b59b6",  # purple
            "#1abc9c",  # teal
            "#e67e22",  # dark orange
        ]
        # Hash the name to get consistent color
        hash_val = sum(ord(c) for c in name)
        return colors[hash_val % len(colors)]
    
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
                    
                # Add UIDs to any annotations that don't have them
                for annotation in self._annotations[file_path]:
                    if 'uid' not in annotation:
                        annotation['uid'] = self._next_uid
                        self._next_uid += 1
                    else:
                        # Track max UID to avoid conflicts
                        if annotation['uid'] >= self._next_uid:
                            self._next_uid = annotation['uid'] + 1
                
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
    
    # ========== Annotation Sets Persistence ==========
    
    def _get_annotation_sets_file_path(self) -> Optional[Path]:
        """Get the path to the annotation sets file for current directory."""
        if not self._current_directory:
            return None
        # Use username-specific file for multi-user support
        return self._current_directory / f".{self._current_user}_notes.json"
    
    def _load_annotation_sets(self) -> None:
        """Load annotation sets from disk."""
        sets_file = self._get_annotation_sets_file_path()
        if not sets_file or not sets_file.exists():
            # Create default set if no file exists
            self._create_default_set()
            return
        
        try:
            with open(sets_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if it's the new multi-set format
            if isinstance(data, dict) and "annotation_sets" in data:
                self._annotation_sets = data["annotation_sets"]
                if not self._annotation_sets:
                    self._create_default_set()
                else:
                    # Set current set to saved one or first available
                    self._current_set_id = data.get("current_set_id")
                    if not self._current_set_id or not any(s["id"] == self._current_set_id for s in self._annotation_sets):
                        self._current_set_id = self._annotation_sets[0]["id"]
            else:
                # Legacy single-set format - convert to multi-set
                self._convert_legacy_to_multi_set(data)
        
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading annotation sets: {e}")
            self._create_default_set()
        
        self.annotationSetsChanged.emit()
        if self._current_set_id:
            self.currentSetChanged.emit(self._current_set_id)
    
    def _save_annotation_sets(self) -> None:
        """Save annotation sets to disk."""
        sets_file = self._get_annotation_sets_file_path()
        if not sets_file:
            return
        
        try:
            data = {
                "annotation_sets": self._annotation_sets,
                "current_set_id": self._current_set_id
            }
            
            with open(sets_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        except IOError as e:
            print(f"Error saving annotation sets: {e}")
            self.errorOccurred.emit(f"Failed to save annotation sets: {e}")
    
    def _create_default_set(self) -> None:
        """Create a default annotation set."""
        set_id = uuid.uuid4().hex[:8]
        set_name = self._get_default_set_name()
        color = self._get_color_for_set_name(set_name)
        
        default_set = {
            "id": set_id,
            "name": set_name,
            "color": color,
            "visible": True,
            "files": {}
        }
        
        self._annotation_sets = [default_set]
        self._current_set_id = set_id
        self._save_annotation_sets()
    
    def _convert_legacy_to_multi_set(self, legacy_data: Dict) -> None:
        """
        Convert legacy single-set annotation format to multi-set format.
        
        Args:
            legacy_data: Legacy annotation data
        """
        # Create a set from legacy data
        set_id = uuid.uuid4().hex[:8]
        set_name = self._get_default_set_name()
        color = self._get_color_for_set_name(set_name)
        
        new_set = {
            "id": set_id,
            "name": set_name,
            "color": color,
            "visible": True,
            "files": legacy_data.get("files", {}) if isinstance(legacy_data, dict) else {}
        }
        
        self._annotation_sets = [new_set]
        self._current_set_id = set_id
        self._save_annotation_sets()
