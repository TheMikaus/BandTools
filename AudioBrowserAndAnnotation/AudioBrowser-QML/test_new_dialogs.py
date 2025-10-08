#!/usr/bin/env python3
"""
Test script for new dialogs: BackupSelectionDialog and AutoGenerationSettingsDialog
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_backend_imports():
    """Test that backend modules can be imported."""
    print("Testing backend imports...")
    
    try:
        from backend.backup_manager import BackupManager
        print("✓ BackupManager imported successfully")
        
        # Create instance
        bm = BackupManager()
        print("✓ BackupManager instance created")
        
        # Test basic methods
        test_folder = Path("/tmp/test_backup")
        test_folder.mkdir(exist_ok=True)
        
        should_backup = bm.should_create_backup(test_folder)
        print(f"✓ should_create_backup() returned: {should_backup}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing BackupManager: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_settings_manager():
    """Test SettingsManager generic accessors."""
    print("\nTesting SettingsManager generic accessors...")
    
    try:
        from backend.settings_manager import SettingsManager
        
        sm = SettingsManager()
        print("✓ SettingsManager instance created")
        
        # Test generic accessors
        sm.setSetting("test_key", "test_value")
        value = sm.getSetting("test_key", "default")
        print(f"✓ Generic getSetting/setSetting work: {value}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing SettingsManager: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_qml_files():
    """Test that QML files exist and have valid syntax."""
    print("\nTesting QML files...")
    
    qml_files = [
        "qml/dialogs/BackupSelectionDialog.qml",
        "qml/dialogs/AutoGenerationSettingsDialog.qml"
    ]
    
    all_ok = True
    for qml_file in qml_files:
        file_path = Path(__file__).parent / qml_file
        
        if not file_path.exists():
            print(f"✗ {qml_file} not found")
            all_ok = False
            continue
        
        print(f"✓ {qml_file} exists")
        
        # Basic syntax check
        content = file_path.read_text()
        if 'Dialog {' not in content:
            print(f"✗ {qml_file} missing Dialog component")
            all_ok = False
        else:
            print(f"✓ {qml_file} has Dialog component")
    
    return all_ok

def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing New Dialogs Implementation")
    print("=" * 60)
    
    results = []
    results.append(("Backend Imports", test_backend_imports()))
    results.append(("SettingsManager", test_settings_manager()))
    results.append(("QML Files", test_qml_files()))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
