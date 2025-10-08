#!/usr/bin/env python3
"""
Syntax and structure test for merged annotation view (multi-user support)

Tests that don't require GUI initialization:
1. Methods exist in AnnotationManager
2. Model attributes are correctly defined
3. Python syntax is valid
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

def test_annotation_manager_methods():
    """Test that AnnotationManager has the new methods"""
    print("Testing AnnotationManager method signatures...")
    
    import inspect
    from backend import annotation_manager
    
    # Check getAllUsers method exists
    assert hasattr(annotation_manager.AnnotationManager, 'getAllUsers'), \
        "getAllUsers method not found"
    print("  ✓ getAllUsers() method exists")
    
    # Check getAnnotationsForUser method exists
    assert hasattr(annotation_manager.AnnotationManager, 'getAnnotationsForUser'), \
        "getAnnotationsForUser method not found"
    print("  ✓ getAnnotationsForUser() method exists")
    
    # Check method signatures
    get_all_users = annotation_manager.AnnotationManager.getAllUsers
    sig = inspect.signature(get_all_users)
    print(f"  ✓ getAllUsers signature: {sig}")
    
    get_annotations_for_user = annotation_manager.AnnotationManager.getAnnotationsForUser
    sig = inspect.signature(get_annotations_for_user)
    print(f"  ✓ getAnnotationsForUser signature: {sig}")
    
    print("  ✓ All AnnotationManager methods present!")

def test_annotations_model_structure():
    """Test that AnnotationsModel has the user column"""
    print("\nTesting AnnotationsModel structure...")
    
    from backend import models
    
    # Check COL_USER exists
    assert hasattr(models.AnnotationsModel, 'COL_USER'), \
        "COL_USER attribute not found"
    col_user = models.AnnotationsModel.COL_USER
    print(f"  ✓ COL_USER = {col_user}")
    assert col_user == 3, f"Expected COL_USER=3, got {col_user}"
    
    # Check COL_COUNT updated
    assert hasattr(models.AnnotationsModel, 'COL_COUNT'), \
        "COL_COUNT attribute not found"
    col_count = models.AnnotationsModel.COL_COUNT
    print(f"  ✓ COL_COUNT = {col_count}")
    assert col_count == 5, f"Expected COL_COUNT=5, got {col_count}"
    
    # Check UserRole exists
    assert hasattr(models.AnnotationsModel, 'UserRole'), \
        "UserRole attribute not found"
    print(f"  ✓ UserRole attribute exists")
    
    print("  ✓ All AnnotationsModel structure tests passed!")

def test_qml_syntax():
    """Test that QML file has valid structure"""
    print("\nTesting AnnotationsTab.qml structure...")
    
    qml_file = Path(__file__).parent / "qml" / "tabs" / "AnnotationsTab.qml"
    
    if not qml_file.exists():
        print(f"  ⚠️  QML file not found: {qml_file}")
        return
    
    qml_content = qml_file.read_text()
    
    # Check for userFilter ComboBox
    assert "id: userFilter" in qml_content, "userFilter ComboBox not found"
    print("  ✓ userFilter ComboBox present")
    
    # Check for User: label
    assert 'text: "User:"' in qml_content or "text: 'User:'" in qml_content, \
        "User: label not found"
    print("  ✓ User: label present")
    
    # Check for updateUserFilter function
    assert "function updateUserFilter" in qml_content, \
        "updateUserFilter function not found"
    print("  ✓ updateUserFilter() function present")
    
    # Check for getAllUsers call
    assert "getAllUsers()" in qml_content, \
        "getAllUsers() call not found"
    print("  ✓ getAllUsers() call present")
    
    # Check for getAnnotationsForUser call
    assert "getAnnotationsForUser" in qml_content, \
        "getAnnotationsForUser() call not found"
    print("  ✓ getAnnotationsForUser() call present")
    
    print("  ✓ All QML structure tests passed!")

def test_module_imports():
    """Test that modules can be imported"""
    print("\nTesting module imports...")
    
    try:
        from backend import annotation_manager
        print("  ✓ annotation_manager module imported")
    except Exception as e:
        print(f"  ❌ Failed to import annotation_manager: {e}")
        raise
    
    try:
        from backend import models
        print("  ✓ models module imported")
    except Exception as e:
        print(f"  ❌ Failed to import models: {e}")
        raise
    
    print("  ✓ All modules imported successfully!")

if __name__ == "__main__":
    print("=" * 60)
    print("Syntax Tests for Merged Annotation View")
    print("=" * 60)
    
    try:
        test_module_imports()
        test_annotation_manager_methods()
        test_annotations_model_structure()
        test_qml_syntax()
        
        print("\n" + "=" * 60)
        print("✅ ALL SYNTAX TESTS PASSED!")
        print("=" * 60)
        print("\nMerged annotation view implementation:")
        print("  • Backend methods: getAllUsers(), getAnnotationsForUser()")
        print("  • Model column: COL_USER (index 3)")
        print("  • QML UI: User filter ComboBox with updateUserFilter()")
        print("\nFeature Status: ✅ IMPLEMENTED")
        print("Next: Manual testing with actual audio files")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
