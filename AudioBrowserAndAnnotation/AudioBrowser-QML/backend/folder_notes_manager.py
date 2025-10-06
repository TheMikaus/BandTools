"""
FolderNotesManager - Backend module for folder-level notes management

This module provides functionality to create, read, update, and delete notes
associated with audio folders. Notes are stored as JSON files in each directory.

Author: AudioBrowser QML Development Team
Date: December 2024
"""

from pathlib import Path
from typing import Optional
import json
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot


class FolderNotesManager(QObject):
    """
    Manager class for folder-level notes.
    
    Stores notes as .folder_notes.json in each directory.
    Provides CRUD operations and auto-save support.
    
    Signals:
        notesChanged: Emitted when notes content changes
        notesSaved: Emitted when notes are saved to disk
        notesLoaded: Emitted when notes are loaded from disk
        error: Emitted when an error occurs (with error message)
    """
    
    # Signals
    notesChanged = pyqtSignal(str)  # New notes content
    notesSaved = pyqtSignal(str)    # Path where notes were saved
    notesLoaded = pyqtSignal(str)   # Notes content loaded
    error = pyqtSignal(str)         # Error message
    
    # Constants
    NOTES_FILENAME = ".folder_notes.json"
    
    def __init__(self, parent=None):
        """Initialize the FolderNotesManager."""
        super().__init__(parent)
        self._current_folder: Optional[Path] = None
        self._current_notes: str = ""
        self._auto_save_enabled: bool = True
        self._modified: bool = False
    
    # ========== Properties ==========
    
    @pyqtSlot(result=str)
    def getCurrentNotes(self) -> str:
        """
        Get the current notes content.
        
        Returns:
            Current notes as string
        """
        return self._current_notes
    
    @pyqtSlot(result=str)
    def getCurrentFolder(self) -> str:
        """
        Get the current folder path.
        
        Returns:
            Current folder path as string, or empty string if none
        """
        return str(self._current_folder) if self._current_folder else ""
    
    @pyqtSlot(result=bool)
    def isModified(self) -> bool:
        """
        Check if notes have been modified since last save.
        
        Returns:
            True if modified, False otherwise
        """
        return self._modified
    
    @pyqtSlot(result=bool)
    def getAutoSaveEnabled(self) -> bool:
        """
        Check if auto-save is enabled.
        
        Returns:
            True if auto-save is enabled, False otherwise
        """
        return self._auto_save_enabled
    
    # ========== Settings ==========
    
    @pyqtSlot(bool)
    def setAutoSaveEnabled(self, enabled: bool):
        """
        Enable or disable auto-save functionality.
        
        Args:
            enabled: True to enable auto-save, False to disable
        """
        self._auto_save_enabled = enabled
    
    # ========== Core Operations ==========
    
    @pyqtSlot(str)
    def loadNotesForFolder(self, folder_path: str):
        """
        Load notes for a specific folder.
        
        Args:
            folder_path: Path to the folder
        """
        try:
            # Save current notes if modified
            if self._modified and self._current_folder:
                self.saveNotes()
            
            # Set new folder
            self._current_folder = Path(folder_path) if folder_path else None
            
            if not self._current_folder or not self._current_folder.exists():
                self._current_notes = ""
                self._modified = False
                self.notesLoaded.emit("")
                return
            
            # Load notes from file
            notes_file = self._current_folder / self.NOTES_FILENAME
            
            if notes_file.exists():
                try:
                    with open(notes_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self._current_notes = data.get('notes', '')
                except (json.JSONDecodeError, IOError) as e:
                    self.error.emit(f"Error loading notes: {str(e)}")
                    self._current_notes = ""
            else:
                self._current_notes = ""
            
            self._modified = False
            self.notesLoaded.emit(self._current_notes)
            
        except Exception as e:
            self.error.emit(f"Error loading folder notes: {str(e)}")
            self._current_notes = ""
            self._modified = False
    
    @pyqtSlot(str)
    def updateNotes(self, notes: str):
        """
        Update the notes content (in memory).
        
        Args:
            notes: New notes content
        """
        if notes != self._current_notes:
            self._current_notes = notes
            self._modified = True
            self.notesChanged.emit(notes)
            
            # Auto-save if enabled
            if self._auto_save_enabled and self._current_folder:
                self.saveNotes()
    
    @pyqtSlot()
    def saveNotes(self):
        """
        Save the current notes to disk.
        """
        if not self._current_folder:
            self.error.emit("No folder selected")
            return
        
        try:
            notes_file = self._current_folder / self.NOTES_FILENAME
            
            # Create data structure
            data = {
                'notes': self._current_notes,
                'folder': str(self._current_folder)
            }
            
            # Save to file
            with open(notes_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self._modified = False
            self.notesSaved.emit(str(notes_file))
            
        except IOError as e:
            self.error.emit(f"Error saving notes: {str(e)}")
    
    @pyqtSlot()
    def clearNotes(self):
        """
        Clear the current notes (in memory and on disk).
        """
        if not self._current_folder:
            return
        
        self._current_notes = ""
        self._modified = True
        self.notesChanged.emit("")
        
        # Save empty notes
        self.saveNotes()
    
    @pyqtSlot()
    def deleteNotesFile(self):
        """
        Delete the notes file from disk.
        """
        if not self._current_folder:
            self.error.emit("No folder selected")
            return
        
        try:
            notes_file = self._current_folder / self.NOTES_FILENAME
            
            if notes_file.exists():
                notes_file.unlink()
                self._current_notes = ""
                self._modified = False
                self.notesChanged.emit("")
                
        except IOError as e:
            self.error.emit(f"Error deleting notes file: {str(e)}")
    
    # ========== Utility Methods ==========
    
    @pyqtSlot(str, result=bool)
    def folderHasNotes(self, folder_path: str) -> bool:
        """
        Check if a folder has notes saved.
        
        Args:
            folder_path: Path to check
            
        Returns:
            True if folder has notes, False otherwise
        """
        try:
            folder = Path(folder_path)
            notes_file = folder / self.NOTES_FILENAME
            
            if notes_file.exists():
                # Check if file has content
                with open(notes_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    notes = data.get('notes', '')
                    return bool(notes.strip())
            
            return False
            
        except Exception:
            return False
    
    @pyqtSlot(result=int)
    def getNotesLength(self) -> int:
        """
        Get the length of current notes.
        
        Returns:
            Number of characters in notes
        """
        return len(self._current_notes)
    
    @pyqtSlot(result=int)
    def getNotesWordCount(self) -> int:
        """
        Get the word count of current notes.
        
        Returns:
            Number of words in notes
        """
        if not self._current_notes:
            return 0
        return len(self._current_notes.split())
