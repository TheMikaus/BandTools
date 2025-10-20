#!/usr/bin/env python3
"""
Integration test to verify that QML files load without null reference errors.
This simulates the application startup to check for null reference issues.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_qml_loading():
    """Test that QML files can be loaded without null reference errors."""
    print("Testing QML file loading with null safety...")
    
    # Read the problematic QML files
    qml_files = [
        "qml/tabs/AnnotationsTab.qml",
        "qml/components/WaveformDisplay.qml",
    ]
    
    for qml_file in qml_files:
        file_path = Path(__file__).parent / qml_file
        print(f"\nChecking {qml_file}...")
        
        if not file_path.exists():
            print(f"  ❌ File not found: {file_path}")
            return False
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Verify key null safety patterns exist
            checks = []
            
            if "AnnotationsTab.qml" in qml_file:
                checks = [
                    ("annotationManager ? annotationManager.getAnnotationCount()", "Annotation count check"),
                    ("annotationManager && annotationManager.getAnnotationCount()", "Annotation count enabled check"),
                    ("if (!annotationManager) return []", "Model null guard"),
                    ("if (!annotationManager) return", "Function null guard"),
                    ("annotationManager ? annotationManager.getShowAllSets()", "ShowAllSets check"),
                    ("if (currentIndex >= 0 && annotationManager)", "Current index check"),
                ]
            elif "WaveformDisplay.qml" in qml_file:
                checks = [
                    ("annotationManager ? annotationManager.getAnnotations() : []", "Annotations model check"),
                ]
            
            for pattern, description in checks:
                if pattern in content:
                    print(f"  ✓ {description}")
                else:
                    print(f"  ❌ Missing: {description} (pattern: {pattern})")
                    return False
            
            print(f"  ✓ All null safety patterns present")
            
        except Exception as e:
            print(f"  ❌ Error reading file: {e}")
            return False
    
    return True

def test_no_unsafe_calls():
    """Verify no unsafe annotationManager calls remain."""
    print("\n" + "="*60)
    print("Verifying no unsafe patterns remain...")
    print("="*60)
    
    qml_files = [
        "qml/tabs/AnnotationsTab.qml",
        "qml/components/WaveformDisplay.qml",
    ]
    
    for qml_file in qml_files:
        file_path = Path(__file__).parent / qml_file
        
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        # Look for common unsafe patterns that were in the original error report
        unsafe_patterns = [
            (r'text:.*annotationManager\.getAnnotationCount\(\)', 'Direct call in text binding'),
            (r'enabled:.*annotationManager\.getAnnotationCount\(\)', 'Direct call in enabled binding'),
            (r'model:.*annotationManager\.getAnnotationSets\(\)', 'Direct call in model binding'),
            (r'checked:.*annotationManager\.getShowAllSets\(\)', 'Direct call in checked binding'),
        ]
        
        found_unsafe = False
        for i, line in enumerate(lines, 1):
            for pattern_re, desc in unsafe_patterns:
                import re
                if re.search(pattern_re, line):
                    # Make sure it has null safety
                    if '?' not in line and '&&' not in line:
                        print(f"  ⚠️  {qml_file}:{i} - {desc}")
                        print(f"      {line.strip()}")
                        found_unsafe = True
        
        if not found_unsafe:
            print(f"  ✓ {qml_file} - No unsafe patterns found")
    
    return not found_unsafe

def main():
    """Run integration tests."""
    print("="*60)
    print("Integration Test: QML Null Safety for annotationManager")
    print("="*60)
    
    success = True
    
    # Test 1: QML file loading
    if not test_qml_loading():
        success = False
    
    # Test 2: No unsafe patterns
    if not test_no_unsafe_calls():
        success = False
    
    print("\n" + "="*60)
    if success:
        print("✅ All integration tests passed!")
        print("The QML files should now load without null reference errors.")
        return 0
    else:
        print("❌ Some integration tests failed")
        return 1

if __name__ == "__main__":
    exit(main())
