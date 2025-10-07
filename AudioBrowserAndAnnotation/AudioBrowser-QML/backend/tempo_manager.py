#!/usr/bin/env python3
"""
Tempo Manager Backend Module

Handles tempo/BPM tracking and persistence for audio files.
Stores tempo data in .tempo.json file per directory.
"""

import json
from pathlib import Path
from typing import Dict, Optional
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot


class TempoManager(QObject):
    """
    Manager for tempo/BPM tracking and persistence.
    
    Stores tempo information per audio file in a .tempo.json file
    in the current directory.
    """
    
    # Signals
    tempoDataChanged = pyqtSignal()  # Emitted when tempo data changes
    tempoForFileChanged = pyqtSignal(str, float)  # (filename, bpm)
    
    def __init__(self, parent=None):
        """Initialize the tempo manager."""
        super().__init__(parent)
        
        self._current_directory: Optional[Path] = None
        self._tempo_data: Dict[str, float] = {}  # {filename: bpm}
        self._tempo_json_filename = ".tempo.json"
    
    # ========== Directory Management ==========
    
    def setCurrentDirectory(self, directory: Path) -> None:
        """
        Set the current working directory and load tempo data.
        
        Args:
            directory: Path to the directory
        """
        if self._current_directory == directory:
            return
        
        self._current_directory = directory
        self._load_tempo_data()
        self.tempoDataChanged.emit()
    
    def getCurrentDirectory(self) -> Optional[Path]:
        """Get the current working directory."""
        return self._current_directory
    
    # ========== Tempo Data Access ==========
    
    @pyqtSlot(str, result=float)
    def getBPM(self, filename: str) -> float:
        """
        Get the BPM for a specific file.
        
        Args:
            filename: Name of the audio file
            
        Returns:
            BPM value, or 0 if not set
        """
        return self._tempo_data.get(filename, 0.0)
    
    @pyqtSlot(str, float)
    def setBPM(self, filename: str, bpm: float) -> None:
        """
        Set the BPM for a specific file.
        
        Args:
            filename: Name of the audio file
            bpm: BPM value (1-300 recommended range)
        """
        # Validate BPM range
        if bpm < 0:
            bpm = 0
        elif bpm > 300:
            bpm = 300
        
        # Update or remove tempo data
        if bpm == 0:
            # Remove tempo if set to 0
            if filename in self._tempo_data:
                del self._tempo_data[filename]
        else:
            # Set tempo
            self._tempo_data[filename] = bpm
        
        # Save and notify
        self._save_tempo_data()
        self.tempoForFileChanged.emit(filename, bpm)
        self.tempoDataChanged.emit()
    
    @pyqtSlot(str)
    def clearBPM(self, filename: str) -> None:
        """
        Clear the BPM for a specific file.
        
        Args:
            filename: Name of the audio file
        """
        if filename in self._tempo_data:
            del self._tempo_data[filename]
            self._save_tempo_data()
            self.tempoForFileChanged.emit(filename, 0)
            self.tempoDataChanged.emit()
    
    def getAllTempoData(self) -> Dict[str, float]:
        """
        Get all tempo data for the current directory.
        
        Returns:
            Dictionary mapping filenames to BPM values
        """
        return self._tempo_data.copy()
    
    # ========== Persistence ==========
    
    def _get_tempo_json_path(self) -> Optional[Path]:
        """Get the path to the .tempo.json file for the current directory."""
        if self._current_directory is None:
            return None
        return self._current_directory / self._tempo_json_filename
    
    def _load_tempo_data(self) -> None:
        """Load tempo data from .tempo.json file."""
        tempo_path = self._get_tempo_json_path()
        if tempo_path is None or not tempo_path.exists():
            self._tempo_data = {}
            return
        
        try:
            with open(tempo_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate data structure
            if isinstance(data, dict):
                # Convert all values to float
                self._tempo_data = {
                    str(k): float(v) 
                    for k, v in data.items() 
                    if isinstance(v, (int, float))
                }
            else:
                self._tempo_data = {}
                
        except (json.JSONDecodeError, IOError, ValueError) as e:
            # Handle corrupted or invalid JSON files
            print(f"Warning: Could not load tempo data from {tempo_path}: {e}")
            self._tempo_data = {}
    
    def _save_tempo_data(self) -> None:
        """Save tempo data to .tempo.json file."""
        tempo_path = self._get_tempo_json_path()
        if tempo_path is None:
            return
        
        try:
            with open(tempo_path, 'w', encoding='utf-8') as f:
                json.dump(self._tempo_data, f, indent=2)
        except IOError as e:
            print(f"Error: Could not save tempo data to {tempo_path}: {e}")
    
    # ========== Utility Methods ==========
    
    @pyqtSlot(result=int)
    def getFileCount(self) -> int:
        """Get the number of files with tempo data."""
        return len(self._tempo_data)
    
    @pyqtSlot()
    def clearAll(self) -> None:
        """Clear all tempo data for the current directory."""
        self._tempo_data = {}
        self._save_tempo_data()
        self.tempoDataChanged.emit()
