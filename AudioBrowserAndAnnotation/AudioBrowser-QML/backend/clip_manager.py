#!/usr/bin/env python3
"""
Clip Manager Module

Manages audio clips (regions) for audio files with CRUD operations, persistence,
and export functionality. Provides QML integration via signals and slots.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot


class ClipManager(QObject):
    """
    Manages audio clips for audio files.
    
    Provides CRUD operations, JSON persistence, clip export,
    and signals for QML integration.
    
    Features:
    - Create, read, update, delete clips
    - JSON file-based storage (per audio file)
    - Clip properties: start_time, end_time, name, notes
    - Export functionality to extract audio segments
    - Automatic timestamp tracking
    - Signal emissions for UI updates
    """
    
    # Signals for state changes
    clipsChanged = pyqtSignal(str)  # Emitted when clips change (file path)
    clipAdded = pyqtSignal(str, dict)  # file path, clip data
    clipUpdated = pyqtSignal(str, int)  # file path, clip index
    clipDeleted = pyqtSignal(str, int)  # file path, clip index
    currentFileChanged = pyqtSignal(str)  # Current file path
    errorOccurred = pyqtSignal(str)  # Error message
    exportProgress = pyqtSignal(int, int)  # current, total
    exportComplete = pyqtSignal(str)  # exported file path
    
    def __init__(self, parent=None):
        """Initialize the clip manager."""
        super().__init__(parent)
        self._current_file: str = ""
        self._clips: Dict[str, List[Dict[str, Any]]] = {}  # filepath -> clips
        
    # ========== QML-accessible methods ==========
    
    @pyqtSlot(str)
    def setCurrentFile(self, file_path: str) -> None:
        """
        Set the current audio file for clip management.
        
        Args:
            file_path: Path to the audio file
        """
        if file_path != self._current_file:
            self._current_file = file_path
            self.currentFileChanged.emit(file_path)
            
            # Load clips for this file if not already loaded
            if file_path and file_path not in self._clips:
                self._load_clips(file_path)
    
    @pyqtSlot(result=str)
    def getCurrentFile(self) -> str:
        """Get the current file path."""
        return self._current_file
    
    @pyqtSlot(int, int, str, str, result=bool)
    def addClip(self, start_ms: int, end_ms: int, name: str = "", notes: str = "") -> bool:
        """
        Add a new clip to the current file.
        
        Args:
            start_ms: Start timestamp in milliseconds
            end_ms: End timestamp in milliseconds
            name: Clip name
            notes: Optional notes
            
        Returns:
            True if successful, False otherwise
        """
        if not self._current_file:
            self.errorOccurred.emit("No file selected")
            return False
            
        if start_ms < 0 or end_ms < 0:
            self.errorOccurred.emit("Timestamps must be non-negative")
            return False
            
        if start_ms >= end_ms:
            self.errorOccurred.emit("Start time must be before end time")
            return False
        
        # Create clip data
        clip = {
            "start_ms": start_ms,
            "end_ms": end_ms,
            "duration_ms": end_ms - start_ms,
            "name": name,
            "notes": notes,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Add to clips list
        if self._current_file not in self._clips:
            self._clips[self._current_file] = []
        
        self._clips[self._current_file].append(clip)
        
        # Save to disk
        self._save_clips(self._current_file)
        
        # Emit signals
        self.clipAdded.emit(self._current_file, clip)
        self.clipsChanged.emit(self._current_file)
        
        return True
    
    @pyqtSlot(int, int, int, str, str, result=bool)
    def updateClip(self, index: int, start_ms: int, end_ms: int, 
                   name: str = "", notes: str = "") -> bool:
        """
        Update an existing clip.
        
        Args:
            index: Index of the clip to update
            start_ms: New start timestamp in milliseconds
            end_ms: New end timestamp in milliseconds
            name: New clip name
            notes: New notes
            
        Returns:
            True if successful, False otherwise
        """
        if not self._current_file:
            self.errorOccurred.emit("No file selected")
            return False
            
        if self._current_file not in self._clips:
            self.errorOccurred.emit("No clips for current file")
            return False
            
        clips = self._clips[self._current_file]
        if index < 0 or index >= len(clips):
            self.errorOccurred.emit(f"Invalid clip index: {index}")
            return False
        
        if start_ms < 0 or end_ms < 0:
            self.errorOccurred.emit("Timestamps must be non-negative")
            return False
            
        if start_ms >= end_ms:
            self.errorOccurred.emit("Start time must be before end time")
            return False
        
        # Update clip
        clips[index]["start_ms"] = start_ms
        clips[index]["end_ms"] = end_ms
        clips[index]["duration_ms"] = end_ms - start_ms
        clips[index]["name"] = name
        clips[index]["notes"] = notes
        clips[index]["updated_at"] = datetime.now().isoformat()
        
        # Save to disk
        self._save_clips(self._current_file)
        
        # Emit signals
        self.clipUpdated.emit(self._current_file, index)
        self.clipsChanged.emit(self._current_file)
        
        return True
    
    @pyqtSlot(int, result=bool)
    def deleteClip(self, index: int) -> bool:
        """
        Delete a clip by index.
        
        Args:
            index: Index of the clip to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self._current_file:
            self.errorOccurred.emit("No file selected")
            return False
            
        if self._current_file not in self._clips:
            self.errorOccurred.emit("No clips for current file")
            return False
            
        clips = self._clips[self._current_file]
        if index < 0 or index >= len(clips):
            self.errorOccurred.emit(f"Invalid clip index: {index}")
            return False
        
        # Remove clip
        del clips[index]
        
        # Save to disk
        self._save_clips(self._current_file)
        
        # Emit signals
        self.clipDeleted.emit(self._current_file, index)
        self.clipsChanged.emit(self._current_file)
        
        return True
    
    @pyqtSlot(result=bool)
    def clearClips(self) -> bool:
        """
        Clear all clips for the current file.
        
        Returns:
            True if successful, False otherwise
        """
        if not self._current_file:
            self.errorOccurred.emit("No file selected")
            return False
        
        if self._current_file in self._clips:
            self._clips[self._current_file] = []
            self._save_clips(self._current_file)
            self.clipsChanged.emit(self._current_file)
        
        return True
    
    @pyqtSlot(result=list)
    def getClips(self) -> List[Dict[str, Any]]:
        """
        Get all clips for the current file.
        
        Returns:
            List of clip dictionaries
        """
        if not self._current_file:
            return []
        
        return self._clips.get(self._current_file, [])
    
    @pyqtSlot(int, result='QVariantMap')
    def getClip(self, index: int) -> Dict[str, Any]:
        """
        Get a specific clip by index.
        
        Args:
            index: Clip index
            
        Returns:
            Clip dictionary or empty dict if not found
        """
        clips = self.getClips()
        if 0 <= index < len(clips):
            return clips[index]
        return {}
    
    @pyqtSlot(result=int)
    def getClipCount(self) -> int:
        """
        Get the number of clips for the current file.
        
        Returns:
            Number of clips
        """
        return len(self.getClips())
    
    @pyqtSlot(int, str, result=bool)
    def exportClip(self, index: int, output_path: str = "") -> bool:
        """
        Export a clip as a separate audio file.
        
        Args:
            index: Clip index to export
            output_path: Output file path (auto-generated if empty)
            
        Returns:
            True if successful, False otherwise
        """
        if not self._current_file:
            self.errorOccurred.emit("No file selected")
            return False
        
        clips = self.getClips()
        if index < 0 or index >= len(clips):
            self.errorOccurred.emit(f"Invalid clip index: {index}")
            return False
        
        clip = clips[index]
        
        try:
            # Import pydub for audio processing
            try:
                from pydub import AudioSegment
            except ImportError:
                self.errorOccurred.emit("pydub library required for clip export. Install with: pip install pydub")
                return False
            
            # Load audio file
            audio = AudioSegment.from_file(self._current_file)
            
            # Extract clip segment
            start_ms = clip["start_ms"]
            end_ms = clip["end_ms"]
            clip_segment = audio[start_ms:end_ms]
            
            # Generate output path if not provided
            if not output_path:
                source_path = Path(self._current_file)
                clip_name = clip.get("name", f"clip_{index+1}")
                # Sanitize clip name for filename
                safe_name = "".join(c for c in clip_name if c.isalnum() or c in (' ', '-', '_')).strip()
                if not safe_name:
                    safe_name = f"clip_{index+1}"
                output_path = str(source_path.parent / f"{source_path.stem}_{safe_name}{source_path.suffix}")
            
            # Export clip
            output_path_obj = Path(output_path)
            file_format = output_path_obj.suffix[1:].lower()  # Remove the dot
            
            # Map common extensions to pydub format names
            format_map = {
                'mp3': 'mp3',
                'wav': 'wav',
                'wave': 'wav',
                'ogg': 'ogg',
                'flac': 'flac'
            }
            
            export_format = format_map.get(file_format, 'wav')
            
            clip_segment.export(output_path, format=export_format)
            
            # Emit success signal
            self.exportComplete.emit(output_path)
            
            return True
            
        except Exception as e:
            self.errorOccurred.emit(f"Failed to export clip: {str(e)}")
            return False
    
    # ========== Private methods ==========
    
    def _get_clips_file_path(self, audio_file: str) -> Path:
        """
        Get the path to the clips JSON file for an audio file.
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            Path to the clips JSON file
        """
        audio_path = Path(audio_file)
        clips_filename = f".{audio_path.stem}_clips.json"
        return audio_path.parent / clips_filename
    
    def _load_clips(self, file_path: str) -> None:
        """
        Load clips from disk for a specific audio file.
        
        Args:
            file_path: Path to the audio file
        """
        clips_file = self._get_clips_file_path(file_path)
        
        if not clips_file.exists():
            self._clips[file_path] = []
            return
        
        try:
            with open(clips_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Validate data format
            if isinstance(data, list):
                self._clips[file_path] = data
            else:
                self._clips[file_path] = []
                self.errorOccurred.emit(f"Invalid clips file format: {clips_file}")
                
        except Exception as e:
            self._clips[file_path] = []
            self.errorOccurred.emit(f"Failed to load clips: {str(e)}")
    
    def _save_clips(self, file_path: str) -> None:
        """
        Save clips to disk for a specific audio file.
        
        Args:
            file_path: Path to the audio file
        """
        if file_path not in self._clips:
            return
        
        clips_file = self._get_clips_file_path(file_path)
        
        try:
            # Create parent directory if it doesn't exist
            clips_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write clips to file
            with open(clips_file, 'w', encoding='utf-8') as f:
                json.dump(self._clips[file_path], f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.errorOccurred.emit(f"Failed to save clips: {str(e)}")
