#!/usr/bin/env python3
"""
Batch Operations Backend Module

Handles batch file operations for the AudioBrowser QML application.
Provides batch rename, format conversion, and other bulk operations.
"""

import os
import re
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Callable
from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot


def _ensure_import(mod_name: str, pip_name: str | None = None) -> tuple[bool, str]:
    """Try to import a module, auto-installing if needed.
    
    Args:
        mod_name: Module name to import
        pip_name: Package name for pip (defaults to mod_name)
    
    Returns:
        tuple[bool, str]: (success, error_message)
    """
    try:
        __import__(mod_name)
        return True, ""
    except ImportError:
        if getattr(sys, "frozen", False):
            return False, f"{mod_name} is not available in this frozen build"
        
        pkg = pip_name or mod_name
        
        print(f"Installing {pkg}...")
        install_errors = []
        for args in ([sys.executable, "-m", "pip", "install", pkg],
                     [sys.executable, "-m", "pip", "install", "--user", pkg]):
            try:
                subprocess.check_call(args)
                break
            except subprocess.CalledProcessError as e:
                install_errors.append(f"'{' '.join(args)}' failed with exit code {e.returncode}")
                continue
        else:
            error_msg = f"Failed to install {pkg}. Attempted installations:\n" + "\n".join(f"  - {err}" for err in install_errors)
            return False, error_msg
        
        try:
            __import__(mod_name)
            return True, ""
        except ImportError as e:
            return False, f"Successfully installed {pkg} but still cannot import {mod_name}: {e}"


# Try to import optional dependencies for audio conversion with auto-install
HAVE_PYDUB, pydub_error = _ensure_import("pydub", "pydub")
if HAVE_PYDUB:
    try:
        from pydub import AudioSegment
        from pydub.utils import which as pydub_which
    except ImportError:
        HAVE_PYDUB = False
        AudioSegment = None
        pydub_which = None
else:
    AudioSegment = None
    pydub_which = None


def sanitize_library_name(name: str) -> str:
    """
    Sanitize a library name for use in filenames.
    
    Args:
        name: Name to sanitize
        
    Returns:
        Sanitized name (lowercase, spaces->underscores, no special chars)
    """
    name = re.sub(r'[\\/:*?"<>|]+', "_", name.strip())
    name = re.sub(r"\s+", "_", name).strip()
    return name.lower()


# ========== Worker Classes ==========

class BatchRenameWorker(QObject):
    """Worker thread for batch rename operations."""
    
    progress = pyqtSignal(int, int, str)  # done, total, filename
    fileRenamed = pyqtSignal(str, str, bool, str)  # old_name, new_name, success, error_msg
    finished = pyqtSignal(bool)  # canceled?
    
    def __init__(self, rename_plan: List[Tuple[Path, Path]], 
                 metadata_updater: Optional[Callable[[str, str], None]] = None):
        """
        Initialize batch rename worker.
        
        Args:
            rename_plan: List of (source_path, target_path) tuples
            metadata_updater: Optional callback to update metadata after rename
        """
        super().__init__()
        self._rename_plan = rename_plan
        self._metadata_updater = metadata_updater
        self._cancel = False
    
    def cancel(self):
        """Cancel the operation."""
        self._cancel = True
    
    def run(self):
        """Execute the batch rename operation."""
        total = len(self._rename_plan)
        done = 0
        
        for src, dst in self._rename_plan:
            if self._cancel:
                self.finished.emit(True)
                return
            
            self.progress.emit(done, total, src.name)
            
            try:
                # Perform the rename
                src.rename(dst)
                
                # Update metadata if callback provided
                if self._metadata_updater:
                    self._metadata_updater(src.name, dst.name)
                
                self.fileRenamed.emit(src.name, dst.name, True, "")
                
            except Exception as e:
                self.fileRenamed.emit(src.name, dst.name, False, str(e))
            
            done += 1
        
        self.progress.emit(done, total, "")
        self.finished.emit(False)


class ConvertWorker(QObject):
    """Worker thread for audio format conversion (WAV→MP3)."""
    
    progress = pyqtSignal(int, int, str)  # done, total, filename
    file_done = pyqtSignal(str, str, bool, str)  # src_name, dst_name, deleted_ok, error_msg
    finished = pyqtSignal(bool)  # canceled?
    
    def __init__(self, wav_paths: List[str], bitrate: str = "192k", delete_originals: bool = True):
        """
        Initialize conversion worker.
        
        Args:
            wav_paths: List of WAV file paths to convert
            bitrate: MP3 bitrate (e.g., "128k", "192k", "256k")
            delete_originals: Whether to delete original WAV files after conversion
        """
        super().__init__()
        self._paths = [str(p) for p in wav_paths]
        self._bitrate = str(bitrate)
        self._delete_originals = delete_originals
        self._cancel = False
    
    def cancel(self):
        """Cancel the operation."""
        self._cancel = True
    
    def run(self):
        """Execute the conversion operation."""
        if not HAVE_PYDUB:
            self.finished.emit(False)
            return
        
        total = len(self._paths)
        done = 0
        
        for srcs in self._paths:
            if self._cancel:
                self.finished.emit(True)
                return
            
            src = Path(srcs)
            self.progress.emit(done, total, src.name)
            
            try:
                # Determine target filename
                base = src.stem
                target = src.with_suffix(".mp3")
                n = 1
                while target.exists() and target.resolve() != src.resolve():
                    target = src.with_name(f"{base} ({n}).mp3")
                    n += 1
                
                # Convert to MP3
                audio = AudioSegment.from_file(str(src))
                audio.export(str(target), format="mp3", bitrate=self._bitrate)
                
                # Delete original if requested
                deleted_ok = True
                if self._delete_originals:
                    try:
                        src.unlink()
                    except Exception as de:
                        deleted_ok = False
                        self.file_done.emit(src.name, target.name, False, 
                                          f"Converted but couldn't delete: {de}")
                    else:
                        self.file_done.emit(src.name, target.name, True, "")
                else:
                    self.file_done.emit(src.name, target.name, True, "")
                    
            except Exception as e:
                self.file_done.emit(src.name, "", False, str(e))
            
            done += 1
            self.progress.emit(done, total, src.name)
        
        self.finished.emit(False)


class MonoConvertWorker(QObject):
    """Worker thread for stereo to mono conversion."""
    
    progress = pyqtSignal(int, int, str)  # done, total, filename
    file_done = pyqtSignal(str, bool, str)  # filename, success, error_msg
    finished = pyqtSignal(bool)  # canceled?
    
    def __init__(self, audio_path: str, left_enabled: bool = True, right_enabled: bool = True):
        """
        Initialize mono conversion worker.
        
        Args:
            audio_path: Path to the audio file to convert
            left_enabled: Whether to include left channel
            right_enabled: Whether to include right channel
        """
        super().__init__()
        self._path = str(audio_path)
        self._left_enabled = left_enabled
        self._right_enabled = right_enabled
        self._cancel = False
    
    def cancel(self):
        """Cancel the operation."""
        self._cancel = True
    
    def run(self):
        """Execute the mono conversion operation."""
        if self._cancel:
            self.finished.emit(True)
            return
        
        if not HAVE_PYDUB:
            self.file_done.emit("", False, "pydub library not available")
            self.finished.emit(False)
            return
        
        if not self._left_enabled and not self._right_enabled:
            self.file_done.emit("", False, "Not exporting any audio. Aborting.")
            self.finished.emit(False)
            return
        
        src = Path(self._path)
        self.progress.emit(0, 1, src.name)
        
        try:
            # Load the audio file
            audio = AudioSegment.from_file(str(src))
            
            # Check if already mono
            if audio.channels == 1:
                self.file_done.emit(src.name, False, "File is already mono")
                self.finished.emit(False)
                return
            
            # Convert to mono respecting the muted channels
            channels = audio.split_to_mono()
            if not self._left_enabled:
                mono_audio = channels[1]
            elif not self._right_enabled:
                mono_audio = channels[0]
            else:
                mono_audio = audio.set_channels(1)
            
            # Create backup directory if it doesn't exist
            backup_dir = src.parent / ".backup"
            backup_dir.mkdir(exist_ok=True)
            
            # Create backup filename in .backup folder
            base = src.stem
            backup_name = f"{base}_stereo{src.suffix}"
            backup_path = backup_dir / backup_name
            
            # Make sure backup doesn't already exist
            n = 1
            while backup_path.exists():
                backup_name = f"{base}_stereo({n}){src.suffix}"
                backup_path = backup_dir / backup_name
                n += 1
            
            # Rename original to backup
            src.rename(backup_path)
            
            # Export mono version with original filename
            if src.suffix.lower() in ('.mp3',):
                mono_audio.export(str(src), format="mp3", bitrate="192k")
            else:
                mono_audio.export(str(src), format="wav")
            
            self.file_done.emit(src.name, True, f"Converted to mono (stereo backup: {backup_name})")
            
        except Exception as e:
            self.file_done.emit(src.name, False, str(e))
        
        self.progress.emit(1, 1, src.name)
        self.finished.emit(False)


class VolumeBoostWorker(QObject):
    """Worker thread for volume boost export."""
    
    progress = pyqtSignal(int, int, str)  # done, total, filename
    file_done = pyqtSignal(str, bool, str)  # filename, success, error_msg
    finished = pyqtSignal(bool)  # canceled?
    
    def __init__(self, audio_path: str, boost_db: float):
        """
        Initialize volume boost worker.
        
        Args:
            audio_path: Path to the audio file
            boost_db: Boost amount in dB (e.g., 3.0 for +3dB)
        """
        super().__init__()
        self._path = str(audio_path)
        self._boost_db = float(boost_db)
        self._cancel = False
    
    def cancel(self):
        """Cancel the operation."""
        self._cancel = True
    
    def run(self):
        """Execute the volume boost operation."""
        if self._cancel:
            self.finished.emit(True)
            return
        
        if not HAVE_PYDUB:
            self.file_done.emit("", False, "pydub library not available")
            self.finished.emit(False)
            return
        
        src = Path(self._path)
        self.progress.emit(0, 1, src.name)
        
        try:
            # Load and boost audio
            audio = AudioSegment.from_file(str(src))
            boosted = audio + self._boost_db
            
            # Create output filename
            base = src.stem
            output_name = f"{base}_boosted{src.suffix}"
            output_path = src.with_name(output_name)
            
            # Make sure output doesn't exist
            n = 1
            while output_path.exists():
                output_name = f"{base}_boosted({n}){src.suffix}"
                output_path = src.with_name(output_name)
                n += 1
            
            # Export boosted audio
            if src.suffix.lower() in ('.mp3',):
                boosted.export(str(output_path), format="mp3", bitrate="192k")
            else:
                boosted.export(str(output_path), format="wav")
            
            self.file_done.emit(output_name, True, "")
            
        except Exception as e:
            self.file_done.emit(src.name, False, str(e))
        
        self.progress.emit(1, 1, src.name)
        self.finished.emit(False)


# ========== Main Backend Class ==========

class BatchOperations(QObject):
    """
    Batch operations manager for the AudioBrowser application.
    
    Provides batch rename, format conversion, and other bulk operations
    with signals for QML integration.
    """
    
    # Signals
    operationStarted = pyqtSignal(str)  # operation_name
    operationProgress = pyqtSignal(int, int, str)  # done, total, current_file
    operationFinished = pyqtSignal(bool, str)  # success, message
    errorOccurred = pyqtSignal(str)  # error_message
    
    def __init__(self, parent=None):
        """Initialize the batch operations manager."""
        super().__init__(parent)
        
        self._current_thread: Optional[QThread] = None
        self._current_worker: Optional[QObject] = None
        self._current_directory: Optional[Path] = None
    
    # ========== QML-accessible methods ==========
    
    @pyqtSlot(result=bool)
    def isPydubAvailable(self) -> bool:
        """
        Check if pydub is available for audio operations.
        
        Returns:
            True if pydub is available
        """
        return HAVE_PYDUB
    
    @pyqtSlot(result=bool)
    def isFfmpegAvailable(self) -> bool:
        """
        Check if FFmpeg is available for audio conversion.
        
        Returns:
            True if FFmpeg is available
        """
        if not HAVE_PYDUB or not pydub_which:
            return False
        try:
            return pydub_which("ffmpeg") is not None
        except Exception:
            return False
    
    @pyqtSlot(str)
    def setCurrentDirectory(self, directory: str) -> None:
        """
        Set the current working directory.
        
        Args:
            directory: Path to the directory
        """
        try:
            path = Path(directory)
            if path.exists() and path.is_dir():
                self._current_directory = path
        except Exception as e:
            self.errorOccurred.emit(f"Error setting directory: {e}")
    
    @pyqtSlot(list, str, result=list)
    def previewBatchRename(self, file_paths: List[str], name_pattern: str) -> List[Dict[str, str]]:
        """
        Preview batch rename operation.
        
        Args:
            file_paths: List of file paths to rename
            name_pattern: Name pattern to use (empty = use provided names)
            
        Returns:
            List of dicts with 'oldName', 'newName', 'status'
        """
        try:
            files = [Path(fp) for fp in file_paths]
            if not files:
                return []
            
            # Sort by creation time
            def ctime(p: Path) -> float:
                try:
                    return os.path.getctime(p)
                except Exception:
                    return p.stat().st_mtime
            
            files.sort(key=ctime)
            
            # Generate rename plan
            width = max(2, len(str(len(files))))
            preview = []
            
            for i, p in enumerate(files, start=1):
                # Use provided name or file stem
                if name_pattern:
                    base = sanitize_library_name(name_pattern)
                else:
                    base = sanitize_library_name(p.stem)
                
                new_base = f"{str(i).zfill(width)}_{base}"
                target = p.with_name(f"{new_base}{p.suffix.lower()}")
                
                # Check for conflicts
                n = 1
                while target.exists() and target.resolve() != p.resolve():
                    target = p.with_name(f"{new_base} ({n}){p.suffix.lower()}")
                    n += 1
                
                status = "ok" if not target.exists() or target.resolve() == p.resolve() else "conflict"
                
                preview.append({
                    'oldName': p.name,
                    'newName': target.name,
                    'status': status
                })
            
            return preview
            
        except Exception as e:
            self.errorOccurred.emit(f"Error previewing rename: {e}")
            return []
    
    @pyqtSlot(list, str)
    def executeBatchRename(self, file_paths: List[str], name_pattern: str = "") -> None:
        """
        Execute batch rename operation.
        
        Args:
            file_paths: List of file paths to rename
            name_pattern: Optional name pattern to use
        """
        try:
            if not file_paths:
                self.errorOccurred.emit("No files selected for rename")
                return
            
            files = [Path(fp) for fp in file_paths]
            
            # Sort by creation time
            def ctime(p: Path) -> float:
                try:
                    return os.path.getctime(p)
                except Exception:
                    return p.stat().st_mtime
            
            files.sort(key=ctime)
            
            # Generate rename plan
            width = max(2, len(str(len(files))))
            plan = []
            
            for i, p in enumerate(files, start=1):
                if name_pattern:
                    base = sanitize_library_name(name_pattern)
                else:
                    base = sanitize_library_name(p.stem)
                
                new_base = f"{str(i).zfill(width)}_{base}"
                target = p.with_name(f"{new_base}{p.suffix.lower()}")
                
                # Handle conflicts
                n = 1
                while target.exists() and target.resolve() != p.resolve():
                    target = p.with_name(f"{new_base} ({n}){p.suffix.lower()}")
                    n += 1
                
                plan.append((p, target))
            
            # Execute in worker thread
            self._execute_rename_worker(plan)
            
        except Exception as e:
            self.errorOccurred.emit(f"Error executing rename: {e}")
    
    def _execute_rename_worker(self, rename_plan: List[Tuple[Path, Path]]) -> None:
        """Execute batch rename in worker thread."""
        self.operationStarted.emit("Batch Rename")
        
        self._current_thread = QThread(self)
        self._current_worker = BatchRenameWorker(rename_plan)
        self._current_worker.moveToThread(self._current_thread)
        
        # Connect signals
        self._current_thread.started.connect(self._current_worker.run)
        self._current_worker.progress.connect(self.operationProgress.emit)
        self._current_worker.finished.connect(self._on_rename_finished)
        
        # Start thread
        self._current_thread.start()
    
    def _on_rename_finished(self, canceled: bool):
        """Handle rename operation completion."""
        if canceled:
            self.operationFinished.emit(False, "Rename operation canceled")
        else:
            self.operationFinished.emit(True, "Rename operation completed")
        
        # Cleanup
        if self._current_worker:
            self._current_worker.deleteLater()
        if self._current_thread:
            self._current_thread.quit()
            self._current_thread.wait()
            self._current_thread.deleteLater()
        
        self._current_worker = None
        self._current_thread = None
    
    @pyqtSlot(list, str, bool)
    def convertWavToMp3(self, wav_paths: List[str], bitrate: str = "192k", 
                        delete_originals: bool = True) -> None:
        """
        Convert WAV files to MP3.
        
        Args:
            wav_paths: List of WAV file paths to convert
            bitrate: MP3 bitrate (e.g., "128k", "192k", "256k")
            delete_originals: Whether to delete original WAV files
        """
        if not HAVE_PYDUB:
            self.errorOccurred.emit("pydub library not available")
            return
        
        if not self.isFfmpegAvailable():
            self.errorOccurred.emit("FFmpeg not found. Please install FFmpeg.")
            return
        
        if not wav_paths:
            self.errorOccurred.emit("No WAV files selected")
            return
        
        try:
            self.operationStarted.emit("WAV to MP3 Conversion")
            
            self._current_thread = QThread(self)
            self._current_worker = ConvertWorker(wav_paths, bitrate, delete_originals)
            self._current_worker.moveToThread(self._current_thread)
            
            # Connect signals
            self._current_thread.started.connect(self._current_worker.run)
            self._current_worker.progress.connect(self.operationProgress.emit)
            self._current_worker.finished.connect(self._on_convert_finished)
            
            # Start thread
            self._current_thread.start()
            
        except Exception as e:
            self.errorOccurred.emit(f"Error starting conversion: {e}")
    
    def _on_convert_finished(self, canceled: bool):
        """Handle conversion operation completion."""
        if canceled:
            self.operationFinished.emit(False, "Conversion canceled")
        else:
            self.operationFinished.emit(True, "Conversion completed")
        
        # Cleanup
        if self._current_worker:
            self._current_worker.deleteLater()
        if self._current_thread:
            self._current_thread.quit()
            self._current_thread.wait()
            self._current_thread.deleteLater()
        
        self._current_worker = None
        self._current_thread = None
    
    @pyqtSlot(str, bool, bool)
    def convertToMono(self, audio_path: str, left_enabled: bool = True, 
                     right_enabled: bool = True) -> None:
        """
        Convert stereo audio to mono.
        
        Args:
            audio_path: Path to the audio file
            left_enabled: Whether to include left channel
            right_enabled: Whether to include right channel
        """
        if not HAVE_PYDUB:
            self.errorOccurred.emit("pydub library not available")
            return
        
        if not self.isFfmpegAvailable():
            self.errorOccurred.emit("FFmpeg not found. Please install FFmpeg.")
            return
        
        try:
            self.operationStarted.emit("Stereo to Mono Conversion")
            
            self._current_thread = QThread(self)
            self._current_worker = MonoConvertWorker(audio_path, left_enabled, right_enabled)
            self._current_worker.moveToThread(self._current_thread)
            
            # Connect signals
            self._current_thread.started.connect(self._current_worker.run)
            self._current_worker.progress.connect(self.operationProgress.emit)
            self._current_worker.finished.connect(self._on_mono_finished)
            
            # Start thread
            self._current_thread.start()
            
        except Exception as e:
            self.errorOccurred.emit(f"Error starting mono conversion: {e}")
    
    def _on_mono_finished(self, canceled: bool):
        """Handle mono conversion completion."""
        if canceled:
            self.operationFinished.emit(False, "Mono conversion canceled")
        else:
            self.operationFinished.emit(True, "Mono conversion completed")
        
        # Cleanup
        if self._current_worker:
            self._current_worker.deleteLater()
        if self._current_thread:
            self._current_thread.quit()
            self._current_thread.wait()
            self._current_thread.deleteLater()
        
        self._current_worker = None
        self._current_thread = None
    
    @pyqtSlot(str, float)
    def exportWithVolumeBoost(self, audio_path: str, boost_db: float) -> None:
        """
        Export audio file with volume boost.
        
        Args:
            audio_path: Path to the audio file
            boost_db: Boost amount in dB (e.g., 3.0 for +3dB)
        """
        if not HAVE_PYDUB:
            self.errorOccurred.emit("pydub library not available")
            return
        
        if not self.isFfmpegAvailable():
            self.errorOccurred.emit("FFmpeg not found. Please install FFmpeg.")
            return
        
        try:
            self.operationStarted.emit("Volume Boost Export")
            
            self._current_thread = QThread(self)
            self._current_worker = VolumeBoostWorker(audio_path, boost_db)
            self._current_worker.moveToThread(self._current_thread)
            
            # Connect signals
            self._current_thread.started.connect(self._current_worker.run)
            self._current_worker.progress.connect(self.operationProgress.emit)
            self._current_worker.finished.connect(self._on_boost_finished)
            
            # Start thread
            self._current_thread.start()
            
        except Exception as e:
            self.errorOccurred.emit(f"Error starting volume boost: {e}")
    
    def _on_boost_finished(self, canceled: bool):
        """Handle volume boost completion."""
        if canceled:
            self.operationFinished.emit(False, "Volume boost canceled")
        else:
            self.operationFinished.emit(True, "Volume boost completed")
        
        # Cleanup
        if self._current_worker:
            self._current_worker.deleteLater()
        if self._current_thread:
            self._current_thread.quit()
            self._current_thread.wait()
            self._current_thread.deleteLater()
        
        self._current_worker = None
        self._current_thread = None
    
    @pyqtSlot()
    def cancelCurrentOperation(self) -> None:
        """Cancel the current batch operation."""
        if self._current_worker and hasattr(self._current_worker, 'cancel'):
            self._current_worker.cancel()
