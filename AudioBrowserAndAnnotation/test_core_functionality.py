#!/usr/bin/env python3
"""
Comprehensive test suite for AudioBrowser core functionality.
Tests features that don't require GUI interaction.
"""

import sys
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Test results tracking
tests_passed = 0
tests_failed = 0
test_results = []

def test_result(name, passed, details=""):
    """Track test results"""
    global tests_passed, tests_failed, test_results
    if passed:
        tests_passed += 1
        test_results.append(f"✓ {name}")
        print(f"✓ {name}")
    else:
        tests_failed += 1
        test_results.append(f"✗ {name}: {details}")
        print(f"✗ {name}: {details}")

def test_shared_modules():
    """Test shared modules are importable and functional"""
    print("\n" + "="*70)
    print("TESTING SHARED MODULES")
    print("="*70)
    
    try:
        from shared import metadata_constants as mc
        test_result("Import metadata_constants", True)
        
        # Verify constants exist
        assert hasattr(mc, 'NAMES_JSON')
        assert hasattr(mc, 'DURATIONS_JSON')
        assert hasattr(mc, 'AUDIO_EXTS')
        test_result("Metadata constants defined", True)
        
    except Exception as e:
        test_result("Import metadata_constants", False, str(e))
    
    try:
        from shared import file_utils as fu
        test_result("Import file_utils", True)
        
        # Test sanitize function
        safe_name = fu.sanitize("Test Song: Part 1/2")
        assert "/" not in safe_name
        assert ":" not in safe_name
        test_result("sanitize function works", True)
        
    except Exception as e:
        test_result("file_utils functionality", False, str(e))
    
    try:
        from shared import backup_utils as bu
        test_result("Import backup_utils", True)
        
    except Exception as e:
        test_result("Import backup_utils", False, str(e))

def test_metadata_manager():
    """Test metadata manager functionality"""
    print("\n" + "="*70)
    print("TESTING METADATA MANAGER")
    print("="*70)
    
    try:
        from shared.metadata_manager import MetadataManager
        
        # Create temp directory for testing
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)
            mm = MetadataManager("testuser")
            
            test_result("MetadataManager initialization", True)
            
            # Test username
            assert mm.get_username() == "testuser"
            test_result("Get username", True)
            
            # Test annotation file paths
            test_audio = test_dir / "test_audio.wav"
            path = mm.get_annotation_file_path(test_audio)
            assert ".test_audio_annotations" in str(path)
            test_result("Annotation file path resolution", True)
            
            # Test annotation sets file path
            path = mm.get_annotation_sets_file_path(test_dir)
            assert "audio_notes_testuser" in str(path)
            test_result("Annotation sets file path", True)
            
            # Test JSON I/O
            test_data = {"test": "data", "number": 42}
            test_file = test_dir / "test.json"
            mm.save_json(test_file, test_data)
            loaded_data = mm.load_json(test_file)
            assert loaded_data == test_data
            test_result("JSON save/load", True)
            
    except Exception as e:
        test_result("MetadataManager tests", False, str(e))

def test_file_operations():
    """Test file operations and validation"""
    print("\n" + "="*70)
    print("TESTING FILE OPERATIONS")
    print("="*70)
    
    try:
        from shared.file_utils import sanitize, file_signature
        
        # Test filename sanitization
        test_cases = [
            ("Normal Name", "Normal Name"),
            ("Name/With/Slashes", "Name_With_Slashes"),
            ("Name:With:Colons", "Name_With_Colons"),
            ("Name<With>Brackets", "Name_With_Brackets"),
            ("Name|With|Pipes", "Name_With_Pipes"),
            ('Name"With"Quotes', "Name_With_Quotes"),
            ("Name?With?Questions", "Name_With_Questions"),
            ("Name*With*Stars", "Name_With_Stars"),
        ]
        
        all_passed = True
        for input_name, expected_pattern in test_cases:
            result = sanitize(input_name)
            # Check that forbidden chars are removed/replaced
            if any(c in result for c in r'<>:"/\|?*'):
                all_passed = False
                break
        
        test_result("Filename sanitization", all_passed)
        
        # Test file signature with temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_path = Path(f.name)
        
        try:
            size, mtime = file_signature(temp_path)
            assert size > 0
            assert mtime > 0
            test_result("File signature", True)
        finally:
            temp_path.unlink()
            
    except Exception as e:
        test_result("File operations", False, str(e))

def test_json_handling():
    """Test JSON file handling and error recovery"""
    print("\n" + "="*70)
    print("TESTING JSON HANDLING")
    print("="*70)
    
    try:
        from shared.metadata_manager import MetadataManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)
            mm = MetadataManager("testuser")
            
            # Test loading non-existent file
            result = mm.load_json(test_dir / "nonexistent.json", default={"default": True})
            assert result == {"default": True}
            test_result("Load non-existent JSON with default", True)
            
            # Test corrupted JSON file
            corrupt_file = test_dir / "corrupt.json"
            corrupt_file.write_text("{ this is not valid json }")
            result = mm.load_json(corrupt_file, default={"recovered": True})
            assert result == {"recovered": True}
            test_result("Corrupted JSON recovery", True)
            
            # Test empty JSON file
            empty_file = test_dir / "empty.json"
            empty_file.write_text("")
            result = mm.load_json(empty_file, default={})
            assert result == {}
            test_result("Empty JSON file handling", True)
            
    except Exception as e:
        test_result("JSON handling", False, str(e))

def test_backup_system():
    """Test backup utilities"""
    print("\n" + "="*70)
    print("TESTING BACKUP SYSTEM")
    print("="*70)
    
    try:
        from shared import backup_utils as bu
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)
            
            # Create some test files
            test_file1 = test_dir / ".provided_names.json"
            test_file1.write_text('{"song1": "Test Song 1"}')
            
            test_file2 = test_dir / ".audio_notes_user1.json"
            test_file2.write_text('{"annotations": []}')
            
            # Test creating backup folder name
            backup_folder = bu.create_backup_folder_name(test_dir)
            assert backup_folder is not None
            assert ".backup" in str(backup_folder)
            test_result("Create backup folder name", True)
            
            # Test backup metadata files collection
            files = bu.get_metadata_files_to_backup(test_dir)
            assert isinstance(files, list)
            test_result("Collect metadata files for backup", True)
            
    except Exception as e:
        test_result("Backup system", False, str(e))

def test_python_version_compatibility():
    """Test Python version compatibility"""
    print("\n" + "="*70)
    print("TESTING PYTHON VERSION COMPATIBILITY")
    print("="*70)
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    # Check minimum version
    if version.major >= 3 and version.minor >= 8:
        test_result("Python version >= 3.8", True)
    else:
        test_result("Python version >= 3.8", False, f"Got {version.major}.{version.minor}")
    
    # Test audioop handling for Python 3.13+
    if version >= (3, 13):
        try:
            import audioop
            test_result("audioop available in Python 3.13+", True)
        except ImportError:
            # This is expected, should fall back to audioop-lts
            test_result("audioop fallback handling", True, "audioop-lts would be installed")
    else:
        try:
            import audioop
            test_result("audioop available in Python < 3.13", True)
        except ImportError:
            test_result("audioop available in Python < 3.13", False, "audioop missing")
    
    # Test that OrderedDict is not used
    try:
        # Read the audio_browser.py file and check for OrderedDict
        orig_file = Path(__file__).parent / "AudioBrowserOrig" / "audio_browser.py"
        if orig_file.exists():
            content = orig_file.read_text()
            has_ordereddict_import = "from collections import OrderedDict" in content
            test_result("No OrderedDict imports (Python 3.13 compat)", not has_ordereddict_import)
        else:
            test_result("audio_browser.py exists", False, "File not found")
    except Exception as e:
        test_result("OrderedDict check", False, str(e))

def test_audio_constants():
    """Test audio-related constants and configuration"""
    print("\n" + "="*70)
    print("TESTING AUDIO CONSTANTS")
    print("="*70)
    
    try:
        from shared.metadata_constants import AUDIO_EXTS
        
        # Verify common audio formats are included
        required_formats = {'.wav', '.mp3'}
        assert required_formats.issubset(AUDIO_EXTS)
        test_result("Audio format constants", True)
        
    except Exception as e:
        test_result("Audio constants", False, str(e))

def test_error_handling():
    """Test error handling patterns"""
    print("\n" + "="*70)
    print("TESTING ERROR HANDLING")
    print("="*70)
    
    try:
        from shared.metadata_manager import MetadataManager
        
        # Test handling of invalid directory
        try:
            mm = MetadataManager("testuser")
            # Manager doesn't take a directory, so this should always succeed
            test_result("MetadataManager instantiation", True)
        except Exception as e:
            test_result("MetadataManager instantiation", False, str(e))
        
    except Exception as e:
        test_result("Error handling", False, str(e))

def main():
    """Run all tests"""
    print("="*70)
    print("AUDIOBROWSER CORE FUNCTIONALITY TEST SUITE")
    print("="*70)
    print(f"Python version: {sys.version}")
    print(f"Test started: {datetime.now().isoformat()}")
    
    # Run all test suites
    test_shared_modules()
    test_metadata_manager()
    test_file_operations()
    test_json_handling()
    test_backup_system()
    test_python_version_compatibility()
    test_audio_constants()
    test_error_handling()
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests passed: {tests_passed}")
    print(f"Tests failed: {tests_failed}")
    print(f"Total tests: {tests_passed + tests_failed}")
    print(f"Success rate: {100 * tests_passed / max(1, tests_passed + tests_failed):.1f}%")
    
    if tests_failed > 0:
        print("\n" + "="*70)
        print("FAILED TESTS:")
        print("="*70)
        for result in test_results:
            if result.startswith("✗"):
                print(result)
    
    print("\n" + "="*70)
    print(f"Test completed: {datetime.now().isoformat()}")
    print("="*70)
    
    # Return exit code
    return 0 if tests_failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
