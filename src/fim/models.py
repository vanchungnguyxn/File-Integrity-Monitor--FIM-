"""Data models for File Integrity Monitor."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Event:
    """Represents a file system event."""
    
    type: str  # 'ADDED', 'MODIFIED', 'DELETED'
    path: str
    old_hash: Optional[str] = None
    new_hash: Optional[str] = None
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'type': self.type,
            'path': self.path,
            'old_hash': self.old_hash,
            'new_hash': self.new_hash,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Event':
        """Create Event from dictionary."""
        return cls(
            type=data['type'],
            path=data['path'],
            old_hash=data.get('old_hash'),
            new_hash=data.get('new_hash'),
            timestamp=data.get('timestamp')
        )
