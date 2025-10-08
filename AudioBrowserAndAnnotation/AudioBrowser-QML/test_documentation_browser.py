#!/usr/bin/env python3
"""
Test Documentation Browser Implementation

Tests for Issue #15: Documentation Browser feature
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_backend_import():
    """Test that backend module imports correctly."""
    print("Testing documentation_manager import...")
    try:
        from backend.documentation_manager import DocumentationManager
        print("✓ DocumentationManager imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import DocumentationManager: {e}")
        return False

def test_documentation_manager_creation():
    """Test creating DocumentationManager instance."""
    print("\nTesting DocumentationManager instantiation...")
    try:
        from backend.documentation_manager import DocumentationManager
        from PyQt6.QtCore import QCoreApplication
        
        app = QCoreApplication(sys.argv)
        manager = DocumentationManager()
        print("✓ DocumentationManager instance created")
        
        # Test document discovery
        docs = manager.getDocuments()
        print(f"✓ Discovered {len(docs)} documents")
        
        if len(docs) > 0:
            print(f"  First document: {docs[0]['category']} - {docs[0]['title']}")
        
        return True
    except Exception as e:
        print(f"✗ Failed to create DocumentationManager: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_documentation_methods():
    """Test DocumentationManager methods."""
    print("\nTesting DocumentationManager methods...")
    try:
        from backend.documentation_manager import DocumentationManager
        from PyQt6.QtCore import QCoreApplication
        
        app = QCoreApplication(sys.argv)
        manager = DocumentationManager()
        
        # Test getDocuments
        docs = manager.getDocuments()
        assert isinstance(docs, list), "getDocuments should return a list"
        print(f"✓ getDocuments() returned {len(docs)} documents")
        
        # Test searchDocuments
        if docs:
            search_results = manager.searchDocuments("guide")
            print(f"✓ searchDocuments('guide') returned {len(search_results)} results")
        
        # Test loadDocument
        if docs:
            content = manager.loadDocument(docs[0]['filepath'])
            assert isinstance(content, str), "loadDocument should return string"
            print(f"✓ loadDocument() returned {len(content)} characters")
        
        # Test getDocumentCount
        count = manager.getDocumentCount()
        assert count == len(docs), "Document count should match docs list length"
        print(f"✓ getDocumentCount() returned {count}")
        
        return True
    except Exception as e:
        print(f"✗ Method test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_qml_dialog_syntax():
    """Test QML dialog syntax."""
    print("\nTesting DocumentationBrowserDialog.qml syntax...")
    try:
        qml_file = Path(__file__).parent / "qml" / "dialogs" / "DocumentationBrowserDialog.qml"
        if not qml_file.exists():
            print(f"✗ QML file not found: {qml_file}")
            return False
        
        with open(qml_file, 'r') as f:
            content = f.read()
        
        # Check for required components
        required = [
            "Dialog",
            "documentationManager",
            "loadDocuments",
            "filterDocuments",
            "loadDocument",
            "ListView",
            "TextArea",
            "searchField"
        ]
        
        missing = []
        for item in required:
            if item not in content:
                missing.append(item)
        
        if missing:
            print(f"✗ Missing required components: {missing}")
            return False
        
        print(f"✓ QML dialog syntax appears valid ({len(content)} characters)")
        print(f"  Contains all required components: {', '.join(required)}")
        return True
    except Exception as e:
        print(f"✗ QML syntax test failed: {e}")
        return False

def test_main_qml_integration():
    """Test main.qml integration."""
    print("\nTesting main.qml integration...")
    try:
        main_qml = Path(__file__).parent / "qml" / "main.qml"
        if not main_qml.exists():
            print(f"✗ main.qml not found: {main_qml}")
            return False
        
        with open(main_qml, 'r') as f:
            content = f.read()
        
        # Check for dialog declaration
        if "DocumentationBrowserDialog" not in content:
            print("✗ DocumentationBrowserDialog not found in main.qml")
            return False
        print("✓ DocumentationBrowserDialog declaration found")
        
        # Check for menu item
        if "Documentation Browser" not in content:
            print("✗ Documentation Browser menu item not found")
            return False
        print("✓ Documentation Browser menu item found")
        
        # Check for keyboard shortcut
        if "Ctrl+Shift+H" not in content:
            print("✗ Ctrl+Shift+H shortcut not found")
            return False
        print("✓ Ctrl+Shift+H shortcut found")
        
        return True
    except Exception as e:
        print(f"✗ main.qml integration test failed: {e}")
        return False

def test_main_py_integration():
    """Test main.py integration."""
    print("\nTesting main.py integration...")
    try:
        main_py = Path(__file__).parent / "main.py"
        if not main_py.exists():
            print(f"✗ main.py not found: {main_py}")
            return False
        
        with open(main_py, 'r') as f:
            content = f.read()
        
        # Check for import
        if "from backend.documentation_manager import DocumentationManager" not in content:
            print("✗ DocumentationManager import not found in main.py")
            return False
        print("✓ DocumentationManager import found")
        
        # Check for instantiation
        if "documentation_manager = DocumentationManager()" not in content:
            print("✗ DocumentationManager instantiation not found")
            return False
        print("✓ DocumentationManager instantiation found")
        
        # Check for context property
        if 'setContextProperty("documentationManager"' not in content:
            print("✗ documentationManager context property not found")
            return False
        print("✓ documentationManager context property found")
        
        return True
    except Exception as e:
        print(f"✗ main.py integration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Documentation Browser Implementation Tests")
    print("=" * 60)
    
    tests = [
        ("Backend Import", test_backend_import),
        ("Manager Creation", test_documentation_manager_creation),
        ("Manager Methods", test_documentation_methods),
        ("QML Dialog Syntax", test_qml_dialog_syntax),
        ("main.qml Integration", test_main_qml_integration),
        ("main.py Integration", test_main_py_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' raised exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
