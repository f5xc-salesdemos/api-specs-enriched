# Copyright (c) 2026 Robin Mordasiewicz. MIT License.

"""Security tests for ZIP extraction."""

import zipfile
from pathlib import Path

import pytest

from scripts.download import extract_zip, validate_zip_member_path, validate_zip_member_size


class TestPathTraversalProtection:
    """Test path traversal attack prevention."""

    def test_reject_absolute_paths(self):
        """Reject absolute paths."""
        assert not validate_zip_member_path("/etc/passwd")
        assert not validate_zip_member_path("/tmp/evil.json")

    def test_reject_parent_directory_traversal(self):
        """Reject ../ traversal attempts."""
        assert not validate_zip_member_path("../../../etc/passwd")
        assert not validate_zip_member_path("foo/../../evil.json")

    def test_accept_safe_paths(self):
        """Accept safe relative paths."""
        assert validate_zip_member_path("api.json")
        assert validate_zip_member_path("foo/bar/api.json")

    def test_malicious_zip_extraction_fails(self, tmp_path):
        """Test extraction of malicious ZIP fails safely."""
        # Create malicious ZIP with path traversal
        evil_zip = tmp_path / "evil.zip"
        with zipfile.ZipFile(evil_zip, "w") as zf:
            zf.writestr("../../../etc/passwd", "malicious content")

        output = tmp_path / "output"
        files = extract_zip(evil_zip, output)

        # Should extract nothing or skip the malicious entry
        assert len(files) == 0 or not (tmp_path / ".." / ".." / ".." / "etc" / "passwd").exists()


class TestZipBombProtection:
    """Test zip bomb attack prevention."""

    def test_reject_large_files(self):
        """Reject files exceeding size limit."""
        info = zipfile.ZipInfo("huge.json")
        info.file_size = 100 * 1024 * 1024  # 100 MB
        info.compress_size = 1024  # 1 KB compressed

        is_valid, msg = validate_zip_member_size(info)
        assert not is_valid
        assert "too large" in msg.lower()

    def test_reject_suspicious_compression(self):
        """Reject files with suspicious compression ratios."""
        info = zipfile.ZipInfo("bomb.json")
        info.file_size = 5 * 1024 * 1024  # 5 MB uncompressed (under 10 MB limit)
        info.compress_size = 10 * 1024  # 10 KB compressed (500:1 ratio - suspicious!)

        is_valid, msg = validate_zip_member_size(info)
        assert not is_valid
        assert "compression ratio" in msg.lower()

    def test_accept_normal_compression(self):
        """Accept files with normal compression."""
        info = zipfile.ZipInfo("normal.json")
        info.file_size = 100 * 1024  # 100 KB
        info.compress_size = 10 * 1024  # 10 KB (10:1 ratio)

        is_valid, msg = validate_zip_member_size(info)
        assert is_valid


class TestSafeExtractionIntegration:
    """Test complete extraction flow with security."""

    def test_safe_zip_extraction_succeeds(self, tmp_path):
        """Test normal ZIP extraction works with security checks."""
        # Create a safe ZIP file
        safe_zip = tmp_path / "safe.zip"
        with zipfile.ZipFile(safe_zip, "w") as zf:
            zf.writestr("api1.json", '{"test": "data1"}')
            zf.writestr("api2.json", '{"test": "data2"}')
            zf.writestr("subdir/api3.json", '{"test": "data3"}')  # Should flatten

        output = tmp_path / "output"
        files = extract_zip(safe_zip, output)

        # Should extract all 3 JSON files
        assert len(files) == 3
        assert "api1.json" in files
        assert "api2.json" in files
        assert "api3.json" in files  # Flattened from subdir

        # Verify files exist
        assert (output / "api1.json").exists()
        assert (output / "api2.json").exists()
        assert (output / "api3.json").exists()

    def test_mixed_safe_and_unsafe_extraction(self, tmp_path):
        """Test ZIP with both safe and unsafe paths - only safe extracted."""
        # Create ZIP with mix of safe and unsafe files
        mixed_zip = tmp_path / "mixed.zip"
        with zipfile.ZipFile(mixed_zip, "w") as zf:
            zf.writestr("api1.json", '{"test": "safe"}')
            zf.writestr("../evil.json", '{"test": "malicious"}')  # Should skip
            zf.writestr("api2.json", '{"test": "safe2"}')

        output = tmp_path / "output"
        files = extract_zip(mixed_zip, output)

        # Should only extract the 2 safe files
        assert len(files) == 2
        assert "api1.json" in files
        assert "api2.json" in files
        assert "evil.json" not in files

        # Verify only safe files exist
        assert (output / "api1.json").exists()
        assert (output / "api2.json").exists()
        assert not (tmp_path / ".." / "evil.json").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
