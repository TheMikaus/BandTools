"""
Backup Utilities

Common backup-related functions used across AudioBrowser applications.
Handles metadata file backups with timestamped folders.
"""

import getpass
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Tuple

from .metadata_constants import (
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


def create_backup_folder_name(practice_folder: Path) -> Path:
    """
    Create a unique backup folder name with format .backup/YYYY-MM-DD-###
    
    Backups are created in each practice folder under .backup/ directory.
    The format ensures chronological ordering and prevents conflicts when
    multiple backups are created on the same day.
    
    Args:
        practice_folder: Practice folder where the backup will be created
        
    Returns:
        Path to the backup folder (not yet created)
    """
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    backups_dir = practice_folder / ".backup"
    
    # Find the next available number for today
    counter = 1
    while True:
        backup_folder = backups_dir / f"{date_str}-{counter:03d}"
        if not backup_folder.exists():
            return backup_folder
        counter += 1


def get_metadata_files_to_backup(practice_folder: Path) -> List[Path]:
    """
    Get list of metadata files that exist in the practice folder.
    
    This includes:
    - .provided_names.json (file naming data)
    - .duration_cache.json (playback duration cache)
    - .waveforms/.waveform_cache.json (waveform visualization cache)
    - .audio_fingerprints.json (audio fingerprint data)
    - .tempo.json (tempo/BPM data)
    - .takes_metadata.json (best/partial take indicators)
    - .practice_goals.json (practice goals)
    - .setlists.json (setlist data)
    - .clips.json (clip definitions)
    - .audio_notes_<username>.json (user-specific annotation data)
    
    Args:
        practice_folder: Directory to scan for metadata files
        
    Returns:
        List of Path objects for existing metadata files
    """
    # Skip backup directories entirely
    if practice_folder.name in ['.backup', '.backups']:
        return []
    
    metadata_files = []
    
    # List of all possible metadata files
    possible_files = [
        practice_folder / NAMES_JSON,
        practice_folder / DURATIONS_JSON,
        practice_folder / ".waveforms" / WAVEFORM_JSON,  # Waveform cache in .waveforms subdirectory
        practice_folder / FINGERPRINTS_JSON,
        practice_folder / TEMPO_JSON,
        practice_folder / TAKES_METADATA_JSON,
        practice_folder / PRACTICE_GOALS_JSON,
        practice_folder / SETLISTS_JSON,
        practice_folder / CLIPS_JSON,
    ]
    
    # Add user-specific annotation files
    username = getpass.getuser()
    user_notes_file = practice_folder / f".audio_notes_{username}.json"
    possible_files.append(user_notes_file)
    
    # Also check for any other user-specific annotation files
    for json_file in practice_folder.glob(".audio_notes_*.json"):
        if json_file not in possible_files:
            possible_files.append(json_file)
    
    # Only include files that actually exist and are not in backup directories
    for file_path in possible_files:
        if file_path.exists() and file_path.is_file():
            # Make sure the file is not in a backup directory
            if not any(part in ['.backup', '.backups'] for part in file_path.parts):
                metadata_files.append(file_path)
    
    return metadata_files


def should_create_backup(practice_folder: Path) -> bool:
    """
    Determine if a backup should be created for this practice folder.
    Only create backup if there are metadata files that could change.
    
    Args:
        practice_folder: Practice folder to check
        
    Returns:
        True if backup should be created
    """
    return len(get_metadata_files_to_backup(practice_folder)) > 0


def backup_metadata_files(practice_folder: Path, backup_base_folder: Path) -> int:
    """
    Backup metadata files from practice_folder to backup_base_folder.
    
    Args:
        practice_folder: Source directory containing metadata files
        backup_base_folder: Destination backup directory
        
    Returns:
        Number of files successfully backed up
    """
    metadata_files = get_metadata_files_to_backup(practice_folder)
    
    if not metadata_files:
        return 0  # No files to backup
    
    # Create the backup directory
    backup_base_folder.mkdir(parents=True, exist_ok=True)
    
    backed_up_count = 0
    for metadata_file in metadata_files:
        try:
            backup_file_path = backup_base_folder / metadata_file.name
            # Copy the file
            backup_file_path.write_bytes(metadata_file.read_bytes())
            backed_up_count += 1
        except Exception as e:
            print(f"Warning: Failed to backup {metadata_file}: {e}")
    
    return backed_up_count


def create_metadata_backup_if_needed(practice_folder: Path) -> Optional[Path]:
    """
    Create a backup of metadata files if needed.
    
    This function implements the main backup logic:
    1. Check if there are metadata files that could change
    2. Create a timestamped backup folder if needed
    3. Copy all metadata files to the backup folder
    
    Args:
        practice_folder: Practice folder to backup
        
    Returns:
        Path to the created backup folder, or None if no backup was needed
    """
    if not should_create_backup(practice_folder):
        return None
    
    backup_folder = create_backup_folder_name(practice_folder)
    num_backed_up = backup_metadata_files(practice_folder, backup_folder)
    
    if num_backed_up > 0:
        return backup_folder
    
    return None


def discover_available_backups(root_path: Path) -> List[Tuple[Path, str]]:
    """
    Discover all available backup folders under the root path.
    
    Searches for .backup directories in all subdirectories and returns
    a list of backup folders with their display names.
    
    Args:
        root_path: Root directory to search for backups
        
    Returns:
        List of tuples (backup_folder_path, display_name)
    """
    backups = []
    
    try:
        for backup_dir in root_path.rglob(".backup"):
            if backup_dir.is_dir():
                # Find all dated backup folders
                for backup_folder in backup_dir.iterdir():
                    if backup_folder.is_dir() and backup_folder.name[0].isdigit():
                        # Create display name with practice folder and date
                        practice_folder = backup_dir.parent
                        relative_path = practice_folder.relative_to(root_path)
                        display_name = f"{relative_path} - {backup_folder.name}"
                        backups.append((backup_folder, display_name))
    except Exception as e:
        print(f"Error discovering backups: {e}")
    
    # Sort by date (newest first)
    backups.sort(key=lambda x: x[0].name, reverse=True)
    
    return backups


def get_backup_contents(backup_folder: Path, root_path: Path) -> Dict[Path, List[Path]]:
    """
    Get the contents of a backup folder organized by practice folder.
    
    Args:
        backup_folder: Path to the backup folder
        root_path: Root directory for relative path calculation
        
    Returns:
        Dictionary mapping practice folders to lists of backed up files
    """
    contents = {}
    
    try:
        # The practice folder is the parent of .backup
        practice_folder = backup_folder.parent.parent
        
        # List all files in the backup folder
        backed_up_files = []
        for file_path in backup_folder.iterdir():
            if file_path.is_file():
                backed_up_files.append(file_path)
        
        if backed_up_files:
            contents[practice_folder] = backed_up_files
    except Exception as e:
        print(f"Error reading backup contents: {e}")
    
    return contents


def restore_metadata_from_backup(backup_folder: Path, target_practice_folder: Path, root_path: Path) -> int:
    """
    Restore metadata files from a backup folder to the target practice folder.
    
    Args:
        backup_folder: Path to the backup folder
        target_practice_folder: Destination practice folder
        root_path: Root directory (for logging/display purposes)
        
    Returns:
        Number of files successfully restored
    """
    restored_count = 0
    
    try:
        # List all files in the backup folder
        for backup_file in backup_folder.iterdir():
            if backup_file.is_file():
                # Restore to target practice folder
                target_file = target_practice_folder / backup_file.name
                try:
                    target_file.write_bytes(backup_file.read_bytes())
                    restored_count += 1
                except Exception as e:
                    print(f"Warning: Failed to restore {backup_file.name}: {e}")
    except Exception as e:
        print(f"Error restoring from backup: {e}")
    
    return restored_count
