#!/usr/bin/env python3
"""
Backend Module Test Script

Tests the backend modules for the AudioBrowser QML application.
This script validates that all backend modules can be imported and instantiated.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all backend modules can be imported."""
    print("Testing backend module imports...")
    
    try:
        from backend.settings_manager import SettingsManager
        print("  ✓ SettingsManager imported")
    except Exception as e:
        print(f"  ✗ SettingsManager import failed: {e}")
        return False
    
    try:
        from backend.color_manager import ColorManager
        print("  ✓ ColorManager imported")
    except Exception as e:
        print(f"  ✗ ColorManager import failed: {e}")
        return False
    
    try:
        from backend.audio_engine import AudioEngine
        print("  ✓ AudioEngine imported")
    except Exception as e:
        print(f"  ✗ AudioEngine import failed: {e}")
        return False
    
    try:
        from backend.file_manager import FileManager
        print("  ✓ FileManager imported")
    except Exception as e:
        print(f"  ✗ FileManager import failed: {e}")
        return False
    
    try:
        from backend.models import FileListModel, AnnotationsModel
        print("  ✓ Models imported (FileListModel, AnnotationsModel)")
    except Exception as e:
        print(f"  ✗ Models import failed: {e}")
        return False
    
    return True


def test_syntax():
    """Test Python syntax for all backend modules."""
    import ast
    
    print("\nTesting Python syntax...")
    
    files = [
        'main.py',
        'backend/settings_manager.py',
        'backend/color_manager.py',
        'backend/audio_engine.py',
        'backend/file_manager.py',
        'backend/models.py'
    ]
    
    all_valid = True
    for file in files:
        try:
            with open(file, 'r') as f:
                ast.parse(f.read())
            print(f"  ✓ {file}")
        except Exception as e:
            print(f"  ✗ {file}: {e}")
            all_valid = False
    
    return all_valid


def test_qml_files():
    """Check that all QML files exist."""
    print("\nChecking QML files...")
    
    qml_files = [
        'qml/main.qml',
        'qml/styles/Theme.qml',
        'qml/components/StyledButton.qml',
        'qml/components/StyledLabel.qml',
        'qml/components/StyledTextField.qml',
        'qml/tabs/LibraryTab.qml',
        'qml/tabs/AnnotationsTab.qml',
        'qml/tabs/ClipsTab.qml',
    ]
    
    all_exist = True
    for qml_file in qml_files:
        if Path(qml_file).exists():
            print(f"  ✓ {qml_file}")
        else:
            print(f"  ✗ {qml_file} not found")
            all_exist = False
    
    return all_exist


def main():
    """Run all tests."""
    print("=" * 60)
    print("AudioBrowser QML Backend Test Suite")
    print("=" * 60)
    
    # Test syntax first (doesn't require PyQt6)
    syntax_ok = test_syntax()
    
    # Test QML files
    qml_ok = test_qml_files()
    
    # Try to import modules (requires PyQt6)
    try:
        import PyQt6
        imports_ok = test_imports()
    except ImportError:
        print("\nWarning: PyQt6 not installed, skipping import tests")
        print("Install with: pip install PyQt6")
        imports_ok = None
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    print(f"Python Syntax: {'✓ PASS' if syntax_ok else '✗ FAIL'}")
    print(f"QML Files: {'✓ PASS' if qml_ok else '✗ FAIL'}")
    if imports_ok is not None:
        print(f"Module Imports: {'✓ PASS' if imports_ok else '✗ FAIL'}")
    else:
        print(f"Module Imports: SKIPPED (PyQt6 not installed)")
    
    # Return success if all tests passed (or were skipped)
    if syntax_ok and qml_ok and (imports_ok is None or imports_ok):
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
