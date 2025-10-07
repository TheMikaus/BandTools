#!/usr/bin/env python3
"""
Test suite for fingerprint_engine module.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all fingerprint engine imports work."""
    print("Testing imports...")
    try:
        from backend.fingerprint_engine import (
            FingerprintEngine,
            compute_audio_fingerprint,
            compute_spectral_fingerprint,
            compute_lightweight_fingerprint,
            compute_chromaprint_fingerprint,
            compute_audfprint_fingerprint,
            compare_fingerprints,
            FINGERPRINT_ALGORITHMS,
            DEFAULT_ALGORITHM
        )
        print("  ✓ All imports successful")
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_basic_fingerprinting():
    """Test basic fingerprinting functionality."""
    print("\nTesting basic fingerprinting...")
    try:
        from backend.fingerprint_engine import (
            compute_audio_fingerprint,
            compare_fingerprints
        )
        
        # Create synthetic audio samples
        import math
        samples = [math.sin(2 * math.pi * 440 * t / 44100) for t in range(44100)]  # 1 second of 440 Hz
        sr = 44100
        
        # Generate fingerprint
        fp1 = compute_audio_fingerprint(samples, sr)
        
        if not fp1:
            print("  ✗ Failed to generate fingerprint")
            return False
        
        print(f"  ✓ Generated fingerprint with {len(fp1)} elements")
        
        # Test similarity with itself (should be 1.0)
        similarity = compare_fingerprints(fp1, fp1)
        
        if similarity < 0.99:
            print(f"  ✗ Self-similarity too low: {similarity}")
            return False
        
        print(f"  ✓ Self-similarity correct: {similarity:.4f}")
        
        # Generate different fingerprint
        samples2 = [math.sin(2 * math.pi * 880 * t / 44100) for t in range(44100)]  # 880 Hz
        fp2 = compute_audio_fingerprint(samples2, sr)
        
        # Compare different fingerprints (should be lower)
        diff_similarity = compare_fingerprints(fp1, fp2)
        
        print(f"  ✓ Different fingerprint similarity: {diff_similarity:.4f}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_all_algorithms():
    """Test all fingerprinting algorithms."""
    print("\nTesting all algorithms...")
    try:
        from backend.fingerprint_engine import (
            compute_multiple_fingerprints,
            FINGERPRINT_ALGORITHMS
        )
        
        # Create synthetic audio
        import math
        samples = [math.sin(2 * math.pi * 440 * t / 44100) for t in range(44100)]
        sr = 44100
        
        fingerprints = compute_multiple_fingerprints(samples, sr)
        
        if len(fingerprints) != len(FINGERPRINT_ALGORITHMS):
            print(f"  ✗ Expected {len(FINGERPRINT_ALGORITHMS)} algorithms, got {len(fingerprints)}")
            return False
        
        for alg_name, fp in fingerprints.items():
            if not fp:
                print(f"  ✗ Algorithm '{alg_name}' failed to generate fingerprint")
                return False
            print(f"  ✓ {alg_name}: {len(fp)} elements")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_engine_instantiation():
    """Test FingerprintEngine instantiation."""
    print("\nTesting FingerprintEngine instantiation...")
    try:
        from PyQt6.QtWidgets import QApplication
        from backend.fingerprint_engine import FingerprintEngine
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        engine = FingerprintEngine()
        
        # Test basic properties
        alg = engine.getAlgorithm()
        threshold = engine.getThreshold()
        
        print(f"  ✓ Engine created")
        print(f"  ✓ Default algorithm: {alg}")
        print(f"  ✓ Default threshold: {threshold}")
        
        # Test setting properties
        engine.setAlgorithm("lightweight")
        engine.setThreshold(0.8)
        
        print(f"  ✓ Algorithm changed to: {engine.getAlgorithm()}")
        print(f"  ✓ Threshold changed to: {engine.getThreshold()}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Fingerprint Engine Test Suite")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Basic Fingerprinting", test_basic_fingerprinting()))
    results.append(("All Algorithms", test_all_algorithms()))
    results.append(("Engine Instantiation", test_engine_instantiation()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
