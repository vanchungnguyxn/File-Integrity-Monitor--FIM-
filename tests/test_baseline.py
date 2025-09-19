"""Tests for baseline module."""

import tempfile
import json
from pathlib import Path
import pytest

from fim.baseline import build_baseline, save_baseline, load_baseline


class TestBaseline:
    """Test cases for baseline functionality."""
    
    def test_build_baseline_simple(self):
        """Test building baseline for a simple directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test files
            (temp_path / "file1.txt").write_text("content1")
            (temp_path / "file2.txt").write_text("content2")
            
            # Create subdirectory with file
            subdir = temp_path / "subdir"
            subdir.mkdir()
            (subdir / "file3.txt").write_text("content3")
            
            baseline = build_baseline(temp_path)
            
            # Should have 3 files
            assert len(baseline) == 3
            assert "file1.txt" in baseline
            assert "file2.txt" in baseline
            assert str(Path("subdir") / "file3.txt") in baseline
            
            # All values should be SHA256 hashes
            for hash_value in baseline.values():
                assert len(hash_value) == 64
                assert all(c in '0123456789abcdef' for c in hash_value)
    
    def test_build_baseline_empty_directory(self):
        """Test building baseline for an empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            baseline = build_baseline(temp_path)
            assert baseline == {}
    
    def test_build_baseline_nested_directories(self):
        """Test building baseline for nested directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create nested structure
            level1 = temp_path / "level1"
            level2 = level1 / "level2"
            level3 = level2 / "level3"
            
            level1.mkdir()
            level2.mkdir()
            level3.mkdir()
            
            (level1 / "file1.txt").write_text("content1")
            (level2 / "file2.txt").write_text("content2")
            (level3 / "file3.txt").write_text("content3")
            
            baseline = build_baseline(temp_path)
            
            assert len(baseline) == 3
            assert str(Path("level1") / "file1.txt") in baseline
            assert str(Path("level1") / "level2" / "file2.txt") in baseline
            assert str(Path("level1") / "level2" / "level3" / "file3.txt") in baseline
    
    def test_save_and_load_baseline(self):
        """Test saving and loading baseline to/from JSON file."""
        baseline_data = {
            "file1.txt": "hash1",
            "file2.txt": "hash2",
            "subdir/file3.txt": "hash3"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            baseline_path = Path(f.name)
        
        try:
            # Save baseline
            save_baseline(baseline_data, baseline_path)
            
            # Verify file was created and has correct structure
            assert baseline_path.exists()
            
            with open(baseline_path, 'r') as f:
                saved_data = json.load(f)
            
            assert "baseline" in saved_data
            assert saved_data["baseline"] == baseline_data
            
            # Load baseline
            loaded_baseline = load_baseline(baseline_path)
            assert loaded_baseline == baseline_data
            
        finally:
            baseline_path.unlink()
    
    def test_load_baseline_nonexistent_file(self):
        """Test loading baseline from non-existent file."""
        nonexistent_path = Path("/this/file/does/not/exist.json")
        
        with pytest.raises(FileNotFoundError):
            load_baseline(nonexistent_path)
    
    def test_load_baseline_invalid_json(self):
        """Test loading baseline from invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            invalid_path = Path(f.name)
        
        try:
            with pytest.raises(json.JSONDecodeError):
                load_baseline(invalid_path)
        finally:
            invalid_path.unlink()
    
    def test_load_baseline_missing_baseline_key(self):
        """Test loading baseline from JSON without baseline key."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"other_key": "value"}, f)
            json_path = Path(f.name)
        
        try:
            baseline = load_baseline(json_path)
            assert baseline == {}
        finally:
            json_path.unlink()
    
    def test_build_baseline_with_unreadable_files(self):
        """Test building baseline when some files are unreadable."""
        # Skip this test on Windows as chmod doesn't work the same way
        import os
        if os.name == 'nt':
            pytest.skip("File permission test not applicable on Windows")
            
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create readable file
            (temp_path / "readable.txt").write_text("content")
            
            # Create file and make it unreadable (on Unix systems)
            unreadable_file = temp_path / "unreadable.txt"
            unreadable_file.write_text("content")
            
            try:
                unreadable_file.chmod(0o000)  # Remove all permissions
                
                baseline = build_baseline(temp_path)
                
                # Should still include readable files
                assert "readable.txt" in baseline
                # Unreadable file should be excluded
                assert "unreadable.txt" not in baseline
                
            except (OSError, PermissionError):
                # Skip this test on systems that don't support chmod
                pytest.skip("Cannot test unreadable files on this system")
            finally:
                try:
                    unreadable_file.chmod(0o644)  # Restore permissions for cleanup
                except (OSError, PermissionError):
                    pass
