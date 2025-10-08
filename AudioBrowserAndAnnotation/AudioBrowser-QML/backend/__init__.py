"""
AudioBrowser QML Backend Package

This package contains the Python backend modules for the AudioBrowser QML application.
Backend modules handle business logic, data management, and system integration while
QML handles the UI presentation.
"""

__version__ = "0.14.0"  # Phase 14 complete (96% feature parity - Undo/Redo)

# Export main backend classes
from .fingerprint_engine import FingerprintEngine
from .backup_manager import BackupManager
