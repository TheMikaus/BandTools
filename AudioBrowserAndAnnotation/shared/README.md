# Shared Modules for AudioBrowser Applications

This directory contains common functionality shared between AudioBrowserOrig and AudioBrowser-QML applications. By centralizing common code here, we avoid duplication and ensure that bug fixes and improvements benefit both applications.

## Overview

The shared modules package provides:

- **Metadata constants** - Common JSON file name constants
- **Backup utilities** - Metadata backup and restore functionality
- **File utilities** - Common file operations (sanitize, file signatures)
- **Audio workers** - Background audio processing workers (channel muting, etc.)

## Modules

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

## Usage in Applications

### AudioBrowserOrig

The original PyQt6 application imports and uses shared modules:

```python
# In audio_browser.py
from shared.metadata_constants import NAMES_JSON, AUDIO_EXTS
from shared.file_utils import sanitize, sanitize_library_name
from shared import backup_utils

# Use shared constants
names_file = practice_folder / NAMES_JSON

# Use shared functions
clean_name = sanitize(user_input)
backup_utils.create_metadata_backup_if_needed(practice_folder)
```

### AudioBrowser-QML

The QML-based application uses shared modules in backend classes:

```python
# In backend/backup_manager.py
from shared.metadata_constants import NAMES_JSON, TEMPO_JSON
from shared import backup_utils

class BackupManager(QObject):
    def backup_metadata_files(self, practice_folder, backup_folder):
        return backup_utils.backup_metadata_files(practice_folder, backup_folder)
```

## Testing

Run the test suite to verify shared modules work correctly:

```bash
cd AudioBrowserAndAnnotation
python test_shared_modules.py
```

The test suite validates:
- Metadata constants are defined correctly
- File utility functions work as expected
- Backup utilities can create, list, and restore backups
- Audio workers can be instantiated (if PyQt6 is available)

## Benefits

### Code Reuse
- **Before**: Each application had duplicate implementations of backup, sanitize, etc.
- **After**: Single implementation shared by both applications

### Maintainability
- **Before**: Bug fixes needed to be applied twice (once per application)
- **After**: Fix once in shared module, both applications benefit

### Consistency
- **Before**: Implementations could drift apart over time
- **After**: Guaranteed consistency in behavior

### Reduced Complexity
- **Before**: ~200 lines of duplicate code across applications
- **After**: Single source of truth, applications delegate to shared utilities

## Future Enhancements

Potential additional shared modules:

- **Audio processing utilities** - Common audio loading/saving functions
- **Waveform generation** - Shared waveform visualization logic
- **Fingerprinting** - Audio fingerprint generation and matching
- **Configuration management** - Shared settings/configuration handling
- **JSON utilities** - Common JSON load/save with error handling

## Version History

- **v1.0.0** - Initial creation with metadata constants, backup utilities, file utilities, and audio workers

## See Also

- [AudioBrowserOrig Documentation](../AudioBrowserOrig/docs/)
- [AudioBrowser-QML Documentation](../AudioBrowser-QML/docs/)
- [Main README](../README.md)
