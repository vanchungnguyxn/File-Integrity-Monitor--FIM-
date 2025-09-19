"""Baseline management for File Integrity Monitor."""

import os
from pathlib import Path
from typing import Dict

from .hasher import file_sha256
from .storage import load_json, save_json


def build_baseline(root: Path) -> Dict[str, str]:
    """
    Build baseline by scanning all files in directory tree.
    
    Args:
        root: Root directory to scan
        
    Returns:
        Dictionary mapping relative file paths to SHA256 hashes
    """
    baseline = {}
    root = Path(root).resolve()
    
    for file_path in root.rglob('*'):
        if file_path.is_file():
            relative_path = file_path.relative_to(root)
            hash_value = file_sha256(file_path)
            
            if hash_value is not None:
                baseline[str(relative_path)] = hash_value
    
    return baseline


def save_baseline(baseline: Dict[str, str], path: Path) -> None:
    """
    Save baseline to JSON file.
    
    Args:
        baseline: Dictionary mapping file paths to hashes
        path: Path to save baseline to
    """
    data = {
        'baseline': baseline
    }
    save_json(data, path)


def load_baseline(path: Path) -> Dict[str, str]:
    """
    Load baseline from JSON file.
    
    Args:
        path: Path to baseline JSON file
        
    Returns:
        Dictionary mapping file paths to hashes
        
    Raises:
        FileNotFoundError: If baseline file doesn't exist
    """
    data = load_json(path)
    return data.get('baseline', {})
