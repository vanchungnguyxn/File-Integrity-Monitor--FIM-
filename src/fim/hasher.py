"""File hashing utilities for File Integrity Monitor."""

import hashlib
from pathlib import Path
from typing import Optional


def file_sha256(path: Path, chunk_size: int = 1 << 20) -> Optional[str]:
    """
    Calculate SHA256 hash of a file.
    
    Args:
        path: Path to the file
        chunk_size: Size of chunks to read (default 1MB)
        
    Returns:
        SHA256 hash as hex string, or None if file cannot be read
    """
    try:
        sha256_hash = hashlib.sha256()
        
        with open(path, 'rb') as f:
            while chunk := f.read(chunk_size):
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()
    
    except (OSError, IOError, PermissionError):
        return None
