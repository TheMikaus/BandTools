# Thread Cleanup Fix for WaveformEngine

## Problem Description

The AudioBrowserQML application was experiencing a critical threading issue where QThread objects were being destroyed while their worker threads were still running. This manifested as the following error message:

```
qml: Selected folder: C:\Users\white\Desktop\DMG\2025-09-24
qml: Generating waveforms for 37 files in C:\Users\white\Desktop\DMG\2025-09-24
QThread: Destroyed while thread '' is still running
```

This error occurred when:
1. A user selected a folder containing multiple audio files
2. The application started generating waveforms for all files in the background
3. The user changed folders or closed the application before all waveforms finished processing
4. The WaveformEngine was destroyed without properly cleaning up running threads

## Root Cause

The issue had multiple contributing factors:

1. **Missing Destructor**: The `WaveformEngine` class had no destructor (`__del__`) method to ensure cleanup when the object was destroyed.

2. **No Cleanup Method**: There was no public method to cancel all running waveform generations and wait for threads to finish.

3. **Incomplete Cancellation Signal**: When workers were cancelled, they would return early without emitting a signal to notify the thread to quit, leaving threads in a running state.

4. **Premature Object Deletion**: Worker and thread objects were being deleted immediately instead of being scheduled for deletion after they finished their work.

## Solution

The fix involved several coordinated changes to the `WaveformEngine` and `WaveformWorker` classes:

### 1. Added Destructor

```python
def __del__(self):
    """Cleanup method to ensure all threads are properly terminated."""
    self.cleanup()
```

The destructor ensures that when a `WaveformEngine` instance is garbage collected, all threads are properly cleaned up.

### 2. Added Cleanup Method

```python
@pyqtSlot()
def cleanup(self) -> None:
    """
    Clean up all running threads.
    
    This method should be called before the engine is destroyed to ensure
    all worker threads are properly terminated and waited for.
    """
    # Cancel all workers first
    for file_path in list(self._workers.keys()):
        worker = self._workers.get(file_path)
        if worker:
            worker.cancel()
    
    # Request all threads to quit and wait for them
    for file_path, thread in list(self._threads.items()):
        if thread and thread.isRunning():
            thread.quit()
    
    # Wait for all threads to actually finish
    for file_path, thread in list(self._threads.items()):
        if thread and thread.isRunning():
            if not thread.wait(2000):
                # Last resort: terminate the thread
                thread.terminate()
                thread.wait(1000)
    
    # Clear the dictionaries
    self._workers.clear()
    self._threads.clear()
```

This method:
- Cancels all active workers
- Requests all threads to quit
- Waits up to 2 seconds for each thread to finish
- As a last resort, terminates threads that don't respond
- Clears all internal tracking dictionaries

### 3. Added Cancelled Signal

The `WaveformWorker` class was enhanced with a `cancelled` signal:

```python
class WaveformWorker(QObject):
    progress = pyqtSignal(int, int)
    finished = pyqtSignal(str, list, int, int, int)
    error = pyqtSignal(str, str)
    cancelled = pyqtSignal(str)  # NEW: emitted when generation is cancelled
```

The worker's `run()` method now emits this signal when cancellation is detected:

```python
if self._cancelled:
    self.cancelled.emit(self._path)
    return
```

This ensures that when a worker is cancelled, it properly notifies the system so the thread can quit gracefully.

### 4. Connected Cancelled Signal to Thread Quit

In `generateWaveform()`:

```python
worker.cancelled.connect(lambda path: self._on_waveform_cancelled(path))
worker.cancelled.connect(thread.quit)
```

This ensures that when a worker is cancelled, the thread receives a quit signal.

### 5. Proper Object Lifecycle Management

Changed from immediate deletion to scheduled deletion using `deleteLater()`:

```python
def _on_waveform_finished(self, file_path: str, ...):
    # Clean up worker and thread
    worker = self._workers.pop(file_path, None)
    thread = self._threads.pop(file_path, None)
    
    if thread:
        thread.deleteLater()  # Schedule for deletion, not immediate
    if worker:
        worker.deleteLater()
```

This allows Qt's event loop to properly clean up objects after they've finished their work.

## Testing

Three comprehensive test suites were created to verify the fix:

### 1. `test_thread_cleanup.py`
Tests basic cleanup functionality:
- Verifies cleanup method exists
- Tests cleanup with no threads running
- Verifies destructor calls cleanup
- Checks that worker deleteLater is properly connected

### 2. `test_batch_waveform_cleanup.py`
Simulates the original issue scenario:
- Creates multiple test WAV files
- Starts batch waveform generation
- Calls cleanup before all waveforms complete
- Verifies no "QThread: Destroyed while thread is still running" warnings

### 3. `test_cleanup_during_generation.py`
Tests aggressive cleanup scenarios:
- Creates larger files that take longer to process
- Calls cleanup very quickly after starting generation
- Tests rapid start/stop cycles
- Ensures cleanup works even when threads are actively processing

All tests pass successfully with no QThread warnings.

## Usage Guidelines

### For Application Code

When changing folders or closing the application, call `cleanup()` explicitly:

```python
def change_folder(new_folder):
    # Clean up any running waveform generation
    waveform_engine.cleanup()
    
    # Now safe to change folder
    file_manager.setCurrentDirectory(new_folder)
```

### For QML Code

No changes needed - the cleanup happens automatically when the WaveformEngine is destroyed, but explicit cleanup can be called if desired:

```qml
onFolderChanged: {
    waveformEngine.cleanup()
    fileManager.setCurrentDirectory(newFolder)
}
```

## Benefits

1. **No More Thread Warnings**: The "QThread: Destroyed while thread is still running" warning is eliminated.

2. **Graceful Shutdown**: Application can exit cleanly even with waveforms still generating.

3. **Responsive Folder Changes**: Users can change folders without waiting for all waveforms to complete.

4. **Resource Management**: Threads are properly cleaned up, preventing resource leaks.

5. **Stability**: No more potential crashes from improperly managed threads.

## Implementation Notes

- The fix uses Qt's signal/slot mechanism for proper thread communication
- `deleteLater()` ensures objects are deleted in the correct thread context
- The cleanup method uses a two-phase approach: cancel, then wait
- As a last resort, threads can be terminated if they don't respond
- All cleanup is done synchronously to ensure completion before proceeding

## Related Files

- `backend/waveform_engine.py` - Main implementation
- `test_thread_cleanup.py` - Basic cleanup tests
- `test_batch_waveform_cleanup.py` - Batch generation tests
- `test_cleanup_during_generation.py` - Active generation tests

## See Also

- [Qt Documentation on QThread](https://doc.qt.io/qt-6/qthread.html)
- [Qt Documentation on deleteLater()](https://doc.qt.io/qt-6/qobject.html#deleteLater)
- [Qt Thread Basics](https://doc.qt.io/qt-6/thread-basics.html)
