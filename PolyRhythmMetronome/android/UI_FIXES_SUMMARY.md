# Android UI Fixes and Enhancements - Summary

## Date: 2025-10-13

## Issues Addressed

### 1. Tone Mode Layout Fix ✓

**Problem:** When using tone mode, the two frequency input boxes (regular and accent) were stacked vertically, taking up too much space.

**Solution:**
- Changed `freq_box` orientation from `'vertical'` to `'horizontal'`
- Reduced font size from `11sp` to `10sp`
- Added `size_hint_x=0.5` to both input boxes to share width equally
- Shortened hint text from "Acc Hz" to "Acc" to save space

**Code Changes:**
```python
# Before:
freq_box = BoxLayout(orientation='vertical', spacing='1dp')
self.freq_input = TextInput(..., font_size='11sp', hint_text='Hz')
self.accent_freq_input = TextInput(..., font_size='11sp', hint_text='Acc Hz')

# After:
freq_box = BoxLayout(orientation='horizontal', spacing='2dp')
self.freq_input = TextInput(..., font_size='10sp', hint_text='Hz', size_hint_x=0.5)
self.accent_freq_input = TextInput(..., font_size='10sp', hint_text='Acc', size_hint_x=0.5)
```

**Visual Impact:**
- Inputs now appear side-by-side: `[880][880]` instead of stacked
- More compact UI, especially important on smaller screens
- Better space utilization in the layer widget

---

### 2. Color Picker Conversion Fix ✓

**Problem:** The color selected from the color picker wheel didn't match the color displayed on the panel after selection. This was due to rounding errors and color space conversion inconsistencies.

**Solution:**
- Added `round()` to RGB-to-hex conversion to prevent rounding errors
- Changed button color update to use `_hex_to_rgba(hex_color)` instead of direct ColorPicker color
- Applied same conversion to canvas background color updates

**Code Changes:**
```python
# Before:
hex_color = '#{:02x}{:02x}{:02x}'.format(int(r*255), int(g*255), int(b*255))
self.color_button.background_color = color_picker.color
Color(r, g, b, 0.3)

# After:
hex_color = '#{:02x}{:02x}{:02x}'.format(
    int(round(r * 255)), 
    int(round(g * 255)), 
    int(round(b * 255))
)
self.color_button.background_color = self._hex_to_rgba(hex_color)
rgba_from_hex = self._hex_to_rgba(hex_color)
Color(rgba_from_hex[0], rgba_from_hex[1], rgba_from_hex[2], 0.3)
```

**Why This Works:**
1. `round()` prevents 0.9999... from being truncated to 254 instead of 255
2. Converting hex back to RGBA ensures consistency across all color representations
3. All color displays (button, canvas, storage) now use the same hex-derived values

---

### 3. Ticks Directory Auto-Creation ✓

**Problem:** If the `ticks/` directory didn't exist when the app started, it would silently fail to load tick sounds. Users had no way to know they needed to create the directory.

**Solution:**
- Added directory creation in `_scan_ticks_folder()` method
- Includes error handling and logging
- Creates directory with `exist_ok=True` to prevent errors if it already exists

**Code Changes:**
```python
def _scan_ticks_folder(self):
    """Scan the ticks folder for MP3 and WAV files and identify pairs"""
    # Create ticks directory if it doesn't exist
    if not os.path.exists(self.ticks_dir):
        try:
            os.makedirs(self.ticks_dir, exist_ok=True)
            print(f"[audio] Created ticks directory: {self.ticks_dir}")
        except Exception as e:
            print(f"[audio] Could not create ticks directory: {e}")
        return
```

**Benefits:**
- No manual directory creation needed
- Clear log messages for debugging
- Graceful handling of permission errors

---

### 4. Baseline Tick Sounds Deployment ✓

**Problem:** No baseline tick sounds were included with the app, making the mp3_tick feature unusable out of the box.

**Solution:**
1. **Generated Baseline Tick Sounds:**
   - `click.wav` - Simple click (single file, 1200 Hz)
   - `woodblock_1.wav` / `woodblock_2.wav` - Woodblock pair (900/700 Hz)
   - `cowbell_1.wav` / `cowbell_2.wav` - Cowbell pair (800/600 Hz)
   - `hiclick_1.wav` / `hiclick_2.wav` - High click pair (1500/1000 Hz)

2. **Enhanced Audio Format Support:**
   - Updated `Mp3TickCache` to scan for both `.mp3` AND `.wav` files
   - Renamed variable from `mp3_files` to `audio_files` for clarity
   - Updated class docstring to reflect WAV support

3. **Build Configuration:**
   - Updated `buildozer.spec` to include `.wav` in `source.include_exts`
   - Existing pattern `ticks/*` already includes all files in ticks folder

**Code Changes:**
```python
# Before:
source.include_exts = py,png,jpg,kv,atlas,json,mp3
for filename in os.listdir(self.ticks_dir):
    if filename.lower().endswith('.mp3'):

# After:
source.include_exts = py,png,jpg,kv,atlas,json,mp3,wav
for filename in os.listdir(self.ticks_dir):
    if filename.lower().endswith(('.mp3', '.wav')):
```

**Tick Sound Characteristics:**
- All sounds are short (40-150ms) for crisp metronome clicks
- Uses exponential decay envelopes for natural attack
- Different harmonic content creates distinct timbres:
  - Click: Pure sine wave
  - Woodblock: Mixed harmonics (fundamental + odd harmonics)
  - Cowbell: Inharmonic partials for metallic sound
  - HiClick: High frequency, very short duration

**Files Added:**
- `PolyRhythmMetronome/android/ticks/*.wav` (7 files, ~52KB total)
- `PolyRhythmMetronome/Desktop/ticks/*.wav` (7 files, ~52KB total)

---

## Testing Recommendations

### Test Case 1: Tone Mode Layout
1. Launch app and add a new layer
2. Select "tone" mode
3. Verify frequency inputs appear side-by-side
4. Verify inputs are smaller and more compact
5. Try entering different frequencies in both boxes

### Test Case 2: Color Picker
1. Add a layer and click the color button
2. Select a bright, saturated color from the wheel
3. Click OK
4. Verify the button color matches what you selected
5. Try multiple colors (red, blue, green, yellow)

### Test Case 3: Ticks Directory
1. Uninstall app completely
2. Reinstall app
3. Check logs for "Created ticks directory" message
4. Verify ticks directory exists in app files

### Test Case 4: Baseline Ticks
1. Add a layer
2. Select "mp3_tick" mode
3. Verify dropdown shows: click, cowbell, hiclick, woodblock
4. Select each tick and test playback
5. For paired ticks (woodblock, cowbell, hiclick), verify:
   - First beat uses _1 file (higher pitch)
   - Other beats use _2 file (lower pitch)

### Test Case 5: WAV File Support
1. Add a custom `.wav` file to ticks folder
2. Restart app
3. Verify custom tick appears in dropdown
4. Test playback of custom tick

---

## Technical Notes

### Color Conversion Details
- Kivy ColorPicker uses float values (0.0 - 1.0) in RGB space
- Hex colors use integers (0 - 255)
- Floating point precision can cause 254.9999 vs 255.0 differences
- Round-trip conversion (RGBA → hex → RGBA) ensures consistency

### Audio File Format Support
- **WAV**: Native Python `wave` module, always supported
- **MP3**: Android MediaCodec API (Android only), requires Android 5.0+
- Both formats are resampled to 44100 Hz if needed
- Both formats are converted to mono if stereo

### Build System Impact
- Adding `.wav` to `source.include_exts` increases APK size by ~50KB
- Pattern `ticks/*` ensures all tick files are included
- Files are deployed to app's internal storage on install

---

## Backward Compatibility

All changes are backward compatible:
- Existing saved rhythms will load correctly
- Tone mode still works if users have data from old version
- Color format (hex strings) unchanged
- MP3 files still supported alongside WAV files

---

## Files Modified

1. `PolyRhythmMetronome/android/main.py`
   - Line 534: Updated class docstring
   - Lines 544-552: Added directory creation
   - Lines 555-557: Support WAV files
   - Lines 617-620: Updated function docstring
   - Lines 1253-1279: Changed tone mode layout
   - Lines 1341-1365: Fixed color conversion

2. `PolyRhythmMetronome/android/buildozer.spec`
   - Line 16: Added `wav` to included extensions

3. `PolyRhythmMetronome/android/ticks/README.md`
   - Updated to document baseline ticks and WAV support

4. `PolyRhythmMetronome/android/ticks/*.wav` (7 new files)
5. `PolyRhythmMetronome/Desktop/ticks/*.wav` (7 new files)

---

## Future Enhancements

Possible future improvements:
1. Add MP3 conversion tool in app settings
2. Allow users to record custom tick sounds
3. Add more baseline tick varieties (rim shot, clap, etc.)
4. Support for stereo tick sounds (currently converted to mono)
5. Volume normalization across different tick files
