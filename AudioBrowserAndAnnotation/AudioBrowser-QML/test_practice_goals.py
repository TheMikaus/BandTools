#!/usr/bin/env python3
"""
Unit tests for Practice Goals backend functionality.

Tests goal creation, progress calculation, and data persistence.
"""

import sys
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

# Mock PyQt6 for testing without Qt installed
try:
    from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
except ImportError:
    print("PyQt6 not available, using mock...")
    class QObject:
        def __init__(self, *args, **kwargs):
            pass
    
    def pyqtSignal(*args, **kwargs):
        return None
    
    def pyqtSlot(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    # Create mock module
    class MockQtCore:
        QObject = QObject
        pyqtSignal = pyqtSignal
        pyqtSlot = pyqtSlot
    
    sys.modules['PyQt6'] = type(sys)('PyQt6')
    sys.modules['PyQt6.QtCore'] = MockQtCore()

# Import backend module
from backend.practice_goals import PracticeGoals, save_json, load_json


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def test_goals_module_structure():
    """Test that the PracticeGoals module has the expected structure."""
    print("\nTesting goals module structure...")
    
    # Test that PracticeGoals class can be imported
    assert PracticeGoals is not None, "PracticeGoals class should be importable"
    print("  ✓ PracticeGoals class can be imported")
    
    # Test that module has expected functions
    assert save_json is not None, "save_json should exist"
    assert load_json is not None, "load_json should exist"
    print("  ✓ Module has expected helper functions")
    
    # Create instance
    goals = PracticeGoals()
    assert goals is not None, "Should be able to create PracticeGoals instance"
    print("  ✓ PracticeGoals instance can be created")
    
    # Test that it has expected methods
    assert hasattr(goals, 'setRootPath'), "Should have setRootPath method"
    assert hasattr(goals, 'getRootPath'), "Should have getRootPath method"
    assert hasattr(goals, 'loadGoals'), "Should have loadGoals method"
    assert hasattr(goals, 'saveGoals'), "Should have saveGoals method"
    assert hasattr(goals, 'createGoal'), "Should have createGoal method"
    assert hasattr(goals, 'createSongGoal'), "Should have createSongGoal method"
    assert hasattr(goals, 'deleteGoal'), "Should have deleteGoal method"
    assert hasattr(goals, 'calculateGoalProgress'), "Should have calculateGoalProgress method"
    assert hasattr(goals, 'calculateAllGoalsProgress'), "Should have calculateAllGoalsProgress method"
    print("  ✓ PracticeGoals has all expected methods")
    
    return True


def test_json_operations():
    """Test JSON save and load operations."""
    print("\nTesting JSON operations...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_path = Path(tmpdir) / "test.json"
        
        # Test save
        test_data = {"weekly_goals": [], "monthly_goals": [], "song_goals": []}
        save_json(test_path, test_data)
        assert test_path.exists(), "JSON file should be created"
        print("  ✓ JSON save works")
        
        # Test load
        loaded_data = load_json(test_path, {})
        assert loaded_data == test_data, "Loaded data should match saved data"
        print("  ✓ JSON load works")
        
        # Test load with default for non-existent file
        non_existent = Path(tmpdir) / "nonexistent.json"
        loaded_default = load_json(non_existent, {"default": True})
        assert loaded_default == {"default": True}, "Should return default for non-existent file"
        print("  ✓ JSON load with default works")
    
    return True


def test_goal_creation_and_loading():
    """Test goal creation and loading."""
    print("\nTesting goal creation and loading...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        goals = PracticeGoals()
        goals.setRootPath(tmpdir)
        
        # Test that root path is set correctly
        assert goals.getRootPath() == tmpdir, "Root path should be set"
        print("  ✓ Root path setting works")
        
        # Load empty goals
        goals_json = goals.loadGoals()
        goals_data = json.loads(goals_json)
        assert "weekly_goals" in goals_data, "Should have weekly_goals key"
        assert "monthly_goals" in goals_data, "Should have monthly_goals key"
        assert "song_goals" in goals_data, "Should have song_goals key"
        assert len(goals_data["weekly_goals"]) == 0, "Weekly goals should be empty"
        print("  ✓ Empty goals loading works")
        
        # Create a weekly goal
        today = datetime.now()
        end_date = today + timedelta(days=7)
        start_str = today.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        goal_id = goals.createGoal("weekly", "time", 300, start_str, end_str)
        assert goal_id is not None, "Should return goal ID"
        assert len(goal_id) > 0, "Goal ID should not be empty"
        print(f"  ✓ Weekly goal created with ID: {goal_id[:8]}...")
        
        # Load goals and verify
        goals_json = goals.loadGoals()
        goals_data = json.loads(goals_json)
        assert len(goals_data["weekly_goals"]) == 1, "Should have one weekly goal"
        
        goal = goals_data["weekly_goals"][0]
        assert goal["id"] == goal_id, "Goal ID should match"
        assert goal["type"] == "time", "Goal type should be 'time'"
        assert goal["target"] == 300, "Target should be 300"
        assert goal["start_date"] == start_str, "Start date should match"
        assert goal["end_date"] == end_str, "End date should match"
        print("  ✓ Goal data persisted correctly")
        
        # Create a song goal
        song_goal_id = goals.createSongGoal("Test Song", "practice_count", 5, start_str, end_str)
        assert song_goal_id is not None, "Should return song goal ID"
        print(f"  ✓ Song goal created with ID: {song_goal_id[:8]}...")
        
        # Load and verify song goal
        goals_json = goals.loadGoals()
        goals_data = json.loads(goals_json)
        assert len(goals_data["song_goals"]) == 1, "Should have one song goal"
        
        song_goal = goals_data["song_goals"][0]
        assert song_goal["song_name"] == "Test Song", "Song name should match"
        assert song_goal["type"] == "practice_count", "Goal type should be 'practice_count'"
        print("  ✓ Song goal data persisted correctly")
        
        # Test goal deletion
        goals.deleteGoal("weekly", goal_id)
        goals_json = goals.loadGoals()
        goals_data = json.loads(goals_json)
        assert len(goals_data["weekly_goals"]) == 0, "Weekly goal should be deleted"
        print("  ✓ Goal deletion works")
    
    return True


def test_progress_calculation():
    """Test goal progress calculation."""
    print("\nTesting progress calculation...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        goals = PracticeGoals()
        goals.setRootPath(tmpdir)
        
        # Create a test goal
        today = datetime.now()
        start_date = today - timedelta(days=3)
        end_date = today + timedelta(days=4)
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        goal_id = goals.createGoal("weekly", "session_count", 5, start_str, end_str)
        
        # Load the goal
        goals_json = goals.loadGoals()
        goals_data = json.loads(goals_json)
        goal = goals_data["weekly_goals"][0]
        
        # Create mock stats with practice sessions
        mock_stats = {
            "practice_sessions": [
                {"date": (today - timedelta(days=2)).strftime("%Y-%m-%d"), "files": 10},
                {"date": (today - timedelta(days=1)).strftime("%Y-%m-%d"), "files": 8},
                {"date": today.strftime("%Y-%m-%d"), "files": 12}
            ],
            "songs": {}
        }
        
        # Calculate progress
        progress_json = goals.calculateGoalProgress(
            json.dumps(goal),
            json.dumps(mock_stats)
        )
        progress = json.loads(progress_json)
        
        # Verify progress structure
        assert "current" in progress, "Progress should have 'current' field"
        assert "target" in progress, "Progress should have 'target' field"
        assert "percentage" in progress, "Progress should have 'percentage' field"
        assert "status" in progress, "Progress should have 'status' field"
        assert "days_remaining" in progress, "Progress should have 'days_remaining' field"
        assert "message" in progress, "Progress should have 'message' field"
        print("  ✓ Progress has all required fields")
        
        # Verify calculated values
        assert progress["current"] == 3, f"Should have 3 sessions, got {progress['current']}"
        assert progress["target"] == 5, "Target should be 5"
        assert progress["percentage"] == 60, f"Percentage should be 60%, got {progress['percentage']}%"
        assert progress["status"] == "in_progress", f"Status should be 'in_progress', got {progress['status']}"
        assert progress["days_remaining"] == 4, f"Days remaining should be 4, got {progress['days_remaining']}"
        print("  ✓ Progress values calculated correctly")
        
        # Test completed goal
        completed_goal = {
            "type": "session_count",
            "target": 2,  # Lower target
            "start_date": start_str,
            "end_date": end_str
        }
        
        progress_json = goals.calculateGoalProgress(
            json.dumps(completed_goal),
            json.dumps(mock_stats)
        )
        progress = json.loads(progress_json)
        
        assert progress["status"] == "complete", "Status should be 'complete'"
        assert progress["percentage"] == 100, "Percentage should be 100%"
        print("  ✓ Completed goal detected correctly")
        
        # Test expired goal
        expired_goal = {
            "type": "session_count",
            "target": 10,
            "start_date": (today - timedelta(days=10)).strftime("%Y-%m-%d"),
            "end_date": (today - timedelta(days=3)).strftime("%Y-%m-%d")
        }
        
        progress_json = goals.calculateGoalProgress(
            json.dumps(expired_goal),
            json.dumps(mock_stats)
        )
        progress = json.loads(progress_json)
        
        assert progress["status"] == "expired", "Status should be 'expired'"
        assert progress["days_remaining"] < 0, "Days remaining should be negative"
        print("  ✓ Expired goal detected correctly")
    
    return True


def run_tests():
    """Run all tests."""
    print_section("Practice Goals Backend Test Suite")
    
    passed = 0
    total = 0
    
    tests = [
        ("Module Structure", test_goals_module_structure),
        ("JSON Operations", test_json_operations),
        ("Goal Creation and Loading", test_goal_creation_and_loading),
        ("Progress Calculation", test_progress_calculation)
    ]
    
    for test_name, test_func in tests:
        total += 1
        try:
            if test_func():
                passed += 1
                print(f"  ✓ {test_name} test passed")
        except AssertionError as e:
            print(f"  ✗ {test_name} test failed: {e}")
        except Exception as e:
            print(f"  ✗ {test_name} test error: {e}")
    
    print_section("Test Summary")
    print(f"Passed: {passed}/{total}\n")
    
    if passed == total:
        print("✓ All tests passed!\n")
        return 0
    else:
        print(f"✗ {total - passed} test(s) failed\n")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
