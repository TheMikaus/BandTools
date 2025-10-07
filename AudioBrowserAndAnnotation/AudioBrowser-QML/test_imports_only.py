#!/usr/bin/env python3
"""
Simple test to verify that all modules can be imported without errors.
This doesn't require Qt GUI components.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("Testing Module Imports")
print("=" * 60)

all_passed = True

# Test basic Python imports
print("\n1. Testing standard library imports...")
try:
    import json
    from pathlib import Path
    from typing import List, Dict, Optional
    print("   ✓ Standard library imports OK")
except Exception as e:
    print(f"   ✗ Failed: {e}")
    all_passed = False

# Test numpy without GUI
print("\n2. Testing NumPy...")
try:
    import numpy as np
    arr = np.array([1, 2, 3])
    print(f"   ✓ NumPy available: {np.__version__}")
except Exception as e:
    print(f"   ✗ NumPy not available: {e}")
    # Not critical for testing, continue

# Test fingerprint functions (non-GUI parts)
print("\n3. Testing fingerprint algorithm functions...")
try:
    # Import just the algorithm functions, not the Qt classes
    import backend.fingerprint_engine as fp_engine
    
    # Test that constants are available
    assert hasattr(fp_engine, 'FINGERPRINT_ALGORITHMS')
    assert hasattr(fp_engine, 'DEFAULT_ALGORITHM')
    
    # Test that algorithm functions exist
    assert hasattr(fp_engine, 'compute_audio_fingerprint')
    assert hasattr(fp_engine, 'compute_spectral_fingerprint')
    assert hasattr(fp_engine, 'compute_lightweight_fingerprint')
    assert hasattr(fp_engine, 'compute_chromaprint_fingerprint')
    assert hasattr(fp_engine, 'compute_audfprint_fingerprint')
    assert hasattr(fp_engine, 'compare_fingerprints')
    
    print(f"   ✓ Fingerprint algorithms available: {len(fp_engine.FINGERPRINT_ALGORITHMS)}")
    for alg_name, alg_info in fp_engine.FINGERPRINT_ALGORITHMS.items():
        print(f"     - {alg_name}: {alg_info['name']}")
    
except Exception as e:
    print(f"   ✗ Failed: {e}")
    import traceback
    traceback.print_exc()
    all_passed = False

# Test a simple fingerprint generation
print("\n4. Testing fingerprint generation...")
try:
    import math
    import backend.fingerprint_engine as fp_engine
    
    # Create synthetic audio (1 second of 440 Hz sine wave)
    samples = [math.sin(2 * math.pi * 440 * t / 44100) for t in range(44100)]
    sr = 44100
    
    # Generate fingerprint
    fp = fp_engine.compute_audio_fingerprint(samples, sr)
    
    if not fp:
        print("   ✗ Fingerprint generation returned empty result")
        all_passed = False
    else:
        print(f"   ✓ Generated fingerprint: {len(fp)} elements")
        
        # Test self-similarity
        similarity = fp_engine.compare_fingerprints(fp, fp)
        print(f"   ✓ Self-similarity: {similarity:.4f}")
        
        if similarity < 0.99:
            print(f"   ✗ Warning: Self-similarity unexpectedly low")
            all_passed = False
            
except Exception as e:
    print(f"   ✗ Failed: {e}")
    import traceback
    traceback.print_exc()
    all_passed = False

# Test cache functions
print("\n5. Testing cache management functions...")
try:
    import tempfile
    import backend.fingerprint_engine as fp_engine
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Test cache creation
        cache = fp_engine.load_fingerprint_cache(tmppath)
        assert "files" in cache
        assert "version" in cache
        print("   ✓ Cache loading works")
        
        # Test cache saving
        cache["files"]["test.wav"] = {
            "fingerprints": {
                "spectral": [0.1, 0.2, 0.3]
            }
        }
        fp_engine.save_fingerprint_cache(tmppath, cache)
        print("   ✓ Cache saving works")
        
        # Test cache reloading
        cache2 = fp_engine.load_fingerprint_cache(tmppath)
        assert "test.wav" in cache2["files"]
        print("   ✓ Cache persistence works")
        
except Exception as e:
    print(f"   ✗ Failed: {e}")
    import traceback
    traceback.print_exc()
    all_passed = False

print("\n" + "=" * 60)
if all_passed:
    print("✓ All import and function tests passed!")
    print("=" * 60)
    sys.exit(0)
else:
    print("✗ Some tests failed")
    print("=" * 60)
    sys.exit(1)
