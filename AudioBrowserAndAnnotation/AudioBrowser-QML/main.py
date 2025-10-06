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
    except ImportError:
        print(f"Installing {pip_name}...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
        __import__(mod_name)
        return True

# Install required dependencies
_ensure_import("PyQt6.QtCore", "PyQt6")
_ensure_import("PyQt6.QtGui", "PyQt6")
_ensure_import("PyQt6.QtWidgets", "PyQt6")
_ensure_import("PyQt6.QtQuick", "PyQt6")
_ensure_import("PyQt6.QtQml", "PyQt6")

from PyQt6.QtCore import QUrl, QObject, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine

# Import backend modules
from backend.settings_manager import SettingsManager
from backend.color_manager import ColorManager


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
    app.setApplicationVersion("0.1.0")
    
    # Create QML engine
    engine = QQmlApplicationEngine()
    
    # Create backend managers
    settings_manager = SettingsManager()
    color_manager = ColorManager(theme=settings_manager.getTheme())
    
    # Create and expose view model to QML
    view_model = ApplicationViewModel()
    
    # Expose backend objects to QML via context properties
    engine.rootContext().setContextProperty("appViewModel", view_model)
    engine.rootContext().setContextProperty("settingsManager", settings_manager)
    engine.rootContext().setContextProperty("colorManager", color_manager)
    
    # Connect settings to color manager
    settings_manager.themeChanged.connect(color_manager.setTheme)
    
    # Load QML file
    qml_file = Path(__file__).parent / "qml" / "main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    
    # Check if QML loaded successfully
    if not engine.rootObjects():
        print("Error: Failed to load QML file")
        return 1
    
    print("AudioBrowser QML Phase 0 - Application started successfully")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
