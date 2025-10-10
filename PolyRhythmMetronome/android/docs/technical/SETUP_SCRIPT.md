# Android Development Setup Script - Technical Documentation

## Overview

The `setup_android_dev.py` script automates the installation and verification of all dependencies required to build the PolyRhythmMetronome Android app using Buildozer.

## Purpose

Building Android apps with Python and Buildozer requires numerous dependencies:
- Python 3.8+ with pip
- Build tools (buildozer, cython)
- Java Development Kit (OpenJDK 11+)
- System libraries and build tools
- Android SDK and NDK (downloaded by buildozer)

This script eliminates the manual setup process and ensures all requirements are met before attempting to build.

## Architecture

### Script Structure

```
setup_android_dev.py
├── Detection Functions
│   ├── detect_os()           # Identify Linux, macOS, Windows, WSL
│   ├── check_python_version() # Verify Python 3.8+
│   ├── check_system_command() # Check for system commands
│   ├── check_wsl_installed()  # Check if WSL is installed (Windows)
│   └── check_ubuntu_in_wsl()  # Check if Ubuntu is in WSL
│
├── Check Functions
│   ├── check_pip()            # Verify pip availability
│   ├── check_openjdk()        # Check Java installation
│   └── check_system_packages_ubuntu()
│
├── Installation Functions
│   ├── check_and_install_pip_package()
│   ├── install_openjdk_ubuntu()
│   ├── install_wsl_windows()  # Guide WSL installation
│   ├── install_ubuntu_in_wsl() # Guide Ubuntu installation
│   ├── setup_wsl_and_ubuntu()  # Orchestrate WSL/Ubuntu setup
│   └── check_system_packages_ubuntu()
│
├── Verification Functions
│   └── verify_buildozer_setup()
│
└── Main Flow
    └── main()                 # Orchestrates all checks
```

### Design Principles

1. **Non-destructive**: Only installs missing dependencies
2. **Fail-fast**: Stops if critical requirements aren't met
3. **Informative**: Clear output with color-coded status
4. **Safe**: Requires sudo only for system packages
5. **Cross-platform**: Detects OS and provides appropriate instructions

## Functionality

### 1. Python Version Check

```python
def check_python_version():
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        return True
```

**Why**: Buildozer requires Python 3.8+ for proper operation.

### 2. pip Availability

```python
def check_pip():
    success, stdout, stderr = run_command([sys.executable, "-m", "pip", "--version"])
```

**Why**: All Python packages are installed via pip. Using `python -m pip` ensures we use the correct pip for the current Python interpreter.

### 3. Python Package Installation

```python
def check_and_install_pip_package(package_name, import_name=None, pip_name=None):
    try:
        __import__(import_name)
        return True  # Already installed
    except ImportError:
        # Install with --user flag
        run_command([sys.executable, "-m", "pip", "install", "--user", pip_name])
```

**Why**: `--user` flag installs to `~/.local/` avoiding permission issues. Non-root users can install Python packages.

### 4. OpenJDK Detection

```python
def check_openjdk():
    success, stdout, stderr = run_command(["java", "-version"])
    # Check stderr because java -version outputs to stderr
    if "openjdk" in output.lower() and ("11" in output or "17" in output):
        return True
```

**Why**: 
- Java is required for Android SDK tools
- OpenJDK 11+ is required by recent Android build tools
- `java -version` outputs to stderr by convention

### 5. System Package Detection (Ubuntu)

```python
def check_system_packages_ubuntu():
    required_packages = [
        "git", "zip", "unzip", "autoconf", "libtool", "pkg-config",
        "zlib1g-dev", "libncurses-dev", "libncursesw5-dev", 
        "cmake", "libffi-dev", "libssl-dev"
    ]
    
    for package in required_packages:
        run_command(["dpkg", "-s", package])
```

**Why**:
- `dpkg -s` checks if a Debian package is installed
- Returns non-zero exit code if package is missing
- These libraries are required by Python-for-Android compilation

### 6. OS Detection

```python
def detect_os():
    system = platform.system()
    if system == "Linux":
        # Check if running inside WSL
        with open("/proc/version", "r") as f:
            if "microsoft" in f.read().lower():
                return "wsl"
        # Check /etc/os-release for distribution
        if "Ubuntu" in content or "Debian" in content:
            return "ubuntu"
```

**Why**: Different operating systems require different installation methods. Ubuntu/Debian use `apt`, Fedora uses `dnf`, macOS uses `brew`. WSL detection allows the script to provide appropriate instructions for Windows users.

### 7. WSL and Ubuntu Detection (Windows)

```python
def check_wsl_installed():
    success, stdout, stderr = run_command(["wsl", "--status"])
    return success or "Default Distribution" in stdout

def check_ubuntu_in_wsl():
    success, stdout, stderr = run_command(["wsl", "--list", "--verbose"])
    return "Ubuntu" in stdout or "ubuntu" in stdout.lower()
```

**Why**: On Windows, buildozer requires a Linux environment. WSL (Windows Subsystem for Linux) provides this. The script checks if WSL and Ubuntu are installed and guides users through installation if needed.

## Package Requirements

### Why These Packages?

#### Python Packages

| Package | Purpose |
|---------|---------|
| `buildozer` | Android APK build orchestrator |
| `cython` | Python to C compiler (required by Kivy) |

#### System Packages

| Package | Purpose |
|---------|---------|
| `openjdk-11-jdk` | Java compiler and runtime (Android SDK) |
| `git` | Version control (downloads dependencies) |
| `zip`, `unzip` | Archive handling (APK creation) |
| `autoconf`, `libtool` | Build system tools |
| `pkg-config` | Library configuration |
| `zlib1g-dev` | Compression library |
| `libncurses-dev` | Terminal UI library |
| `cmake` | Build system generator |
| `libffi-dev` | Foreign function interface (ctypes) |
| `libssl-dev` | SSL/TLS support |

### Removed Dependencies

**`libtinfo5`**: Removed because it's not available in Ubuntu 24.04+. The functionality is provided by `libncurses-dev` (ncurses6).

**`libncurses5-dev`**: Changed to `libncurses-dev` for better compatibility with modern Ubuntu versions.

## Output Format

### Color Coding

```python
GREEN = '\033[92m'   # ✓ Success
YELLOW = '\033[93m'  # ⚠ Warning
RED = '\033[91m'     # ✗ Error
BLUE = '\033[94m'    # ℹ Info
```

**Why**: Visual feedback makes it easier to quickly understand status without reading all text.

### Sections

1. **Header**: Environment setup context
2. **Python Check**: Version verification
3. **pip Check**: Package manager availability
4. **Python Packages**: buildozer and cython
5. **System Dependencies**: OS packages and Java
6. **Summary**: Final status and next steps

## Error Handling

### Strategy

1. **Continue on non-critical failures**: Script attempts all checks even if some fail
2. **Clear error messages**: Each failure explains what went wrong
3. **Actionable instructions**: Tells user exactly what to run manually
4. **Exit codes**: 
   - `0` = All dependencies installed
   - `1` = Some dependencies missing

### Example Error Flow

```python
all_checks_passed = True

if not check_python_version():
    all_checks_passed = False
    return 1  # Critical - can't continue

if not check_openjdk():
    all_checks_passed = False
    # Continue checking other dependencies

return 0 if all_checks_passed else 1
```

## Security Considerations

### sudo Usage

**Only required for**:
- Installing system packages (`apt install`)
- Installing OpenJDK

**Not required for**:
- Installing Python packages (uses `--user`)
- Checking package status
- Running script for status check

### Best Practice

```bash
# Run without sudo first to see what's needed
python3 setup_android_dev.py

# Then run with sudo if system packages are needed
sudo python3 setup_android_dev.py
```

## Platform Support

### Supported Platforms

#### Ubuntu/Debian (Full Support)
- ✓ Automatic package detection
- ✓ Automatic installation with sudo
- ✓ Verified on Ubuntu 24.04

#### WSL (Full Support)
- ✓ Detected automatically
- ✓ Same Ubuntu/Debian support
- ✓ Verified on WSL2 with Ubuntu

#### macOS (Instructions Only)
- Manual instructions provided
- Uses Homebrew for packages
- User must install manually

#### Fedora/RHEL (Instructions Only)
- Manual instructions provided
- Uses `dnf` for packages
- User must install manually

#### Windows (Guided Setup)
- ✓ Automatic WSL detection
- ✓ Automatic Ubuntu distribution check
- ✓ Provides step-by-step installation instructions
- ✓ Guides user to complete setup in Ubuntu/WSL
- Buildozer doesn't support native Windows
- Requires WSL2 or Docker for local builds

## Integration Points

### Buildozer Integration

After setup, buildozer will:
1. Read `buildozer.spec` configuration
2. Download Android SDK (~2GB) to `.buildozer/`
3. Download Android NDK (~1GB)
4. Install Python-for-Android toolchain
5. Compile Kivy and dependencies
6. Build APK

**First build**: 30-60 minutes
**Subsequent builds**: 5-10 minutes

### PATH Configuration

Buildozer installs to `~/.local/bin/`. Script checks if it's in PATH:

```python
def verify_buildozer_setup():
    if check_system_command("buildozer"):
        return True
    else:
        print("Add this to your ~/.bashrc:")
        print('export PATH="$HOME/.local/bin:$PATH"')
```

## Testing

### Manual Testing Checklist

- [ ] Run on fresh Ubuntu install
- [ ] Run without sudo (check status)
- [ ] Run with sudo (install packages)
- [ ] Verify all packages install correctly
- [ ] Check buildozer command works
- [ ] Verify OpenJDK version detection
- [ ] Test on Ubuntu 24.04, 22.04, 20.04

### Automated Testing

Currently, the script does not have automated tests. Future enhancement would add:
- Mock system commands for testing
- Docker-based testing on different OS versions
- CI/CD integration

## Maintenance

### Updating Dependencies

When buildozer requirements change:

1. Update `required_packages` list
2. Test on target OS versions
3. Update documentation
4. Update README with new requirements

### Version Compatibility

The script is designed to work with:
- Python 3.8 through 3.12+
- Buildozer 1.2+
- OpenJDK 11, 17, or 21
- Ubuntu 20.04, 22.04, 24.04

## Future Enhancements

### Planned Features

1. **Dry-run mode**: Show what would be installed without installing
2. **Quiet mode**: Less verbose output for CI/CD
3. **JSON output**: Machine-readable status for automation
4. **Automatic PATH update**: Modify shell rc files automatically
5. **Dependency version checking**: Verify minimum versions
6. **Cache cleanup**: Remove old buildozer caches

### Possible Improvements

1. **Docker support**: Detect if running in container
2. **Virtual environment detection**: Warn if in venv
3. **Disk space check**: Verify enough space for SDK/NDK
4. **Network check**: Verify internet connectivity
5. **Multi-language support**: Translations for error messages

## Related Documentation

- [SETUP_SCRIPT_README.md](../../SETUP_SCRIPT_README.md) - User guide
- [README.md](../../README.md) - Main Android app documentation
- [BUILD_GUIDE.md](BUILD_GUIDE.md) - Detailed build instructions

## References

- [Buildozer Documentation](https://buildozer.readthedocs.io/)
- [Python-for-Android](https://python-for-android.readthedocs.io/)
- [Kivy Documentation](https://kivy.org/doc/stable/)
- [Android Developer Guide](https://developer.android.com/)
