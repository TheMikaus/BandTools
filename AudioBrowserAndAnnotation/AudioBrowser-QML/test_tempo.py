#!/usr/bin/env python3
"""
Unit tests for tempo manager functionality.
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtCore import QCoreApplication
from backend.tempo_manager import TempoManager


def test_tempo_manager_basic():
    """Test basic tempo manager functionality."""
    app = QCoreApplication(sys.argv)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create tempo manager
        tempo_mgr = TempoManager()
        tempo_mgr.setCurrentDirectory(tmpdir)
        
        # Test setting and getting BPM
        tempo_mgr.setBPM("song1.mp3", 120)
        tempo_mgr.setBPM("song2.wav", 90)
        
        assert tempo_mgr.getBPM("song1.mp3") == 120
        assert tempo_mgr.getBPM("song2.wav") == 90
        assert tempo_mgr.getBPM("song3.mp3") == 0  # Not set
        
        # Check file count
        assert tempo_mgr.getFileCount() == 2
        
        # Check persistence file exists
        tempo_json = tmpdir / ".tempo.json"
        assert tempo_json.exists()
        
        # Verify JSON content
        with open(tempo_json, 'r') as f:
            data = json.load(f)
        assert data["song1.mp3"] == 120
        assert data["song2.wav"] == 90
        
        print("✓ test_tempo_manager_basic passed")
        return True


def test_tempo_manager_persistence():
    """Test tempo data persistence across manager instances."""
    app = QCoreApplication(sys.argv)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create first manager and set data
        tempo_mgr1 = TempoManager()
        tempo_mgr1.setCurrentDirectory(tmpdir)
        tempo_mgr1.setBPM("test.mp3", 140)
        
        # Create second manager and verify data loads
        tempo_mgr2 = TempoManager()
        tempo_mgr2.setCurrentDirectory(tmpdir)
        
        assert tempo_mgr2.getBPM("test.mp3") == 140
        
        print("✓ test_tempo_manager_persistence passed")
        return True


def test_tempo_manager_clear():
    """Test clearing BPM and clearing all."""
    app = QCoreApplication(sys.argv)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        tempo_mgr = TempoManager()
        tempo_mgr.setCurrentDirectory(tmpdir)
        
        # Set some BPMs
        tempo_mgr.setBPM("song1.mp3", 120)
        tempo_mgr.setBPM("song2.mp3", 130)
        assert tempo_mgr.getFileCount() == 2
        
        # Clear one
        tempo_mgr.clearBPM("song1.mp3")
        assert tempo_mgr.getBPM("song1.mp3") == 0
        assert tempo_mgr.getFileCount() == 1
        
        # Clear all
        tempo_mgr.clearAll()
        assert tempo_mgr.getFileCount() == 0
        assert tempo_mgr.getBPM("song2.mp3") == 0
        
        print("✓ test_tempo_manager_clear passed")
        return True


def test_tempo_manager_validation():
    """Test BPM validation."""
    app = QCoreApplication(sys.argv)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        tempo_mgr = TempoManager()
        tempo_mgr.setCurrentDirectory(tmpdir)
        
        # Test negative value
        tempo_mgr.setBPM("test.mp3", -10)
        assert tempo_mgr.getBPM("test.mp3") == 0
        
        # Test value above max
        tempo_mgr.setBPM("test.mp3", 500)
        assert tempo_mgr.getBPM("test.mp3") == 300
        
        # Test zero removes BPM
        tempo_mgr.setBPM("test.mp3", 120)
        tempo_mgr.setBPM("test.mp3", 0)
        assert tempo_mgr.getBPM("test.mp3") == 0
        assert tempo_mgr.getFileCount() == 0
        
        print("✓ test_tempo_manager_validation passed")
        return True


if __name__ == "__main__":
    print("Running tempo manager tests...")
    
    tests = [
        test_tempo_manager_basic,
        test_tempo_manager_persistence,
        test_tempo_manager_clear,
        test_tempo_manager_validation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
