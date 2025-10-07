#!/usr/bin/env python3
"""
Practice Goals Backend Module

Manages practice goal creation, tracking, and progress calculation.
Supports time-based goals, session-based goals, and song-specific goals.
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot


# Constants
PRACTICE_GOALS_JSON = ".practice_goals.json"


def save_json(path: Path, data: Any):
    """Save data to JSON file."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except (IOError, OSError) as e:
        print(f"Error saving JSON to {path}: {e}")


def load_json(path: Path, default: Any = None) -> Any:
    """Load JSON file, returning default if file doesn't exist or is invalid."""
    if not path.exists():
        return default
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default


class PracticeGoals(QObject):
    """
    Backend manager for practice goals.
    
    Manages:
    - Goal creation and deletion (weekly, monthly, song-specific)
    - Goal progress tracking
    - Goal deadline monitoring
    - Integration with practice statistics
    """
    
    goalsChanged = pyqtSignal()  # Emitted when goals are modified
    
    def __init__(self):
        super().__init__()
        self._root_path: Optional[Path] = None
        self._practice_statistics = None  # Reference to PracticeStatistics instance
    
    @pyqtSlot(str)
    def setRootPath(self, path: str):
        """Set the root path for storing practice goals."""
        if path:
            self._root_path = Path(path)
        else:
            self._root_path = None
    
    @pyqtSlot(result=str)
    def getRootPath(self) -> str:
        """Get the current root path."""
        return str(self._root_path) if self._root_path else ""
    
    def setPracticeStatistics(self, practice_statistics):
        """Set reference to PracticeStatistics instance for progress calculation."""
        self._practice_statistics = practice_statistics
    
    def _get_goals_path(self) -> Optional[Path]:
        """Get path to practice goals JSON file."""
        if not self._root_path:
            return None
        return self._root_path / PRACTICE_GOALS_JSON
    
    @pyqtSlot(result=str)
    def loadGoals(self) -> str:
        """
        Load practice goals from JSON file.
        
        Returns JSON string with structure:
        {
            "weekly_goals": [...],
            "monthly_goals": [...],
            "song_goals": [...]
        }
        """
        goals_path = self._get_goals_path()
        if not goals_path:
            return json.dumps({
                "weekly_goals": [],
                "monthly_goals": [],
                "song_goals": []
            })
        
        goals_data = load_json(goals_path, {}) or {}
        result = {
            "weekly_goals": goals_data.get("weekly_goals", []),
            "monthly_goals": goals_data.get("monthly_goals", []),
            "song_goals": goals_data.get("song_goals", [])
        }
        return json.dumps(result)
    
    @pyqtSlot(str)
    def saveGoals(self, goals_json: str):
        """Save practice goals to JSON file."""
        goals_path = self._get_goals_path()
        if not goals_path:
            return
        
        try:
            goals_data = json.loads(goals_json)
            save_json(goals_path, goals_data)
            if self.goalsChanged is not None:
                self.goalsChanged.emit()
        except json.JSONDecodeError as e:
            print(f"Error saving goals: {e}")
    
    @pyqtSlot(str, str, int, str, str, result=str)
    def createGoal(self, category: str, goal_type: str, target: int, 
                   start_date: str, end_date: str) -> str:
        """
        Create a new practice goal.
        
        Args:
            category: "weekly", "monthly", or "song"
            goal_type: "time", "session_count", "practice_count", or "best_take"
            target: Target value (minutes for time, count for others)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Goal ID (UUID) as string
        """
        goal_id = str(uuid.uuid4())
        created_time = datetime.now().isoformat()
        
        goal = {
            "id": goal_id,
            "type": goal_type,
            "target": target,
            "start_date": start_date,
            "end_date": end_date,
            "created": created_time
        }
        
        # Load existing goals
        goals_json = self.loadGoals()
        goals_data = json.loads(goals_json)
        
        # Add to appropriate category
        key = f"{category}_goals"
        if key not in goals_data:
            goals_data[key] = []
        goals_data[key].append(goal)
        
        # Save
        self.saveGoals(json.dumps(goals_data))
        
        return goal_id
    
    @pyqtSlot(str, str, str, int, str, str, result=str)
    def createSongGoal(self, song_name: str, goal_type: str, target: int,
                       start_date: str, end_date: str) -> str:
        """
        Create a song-specific practice goal.
        
        Args:
            song_name: Name of the song
            goal_type: "practice_count" or "best_take"
            target: Target value
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Goal ID (UUID) as string
        """
        goal_id = str(uuid.uuid4())
        created_time = datetime.now().isoformat()
        
        goal = {
            "id": goal_id,
            "song_name": song_name,
            "type": goal_type,
            "target": target,
            "start_date": start_date,
            "end_date": end_date,
            "created": created_time
        }
        
        # Load existing goals
        goals_json = self.loadGoals()
        goals_data = json.loads(goals_json)
        
        # Add to song goals
        if "song_goals" not in goals_data:
            goals_data["song_goals"] = []
        goals_data["song_goals"].append(goal)
        
        # Save
        self.saveGoals(json.dumps(goals_data))
        
        return goal_id
    
    @pyqtSlot(str, str)
    def deleteGoal(self, category: str, goal_id: str):
        """
        Delete a practice goal.
        
        Args:
            category: "weekly", "monthly", or "song"
            goal_id: Goal ID to delete
        """
        # Load existing goals
        goals_json = self.loadGoals()
        goals_data = json.loads(goals_json)
        
        # Remove from appropriate category
        key = f"{category}_goals"
        if key in goals_data:
            goals_data[key] = [g for g in goals_data[key] if g.get("id") != goal_id]
        
        # Save
        self.saveGoals(json.dumps(goals_data))
    
    @pyqtSlot(str, str, result=str)
    def calculateGoalProgress(self, goal_json: str, stats_json: str) -> str:
        """
        Calculate progress for a given goal.
        
        Args:
            goal_json: Goal data as JSON string
            stats_json: Practice statistics as JSON string
            
        Returns:
            JSON string with progress info:
            {
                "current": <current value>,
                "target": <target value>,
                "percentage": <0-100>,
                "status": "in_progress"|"complete"|"expired"|"error",
                "days_remaining": <days until end_date>,
                "message": <status message>
            }
        """
        try:
            goal = json.loads(goal_json)
            stats = json.loads(stats_json)
        except json.JSONDecodeError:
            return json.dumps({
                "current": 0,
                "target": 0,
                "percentage": 0,
                "status": "error",
                "days_remaining": 0,
                "message": "Invalid input data"
            })
        
        goal_type = goal.get("type")
        target = goal.get("target", 0)
        start_date_str = goal.get("start_date")
        end_date_str = goal.get("end_date")
        
        # Parse dates
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            return json.dumps({
                "current": 0,
                "target": target,
                "percentage": 0,
                "status": "error",
                "days_remaining": 0,
                "message": "Invalid date format"
            })
        
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        days_remaining = (end_date - today).days
        
        # Initialize progress
        current_value = 0
        status = "in_progress"
        message = ""
        
        # Calculate based on goal type
        if goal_type == "time":
            # Practice time goal (in minutes) - estimate 60 minutes per session
            for session in stats.get("practice_sessions", []):
                session_date_str = session.get("date")
                if session_date_str:
                    try:
                        # Parse various date formats
                        session_date = None
                        for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]:
                            try:
                                session_date = datetime.strptime(session_date_str, fmt)
                                break
                            except ValueError:
                                continue
                        
                        if session_date and start_date <= session_date <= end_date:
                            # Estimate 60 minutes per session (could be improved with actual duration)
                            current_value += 60
                    except (ValueError, TypeError):
                        pass
            
            message = f"{current_value} / {target} minutes"
            
        elif goal_type == "session_count":
            # Session count goal
            for session in stats.get("practice_sessions", []):
                session_date_str = session.get("date")
                if session_date_str:
                    try:
                        session_date = None
                        for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]:
                            try:
                                session_date = datetime.strptime(session_date_str, fmt)
                                break
                            except ValueError:
                                continue
                        
                        if session_date and start_date <= session_date <= end_date:
                            current_value += 1
                    except (ValueError, TypeError):
                        pass
            
            message = f"{current_value} / {target} sessions"
            
        elif goal_type == "practice_count":
            # Song practice count goal
            song_name = goal.get("song_name", "")
            songs = stats.get("songs", {})
            if song_name in songs:
                song_data = songs[song_name]
                # Count practices in date range
                for practice_date_str in song_data.get("practice_dates", []):
                    try:
                        practice_date = datetime.strptime(practice_date_str, "%Y-%m-%d")
                        if start_date <= practice_date <= end_date:
                            current_value += 1
                    except (ValueError, TypeError):
                        pass
            
            message = f"{current_value} / {target} practices"
            
        elif goal_type == "best_take":
            # Song best take goal
            song_name = goal.get("song_name", "")
            songs = stats.get("songs", {})
            if song_name in songs:
                song_data = songs[song_name]
                current_value = song_data.get("best_takes", 0)
            
            message = f"{current_value} / {target} best takes"
        
        # Calculate percentage
        if target > 0:
            percentage = min(100, int((current_value / target) * 100))
        else:
            percentage = 0
        
        # Determine status
        if current_value >= target:
            status = "complete"
        elif days_remaining < 0:
            status = "expired"
        else:
            status = "in_progress"
        
        return json.dumps({
            "current": current_value,
            "target": target,
            "percentage": percentage,
            "status": status,
            "days_remaining": days_remaining,
            "message": message
        })
    
    @pyqtSlot(str, result=str)
    def calculateAllGoalsProgress(self, stats_json: str) -> str:
        """
        Calculate progress for all goals.
        
        Args:
            stats_json: Practice statistics as JSON string
            
        Returns:
            JSON string with all goals and their progress
        """
        goals_json = self.loadGoals()
        goals_data = json.loads(goals_json)
        
        all_goals = []
        
        # Process weekly goals
        for goal in goals_data.get("weekly_goals", []):
            goal["category"] = "weekly"
            progress_json = self.calculateGoalProgress(json.dumps(goal), stats_json)
            progress = json.loads(progress_json)
            goal["progress"] = progress
            all_goals.append(goal)
        
        # Process monthly goals
        for goal in goals_data.get("monthly_goals", []):
            goal["category"] = "monthly"
            progress_json = self.calculateGoalProgress(json.dumps(goal), stats_json)
            progress = json.loads(progress_json)
            goal["progress"] = progress
            all_goals.append(goal)
        
        # Process song goals
        for goal in goals_data.get("song_goals", []):
            goal["category"] = "song"
            progress_json = self.calculateGoalProgress(json.dumps(goal), stats_json)
            progress = json.loads(progress_json)
            goal["progress"] = progress
            all_goals.append(goal)
        
        return json.dumps(all_goals)
