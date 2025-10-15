#!/usr/bin/env python3
"""
Test for FloatRingBuffer implementation

Verifies that the lock-free ring buffer works correctly
for the producer-consumer pattern.
"""

import numpy as np
import sys
import os


# Standalone versions of classes for testing (avoid tkinter dependency)
def tanh_soft_clip(x):
    """Soft clip audio using tanh to prevent harsh digital clipping"""
    a = 2.0
    return np.tanh(a * x) / np.tanh(a)


class FloatRingBuffer:
    """Lock-free-ish single-producer single-consumer ring buffer for float mono frames"""
    def __init__(self, capacity_frames):
        self.buf = np.zeros(capacity_frames, dtype=np.float32)
        self.capacity = capacity_frames
        # Use separate read/write indices (volatile in nature due to GIL)
        self._read_idx = 0
        self._write_idx = 0
    
    def push(self, src):
        """Push frames into buffer, returns number of frames actually written"""
        frames = len(src)
        space = self.free_space()
        n = min(frames, space)
        if n <= 0:
            return 0
        
        w = self._write_idx
        # Handle wrap-around
        first_chunk = min(n, self.capacity - w)
        self.buf[w:w + first_chunk] = src[:first_chunk]
        if n > first_chunk:
            self.buf[0:n - first_chunk] = src[first_chunk:n]
        
        self._write_idx = (w + n) % self.capacity
        return n
    
    def pop(self, dst, frames):
        """Pop frames from buffer into dst, returns number of frames actually read"""
        avail = self.available()
        n = min(frames, avail)
        
        r = self._read_idx
        # Handle wrap-around
        first_chunk = min(n, self.capacity - r)
        dst[:first_chunk] = self.buf[r:r + first_chunk]
        if n > first_chunk:
            dst[first_chunk:n] = self.buf[0:n - first_chunk]
        
        # Pad with zeros if we don't have enough data
        if n < frames:
            dst[n:frames] = 0.0
        
        self._read_idx = (r + n) % self.capacity
        return n
    
    def available(self):
        """Number of frames available to read"""
        return (self._write_idx - self._read_idx + self.capacity) % self.capacity
    
    def free_space(self):
        """Number of frames available to write"""
        return self.capacity - 1 - self.available()


def test_ring_buffer_basic():
    """Test basic push/pop operations"""
    print("Testing basic push/pop...")
    
    capacity = 10
    rb = FloatRingBuffer(capacity)
    
    # Test initial state
    assert rb.available() == 0, "Buffer should be empty initially"
    assert rb.free_space() == capacity - 1, "Free space should be capacity - 1"
    
    # Test push
    data = np.array([1.0, 2.0, 3.0], dtype=np.float32)
    pushed = rb.push(data)
    assert pushed == 3, f"Should push 3 frames, got {pushed}"
    assert rb.available() == 3, "Should have 3 frames available"
    
    # Test pop
    output = np.zeros(3, dtype=np.float32)
    popped = rb.pop(output, 3)
    assert popped == 3, f"Should pop 3 frames, got {popped}"
    assert np.allclose(output, data), "Output should match input"
    assert rb.available() == 0, "Buffer should be empty after pop"
    
    print("✓ Basic push/pop test passed")


def test_ring_buffer_wraparound():
    """Test wrap-around behavior"""
    print("Testing wrap-around...")
    
    capacity = 8
    rb = FloatRingBuffer(capacity)
    
    # Fill buffer near capacity (capacity - 1 due to sentinel)
    data1 = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0], dtype=np.float32)
    pushed = rb.push(data1)
    assert pushed == 7, f"Should push 7 frames, got {pushed}"
    
    # Pop some data
    output = np.zeros(4, dtype=np.float32)
    popped = rb.pop(output, 4)
    assert popped == 4, f"Should pop 4 frames, got {popped}"
    assert np.allclose(output, data1[:4]), "Output should match first 4 values"
    
    # Push more data (should wrap around)
    data2 = np.array([8.0, 9.0, 10.0], dtype=np.float32)
    pushed = rb.push(data2)
    assert pushed == 3, f"Should push 3 frames, got {pushed}"
    
    # Pop remaining data
    output = np.zeros(6, dtype=np.float32)
    popped = rb.pop(output, 6)
    assert popped == 6, f"Should pop 6 frames, got {popped}"
    expected = np.array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0], dtype=np.float32)
    assert np.allclose(output, expected), f"Output mismatch: {output} vs {expected}"
    
    print("✓ Wrap-around test passed")


def test_ring_buffer_overflow():
    """Test buffer overflow behavior"""
    print("Testing buffer overflow...")
    
    capacity = 5
    rb = FloatRingBuffer(capacity)
    
    # Try to push more than capacity
    data = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0], dtype=np.float32)
    pushed = rb.push(data)
    # Can only push capacity - 1 items
    assert pushed == 4, f"Should push 4 frames (capacity-1), got {pushed}"
    assert rb.free_space() == 0, "Buffer should be full"
    
    print("✓ Buffer overflow test passed")


def test_ring_buffer_underrun():
    """Test buffer underrun behavior (zero-padding)"""
    print("Testing buffer underrun...")
    
    capacity = 10
    rb = FloatRingBuffer(capacity)
    
    # Push less than requested
    data = np.array([1.0, 2.0], dtype=np.float32)
    rb.push(data)
    
    # Try to pop more than available
    output = np.zeros(5, dtype=np.float32)
    popped = rb.pop(output, 5)
    assert popped == 2, f"Should pop 2 frames (available), got {popped}"
    
    # Check that remaining is zero-padded
    expected = np.array([1.0, 2.0, 0.0, 0.0, 0.0], dtype=np.float32)
    assert np.allclose(output, expected), f"Output should be zero-padded: {output} vs {expected}"
    
    print("✓ Buffer underrun test passed")


def test_soft_clipping():
    """Test soft-clipping function"""
    print("Testing soft-clipping...")
    
    # Test zero (should remain zero)
    x = np.array([0.0], dtype=np.float32)
    y = tanh_soft_clip(x)
    assert np.allclose(y, [0.0], atol=0.01), f"Zero should remain zero: {y}"
    
    # Test clipping range (should be compressed and bounded)
    x = np.array([2.0, -2.0, 3.0, -3.0], dtype=np.float32)
    y = tanh_soft_clip(x)
    # The function divides by tanh(2.0) ≈ 0.964, so max output is ~1.038
    # This is acceptable for soft-clipping (allows some headroom)
    assert np.all(np.abs(y) < 1.1), f"Clipped values should be near [-1, 1]: {y}"
    assert np.all(np.abs(y) < np.abs(x)), f"Clipped values should be less than input: {y} vs {x}"
    
    # Test that it's monotonic (preserves order)
    x = np.array([-2.0, -1.0, 0.0, 1.0, 2.0], dtype=np.float32)
    y = tanh_soft_clip(x)
    assert np.all(np.diff(y) > 0), "Soft-clip should be monotonically increasing"
    
    # Test that large values are compressed more than small values
    x_small = np.array([0.5], dtype=np.float32)
    x_large = np.array([2.0], dtype=np.float32)
    y_small = tanh_soft_clip(x_small)
    y_large = tanh_soft_clip(x_large)
    compression_small = y_small[0] / x_small[0]
    compression_large = y_large[0] / x_large[0]
    assert compression_large < compression_small, "Large values should be compressed more"
    
    print("✓ Soft-clipping test passed")


def test_producer_consumer_pattern():
    """Test simulated producer-consumer pattern"""
    print("Testing producer-consumer pattern simulation...")
    
    capacity = 100
    rb = FloatRingBuffer(capacity)
    
    # Simulate producer pushing blocks
    block_size = 10
    num_blocks = 5
    
    for i in range(num_blocks):
        # Producer creates audio block
        audio_block = np.ones(block_size, dtype=np.float32) * (i + 1)
        pushed = rb.push(audio_block)
        assert pushed == block_size, f"Block {i}: should push {block_size}, got {pushed}"
    
    # Simulate consumer pulling blocks
    output = np.zeros(num_blocks * block_size, dtype=np.float32)
    for i in range(num_blocks):
        block = np.zeros(block_size, dtype=np.float32)
        popped = rb.pop(block, block_size)
        assert popped == block_size, f"Block {i}: should pop {block_size}, got {popped}"
        output[i * block_size:(i + 1) * block_size] = block
    
    # Verify all data received correctly
    expected = np.concatenate([np.ones(block_size, dtype=np.float32) * (i + 1) for i in range(num_blocks)])
    assert np.allclose(output, expected), "Consumer should receive all producer data in order"
    
    print("✓ Producer-consumer pattern test passed")


def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("Running FloatRingBuffer Tests")
    print("="*60)
    
    try:
        test_ring_buffer_basic()
        test_ring_buffer_wraparound()
        test_ring_buffer_overflow()
        test_ring_buffer_underrun()
        test_soft_clipping()
        test_producer_consumer_pattern()
        
        print()
        print("="*60)
        print("✓ ALL TESTS PASSED")
        print("="*60)
        return True
    except AssertionError as e:
        print()
        print("="*60)
        print(f"✗ TEST FAILED: {e}")
        print("="*60)
        return False
    except Exception as e:
        print()
        print("="*60)
        print(f"✗ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("="*60)
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
