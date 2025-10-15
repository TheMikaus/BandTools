#!/usr/bin/env python3
"""
Simple test to verify Android SimpleMetronomeEngine compiles and has safe threading
without requiring Kivy, Android SDK, or audio hardware.
"""

import sys
import os

print("Testing Android PolyRhythmMetronome engine...")
print()

try:
    # Test numpy import (required)
    import numpy as np
    print("✓ numpy imported")
    
    # Test that the Android main.py compiles
    import py_compile
    
    android_path = os.path.join(os.path.dirname(__file__), 'android', 'main.py')
    print(f"✓ Testing compilation of {android_path}")
    
    py_compile.compile(android_path, doraise=True)
    print("✓ Android version compiles successfully")
    
    # Test that the key classes are present in the source
    with open(android_path, 'r') as f:
        source = f.read()
    
    required_classes = [
        'FloatRingBuffer',
        'Source',
        'SimpleMetronomeEngine',
        'ToneGenerator',
        'DrumSynth',
        'RhythmState'
    ]
    
    required_functions = [
        'tanh_soft_clip',
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
    
    # Verify the safe producer-consumer pattern is implemented
    safe_pattern_indicators = [
        'def _run_producer',  # Producer thread method
        'def _run_render_thread',  # Single render thread method
        'class FloatRingBuffer',  # Ring buffer class
        'class Source',  # Source class with ring buffer
        'tanh_soft_clip(mix_left)',  # Soft clipping in render thread
        'tanh_soft_clip(mix_right)',  # Soft clipping in render thread
        'self.render_thread',  # Single render thread
        'self.producer_threads',  # Multiple producer threads
        'source.ring.push',  # Producers push to ring
        'source.ring.pop',  # Render thread pulls from ring
    ]
    
    found_indicators = []
    missing_indicators = []
    for indicator in safe_pattern_indicators:
        if indicator in source:
            found_indicators.append(indicator)
        else:
            missing_indicators.append(indicator)
    
    if missing_indicators:
        print(f"✗ Safe pattern not fully implemented")
        print(f"  Missing: {missing_indicators}")
        sys.exit(1)
    
    print("✓ Safe producer-consumer pattern implemented")
    
    # Verify single AudioTrack write in render thread
    # The old _play_sound method may still exist but should not be called
    render_start = source.find('def _run_render_thread')
    if render_start == -1:
        print("✗ _run_render_thread method not found")
        sys.exit(1)
    
    # Find the end of the render thread method (next method definition or class)
    render_end = source.find('\n    def ', render_start + 1)
    if render_end == -1:
        render_end = source.find('\nclass ', render_start + 1)
    if render_end == -1:
        render_end = len(source)
    
    render_method = source[render_start:render_end]
    write_count_in_render = render_method.count('audio_track.write(')
    
    if write_count_in_render != 1:
        print(f"✗ Expected exactly 1 AudioTrack.write call in render thread, found {write_count_in_render}")
        sys.exit(1)
    
    print("✓ Single AudioTrack.write() call in render thread (safe - no concurrent writes)")
    
    # Verify old methods are not called in new pattern
    # Check for actual method calls (with parentheses)
    producer_start = source.find('def _run_producer')
    if producer_start != -1:
        producer_end = source.find('\n    def ', producer_start + 1)
        if producer_end == -1:
            producer_end = source.find('\nclass ', producer_start + 1)
        producer_method = source[producer_start:producer_end] if producer_end != -1 else source[producer_start:]
        
        if 'self._play_sound(' in producer_method:
            print("✗ Error: _play_sound() called in producer thread")
            sys.exit(1)
    
    if render_start != -1 and render_end != -1:
        if 'self._play_sound(' in render_method:
            print("✗ Error: _play_sound() called in render thread")
            sys.exit(1)
    
    print("✓ Old concurrent-write methods not called in new pattern")
    
    print()
    print("="*60)
    print("✓ ALL ANDROID ENGINE TESTS PASSED")
    print("="*60)
    print()
    print("Note: Full functional testing requires Kivy, Android SDK, and audio hardware.")
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
