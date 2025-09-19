"""File system watcher for File Integrity Monitor."""

import os
from pathlib import Path
from typing import Dict, List
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer
import time

from .models import Event
from .hasher import file_sha256


class FIMEventHandler(FileSystemEventHandler):
    """Handler for file system events."""
    
    def __init__(self, root_path: Path, baseline: Dict[str, str]):
        """
        Initialize event handler.
        
        Args:
            root_path: Root directory being watched
            baseline: Current baseline dictionary
        """
        self.root_path = Path(root_path).resolve()
        self.baseline = baseline.copy()
        self.events: List[Event] = []
    
    def _get_relative_path(self, path: str) -> str:
        """Get relative path from absolute path."""
        abs_path = Path(path).resolve()
        return str(abs_path.relative_to(self.root_path))
    
    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation."""
        if event.is_directory:
            return
        
        try:
            rel_path = self._get_relative_path(event.src_path)
            new_hash = file_sha256(Path(event.src_path))
            
            if new_hash is not None:
                self.baseline[rel_path] = new_hash
                
                fim_event = Event(
                    type='ADDED',
                    path=rel_path,
                    new_hash=new_hash
                )
                self.events.append(fim_event)
        except (ValueError, OSError):
            # Ignore files outside root or access errors
            pass
    
    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification."""
        if event.is_directory:
            return
        
        try:
            rel_path = self._get_relative_path(event.src_path)
            new_hash = file_sha256(Path(event.src_path))
            
            if new_hash is not None:
                old_hash = self.baseline.get(rel_path)
                
                # Only record if hash actually changed
                if old_hash != new_hash:
                    self.baseline[rel_path] = new_hash
                    
                    fim_event = Event(
                        type='MODIFIED',
                        path=rel_path,
                        old_hash=old_hash,
                        new_hash=new_hash
                    )
                    self.events.append(fim_event)
        except (ValueError, OSError):
            # Ignore files outside root or access errors
            pass
    
    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file deletion."""
        if event.is_directory:
            return
        
        try:
            rel_path = self._get_relative_path(event.src_path)
            old_hash = self.baseline.pop(rel_path, None)
            
            if old_hash is not None:
                fim_event = Event(
                    type='DELETED',
                    path=rel_path,
                    old_hash=old_hash
                )
                self.events.append(fim_event)
        except ValueError:
            # Ignore files outside root
            pass
    
    def on_moved(self, event: FileSystemEvent) -> None:
        """Handle file moves (treat as delete + create)."""
        if event.is_directory:
            return
        
        # Handle as deletion from old location
        try:
            old_rel_path = self._get_relative_path(event.src_path)
            old_hash = self.baseline.pop(old_rel_path, None)
            
            if old_hash is not None:
                fim_event = Event(
                    type='DELETED',
                    path=old_rel_path,
                    old_hash=old_hash
                )
                self.events.append(fim_event)
        except ValueError:
            pass
        
        # Handle as creation at new location
        try:
            new_rel_path = self._get_relative_path(event.dest_path)
            new_hash = file_sha256(Path(event.dest_path))
            
            if new_hash is not None:
                self.baseline[new_rel_path] = new_hash
                
                fim_event = Event(
                    type='ADDED',
                    path=new_rel_path,
                    new_hash=new_hash
                )
                self.events.append(fim_event)
        except (ValueError, OSError):
            pass


def watch_directory(root_path: Path, baseline: Dict[str, str]) -> tuple[Dict[str, str], List[Event]]:
    """
    Watch directory for changes and return updated baseline and events.
    
    Args:
        root_path: Directory to watch
        baseline: Initial baseline
        
    Returns:
        Tuple of (updated_baseline, events_list)
    """
    event_handler = FIMEventHandler(root_path, baseline)
    observer = Observer()
    observer.schedule(event_handler, str(root_path), recursive=True)
    
    observer.start()
    
    try:
        print(f"Watching {root_path} for changes. Press Ctrl+C to stop...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping watcher...")
    finally:
        observer.stop()
        observer.join()
    
    return event_handler.baseline, event_handler.events
