#!/usr/bin/env python3
"""
Test for Google Drive Sync Backend Module

Tests basic functionality of the GDriveSync class without requiring
actual Google Drive credentials or PyQt6.
"""

import sys
from pathlib import Path

def test_module_structure():
    """Test that the module has expected structure."""
    print("Testing gdrive_sync module structure...")
    
    # Test module can be imported
    try:
        from backend import gdrive_sync
        print("✓ Module imports successfully")
    except ImportError as e:
        print(f"✗ Failed to import module: {e}")
        return False
    
    # Test required classes exist
    required_classes = ['SyncHistory', 'SyncRules', 'SyncVersion', 'GDriveSync']
    for class_name in required_classes:
        if hasattr(gdrive_sync, class_name):
            print(f"✓ Class '{class_name}' exists")
        else:
            print(f"✗ Class '{class_name}' not found")
            return False
    
    # Test GDRIVE_AVAILABLE flag exists
    if hasattr(gdrive_sync, 'GDRIVE_AVAILABLE'):
        print(f"✓ GDRIVE_AVAILABLE flag: {gdrive_sync.GDRIVE_AVAILABLE}")
    else:
        print("✗ GDRIVE_AVAILABLE flag not found")
        return False
    
    return True

def test_sync_classes():
    """Test helper classes."""
    print("\nTesting helper classes...")
    
    from backend.gdrive_sync import SyncHistory, SyncRules, SyncVersion
    
    # Test SyncHistory
    try:
        history = SyncHistory()
        history.add_entry('upload', 5, 'testuser', details='Test sync')
        entries = history.get_recent_entries(1)
        assert len(entries) == 1
        assert entries[0]['operation'] == 'upload'
        assert entries[0]['user'] == 'testuser'
        print("✓ SyncHistory works correctly")
    except Exception as e:
        print(f"✗ SyncHistory failed: {e}")
        return False
    
    # Test SyncRules
    try:
        rules = SyncRules(max_file_size_mb=10, sync_audio_files=True)
        assert rules.max_file_size_mb == 10
        assert rules.sync_audio_files == True
        
        # Test should_sync_file
        assert rules.should_sync_file(Path('test.mp3'), 5 * 1024 * 1024) == True
        assert rules.should_sync_file(Path('test.mp3'), 15 * 1024 * 1024) == False
        print("✓ SyncRules works correctly")
    except Exception as e:
        print(f"✗ SyncRules failed: {e}")
        return False
    
    # Test SyncVersion
    try:
        version = SyncVersion(version=1)
        version.add_operation('add', 'test.mp3')
        assert version.version == 1
        assert len(version.operations) == 1
        print("✓ SyncVersion works correctly")
    except Exception as e:
        print(f"✗ SyncVersion failed: {e}")
        return False
    
    return True

def test_utility_functions():
    """Test utility functions."""
    print("\nTesting utility functions...")
    
    from backend.gdrive_sync import should_sync_file, ANNOTATION_PATTERNS
    
    # Test should_sync_file
    test_cases = [
        ('test.mp3', True),
        ('test.wav', True),
        ('.audio_notes_user.json', True),
        ('.provided_names.json', True),
        ('.hidden_file', False),
        ('document.pdf', False),
    ]
    
    for filename, expected in test_cases:
        result = should_sync_file(filename)
        if result == expected:
            print(f"✓ should_sync_file('{filename}') = {result}")
        else:
            print(f"✗ should_sync_file('{filename}') expected {expected}, got {result}")
            return False
    
    return True

def test_gdrive_sync_class():
    """Test GDriveSync class basic functionality without PyQt6."""
    print("\nTesting GDriveSync class...")
    
    # We can't fully test GDriveSync without PyQt6, but we can check it exists
    # and has expected methods
    from backend.gdrive_sync import GDriveSync
    
    expected_methods = [
        'authenticate', 'isAvailable', 'isAuthenticated', 'getCurrentUser',
        'select_remote_folder', 'performSync', 'upload_file', 'download_file'
    ]
    
    for method_name in expected_methods:
        if hasattr(GDriveSync, method_name):
            print(f"✓ Method '{method_name}' exists")
        else:
            print(f"✗ Method '{method_name}' not found")
            return False
    
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("Google Drive Sync Backend Tests")
    print("=" * 60)
    
    tests = [
        test_module_structure,
        test_sync_classes,
        test_utility_functions,
        test_gdrive_sync_class,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n✗ Test {test_func.__name__} raised exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
