#!/usr/bin/env python3
"""
Practice Statistics Backend Module

Analyzes practice folders and audio recordings to generate statistics
about practice sessions, song frequency, and practice consistency.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot


# Constants
AUDIO_EXTS = {".wav", ".wave", ".mp3"}
NAMES_JSON = ".provided_names.json"
NOTES_JSON_PATTERN = ".audio_notes*.json"
TAKES_METADATA_JSON = ".takes_metadata.json"


def discover_directories_with_audio_files(root_path: Path) -> List[Path]:
    """
    Recursively discover all directories that contain audio files.
    Returns list of directories that have .wav, .wave, or .mp3 files.
    """
    directories_with_audio = []
    if not root_path.exists() or not root_path.is_dir():
        return directories_with_audio
    
    def scan_directory(directory: Path):
        """Recursively scan directory for audio files."""
        try:
            has_audio_files = False
            subdirectories = []
            
            for item in directory.iterdir():
                if item.is_file() and item.suffix.lower() in AUDIO_EXTS:
                    has_audio_files = True
                elif item.is_dir():
                    # Skip hidden directories and common non-audio directories
                    if not item.name.startswith('.') and item.name.lower() not in {'__pycache__', 'node_modules', '.git'}:
                        subdirectories.append(item)
            
            # Add this directory if it contains audio files
            if has_audio_files:
                directories_with_audio.append(directory)
            
            # Recursively scan subdirectories
            for subdir in subdirectories:
                scan_directory(subdir)
                
        except (OSError, PermissionError):
            pass  # Skip directories we can't access
    
    scan_directory(root_path)
    return directories_with_audio


def load_json(path: Path, default: Any = None) -> Any:
    """Load JSON file, returning default if file doesn't exist or is invalid."""
    if not path.exists():
        return default
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default


class PracticeStatistics(QObject):
    """
    Backend manager for practice statistics.
    
    Analyzes practice folders and generates statistics about:
    - Practice sessions (date, folder, file count, songs)
    - Song frequency (times practiced, total takes)
    - Practice consistency (days between sessions)
    """
    
    statisticsGenerated = pyqtSignal(dict)  # Emitted when statistics are generated
    
    def __init__(self):
        super().__init__()
        self._root_path: Optional[Path] = None
    
    @pyqtSlot(str)
    def setRootPath(self, path: str):
        """Set the root path for discovering practice folders."""
        if path:
            self._root_path = Path(path)
        else:
            self._root_path = None
    
    @pyqtSlot(result=str)
    def getRootPath(self) -> str:
        """Get the current root path."""
        return str(self._root_path) if self._root_path else ""
    
    @pyqtSlot(result=str)
    def generateStatistics(self) -> str:
        """
        Generate practice statistics and return as JSON string.
        
        Returns dictionary with:
            - practice_sessions: list of practice session info
            - songs: dict of song names with practice count and dates
            - summary: overall statistics
        """
        if not self._root_path or not self._root_path.exists():
            return json.dumps({
                "practice_sessions": [],
                "songs": {},
                "summary": {
                    "total_sessions": 0,
                    "total_files": 0,
                    "unique_songs": 0,
                    "date_range": None,
                    "consistency_text": "No root path set"
                }
            })
        
        stats = self._generate_practice_folder_statistics()
        self.statisticsGenerated.emit(stats)
        return json.dumps(stats)
    
    def _generate_practice_folder_statistics(self) -> Dict[str, Any]:
        """Generate statistics by analyzing practice folders and their audio files.
        
        Returns dictionary with:
            - practice_sessions: list of practice session info (date, folder, file count, songs)
            - songs: dict of song names with practice count and dates
            - summary: overall statistics
        """
        stats = {
            "practice_sessions": [],
            "songs": {},
            "summary": {
                "total_sessions": 0,
                "total_files": 0,
                "unique_songs": 0,
                "date_range": None,
                "consistency_text": "Not enough data"
            }
        }
        
        # Discover all directories with audio files
        practice_folders = discover_directories_with_audio_files(self._root_path)
        
        all_session_dates = []
        
        for folder in practice_folders:
            # Get audio files in this folder
            audio_files = []
            for ext in AUDIO_EXTS:
                audio_files.extend(list(folder.glob(f"*{ext}")))
            
            if not audio_files:
                continue
            
            # Get folder date (use folder modification time or name)
            folder_date = self._extract_folder_date(folder)
            
            if folder_date:
                all_session_dates.append(folder_date)
            
            # Load provided names for this folder
            names_json_path = folder / NAMES_JSON
            provided_names = load_json(names_json_path, {}) or {}
            
            # Load notes to check for best takes and partial takes
            notes_data = self._load_takes_metadata(folder)
            
            # Analyze files in this folder
            folder_songs = {}
            best_takes = []
            partial_takes = []
            
            for audio_file in audio_files:
                filename = audio_file.name
                
                # Get song name (provided name or filename)
                song_name = provided_names.get(filename, filename)
                if not song_name or song_name.strip() == "":
                    song_name = filename
                
                # Track song in folder
                if song_name not in folder_songs:
                    folder_songs[song_name] = 0
                folder_songs[song_name] += 1
                
                # Track globally
                if song_name not in stats["songs"]:
                    stats["songs"][song_name] = {
                        "practice_count": 0,
                        "total_takes": 0,
                        "first_practiced": None,
                        "last_practiced": None,
                        "best_takes": 0,
                        "partial_takes": 0
                    }
                
                stats["songs"][song_name]["practice_count"] += 1
                stats["songs"][song_name]["total_takes"] += 1
                
                if folder_date:
                    if stats["songs"][song_name]["first_practiced"] is None:
                        stats["songs"][song_name]["first_practiced"] = folder_date
                    stats["songs"][song_name]["last_practiced"] = folder_date
                    
                    # Update with earlier date if found
                    if stats["songs"][song_name]["first_practiced"] > folder_date:
                        stats["songs"][song_name]["first_practiced"] = folder_date
                    # Update with later date if found
                    if stats["songs"][song_name]["last_practiced"] < folder_date:
                        stats["songs"][song_name]["last_practiced"] = folder_date
                
                # Check if this file is marked as best take or partial take
                file_metadata = notes_data.get(filename, {})
                if isinstance(file_metadata, dict):
                    if file_metadata.get("best_take", False):
                        best_takes.append(song_name)
                        stats["songs"][song_name]["best_takes"] += 1
                    if file_metadata.get("partial_take", False):
                        partial_takes.append(song_name)
                        stats["songs"][song_name]["partial_takes"] += 1
            
            # Add session info
            session_info = {
                "date": folder_date.isoformat() if folder_date else None,
                "folder": folder.name,
                "file_count": len(audio_files),
                "unique_songs": len(folder_songs),
                "songs": list(folder_songs.keys()),
                "best_takes": best_takes,
                "partial_takes": partial_takes
            }
            stats["practice_sessions"].append(session_info)
        
        # Sort sessions by date (most recent first)
        stats["practice_sessions"].sort(
            key=lambda x: datetime.fromisoformat(x["date"]) if x["date"] else datetime.min,
            reverse=True
        )
        
        # Calculate summary statistics
        stats["summary"]["total_sessions"] = len(stats["practice_sessions"])
        stats["summary"]["total_files"] = sum(s["file_count"] for s in stats["practice_sessions"])
        stats["summary"]["unique_songs"] = len(stats["songs"])
        
        if all_session_dates:
            all_session_dates.sort()
            stats["summary"]["date_range"] = {
                "first": all_session_dates[0].isoformat(),
                "last": all_session_dates[-1].isoformat()
            }
        
        # Calculate practice consistency (days between sessions)
        if len(all_session_dates) >= 2:
            days_between = []
            for i in range(1, len(all_session_dates)):
                days_diff = (all_session_dates[i] - all_session_dates[i-1]).days
                if days_diff > 0:  # Only count if there's a gap
                    days_between.append(days_diff)
            
            if days_between:
                avg_days = sum(days_between) / len(days_between)
                stats["summary"]["consistency_text"] = f"{avg_days:.1f} days average between practices"
        
        # Convert datetime objects to ISO strings for JSON serialization
        for song_name, song_data in stats["songs"].items():
            if song_data.get("first_practiced"):
                song_data["first_practiced"] = song_data["first_practiced"].isoformat()
            if song_data.get("last_practiced"):
                song_data["last_practiced"] = song_data["last_practiced"].isoformat()
        
        return stats
    
    def _extract_folder_date(self, folder: Path) -> Optional[datetime]:
        """Extract date from folder name or modification time."""
        try:
            # Try to parse date from folder name (common format: YYYY-MM-DD-...)
            folder_name = folder.name
            # Look for YYYY-MM-DD pattern
            date_match = re.match(r'(\d{4})-(\d{2})-(\d{2})', folder_name)
            if date_match:
                year, month, day = date_match.groups()
                return datetime(int(year), int(month), int(day))
            else:
                # Fall back to folder modification time
                return datetime.fromtimestamp(folder.stat().st_mtime)
        except:
            # Fall back to folder modification time
            try:
                return datetime.fromtimestamp(folder.stat().st_mtime)
            except:
                return datetime.now()
    
    def _load_takes_metadata(self, folder: Path) -> Dict[str, Any]:
        """Load takes metadata (best take, partial take markers) from folder."""
        notes_data = {}
        
        # Try new format first (.takes_metadata.json)
        takes_metadata_path = folder / TAKES_METADATA_JSON
        if takes_metadata_path.exists():
            metadata = load_json(takes_metadata_path, {})
            if metadata:
                notes_data.update(metadata)
        
        # Also check old format (.audio_notes_*.json) for backward compatibility
        for notes_file in folder.glob(NOTES_JSON_PATTERN):
            user_notes = load_json(notes_file, {}) or {}
            if user_notes:
                notes_data.update(user_notes)
        
        return notes_data
    
    @pyqtSlot(str, result=str)
    def formatStatisticsAsHtml(self, stats_json: str) -> str:
        """
        Format statistics as HTML for display in QML TextEdit.
        
        Args:
            stats_json: JSON string containing statistics data
            
        Returns:
            HTML formatted string
        """
        try:
            stats = json.loads(stats_json)
        except json.JSONDecodeError:
            return "<h2>Error</h2><p>Failed to parse statistics data</p>"
        
        sessions = stats.get("practice_sessions", [])
        songs = stats.get("songs", {})
        summary = stats.get("summary", {})
        
        # Recent sessions (last 10)
        recent_sessions = sessions[:10] if len(sessions) > 10 else sessions
        
        # Session statistics
        session_count = summary.get("total_sessions", 0)
        total_files = summary.get("total_files", 0)
        unique_songs = summary.get("unique_songs", 0)
        
        # Date range
        date_range_text = "No practices recorded"
        if summary.get("date_range"):
            try:
                first_date = datetime.fromisoformat(summary["date_range"]["first"]).strftime("%Y-%m-%d")
                last_date = datetime.fromisoformat(summary["date_range"]["last"]).strftime("%Y-%m-%d")
                if first_date == last_date:
                    date_range_text = first_date
                else:
                    date_range_text = f"{first_date} to {last_date}"
            except:
                date_range_text = "Invalid date range"
        
        consistency_text = summary.get("consistency_text", "Not enough data")
        
        # Song statistics - sort by practice count
        song_stats_list = []
        for song_name, song_data in songs.items():
            practice_count = song_data.get("practice_count", 0)
            total_takes = song_data.get("total_takes", 0)
            last_practiced = song_data.get("last_practiced")
            best_takes = song_data.get("best_takes", 0)
            
            # Format last practiced time
            if last_practiced:
                try:
                    last_date = datetime.fromisoformat(last_practiced)
                    days_ago = (datetime.now() - last_date).days
                    if days_ago == 0:
                        last_practiced_str = "Today"
                    elif days_ago == 1:
                        last_practiced_str = "Yesterday"
                    else:
                        last_practiced_str = f"{days_ago} days ago"
                except:
                    last_practiced_str = "Unknown"
            else:
                last_practiced_str = "Never"
            
            song_stats_list.append({
                "name": song_name,
                "practice_count": practice_count,
                "total_takes": total_takes,
                "last_practiced": last_practiced_str,
                "best_takes": best_takes
            })
        
        # Sort songs by practice count (most practiced first)
        song_stats_list.sort(key=lambda x: x["practice_count"], reverse=True)
        most_practiced = song_stats_list[:5]  # Top 5
        least_practiced = song_stats_list[-5:] if len(song_stats_list) > 5 else []
        least_practiced.reverse()  # Least practiced first
        
        # Get current timestamp for last updated note
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Build HTML content
        html_content = f"""
        <h2>Practice Statistics</h2>
        <p><em>Statistics generated by analyzing practice folders and audio files</em></p>
        <p><em>Last updated: {current_time}</em></p>
        
        <h3>Overall Summary</h3>
        <table cellpadding="5" border="0">
        <tr><td><b>Total Practice Sessions:</b></td><td>{session_count}</td></tr>
        <tr><td><b>Total Recordings:</b></td><td>{total_files}</td></tr>
        <tr><td><b>Unique Songs:</b></td><td>{unique_songs}</td></tr>
        <tr><td><b>Date Range:</b></td><td>{date_range_text}</td></tr>
        <tr><td><b>Practice Consistency:</b></td><td>{consistency_text}</td></tr>
        </table>
        
        <h3>Recent Practice Sessions</h3>
        <table cellpadding="5" border="1" cellspacing="0" style="border-collapse: collapse;">
        <tr style="background-color: #e0e0e0;">
            <th>Date</th>
            <th>Folder</th>
            <th>Files</th>
            <th>Songs</th>
            <th>Best Takes</th>
        </tr>
        """
        
        for session in recent_sessions:
            date_str = "Unknown"
            if session.get("date"):
                try:
                    date_str = datetime.fromisoformat(session["date"]).strftime("%Y-%m-%d")
                except:
                    date_str = "Invalid"
            
            folder = session.get("folder", "Unknown")
            file_count = session.get("file_count", 0)
            unique_song_count = session.get("unique_songs", 0)
            best_take_count = len(session.get("best_takes", []))
            
            html_content += f"""
        <tr>
            <td>{date_str}</td>
            <td>{folder}</td>
            <td>{file_count}</td>
            <td>{unique_song_count}</td>
            <td>{best_take_count}</td>
        </tr>
            """
        
        html_content += """
        </table>
        """
        
        # Most practiced songs
        if most_practiced:
            html_content += """
        <h3>Most Practiced Songs</h3>
        <table cellpadding="5" border="1" cellspacing="0" style="border-collapse: collapse;">
        <tr style="background-color: #e0e0e0;">
            <th>Song</th>
            <th>Times Practiced</th>
            <th>Total Takes</th>
            <th>Best Takes</th>
            <th>Last Practiced</th>
        </tr>
            """
            
            for song in most_practiced:
                html_content += f"""
        <tr>
            <td>{song["name"]}</td>
            <td>{song["practice_count"]}</td>
            <td>{song["total_takes"]}</td>
            <td>{song["best_takes"]}</td>
            <td>{song["last_practiced"]}</td>
        </tr>
                """
            
            html_content += """
        </table>
            """
        
        # Least practiced songs
        if least_practiced and len(song_stats_list) > 5:
            html_content += """
        <h3>Least Practiced Songs</h3>
        <table cellpadding="5" border="1" cellspacing="0" style="border-collapse: collapse;">
        <tr style="background-color: #e0e0e0;">
            <th>Song</th>
            <th>Times Practiced</th>
            <th>Total Takes</th>
            <th>Best Takes</th>
            <th>Last Practiced</th>
        </tr>
            """
            
            for song in least_practiced:
                html_content += f"""
        <tr>
            <td>{song["name"]}</td>
            <td>{song["practice_count"]}</td>
            <td>{song["total_takes"]}</td>
            <td>{song["best_takes"]}</td>
            <td>{song["last_practiced"]}</td>
        </tr>
                """
            
            html_content += """
        </table>
            """
        
        if not most_practiced:
            html_content += """
        <p><em>No songs found in practice folders</em></p>
            """
        
        return html_content
