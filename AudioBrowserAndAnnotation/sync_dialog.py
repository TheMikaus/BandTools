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

logger = logging.getLogger(__name__)

# Import PyQt6 - these are required for the dialog to work
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QCheckBox, QTextEdit,
    QProgressDialog, QMessageBox, QInputDialog, QHeaderView,
    QAbstractItemView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor


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


class SyncRulesDialog(QDialog):
    """Dialog for configuring selective sync rules."""
    
    def __init__(self, sync_rules, parent=None):
        super().__init__(parent)
        self.sync_rules = sync_rules
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("Sync Rules Configuration")
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Info label
        info_label = QLabel(
            "<b>Configure selective sync rules to control what gets synced:</b>"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # File size limit
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Max file size (MB, 0=unlimited):"))
        self.size_spin = QCheckBox()
        from PyQt6.QtWidgets import QSpinBox
        self.size_value = QSpinBox()
        self.size_value.setMinimum(0)
        self.size_value.setMaximum(10000)
        self.size_value.setValue(int(self.sync_rules.max_file_size_mb))
        self.size_value.setEnabled(self.sync_rules.max_file_size_mb > 0)
        
        self.size_enabled = QCheckBox("Limit file size")
        self.size_enabled.setChecked(self.sync_rules.max_file_size_mb > 0)
        self.size_enabled.toggled.connect(lambda checked: self.size_value.setEnabled(checked))
        
        size_layout.addWidget(self.size_enabled)
        size_layout.addWidget(self.size_value)
        size_layout.addWidget(QLabel("MB"))
        layout.addLayout(size_layout)
        
        # Sync audio files checkbox
        self.sync_audio_check = QCheckBox("Sync audio files (WAV, MP3, etc.)")
        self.sync_audio_check.setChecked(self.sync_rules.sync_audio_files)
        self.sync_audio_check.setToolTip(
            "Uncheck to sync only metadata/annotation files, not audio files"
        )
        layout.addWidget(self.sync_audio_check)
        
        # Annotations only checkbox
        self.annotations_only_check = QCheckBox("Sync annotations only (no audio)")
        self.annotations_only_check.setChecked(self.sync_rules.sync_annotations_only)
        self.annotations_only_check.setToolTip(
            "Only sync .audio_notes_*.json, .provided_names.json, and other metadata files"
        )
        layout.addWidget(self.annotations_only_check)
        
        # Auto-sync checkbox
        self.auto_sync_check = QCheckBox("Enable auto-sync mode")
        self.auto_sync_check.setChecked(self.sync_rules.auto_sync_enabled)
        self.auto_sync_check.setToolTip(
            "Automatically sync when files change (requires manual trigger for now)"
        )
        layout.addWidget(self.auto_sync_check)
        
        # Auto-download best takes
        self.auto_download_best_check = QCheckBox("Auto-download Best Takes only")
        self.auto_download_best_check.setChecked(self.sync_rules.auto_download_best_takes)
        self.auto_download_best_check.setToolTip(
            "Automatically download only files marked as Best Takes"
        )
        layout.addWidget(self.auto_download_best_check)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save Rules")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
    
    def get_rules(self):
        """Get the configured sync rules."""
        from gdrive_sync import SyncRules
        return SyncRules(
            max_file_size_mb=self.size_value.value() if self.size_enabled.isChecked() else 0,
            sync_audio_files=self.sync_audio_check.isChecked(),
            sync_annotations_only=self.annotations_only_check.isChecked(),
            auto_sync_enabled=self.auto_sync_check.isChecked(),
            auto_download_best_takes=self.auto_download_best_check.isChecked()
        )


class SyncHistoryDialog(QDialog):
    """Dialog for viewing sync history."""
    
    def __init__(self, sync_history, parent=None):
        super().__init__(parent)
        self.sync_history = sync_history
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("Sync History")
        self.resize(700, 500)
        
        layout = QVBoxLayout(self)
        
        # Info label
        info_label = QLabel("<b>Recent sync operations:</b>")
        layout.addWidget(info_label)
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels([
            "Date/Time", "Operation", "Files", "User", "Details"
        ])
        
        # Set column widths
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        
        # Populate history
        entries = self.sync_history.get_recent_entries(50)  # Show last 50
        entries.reverse()  # Most recent first
        
        self.history_table.setRowCount(len(entries))
        for i, entry in enumerate(entries):
            # Parse timestamp
            timestamp = entry.get('timestamp', '')
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                time_str = timestamp
            
            self.history_table.setItem(i, 0, QTableWidgetItem(time_str))
            self.history_table.setItem(i, 1, QTableWidgetItem(entry.get('operation', '')))
            self.history_table.setItem(i, 2, QTableWidgetItem(str(entry.get('files_count', 0))))
            self.history_table.setItem(i, 3, QTableWidgetItem(entry.get('user', '')))
            self.history_table.setItem(i, 4, QTableWidgetItem(entry.get('details', '')))
        
        layout.addWidget(self.history_table)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class ConflictResolutionDialog(QDialog):
    """Dialog for resolving sync conflicts."""
    
    def __init__(self, conflicts: List[Dict], parent=None):
        super().__init__(parent)
        self.conflicts = conflicts
        self.resolutions = {}  # file -> 'keep_local' / 'keep_remote' / 'merge'
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("Resolve Sync Conflicts")
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Info label
        info_label = QLabel(
            f"<b>Found {len(self.conflicts)} conflicting file(s):</b><br>"
            "Choose how to resolve each conflict:"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Conflicts table
        self.conflicts_table = QTableWidget()
        self.conflicts_table.setColumnCount(4)
        self.conflicts_table.setHorizontalHeaderLabels([
            "File", "Local Modified", "Remote Modified", "Resolution"
        ])
        
        # Set column widths
        header = self.conflicts_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        # Populate conflicts
        from PyQt6.QtWidgets import QComboBox
        self.conflicts_table.setRowCount(len(self.conflicts))
        
        for i, conflict in enumerate(self.conflicts):
            filename = conflict.get('name', '')
            local_time = conflict.get('local_modified', 'Unknown')
            remote_time = conflict.get('remote_modified', 'Unknown')
            
            self.conflicts_table.setItem(i, 0, QTableWidgetItem(filename))
            self.conflicts_table.setItem(i, 1, QTableWidgetItem(local_time))
            self.conflicts_table.setItem(i, 2, QTableWidgetItem(remote_time))
            
            # Resolution combo box
            combo = QComboBox()
            combo.addItems(["Keep Local", "Keep Remote", "Merge (if possible)"])
            combo.setCurrentIndex(0)
            self.conflicts_table.setCellWidget(i, 3, combo)
            
            # Default to keep local
            self.resolutions[filename] = 'keep_local'
            combo.currentIndexChanged.connect(
                lambda idx, fn=filename: self._on_resolution_changed(fn, idx)
            )
        
        layout.addWidget(self.conflicts_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        resolve_btn = QPushButton("Apply Resolutions")
        resolve_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(resolve_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
    
    def _on_resolution_changed(self, filename: str, index: int):
        """Handle resolution change."""
        resolutions = ['keep_local', 'keep_remote', 'merge']
        self.resolutions[filename] = resolutions[index]
    
    def get_resolutions(self) -> Dict[str, str]:
        """Get the conflict resolutions."""
        return self.resolutions
