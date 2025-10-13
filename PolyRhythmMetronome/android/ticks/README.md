# MP3 Tick Sounds

Place MP3 files in this folder to use as metronome tick sounds.

## Single Files
- Place a single MP3 file (e.g., `click.mp3`) to use the same sound for all beats

## Paired Files (Accent vs Regular)
- Place two files with `_1` and `_2` suffixes (e.g., `woodblock_1.mp3` and `woodblock_2.mp3`)
- The `_1` file will play on accented beats (first beat of measure)
- The `_2` file will play on regular beats

## Examples
- `click.mp3` → "click" (single sound for all beats)
- `woodblock_1.mp3` + `woodblock_2.mp3` → "woodblock" (paired sounds)

The app will scan this folder on startup and make all ticks available in the MP3 mode dropdown.

## Android Implementation

This Android version uses native Android MediaCodec for MP3 decoding, which means:
- **No ffmpeg required** - Uses Android's built-in media APIs
- **Native performance** - Hardware-accelerated decoding where available
- **Small app size** - No external codec libraries needed

The MP3 files are decoded once at startup and cached in memory for instant playback.
