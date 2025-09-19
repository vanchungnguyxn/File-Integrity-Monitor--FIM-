"""Tests for hasher module."""

import tempfile
from pathlib import Path
import pytest

from fim.hasher import file_sha256


class TestFileHasher:
    """Test cases for file hashing functionality."""
    
    def test_file_sha256_simple(self):
        """Test SHA256 calculation for a simple file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("hello world")
            temp_path = Path(f.name)
        
        try:
            hash_value = file_sha256(temp_path)
            # SHA256 of "hello world"
            expected = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
            assert hash_value == expected
        finally:
            temp_path.unlink()
    
    def test_file_sha256_empty_file(self):
        """Test SHA256 calculation for an empty file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            hash_value = file_sha256(temp_path)
            # SHA256 of empty string
            expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            assert hash_value == expected
        finally:
            temp_path.unlink()
    
    def test_file_sha256_binary_file(self):
        """Test SHA256 calculation for a binary file."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            f.write(b'\x00\x01\x02\x03\xFF\xFE\xFD\xFC')
            temp_path = Path(f.name)
        
        try:
            hash_value = file_sha256(temp_path)
            # This should produce a consistent hash
            assert hash_value is not None
            assert len(hash_value) == 64  # SHA256 is 64 hex chars
            assert all(c in '0123456789abcdef' for c in hash_value)
        finally:
            temp_path.unlink()
    
    def test_file_sha256_large_file(self):
        """Test SHA256 calculation for a large file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            # Write 2MB of data
            data = "A" * (2 * 1024 * 1024)
            f.write(data)
            temp_path = Path(f.name)
        
        try:
            hash_value = file_sha256(temp_path)
            assert hash_value is not None
            assert len(hash_value) == 64
        finally:
            temp_path.unlink()
    
    def test_file_sha256_nonexistent_file(self):
        """Test SHA256 calculation for a non-existent file."""
        nonexistent_path = Path("/this/file/does/not/exist.txt")
        hash_value = file_sha256(nonexistent_path)
        assert hash_value is None
    
    def test_file_sha256_custom_chunk_size(self):
        """Test SHA256 calculation with custom chunk size."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("hello world")
            temp_path = Path(f.name)
        
        try:
            # Test with very small chunk size
            hash_value = file_sha256(temp_path, chunk_size=4)
            expected = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
            assert hash_value == expected
        finally:
            temp_path.unlink()
    
    def test_file_sha256_directory(self):
        """Test SHA256 calculation for a directory (should return None)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            dir_path = Path(temp_dir)
            hash_value = file_sha256(dir_path)
            assert hash_value is None
