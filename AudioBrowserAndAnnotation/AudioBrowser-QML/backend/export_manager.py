#!/usr/bin/env python3
"""
Export Manager Backend Module

Handles exporting best take files as packages.
Supports folder and ZIP export with optional format conversion.
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
from typing import List, Dict, Optional, Callable
from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot


class ExportWorker(QThread):
    """
    Worker thread for exporting best take files.
    
    Signals:
        progress: Emitted during export (message: str)
        fileProgress: Emitted for each file (current: int, total: int)
        finished: Emitted when export completes (success: bool, message: str)
    """
    
    progress = pyqtSignal(str)
    fileProgress = pyqtSignal(int, int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, files: List[str], destination: str, export_format: str,
                 convert_to_mp3: bool, include_metadata: bool):
        """
        Initialize export worker.
        
        Args:
            files: List of file paths to export
            destination: Destination folder path
            export_format: 'folder' or 'zip'
            convert_to_mp3: Whether to convert audio files to MP3
            include_metadata: Whether to include metadata JSON files
        """
        super().__init__()
        self.files = files
        self.destination = destination
        self.export_format = export_format
        self.convert_to_mp3 = convert_to_mp3
        self.include_metadata = include_metadata
        self._cancelled = False
    
    def cancel(self):
        """Cancel the export operation."""
        self._cancelled = True
    
    def run(self):
        """Run the export operation."""
        try:
            self.progress.emit("Starting export...")
            
            # Create destination folder
            dest_path = Path(self.destination)
            dest_path.mkdir(parents=True, exist_ok=True)
            
            # Export files
            total_files = len(self.files)
            exported_files = []
            
            for i, file_path in enumerate(self.files):
                if self._cancelled:
                    self.finished.emit(False, "Export cancelled by user")
                    return
                
                file_path = Path(file_path)
                if not file_path.exists():
                    self.progress.emit(f"Warning: File not found: {file_path.name}")
                    continue
                
                self.progress.emit(f"Exporting {file_path.name}...")
                self.fileProgress.emit(i + 1, total_files)
                
                # Determine output filename
                if self.convert_to_mp3 and file_path.suffix.lower() in ['.wav', '.wave']:
                    output_name = file_path.stem + '.mp3'
                else:
                    output_name = file_path.name
                
                output_path = dest_path / output_name
                
                # Copy or convert file
                if self.convert_to_mp3 and file_path.suffix.lower() in ['.wav', '.wave']:
                    # Convert to MP3 (requires pydub and ffmpeg)
                    success = self._convert_to_mp3(file_path, output_path)
                    if not success:
                        # Fall back to copying
                        shutil.copy2(file_path, dest_path / file_path.name)
                        exported_files.append(dest_path / file_path.name)
                    else:
                        exported_files.append(output_path)
                else:
                    # Just copy the file
                    shutil.copy2(file_path, output_path)
                    exported_files.append(output_path)
                
                # Copy metadata files if requested
                if self.include_metadata:
                    self._copy_metadata_files(file_path, dest_path)
            
            # Create ZIP if requested
            if self.export_format == 'zip':
                self.progress.emit("Creating ZIP archive...")
                zip_path = dest_path.parent / f"{dest_path.name}.zip"
                self._create_zip(dest_path, zip_path)
                
                # Remove temporary folder
                shutil.rmtree(dest_path)
                
                self.finished.emit(True, f"Export complete! Created: {zip_path}")
            else:
                self.finished.emit(True, f"Export complete! {len(exported_files)} file(s) exported to: {dest_path}")
        
        except Exception as e:
            self.finished.emit(False, f"Export failed: {str(e)}")
    
    def _convert_to_mp3(self, input_path: Path, output_path: Path) -> bool:
        """
        Convert audio file to MP3.
        
        Args:
            input_path: Input WAV file path
            output_path: Output MP3 file path
        
        Returns:
            True if conversion succeeded, False otherwise
        """
        try:
            from pydub import AudioSegment
            
            # Load audio file
            audio = AudioSegment.from_wav(str(input_path))
            
            # Export as MP3
            audio.export(str(output_path), format='mp3', bitrate='192k')
            
            return True
        except ImportError:
            self.progress.emit("Warning: pydub not available, cannot convert to MP3")
            return False
        except Exception as e:
            self.progress.emit(f"Warning: Failed to convert {input_path.name} to MP3: {e}")
            return False
    
    def _copy_metadata_files(self, audio_file: Path, dest_folder: Path):
        """
        Copy metadata files associated with an audio file.
        
        Args:
            audio_file: Audio file path
            dest_folder: Destination folder
        """
        audio_folder = audio_file.parent
        audio_stem = audio_file.stem
        
        # Metadata files that might exist for this audio file
        metadata_patterns = [
            f".annotations_{audio_stem}.json",
            f".clips_{audio_stem}.json",
            ".tempo.json",  # Tempo file for entire folder
            ".takes_metadata.json",  # Takes metadata for entire folder
        ]
        
        for pattern in metadata_patterns:
            metadata_file = audio_folder / pattern
            if metadata_file.exists():
                try:
                    shutil.copy2(metadata_file, dest_folder / metadata_file.name)
                except Exception as e:
                    self.progress.emit(f"Warning: Failed to copy metadata {metadata_file.name}: {e}")
    
    def _create_zip(self, folder_path: Path, zip_path: Path):
        """
        Create a ZIP archive from a folder.
        
        Args:
            folder_path: Folder to zip
            zip_path: Output ZIP file path
        """
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in folder_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(folder_path)
                    zipf.write(file_path, arcname)


class ExportManager(QObject):
    """
    Manager for exporting best take packages.
    
    Provides a high-level interface for exporting files with progress tracking.
    """
    
    # Signals
    exportStarted = pyqtSignal()
    exportProgress = pyqtSignal(str)
    exportFileProgress = pyqtSignal(int, int)
    exportFinished = pyqtSignal(bool, str)
    
    def __init__(self):
        super().__init__()
        self._worker: Optional[ExportWorker] = None
    
    @pyqtSlot(list, str, str, bool, bool)
    def startExport(self, files: List[str], destination: str, export_format: str,
                    convert_to_mp3: bool, include_metadata: bool):
        """
        Start exporting files.
        
        Args:
            files: List of file paths to export
            destination: Destination folder path
            export_format: 'folder' or 'zip'
            convert_to_mp3: Whether to convert audio files to MP3
            include_metadata: Whether to include metadata JSON files
        """
        if self._worker is not None and self._worker.isRunning():
            print("Export already in progress")
            return
        
        # Create worker thread
        self._worker = ExportWorker(files, destination, export_format,
                                    convert_to_mp3, include_metadata)
        
        # Connect signals
        self._worker.progress.connect(self.exportProgress.emit)
        self._worker.fileProgress.connect(self.exportFileProgress.emit)
        self._worker.finished.connect(self._on_export_finished)
        
        # Start export
        self.exportStarted.emit()
        self._worker.start()
    
    @pyqtSlot()
    def cancelExport(self):
        """Cancel the current export operation."""
        if self._worker is not None and self._worker.isRunning():
            self._worker.cancel()
    
    def _on_export_finished(self, success: bool, message: str):
        """
        Handle export finished signal.
        
        Args:
            success: Whether export succeeded
            message: Result message
        """
        self.exportFinished.emit(success, message)
        self._worker = None
