# AudioBrowser Test Plans - Quick Reference Summary

**Date**: January 2025  
**Full Document**: See [COLLATED_TEST_PLAN.md](COLLATED_TEST_PLAN.md)

---

## Overview

This is a quick reference guide for the complete test suite for both AudioBrowser applications.

### Total Test Coverage: 345 Test Cases

| Application | Features | Test Cases |
|------------|----------|------------|
| **AudioBrowserOrig** | 10 major features | 319 tests |
| **AudioBrowser-QML** | 1 major feature | 26 tests |

---

## AudioBrowserOrig Test Plans (319 tests)

| # | Feature | Tests | Priority | Status | Test Plan Link |
|---|---------|-------|----------|--------|----------------|
| 1 | Clickable Status Bar Items | 23 | High | ✅ Ready | [TEST_PLAN_CLICKABLE_STATUS.md](AudioBrowserOrig/docs/test_plans/TEST_PLAN_CLICKABLE_STATUS.md) |
| 2 | Now Playing Panel | 29 | High | ✅ Ready | [TEST_PLAN_NOW_PLAYING_PANEL.md](AudioBrowserOrig/docs/test_plans/TEST_PLAN_NOW_PLAYING_PANEL.md) |
| 3 | Performance Improvements | 41 | **Critical** | ✅ Ready | [TEST_PLAN_PERFORMANCE_IMPROVEMENTS.md](AudioBrowserOrig/docs/test_plans/TEST_PLAN_PERFORMANCE_IMPROVEMENTS.md) |
| 4 | Practice Goals | 40 | High | ✅ Ready | [TEST_PLAN_PRACTICE_GOALS.md](AudioBrowserOrig/docs/test_plans/TEST_PLAN_PRACTICE_GOALS.md) |
| 5 | Setlist Builder | 43 | High | ✅ Ready | [TEST_PLAN_SETLIST_BUILDER.md](AudioBrowserOrig/docs/test_plans/TEST_PLAN_SETLIST_BUILDER.md) |
| 6 | Spectral Analysis | 35 | Medium | ✅ Ready | [TEST_PLAN_SPECTRAL_ANALYSIS.md](AudioBrowserOrig/docs/test_plans/TEST_PLAN_SPECTRAL_ANALYSIS.md) |
| 7 | Stereo Waveform View | 15 | Medium | ✅ Ready | [TEST_PLAN_STEREO_WAVEFORM.md](AudioBrowserOrig/docs/test_plans/TEST_PLAN_STEREO_WAVEFORM.md) |
| 8 | Sync Improvements | 38 | Medium | ✅ Ready | [TEST_PLAN_SYNC_IMPROVEMENTS.md](AudioBrowserOrig/docs/test_plans/TEST_PLAN_SYNC_IMPROVEMENTS.md) |
| 9 | Tempo & Metronome | 31 | Medium | ✅ Ready | [TEST_PLAN_TEMPO_METRONOME.md](AudioBrowserOrig/docs/test_plans/TEST_PLAN_TEMPO_METRONOME.md) |
| 10 | Workspace Layouts & Progress | 24 | Medium | ✅ Ready | [TEST_PLAN_WORKSPACE_PROGRESS.md](AudioBrowserOrig/docs/test_plans/TEST_PLAN_WORKSPACE_PROGRESS.md) |

---

## AudioBrowser-QML Test Plans (26 tests)

| # | Feature | Tests | Priority | Status | Test Plan Link |
|---|---------|-------|----------|--------|----------------|
| 11 | Spectrogram Overlay | 26 | High | ✅ Ready | [TEST_PLAN_SPECTROGRAM.md](AudioBrowser-QML/docs/test_plans/TEST_PLAN_SPECTROGRAM.md) |

---

## Test Execution Time Estimates

| Testing Level | Duration | Test Cases | Description |
|--------------|----------|------------|-------------|
| **Smoke Test** | 1 hour | 7 critical | Basic functionality verification |
| **Essential Test** | 4 hours | ~50 high priority | Core features and workflows |
| **Comprehensive Test** | 16-24 hours | 345 all tests | Complete test suite |
| **With Bug Reproduction** | 24-36 hours | 345 + bug verification | Full testing with issue tracking |

---

## Testing Priority Guide

### Critical Priority (Must Pass for Release)
- **Performance Improvements** (41 tests) - Core functionality affecting all users
- Key integration tests across all features

### High Priority (Should Pass for Quality Release)
- **Practice Goals** (40 tests) - Complex data tracking
- **Setlist Builder** (43 tests) - Data persistence and export
- **Now Playing Panel** (29 tests) - Core workflow enhancement
- **Clickable Status Bar** (23 tests) - User interface enhancement
- **Spectrogram Overlay** (26 tests) - QML visualization

### Medium Priority (Important for User Experience)
- **Spectral Analysis** (35 tests) - Advanced audio analysis
- **Sync Improvements** (38 tests) - Cloud synchronization
- **Tempo & Metronome** (31 tests) - Musical features
- **Workspace Layouts** (24 tests) - UI customization
- **Stereo Waveform** (15 tests) - Audio visualization

---

## Test Environment Requirements

### Minimum Requirements
- **CPU**: 4-core processor
- **RAM**: 8GB
- **Disk**: 10GB free space
- **Display**: 1920x1080 resolution
- **OS**: Windows, macOS, or Linux
- **Python**: 3.8+
- **PyQt6**: Latest version

### Test Data Needed
- **Small library**: 10-50 files (~50-250 MB)
- **Medium library**: 100-500 files (~500 MB - 2.5 GB)
- **Large library**: 1000+ files (~5 GB+)
- **Practice folders**: Multiple dated folders
- **Mixed content**: WAV and MP3, mono and stereo files

---

## Quick Start Testing Guide

### Step 1: Pre-Testing Setup (15 minutes)
1. ☐ Install latest AudioBrowser build
2. ☐ Prepare test data (small, medium, large libraries)
3. ☐ Set up test tracking spreadsheet
4. ☐ Review test plans for features you'll test
5. ☐ Set up screen recording for bug documentation

### Step 2: Smoke Test (1 hour)
Execute 7 critical tests:
1. ☐ Application launches without errors
2. ☐ Can open and browse practice folder
3. ☐ Can play audio files successfully
4. ☐ Can add and save annotations
5. ☐ Can mark best takes
6. ☐ Performance acceptable with 100 files
7. ☐ No crashes in basic workflow

### Step 3: Feature Testing (4-20 hours)
Choose your testing depth:
- **Essential** (4 hours): Test high-priority features
- **Thorough** (8 hours): Test critical + high priority
- **Comprehensive** (16-20 hours): All 345 test cases

### Step 4: Bug Reporting and Tracking
For each bug found:
1. Document steps to reproduce
2. Take screenshots/videos
3. Rate severity (Critical/Major/Minor/Cosmetic)
4. File in bug tracking system
5. Note any workarounds

### Step 5: Test Summary and Sign-Off
1. ☐ Complete test execution tracking
2. ☐ Calculate pass rates for each feature
3. ☐ Document all bugs with status
4. ☐ Create test summary report
5. ☐ Get sign-off from QA lead

---

## Key Keyboard Shortcuts to Test

| Shortcut | Function |
|----------|----------|
| `Ctrl+Shift+G` | Practice Goals dialog |
| `Ctrl+Shift+S` | Practice Statistics |
| `Ctrl+Shift+L` | Save Window Layout |
| `Ctrl+Shift+R` | Restore Window Layout |
| `Ctrl+Shift+H` | Documentation Browser |
| `Space` | Play/Pause |
| `N` | Add annotation |

---

## Common Test Scenarios

### Scenario 1: First-Time User
1. Install application
2. Open practice folder
3. Browse and play files
4. Add annotations
5. Mark best takes
6. Create setlist

### Scenario 2: Power User
1. Open large library (1000+ files)
2. Verify performance
3. Set practice goals
4. Review statistics
5. Create complex setlist
6. Export for performance

### Scenario 3: Band Practice
1. Open practice folder
2. Real-time annotation
3. Use Now Playing Panel
4. Mark best takes
5. Add notes
6. Save and sync

---

## Bug Severity Definitions

| Severity | Definition | Example |
|----------|------------|---------|
| **Critical** | App crashes, data loss, core feature broken | Application won't start, data corruption |
| **Major** | Feature doesn't work, difficult workaround | Can't add annotations, sync fails |
| **Minor** | Small issue, workaround available | UI text overlap, slow operation |
| **Cosmetic** | Visual/text issue only | Spelling error, color mismatch |

---

## Test Status Tracking

Use this checklist to track your overall progress:

### AudioBrowserOrig Features
- [ ] 1. Clickable Status Bar (23 tests)
- [ ] 2. Now Playing Panel (29 tests)
- [ ] 3. Performance Improvements (41 tests) - **CRITICAL**
- [ ] 4. Practice Goals (40 tests)
- [ ] 5. Setlist Builder (43 tests)
- [ ] 6. Spectral Analysis (35 tests)
- [ ] 7. Stereo Waveform (15 tests)
- [ ] 8. Sync Improvements (38 tests)
- [ ] 9. Tempo & Metronome (31 tests)
- [ ] 10. Workspace & Progress (24 tests)

### AudioBrowser-QML Features
- [ ] 11. Spectrogram Overlay (26 tests)

### Testing Complete
- [ ] All test cases executed
- [ ] All bugs documented
- [ ] Test summary created
- [ ] Sign-off obtained

---

## Resources

### Documentation
- **Full Test Plan**: [COLLATED_TEST_PLAN.md](COLLATED_TEST_PLAN.md) (complete details)
- **AudioBrowserOrig Docs**: [AudioBrowserOrig/docs/INDEX.md](AudioBrowserOrig/docs/INDEX.md)
- **AudioBrowser-QML Docs**: [AudioBrowser-QML/docs/INDEX.md](AudioBrowser-QML/docs/INDEX.md)

### Test Plans Location
- **AudioBrowserOrig**: `AudioBrowserOrig/docs/test_plans/`
- **AudioBrowser-QML**: `AudioBrowser-QML/docs/test_plans/`

### Templates
- **Master Test Tracking**: See [COLLATED_TEST_PLAN.md](COLLATED_TEST_PLAN.md#master-test-tracking-template)
- **Bug Reporting**: See [COLLATED_TEST_PLAN.md](COLLATED_TEST_PLAN.md#bug-reporting-template)

---

## Contact

For questions about testing or to report issues:
- **GitHub Repository**: https://github.com/TheMikaus/BandTools
- **Issues**: Create a new issue on GitHub
- **Test Plans**: This directory

---

**Document Version**: 1.0  
**Last Updated**: January 2025  
**Maintained by**: BandTools Development Team
