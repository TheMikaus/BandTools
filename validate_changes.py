#!/usr/bin/env python3
"""
Validation script for AudioBrowser TreeView selection changes
"""
import sys
import os
import re
from pathlib import Path

def validate_syntax():
    """Validate that audio_browser.py has valid syntax"""
    try:
        audio_browser_path = Path(__file__).parent / "AudioBrowserAndAnnotation" / "audio_browser.py"
        with open(audio_browser_path, 'r') as f:
            content = f.read()
        
        # Try to compile the file
        compile(content, str(audio_browser_path), 'exec')
        print("✓ audio_browser.py syntax is valid")
        return True
    except Exception as e:
        print(f"✗ Syntax error in audio_browser.py: {e}")
        return False

def validate_stylesheet_present():
    """Validate that our stylesheet changes are present"""
    try:
        audio_browser_path = Path(__file__).parent / "AudioBrowserAndAnnotation" / "audio_browser.py"
        with open(audio_browser_path, 'r') as f:
            content = f.read()
        
        # Check for our specific styling
        required_colors = ["#1e3a8a", "#1d4ed8", "#2563eb"]
        required_selectors = ["QTreeView::item:selected", "QTreeView::item:selected:active", "QTreeView::item:selected:!active"]
        
        all_colors_present = all(color in content for color in required_colors)
        all_selectors_present = all(selector in content for selector in required_selectors)
        
        if all_colors_present and all_selectors_present:
            print("✓ Enhanced selection stylesheet is present")
            return True
        else:
            print("✗ Enhanced selection stylesheet is missing or incomplete")
            return False
            
    except Exception as e:
        print(f"✗ Error checking stylesheet: {e}")
        return False

def validate_color_contrast():
    """Validate that our color choices meet accessibility standards"""
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def luminance(rgb):
        def srgb_to_linear(c):
            c = c / 255.0
            if c <= 0.03928:
                return c / 12.92
            else:
                return ((c + 0.055) / 1.055) ** 2.4
        
        r, g, b = rgb
        return 0.2126 * srgb_to_linear(r) + 0.7152 * srgb_to_linear(g) + 0.0722 * srgb_to_linear(b)

    def contrast_ratio(color1, color2):
        lum1 = luminance(hex_to_rgb(color1))
        lum2 = luminance(hex_to_rgb(color2))
        
        if lum1 > lum2:
            return (lum1 + 0.05) / (lum2 + 0.05)
        else:
            return (lum2 + 0.05) / (lum1 + 0.05)

    # Test our color choices
    background_colors = ["#1e3a8a", "#1d4ed8", "#2563eb"]
    text_color = "#ffffff"  # white
    
    all_pass = True
    print("Color contrast validation:")
    
    for bg_color in background_colors:
        ratio = contrast_ratio(bg_color, text_color)
        passes_aa = ratio >= 4.5
        
        if passes_aa:
            print(f"  ✓ {bg_color} vs {text_color}: {ratio:.2f}:1 (PASS)")
        else:
            print(f"  ✗ {bg_color} vs {text_color}: {ratio:.2f}:1 (FAIL)")
            all_pass = False
    
    return all_pass

def main():
    """Run all validation tests"""
    print("Validating AudioBrowser TreeView selection enhancements...")
    print()
    
    tests = [
        ("Syntax validation", validate_syntax),
        ("Stylesheet presence", validate_stylesheet_present),
        ("Color contrast", validate_color_contrast),
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        result = test_func()
        if not result:
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 All validations passed! The TreeView selection enhancement is ready.")
    else:
        print("❌ Some validations failed. Please review the changes.")
    
    return all_passed

if __name__ == "__main__":
    sys.exit(0 if main() else 1)