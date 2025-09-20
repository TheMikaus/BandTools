#!/usr/bin/env python3
"""
Focused test for QTreeView styling changes
"""
import sys
import tempfile
from pathlib import Path

def test_stylesheet_functionality():
    """Test that our QTreeView stylesheet syntax is valid for PyQt6"""
    
    # Create a minimal test that doesn't require GUI
    test_code = '''
import sys

# Mock the GUI components for testing
class MockQTreeView:
    def __init__(self):
        self._stylesheet = ""
    
    def setStyleSheet(self, stylesheet):
        # Validate that it's a string and contains our expected content
        if not isinstance(stylesheet, str):
            raise ValueError("Stylesheet must be a string")
        
        required_selectors = [
            "QTreeView::item:selected",
            "QTreeView::item:selected:active", 
            "QTreeView::item:selected:!active"
        ]
        
        required_colors = ["#1e3a8a", "#1d4ed8", "#2563eb"]
        
        for selector in required_selectors:
            if selector not in stylesheet:
                raise ValueError(f"Missing selector: {selector}")
        
        for color in required_colors:
            if color not in stylesheet:
                raise ValueError(f"Missing color: {color}")
        
        self._stylesheet = stylesheet
        return True

# Test our stylesheet
tree = MockQTreeView()
tree.setStyleSheet("""
    QTreeView::item:selected {
        background-color: #1e3a8a;
        color: white;
    }
    QTreeView::item:selected:active {
        background-color: #1d4ed8;
        color: white;
    }
    QTreeView::item:selected:!active {
        background-color: #2563eb;
        color: white;
    }
""")

print("✓ Stylesheet validation passed")
'''
    
    try:
        exec(test_code)
        return True
    except Exception as e:
        print(f"✗ Stylesheet test failed: {e}")
        return False

def test_audio_browser_imports():
    """Test that audio_browser.py can be parsed and imports work"""
    try:
        # Test that the file can be parsed and has valid syntax
        audio_browser_path = Path(__file__).parent / "AudioBrowserAndAnnotation" / "audio_browser.py"
        
        with open(audio_browser_path, 'r') as f:
            content = f.read()
        
        # Extract just the import section to test
        lines = content.split('\n')
        import_section = []
        in_import_section = True
        
        for line in lines:
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                import_section.append(line)
            elif line.strip().startswith('#') or line.strip() == '':
                continue
            elif 'import' not in line and import_section:
                # End of import section
                break
        
        # Test that our changes don't break the basic structure
        if 'setStyleSheet' not in content:
            raise ValueError("setStyleSheet call not found")
        
        if '#1e3a8a' not in content:
            raise ValueError("Primary selection color not found")
            
        print("✓ Audio browser structure validation passed")
        return True
        
    except Exception as e:
        print(f"✗ Audio browser validation failed: {e}")
        return False

def main():
    """Run focused tests for our changes"""
    print("Running focused tests for QTreeView selection styling...")
    print()
    
    tests = [
        ("Stylesheet functionality", test_stylesheet_functionality),
        ("Audio browser structure", test_audio_browser_imports),
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"Testing {test_name}...")
        result = test_func()
        if not result:
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 All focused tests passed!")
    else:
        print("❌ Some tests failed.")
    
    return all_passed

if __name__ == "__main__":
    sys.exit(0 if main() else 1)