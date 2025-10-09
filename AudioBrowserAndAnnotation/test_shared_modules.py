"""
Test Shared Modules

Tests the shared modules used by both AudioBrowser applications.
"""

import sys
import tempfile
from pathlib import Path

# Add shared module to path
sys.path.insert(0, str(Path(__file__).parent))


def test_metadata_constants():
    """Test metadata constants module."""
    print("\nTesting Metadata Constants...")
    
    from shared.metadata_constants import (
        NAMES_JSON, DURATIONS_JSON, WAVEFORM_JSON, FINGERPRINTS_JSON,
        TEMPO_JSON, TAKES_METADATA_JSON, PRACTICE_GOALS_JSON, SETLISTS_JSON,
        CLIPS_JSON, RESERVED_JSON, AUDIO_EXTS
    )
    
    # Test that constants are strings
    assert isinstance(NAMES_JSON, str), "NAMES_JSON should be a string"
    assert NAMES_JSON == ".provided_names.json", f"NAMES_JSON should be '.provided_names.json', got {NAMES_JSON}"
    
    # Test that RESERVED_JSON is a set
    assert isinstance(RESERVED_JSON, set), "RESERVED_JSON should be a set"
    assert NAMES_JSON in RESERVED_JSON, "NAMES_JSON should be in RESERVED_JSON"
    
    # Test AUDIO_EXTS
    assert isinstance(AUDIO_EXTS, set), "AUDIO_EXTS should be a set"
    assert ".wav" in AUDIO_EXTS, ".wav should be in AUDIO_EXTS"
    
    print("   ✓ Metadata constants module works correctly")
    return True


def test_file_utils():
    """Test file utilities module."""
    print("\nTesting File Utilities...")
    
    from shared.file_utils import sanitize, sanitize_library_name, file_signature
    
    # Test sanitize function
    result = sanitize("test:file*name")
    assert ":" not in result and "*" not in result, f"sanitize should remove invalid chars, got {result}"
    
    # Test sanitize_library_name
    result = sanitize_library_name("Test Library Name")
    assert result == "test_library_name", f"sanitize_library_name should lowercase and replace spaces, got {result}"
    
    # Test file_signature with non-existent file
    sig = file_signature(Path("/nonexistent/file.txt"))
    assert sig == (0, 0), f"file_signature for non-existent file should be (0, 0), got {sig}"
    
    print("   ✓ File utilities module works correctly")
    return True


def test_backup_utils():
    """Test backup utilities module."""
    print("\nTesting Backup Utilities...")
    
    from shared.backup_utils import (
        create_backup_folder_name,
        get_metadata_files_to_backup,
        should_create_backup,
        backup_metadata_files,
        create_metadata_backup_if_needed,
    )
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        practice_folder = Path(tmpdir) / "practice"
        practice_folder.mkdir()
        
        # Test create_backup_folder_name
        backup_folder = create_backup_folder_name(practice_folder)
        assert backup_folder.parent.name == ".backup", "Backup folder should be in .backup directory"
        assert "-" in backup_folder.name, "Backup folder name should contain date"
        
        # Test get_metadata_files_to_backup with no files
        files = get_metadata_files_to_backup(practice_folder)
        assert len(files) == 0, f"Should have no metadata files, got {len(files)}"
        
        # Test should_create_backup
        should_backup = should_create_backup(practice_folder)
        assert not should_backup, "Should not create backup when no metadata files exist"
        
        # Create a metadata file
        metadata_file = practice_folder / ".provided_names.json"
        metadata_file.write_text('{"test": "data"}')
        
        # Test get_metadata_files_to_backup with one file
        files = get_metadata_files_to_backup(practice_folder)
        assert len(files) == 1, f"Should have 1 metadata file, got {len(files)}"
        
        # Test should_create_backup
        should_backup = should_create_backup(practice_folder)
        assert should_backup, "Should create backup when metadata files exist"
        
        # Test backup_metadata_files
        backup_folder = practice_folder / ".backup" / "test"
        num_backed_up = backup_metadata_files(practice_folder, backup_folder)
        assert num_backed_up == 1, f"Should have backed up 1 file, got {num_backed_up}"
        assert (backup_folder / ".provided_names.json").exists(), "Backup file should exist"
        
        # Test create_metadata_backup_if_needed
        backup_path = create_metadata_backup_if_needed(practice_folder)
        assert backup_path is not None, "Should create backup"
        assert backup_path.exists(), "Backup folder should exist"
    
    print("   ✓ Backup utilities module works correctly")
    return True


def test_audio_workers():
    """Test audio workers module."""
    print("\nTesting Audio Workers...")
    
    try:
        from shared.audio_workers import ChannelMutingWorker, find_ffmpeg, HAVE_PYDUB
    except ImportError as e:
        if "PyQt6" in str(e):
            print("   ⊘ Skipping audio_workers test (PyQt6 not available in test environment)")
            return True
        raise
    
    # Test find_ffmpeg
    ffmpeg_path = find_ffmpeg()
    print(f"   - FFmpeg path: {ffmpeg_path or 'Not found'}")
    
    # Test ChannelMutingWorker class exists and can be instantiated
    worker = ChannelMutingWorker("/path/to/audio.wav", True, False, "/tmp/output.wav")
    assert hasattr(worker, 'run'), "ChannelMutingWorker should have run method"
    assert hasattr(worker, 'finished'), "ChannelMutingWorker should have finished signal"
    
    print(f"   - pydub available: {HAVE_PYDUB}")
    print("   ✓ Audio workers module works correctly")
    return True


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Testing Shared Modules")
    print("=" * 60)
    
    tests = [
        test_metadata_constants,
        test_file_utils,
        test_backup_utils,
        test_audio_workers,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"   ✗ Test failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
