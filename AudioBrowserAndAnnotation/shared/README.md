# Shared Modules for AudioBrowser Applications

This directory contains common functionality shared between AudioBrowserOrig and AudioBrowser-QML applications. By centralizing common code here, we avoid duplication and ensure that bug fixes and improvements benefit both applications.

## Overview

The shared modules package provides:

- **Metadata constants** - Common JSON file name constants
- **Metadata manager** - Centralized annotation and metadata file management (NEW)
- **Backup utilities** - Metadata backup and restore functionality
- **File utilities** - Common file operations (sanitize, file signatures)
- **Audio workers** - Background audio processing workers (channel muting, etc.)

## Modules

### `metadata_manager.py` ⭐ NEW

Centralized metadata management for annotation files with automatic backup support:

```python
from shared.metadata_manager import MetadataManager

# Initialize with username
manager = MetadataManager(username="user")

# Load annotation sets
sets_data = manager.load_annotation_sets(practice_folder)

# Save annotation sets (automatic backup)
manager.save_annotation_sets(practice_folder, sets_data)

# Migrate legacy annotations
manager.migrate_legacy_to_sets(practice_folder)

# Discover annotation files in directory
files = manager.discover_annotation_files(practice_folder)
```

Features:
- Consistent file path resolution across both applications
- Automatic backup creation before modifications
- Legacy format migration support
- Multi-user annotation support
- JSON I/O with error handling
- Annotation file discovery utilities

See [Metadata Manager Details](#metadata-manager-details) below for full API documentation.

### `metadata_constants.py`

Defines constants for metadata file names used across both applications:

```python
from shared.metadata_constants import (
    NAMES_JSON,           # ".provided_names.json"
    DURATIONS_JSON,       # ".duration_cache.json"
    WAVEFORM_JSON,        # ".waveform_cache.json"
    FINGERPRINTS_JSON,    # ".audio_fingerprints.json"
    TEMPO_JSON,           # ".tempo.json"
    # ... and more
    AUDIO_EXTS,          # {".wav", ".wave", ".mp3"}
)
```

### `backup_utils.py`

Common backup and restore functions for metadata files:

```python
from shared import backup_utils

# Create a timestamped backup folder
backup_folder = backup_utils.create_backup_folder_name(practice_folder)

# Get list of metadata files to backup
files = backup_utils.get_metadata_files_to_backup(practice_folder)

# Backup metadata files
count = backup_utils.backup_metadata_files(practice_folder, backup_folder)

# Check if backup is needed
if backup_utils.should_create_backup(practice_folder):
    backup_utils.create_metadata_backup_if_needed(practice_folder)

# Discover available backups
backups = backup_utils.discover_available_backups(root_path)

# Restore from backup
count = backup_utils.restore_metadata_from_backup(backup_folder, target_folder, root_path)
```

### `file_utils.py`

Common file utility functions:

```python
from shared.file_utils import sanitize, sanitize_library_name, file_signature

# Sanitize a filename (replace invalid chars with underscores)
clean_name = sanitize("song:name*with?invalid<chars")
# Result: "song_name_with_invalid_chars"

# Sanitize a library name (lowercase, spaces to underscores)
lib_name = sanitize_library_name("My Song Library")
# Result: "my_song_library"

# Get file signature (size, mtime)
sig = file_signature(Path("audio.wav"))
# Result: (12345, 1696875600) or (0, 0) if file doesn't exist
```

### `audio_workers.py`

Background audio processing workers that use PyQt6 signals:

```python
from shared.audio_workers import ChannelMutingWorker, find_ffmpeg, HAVE_PYDUB

# Check if pydub is available
if HAVE_PYDUB:
    # Create worker to mute channels
    worker = ChannelMutingWorker(
        audio_path="input.wav",
        left_enabled=True,    # Keep left channel
        right_enabled=False,  # Mute right channel
        temp_path="output.wav"
    )
    worker.finished.connect(on_finished)
    thread = QThread()
    worker.moveToThread(thread)
    thread.started.connect(worker.run)
    thread.start()

# Check FFmpeg availability
ffmpeg_path = find_ffmpeg()
```

## Metadata Manager Details

The `MetadataManager` class provides centralized annotation file management with the following features:

### Initialization

```python
manager = MetadataManager(username="user")  # Defaults to system username
manager.set_username("newuser")  # Change username
username = manager.get_username()  # Get current username
```

### Annotation Sets Operations

```python
# Load annotation sets
sets_data = manager.load_annotation_sets(directory, username=None)
# Returns dict with keys: 'version', 'sets', 'current_set_id', 'updated'

# Save annotation sets
success = manager.save_annotation_sets(directory, sets_data, username=None, create_backup=True)
# Returns True if successful, False otherwise
```

### Legacy Annotations

```python
# Load legacy per-file annotations
annotations = manager.load_legacy_annotations(audio_file_path)

# Save legacy annotations
success = manager.save_legacy_annotations(audio_file_path, annotations, create_backup=True)

# Migrate legacy to modern format
success = manager.migrate_legacy_to_sets(directory, username=None)
```

### File Path Resolution

```python
# Get annotation sets file path (user-specific)
path = manager.get_annotation_sets_file_path(directory, username=None)
# Returns Path like: /folder/.audio_notes_user.json

# Get legacy annotation file path (per-file)
path = manager.get_annotation_file_path(audio_file_path)
# Returns Path like: /folder/.song_annotations.json
```

### Discovery Utilities

```python
# Discover all annotation files in a directory
files = manager.discover_annotation_files(directory)
# Returns list of (username, file_path) tuples

# Get total annotation count
count = manager.get_annotation_count(directory, username=None)
```

### JSON I/O

```python
# Load JSON with error handling
data = manager.load_json(path, default=None)

# Save JSON with automatic backup
success = manager.save_json(path, data, create_backup=True)
```

### Backup Control

```python
# Enable/disable automatic backups
manager.set_backup_enabled(True)  # Default
manager.set_backup_enabled(False)  # Disable for batch operations
```

## Usage in Applications

### AudioBrowserOrig

The original PyQt6 application uses the metadata manager for annotation persistence:

```python
# In audio_browser.py
from shared.metadata_manager import MetadataManager

class AudioBrowser(QMainWindow):
    def __init__(self):
        # ... other initialization ...
        self._metadata_manager = MetadataManager(username=self._resolve_user_display_name())
    
    def _load_notes(self):
        # Use shared manager for loading and migration
        data = self._metadata_manager.load_annotation_sets(
            self.current_practice_folder,
            username=self._resolve_user_display_name()
        )
        # Process loaded data...
    
    def _save_notes(self):
        # Use shared manager for saving with automatic backup
        success = self._metadata_manager.save_annotation_sets(
            self.current_practice_folder,
            payload,
            username=self._resolve_user_display_name(),
            create_backup=False  # Manual backup already done
        )
```

### AudioBrowser-QML

The QML-based application uses the metadata manager in backend classes:

```python
# In backend/annotation_manager.py
from shared.metadata_manager import MetadataManager

class AnnotationManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._metadata_manager = MetadataManager(username=self._current_user)
    
    def _load_annotation_sets(self):
        data = self._metadata_manager.load_annotation_sets(
            self._current_directory,
            username=self._current_user
        )
        # Process loaded data...
    
    def _save_annotation_sets(self):
        success = self._metadata_manager.save_annotation_sets(
            self._current_directory,
            data,
            username=self._current_user,
            create_backup=True
        )
```

## Testing

Run the test suite to verify shared modules work correctly:

```bash
cd AudioBrowserAndAnnotation
python test_shared_modules.py      # Test original shared modules
python test_metadata_manager.py    # Test metadata manager (NEW)
```

The test suites validate:
- Metadata constants are defined correctly
- File utility functions work as expected
- Backup utilities can create, list, and restore backups
- Audio workers can be instantiated (if PyQt6 is available)
- **Metadata manager handles annotation I/O correctly (NEW)**
- **Metadata manager creates backups automatically (NEW)**
- **Legacy migration works correctly (NEW)**

## Benefits

### Code Reuse
- **Before**: Each application had duplicate implementations of backup, sanitize, annotation I/O, etc.
- **After**: Single implementation shared by both applications

### Maintainability
- **Before**: Bug fixes needed to be applied twice (once per application)
- **After**: Fix once in shared module, both applications benefit

### Consistency
- **Before**: Implementations could drift apart over time
- **After**: Guaranteed consistency in behavior, especially for critical annotation data

### Reduced Complexity
- **Before**: ~400 lines of duplicate code across applications
- **After**: Single source of truth, applications delegate to shared utilities

### Safety
- **NEW**: Automatic backup before modifications ensures data safety
- **NEW**: Consistent error handling across both applications
- **NEW**: Validated migration paths from legacy formats

## Future Enhancements

Potential additional shared modules:

- **Audio processing utilities** - Common audio loading/saving functions
- **Waveform generation** - Shared waveform visualization logic
- **Fingerprinting** - Audio fingerprint generation and matching
- **Configuration management** - Shared settings/preferences handling

## Version History

- **v1.1.0** (Current) - Added MetadataManager for centralized annotation management
- **v1.0.0** - Initial creation with metadata constants, backup utilities, file utilities, and audio workers

## See Also

- [AudioBrowserOrig Documentation](../AudioBrowserOrig/docs/)
- [AudioBrowser-QML Documentation](../AudioBrowser-QML/docs/)
- [Main README](../README.md)
- [Shared Modules Migration Summary](../SHARED_MODULES_MIGRATION.md)
