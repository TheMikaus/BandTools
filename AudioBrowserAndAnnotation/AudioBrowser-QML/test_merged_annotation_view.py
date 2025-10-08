#!/usr/bin/env python3
"""
Test script for merged annotation view (multi-user support)

Tests:
1. getAllUsers() returns list of unique users
2. getAnnotationsForUser() filters by user correctly
3. User column appears in AnnotationsModel
4. User filter works in annotations display
"""

import sys
import tempfile
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def test_annotation_manager_multi_user():
    """Test annotation manager's multi-user methods"""
    print("Testing AnnotationManager multi-user support...")
    
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    from backend.annotation_manager import AnnotationManager
    
    manager = AnnotationManager()
    
    # Create a temp file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        test_file = f.name
    
    try:
        manager.setCurrentFile(test_file)
        
        # Add annotations from different users
        manager.setCurrentUser("user1")
        manager.addAnnotation(1000, "User 1 annotation 1", "timing", False, "#ff0000")
        manager.addAnnotation(2000, "User 1 annotation 2", "energy", True, "#ff0000")
        
        manager.setCurrentUser("user2")
        manager.addAnnotation(1500, "User 2 annotation 1", "harmony", False, "#00ff00")
        manager.addAnnotation(2500, "User 2 annotation 2", "notes", False, "#00ff00")
        
        manager.setCurrentUser("user3")
        manager.addAnnotation(3000, "User 3 annotation 1", "dynamics", True, "#0000ff")
        
        # Test getAllUsers()
        users = manager.getAllUsers()
        print(f"  ✓ getAllUsers() returned: {users}")
        assert len(users) == 3, f"Expected 3 users, got {len(users)}"
        assert "user1" in users and "user2" in users and "user3" in users
        
        # Test getAnnotationsForUser() - all users (empty string)
        all_annotations = manager.getAnnotationsForUser("")
        print(f"  ✓ All annotations count: {len(all_annotations)}")
        assert len(all_annotations) == 5, f"Expected 5 annotations, got {len(all_annotations)}"
        
        # Test getAnnotationsForUser() - specific user
        user1_annotations = manager.getAnnotationsForUser("user1")
        print(f"  ✓ user1 annotations count: {len(user1_annotations)}")
        assert len(user1_annotations) == 2, f"Expected 2 annotations for user1, got {len(user1_annotations)}"
        
        user2_annotations = manager.getAnnotationsForUser("user2")
        print(f"  ✓ user2 annotations count: {len(user2_annotations)}")
        assert len(user2_annotations) == 2, f"Expected 2 annotations for user2, got {len(user2_annotations)}"
        
        user3_annotations = manager.getAnnotationsForUser("user3")
        print(f"  ✓ user3 annotations count: {len(user3_annotations)}")
        assert len(user3_annotations) == 1, f"Expected 1 annotation for user3, got {len(user3_annotations)}"
        
        # Verify that filtered annotations belong to the correct user
        for annotation in user1_annotations:
            assert annotation["user"] == "user1", "Annotation doesn't belong to user1"
        
        print("  ✓ All AnnotationManager multi-user tests passed!")
        
    finally:
        # Cleanup
        Path(test_file).unlink(missing_ok=True)
        json_file = Path(test_file).with_suffix(".annotations.json")
        json_file.unlink(missing_ok=True)

def test_annotations_model_user_column():
    """Test that AnnotationsModel includes user column"""
    print("\nTesting AnnotationsModel user column...")
    
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    from backend.models import AnnotationsModel
    
    model = AnnotationsModel()
    
    # Check column count (should be 5: Time, Category, Text, User, Important)
    col_count = model.columnCount()
    print(f"  ✓ Column count: {col_count}")
    assert col_count == 5, f"Expected 5 columns, got {col_count}"
    
    # Check that COL_USER exists and is correct
    assert hasattr(model, 'COL_USER'), "COL_USER not defined"
    assert model.COL_USER == 3, f"COL_USER should be 3, got {model.COL_USER}"
    print(f"  ✓ COL_USER index: {model.COL_USER}")
    
    # Check that UserRole exists
    assert hasattr(model, 'UserRole'), "UserRole not defined"
    print(f"  ✓ UserRole defined")
    
    # Check role names includes 'user'
    role_names = model.roleNames()
    user_role_bytes = None
    for role_id, role_name in role_names.items():
        if role_name == b'user':
            user_role_bytes = role_name
            break
    
    assert user_role_bytes is not None, "'user' role not in roleNames()"
    print(f"  ✓ 'user' role found in roleNames")
    
    # Test with actual data
    test_annotations = [
        {"timestamp_ms": 1000, "text": "Test 1", "category": "timing", "user": "alice", "important": False, "color": "#ff0000"},
        {"timestamp_ms": 2000, "text": "Test 2", "category": "energy", "user": "bob", "important": True, "color": "#00ff00"},
    ]
    
    model.setAnnotations(test_annotations)
    
    # Check data retrieval for user column
    from PyQt6.QtCore import QModelIndex
    index_row0 = model.index(0, model.COL_USER)
    user_data = model.data(index_row0)
    print(f"  ✓ User data for row 0: {user_data}")
    assert user_data == "alice", f"Expected 'alice', got {user_data}"
    
    index_row1 = model.index(1, model.COL_USER)
    user_data = model.data(index_row1)
    print(f"  ✓ User data for row 1: {user_data}")
    assert user_data == "bob", f"Expected 'bob', got {user_data}"
    
    print("  ✓ All AnnotationsModel user column tests passed!")

def test_integration():
    """Integration test of multi-user annotation features"""
    print("\nRunning integration test...")
    
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    from backend.annotation_manager import AnnotationManager
    from backend.models import AnnotationsModel
    
    manager = AnnotationManager()
    model = AnnotationsModel()
    
    # Create a temp file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        test_file = f.name
    
    try:
        manager.setCurrentFile(test_file)
        
        # Add annotations from multiple users
        manager.setCurrentUser("alice")
        manager.addAnnotation(1000, "Alice's first note", "timing", False, "#ff0000")
        manager.addAnnotation(3000, "Alice's second note", "energy", True, "#ff0000")
        
        manager.setCurrentUser("bob")
        manager.addAnnotation(2000, "Bob's note", "harmony", False, "#00ff00")
        
        # Get all annotations and load into model
        all_annotations = manager.getAnnotations()
        model.setAnnotations(all_annotations)
        
        print(f"  ✓ Total annotations in model: {model.rowCount()}")
        assert model.rowCount() == 3, f"Expected 3 rows, got {model.rowCount()}"
        
        # Test filtering by user through manager
        alice_annotations = manager.getAnnotationsForUser("alice")
        model.setAnnotations(alice_annotations)
        
        print(f"  ✓ Alice's annotations in model: {model.rowCount()}")
        assert model.rowCount() == 2, f"Expected 2 rows for Alice, got {model.rowCount()}"
        
        # Verify all rows show Alice as user
        for row in range(model.rowCount()):
            index = model.index(row, model.COL_USER)
            user = model.data(index)
            assert user == "alice", f"Expected 'alice', got '{user}' at row {row}"
        
        print("  ✓ Integration test passed!")
        
    finally:
        # Cleanup
        Path(test_file).unlink(missing_ok=True)
        json_file = Path(test_file).with_suffix(".annotations.json")
        json_file.unlink(missing_ok=True)

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Merged Annotation View (Multi-User Support)")
    print("=" * 60)
    
    try:
        test_annotation_manager_multi_user()
        test_annotations_model_user_column()
        test_integration()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nMerged annotation view features:")
        print("  • getAllUsers() - Get list of all users with annotations")
        print("  • getAnnotationsForUser(user) - Filter annotations by user")
        print("  • User column added to AnnotationsModel")
        print("  • UI filter for selecting user (in AnnotationsTab.qml)")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
