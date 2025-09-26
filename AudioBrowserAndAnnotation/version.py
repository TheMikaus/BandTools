#!/usr/bin/env python3
"""
Version management for AudioBrowser application.

The version scheme is MAJOR.MINOR where:
- MAJOR starts at 1 and represents significant releases
- MINOR increments automatically with each commit
"""

import subprocess
from pathlib import Path
from typing import Tuple


def get_git_commit_count() -> int:
    """Get the total number of commits in the current git repository."""
    try:
        # Get the directory containing this file
        current_dir = Path(__file__).parent
        
        # Run git rev-list --count HEAD from the current directory
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=current_dir,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return int(result.stdout.strip())
        else:
            # Fallback if git command fails
            return 1
            
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, ValueError, FileNotFoundError):
        # Fallback if git is not available or any other error occurs
        return 1


def get_version() -> Tuple[int, int]:
    """
    Get the current version as (major, minor) tuple.
    
    Returns:
        Tuple of (major_version, minor_version)
    """
    major_version = 1  # Start at version 1.x
    minor_version = get_git_commit_count()
    
    return (major_version, minor_version)


def get_version_string() -> str:
    """
    Get the version as a formatted string.
    
    Returns:
        Version string in format "MAJOR.MINOR"
    """
    major, minor = get_version()
    return f"{major}.{minor}"


def get_version_info() -> str:
    """
    Get detailed version information including build info.
    
    Returns:
        Detailed version string with additional info
    """
    version = get_version_string()
    commit_count = get_git_commit_count()
    
    try:
        # Try to get current commit hash
        current_dir = Path(__file__).parent
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=current_dir,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            commit_hash = result.stdout.strip()
            return f"Version {version} (build {commit_count}, commit {commit_hash})"
        else:
            return f"Version {version} (build {commit_count})"
            
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        return f"Version {version} (build {commit_count})"


# Constants for easy import
VERSION_TUPLE = get_version()
VERSION_STRING = get_version_string()
VERSION_INFO = get_version_info()

__version__ = VERSION_STRING

if __name__ == "__main__":
    # Allow running as a script to check version
    print(f"AudioBrowser {VERSION_INFO}")