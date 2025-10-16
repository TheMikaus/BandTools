#!/usr/bin/env python3
"""
Test script to verify mutagen auto-installation in file_manager.py

This test ensures that the mutagen module is automatically installed
when the file_manager module is imported, following the repository's
auto-install pattern.
"""

import sys
import importlib.util
from pathlib import Path

def test_mutagen_auto_install():
    """Test that mutagen is auto-installed when file_manager is imported."""
    
    print("=" * 60)
    print("Testing Mutagen Auto-Installation")
    print("=" * 60)
    
    # First, ensure PyQt6 is available
    try:
        import PyQt6
        print("✓ PyQt6 is available")
    except ImportError:
        print("Installing PyQt6...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "PyQt6"])
        print("✓ PyQt6 installed")
    
    # Import file_manager module directly
    print("\nImporting file_manager module...")
    spec = importlib.util.spec_from_file_location(
        'file_manager',
        Path(__file__).parent / 'backend' / 'file_manager.py'
    )
    file_manager = importlib.util.module_from_spec(spec)
    
    try:
        spec.loader.exec_module(file_manager)
        print("✓ file_manager module loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load file_manager: {e}")
        return False
    
    # Check HAVE_MUTAGEN flag
    print("\nChecking HAVE_MUTAGEN flag...")
    if hasattr(file_manager, 'HAVE_MUTAGEN'):
        print(f"✓ HAVE_MUTAGEN = {file_manager.HAVE_MUTAGEN}")
    else:
        print("✗ HAVE_MUTAGEN flag not found")
        return False
    
    if not file_manager.HAVE_MUTAGEN:
        print("✗ Mutagen was not installed successfully")
        return False
    
    # Check MutagenFile is available
    print("\nChecking MutagenFile availability...")
    if hasattr(file_manager, 'MutagenFile'):
        print(f"✓ MutagenFile is available: {file_manager.MutagenFile}")
    else:
        print("✗ MutagenFile not found in module")
        return False
    
    # Verify mutagen can be imported directly
    print("\nVerifying mutagen can be imported...")
    try:
        import mutagen
        print(f"✓ Mutagen version: {mutagen.version_string}")
    except ImportError as e:
        print(f"✗ Failed to import mutagen: {e}")
        return False
    
    # Check FileManager class has extractDuration method
    print("\nChecking FileManager.extractDuration method...")
    if hasattr(file_manager.FileManager, 'extractDuration'):
        print("✓ extractDuration method exists")
    else:
        print("✗ extractDuration method not found")
        return False
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_mutagen_auto_install()
    sys.exit(0 if success else 1)
