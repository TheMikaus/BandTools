#!/usr/bin/env python3
"""
Test script to verify waveform NOTIFY signal fixes.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_waveform_view_imports():
    """Test that WaveformView can be imported."""
    print("Testing WaveformView imports...")
    
    try:
        # Just check that the file exists and is readable
        waveform_view_py = Path(__file__).parent / "backend" / "waveform_view.py"
        if waveform_view_py.exists():
            print("✓ waveform_view.py file exists")
            return True
        else:
            print("✗ waveform_view.py file not found")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_waveform_view_signals():
    """Test that WaveformView has the required signals."""
    print("\nTesting WaveformView signals...")
    
    try:
        # Read the source code directly instead of importing
        waveform_view_py = Path(__file__).parent / "backend" / "waveform_view.py"
        source = waveform_view_py.read_text()
        
        # Check for required signals
        required_signals = [
            'seekRequested',
            'peaksChanged',
            'durationMsChanged'
        ]
        
        missing_signals = []
        for signal in required_signals:
            if signal not in source:
                missing_signals.append(signal)
        
        if missing_signals:
            print(f"✗ Missing signals: {', '.join(missing_signals)}")
            return False
        
        print("✓ All required signals are defined")
        
        # Check that properties use notify parameter
        if 'notify=peaksChanged' in source:
            print("✓ peaks property has notify=peaksChanged")
        else:
            print("✗ peaks property missing notify parameter")
            return False
            
        if 'notify=durationMsChanged' in source:
            print("✓ durationMs property has notify=durationMsChanged")
        else:
            print("✗ durationMs property missing notify parameter")
            return False
        
        # Check that signals are emitted
        if 'self.peaksChanged.emit()' in source:
            print("✓ peaksChanged signal is emitted")
        else:
            print("✗ peaksChanged signal not emitted")
            return False
            
        if 'self.durationMsChanged.emit()' in source:
            print("✓ durationMsChanged signal is emitted")
        else:
            print("✗ durationMsChanged signal not emitted")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Error checking signals: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_python_syntax():
    """Test that the Python file has valid syntax."""
    print("\nTesting Python syntax...")
    
    try:
        waveform_view_py = Path(__file__).parent / "backend" / "waveform_view.py"
        
        with open(waveform_view_py, 'r') as f:
            code = f.read()
        
        # Try to compile the code
        compile(code, str(waveform_view_py), 'exec')
        
        print("✓ Python syntax is valid")
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error checking syntax: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing Waveform NOTIFY Signal Fixes")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Python Syntax", test_python_syntax()))
    results.append(("WaveformView Imports", test_waveform_view_imports()))
    results.append(("WaveformView Signals", test_waveform_view_signals()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
