"""
File Utilities

Common file handling utility functions used across AudioBrowser applications.
"""

import re
from pathlib import Path
from typing import Tuple


def sanitize(name: str) -> str:
    """
    Sanitize a name for use in filenames by removing invalid characters.
    
    Args:
        name: Name to sanitize
        
    Returns:
        Sanitized name with invalid characters replaced by underscores
    """
    name = re.sub(r'[\\/:*?"<>|]+', "_", name.strip())
    return re.sub(r"\s+", " ", name).strip()


def sanitize_library_name(name: str) -> str:
    """
    Sanitize a library name for use in filenames: lowercase and replace spaces with underscores.
    
    Args:
        name: Library name to sanitize
        
    Returns:
        Sanitized library name (lowercase, spaces->underscores, no special chars)
    """
    name = re.sub(r'[\\/:*?"<>|]+', "_", name.strip())
    name = re.sub(r"\s+", "_", name).strip()
    return name.lower()


def file_signature(p: Path) -> Tuple[int, int]:
    """
    Get a signature for a file based on size and modification time.
    
    Args:
        p: Path to the file
        
    Returns:
        Tuple of (size, mtime) or (0, 0) if file cannot be accessed
    """
    try:
        st = p.stat()
        return int(st.st_size), int(st.st_mtime)
    except Exception:
        return (0, 0)
