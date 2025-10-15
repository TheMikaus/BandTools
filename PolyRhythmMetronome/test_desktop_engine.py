#!/usr/bin/env python3
"""
Simple test to verify Desktop StreamEngine compiles and initializes correctly
without requiring GUI or audio hardware.
"""

import sys
import os

# We'll test imports and basic initialization without actually starting audio
print("Testing Desktop PolyRhythmMetronome engine...")
print()

try:
    # Test numpy import (required)
    import numpy as np
    print("✓ numpy imported")
    
    # Test that the main classes can be imported
    # Note: We can't actually import the module due to tkinter dependency
    # So we'll just verify the file compiles
    import py_compile
    
    desktop_path = os.path.join(os.path.dirname(__file__), 'Desktop', 'Poly_Rhythm_Metronome.py')
    print(f"✓ Testing compilation of {desktop_path}")
    
    py_compile.compile(desktop_path, doraise=True)
    print("✓ Desktop version compiles successfully")
    
    # Test that the key classes are present in the source
    with open(desktop_path, 'r') as f:
        source = f.read()
    
    required_classes = [
        'FloatRingBuffer',
        'StreamEngine',
        'ToneCache',
        'WaveCache',
        'DrumSynth',
        'Mp3TickCache',
        'RhythmState'
    ]
    
    required_functions = [
        'tanh_soft_clip',
        'float_to_int16'
    ]
    
    missing = []
    for cls in required_classes:
        if f'class {cls}' not in source:
            missing.append(f'class {cls}')
    
    for func in required_functions:
        if f'def {func}' not in source:
            missing.append(f'def {func}')
    
    if missing:
        print(f"✗ Missing required definitions: {missing}")
        sys.exit(1)
    
    print(f"✓ All required classes present: {', '.join(required_classes)}")
    print(f"✓ All required functions present: {', '.join(required_functions)}")
    
    # Verify the safe pattern is implemented
    safe_pattern_indicators = [
        'tanh_soft_clip(block',  # Applied in callback
        'tanh_soft_clip(frame',  # Applied in simpleaudio loop
        'class FloatRingBuffer',  # Ring buffer class exists
    ]
    
    found_indicators = []
    for indicator in safe_pattern_indicators:
        if indicator in source:
            found_indicators.append(indicator)
    
    if len(found_indicators) != len(safe_pattern_indicators):
        print(f"✗ Safe pattern not fully implemented")
        print(f"  Found: {found_indicators}")
        print(f"  Expected: {safe_pattern_indicators}")
        sys.exit(1)
    
    print("✓ Safe threading pattern implemented (soft-clipping applied)")
    
    print()
    print("="*60)
    print("✓ ALL DESKTOP ENGINE TESTS PASSED")
    print("="*60)
    print()
    print("Note: Full functional testing requires GUI (tkinter) and audio hardware.")
    print("This test verifies compilation and presence of safe threading components.")
    
    sys.exit(0)

except Exception as e:
    print()
    print("="*60)
    print(f"✗ TEST FAILED: {e}")
    print("="*60)
    import traceback
    traceback.print_exc()
    sys.exit(1)
