#!/usr/bin/env python3
"""
AudioBrowser QML Application Entry Point

This is the main entry point for the QML-based AudioBrowser application.
Phase 0: Basic QML application setup and infrastructure
"""

import sys
from pathlib import Path

# Ensure PyQt6 dependencies are available
def _ensure_import(mod_name: str, pip_name: str | None = None) -> bool:
    """Try to import a module, installing it if necessary."""
    if pip_name is None:
        pip_name = mod_name
    
    try:
        __import__(mod_name)
        return True
    except ImportError as e:
        # Log the initial import error for diagnostics
        print(f"WARNING: Failed to import {mod_name}: {e}", file=sys.stderr)
        print(f"Installing {pip_name}...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
        except subprocess.CalledProcessError as install_error:
            error_msg = f"Failed to install {pip_name}: {install_error}"
            print(f"ERROR: {error_msg}", file=sys.stderr)
            raise
        
        try:
            __import__(mod_name)
            return True
        except ImportError as post_install_error:
            # Special handling for pydub: if it fails with pyaudioop error on Python 3.13+,
            # install audioop-lts which provides the missing audioop module
            if mod_name == "pydub" and "pyaudioop" in str(post_install_error) and sys.version_info >= (3, 13):
                print(f"WARNING: pydub requires audioop module (removed in Python 3.13+). Installing audioop-lts...", file=sys.stderr)
                try:
                    import subprocess
                    # Try to install audioop-lts
                    for args in ([sys.executable, "-m", "pip", "install", "audioop-lts"],
                                 [sys.executable, "-m", "pip", "install", "--user", "audioop-lts"]):
                        try:
                            subprocess.check_call(args)
                            break
                        except subprocess.CalledProcessError:
                            continue
                    
                    # Try importing pydub again
                    __import__(mod_name)
                    print(f"SUCCESS: {mod_name} now works with audioop-lts", file=sys.stderr)
                    return True
                except Exception as audioop_error:
                    error_msg = f"Successfully installed {pip_name} but still cannot import {mod_name}: {post_install_error}. Also tried installing audioop-lts: {audioop_error}"
                    print(f"ERROR: {error_msg}", file=sys.stderr)
                    raise
            
            error_msg = f"Successfully installed {pip_name} but still cannot import {mod_name}: {post_install_error}"
            print(f"ERROR: {error_msg}", file=sys.stderr)
            raise

# Install required dependencies
_ensure_import("PyQt6.QtCore", "PyQt6")
_ensure_import("PyQt6.QtGui", "PyQt6")
_ensure_import("PyQt6.QtWidgets", "PyQt6")
_ensure_import("PyQt6.QtQuick", "PyQt6")
_ensure_import("PyQt6.QtQml", "PyQt6")

from PyQt6.QtCore import QUrl, QObject, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine, qmlRegisterType

# Import backend modules
from backend.settings_manager import SettingsManager
from backend.color_manager import ColorManager
from backend.audio_engine import AudioEngine
from backend.file_manager import FileManager
from backend.models import FileListModel, AnnotationsModel
from backend.waveform_engine import WaveformEngine
from backend.waveform_view import WaveformView
from backend.annotation_manager import AnnotationManager
from backend.clip_manager import ClipManager
from backend.folder_notes_manager import FolderNotesManager
from backend.batch_operations import BatchOperations
from backend.practice_statistics import PracticeStatistics
from backend.practice_goals import PracticeGoals
from backend.setlist_manager import SetlistManager
from backend.tempo_manager import TempoManager
from backend.fingerprint_engine import FingerprintEngine
from backend.backup_manager import BackupManager
from backend.export_manager import ExportManager
from backend.documentation_manager import DocumentationManager
from backend.undo_manager import UndoManager
from backend.sync_manager import SyncManager
from backend.log_viewer import LogViewer


class ApplicationViewModel(QObject):
    """
    Main application view model exposing application state to QML.
    Phase 0: Basic stub for testing QML integration.
    """
    
    messageChanged = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._message = "AudioBrowser QML - Phase 0"
    
    @pyqtSlot(result=str)
    def getMessage(self):
        """Get the current message."""
        return self._message
    
    @pyqtSlot(str)
    def setMessage(self, message: str):
        """Set a new message."""
        if message != self._message:
            self._message = message
            self.messageChanged.emit(self._message)


def main():
    """Main application entry point."""
    app = QGuiApplication(sys.argv)
    
    # Set application metadata
    app.setOrganizationName("BandTools")
    app.setOrganizationDomain("github.com/TheMikaus/BandTools")
    app.setApplicationName("AudioBrowser-QML")
    app.setApplicationVersion("0.14.0")  # Phase 14 in progress - Undo/Redo System
    
    # Register custom QML types
    qmlRegisterType(WaveformView, "AudioBrowser", 1, 0, "WaveformView")
    
    # Create QML engine
    engine = QQmlApplicationEngine()
    
    # Create backend managers
    settings_manager = SettingsManager()
    color_manager = ColorManager(theme=settings_manager.getTheme())
    audio_engine = AudioEngine()
    file_manager = FileManager()
    tempo_manager = TempoManager()
    waveform_engine = WaveformEngine()
    annotation_manager = AnnotationManager()
    clip_manager = ClipManager()
    folder_notes_manager = FolderNotesManager()
    batch_operations = BatchOperations()
    practice_statistics = PracticeStatistics()
    practice_goals = PracticeGoals()
    
    # Connect practice goals to practice statistics
    practice_goals.setPracticeStatistics(practice_statistics)
    
    # Create setlist manager (will be initialized with root path when directory changes)
    setlist_manager = SetlistManager(Path.home())
    
    # Create fingerprint engine
    fingerprint_engine = FingerprintEngine()
    
    # Create backup manager
    backup_manager = BackupManager()
    export_manager = ExportManager()
    
    # Create documentation manager
    documentation_manager = DocumentationManager()
    
    # Register custom QML types
    qmlRegisterType(WaveformView, "AudioBrowser", 1, 0, "WaveformView")

    # Create QML engine
    engine = QQmlApplicationEngine()

    # Create backend managers with error checks
    def safe_create(name, ctor):
        try:
            obj = ctor()
            if obj is None:
                print(f"ERROR: {name} is None after construction", file=sys.stderr)
                sys.exit(2)
            return obj
        except Exception as e:
            print(f"ERROR: Failed to construct {name}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            sys.exit(2)

    settings_manager = safe_create("SettingsManager", SettingsManager)
    color_manager = safe_create("ColorManager", lambda: ColorManager(theme=settings_manager.getTheme()))
    audio_engine = safe_create("AudioEngine", AudioEngine)
    file_manager = safe_create("FileManager", FileManager)
    tempo_manager = safe_create("TempoManager", TempoManager)
    waveform_engine = safe_create("WaveformEngine", WaveformEngine)
    annotation_manager = safe_create("AnnotationManager", AnnotationManager)
    clip_manager = safe_create("ClipManager", ClipManager)
    folder_notes_manager = safe_create("FolderNotesManager", FolderNotesManager)
    batch_operations = safe_create("BatchOperations", BatchOperations)
    practice_statistics = safe_create("PracticeStatistics", PracticeStatistics)
    practice_goals = safe_create("PracticeGoals", PracticeGoals)

    # Connect practice goals to practice statistics
    try:
        practice_goals.setPracticeStatistics(practice_statistics)
    except Exception as e:
        print(f"ERROR: Failed to connect PracticeGoals to PracticeStatistics: {e}", file=sys.stderr)
        sys.exit(2)

    setlist_manager = safe_create("SetlistManager", lambda: SetlistManager(Path.home()))
    fingerprint_engine = safe_create("FingerprintEngine", FingerprintEngine)
    backup_manager = safe_create("BackupManager", BackupManager)
    export_manager = safe_create("ExportManager", ExportManager)
    documentation_manager = safe_create("DocumentationManager", DocumentationManager)
    undo_manager = safe_create("UndoManager", UndoManager)
    try:
        undo_manager.setFileManager(file_manager)
        undo_manager.setAnnotationManager(annotation_manager)
        undo_manager.setCapacity(settings_manager.getUndoLimit())
    except Exception as e:
        print(f"ERROR: Failed to configure UndoManager: {e}", file=sys.stderr)
        sys.exit(2)
    try:
        annotation_manager.setUndoManager(undo_manager)
    except Exception as e:
        print(f"ERROR: Failed to connect AnnotationManager to UndoManager: {e}", file=sys.stderr)
        sys.exit(2)
    config_dir = Path.home() / ".audiobrowser"
    sync_manager = safe_create("SyncManager", lambda: SyncManager(config_dir))
    log_viewer = safe_create("LogViewer", LogViewer)
    file_list_model = safe_create("FileListModel", lambda: FileListModel(file_manager=file_manager, tempo_manager=tempo_manager))
    annotations_model = safe_create("AnnotationsModel", AnnotationsModel)
    view_model = safe_create("ApplicationViewModel", ApplicationViewModel)
    def update_tempo_directory(directory):
        if directory:
            tempo_manager.setCurrentDirectory(Path(directory))
    file_manager.currentDirectoryChanged.connect(update_tempo_directory)
    
    # Connect tempo manager changes to file list refresh
    def refresh_file_list_on_tempo_change():
        # Re-populate the file list model to refresh BPM data
        file_list_model.setFiles([str(f) for f in file_manager._discovered_files])
    tempo_manager.tempoDataChanged.connect(refresh_file_list_on_tempo_change)
    
    # Connect file manager to batch operations
    file_manager.currentDirectoryChanged.connect(batch_operations.setCurrentDirectory)
    
    # Connect file manager to setlist manager (update root path when directory changes)
    def update_setlist_root(directory):
        if directory:
            setlist_manager.root_path = Path(directory)
            setlist_manager._load_setlists()
            setlist_manager.setlistsChanged.emit()
    file_manager.currentDirectoryChanged.connect(update_setlist_root)
    
    # Save directory changes to settings
    file_manager.currentDirectoryChanged.connect(settings_manager.setRootDir)
    
    # Add to recent folders when directory changes
    def add_to_recent_folders(directory):
        if directory:
            settings_manager.addRecentFolder(directory, 10)
    file_manager.currentDirectoryChanged.connect(add_to_recent_folders)
    
    # Connect annotation manager to annotations model
    def update_annotations_model(file_path):
        annotations = annotation_manager.getAnnotations()
        annotations_model.setAnnotations(annotations)
    annotation_manager.annotationsChanged.connect(update_annotations_model)
    
    # Connect fingerprint engine to file manager
    file_manager.currentDirectoryChanged.connect(fingerprint_engine.setCurrentDirectory)
    
    # Connect backup manager to file manager (update current folder and root path)
    file_manager.currentDirectoryChanged.connect(backup_manager.setCurrentFolder)
    def update_backup_root(directory):
        if directory:
            # Set root path for backup discovery (use parent if deep in hierarchy)
            root = Path(directory)
            # Try to find a reasonable root (go up a few levels if deep)
            while len(root.parts) > 3 and root.parent != root:
                root = root.parent
            backup_manager.setRootPath(str(root))
    file_manager.currentDirectoryChanged.connect(update_backup_root)
    
    # Set up audio loader for fingerprint engine
    def load_audio_for_fingerprinting(filepath: str):
        """Load audio samples for fingerprinting."""
        try:
            # Use waveform engine's audio loading capability
            from backend.waveform_engine import load_audio_data
            samples, sr = load_audio_data(Path(filepath))
            return samples, sr
        except Exception as e:
            print(f"Error loading audio for fingerprinting: {e}")
            return None, None

    fingerprint_engine.setAudioLoader(load_audio_for_fingerprinting)

    # Set initial volume from settings
    audio_engine.setVolume(settings_manager.getVolume())

    # Expose backend objects to QML before loading QML file
    ctx = engine.rootContext()
    ctx.setContextProperty("appViewModel", view_model)
    ctx.setContextProperty("settingsManager", settings_manager)
    ctx.setContextProperty("colorManager", color_manager)
    ctx.setContextProperty("audioEngine", audio_engine)
    ctx.setContextProperty("fileManager", file_manager)
    ctx.setContextProperty("tempoManager", tempo_manager)
    ctx.setContextProperty("fileListModel", file_list_model)
    ctx.setContextProperty("annotationsModel", annotations_model)
    ctx.setContextProperty("waveformEngine", waveform_engine)
    ctx.setContextProperty("annotationManager", annotation_manager)
    ctx.setContextProperty("clipManager", clip_manager)
    ctx.setContextProperty("folderNotesManager", folder_notes_manager)
    ctx.setContextProperty("batchOperations", batch_operations)
    ctx.setContextProperty("practiceStatistics", practice_statistics)
    ctx.setContextProperty("practiceGoals", practice_goals)
    ctx.setContextProperty("setlistManager", setlist_manager)
    ctx.setContextProperty("fingerprintEngine", fingerprint_engine)
    ctx.setContextProperty("backupManager", backup_manager)
    ctx.setContextProperty("exportManager", export_manager)
    ctx.setContextProperty("documentationManager", documentation_manager)
    ctx.setContextProperty("undoManager", undo_manager)
    ctx.setContextProperty("syncManager", sync_manager)
    ctx.setContextProperty("logViewer", log_viewer)

    # Load saved root directory on startup
    saved_root = settings_manager.getRootDir()
    if saved_root and Path(saved_root).exists():
        file_manager.setCurrentDirectory(saved_root)

    # Load QML file
    qml_file = Path(__file__).parent / "qml" / "main.qml"
    print(f"Loading QML file: {qml_file}")
    engine.load(QUrl.fromLocalFile(str(qml_file)))

    # Check if QML loaded successfully
    if not engine.rootObjects():
        print("Error: Failed to load QML file")
        return 1

    print("AudioBrowser QML Phase 7 - Application started successfully")
    sys.stdout.flush()  # Ensure message is printed immediately
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
