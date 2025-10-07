# BandTools Repository Standards

This document defines the standards that all applications in the BandTools repository must follow to ensure consistency, maintainability, and ease of development.

## Overview

The BandTools repository contains multiple desktop applications for musicians. To maintain quality and consistency across all applications, we enforce the following standards:

1. **Code Quality**: All code must compile and run without errors
2. **Documentation Organization**: Structured documentation in standard folders
3. **Dependency Management**: Auto-installation of required dependencies
4. **Application Stability**: Applications must run without crashing

## Required Standards

### 1. Code Quality and Compilation

**Requirement**: All Python files must have valid syntax and compile without errors.

**Verification**:
```bash
python3 -m py_compile <application_file>.py
```

**Implementation**:
- Use proper Python syntax following PEP 8 guidelines
- Test code compilation before committing
- Use type hints where applicable

### 2. Documentation Organization

**Requirement**: Every application MUST have a `docs/` folder with the following structure:

```
ApplicationName/
├── docs/
│   ├── INDEX.md              # Documentation index and navigation
│   ├── user_guides/          # End-user documentation
│   ├── technical/            # Developer/technical documentation
│   └── test_plans/           # QA and testing documentation
```

**Documentation Categories**:

#### User Guides (`docs/user_guides/`)
- How-to guides and tutorials
- Feature explanations for end users
- Setup and configuration guides
- Visual guides and UI documentation

**Target Audience**: End users, musicians, band members

#### Technical Documentation (`docs/technical/`)
- Implementation details and architecture
- Build instructions (BUILD.md)
- Developer notes and design decisions
- API documentation
- Feature roadmaps and improvement ideas

**Target Audience**: Developers, contributors, technical users

#### Test Plans (`docs/test_plans/`)
- Test cases and procedures
- QA checklists
- Bug reporting templates
- Validation criteria
- Test execution results

**Target Audience**: QA testers, developers, contributors

**INDEX.md Requirements**:
- Every `docs/` folder must contain an `INDEX.md` file
- INDEX.md should list all documentation with brief descriptions
- Include cross-references to related documents
- Maintain up-to-date links to all documentation

**Empty Folders**:
- Use `.gitkeep` files to preserve empty documentation folders in git
- This ensures the folder structure is maintained even when no documents exist yet

### 3. Dependency Management

**Requirement**: All applications must implement automatic dependency installation.

**Auto-Install Pattern**:

All applications should include an auto-install function similar to:

```python
def _ensure_import(mod_name: str, pip_name: str | None = None) -> tuple[bool, str]:
    """Try to import a module, auto-installing if needed."""
    try:
        importlib.import_module(mod_name)
        return True, ""
    except ImportError:
        if getattr(sys, "frozen", False):
            return False, f"{mod_name} is not available in this frozen build"
        
        pkg = pip_name or mod_name
        print(f"Installing {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        
        try:
            importlib.import_module(mod_name)
            return True, ""
        except ImportError as e:
            return False, f"Failed to import {mod_name}: {e}"
```

**Benefits**:
- Users don't need to manually install dependencies
- Simplifies first-time setup
- Works in development and can be bundled for frozen builds

**Common Dependencies**:
- AudioBrowser: PyQt6, pydub (optional)
- PolyRhythmMetronome: numpy, sounddevice, simpleaudio
- All apps: Standard library modules (json, pathlib, etc.)

### 4. Application Stability

**Requirement**: Applications must handle errors gracefully and not crash unexpectedly.

**Implementation Guidelines**:
- Use try-except blocks for file operations
- Validate user input before processing
- Provide meaningful error messages to users
- Handle missing optional dependencies gracefully
- Test basic functionality before releases

## Verification

### Automated Verification Script

The repository includes `verify_repository_standards.py` to check compliance:

```bash
python3 verify_repository_standards.py
```

This script verifies:
- ✓ Python syntax validity
- ✓ Documentation folder structure
- ✓ Presence of auto-install mechanisms
- ✓ Existence of README and CHANGELOG files

### Expected Output

When all standards are met:
```
✓ All applications meet repository standards!
Total: 4/4 applications meet required standards
```

## Complete Application Structure

Here's the complete recommended structure for each application:

```
ApplicationName/
├── main_application.py        # Primary application file
├── README.md                  # Application overview and quick start
├── CHANGELOG.md               # Version history and changes
├── BUILD.md                   # Build instructions (if applicable)
├── build_exe.bat              # Windows build script (if applicable)
├── build_exe.sh               # Unix/Linux build script (if applicable)
├── docs/                      # Documentation folder
│   ├── INDEX.md               # Documentation index
│   ├── user_guides/           # End-user documentation
│   │   ├── .gitkeep           # Preserve empty folder
│   │   └── FEATURE_GUIDE.md   # Feature guides
│   ├── technical/             # Technical documentation
│   │   ├── .gitkeep           # Preserve empty folder
│   │   ├── BUILD.md           # Build instructions
│   │   └── IMPLEMENTATION.md  # Implementation details
│   └── test_plans/            # Testing documentation
│       ├── .gitkeep           # Preserve empty folder
│       └── TEST_PLAN.md       # Test procedures
└── additional_files           # Icons, specs, data files, etc.
```

## Compliance Checklist

Before completing any task or feature, verify:

- [ ] Code compiles without syntax errors
- [ ] Application runs and performs basic functions
- [ ] Documentation folders exist (user_guides, technical, test_plans)
- [ ] INDEX.md exists in docs/ folder
- [ ] Auto-install mechanism is present for dependencies
- [ ] README.md exists and is up-to-date
- [ ] CHANGELOG.md is updated with changes
- [ ] Verification script passes: `python3 verify_repository_standards.py`

## Working with Copilot/AI Assistants

When using GitHub Copilot or other AI assistants on this repository:

1. **Always verify standards** after making changes
2. **Run the verification script** before committing
3. **Update documentation** when adding features
4. **Test application functionality** - don't just check syntax
5. **Follow existing patterns** in the codebase

The `.github/copilot-instructions.md` file contains detailed guidelines for AI assistants working on this repository.

## Migration Guide

If you have an existing application that doesn't meet these standards:

1. **Create docs structure**:
   ```bash
   mkdir -p docs/user_guides docs/technical docs/test_plans
   touch docs/user_guides/.gitkeep
   touch docs/technical/.gitkeep
   touch docs/test_plans/.gitkeep
   ```

2. **Create INDEX.md**:
   - Copy template from another application's docs/INDEX.md
   - Customize for your application
   - List existing documentation

3. **Add auto-install**:
   - Review existing applications for auto-install patterns
   - Implement `_ensure_import()` or `ensure_pkg()` function
   - Use it for all external dependencies

4. **Move existing docs**:
   - Sort documentation by category
   - Move to appropriate folders
   - Update cross-references

5. **Verify compliance**:
   ```bash
   python3 verify_repository_standards.py
   ```

## Benefits

Following these standards provides:

- **Consistency**: All applications follow the same structure
- **Discoverability**: Easy to find documentation and resources
- **Maintainability**: Clear organization aids long-term maintenance
- **Onboarding**: New contributors can quickly understand the structure
- **Quality**: Automated verification catches issues early
- **User Experience**: Auto-install reduces setup friction

## Questions and Support

For questions about these standards:
- Review existing applications as examples
- Check `.github/copilot-instructions.md` for detailed guidelines
- Consult documentation in AudioBrowserOrig/docs/ (most mature example)
- Open an issue on GitHub for clarification

---

**Last Updated**: 2024

**Version**: 1.0

**Maintained by**: BandTools Development Team
