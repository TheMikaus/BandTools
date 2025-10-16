#!/usr/bin/env python3
"""
Section Manager Backend Module

Manages song sections (Verse, Chorus, Bridge, etc.) for audio files.
Provides CRUD operations, JSON persistence, and fingerprint-based auto-detection.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot


class SectionManager(QObject):
    """
    Manages sections for audio files.
    
    A section is a labeled part of a song (e.g., Verse, Chorus, Bridge)
    with a start time and end time. Sections can be used for:
    - Navigation within songs
    - Auto-detection using fingerprints
    - Practice and analysis
    
    Features:
    - Create, read, update, delete sections
    - JSON file-based storage (per audio file)
    - Auto-detection using fingerprint matching
    - Common section labels (Verse, Chorus, Bridge, etc.)
    """
    
    # Signals for state changes
    sectionsChanged = pyqtSignal(str)  # Emitted when sections change (file path)
    sectionAdded = pyqtSignal(str, dict)  # file path, section data
    sectionUpdated = pyqtSignal(str, int)  # file path, section index
    sectionDeleted = pyqtSignal(str, int)  # file path, section index
    currentFileChanged = pyqtSignal(str)  # Current file path
    errorOccurred = pyqtSignal(str)  # Error message
    
    # Common section labels
    COMMON_LABELS = [
        "Intro",
        "Verse",
        "Pre-Chorus",
        "Chorus",
        "Bridge",
        "Solo",
        "Interlude",
        "Outro",
        "Break",
    ]
    
    def __init__(self, parent=None):
        """Initialize the section manager."""
        super().__init__(parent)
        self._current_file: str = ""
        self._sections: Dict[str, List[Dict[str, Any]]] = {}  # filepath -> sections
        self._current_directory: Optional[Path] = None
        self._fingerprint_engine = None  # Will be set externally if available
        
    # ========== QML-accessible methods ==========
    
    @pyqtSlot(str)
    def setCurrentFile(self, file_path: str) -> None:
        """
        Set the current audio file for section management.
        
        Args:
            file_path: Path to the audio file
        """
        if file_path != self._current_file:
            self._current_file = file_path
            self.currentFileChanged.emit(file_path)
            
            # Load sections for this file if not already loaded
            if file_path and file_path not in self._sections:
                self._load_sections(file_path)
    
    @pyqtSlot(result=str)
    def getCurrentFile(self) -> str:
        """Get the current file path."""
        return self._current_file
    
    @pyqtSlot(int, int, str, str)
    def addSection(self, start_ms: int, end_ms: int, label: str, notes: str = "") -> None:
        """
        Add a new section to the current file.
        
        Args:
            start_ms: Start time in milliseconds
            end_ms: End time in milliseconds
            label: Section label (e.g., "Verse", "Chorus")
            notes: Optional notes about the section
        """
        if not self._current_file:
            self.errorOccurred.emit("No file selected")
            return
        
        if start_ms < 0 or end_ms <= start_ms:
            self.errorOccurred.emit("Invalid section times")
            return
        
        if not label.strip():
            self.errorOccurred.emit("Section label cannot be empty")
            return
        
        # Create section data
        section = {
            "start_ms": start_ms,
            "end_ms": end_ms,
            "label": label.strip(),
            "notes": notes.strip(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        
        # Add to sections list
        if self._current_file not in self._sections:
            self._sections[self._current_file] = []
        
        self._sections[self._current_file].append(section)
        
        # Sort by start time
        self._sections[self._current_file].sort(key=lambda s: s["start_ms"])
        
        # Save to disk
        self._save_sections(self._current_file)
        
        # Emit signals
        self.sectionAdded.emit(self._current_file, section)
        self.sectionsChanged.emit(self._current_file)
    
    @pyqtSlot(int, int, int, str, str)
    def updateSection(self, index: int, start_ms: int, end_ms: int, 
                      label: str, notes: str = "") -> None:
        """
        Update an existing section.
        
        Args:
            index: Index of the section to update
            start_ms: New start time in milliseconds
            end_ms: New end time in milliseconds
            label: New section label
            notes: New notes
        """
        if not self._current_file:
            self.errorOccurred.emit("No file selected")
            return
        
        if self._current_file not in self._sections:
            self.errorOccurred.emit("No sections for current file")
            return
        
        sections = self._sections[self._current_file]
        if not (0 <= index < len(sections)):
            self.errorOccurred.emit(f"Invalid section index: {index}")
            return
        
        if start_ms < 0 or end_ms <= start_ms:
            self.errorOccurred.emit("Invalid section times")
            return
        
        if not label.strip():
            self.errorOccurred.emit("Section label cannot be empty")
            return
        
        # Update section
        section = sections[index]
        section["start_ms"] = start_ms
        section["end_ms"] = end_ms
        section["label"] = label.strip()
        section["notes"] = notes.strip()
        section["updated_at"] = datetime.now().isoformat()
        
        # Re-sort by start time
        sections.sort(key=lambda s: s["start_ms"])
        
        # Save to disk
        self._save_sections(self._current_file)
        
        # Emit signals
        self.sectionUpdated.emit(self._current_file, index)
        self.sectionsChanged.emit(self._current_file)
    
    @pyqtSlot(int)
    def deleteSection(self, index: int) -> None:
        """
        Delete a section by index.
        
        Args:
            index: Index of the section to delete
        """
        if not self._current_file:
            self.errorOccurred.emit("No file selected")
            return
        
        if self._current_file not in self._sections:
            self.errorOccurred.emit("No sections for current file")
            return
        
        sections = self._sections[self._current_file]
        if not (0 <= index < len(sections)):
            self.errorOccurred.emit(f"Invalid section index: {index}")
            return
        
        # Delete section
        del sections[index]
        
        # Save to disk
        self._save_sections(self._current_file)
        
        # Emit signals
        self.sectionDeleted.emit(self._current_file, index)
        self.sectionsChanged.emit(self._current_file)
    
    @pyqtSlot(result=list)
    def getSections(self) -> List[Dict[str, Any]]:
        """
        Get all sections for the current file.
        
        Returns:
            List of section dictionaries
        """
        if not self._current_file:
            return []
        
        return self._sections.get(self._current_file, []).copy()
    
    @pyqtSlot(result=int)
    def getSectionCount(self) -> int:
        """
        Get the number of sections for the current file.
        
        Returns:
            Number of sections
        """
        if not self._current_file:
            return 0
        
        return len(self._sections.get(self._current_file, []))
    
    @pyqtSlot(int, result=dict)
    def getSectionAt(self, index: int) -> Dict[str, Any]:
        """
        Get a section by index.
        
        Args:
            index: Section index
            
        Returns:
            Section dictionary or empty dict if invalid index
        """
        if not self._current_file:
            return {}
        
        sections = self._sections.get(self._current_file, [])
        if 0 <= index < len(sections):
            return sections[index].copy()
        return {}
    
    @pyqtSlot(result=list)
    def getCommonLabels(self) -> List[str]:
        """
        Get the list of common section labels.
        
        Returns:
            List of common label strings
        """
        return self.COMMON_LABELS.copy()
    
    @pyqtSlot()
    def autoDetectSections(self) -> None:
        """
        Auto-detect sections using fingerprint matching.
        
        This will use the fingerprint engine to find similar sections
        across files and suggest section labels based on patterns.
        """
        if not self._current_file:
            self.errorOccurred.emit("No file selected")
            return
        
        if not self._fingerprint_engine:
            self.errorOccurred.emit("Fingerprint engine not available")
            return
        
        # TODO: Implement fingerprint-based auto-detection
        # This would:
        # 1. Generate fingerprints for different time segments
        # 2. Match against known sections in other files
        # 3. Suggest section labels based on matches
        self.errorOccurred.emit("Auto-detection not yet implemented")
    
    def setFingerprintEngine(self, engine) -> None:
        """
        Set the fingerprint engine for auto-detection.
        
        Args:
            engine: FingerprintEngine instance
        """
        self._fingerprint_engine = engine
    
    def setCurrentDirectory(self, directory: Path) -> None:
        """
        Set the current directory for section storage.
        
        Args:
            directory: Path to the directory
        """
        self._current_directory = directory
    
    # ========== Private methods ==========
    
    def _load_sections(self, file_path: str) -> None:
        """
        Load sections from JSON file.
        
        Args:
            file_path: Path to the audio file
        """
        try:
            audio_path = Path(file_path)
            # Sections are stored as .{filename}_sections.json
            sections_file = audio_path.parent / f".{audio_path.stem}_sections.json"
            
            if sections_file.exists():
                with open(sections_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._sections[file_path] = data.get("sections", [])
            else:
                self._sections[file_path] = []
        except Exception as e:
            self.errorOccurred.emit(f"Failed to load sections: {e}")
            self._sections[file_path] = []
    
    def _save_sections(self, file_path: str) -> None:
        """
        Save sections to JSON file.
        
        Args:
            file_path: Path to the audio file
        """
        try:
            audio_path = Path(file_path)
            sections_file = audio_path.parent / f".{audio_path.stem}_sections.json"
            
            data = {
                "file_path": str(audio_path),
                "sections": self._sections.get(file_path, [])
            }
            
            with open(sections_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.errorOccurred.emit(f"Failed to save sections: {e}")
