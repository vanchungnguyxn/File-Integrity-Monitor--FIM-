"""Storage utilities for File Integrity Monitor."""

import json
from pathlib import Path
from typing import Dict, List, Any

from .models import Event


def load_json(path: Path) -> Dict[str, Any]:
    """
    Load JSON data from file.
    
    Args:
        path: Path to JSON file
        
    Returns:
        Dictionary with JSON data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
    """
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: Dict[str, Any], path: Path) -> None:
    """
    Save data to JSON file.
    
    Args:
        data: Dictionary to save
        path: Path to save to
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_events(path: Path) -> List[Event]:
    """
    Load events from JSON file.
    
    Args:
        path: Path to events JSON file
        
    Returns:
        List of Event objects
    """
    try:
        data = load_json(path)
        return [Event.from_dict(event_data) for event_data in data.get('events', [])]
    except FileNotFoundError:
        return []


def save_events(events: List[Event], path: Path) -> None:
    """
    Save events to JSON file.
    
    Args:
        events: List of Event objects
        path: Path to save to
    """
    data = {
        'events': [event.to_dict() for event in events]
    }
    save_json(data, path)
