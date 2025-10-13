# Tick Sounds (MP3/WAV)

Place MP3 or WAV files in this folder to use as metronome tick sounds.

## Baseline Ticks Included

The following baseline tick sounds are included with the app:
- **click.wav** - Simple click sound for all beats
- **woodblock** (paired) - Natural woodblock sound with accent/regular distinction
- **cowbell** (paired) - Metallic cowbell sound with accent/regular distinction  
- **hiclick** (paired) - High-pitched clicks with accent/regular distinction

## Single Files
- Place a single audio file (e.g., `click.mp3` or `beep.wav`) to use the same sound for all beats

## Paired Files (Accent vs Regular)
- Place two files with `_1` and `_2` suffixes (e.g., `woodblock_1.wav` and `woodblock_2.wav`)
- The `_1` file will play on accented beats (first beat of measure)
- The `_2` file will play on regular beats

## Examples
- `click.wav` → "click" (single sound for all beats)
- `woodblock_1.wav` + `woodblock_2.wav` → "woodblock" (paired sounds)
- `mybeat.mp3` → "mybeat" (single MP3 for all beats)

The app will scan this folder on startup and make all ticks available in the MP3 mode dropdown.

## Android Implementation

This Android version uses native Android MediaCodec for MP3 decoding, which means:
- **No ffmpeg required** - Uses Android's built-in media APIs
- **Native performance** - Hardware-accelerated decoding where available
- **Small app size** - No external codec libraries needed

The MP3 files are decoded once at startup and cached in memory for instant playback.
