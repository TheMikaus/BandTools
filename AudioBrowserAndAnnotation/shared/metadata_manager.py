"""
Metadata Manager

Common metadata management functionality used across AudioBrowser applications.
Handles loading, saving, and backing up annotation data and other metadata.
"""

import json
import getpass
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .metadata_constants import NOTES_JSON
from . import backup_utils


class MetadataManager:
    """
    Manages metadata file operations for AudioBrowser applications.
    
    Provides centralized handling of:
    - Annotation file path resolution
    - Loading/saving annotation data
    - Automatic backup before modifications
    - JSON file I/O with error handling
    """
    
    def __init__(self, username: Optional[str] = None):
        """
        Initialize the metadata manager.
        
        Args:
            username: Username for user-specific metadata files. 
                     If None, uses system username.
        """
        self._username = username or getpass.getuser()
        self._backup_enabled = True
    
    def set_username(self, username: str) -> None:
        """Set the username for user-specific metadata files."""
        self._username = username or getpass.getuser()
    
    def get_username(self) -> str:
        """Get the current username."""
        return self._username
    
    def set_backup_enabled(self, enabled: bool) -> None:
        """Enable or disable automatic backups before saves."""
        self._backup_enabled = enabled
    
    def get_annotation_file_path(self, audio_file_path: Path) -> Path:
        """
        Get the path to the annotation file for a given audio file.
        
        This is for legacy per-file annotations (deprecated in favor of sets).
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Path to the annotation JSON file
        """
        annotation_file = audio_file_path.parent / f".{audio_file_path.stem}_annotations.json"
        return annotation_file
    
    def get_annotation_sets_file_path(self, directory: Path, username: Optional[str] = None) -> Path:
        """
        Get the path to the annotation sets file for a directory.
        
        Uses username-specific file for multi-user support.
        Format: .audio_notes_{username}.json
        
        Args:
            directory: Directory containing the audio files
            username: Username for the annotation set. If None, uses manager's username.
            
        Returns:
            Path to the annotation sets JSON file
        """
        user = username or self._username
        return directory / f".audio_notes_{user}.json"
    
    def load_json(self, path: Path, default: Any = None) -> Any:
        """
        Load JSON data from a file.
        
        Args:
            path: Path to the JSON file
            default: Default value to return if file doesn't exist or fails to load
            
        Returns:
            Loaded JSON data or default value
        """
        try:
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load {path}: {e}")
        return default
    
    def save_json(self, path: Path, data: Any, create_backup: bool = True) -> bool:
        """
        Save JSON data to a file.
        
        Args:
            path: Path to the JSON file
            data: Data to serialize as JSON
            create_backup: Whether to create a backup before saving
            
        Returns:
            True if save was successful, False otherwise
        """
        try:
            # Create backup if enabled and file exists
            if create_backup and self._backup_enabled and path.exists():
                practice_folder = path.parent
                if backup_utils.should_create_backup(practice_folder):
                    backup_utils.create_metadata_backup_if_needed(practice_folder)
            
            # Create parent directory if it doesn't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save JSON data
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except (IOError, TypeError) as e:
            print(f"Error: Failed to save {path}: {e}")
            return False
    
    def load_annotation_sets(self, directory: Path, username: Optional[str] = None) -> Dict[str, Any]:
        """
        Load annotation sets from disk.
        
        Args:
            directory: Directory containing the annotation sets file
            username: Username for the annotation set. If None, uses manager's username.
            
        Returns:
            Dictionary with keys:
                - 'version': int - Data format version
                - 'sets': list - List of annotation set dictionaries
                - 'current_set_id': str - ID of the currently active set
                - 'updated': str - ISO timestamp of last update
        """
        sets_file = self.get_annotation_sets_file_path(directory, username)
        data = self.load_json(sets_file, {})
        
        # Ensure data has expected structure
        if not isinstance(data, dict):
            return self._create_default_annotation_sets_data()
        
        # Check if this is the new multi-set format
        if "sets" in data:
            return data
        
        # Legacy format or empty - return default structure
        return self._create_default_annotation_sets_data()
    
    def save_annotation_sets(self, directory: Path, sets_data: Dict[str, Any], 
                            username: Optional[str] = None, create_backup: bool = True) -> bool:
        """
        Save annotation sets to disk.
        
        Args:
            directory: Directory to save the annotation sets file
            sets_data: Dictionary containing annotation sets data with keys:
                      'version', 'sets', 'current_set_id', 'updated'
            username: Username for the annotation set. If None, uses manager's username.
            create_backup: Whether to create a backup before saving
            
        Returns:
            True if save was successful, False otherwise
        """
        sets_file = self.get_annotation_sets_file_path(directory, username)
        
        # Ensure updated timestamp is current
        sets_data = sets_data.copy()
        sets_data["updated"] = datetime.now().isoformat(timespec="seconds")
        
        return self.save_json(sets_file, sets_data, create_backup=create_backup)
    
    def load_legacy_annotations(self, audio_file_path: Path) -> List[Dict[str, Any]]:
        """
        Load legacy per-file annotations (deprecated format).
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            List of annotation dictionaries
        """
        annotation_file = self.get_annotation_file_path(audio_file_path)
        data = self.load_json(annotation_file, [])
        
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # Multi-user format: {"users": {"user1": [...], "user2": [...]}}
            all_annotations = []
            if "users" in data:
                for user, user_annotations in data["users"].items():
                    for annotation in user_annotations:
                        annotation["user"] = user
                        all_annotations.append(annotation)
            elif "annotations" in data:
                all_annotations = data["annotations"]
            return all_annotations
        
        return []
    
    def save_legacy_annotations(self, audio_file_path: Path, annotations: List[Dict[str, Any]], 
                               create_backup: bool = True) -> bool:
        """
        Save legacy per-file annotations (deprecated format).
        
        Args:
            audio_file_path: Path to the audio file
            annotations: List of annotation dictionaries
            create_backup: Whether to create a backup before saving
            
        Returns:
            True if save was successful, False otherwise
        """
        annotation_file = self.get_annotation_file_path(audio_file_path)
        return self.save_json(annotation_file, annotations, create_backup=create_backup)
    
    def migrate_legacy_to_sets(self, directory: Path, username: Optional[str] = None) -> bool:
        """
        Migrate legacy single-set annotation data to multi-set format.
        
        Args:
            directory: Directory containing the legacy .audio_notes.json file
            username: Username for the new annotation set. If None, uses manager's username.
            
        Returns:
            True if migration was successful or unnecessary, False on error
        """
        user = username or self._username
        legacy_path = directory / NOTES_JSON
        new_path = self.get_annotation_sets_file_path(directory, user)
        
        # If new file already exists, no migration needed
        if new_path.exists():
            return True
        
        # If no legacy file exists, create default
        if not legacy_path.exists():
            sets_data = self._create_default_annotation_sets_data()
            return self.save_annotation_sets(directory, sets_data, user, create_backup=False)
        
        # Load legacy data
        legacy_data = self.load_json(legacy_path, {})
        if not legacy_data:
            return True
        
        # Convert to multi-set format
        sets_data = self._convert_legacy_to_multi_set(legacy_data, user)
        
        # Save as new format
        return self.save_annotation_sets(directory, sets_data, user, create_backup=False)
    
    def _create_default_annotation_sets_data(self, username: Optional[str] = None) -> Dict[str, Any]:
        """
        Create default annotation sets data structure.
        
        Args:
            username: Username for the default set. If None, uses manager's username.
            
        Returns:
            Dictionary with default annotation sets structure
        """
        user = username or self._username
        set_id = uuid.uuid4().hex[:8]
        
        default_set = {
            "id": set_id,
            "name": user,
            "color": "#00cc66",
            "visible": True,
            "folder_notes": "",
            "files": {}
        }
        
        return {
            "version": 3,
            "updated": datetime.now().isoformat(timespec="seconds"),
            "sets": [default_set],
            "current_set_id": set_id
        }
    
    def _convert_legacy_to_multi_set(self, legacy_data: Dict[str, Any], 
                                    username: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert legacy single-set data to multi-set format.
        
        Args:
            legacy_data: Legacy annotation data dictionary
            username: Username for the converted set. If None, uses manager's username.
            
        Returns:
            Dictionary with multi-set structure
        """
        user = username or self._username
        set_id = uuid.uuid4().hex[:8]
        
        # Extract legacy data
        folder_notes = str(legacy_data.get("folder_notes", "") or "")
        files = {}
        
        if "files" in legacy_data:
            for fname, meta in legacy_data.get("files", {}).items():
                if not isinstance(meta, dict):
                    continue
                
                files[str(fname)] = {
                    "general": str(meta.get("general", "") or ""),
                    "best_take": bool(meta.get("best_take", False)),
                    "partial_take": bool(meta.get("partial_take", False)),
                    "reference_song": bool(meta.get("reference_song", False)),
                    "notes": [
                        {
                            "uid": int(n.get("uid", 0) or 0),
                            "ms": int(n.get("ms", 0)),
                            "text": str(n.get("text", "")),
                            "important": bool(n.get("important", False)),
                            **({"end_ms": int(n["end_ms"])} if n.get("end_ms") is not None else {}),
                            **({"subsection": bool(n["subsection"])} if n.get("subsection") else {}),
                            **({"subsection_note": str(n["subsection_note"])} if n.get("subsection_note") else {})
                        }
                        for n in (meta.get("notes", []) or [])
                        if isinstance(n, dict)
                    ]
                }
        
        converted_set = {
            "id": set_id,
            "name": user,
            "color": "#00cc66",
            "visible": True,
            "folder_notes": folder_notes,
            "files": files
        }
        
        return {
            "version": 3,
            "updated": datetime.now().isoformat(timespec="seconds"),
            "sets": [converted_set],
            "current_set_id": set_id
        }
    
    def discover_annotation_files(self, directory: Path) -> List[Tuple[str, Path]]:
        """
        Discover all annotation files in a directory.
        
        Returns both user-specific (.audio_notes_{username}.json) and
        legacy (.audio_notes.json) annotation files.
        
        Args:
            directory: Directory to scan for annotation files
            
        Returns:
            List of tuples (username, file_path) for each annotation file found
        """
        annotation_files = []
        
        # Check for legacy file
        legacy_path = directory / NOTES_JSON
        if legacy_path.exists():
            annotation_files.append(("legacy", legacy_path))
        
        # Check for user-specific files
        for json_file in directory.glob(".audio_notes_*.json"):
            # Extract username from filename
            filename = json_file.name
            if filename.startswith(".audio_notes_") and filename.endswith(".json"):
                # Remove ".audio_notes_" prefix and ".json" suffix
                username = filename[13:-5]
                annotation_files.append((username, json_file))
        
        return annotation_files
    
    def get_annotation_count(self, directory: Path, username: Optional[str] = None) -> int:
        """
        Get the total number of annotations in a directory.
        
        Args:
            directory: Directory containing annotation files
            username: Username to count annotations for. If None, counts all users.
            
        Returns:
            Total number of annotations
        """
        count = 0
        
        if username:
            # Count for specific user
            sets_data = self.load_annotation_sets(directory, username)
            for aset in sets_data.get("sets", []):
                for file_data in aset.get("files", {}).values():
                    count += len(file_data.get("notes", []))
        else:
            # Count for all users
            annotation_files = self.discover_annotation_files(directory)
            for user, file_path in annotation_files:
                data = self.load_json(file_path, {})
                if isinstance(data, dict) and "sets" in data:
                    for aset in data.get("sets", []):
                        for file_data in aset.get("files", {}).values():
                            count += len(file_data.get("notes", []))
        
        return count
