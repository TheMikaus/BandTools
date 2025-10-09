"""
Backup Manager Module

Handles metadata file backups for AudioBrowser QML.
Creates timestamped backups before modifications and supports restore functionality.
"""

import sys
from pathlib import Path
from typing import List, Tuple, Dict, Optional

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

# Add parent directory to path to import shared modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.metadata_constants import (
    NAMES_JSON,
    DURATIONS_JSON,
    WAVEFORM_JSON,
    FINGERPRINTS_JSON,
    TEMPO_JSON,
    TAKES_METADATA_JSON,
    PRACTICE_GOALS_JSON,
    SETLISTS_JSON,
    CLIPS_JSON,
)
from shared import backup_utils


class BackupManager(QObject):
    """
    Manages metadata file backups for AudioBrowser.
    
    Features:
    - Automatic backup creation before file modifications
    - Timestamped backup folders (.backup/YYYY-MM-DD-###)
    - Discovery of available backups across practice folders
    - Restore from backup with preview
    """
    
    # Signals
    backupCreated = pyqtSignal(str)  # backup_folder_path
    backupRestored = pyqtSignal(int)  # files_restored_count
    backupError = pyqtSignal(str)  # error_message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_folder = None
        self._root_path = None
    
    @pyqtSlot(str)
    def setCurrentFolder(self, folder_path: str):
        """Set the current practice folder."""
        self._current_folder = Path(folder_path) if folder_path else None
    
    @pyqtSlot(str)
    def setRootPath(self, root_path: str):
        """Set the root band practice directory."""
        self._root_path = Path(root_path) if root_path else None
    
    def create_backup_folder_name(self, practice_folder: Path) -> Path:
        """
        Create a unique backup folder name with format .backup/YYYY-MM-DD-###
        
        Args:
            practice_folder: Practice folder where the backup will be created
            
        Returns:
            Path to the backup folder (not yet created)
        """
        return backup_utils.create_backup_folder_name(practice_folder)
    
    def get_metadata_files_to_backup(self, practice_folder: Path) -> List[Path]:
        """
        Get list of metadata files that exist in the practice folder.
        
        See shared.backup_utils.get_metadata_files_to_backup for details.
        
        Args:
            practice_folder: Directory to scan for metadata files
            
        Returns:
            List of Path objects for existing metadata files
        """
        return backup_utils.get_metadata_files_to_backup(practice_folder)
    
    def backup_metadata_files(self, practice_folder: Path, backup_base_folder: Path) -> int:
        """
        Backup metadata files from practice_folder to backup_base_folder.
        
        Args:
            practice_folder: Source folder containing metadata files
            backup_base_folder: Destination backup folder
            
        Returns:
            Number of files backed up
        """
        return backup_utils.backup_metadata_files(practice_folder, backup_base_folder)
    
    def should_create_backup(self, practice_folder: Path) -> bool:
        """
        Determine if a backup should be created for this practice folder.
        Only create backup if there are metadata files that could change.
        
        Args:
            practice_folder: Practice folder to check
            
        Returns:
            True if backup should be created
        """
        return backup_utils.should_create_backup(practice_folder)
    
    @pyqtSlot(str, result=str)
    def createBackup(self, folder_path: str) -> str:
        """
        Create a backup of metadata files for the given folder.
        
        Args:
            folder_path: Path to the practice folder
            
        Returns:
            Path to created backup folder, or empty string if no backup created
        """
        try:
            practice_folder = Path(folder_path)
            
            if not self.should_create_backup(practice_folder):
                return ""
            
            backup_folder = self.create_backup_folder_name(practice_folder)
            backed_up_count = self.backup_metadata_files(practice_folder, backup_folder)
            
            if backed_up_count > 0:
                self.backupCreated.emit(str(backup_folder))
                return str(backup_folder)
            else:
                # Clean up empty backup folder
                try:
                    backup_folder.rmdir()
                    # Also try to remove parent .backup directory if it's empty
                    backup_folder.parent.rmdir()
                except Exception:
                    pass
                return ""
                
        except Exception as e:
            error_msg = f"Failed to create backup: {str(e)}"
            self.backupError.emit(error_msg)
            return ""
    
    @pyqtSlot(str, result=list)
    def discoverBackups(self, root_path: str) -> List[dict]:
        """
        Discover all available backup folders in all practice folders.
        
        Args:
            root_path: Root band practice directory to search for .backup folders
            
        Returns:
            List of dictionaries with backup info (path, displayName, date)
        """
        try:
            root = Path(root_path)
            backups = []
            
            # Search for .backup directories recursively
            for backup_dir in root.rglob(".backup"):
                if backup_dir.is_dir():
                    # Look for dated backup folders within each .backup directory
                    for backup_folder in backup_dir.iterdir():
                        if backup_folder.is_dir():
                            try:
                                # Parse folder name format: YYYY-MM-DD-###
                                folder_name = backup_folder.name
                                date_part = folder_name.rsplit('-', 1)[0]  # Remove counter
                                date_obj = datetime.strptime(date_part, "%Y-%m-%d")
                                
                                # Get relative path from root for display
                                practice_folder = backup_dir.parent
                                rel_practice = practice_folder.relative_to(root)
                                practice_name = str(rel_practice) if str(rel_practice) != "." else "Root"
                                
                                # Create display name with date and practice folder
                                display_name = f"{date_obj.strftime('%A, %B %d, %Y')} ({folder_name}) - {practice_name}"
                                
                                backups.append({
                                    'path': str(backup_folder),
                                    'displayName': display_name,
                                    'date': date_obj.strftime("%Y-%m-%d"),
                                    'practiceFolder': str(practice_folder)
                                })
                                
                            except (ValueError, IndexError):
                                # If folder doesn't match expected format, include it anyway
                                practice_folder = backup_dir.parent
                                rel_practice = practice_folder.relative_to(root)
                                practice_name = str(rel_practice) if str(rel_practice) != "." else "Root"
                                display_name = f"{backup_folder.name} - {practice_name}"
                                
                                backups.append({
                                    'path': str(backup_folder),
                                    'displayName': display_name,
                                    'date': '',
                                    'practiceFolder': str(practice_folder)
                                })
            
            # Sort by folder name (includes timestamp) in descending order
            backups.sort(key=lambda x: Path(x['path']).name, reverse=True)
            return backups
            
        except Exception as e:
            error_msg = f"Failed to discover backups: {str(e)}"
            self.backupError.emit(error_msg)
            return []
    
    @pyqtSlot(str, result=list)
    def getBackupContents(self, backup_folder_path: str) -> List[str]:
        """
        Get the list of files in a backup folder.
        
        Args:
            backup_folder_path: Path to specific backup folder
            
        Returns:
            List of file names in the backup
        """
        try:
            backup_folder = Path(backup_folder_path)
            
            if not backup_folder.exists():
                return []
            
            # Get all JSON files in the backup folder
            files = []
            for backup_file in backup_folder.glob("*.json"):
                if backup_file.is_file():
                    files.append(backup_file.name)
            
            return sorted(files)
            
        except Exception as e:
            error_msg = f"Failed to get backup contents: {str(e)}"
            self.backupError.emit(error_msg)
            return []
    
    @pyqtSlot(str, str, result=int)
    def restoreBackup(self, backup_folder_path: str, target_folder_path: str) -> int:
        """
        Restore metadata files from a backup folder to the target practice folder.
        
        Args:
            backup_folder_path: Path to the backup folder containing the files
            target_folder_path: Practice folder where files should be restored
            
        Returns:
            Number of files successfully restored
        """
        try:
            backup_folder = Path(backup_folder_path)
            target_folder = Path(target_folder_path)
            
            if not backup_folder.exists():
                self.backupError.emit(f"Backup folder not found: {backup_folder_path}")
                return 0
            
            restored_count = 0
            # Copy all JSON files from backup to target folder
            for backup_file in backup_folder.glob("*.json"):
                try:
                    target_file = target_folder / backup_file.name
                    target_file.write_bytes(backup_file.read_bytes())
                    restored_count += 1
                    print(f"Restored: {backup_file.name}")
                except Exception as e:
                    print(f"Warning: Failed to restore {backup_file.name}: {e}")
            
            if restored_count > 0:
                self.backupRestored.emit(restored_count)
            
            return restored_count
            
        except Exception as e:
            error_msg = f"Failed to restore backup: {str(e)}"
            self.backupError.emit(error_msg)
            return 0
