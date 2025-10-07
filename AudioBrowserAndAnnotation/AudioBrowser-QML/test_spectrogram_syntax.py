#!/usr/bin/env python3
"""
Syntax validation test for spectrogram feature.

Tests that the code compiles and has correct structure without running Qt.
"""

import sys
import os
import ast
from pathlib import Path

def test_waveform_view_syntax():
    """Test that waveform_view.py is syntactically valid."""
    print("Test 1: waveform_view.py syntax check...")
    
    try:
        waveform_view_path = Path(__file__).parent / "backend" / "waveform_view.py"
        with open(waveform_view_path, 'r') as f:
            code = f.read()
        
        # Try to parse the file
        ast.parse(code)
        print("  ✓ waveform_view.py is syntactically valid")
        return True
        
    except SyntaxError as e:
        print(f"  ✗ Syntax error in waveform_view.py: {e}")
        return False
    except Exception as e:
        print(f"  ✗ Error reading waveform_view.py: {e}")
        return False


def test_spectrogram_attributes():
    """Test that spectrogram-related attributes exist in the code."""
    print("\nTest 2: Spectrogram attribute check...")
    
    try:
        waveform_view_path = Path(__file__).parent / "backend" / "waveform_view.py"
        with open(waveform_view_path, 'r') as f:
            code = f.read()
        
        # Check for key spectrogram attributes
        required_attrs = [
            '_show_spectrogram',
            '_spectrogram_data',
            '_current_audio_file',
            'showSpectrogram',
            'setAudioFile',
            '_compute_spectrogram',
            '_load_audio_samples',
            '_draw_spectrogram',
        ]
        
        missing = []
        for attr in required_attrs:
            if attr not in code:
                missing.append(attr)
        
        if missing:
            print(f"  ✗ Missing attributes: {', '.join(missing)}")
            return False
        
        print(f"  ✓ All required attributes present ({len(required_attrs)} found)")
        return True
        
    except Exception as e:
        print(f"  ✗ Error checking attributes: {e}")
        return False


def test_fft_imports():
    """Test that NumPy import is present."""
    print("\nTest 3: NumPy/FFT imports check...")
    
    try:
        waveform_view_path = Path(__file__).parent / "backend" / "waveform_view.py"
        with open(waveform_view_path, 'r') as f:
            code = f.read()
        
        # Check for NumPy import
        if 'import numpy' not in code:
            print("  ✗ NumPy import not found")
            return False
        
        if 'HAVE_NUMPY' not in code:
            print("  ✗ HAVE_NUMPY flag not found")
            return False
        
        # Check for FFT usage
        if 'np.fft.rfft' not in code:
            print("  ✗ FFT usage not found")
            return False
        
        print("  ✓ NumPy import and FFT usage present")
        return True
        
    except Exception as e:
        print(f"  ✗ Error checking imports: {e}")
        return False


def test_color_gradient():
    """Test that color gradient code is present."""
    print("\nTest 4: Color gradient check...")
    
    try:
        waveform_view_path = Path(__file__).parent / "backend" / "waveform_view.py"
        with open(waveform_view_path, 'r') as f:
            code = f.read()
        
        # Check for color mapping logic
        color_checks = [
            'Blue',  # Color comments
            'Green',
            'Yellow',
            'Red',
            'QColor',  # Color usage
        ]
        
        missing = []
        for check in color_checks:
            if check not in code:
                missing.append(check)
        
        if missing:
            print(f"  ✗ Missing color elements: {', '.join(missing)}")
            return False
        
        print("  ✓ Color gradient code present")
        return True
        
    except Exception as e:
        print(f"  ✗ Error checking color gradient: {e}")
        return False


def test_qml_integration():
    """Test that QML integration is present in AnnotationsTab."""
    print("\nTest 5: QML integration check...")
    
    try:
        annotations_tab_path = Path(__file__).parent / "qml" / "tabs" / "AnnotationsTab.qml"
        with open(annotations_tab_path, 'r') as f:
            code = f.read()
        
        # Check for spectrogram toggle
        if 'spectrogramToggle' not in code:
            print("  ✗ spectrogramToggle not found in AnnotationsTab")
            return False
        
        if 'Spectrogram' not in code:
            print("  ✗ Spectrogram text not found in AnnotationsTab")
            return False
        
        if 'setSpectrogramMode' not in code:
            print("  ✗ setSpectrogramMode call not found in AnnotationsTab")
            return False
        
        print("  ✓ QML integration present in AnnotationsTab")
        
        # Check WaveformDisplay
        waveform_display_path = Path(__file__).parent / "qml" / "components" / "WaveformDisplay.qml"
        with open(waveform_display_path, 'r') as f:
            code = f.read()
        
        if 'setSpectrogramMode' not in code:
            print("  ✗ setSpectrogramMode function not found in WaveformDisplay")
            return False
        
        if 'showSpectrogram' not in code:
            print("  ✗ showSpectrogram property not found in WaveformDisplay")
            return False
        
        if 'setAudioFile' not in code:
            print("  ✗ setAudioFile call not found in WaveformDisplay")
            return False
        
        print("  ✓ QML integration present in WaveformDisplay")
        return True
        
    except Exception as e:
        print(f"  ✗ Error checking QML integration: {e}")
        return False


def test_stft_parameters():
    """Test that STFT parameters are correctly defined."""
    print("\nTest 6: STFT parameters check...")
    
    try:
        waveform_view_path = Path(__file__).parent / "backend" / "waveform_view.py"
        with open(waveform_view_path, 'r') as f:
            code = f.read()
        
        # Check for STFT parameters
        params = [
            'fft_size = 2048',
            'hop_length = 512',
            'freq_bins = 128',
            'min_freq = 60',
            'max_freq = 8000',
        ]
        
        missing = []
        for param in params:
            if param not in code:
                missing.append(param)
        
        if missing:
            print(f"  ✗ Missing STFT parameters: {', '.join(missing)}")
            return False
        
        print("  ✓ STFT parameters correctly defined")
        return True
        
    except Exception as e:
        print(f"  ✗ Error checking STFT parameters: {e}")
        return False


def test_caching_logic():
    """Test that caching logic is present."""
    print("\nTest 7: Caching logic check...")
    
    try:
        waveform_view_path = Path(__file__).parent / "backend" / "waveform_view.py"
        with open(waveform_view_path, 'r') as f:
            code = f.read()
        
        # Check for caching logic
        if 'self._spectrogram_data is None' not in code:
            print("  ✗ Spectrogram data caching check not found")
            return False
        
        if '_spectrogram_data = None' not in code:
            print("  ✗ Spectrogram data clearing not found")
            return False
        
        print("  ✓ Caching logic present")
        return True
        
    except Exception as e:
        print(f"  ✗ Error checking caching logic: {e}")
        return False


def run_all_tests():
    """Run all syntax tests and report results."""
    print("=" * 60)
    print("Spectrogram Syntax Validation Test Suite")
    print("=" * 60)
    
    tests = [
        test_waveform_view_syntax,
        test_spectrogram_attributes,
        test_fft_imports,
        test_color_gradient,
        test_qml_integration,
        test_stft_parameters,
        test_caching_logic,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ✗ Test crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("✓ All syntax tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
