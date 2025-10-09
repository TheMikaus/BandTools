# Quick Verification Guide

## Are You Getting QML Errors?

If you see errors like:
- "Duplicate signal name"
- "Cannot assign to non-existent property 'info'"
- "Type LibraryTab unavailable"

## Quick Fix - Just Run This:

```bash
cd AudioBrowserAndAnnotation/AudioBrowser-QML
python3 verify_qml_installation.py
```

## Expected Result

You should see all green checkmarks (✓):

```
✓ QML Fixes: All checks passed
✓ Environment: All checks passed
✓ Application Files: All checks passed

✓ SUCCESS: AudioBrowser-QML is ready to run!
```

## If All Checks Pass

Great! The fixes are in place. If you're still seeing errors:

1. **Clear your cache:**
   ```bash
   # Windows
   del /s /q %TEMP%\*.qmlc
   
   # Linux/macOS
   rm -rf ~/.cache/BandTools/*.qmlc
   rm -rf /tmp/*.qmlc
   ```

2. **Restart your terminal** and try again

3. **Update PyQt6:**
   ```bash
   pip install --upgrade PyQt6
   ```

## If Some Checks Fail

See the detailed troubleshooting guide:
```bash
# Read the guide
cat docs/user_guides/QML_ERROR_TROUBLESHOOTING.md

# Or open in your browser
# File location: docs/user_guides/QML_ERROR_TROUBLESHOOTING.md
```

## Still Having Issues?

1. Make sure you have the latest code:
   ```bash
   git pull origin main
   ```

2. Check you're on the right branch:
   ```bash
   git status
   git log --oneline -3
   ```

3. Run the detailed validation:
   ```bash
   python3 validate_qml_fixes.py
   ```

## Quick Links

- [Full Troubleshooting Guide](docs/user_guides/QML_ERROR_TROUBLESHOOTING.md)
- [Technical Fix Details](docs/QML_COMPILATION_FIX.md)
- [Button Style Reference](docs/STYLED_BUTTON_VARIANTS.md)

## One-Liner Verification

```bash
python3 verify_qml_installation.py && echo "Ready to run!" && python3 main.py
```

This will:
1. Verify the installation
2. Print "Ready to run!" if successful
3. Launch the application

---

**TL;DR**: Run `python3 verify_qml_installation.py` and it will tell you if everything is OK.
