# Performance Guide: Large Libraries & Fast Generation

**AudioBrowser Version**: 1.x  
**Last Updated**: January 2025

---

## Overview

This guide explains how to get the best performance from AudioBrowser when working with large music libraries. Learn how to:

- Handle libraries with hundreds or thousands of recordings
- Speed up waveform generation with parallel processing
- Navigate large libraries efficiently
- Configure performance settings for your hardware

---

## Quick Start: Working with Large Libraries

If you have a library with 500+ audio files, AudioBrowser will automatically use **pagination** to load files in manageable chunks. You'll see:

1. Navigation buttons: **◄ Previous** and **Next ►**
2. Page information: "Showing 1-200 of 1234 files"
3. Fast folder loading (< 1 second)

That's it! AudioBrowser handles everything automatically. Read on for advanced options and tips.

---

## Feature 1: Pagination for Large Libraries

### What is Pagination?

Pagination divides your large library into "pages" of files, loading only one page at a time. This keeps AudioBrowser fast and responsive, even with thousands of files.

### When Does It Activate?

- **Automatically** for libraries with 500+ files
- Configurable threshold in settings (if you want to change it)

### How to Navigate Pages

**Using Buttons**:
- Click **Next ►** to see the next set of files
- Click **◄ Previous** to go back
- Buttons are disabled when you're at the first or last page

**Page Information**:
- Look for "Showing X-Y of Z files" below the file table
- X-Y = files currently displayed
- Z = total files in the folder

**Tips**:
- The table scrolls to the top when you change pages
- Your selection is preserved within a page
- Best takes and other metadata work across all pages

### Example

You have 1,200 recordings from the past year:

1. **Before**: Loading the folder took 7 seconds and scrolling was laggy
2. **After**: Folder loads in < 1 second, showing first 200 files
3. Click **Next ►** to see files 201-400 (instant)
4. Click **Next ►** again to see files 401-600
5. And so on...

### Configuring Pagination

**To Change Settings**:
1. Go to **File** → **Preferences**
2. Look for **Performance Settings** section
3. Configure:
   - **Enable pagination for large libraries**: Check to enable (default: ON)
   - **Files per page**: 50-1000 (default: 200)

**Recommended Settings**:
- **Small libraries (< 100 files)**: Pagination disabled (not needed)
- **Medium libraries (100-500 files)**: 200 files per page
- **Large libraries (500-2000 files)**: 200 files per page
- **Very large libraries (2000+ files)**: 100 files per page (more pages, but faster)

**Why Adjust?**:
- **More files per page**: Fewer page changes, but slightly slower load
- **Fewer files per page**: More page changes, but faster load and less memory

---

## Feature 2: Parallel Waveform Generation

### What is Parallel Processing?

When generating waveforms for multiple files, AudioBrowser can use **multiple CPU cores** simultaneously. This can be 2-4x faster than the old sequential method.

### How It Works

**Automatically Enabled**:
- AudioBrowser detects your CPU core count
- Uses (cores - 1) workers by default
- Example: 8-core CPU → 7 workers

**Example Performance**:
- **Sequential (old)**: 100 files in 100 seconds
- **Parallel (4 cores)**: 100 files in 30 seconds
- **Speedup**: 3.3x faster

### Configuring Parallel Workers

**To Change Settings**:
1. Go to **File** → **Preferences**
2. Look for **Performance Settings** section
3. Set **Parallel workers**:
   - **0 (Auto)**: Recommended - uses CPU count - 1
   - **1**: Sequential (old behavior)
   - **2-16**: Manual setting

**Recommended Settings**:
- **Auto (0)**: Best for most users
- **Half of CPU cores**: Good balance (e.g., 4 workers on 8-core CPU)
- **1 (sequential)**: If you experience issues or have other heavy tasks running

**When to Adjust**:
- Set to **1** if computer slows down during generation
- Set to **lower number** if you're doing other work simultaneously
- Set to **Auto** for maximum speed (default)

---

## Feature 3: Search & Filter with Large Libraries

### Current Behavior

**Important**: Search currently operates on the **current page only** for performance reasons.

### How to Search Across All Files

**Option 1: Use Provided Names**
- Add provided names to all your files
- Use file system search to find files by name
- Open the folder in AudioBrowser

**Option 2: Navigate Pages**
- Use search on first page
- Click **Next ►** and search again
- Repeat for each page

**Option 3: Adjust Pagination**
- Increase "Files per page" to show more files at once
- Search will cover more files per page
- Trade-off: Slightly slower page load

### Future Enhancement

Global search across all pages is planned for a future update!

---

## Performance Tips & Best Practices

### For Fastest Performance

1. **Enable Pagination**: Auto-enables for 500+ files (recommended)
2. **Use Parallel Processing**: Set to Auto in preferences
3. **Close Other Applications**: Free up CPU and memory
4. **Use SSD Storage**: Faster file access than HDD
5. **Keep Libraries Organized**: Split into yearly/monthly folders

### For Maximum Responsiveness

1. **Smaller Chunk Sizes**: 100 files per page instead of 200
2. **Disable Auto-Generation**: Generate waveforms manually when needed
3. **Use Search**: Find specific files quickly
4. **Mark Best Takes**: Helps identify key recordings quickly

### For Batch Operations

1. **Select Files on Current Page**: Use Ctrl+Click or Shift+Click
2. **Batch Mark Best Takes**: Mark all selected files at once
3. **Navigate to Next Page**: Repeat batch operation
4. **Auto-Label Suggestions**: Works across all pages

---

## Understanding Performance Metrics

### Load Time

**What It Measures**: Time to display the file table after selecting a folder

**Good Performance**:
- Small library (< 100 files): < 0.5 seconds
- Medium library (100-500 files): < 1 second
- Large library (500+ files): < 1 second (with pagination)

**If Slow**:
- Enable pagination in preferences
- Reduce "Files per page" setting
- Check if other applications are using CPU/disk

### Generation Time

**What It Measures**: Time to generate waveforms for all files

**Good Performance**:
- 50 files: < 30 seconds
- 100 files: < 1 minute
- 500 files: < 5 minutes (with parallel processing)

**If Slow**:
- Enable parallel processing (set to Auto)
- Close other applications
- Check CPU usage in Task Manager
- Consider generating in batches (select specific folders)

### Memory Usage

**Expected Usage**:
- Small library (50 files): ~100 MB
- Medium library (200 files): ~200 MB
- Large library (1000 files with pagination): ~200 MB
- Very large library (2000+ files with pagination): ~300 MB

**If High**:
- Reduce "Files per page" in settings
- Close unused tabs in the application
- Restart AudioBrowser to clear cache

---

## Troubleshooting

### Problem: Folder Takes Too Long to Load

**Possible Causes**:
1. Library has 500+ files but pagination is disabled
2. Too many files per page
3. Slow disk (HDD instead of SSD)

**Solutions**:
1. Enable pagination in preferences
2. Reduce "Files per page" to 100
3. Move library to faster storage (SSD)

### Problem: Waveform Generation Is Slow

**Possible Causes**:
1. Parallel processing disabled
2. Other applications using CPU
3. Large audio files (long recordings)

**Solutions**:
1. Set "Parallel workers" to Auto in preferences
2. Close other applications during generation
3. Generate in batches (one folder at a time)
4. Check Task Manager for CPU usage

### Problem: UI Feels Laggy

**Possible Causes**:
1. Too many files loaded (pagination disabled)
2. Low-end hardware
3. Other applications using resources

**Solutions**:
1. Enable pagination with smaller chunk size (100 files)
2. Close other applications
3. Restart AudioBrowser
4. Check system resources (CPU, Memory)

### Problem: Can't Find a Specific File

**Possible Causes**:
1. File is on a different page (pagination)
2. File is in a different folder
3. Search only looks at current page

**Solutions**:
1. Navigate through pages using Next/Previous buttons
2. Check folder structure in the tree
3. Use file system search to find file, then open folder
4. Increase "Files per page" to see more files at once

---

## Keyboard Shortcuts (Relevant to Performance)

| Shortcut | Action | Description |
|----------|--------|-------------|
| `Ctrl+F` | Quick Search | Search within current page |
| `Page Down` | Scroll Down | Scroll table (not page navigation) |
| `Page Up` | Scroll Up | Scroll table (not page navigation) |
| `Home` | First File | Jump to first file in current page |
| `End` | Last File | Jump to last file in current page |

**Note**: Keyboard shortcuts for page navigation (Alt+Left/Alt+Right) may be added in a future update.

---

## Advanced Configuration

### For Power Users

**Optimal Settings for Different Hardware**:

**High-End System (8+ cores, SSD)**:
- Pagination: Enabled
- Files per page: 200-500
- Parallel workers: Auto (or 6-8)
- Auto-generation: On folder selection

**Mid-Range System (4 cores, SSD)**:
- Pagination: Enabled
- Files per page: 200
- Parallel workers: Auto (or 3)
- Auto-generation: On folder selection

**Low-End System (2 cores, HDD)**:
- Pagination: Enabled
- Files per page: 100
- Parallel workers: 1 (sequential)
- Auto-generation: Manual

### Testing Your Configuration

1. Select a test folder with 100+ files
2. Note the load time and generation time
3. Adjust settings in preferences
4. Reload the folder and compare
5. Find the best balance for your system

---

## Frequently Asked Questions

### Q: Will pagination break my workflow?

**A**: No! Pagination is designed to be transparent:
- All features work across pages (best takes, annotations, etc.)
- Batch operations work on current page
- Navigation is quick and intuitive
- Small libraries aren't affected (pagination doesn't activate)

### Q: How much faster is parallel processing?

**A**: Typical speedups:
- **2-core system**: 1.5-2x faster
- **4-core system**: 2.5-3.5x faster
- **8-core system**: 3-5x faster

Actual speedup depends on your specific CPU and workload.

### Q: Can I disable pagination?

**A**: Yes, but not recommended for large libraries:
1. Go to Preferences
2. Uncheck "Enable pagination for large libraries"
3. Note: Performance will suffer with 500+ files

### Q: Does pagination affect searching?

**A**: Currently, search operates on the current page only. This is by design for performance. Use navigation to search across pages, or increase "Files per page" to search more files at once.

### Q: Can I generate waveforms for specific files only?

**A**: Currently, auto-generation processes all files in a folder. Manual generation per-file is planned for a future update (lazy loading feature).

### Q: How do I check if parallel processing is working?

**A**: 
1. Start waveform generation
2. Open Task Manager (Windows) or Activity Monitor (Mac)
3. Check CPU usage - should be high (60-90%) if parallel processing is active
4. Check individual core usage - multiple cores should show activity

---

## Version History

### Version 1.x (January 2025)
- ✅ Pagination for large libraries (Section 5.2.1)
- ✅ Parallel waveform generation (Section 5.1.4)
- ✅ Performance settings in preferences
- 🚧 Lazy loading (planned for next version)
- 🚧 Global search (planned for future version)

---

## Related Documentation

- [TEST_PLAN_PERFORMANCE_IMPROVEMENTS.md](../test_plans/TEST_PLAN_PERFORMANCE_IMPROVEMENTS.md) - Complete test plan
- [IMPLEMENTATION_SUMMARY_PERFORMANCE.md](../technical/IMPLEMENTATION_SUMMARY_PERFORMANCE.md) - Technical details
- [INTERFACE_IMPROVEMENT_IDEAS.md](../technical/INTERFACE_IMPROVEMENT_IDEAS.md) - Feature roadmap

---

## Getting Help

If you experience performance issues not covered in this guide:

1. Check system requirements (Python 3.8+, PyQt6)
2. Review troubleshooting section above
3. Check application logs (audiobrowser.log)
4. Report issues with:
   - Library size (number of files)
   - System specs (CPU, RAM, storage type)
   - Settings configuration
   - Expected vs actual behavior

---

## Conclusion

AudioBrowser's performance features enable you to work efficiently with libraries of any size. The automatic pagination and parallel processing ensure that whether you have 50 files or 5,000 files, the application remains fast and responsive.

**Key Takeaways**:
- Pagination activates automatically for 500+ files
- Parallel processing speeds up waveform generation 2-4x
- Configure settings in Preferences for optimal performance
- All features work seamlessly with pagination

Enjoy working with your large music libraries! 🎵
