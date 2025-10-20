#!/usr/bin/env python3
"""
Test Play Button Icon and Metadata Manager Connections

This test verifies:
1. Audio engine emits playbackStateChanged signal correctly
2. Annotation manager receives currentFileChanged signal from audio engine
3. Clip manager receives currentFileChanged signal from audio engine
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_audio_engine_signals():
    """Test that audio engine emits playbackStateChanged signal."""
    print("\n=== Testing Audio Engine Signals ===")
    
    try:
        from PyQt6.QtCore import QCoreApplication
        from backend.audio_engine import AudioEngine
        
        app = QCoreApplication(sys.argv)
        audio_engine = AudioEngine()
        
        # Track signal emissions
        state_changes = []
        
        def on_state_changed(state):
            state_changes.append(state)
            print(f"  ✓ playbackStateChanged signal emitted with state: {state}")
        
        audio_engine.playbackStateChanged.connect(on_state_changed)
        
        # Trigger state change by calling pause (will emit 'paused' state)
        audio_engine.pause()
        
        # Process events to allow signal to be emitted
        app.processEvents()
        
        if len(state_changes) > 0:
            print(f"  ✓ Audio engine correctly emits playbackStateChanged signal")
            return True
        else:
            print(f"  ✗ Audio engine did not emit playbackStateChanged signal")
            return False
            
    except Exception as e:
        print(f"  ✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_annotation_manager_connection():
    """Test that annotation manager has setCurrentFile method."""
    print("\n=== Testing Annotation Manager Connection ===")
    
    try:
        from backend.annotation_manager import AnnotationManager
        
        annotation_manager = AnnotationManager()
        
        # Check that setCurrentFile method exists
        if not hasattr(annotation_manager, 'setCurrentFile'):
            print(f"  ✗ AnnotationManager does not have setCurrentFile method")
            return False
        
        print(f"  ✓ AnnotationManager has setCurrentFile method")
        
        # Test calling it with a file path
        test_file = "/tmp/test_audio.mp3"
        annotation_manager.setCurrentFile(test_file)
        
        # Verify the file was set
        current_file = annotation_manager.getCurrentFile()
        if current_file == test_file:
            print(f"  ✓ AnnotationManager correctly sets current file")
            return True
        else:
            print(f"  ✗ AnnotationManager did not set current file correctly")
            return False
            
    except Exception as e:
        print(f"  ✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_clip_manager_connection():
    """Test that clip manager has setCurrentFile method."""
    print("\n=== Testing Clip Manager Connection ===")
    
    try:
        from backend.clip_manager import ClipManager
        
        clip_manager = ClipManager()
        
        # Check that setCurrentFile method exists
        if not hasattr(clip_manager, 'setCurrentFile'):
            print(f"  ✗ ClipManager does not have setCurrentFile method")
            return False
        
        print(f"  ✓ ClipManager has setCurrentFile method")
        
        # Test calling it with a file path
        test_file = "/tmp/test_audio.mp3"
        clip_manager.setCurrentFile(test_file)
        
        # Verify the file was set
        current_file = clip_manager.getCurrentFile()
        if current_file == test_file:
            print(f"  ✓ ClipManager correctly sets current file")
            return True
        else:
            print(f"  ✗ ClipManager did not set current file correctly")
            return False
            
    except Exception as e:
        print(f"  ✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_signal_connection_integration():
    """Test that audio engine's currentFileChanged connects to managers."""
    print("\n=== Testing Signal Connection Integration ===")
    
    try:
        from PyQt6.QtCore import QCoreApplication
        from backend.audio_engine import AudioEngine
        from backend.annotation_manager import AnnotationManager
        from backend.clip_manager import ClipManager
        
        app = QCoreApplication(sys.argv)
        audio_engine = AudioEngine()
        annotation_manager = AnnotationManager()
        clip_manager = ClipManager()
        
        # Connect signals (as done in main.py)
        audio_engine.currentFileChanged.connect(annotation_manager.setCurrentFile)
        audio_engine.currentFileChanged.connect(clip_manager.setCurrentFile)
        
        print(f"  ✓ Signals connected successfully")
        
        # Emit a file change
        test_file = "/tmp/test_integration.mp3"
        audio_engine.currentFileChanged.emit(test_file)
        
        # Process events to allow signals to be delivered
        app.processEvents()
        
        # Check if managers received the file
        annotation_file = annotation_manager.getCurrentFile()
        clip_file = clip_manager.getCurrentFile()
        
        success = True
        if annotation_file == test_file:
            print(f"  ✓ AnnotationManager received currentFileChanged signal")
        else:
            print(f"  ✗ AnnotationManager did not receive signal (got: {annotation_file})")
            success = False
        
        if clip_file == test_file:
            print(f"  ✓ ClipManager received currentFileChanged signal")
        else:
            print(f"  ✗ ClipManager did not receive signal (got: {clip_file})")
            success = False
        
        return success
            
    except Exception as e:
        print(f"  ✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("Testing Play Button Icon and Metadata Manager Connections")
    print("=" * 70)
    
    results = []
    
    # Run tests
    results.append(("Audio Engine Signals", test_audio_engine_signals()))
    results.append(("Annotation Manager Connection", test_annotation_manager_connection()))
    results.append(("Clip Manager Connection", test_clip_manager_connection()))
    results.append(("Signal Connection Integration", test_signal_connection_integration()))
    
    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
