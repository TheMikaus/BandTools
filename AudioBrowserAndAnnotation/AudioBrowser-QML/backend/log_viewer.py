#!/usr/bin/env python3
"""
Log Viewer Backend Module

Provides access to application logs for the AudioBrowser QML application.
"""

import os
import logging
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot


class LogViewer(QObject):
    """
    Log viewer for accessing application logs.
    
    Provides methods to read and manage log files.
    """
    
    # Signals
    logPathChanged = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """Initialize the log viewer."""
        super().__init__(parent)
        
        # Determine log file path
        self._log_file = Path(__file__).parent.parent / "audiobrowser.log"
        self._setup_logging()
    
    def _setup_logging(self):
        """Set up logging to file with enhanced formatting."""
        # Configure logging with more detailed format
        logging.basicConfig(
            level=logging.DEBUG,  # Changed to DEBUG for more detailed logs
            format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            handlers=[
                logging.FileHandler(self._log_file, mode='a', encoding='utf-8', errors='replace'),
            ],
            force=True
        )
        
        # Log startup message with version info
        logger = logging.getLogger(__name__)
        logger.info("=" * 80)
        logger.info("AudioBrowser QML application started")
        logger.info(f"Log file: {self._log_file.absolute()}")
        logger.info("=" * 80)
    
    @pyqtSlot(result=str)
    def getLogPath(self) -> str:
        """
        Get the path to the log file.
        
        Returns:
            Path to the log file
        """
        return str(self._log_file.absolute())
    
    @pyqtSlot(result=str)
    def getLogContents(self) -> str:
        """
        Get the contents of the log file.
        
        Returns:
            Log file contents
        """
        try:
            if self._log_file.exists():
                with open(self._log_file, 'r', encoding='utf-8', errors='replace') as f:
                    return f.read()
            return "No log file found."
        except Exception as e:
            return f"Error reading log file: {e}"
    
    @pyqtSlot(result=bool)
    def logFileExists(self) -> bool:
        """
        Check if the log file exists.
        
        Returns:
            True if the log file exists, False otherwise
        """
        return self._log_file.exists()
    
    @pyqtSlot()
    def clearLog(self) -> None:
        """Clear the log file."""
        try:
            if self._log_file.exists():
                self._log_file.unlink()
            self._setup_logging()
        except Exception as e:
            logging.error(f"Error clearing log file: {e}")
    
    @pyqtSlot()
    def openLogInSystemViewer(self) -> None:
        """Open the log file in the system's default text viewer."""
        try:
            import subprocess
            import sys
            
            log_path = str(self._log_file.absolute())
            
            if sys.platform == "win32":
                os.startfile(log_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", log_path])
            else:
                subprocess.run(["xdg-open", log_path])
        except Exception as e:
            logging.error(f"Error opening log file: {e}")
