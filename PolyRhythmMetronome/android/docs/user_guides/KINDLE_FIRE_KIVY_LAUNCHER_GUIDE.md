# Kivy Launcher Setup for Kindle Fire HD 10

This guide provides step-by-step instructions for setting up and using Kivy Launcher on Kindle Fire HD 10 for testing the PolyRhythmMetronome app without building APKs.

## Overview

Kivy Launcher allows you to run Python/Kivy apps directly on your Kindle Fire HD 10 without building APKs. This is perfect for:
- **Quick testing** - No build time required
- **Rapid iteration** - Just copy updated Python files
- **Real device testing** - Test on actual hardware

**Important**: Kindle Fire devices use Amazon's Fire OS and don't have Google Play Store, so you'll need to sideload Kivy Launcher.

---

## Prerequisites

- Kindle Fire HD 10 tablet
- Windows PC with USB cable
- ADB (Android Debug Bridge) installed on Windows
- Python 3.8+ with Kivy and NumPy installed

---

## Part 1: Enable Developer Options on Kindle Fire HD 10

### Step 1: Access Device Settings

1. **Unlock your Kindle Fire HD 10**
2. **Swipe down** from the top of the screen
3. Tap **Settings** (gear icon)
4. Scroll down and tap **Device Options**

### Step 2: Enable Developer Options

1. Tap **About Fire Tablet**
2. Tap **Serial Number** **7 times rapidly**
   - You'll see a message: "You are now a developer!"
3. Press **Back** button to return to Device Options
4. You should now see **Developer Options** in the menu

### Step 3: Enable ADB Debugging

1. Tap **Developer Options**
2. Toggle **Enable ADB** to ON
3. Toggle **Apps from Unknown Sources** to ON (if available)
   - This allows installation of apps not from Amazon Appstore

**Note**: The option names may vary slightly depending on your Fire OS version.

---

## Part 2: Set Up ADB on Windows

### Step 1: Install ADB

**Option A: Using Android SDK Platform Tools (Recommended)**

1. **Download Android SDK Platform Tools**:
   - Go to: https://developer.android.com/studio/releases/platform-tools
   - Download "SDK Platform-Tools for Windows"
   - Extract the ZIP file to a folder (e.g., `C:\platform-tools`)

2. **Add ADB to Windows PATH**:
   - Press `Win + X` and select "System"
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "System variables", find "Path" and click "Edit"
   - Click "New" and add: `C:\platform-tools`
   - Click "OK" to save

3. **Verify installation**:
   ```powershell
   adb version
   ```
   You should see the ADB version number.

**Option B: Using Chocolatey (Alternative)**

If you have Chocolatey package manager:
```powershell
choco install adb
```

### Step 2: Connect Kindle Fire to PC

1. **Connect USB cable** from Kindle Fire to Windows PC
2. **On Kindle Fire**, you may see a prompt "Allow USB debugging?"
   - Tap "OK" or "Allow"
   - Check "Always allow from this computer" if desired

3. **Verify connection** on Windows:
   ```powershell
   adb devices
   ```
   
   You should see output like:
   ```
   List of devices attached
   G0ABC12345678DEF    device
   ```

**Troubleshooting**:
- If device shows as "unauthorized", check Kindle for the USB debugging prompt
- If device not found, try a different USB cable or port
- Restart ADB: `adb kill-server` then `adb start-server`

---

## Part 3: Install Kivy Launcher on Kindle Fire HD 10

Since Kindle Fire doesn't have Google Play Store, you need to sideload Kivy Launcher.

### Step 1: Download Kivy Launcher APK

1. **On your Windows PC**, download Kivy Launcher APK from:
   - Official Kivy GitHub releases: https://github.com/kivy/kivy-launcher/releases
   - Or from APKMirror: https://www.apkmirror.com/apk/kivy/kivy-launcher/
   
   Look for the latest `kivy-launcher-X.X.X.apk` file

2. **Save the APK** to an easy-to-find location (e.g., `C:\Downloads\kivy-launcher.apk`)

### Step 2: Install Kivy Launcher via ADB

1. **Open PowerShell or Command Prompt**

2. **Navigate to APK location**:
   ```powershell
   cd C:\Downloads
   ```

3. **Install the APK**:
   ```powershell
   adb install kivy-launcher.apk
   ```
   
   You should see:
   ```
   Performing Streamed Install
   Success
   ```

**Troubleshooting**:
- If you get "INSTALL_FAILED_UPDATE_INCOMPATIBLE", uninstall old version first:
  ```powershell
  adb uninstall org.kivy.pygame
  adb install kivy-launcher.apk
  ```
- If "INSTALL_FAILED_INSUFFICIENT_STORAGE", free up space on Kindle

### Step 3: Verify Installation

1. **On Kindle Fire**, go to Apps
2. Find **Kivy Launcher** icon
3. **Tap to open** - You should see a list (empty for now)

---

## Part 4: Set Up File Structure for PolyRhythmMetronome

Kivy Launcher expects apps in a specific directory structure on the device.

### Step 1: Create App Directory on Kindle Fire

```powershell
# Create the directory structure
adb shell mkdir -p /sdcard/kivy/polyrhythm
```

### Step 2: Copy App Files

Navigate to your PolyRhythmMetronome project folder:

```powershell
# Navigate to project
cd C:\path\to\BandTools\PolyRhythmMetronome\android

# Copy main.py to Kindle Fire
adb push main.py /sdcard/kivy/polyrhythm/main.py

# If you have any additional Python files, copy them too
# adb push other_file.py /sdcard/kivy/polyrhythm/other_file.py
```

You should see:
```
main.py: 1 file pushed. X KB/s (XXXXX bytes in X.XXXs)
```

### Step 3: Verify Files on Device

```powershell
# List files to verify
adb shell ls -l /sdcard/kivy/polyrhythm/
```

You should see `main.py` listed.

---

## Part 5: Testing the App

### Step 1: Launch from Kivy Launcher

1. **Open Kivy Launcher** on your Kindle Fire
2. You should see **"polyrhythm"** in the app list
3. **Tap "polyrhythm"** to launch the app

The PolyRhythmMetronome app should start running!

### Step 2: Test Functionality

Test these features on the Kindle Fire:
- ✓ Touch controls (buttons, sliders)
- ✓ BPM presets
- ✓ Multiple layers
- ✓ Sound generation (tone and drum modes)
- ✓ Volume controls
- ✓ Mute buttons
- ✓ Save/Load functionality
- ✓ Orientation (portrait and landscape)

### Step 3: Check for Issues

**Common issues and solutions**:

**App doesn't appear in Kivy Launcher**:
- Check file path: `adb shell ls /sdcard/kivy/polyrhythm/main.py`
- Ensure directory name is exactly: `/sdcard/kivy/polyrhythm/`
- Restart Kivy Launcher

**App crashes on start**:
- Check ADB logs:
  ```powershell
  adb logcat | Select-String -Pattern "python"
  ```
- Look for Python errors in the output

**No sound**:
- Check device volume
- Test with headphones
- Verify audio permissions in Kindle settings

**Screen layout issues**:
- Rotate device to test both orientations
- Check if UI elements are visible and accessible

---

## Part 6: Iterative Development Workflow

This is where Kivy Launcher shines - rapid iteration!

### Development Loop

1. **Edit code on Windows**
   ```
   Open main.py in your editor (VS Code, PyCharm, etc.)
   Make changes
   Save
   ```

2. **Test on desktop** (optional but recommended)
   ```powershell
   python main.py
   ```
   Quick sanity check before deploying.

3. **Copy updated file to Kindle**
   ```powershell
   adb push main.py /sdcard/kivy/polyrhythm/main.py
   ```

4. **Relaunch on Kindle Fire**
   - In Kivy Launcher, tap "polyrhythm" again
   - The updated app loads immediately

5. **Repeat** - Fast iteration cycle (30-60 seconds total)

### Example Workflow Session

```
Time: 0:00 - Edit main.py (add new BPM value to presets)
Time: 0:20 - Test on desktop: python main.py
Time: 0:45 - Copy to Kindle: adb push main.py /sdcard/kivy/polyrhythm/main.py
Time: 0:50 - Launch on Kindle from Kivy Launcher
Time: 1:00 - Test feature on real hardware
Time: 1:30 - Confirmed working!

Total iteration time: 1 minute 30 seconds
No APK build required!
```

---

## Part 7: Advanced Usage

### Viewing Debug Output

To see Python print statements and errors from the Kindle:

```powershell
# Start logcat before launching the app
adb logcat -s python:* *:E

# Launch app on Kindle Fire
# Logs will appear in the terminal
```

### Copying Multiple Files

If your app has multiple Python files:

```powershell
# Copy all Python files at once
cd C:\path\to\BandTools\PolyRhythmMetronome\android
adb push *.py /sdcard/kivy/polyrhythm/
```

### Including Assets

If you add images, sounds, or other assets:

```powershell
# Create assets folder
adb shell mkdir -p /sdcard/kivy/polyrhythm/assets

# Copy assets
adb push assets/my_sound.wav /sdcard/kivy/polyrhythm/assets/
```

### Cleaning Up Old Files

```powershell
# Remove app from Kivy Launcher
adb shell rm -rf /sdcard/kivy/polyrhythm

# Reinstall fresh
adb shell mkdir -p /sdcard/kivy/polyrhythm
adb push main.py /sdcard/kivy/polyrhythm/main.py
```

---

## Part 8: Troubleshooting Guide

### Issue: "Device not found" in ADB

**Solutions**:
1. Check USB cable (try a different one - data cables, not charge-only)
2. Check USB port on PC
3. On Kindle: Settings → Device Options → Developer Options → Enable ADB
4. Restart ADB server:
   ```powershell
   adb kill-server
   adb start-server
   adb devices
   ```
5. Restart Kindle Fire

### Issue: "Access denied" when using ADB push

**Solutions**:
1. Check USB debugging authorization on Kindle
2. Try different path (some Fire OS versions use different locations):
   ```powershell
   adb push main.py /mnt/sdcard/kivy/polyrhythm/main.py
   ```

### Issue: Kivy Launcher shows blank screen

**Solutions**:
1. Verify file path is exactly: `/sdcard/kivy/polyrhythm/main.py`
2. Check file was copied successfully:
   ```powershell
   adb shell cat /sdcard/kivy/polyrhythm/main.py
   ```
3. Restart Kivy Launcher app
4. Force stop and clear cache:
   ```powershell
   adb shell pm clear org.kivy.pygame
   ```

### Issue: App crashes immediately

**Debugging steps**:
1. **Check logs**:
   ```powershell
   adb logcat -c  # Clear old logs
   adb logcat -s python:* AndroidRuntime:E *:F
   ```
   
2. **Launch app on Kindle** and watch logs for errors

3. **Common causes**:
   - Missing dependencies (Kivy Launcher includes Kivy and NumPy)
   - Syntax errors in Python code
   - Incompatible Kivy API calls

4. **Verify on desktop first**:
   ```powershell
   python main.py
   ```
   If it works on desktop, the issue is likely device-specific.

### Issue: No sound on Kindle Fire

**Solutions**:
1. Check device volume (both media and system volume)
2. Test with headphones plugged in
3. Verify audio isn't muted in the app
4. Check Fire OS audio permissions:
   - Settings → Apps & Notifications → Kivy Launcher → Permissions

### Issue: Touch controls not responsive

**Solutions**:
1. Try landscape orientation
2. Check if UI elements are properly sized for 1920x1200 screen
3. Test with simple tap on large button first
4. Verify in desktop version with mouse clicks

---

## Part 9: Kindle Fire HD 10 Specific Notes

### Fire OS Version Compatibility

- **Fire OS 7.x** (based on Android 9): Fully compatible
- **Fire OS 8.x** (based on Android 11): Fully compatible
- Kivy Launcher works on all recent Fire OS versions

### Screen Specifications

- **Resolution**: 1920x1200 pixels (224 PPI)
- **Size**: 10.1 inches
- **Aspect Ratio**: 16:10
- **Orientation**: Portrait and landscape supported

### Performance Considerations

The Kindle Fire HD 10 has:
- **CPU**: Octa-core 2.0 GHz
- **RAM**: 2GB or 3GB (depending on model)
- **Storage**: 32GB or 64GB

**Recommendation**: The metronome app runs smoothly on Kindle Fire HD 10. The hardware is more than sufficient for audio generation and UI updates.

### Permissions on Fire OS

Fire OS (Amazon's Android fork) handles permissions similarly to standard Android:
- Storage permissions: Required for save/load functionality
- Kivy Launcher should request these automatically when the app runs

---

## Part 10: Comparison with Other Methods

### Kivy Launcher vs. Building APKs

| Aspect | Kivy Launcher | Built APK |
|--------|---------------|-----------|
| **Setup time** | 15-20 minutes (one-time) | 30-60 minutes (first build) |
| **Iteration speed** | 30-60 seconds | 5-10 minutes (WSL2) or 30-60 min (GitHub Actions) |
| **App icon** | Generic Kivy icon | Custom app icon |
| **Distribution** | Development only | Can share APK file |
| **Permissions** | Limited | Full control |
| **Professional** | No | Yes |
| **Best for** | Testing and iteration | Final releases |

### When to Use Each Method

**Use Kivy Launcher for**:
- ✅ Rapid development iterations
- ✅ Testing code changes quickly
- ✅ Early-stage development
- ✅ Feature prototyping
- ✅ Bug fixing and debugging

**Build APK for**:
- ✅ Final testing before release
- ✅ Sharing with others
- ✅ Testing app icon and branding
- ✅ Testing all permissions
- ✅ Distribution via Amazon Appstore

### Recommended Workflow

```
Phase 1: Development (Desktop Testing)
  └─> Edit code, run python main.py
  └─> Iterate quickly (seconds)

Phase 2: Device Testing (Kivy Launcher)
  └─> Copy to Kindle with adb push
  └─> Test on real hardware (minutes)
  └─> Fix issues, repeat

Phase 3: Pre-release (Build APK)
  └─> Build with WSL2 or GitHub Actions
  └─> Final testing on device
  └─> Ready for distribution
```

---

## Quick Reference Card

### Essential Commands

```powershell
# Check device connection
adb devices

# Copy app to Kindle
cd C:\path\to\BandTools\PolyRhythmMetronome\android
adb push main.py /sdcard/kivy/polyrhythm/main.py

# View logs
adb logcat -s python:*

# Restart ADB
adb kill-server
adb start-server

# Check file on device
adb shell ls -l /sdcard/kivy/polyrhythm/

# Remove app
adb shell rm -rf /sdcard/kivy/polyrhythm
```

### File Paths

- **On Kindle Fire**: `/sdcard/kivy/polyrhythm/main.py`
- **App name in Kivy Launcher**: `polyrhythm`
- **On Windows**: `C:\path\to\BandTools\PolyRhythmMetronome\android\main.py`

### Typical Workflow

```
1. Edit: main.py in VS Code
2. Test: python main.py (desktop)
3. Deploy: adb push main.py /sdcard/kivy/polyrhythm/main.py
4. Launch: Open Kivy Launcher → Tap "polyrhythm"
5. Test: Use the app on Kindle Fire
6. Debug: adb logcat -s python:* (if needed)
7. Repeat: Back to step 1
```

---

## Additional Resources

### Official Documentation
- [Kivy Launcher GitHub](https://github.com/kivy/kivy-launcher)
- [Kivy Documentation](https://kivy.org/doc/stable/)
- [Amazon Fire Tablet Developer Guide](https://developer.amazon.com/docs/fire-tablets/ft-get-started.html)
- [ADB Documentation](https://developer.android.com/studio/command-line/adb)

### Community Resources
- [Kivy Discord](https://chat.kivy.org/)
- [Kivy Subreddit](https://www.reddit.com/r/kivy/)

### Related Guides
- [Local Development on Windows](LOCAL_DEVELOPMENT_WINDOWS.md) - Other testing methods
- [GitHub Actions Build Guide](GITHUB_ACTIONS_BUILD_GUIDE.md) - Cloud APK builds
- [Quick Start Guide](QUICK_START.md) - Basic app usage

---

## Summary

**Kivy Launcher on Kindle Fire HD 10** provides:

✅ **Fast iteration** - 30-60 second deploy cycle  
✅ **Real hardware testing** - Test on actual Kindle Fire  
✅ **No build required** - Skip the 5-60 minute APK build  
✅ **Simple workflow** - Just `adb push` and run  
✅ **Great for development** - Perfect for testing and debugging  

**Setup time**: 15-20 minutes (one-time)  
**Iteration time**: 30-60 seconds per change  

This is the **fastest way** to test your app on real Kindle Fire HD 10 hardware during development!
