#!/bin/bash
# Run all tests for Now Playing Panel fixes

echo "=========================================="
echo "Running All Now Playing Panel Tests"
echo "=========================================="
echo

echo "1. Original Now Playing Panel Tests..."
python3 test_now_playing_panel.py
if [ $? -ne 0 ]; then
    echo "❌ FAILED: test_now_playing_panel.py"
    exit 1
fi
echo

echo "2. Code Verification Tests..."
python3 verify_now_playing_fixes.py
if [ $? -ne 0 ]; then
    echo "❌ FAILED: verify_now_playing_fixes.py"
    exit 1
fi
echo

echo "3. Integration Tests..."
python3 test_integration_now_playing.py
if [ $? -ne 0 ]; then
    echo "❌ FAILED: test_integration_now_playing.py"
    exit 1
fi
echo

echo "4. Visual Demonstration..."
python3 show_fixes_demo.py
echo

echo "=========================================="
echo "✅ ALL TESTS PASSED!"
echo "=========================================="
echo
echo "Summary:"
echo "  - Now Playing panel defaults to expanded"
echo "  - Waveform displays correctly"
echo "  - Position marker updates during playback"
echo "  - Feature parity with original AudioBrowser"
echo
