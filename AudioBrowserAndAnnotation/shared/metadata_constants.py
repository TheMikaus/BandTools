"""
Metadata Constants

Common metadata file name constants used across AudioBrowser applications.
These constants define the JSON files used to store various metadata types
in practice folders.
"""

# Metadata file name constants
NAMES_JSON = ".provided_names.json"
NOTES_JSON = ".audio_notes.json"
SESSION_STATE_JSON = ".session_state.json"
WAVEFORM_JSON = ".waveform_cache.json"
DURATIONS_JSON = ".duration_cache.json"
FINGERPRINTS_JSON = ".audio_fingerprints.json"
USER_COLORS_JSON = ".user_colors.json"
SONG_RENAMES_JSON = ".song_renames.json"
PRACTICE_STATS_JSON = ".practice_stats.json"
PRACTICE_GOALS_JSON = ".practice_goals.json"
SETLISTS_JSON = ".setlists.json"
TEMPO_JSON = ".tempo.json"
TAKES_METADATA_JSON = ".takes_metadata.json"
CLIPS_JSON = ".clips.json"

# Set of all reserved JSON files
RESERVED_JSON = {
    NAMES_JSON,
    NOTES_JSON,
    WAVEFORM_JSON,
    DURATIONS_JSON,
    FINGERPRINTS_JSON,
    USER_COLORS_JSON,
    SONG_RENAMES_JSON,
    PRACTICE_STATS_JSON,
    PRACTICE_GOALS_JSON,
    SETLISTS_JSON,
    TEMPO_JSON,
    TAKES_METADATA_JSON,
    CLIPS_JSON,
    SESSION_STATE_JSON,
}

# Audio file extensions
AUDIO_EXTS = {".wav", ".wave", ".mp3"}
