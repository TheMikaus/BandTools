# PolyRhythmMetronome Android - Documentation Index

This directory contains all documentation for the Android version of PolyRhythmMetronome.

## Documentation Structure

### User Guides
User-facing documentation for end users and musicians.

- [Quick Start Guide](user_guides/QUICK_START.md) - Get started quickly
- [User Manual](user_guides/USER_MANUAL.md) - Complete feature guide
- [MP3 Tick Sounds Guide](user_guides/MP3_TICK_SOUNDS.md) - NEW: Using custom MP3 metronome sounds
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
- [MP3 MediaCodec Implementation](technical/MP3_MEDIACODEC_IMPLEMENTATION.md) - NEW: Native Android MP3 decoding technical details
- [V1.2 Changes](technical/V1.2_CHANGES.md) - Technical details of v1.2 improvements and bug fixes
- [Porting Analysis](technical/PORTING_ANALYSIS.md) - Desktop to Android porting decisions
- [Build Guide](technical/BUILD_GUIDE.md) - Building and deploying
- [Setup Script](technical/SETUP_SCRIPT.md) - Automated dependency setup technical details

### Test Plans
Quality assurance and testing documentation.

- [Test Plan](test_plans/TEST_PLAN.md) - Testing strategy and cases
- [Bug Fixes v1.1 Test Plan](test_plans/bug_fixes_v1.1_test_plan.md) - Comprehensive test plan for v1.1 bug fixes
- [Bug Fixes v1.2 Test Plan](test_plans/bug_fixes_v1.2_test_plan.md) - NEW: Comprehensive test plan for v1.2 UI improvements and bug fixes
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
