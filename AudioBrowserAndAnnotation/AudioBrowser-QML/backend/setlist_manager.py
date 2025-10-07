"""
Setlist Manager for AudioBrowser QML

Manages setlist creation, editing, and organization for performance preparation.
Setlists are stored in `.setlists.json` in the root practice folder.

Author: AI-assisted development
Date: January 2025
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot


class SetlistManager(QObject):
    """
    Manages setlists for organizing songs for performances.
    
    Features:
    - Create, rename, and delete setlists
    - Add/remove songs to/from setlists
    - Reorder songs in setlist
    - Track setlist metadata (name, creation date, notes)
    - Validate setlists (missing files, no best takes)
    - Export setlists to text files
    - Persist data to .setlists.json
    
    Signals:
    - setlistsChanged: Emitted when setlists are modified
    - currentSetlistChanged: Emitted when current setlist selection changes
    """
    
    # Signals
    setlistsChanged = pyqtSignal()
    currentSetlistChanged = pyqtSignal(str)  # setlist_id
    
    def __init__(self, root_path: Path):
        """
        Initialize the setlist manager.
        
        Args:
            root_path: Path to root practice folder
        """
        super().__init__()
        self.root_path = root_path
        self.setlists: Dict[str, Dict[str, Any]] = {}
        self.current_setlist_id: Optional[str] = None
        self._load_setlists()
    
    def _setlists_json_path(self) -> Path:
        """Return path to setlists JSON file."""
        return self.root_path / ".setlists.json"
    
    def _load_setlists(self):
        """
        Load setlists from JSON file.
        
        Structure:
        {
            "setlist_uuid": {
                "name": "Summer Tour 2024",
                "songs": [
                    {"folder": "practice_2024_01_01", "filename": "01_MySong.mp3"},
                    {"folder": "practice_2024_01_15", "filename": "02_Another.mp3"}
                ],
                "notes": "Performance notes here",
                "created_date": "2025-01-15T12:00:00",
                "last_modified": "2025-01-20T15:30:00"
            }
        }
        """
        json_path = self._setlists_json_path()
        if json_path.exists():
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    self.setlists = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading setlists: {e}")
                self.setlists = {}
        else:
            self.setlists = {}
    
    def _save_setlists(self):
        """Save setlists to JSON file."""
        json_path = self._setlists_json_path()
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(self.setlists, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving setlists: {e}")
    
    @pyqtSlot(result=str)
    def getAllSetlistsJson(self) -> str:
        """
        Get all setlists as JSON string for QML.
        
        Returns:
            JSON string of all setlists with format:
            [{"id": "uuid", "name": "Name", "songCount": 5}, ...]
        """
        setlists_list = []
        for setlist_id, setlist_data in self.setlists.items():
            setlists_list.append({
                "id": setlist_id,
                "name": setlist_data.get("name", "Unnamed Setlist"),
                "songCount": len(setlist_data.get("songs", [])),
                "created": setlist_data.get("created_date", ""),
                "modified": setlist_data.get("last_modified", "")
            })
        return json.dumps(setlists_list)
    
    @pyqtSlot(str, result=str)
    def getSetlistDetails(self, setlist_id: str) -> str:
        """
        Get details of a specific setlist as JSON.
        
        Args:
            setlist_id: UUID of the setlist
            
        Returns:
            JSON string with setlist details including songs
        """
        setlist = self.setlists.get(setlist_id)
        if not setlist:
            return json.dumps({"error": "Setlist not found"})
        
        # Get song details
        songs_details = self._get_setlist_songs_details(setlist_id)
        
        result = {
            "id": setlist_id,
            "name": setlist.get("name", "Unnamed Setlist"),
            "notes": setlist.get("notes", ""),
            "songs": songs_details,
            "created": setlist.get("created_date", ""),
            "modified": setlist.get("last_modified", "")
        }
        
        return json.dumps(result)
    
    def _get_setlist_songs_details(self, setlist_id: str) -> List[Dict[str, Any]]:
        """
        Get detailed information about songs in a setlist.
        
        Returns list of dicts with:
        - folder: practice folder name
        - filename: audio filename
        - provided_name: song name from metadata
        - duration_ms: song duration in milliseconds
        - duration_sec: song duration in seconds
        - is_best_take: whether file is marked as best take
        - exists: whether the file still exists
        """
        setlist = self.setlists.get(setlist_id)
        if not setlist:
            return []
        
        songs_details = []
        for song_entry in setlist.get("songs", []):
            folder = song_entry.get("folder", "")
            filename = song_entry.get("filename", "")
            
            # Check if file exists
            folder_path = self.root_path / folder
            file_path = folder_path / filename
            exists = file_path.exists()
            
            # Load provided name from that folder
            provided_name = filename
            if exists:
                names_path = folder_path / ".names.json"
                if names_path.exists():
                    try:
                        with open(names_path, 'r', encoding='utf-8') as f:
                            names_data = json.load(f)
                            provided_name = names_data.get(filename, filename)
                    except (json.JSONDecodeError, IOError):
                        pass
            
            # Get duration
            duration_ms = 0
            if exists:
                duration_path = folder_path / ".durations.json"
                if duration_path.exists():
                    try:
                        with open(duration_path, 'r', encoding='utf-8') as f:
                            duration_data = json.load(f)
                            duration_ms = duration_data.get(filename, 0)
                    except (json.JSONDecodeError, IOError):
                        pass
            
            # Check if best take
            is_best_take = False
            if exists:
                takes_path = folder_path / ".takes_metadata.json"
                if takes_path.exists():
                    try:
                        with open(takes_path, 'r', encoding='utf-8') as f:
                            takes_data = json.load(f)
                            file_takes = takes_data.get(filename, {})
                            is_best_take = file_takes.get("is_best_take", False)
                    except (json.JSONDecodeError, IOError):
                        pass
            
            songs_details.append({
                "folder": folder,
                "filename": filename,
                "provided_name": provided_name,
                "duration_ms": duration_ms,
                "duration_sec": duration_ms // 1000 if duration_ms > 0 else 0,
                "is_best_take": is_best_take,
                "exists": exists
            })
        
        return songs_details
    
    @pyqtSlot(str, result=bool)
    def createSetlist(self, name: str) -> bool:
        """
        Create a new setlist.
        
        Args:
            name: Name of the setlist
            
        Returns:
            True if successful, False otherwise
        """
        if not name or not name.strip():
            return False
        
        setlist_id = str(uuid.uuid4())
        self.setlists[setlist_id] = {
            "name": name.strip(),
            "songs": [],
            "notes": "",
            "created_date": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat()
        }
        
        self._save_setlists()
        self.setlistsChanged.emit()
        return True
    
    @pyqtSlot(str, str, result=bool)
    def renameSetlist(self, setlist_id: str, new_name: str) -> bool:
        """
        Rename a setlist.
        
        Args:
            setlist_id: UUID of the setlist
            new_name: New name for the setlist
            
        Returns:
            True if successful, False otherwise
        """
        if not new_name or not new_name.strip():
            return False
        
        setlist = self.setlists.get(setlist_id)
        if not setlist:
            return False
        
        setlist["name"] = new_name.strip()
        setlist["last_modified"] = datetime.now().isoformat()
        
        self._save_setlists()
        self.setlistsChanged.emit()
        return True
    
    @pyqtSlot(str, result=bool)
    def deleteSetlist(self, setlist_id: str) -> bool:
        """
        Delete a setlist.
        
        Args:
            setlist_id: UUID of the setlist
            
        Returns:
            True if successful, False otherwise
        """
        if setlist_id not in self.setlists:
            return False
        
        del self.setlists[setlist_id]
        
        if self.current_setlist_id == setlist_id:
            self.current_setlist_id = None
            self.currentSetlistChanged.emit("")
        
        self._save_setlists()
        self.setlistsChanged.emit()
        return True
    
    @pyqtSlot(str, str, str, result=bool)
    def addSong(self, setlist_id: str, folder: str, filename: str) -> bool:
        """
        Add a song to a setlist.
        
        Args:
            setlist_id: UUID of the setlist
            folder: Practice folder name
            filename: Audio filename
            
        Returns:
            True if successful, False otherwise
        """
        setlist = self.setlists.get(setlist_id)
        if not setlist:
            return False
        
        # Check if song already exists in setlist
        for song in setlist.get("songs", []):
            if song["folder"] == folder and song["filename"] == filename:
                return False  # Duplicate
        
        # Add song
        setlist["songs"].append({
            "folder": folder,
            "filename": filename
        })
        setlist["last_modified"] = datetime.now().isoformat()
        
        self._save_setlists()
        self.setlistsChanged.emit()
        return True
    
    @pyqtSlot(str, int, result=bool)
    def removeSong(self, setlist_id: str, song_index: int) -> bool:
        """
        Remove a song from a setlist.
        
        Args:
            setlist_id: UUID of the setlist
            song_index: Index of the song in the setlist
            
        Returns:
            True if successful, False otherwise
        """
        setlist = self.setlists.get(setlist_id)
        if not setlist:
            return False
        
        songs = setlist.get("songs", [])
        if song_index < 0 or song_index >= len(songs):
            return False
        
        songs.pop(song_index)
        setlist["last_modified"] = datetime.now().isoformat()
        
        self._save_setlists()
        self.setlistsChanged.emit()
        return True
    
    @pyqtSlot(str, int, int, result=bool)
    def moveSong(self, setlist_id: str, from_index: int, to_index: int) -> bool:
        """
        Move a song within a setlist.
        
        Args:
            setlist_id: UUID of the setlist
            from_index: Current index of the song
            to_index: Target index for the song
            
        Returns:
            True if successful, False otherwise
        """
        setlist = self.setlists.get(setlist_id)
        if not setlist:
            return False
        
        songs = setlist.get("songs", [])
        if from_index < 0 or from_index >= len(songs):
            return False
        if to_index < 0 or to_index >= len(songs):
            return False
        
        # Move song
        song = songs.pop(from_index)
        songs.insert(to_index, song)
        setlist["last_modified"] = datetime.now().isoformat()
        
        self._save_setlists()
        self.setlistsChanged.emit()
        return True
    
    @pyqtSlot(str, str, result=bool)
    def updateNotes(self, setlist_id: str, notes: str) -> bool:
        """
        Update performance notes for a setlist.
        
        Args:
            setlist_id: UUID of the setlist
            notes: Performance notes text
            
        Returns:
            True if successful, False otherwise
        """
        setlist = self.setlists.get(setlist_id)
        if not setlist:
            return False
        
        setlist["notes"] = notes
        setlist["last_modified"] = datetime.now().isoformat()
        
        self._save_setlists()
        return True
    
    @pyqtSlot(str, result=str)
    def validateSetlist(self, setlist_id: str) -> str:
        """
        Validate a setlist for missing files and other issues.
        
        Args:
            setlist_id: UUID of the setlist
            
        Returns:
            JSON string with validation results
        """
        setlist = self.setlists.get(setlist_id)
        if not setlist:
            return json.dumps({"error": "Setlist not found"})
        
        songs_details = self._get_setlist_songs_details(setlist_id)
        
        missing_files = []
        no_best_takes = []
        total_duration = 0
        
        for i, song in enumerate(songs_details):
            if not song["exists"]:
                missing_files.append({
                    "index": i + 1,
                    "name": song["provided_name"],
                    "folder": song["folder"],
                    "filename": song["filename"]
                })
            
            if song["exists"] and not song["is_best_take"]:
                no_best_takes.append({
                    "index": i + 1,
                    "name": song["provided_name"]
                })
            
            if song["exists"]:
                total_duration += song["duration_sec"]
        
        result = {
            "valid": len(missing_files) == 0,
            "total_songs": len(songs_details),
            "missing_files": missing_files,
            "no_best_takes": no_best_takes,
            "total_duration_sec": total_duration,
            "total_duration_formatted": self._format_duration(total_duration)
        }
        
        return json.dumps(result)
    
    @pyqtSlot(str, str, result=bool)
    def exportToText(self, setlist_id: str, output_path: str) -> bool:
        """
        Export a setlist to a text file.
        
        Args:
            setlist_id: UUID of the setlist
            output_path: Path to save the text file
            
        Returns:
            True if successful, False otherwise
        """
        setlist = self.setlists.get(setlist_id)
        if not setlist:
            return False
        
        songs_details = self._get_setlist_songs_details(setlist_id)
        
        # Generate text content
        lines = []
        lines.append("=" * 70)
        lines.append(f"SETLIST: {setlist.get('name', 'Unnamed')}")
        lines.append("=" * 70)
        lines.append("")
        
        if setlist.get("notes"):
            lines.append("PERFORMANCE NOTES:")
            lines.append(setlist["notes"])
            lines.append("")
            lines.append("-" * 70)
            lines.append("")
        
        total_duration = 0
        for i, song in enumerate(songs_details):
            lines.append(f"{i + 1}. {song['provided_name']}")
            
            details = []
            if song["is_best_take"]:
                details.append("✓ Best Take")
            if song["duration_sec"] > 0:
                details.append(self._format_duration(song["duration_sec"]))
                total_duration += song["duration_sec"]
            details.append(f"[{song['folder']}]")
            
            if not song["exists"]:
                details.append("⚠ MISSING FILE")
            
            lines.append(f"   {' | '.join(details)}")
            lines.append("")
        
        lines.append("-" * 70)
        lines.append(f"Total Songs: {len(songs_details)}")
        lines.append(f"Total Duration: {self._format_duration(total_duration)}")
        lines.append("")
        lines.append(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 70)
        
        # Write to file
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            return True
        except IOError as e:
            print(f"Error exporting setlist: {e}")
            return False
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration in seconds as MM:SS or HH:MM:SS."""
        if seconds < 0:
            return "0:00"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
