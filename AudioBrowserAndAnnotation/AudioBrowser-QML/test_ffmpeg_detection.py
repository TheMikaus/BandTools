#!/usr/bin/env python3
"""
Test script for FFmpeg detection in waveform_engine.py

This script tests the improved FFmpeg detection without requiring Qt/GUI libraries.
Run this to verify FFmpeg detection is working correctly on your system.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("=" * 70)
print("FFmpeg Detection Test for AudioBrowser-QML")
print("=" * 70)

# Test 1: Check Python version
print(f"\n1. Python version: {sys.version.split()[0]}")
print(f"   Platform: {sys.platform}")

# Test 2: Import the waveform engine
print("\n2. Importing waveform_engine module...")
try:
    from backend import waveform_engine
    print("   ✓ waveform_engine imported successfully")
except ImportError as e:
    print(f"   ✗ Failed to import waveform_engine: {e}")
    sys.exit(1)

# Test 3: Check if pydub is available
print("\n3. Checking pydub availability...")
if waveform_engine.HAVE_PYDUB:
    print("   ✓ pydub is available")
else:
    print("   ✗ pydub is NOT available")
    print("     Install with: pip install pydub")

# Test 4: Run FFmpeg detection
print("\n4. Testing FFmpeg detection...")
try:
    ffmpeg_path = waveform_engine.find_ffmpeg()
    if ffmpeg_path:
        print(f"   ✓ FFmpeg found at: {ffmpeg_path}")
    else:
        print("   ✗ FFmpeg not found")
except Exception as e:
    print(f"   ✗ Error during FFmpeg detection: {e}")
    ffmpeg_path = None

# Test 5: Verify FFmpeg is executable
if ffmpeg_path:
    print("\n5. Testing FFmpeg execution...")
    try:
        import subprocess
        result = subprocess.run(
            [ffmpeg_path, "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"   ✓ FFmpeg is executable: {version_line}")
        else:
            print(f"   ✗ FFmpeg returned error code: {result.returncode}")
    except Exception as e:
        print(f"   ✗ Could not execute FFmpeg: {e}")
else:
    print("\n5. FFmpeg execution test skipped (not found)")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

if not waveform_engine.HAVE_PYDUB:
    print("\n⚠ ISSUE: pydub is not installed")
    print("  Solution: pip install pydub")
    print("\nWithout pydub, MP3 files will not work in AudioBrowser.")
elif not ffmpeg_path:
    print("\n⚠ ISSUE: FFmpeg is not found on your system")
    print("  Solutions:")
    print("    • Windows: winget install ffmpeg")
    print("    • Linux: sudo apt install ffmpeg")
    print("    • macOS: brew install ffmpeg")
    print("\n  Note: While Qt Multimedia may have built-in FFmpeg for playback,")
    print("  waveform generation requires a separate FFmpeg installation.")
    print("\nWithout FFmpeg, MP3 waveform generation will not work.")
    print("WAV files will still work without FFmpeg.")
else:
    print("\n✓ SUCCESS: FFmpeg detection should work correctly!")
    print("  MP3 files and waveforms should work in AudioBrowser-QML.")
    print("\n  Note: Qt Multimedia's built-in FFmpeg is separate from the")
    print("  FFmpeg installation used for waveform generation.")

print("\n" + "=" * 70)
print("Test complete. You can now run AudioBrowser-QML.")
print("=" * 70)
