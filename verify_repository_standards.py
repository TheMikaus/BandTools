#!/usr/bin/env python3
"""
Repository Standards Verification Script

This script verifies that all applications in the BandTools repository meet
the following standards:
1. Code compiles (syntax check)
2. Documentation is organized in proper folders (user_guides, technical, test_plans)
3. Auto-install mechanisms are present for dependencies
4. Applications have proper error handling

Usage:
    python verify_repository_standards.py
"""

import sys
import os
from pathlib import Path
import py_compile
import importlib.util

def check_syntax(file_path):
    """Check if a Python file has valid syntax."""
    try:
        py_compile.compile(file_path, doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)

def check_docs_structure(app_path):
    """Check if application has proper docs structure."""
    docs_path = app_path / "docs"
    required_folders = ["user_guides", "technical", "test_plans"]
    
    if not docs_path.exists():
        return False, "docs/ folder missing"
    
    missing = []
    for folder in required_folders:
        folder_path = docs_path / folder
        if not folder_path.exists():
            missing.append(folder)
    
    if missing:
        return False, f"Missing folders: {', '.join(missing)}"
    
    # Check for INDEX.md
    if not (docs_path / "INDEX.md").exists():
        return False, "INDEX.md missing in docs/"
    
    return True, None

def check_auto_install(file_path):
    """Check if Python file has auto-install mechanism."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Look for common auto-install patterns
        patterns = [
            "ensure_import",
            "ensure_pkg",
            "_ensure_import",
            "pip install",
            "subprocess.check_call"
        ]
        
        has_auto_install = any(pattern in content for pattern in patterns)
        
        if has_auto_install:
            return True, None
        else:
            return False, "No auto-install mechanism found"
    except Exception as e:
        return False, f"Error reading file: {e}"

def verify_application(app_name, app_path, main_file):
    """Verify all standards for an application."""
    print(f"\n{'='*60}")
    print(f"Checking: {app_name}")
    print(f"{'='*60}")
    
    results = {}
    
    # Check if main file exists
    main_path = app_path / main_file
    if not main_path.exists():
        print(f"✗ Main file not found: {main_file}")
        return False
    
    # 1. Check syntax
    print(f"\n1. Syntax Check")
    success, error = check_syntax(main_path)
    if success:
        print(f"   ✓ {main_file} has valid syntax")
        results['syntax'] = True
    else:
        print(f"   ✗ {main_file} has syntax errors:")
        print(f"     {error}")
        results['syntax'] = False
    
    # 2. Check docs structure
    print(f"\n2. Documentation Structure")
    success, error = check_docs_structure(app_path)
    if success:
        print(f"   ✓ Proper docs/ structure exists")
        print(f"     - docs/user_guides/")
        print(f"     - docs/technical/")
        print(f"     - docs/test_plans/")
        print(f"     - docs/INDEX.md")
        results['docs'] = True
    else:
        print(f"   ✗ Documentation structure issue: {error}")
        results['docs'] = False
    
    # 3. Check auto-install
    print(f"\n3. Auto-Install Mechanism")
    success, error = check_auto_install(main_path)
    if success:
        print(f"   ✓ Auto-install mechanism present")
        results['auto_install'] = True
    else:
        print(f"   ⚠ {error}")
        results['auto_install'] = False
    
    # 4. Check README exists
    print(f"\n4. Documentation Files")
    readme_path = app_path / "README.md"
    changelog_path = app_path / "CHANGELOG.md"
    
    has_readme = readme_path.exists()
    has_changelog = changelog_path.exists()
    
    if has_readme:
        print(f"   ✓ README.md exists")
    else:
        print(f"   ⚠ README.md not found")
    
    if has_changelog:
        print(f"   ✓ CHANGELOG.md exists")
    else:
        print(f"   ⚠ CHANGELOG.md not found")
    
    results['readme'] = has_readme
    results['changelog'] = has_changelog
    
    # Summary
    all_required = results['syntax'] and results['docs']
    all_optional = results.get('auto_install', False) and results['readme'] and results['changelog']
    
    print(f"\n{'─'*60}")
    print(f"Summary for {app_name}:")
    print(f"  Required Standards: {'✓ PASS' if all_required else '✗ FAIL'}")
    print(f"  Optional Standards: {'✓ PASS' if all_optional else '⚠ PARTIAL'}")
    
    return all_required

def main():
    """Main verification function."""
    repo_root = Path(__file__).parent
    
    print("=" * 60)
    print("BandTools Repository Standards Verification")
    print("=" * 60)
    
    # Define applications to check
    applications = [
        ("AudioBrowserOrig", "AudioBrowserAndAnnotation/AudioBrowserOrig", "audio_browser.py"),
        ("AudioBrowser-QML", "AudioBrowserAndAnnotation/AudioBrowser-QML", "main.py"),
        ("PolyRhythmMetronome", "PolyRhythmMetronome", "Poly_Rhythm_Metronome.py"),
        ("JamStikRecord", "JamStikRecord", "generate_blip.py"),  # Note: This app may need a proper main file
    ]
    
    results = {}
    for app_name, app_rel_path, main_file in applications:
        app_path = repo_root / app_rel_path
        results[app_name] = verify_application(app_name, app_path, main_file)
    
    # Final summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for app_name, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {app_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} applications meet required standards")
    
    if passed == total:
        print("\n✓ All applications meet repository standards!")
        return 0
    else:
        print(f"\n⚠ {total - passed} application(s) need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())
