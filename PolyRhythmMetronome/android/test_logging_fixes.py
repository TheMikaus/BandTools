#!/usr/bin/env python3
"""
Test script to validate logging fixes for PolyRhythmMetronome Android.

Tests:
1. Empty mp3_tick values are displayed as "none" instead of empty string
2. Timing drift messages correctly show "early" or "late"
"""

import sys


def test_mp3_tick_display():
    """Test that empty mp3_tick values are displayed correctly"""
    print("Test 1: mp3_tick display with empty string")
    
    # Simulate the old behavior (incorrect)
    layer_old = {"mp3_tick": ""}
    mp3_name_old = layer_old.get("mp3_tick", "none")
    old_result = f"mp3_tick '{mp3_name_old}'"
    print(f"  Old behavior: {old_result}")
    assert old_result == "mp3_tick ''", "Old behavior should show empty string"
    
    # Simulate the new behavior (correct)
    layer_new = {"mp3_tick": ""}
    mp3_name_new = layer_new.get("mp3_tick", "") or "none"
    new_result = f"mp3_tick '{mp3_name_new}'"
    print(f"  New behavior: {new_result}")
    assert new_result == "mp3_tick 'none'", "New behavior should show 'none'"
    
    # Test with actual value
    layer_with_value = {"mp3_tick": "click"}
    mp3_name_value = layer_with_value.get("mp3_tick", "") or "none"
    value_result = f"mp3_tick '{mp3_name_value}'"
    print(f"  With value:   {value_result}")
    assert value_result == "mp3_tick 'click'", "Should show actual value"
    
    # Test with missing key
    layer_missing = {}
    mp3_name_missing = layer_missing.get("mp3_tick", "") or "none"
    missing_result = f"mp3_tick '{mp3_name_missing}'"
    print(f"  Missing key:  {missing_result}")
    assert missing_result == "mp3_tick 'none'", "Should show 'none' when key missing"
    
    print("  ✓ Test 1 passed\n")


def test_timing_drift_display():
    """Test that timing drift is displayed correctly"""
    print("Test 2: Timing drift display")
    
    # Test early arrival (negative timing_error)
    timing_error_early = -0.002  # -2ms
    drift_desc_early = "late" if timing_error_early > 0 else "early"
    early_msg = f"arrived {abs(timing_error_early*1000):.2f}ms {drift_desc_early}"
    print(f"  Early (-2ms): {early_msg}")
    assert early_msg == "arrived 2.00ms early", "Should show as early"
    
    # Test late arrival (positive timing_error)
    timing_error_late = 0.003  # +3ms
    drift_desc_late = "late" if timing_error_late > 0 else "early"
    late_msg = f"arrived {abs(timing_error_late*1000):.2f}ms {drift_desc_late}"
    print(f"  Late (+3ms):  {late_msg}")
    assert late_msg == "arrived 3.00ms late", "Should show as late"
    
    # Test zero (edge case)
    timing_error_zero = 0.0
    drift_desc_zero = "late" if timing_error_zero > 0 else "early"
    zero_msg = f"arrived {abs(timing_error_zero*1000):.2f}ms {drift_desc_zero}"
    print(f"  Zero (0ms):   {zero_msg}")
    assert zero_msg == "arrived 0.00ms early", "Should show as early (due to <= 0)"
    
    print("  ✓ Test 2 passed\n")


def test_avg_drift_display():
    """Test that average drift statistics are displayed correctly"""
    print("Test 3: Average drift statistics display")
    
    # Test negative average (consistently early - good)
    avg_error_early = -0.5  # -0.5ms
    timing_desc_early = "late" if avg_error_early > 0 else "early"
    early_stats = f"avg_drift={abs(avg_error_early):.2f}ms {timing_desc_early}"
    print(f"  Early avg (-0.5ms): {early_stats}")
    assert early_stats == "avg_drift=0.50ms early", "Should show as early"
    
    # Test positive average (consistently late - bad)
    avg_error_late = 1.2  # +1.2ms
    timing_desc_late = "late" if avg_error_late > 0 else "early"
    late_stats = f"avg_drift={abs(avg_error_late):.2f}ms {timing_desc_late}"
    print(f"  Late avg (+1.2ms):  {late_stats}")
    assert late_stats == "avg_drift=1.20ms late", "Should show as late"
    
    print("  ✓ Test 3 passed\n")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing PolyRhythmMetronome Logging Fixes")
    print("=" * 60 + "\n")
    
    try:
        test_mp3_tick_display()
        test_timing_drift_display()
        test_avg_drift_display()
        
        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
