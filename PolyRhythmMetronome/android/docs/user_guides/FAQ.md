# Frequently Asked Questions - PolyRhythmMetronome Android

## General Questions

### What is PolyRhythmMetronome?

PolyRhythmMetronome is a stereo metronome that allows you to play different rhythms in each ear. It's perfect for practicing polyrhythms, complex time signatures, or just having independent click tracks for left and right hands/feet.

### What's the difference between this and a regular metronome?

Regular metronomes play the same click in both ears. PolyRhythmMetronome allows you to set different subdivisions, frequencies, and volumes for each ear independently. This enables you to practice polyrhythms like 3 against 4, or to hear different parts of a complex rhythm separately.

### Why Android? Is there a desktop version?

Yes! There's a full-featured desktop version with even more capabilities. The Android version is optimized for mobile practice sessions and touch interaction. See the Desktop folder for the full version.

## Installation & Setup

### How do I install the app?

1. Download the APK file
2. On your device, go to Settings > Security and enable "Unknown Sources" or "Install from Unknown Sources"
3. Open the APK file to install
4. Find the app in your app drawer

### Does it work on Kindle Fire?

Yes! The app is specifically optimized for Kindle Fire HD 10. It works great on Fire OS.

### What Android version do I need?

Android 5.0 (Lollipop) or newer. This includes:
- Android 5.0 through 14
- Fire OS 5 through 8

### Why does it need storage permissions?

Storage permissions allow the app to save and load your rhythm patterns. Without these, you can use the app but won't be able to save your settings to files.

## Using the App

### How do I start?

1. Set your BPM (tempo) using the slider or preset buttons
2. Configure left and right ears (subdivision, frequency, volume)
3. Tap the green PLAY button
4. Watch the beat indicators flash with each click

### What is "subdivision"?

Subdivision determines how many clicks you hear per beat:
- **1** = One click every 4 beats (whole notes)
- **2** = One click every 2 beats (half notes)
- **4** = One click per beat (quarter notes) ← most common
- **8** = Two clicks per beat (eighth notes)
- **16** = Four clicks per beat (sixteenth notes)

### What is "frequency"?

Frequency is the pitch of the click tone, measured in Hertz (Hz):
- Lower numbers (220-440 Hz) = deeper, bass-like clicks
- Higher numbers (880-1760 Hz) = brighter, treble clicks
- Default: Left = 880 Hz, Right = 440 Hz

### How do I create a polyrhythm?

A polyrhythm is when two different rhythms play simultaneously. To create one:

1. Set BPM to 120 (or your preference)
2. Left ear: Set subdivision to 4 (plays 4 times per measure)
3. Right ear: Set subdivision to 8 (plays 8 times per measure)  
4. Play!

Common polyrhythms:
- **3 against 4**: Left=4, Right=8 (with proper timing)
- **3 against 2**: Left=4, Right=2 (with proper timing)
- **5 against 4**: More advanced

### What's the MUTE button for?

The MUTE button silences one ear temporarily. This is useful when:
- You want to practice with just one part
- You're setting up and don't want to hear both yet
- You want to check how one rhythm sounds alone

### Can I use headphones?

Yes! Headphones are recommended for the best stereo separation. With headphones, you'll clearly hear different rhythms in each ear.

## Features & Functions

### Does it save my settings?

Yes! The app auto-saves your current settings. When you close and reopen the app, your last configuration is restored.

### Can I save multiple rhythm patterns?

Yes! Use the SAVE button to save a pattern with a name, like "3against4" or "practice_pattern". You can then load any saved pattern using the LOAD button.

### Where are my files saved?

Files are saved to the app's private storage area. They're organized by filename and saved as JSON files.

### Can I share rhythm patterns with others?

The JSON files can be shared! However, in the current version, you'd need to manually locate and copy the files. A future version may add easier sharing.

### Can I export to audio?

No, the Android version doesn't support exporting to audio files. Use the desktop version if you need to export rhythm patterns as WAV files.

### Does it work offline?

Yes! The app works completely offline. No internet connection is required.

## Audio & Sound

### Why can't I hear anything?

Check these things:
1. Is your device volume turned up?
2. Are both ears MUTED? (toggle the MUTE buttons)
3. Is the app running? (should say STOP, not PLAY)
4. Try tapping STOP then PLAY again

### Can I use different sounds?

Yes! The Android version supports three sound modes:
- **Tone**: Pure sine wave tones (adjustable frequency)
- **Drum**: Synthesized drum sounds (kick, snare, hihat, crash, tom, ride)
- **MP3 Tick**: Custom MP3 or WAV files from the `ticks/` folder

To use MP3 ticks, place your audio files in the app's `ticks/` directory and select "mp3_tick" mode when adding a layer.

### Why does it sound different from the desktop version?

The Android version uses a simpler audio engine for better mobile performance. The core functionality is the same, but the audio generation is optimized for mobile devices.

### Is there a delay or latency?

Some latency is normal on mobile devices. The amount varies by device:
- Fire HD 10: Minimal latency (~20-40ms)
- Most Android devices: Similar range
- The timing between beats is accurate; only the initial response has slight delay

## Troubleshooting

### The app crashes when I start it

Try these steps:
1. Restart your device
2. Uninstall and reinstall the app
3. Make sure you have Android 5.0 or newer
4. Check if you have sufficient storage space

### The play button doesn't work

- Try tapping STOP first, then PLAY
- Close and reopen the app
- Make sure at least one ear is not MUTED

### I can't save or load files

- Check that you granted storage permissions to the app
- Go to Settings > Apps > PolyRhythm Metronome > Permissions
- Enable Storage permission

### The visual indicators don't flash

This is usually fine - the audio should still work. The flashing is visual feedback only and doesn't affect the metronome function. If concerned:
- Try restarting the app
- Check if your device performance mode is set to power saving (this may slow UI updates)

### Audio sounds choppy or stutters

- Close other apps that might be using audio
- Restart your device
- Check if your device is in a power-saving mode
- Ensure you're not running many background apps

## Advanced Usage

### How do I practice complex polyrhythms?

Start simple and build up:
1. Practice with just left ear (mute right)
2. Practice with just right ear (mute left)
3. Play both together slowly (low BPM)
4. Gradually increase tempo
5. Focus on the "crossover" points where the rhythms align

### Can I change the time signature?

The current version is optimized for 4/4 time. The desktop version has explicit time signature controls. However, you can simulate different time signatures by adjusting BPM and subdivisions.

### What's the highest BPM I can use?

The slider goes up to 240 BPM. This is suitable for:
- Fast practice (120-160 BPM)
- Speed training (160-200 BPM)
- Extreme speed (200-240 BPM)

For most practice, 80-140 BPM is the sweet spot.

### Can I have subdivisions that aren't listed?

The current version only supports the preset subdivisions (1, 2, 4, 8, 16). These cover most musical needs. The desktop version allows custom subdivisions.

## Comparison Questions

### Should I use the Android or Desktop version?

**Use Android if:**
- You want to practice on the go
- You're using a tablet or phone
- You need a simple, focused tool
- Touch interaction is preferred

**Use Desktop if:**
- You need multiple layers per ear
- You want drum sounds or WAV files
- You need to export audio
- You prefer mouse/keyboard
- You're doing composition work

### Can I use both versions?

Absolutely! The Android version is great for portable practice, while the desktop version has more advanced features for detailed work.

### Are the file formats compatible?

Partially. JSON rhythm files from the desktop version can be opened, but:
- Only the first layer per ear will load
- WAV and Drum modes will convert to Tone mode
- Most settings transfer correctly

## Future Features

### Will drum sounds be added?

Drum synthesis is planned for a future version (1.1 or 2.0).

### Will there be multiple layers?

Multi-layer support is planned for version 2.0, based on user feedback.

### Can you add [my feature request]?

Feature requests are welcome! See the main BandTools repository for how to submit ideas.

## Getting Help

### Where can I find more documentation?

- [Quick Start Guide](QUICK_START.md) - Getting started
- [README](../../README.md) - Installation and overview
- [Technical Docs](../technical/) - For developers

### Something's not working!

1. Check this FAQ first
2. Try restarting the app
3. Review the Quick Start Guide
4. Check the GitHub repository for known issues

### How do I report a bug?

Visit the main BandTools GitHub repository to report issues. Include:
- Your device model
- Android/Fire OS version
- Description of the problem
- Steps to reproduce

## Tips & Best Practices

### For Beginners
- Start with subdivision 4 on both ears
- Use BPM 80-100 for learning
- Practice with headphones
- Save patterns you like

### For Polyrhythm Practice
- Master each rhythm separately first
- Start slow (60-80 BPM)
- Gradually increase tempo
- Use mute buttons to isolate parts
- Record yourself to check timing

### For Performance
- Create preset patterns for different songs
- Use save/load for quick switching
- Adjust volumes to balance the mix
- Use visual indicators for visual cues

Happy practicing! 🎵
