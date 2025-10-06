#!/usr/bin/env python3
"""
Integration Test for AudioBrowser QML Application

Tests that the application can start and initialize properly.
"""

import sys
import os
import subprocess
from pathlib import Path

def test_app_starts():
    """Test that the application can start without crashing."""
    print("Testing application startup...")
    
    # Set environment for headless testing
    env = os.environ.copy()
    env['QT_QPA_PLATFORM'] = 'offscreen'
    
    # Run the application for 3 seconds
    app_path = Path(__file__).parent / "main.py"
    
    try:
        result = subprocess.run(
            [sys.executable, str(app_path)],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Combine stdout and stderr
            timeout=3
        )
    except subprocess.TimeoutExpired as e:
        # Timeout is expected - app runs indefinitely
        # Get output (stdout and stderr combined)
        output = e.stdout.decode('utf-8', errors='ignore') if e.stdout else ""
        
        # Check for success message
        if "AudioBrowser QML Phase 0 - Application started successfully" in output:
            print("  ✓ Application started successfully")
            return True
        elif "Loading QML file" in output and "Error: Failed to load QML file" not in output:
            # App is loading but might not have printed success yet
            print("  ✓ Application started (QML loading detected)")
            return True
        else:
            print(f"  ✗ Application did not start properly")
            # Show last 300 chars of output for debugging
            if output:
                print(f"  Output (last 300 chars): ...{output[-300:]}")
            return False
    
    # If it exited on its own, that's likely an error
    if result.returncode != 0:
        print(f"  ✗ Application exited with error code {result.returncode}")
        print(f"  Output: {result.stdout[:300] if result.stdout else 'None'}")
        return False
    
    return True


def main():
    """Run all integration tests."""
    print("=" * 60)
    print("AudioBrowser QML Integration Test Suite")
    print("=" * 60)
    
    startup_ok = test_app_starts()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    print(f"Application Startup: {'✓ PASS' if startup_ok else '✗ FAIL'}")
    
    if startup_ok:
        print("\n✓ All integration tests passed!")
        return 0
    else:
        print("\n✗ Some integration tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
