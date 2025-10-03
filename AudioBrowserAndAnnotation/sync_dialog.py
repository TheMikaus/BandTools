#!/usr/bin/env python3
"""
Sync dialog UI for Google Drive synchronization.

Provides dialogs for:
- Selecting Google Drive folder
- Reviewing and approving sync operations
- Showing sync progress
"""

from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Optional, Set
import logging

try:
    from PyQt6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
        QTableWidget, QTableWidgetItem, QCheckBox, QTextEdit,
        QProgressDialog, QMessageBox, QInputDialog, QHeaderView,
        QAbstractItemView
    )
    from PyQt6.QtCore import Qt, QThread, pyqtSignal
    from PyQt6.QtGui import QColor
except ImportError:
    # Handle case where PyQt6 is not available (shouldn't happen in main app)
    pass

logger = logging.getLogger(__name__)


class SyncWorker(QThread):
    """Worker thread for performing sync operations."""
    
    progress = pyqtSignal(str)  # Progress message
    finished = pyqtSignal(bool, str)  # Success, message
    
    def __init__(self, sync_manager, operations: List[Dict], is_upload: bool):
        super().__init__()
        self.sync_manager = sync_manager
        self.operations = operations
        self.is_upload = is_upload
        self._cancelled = False
    
    def cancel(self):
        """Cancel the sync operation."""
        self._cancelled = True
    
    def run(self):
        """Perform sync operations."""
        try:
            total = len(self.operations)
            success_count = 0
            
            for i, op in enumerate(self.operations):
                if self._cancelled:
                    self.finished.emit(False, "Sync cancelled by user")
                    return
                
                file_name = op['name']
                op_type = op['type']
                
                self.progress.emit(f"Processing {i+1}/{total}: {file_name}")
                
                if self.is_upload:
                    # Upload operations
                    if op_type == 'add' or op_type == 'update':
                        local_path = op['local_path']
                        if self.sync_manager.upload_file(local_path):
                            success_count += 1
                        else:
                            logger.error(f"Failed to upload: {file_name}")
                    elif op_type == 'delete':
                        if self.sync_manager.delete_remote_file(file_name):
                            success_count += 1
                        else:
                            logger.error(f"Failed to delete remote: {file_name}")
                else:
                    # Download operations
                    if op_type == 'add' or op_type == 'update':
                        local_path = op['local_path']
                        if self.sync_manager.download_file(file_name, local_path):
                            success_count += 1
                        else:
                            logger.error(f"Failed to download: {file_name}")
                    elif op_type == 'delete':
                        local_path = op['local_path']
                        try:
                            if local_path.exists():
                                local_path.unlink()
                            success_count += 1
                        except Exception as e:
                            logger.error(f"Failed to delete local: {file_name}: {e}")
            
            if success_count == total:
                self.finished.emit(True, f"Successfully synced {success_count} files")
            else:
                self.finished.emit(False, f"Synced {success_count}/{total} files. Check logs for errors.")
            
        except Exception as e:
            logger.error(f"Sync operation failed: {e}")
            self.finished.emit(False, f"Sync failed: {str(e)}")


class FolderSelectionDialog(QDialog):
    """Dialog for selecting/creating Google Drive folder."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.folder_name: Optional[str] = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("Select Google Drive Folder")
        self.resize(400, 150)
        
        layout = QVBoxLayout(self)
        
        # Instructions
        label = QLabel(
            "Enter the name of the Google Drive folder to use for sync.\n"
            "If it doesn't exist, it will be created."
        )
        label.setWordWrap(True)
        layout.addWidget(label)
        
        # Note about location
        note = QLabel(
            "Note: The folder will be created in the root of your Google Drive."
        )
        note.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(note)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("Select/Create")
        ok_btn.clicked.connect(self._on_ok)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _on_ok(self):
        """Handle OK button click."""
        folder_name, ok = QInputDialog.getText(
            self,
            "Folder Name",
            "Enter Google Drive folder name:",
            text="BandPracticeSessions"
        )
        
        if ok and folder_name:
            self.folder_name = folder_name.strip()
            self.accept()


class SyncReviewDialog(QDialog):
    """Dialog for reviewing and approving sync operations."""
    
    def __init__(self, local_dir: Path, local_only: Set[str], remote_only: Set[str], 
                 sync_manager, is_upload: bool, current_user: str, parent=None):
        super().__init__(parent)
        self.local_dir = local_dir
        self.local_only = local_only
        self.remote_only = remote_only
        self.sync_manager = sync_manager
        self.is_upload = is_upload
        self.current_user = current_user
        self.selected_operations: List[Dict] = []
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI."""
        if self.is_upload:
            self.setWindowTitle("Review Upload Changes")
        else:
            self.setWindowTitle("Review Download Changes")
        
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Instructions
        if self.is_upload:
            instructions = QLabel(
                "Review changes to upload to Google Drive.\n"
                "Check the boxes next to files you want to upload."
            )
        else:
            instructions = QLabel(
                "Review changes to download from Google Drive.\n"
                "Check the boxes next to files you want to download."
            )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Table of operations
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Sync", "Operation", "File", "Notes"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)
        
        # Populate table
        self._populate_table()
        
        # Log area
        log_label = QLabel("Operation Log:")
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(100)
        layout.addWidget(self.log_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self._select_all)
        button_layout.addWidget(select_all_btn)
        
        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self._deselect_all)
        button_layout.addWidget(deselect_all_btn)
        
        button_layout.addStretch()
        
        if self.is_upload:
            sync_btn = QPushButton("Upload Selected")
        else:
            sync_btn = QPushButton("Download Selected")
        sync_btn.clicked.connect(self._on_sync)
        button_layout.addWidget(sync_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _populate_table(self):
        """Populate the table with sync operations."""
        operations = []
        
        if self.is_upload:
            # Local additions/updates
            for filename in sorted(self.local_only):
                operations.append({
                    'type': 'add',
                    'name': filename,
                    'notes': ''
                })
        else:
            # Remote additions/updates
            for filename in sorted(self.remote_only):
                notes = ''
                # Check if this is another user's annotation file
                if filename.startswith('.audio_notes_') and filename.endswith('.json'):
                    username = filename[13:-5]
                    if username != self.current_user:
                        notes = f"From user: {username}"
                
                operations.append({
                    'type': 'add',
                    'name': filename,
                    'notes': notes
                })
        
        self.table.setRowCount(len(operations))
        
        for row, op in enumerate(operations):
            # Checkbox
            checkbox = QCheckBox()
            
            # Auto-check annotation files for download, but user must confirm others
            if not self.is_upload and op['name'].startswith('.'):
                checkbox.setChecked(True)
            elif self.is_upload:
                # Auto-check files user can modify
                if self.sync_manager.can_user_modify(op['name']):
                    checkbox.setChecked(True)
                else:
                    checkbox.setEnabled(False)
                    op['notes'] = "Cannot modify other users' files"
            
            self.table.setCellWidget(row, 0, checkbox)
            
            # Operation type
            op_type = "Add" if op['type'] == 'add' else "Update"
            if self.is_upload:
                op_type += " (upload)"
            else:
                op_type += " (download)"
            self.table.setItem(row, 1, QTableWidgetItem(op_type))
            
            # Filename
            filename_item = QTableWidgetItem(op['name'])
            # Highlight audio files
            if op['name'].lower().endswith(('.wav', '.mp3')):
                filename_item.setBackground(QColor(255, 255, 200))  # Light yellow
            self.table.setItem(row, 2, filename_item)
            
            # Notes
            self.table.setItem(row, 3, QTableWidgetItem(op['notes']))
    
    def _select_all(self):
        """Select all checkboxes."""
        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0)
            if checkbox and checkbox.isEnabled():
                checkbox.setChecked(True)
    
    def _deselect_all(self):
        """Deselect all checkboxes."""
        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(False)
    
    def _get_selected_operations(self) -> List[Dict]:
        """Get list of selected operations."""
        operations = []
        
        for row in range(self.table.rowCount()):
            checkbox = self.table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                filename = self.table.item(row, 2).text()
                local_path = self.local_dir / filename
                
                operations.append({
                    'type': 'add',  # For now, we only support add operations
                    'name': filename,
                    'local_path': local_path
                })
        
        return operations
    
    def _on_sync(self):
        """Handle sync button click."""
        operations = self._get_selected_operations()
        
        if not operations:
            QMessageBox.information(self, "No Files Selected", "Please select files to sync.")
            return
        
        # Confirm
        if self.is_upload:
            msg = f"Upload {len(operations)} file(s) to Google Drive?"
        else:
            msg = f"Download {len(operations)} file(s) from Google Drive?"
        
        reply = QMessageBox.question(
            self, "Confirm Sync", msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Perform sync in worker thread
        self._perform_sync(operations)
    
    def _perform_sync(self, operations: List[Dict]):
        """Perform the sync operations in a worker thread."""
        # Create progress dialog
        progress = QProgressDialog(
            "Syncing files...", "Cancel", 0, 0, self
        )
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        
        # Create worker
        self.worker = SyncWorker(self.sync_manager, operations, self.is_upload)
        
        # Connect signals
        self.worker.progress.connect(lambda msg: (
            progress.setLabelText(msg),
            self.log_text.append(msg)
        ))
        
        def on_finished(success: bool, message: str):
            progress.close()
            self.log_text.append(message)
            
            if success:
                QMessageBox.information(self, "Sync Complete", message)
                self.selected_operations = operations
                self.accept()
            else:
                QMessageBox.warning(self, "Sync Issues", message)
        
        self.worker.finished.connect(on_finished)
        
        # Handle cancel
        progress.canceled.connect(self.worker.cancel)
        
        # Start worker
        self.worker.start()


class SyncStatusDialog(QDialog):
    """Dialog showing current sync status."""
    
    def __init__(self, local_version: int, remote_version: int, 
                 local_files: int, remote_files: int, parent=None):
        super().__init__(parent)
        self.local_version = local_version
        self.remote_version = remote_version
        self.local_files = local_files
        self.remote_files = remote_files
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("Sync Status")
        self.resize(400, 250)
        
        layout = QVBoxLayout(self)
        
        # Status information
        status_text = f"""
<h3>Synchronization Status</h3>

<b>Local Version:</b> {self.local_version}<br>
<b>Remote Version:</b> {self.remote_version}<br>
<br>
<b>Local Files:</b> {self.local_files}<br>
<b>Remote Files:</b> {self.remote_files}<br>
<br>
"""
        
        if self.local_version < self.remote_version:
            status_text += "<font color='orange'><b>⚠ Remote is ahead</b> - New changes available</font><br>"
        elif self.local_version > self.remote_version:
            status_text += "<font color='blue'><b>📤 Local is ahead</b> - You have unpushed changes</font><br>"
        else:
            status_text += "<font color='green'><b>✓ In sync</b> - Local and remote are up to date</font><br>"
        
        label = QLabel(status_text)
        label.setWordWrap(True)
        label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(label)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
