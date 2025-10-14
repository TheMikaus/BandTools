# PolyRhythmMetronome Android - Documentation Index

This directory contains all documentation for the Android version of PolyRhythmMetronome.

## Documentation Structure

### User Guides
User-facing documentation for end users and musicians.

- [Quick Start Guide](user_guides/QUICK_START.md) - Get started quickly
- [User Manual](user_guides/USER_MANUAL.md) - Complete feature guide
- [Timing Diagnostics Guide](user_guides/TIMING_DIAGNOSTICS_GUIDE.md) - NEW: Diagnosing and troubleshooting timing issues (v1.7.0)
- [Accent Frequency Guide](user_guides/accent_frequency_guide.md) - Using different pitches for accent beats in tone mode
- [MP3 Tick Sounds Guide](user_guides/MP3_TICK_SOUNDS.md) - Using custom MP3 metronome sounds
- [v1.2 Improvements Guide](user_guides/v1.2_improvements.md) - What's new in v1.2 with visual examples
- [Color and Flash Guide](user_guides/color_and_flash_guide.md) - Custom colors and visual feedback (v1.1)
- [FAQ](user_guides/FAQ.md) - Frequently asked questions
- [Kindle Fire Kivy Launcher Guide](user_guides/KINDLE_FIRE_KIVY_LAUNCHER_GUIDE.md) - Complete setup for testing on Kindle Fire HD 10 with Kivy Launcher
- [Local Development on Windows](user_guides/LOCAL_DEVELOPMENT_WINDOWS.md) - Build, test, and iterate locally on Windows
- [GitHub Actions Build Guide](user_guides/GITHUB_ACTIONS_BUILD_GUIDE.md) - Building APKs without local Linux setup (cloud builds)

### Technical Documentation
Developer-focused documentation for understanding and modifying the code.

- [Architecture Overview](technical/ARCHITECTURE.md) - System design and structure
- [Audio Implementation](technical/AUDIO_IMPLEMENTATION.md) - Audio playback system details (v1.1)
- [Timing Debug Implementation](technical/TIMING_DEBUG_IMPLEMENTATION.md) - NEW: v1.7.0 timing diagnostics system implementation details
- [Per-Layer Threading](technical/PER_LAYER_THREADING.md) - v1.6.0 per-layer threading architecture explanation
- [AudioTrack Reliability Fix](technical/AUDIOTRACK_RELIABILITY_FIX.md) - v1.6.0 tone playback consistency improvements
- [MP3 MediaCodec Implementation](technical/MP3_MEDIACODEC_IMPLEMENTATION.md) - Native Android MP3 decoding technical details
- [V1.2 Changes](technical/V1.2_CHANGES.md) - Technical details of v1.2 improvements and bug fixes
- [UI Improvements v1.6](technical/UI_IMPROVEMENTS_V1.6.md) - Background colors, color distance, master volume, and overflow fix
- [Porting Analysis](technical/PORTING_ANALYSIS.md) - Desktop to Android porting decisions
- [Build Guide](technical/BUILD_GUIDE.md) - Building and deploying
- [Setup Script](technical/SETUP_SCRIPT.md) - Automated dependency setup technical details

### Test Plans
Quality assurance and testing documentation.

- [Test Plan](test_plans/TEST_PLAN.md) - Testing strategy and cases
- [Timing Diagnostics Test Plan](test_plans/timing_diagnostics_test_plan.md) - NEW: Test plan for v1.7.0 timing diagnostics feature
- [v1.6 Per-Layer Threading Test Plan](test_plans/v1.6_per_layer_threading_test_plan.md) - Comprehensive test plan for v1.6.0 per-layer threading and AudioTrack fixes
- [Bug Fixes v1.1 Test Plan](test_plans/bug_fixes_v1.1_test_plan.md) - Comprehensive test plan for v1.1 bug fixes
- [Bug Fixes v1.2 Test Plan](test_plans/bug_fixes_v1.2_test_plan.md) - Comprehensive test plan for v1.2 UI improvements and bug fixes
- [Bug Fix v1.5 Test Plan](test_plans/bug_fix_v1.5_test_plan.md) - Tone playback buffer size fix
- [MP3 Tick Test Plan](test_plans/MP3_TICK_TEST_PLAN.md) - MP3 tick sounds feature testing
- [Feature Enhancements Test Plan](test_plans/feature_enhancements_test_plan.md) - Test plan for accent frequency, auto-restart, and UI improvements
- [Device Compatibility](test_plans/DEVICE_COMPATIBILITY.md) - Tested devices

## Quick Links

- [Main README](../README.md) - Installation and basic usage
- [Setup Script README](../SETUP_SCRIPT_README.md) - Automated dependency setup
- [Desktop Version](../../Desktop/README.md) - Desktop application documentation
- [Buildozer Spec](../buildozer.spec) - Build configuration

## Contributing

When adding new documentation:
1. Place it in the appropriate subfolder (user_guides, technical, or test_plans)
2. Update this index
3. Follow existing documentation style
4. Use clear headers and examples
