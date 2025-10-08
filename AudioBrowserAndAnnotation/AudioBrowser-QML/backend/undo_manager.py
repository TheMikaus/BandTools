"""
Undo/Redo Manager for AudioBrowser-QML

Implements a command pattern-based undo/redo system for reversible operations.
Supports undo for:
- Provided name changes
- Annotation add/delete/edit operations
- Other reversible user actions

Architecture:
- Command pattern with execute/undo methods
- Stack-based history with configurable capacity
- Integration with existing backend managers
"""

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from typing import List, Dict, Any, Optional
import json


class UndoCommand:
    """Base class for undoable commands."""
    
    def __init__(self):
        self.description = "Unknown action"
    
    def execute(self) -> bool:
        """Execute the command (for redo). Returns True if successful."""
        return False
    
    def undo(self) -> bool:
        """Undo the command. Returns True if successful."""
        return False
    
    def get_description(self) -> str:
        """Get a human-readable description of the command."""
        return self.description


class ProvidedNameCommand(UndoCommand):
    """Command for changing a file's provided name."""
    
    def __init__(self, file_manager, filepath: str, old_name: str, new_name: str):
        super().__init__()
        self.file_manager = file_manager
        self.filepath = filepath
        self.old_name = old_name
        self.new_name = new_name
        self.description = f"Change name: {old_name} → {new_name}"
    
    def execute(self) -> bool:
        """Apply the new name."""
        if self.file_manager:
            self.file_manager.setProvidedName(self.filepath, self.new_name)
            return True
        return False
    
    def undo(self) -> bool:
        """Restore the old name."""
        if self.file_manager:
            self.file_manager.setProvidedName(self.filepath, self.old_name)
            return True
        return False


class AnnotationAddCommand(UndoCommand):
    """Command for adding an annotation."""
    
    def __init__(self, annotation_manager, filepath: str, annotation: Dict[str, Any]):
        super().__init__()
        self.annotation_manager = annotation_manager
        self.filepath = filepath
        self.annotation = annotation.copy()
        self.annotation_uid = annotation.get('uid', -1)
        self.description = f"Add annotation at {self._format_time(annotation.get('timestamp_ms', 0))}"
    
    def _format_time(self, ms: int) -> str:
        """Format milliseconds as MM:SS."""
        total_seconds = ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def execute(self) -> bool:
        """Add the annotation (for redo)."""
        if self.annotation_manager:
            # Re-add with same UID
            self.annotation_manager.addAnnotationDirect(self.filepath, self.annotation)
            return True
        return False
    
    def undo(self) -> bool:
        """Remove the annotation."""
        if self.annotation_manager and self.annotation_uid >= 0:
            self.annotation_manager.deleteAnnotation(self.filepath, self.annotation_uid)
            return True
        return False


class AnnotationDeleteCommand(UndoCommand):
    """Command for deleting an annotation."""
    
    def __init__(self, annotation_manager, filepath: str, annotation: Dict[str, Any]):
        super().__init__()
        self.annotation_manager = annotation_manager
        self.filepath = filepath
        self.annotation = annotation.copy()
        self.annotation_uid = annotation.get('uid', -1)
        self.description = f"Delete annotation at {self._format_time(annotation.get('timestamp_ms', 0))}"
    
    def _format_time(self, ms: int) -> str:
        """Format milliseconds as MM:SS."""
        total_seconds = ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def execute(self) -> bool:
        """Delete the annotation (for redo)."""
        if self.annotation_manager and self.annotation_uid >= 0:
            self.annotation_manager.deleteAnnotation(self.filepath, self.annotation_uid)
            return True
        return False
    
    def undo(self) -> bool:
        """Restore the annotation."""
        if self.annotation_manager:
            self.annotation_manager.addAnnotationDirect(self.filepath, self.annotation)
            return True
        return False


class AnnotationEditCommand(UndoCommand):
    """Command for editing an annotation field."""
    
    def __init__(self, annotation_manager, filepath: str, uid: int, 
                 field: str, old_value: Any, new_value: Any):
        super().__init__()
        self.annotation_manager = annotation_manager
        self.filepath = filepath
        self.uid = uid
        self.field = field
        self.old_value = old_value
        self.new_value = new_value
        
        field_names = {
            'text': 'text',
            'timestamp_ms': 'timestamp',
            'category': 'category',
            'important': 'importance'
        }
        field_name = field_names.get(field, field)
        self.description = f"Edit annotation {field_name}"
    
    def execute(self) -> bool:
        """Apply the new value (for redo)."""
        if self.annotation_manager:
            self.annotation_manager.updateAnnotationField(
                self.filepath, self.uid, self.field, self.new_value
            )
            return True
        return False
    
    def undo(self) -> bool:
        """Restore the old value."""
        if self.annotation_manager:
            self.annotation_manager.updateAnnotationField(
                self.filepath, self.uid, self.field, self.old_value
            )
            return True
        return False


class UndoManager(QObject):
    """
    Manages undo/redo operations for the application.
    
    Signals:
        canUndoChanged(bool) - Emitted when undo availability changes
        canRedoChanged(bool) - Emitted when redo availability changes
        undoTextChanged(str) - Emitted when undo description changes
        redoTextChanged(str) - Emitted when redo description changes
        commandExecuted() - Emitted after a command is executed
    """
    
    # Signals
    canUndoChanged = pyqtSignal(bool)
    canRedoChanged = pyqtSignal(bool)
    undoTextChanged = pyqtSignal(str)
    redoTextChanged = pyqtSignal(str)
    commandExecuted = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._undo_stack: List[UndoCommand] = []
        self._undo_index: int = 0  # Points to the next command to undo
        self._capacity: int = 100  # Default capacity
        self._file_manager = None
        self._annotation_manager = None
    
    def setFileManager(self, file_manager):
        """Set the file manager for file-related commands."""
        self._file_manager = file_manager
    
    def setAnnotationManager(self, annotation_manager):
        """Set the annotation manager for annotation-related commands."""
        self._annotation_manager = annotation_manager
    
    @pyqtSlot(int)
    def setCapacity(self, capacity: int):
        """Set the maximum number of commands to keep in history."""
        self._capacity = max(10, min(1000, capacity))
        self._trim_stack()
        self._update_state()
    
    def _trim_stack(self):
        """Trim the stack to fit within capacity."""
        if len(self._undo_stack) > self._capacity:
            excess = len(self._undo_stack) - self._capacity
            # Remove oldest commands
            del self._undo_stack[:excess]
            self._undo_index = max(0, self._undo_index - excess)
    
    def push_command(self, command: UndoCommand):
        """
        Push a command onto the undo stack.
        This is called after a command has already been executed.
        """
        # If we're not at the end of the stack, remove commands ahead
        if self._undo_index < len(self._undo_stack):
            del self._undo_stack[self._undo_index:]
        
        # Add the new command
        self._undo_stack.append(command)
        self._undo_index = len(self._undo_stack)
        
        # Trim to capacity
        self._trim_stack()
        
        # Notify state change
        self._update_state()
    
    @pyqtSlot()
    def undo(self):
        """Undo the last command."""
        if not self.can_undo():
            return
        
        # Move back one step
        self._undo_index -= 1
        command = self._undo_stack[self._undo_index]
        
        # Execute the undo
        if command.undo():
            self.commandExecuted.emit()
        else:
            # If undo failed, move index back
            self._undo_index += 1
        
        self._update_state()
    
    @pyqtSlot()
    def redo(self):
        """Redo the next command."""
        if not self.can_redo():
            return
        
        # Get the command at current index
        command = self._undo_stack[self._undo_index]
        
        # Execute the redo
        if command.execute():
            self._undo_index += 1
            self.commandExecuted.emit()
        
        self._update_state()
    
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return self._undo_index > 0
    
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return self._undo_index < len(self._undo_stack)
    
    def get_undo_text(self) -> str:
        """Get description of the command that would be undone."""
        if self.can_undo():
            return self._undo_stack[self._undo_index - 1].get_description()
        return ""
    
    def get_redo_text(self) -> str:
        """Get description of the command that would be redone."""
        if self.can_redo():
            return self._undo_stack[self._undo_index].get_description()
        return ""
    
    @pyqtSlot()
    def clear(self):
        """Clear all undo history."""
        self._undo_stack.clear()
        self._undo_index = 0
        self._update_state()
    
    def _update_state(self):
        """Update and emit state change signals."""
        self.canUndoChanged.emit(self.can_undo())
        self.canRedoChanged.emit(self.can_redo())
        self.undoTextChanged.emit(self.get_undo_text())
        self.redoTextChanged.emit(self.get_redo_text())
    
    # Helper methods for common operations
    
    def record_provided_name_change(self, filepath: str, old_name: str, new_name: str):
        """Record a provided name change."""
        if self._file_manager:
            command = ProvidedNameCommand(self._file_manager, filepath, old_name, new_name)
            self.push_command(command)
    
    def record_annotation_add(self, filepath: str, annotation: Dict[str, Any]):
        """Record an annotation addition."""
        if self._annotation_manager:
            command = AnnotationAddCommand(self._annotation_manager, filepath, annotation)
            self.push_command(command)
    
    def record_annotation_delete(self, filepath: str, annotation: Dict[str, Any]):
        """Record an annotation deletion."""
        if self._annotation_manager:
            command = AnnotationDeleteCommand(self._annotation_manager, filepath, annotation)
            self.push_command(command)
    
    def record_annotation_edit(self, filepath: str, uid: int, field: str, 
                              old_value: Any, new_value: Any):
        """Record an annotation field edit."""
        if self._annotation_manager:
            command = AnnotationEditCommand(
                self._annotation_manager, filepath, uid, field, old_value, new_value
            )
            self.push_command(command)
    
    # QML-accessible properties
    
    @pyqtSlot(result=bool)
    def canUndo(self) -> bool:
        """QML-accessible method to check if undo is available."""
        return self.can_undo()
    
    @pyqtSlot(result=bool)
    def canRedo(self) -> bool:
        """QML-accessible method to check if redo is available."""
        return self.can_redo()
    
    @pyqtSlot(result=str)
    def getUndoText(self) -> str:
        """QML-accessible method to get undo description."""
        return self.get_undo_text()
    
    @pyqtSlot(result=str)
    def getRedoText(self) -> str:
        """QML-accessible method to get redo description."""
        return self.get_redo_text()
    
    @pyqtSlot(result=int)
    def getStackSize(self) -> int:
        """Get current number of commands in the stack."""
        return len(self._undo_stack)
    
    @pyqtSlot(result=int)
    def getCurrentIndex(self) -> int:
        """Get current position in the undo stack."""
        return self._undo_index
