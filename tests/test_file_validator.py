"""Tests for file validation functionality."""

import os
import tempfile
from pathlib import Path
import pytest
from hypothesis import given, strategies as st

from src.file_validator import (
    FileValidator,
    FileFormat,
    ErrorType,
    ValidationResult
)


class TestFileValidator:
    """Test suite for FileValidator class."""
    
    def test_check_file_exists_with_existing_file(self, tmp_path):
        """Test file existence check with an existing file."""
        # Create a temporary file
        test_file = tmp_path / "test.docx"
        test_file.write_text("test content")
        
        validator = FileValidator()
        assert validator.check_file_exists(str(test_file)) is True
    
    def test_check_file_exists_with_nonexistent_file(self):
        """Test file existence check with a non-existent file."""
        validator = FileValidator()
        assert validator.check_file_exists("/nonexistent/file.docx") is False
    
    def test_check_file_format_docx(self, tmp_path):
        """Test format detection for .docx files."""
        test_file = tmp_path / "test.docx"
        test_file.write_text("test")
        
        validator = FileValidator()
        assert validator.check_file_format(str(test_file)) == FileFormat.DOCX
    
    def test_check_file_format_xlsx(self, tmp_path):
        """Test format detection for .xlsx files."""
        test_file = tmp_path / "test.xlsx"
        test_file.write_text("test")
        
        validator = FileValidator()
        assert validator.check_file_format(str(test_file)) == FileFormat.XLSX
    
    def test_check_file_format_pdf(self, tmp_path):
        """Test format detection for .pdf files."""
        test_file = tmp_path / "test.pdf"
        test_file.write_text("test")
        
        validator = FileValidator()
        assert validator.check_file_format(str(test_file)) == FileFormat.PDF
    
    def test_check_file_format_unknown(self, tmp_path):
        """Test format detection for unsupported file types."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        validator = FileValidator()
        assert validator.check_file_format(str(test_file)) == FileFormat.UNKNOWN
    
    def test_check_file_format_case_insensitive(self, tmp_path):
        """Test that format detection is case-insensitive."""
        test_file = tmp_path / "test.DOCX"
        test_file.write_text("test")
        
        validator = FileValidator()
        assert validator.check_file_format(str(test_file)) == FileFormat.DOCX
    
    def test_check_file_size_within_limit(self, tmp_path):
        """Test file size check when file is within limit."""
        test_file = tmp_path / "test.docx"
        test_file.write_bytes(b"x" * 1000)  # 1KB file
        
        validator = FileValidator(max_size_mb=1)
        assert validator.check_file_size(str(test_file), 1024 * 1024) is True
    
    def test_check_file_size_exceeds_limit(self, tmp_path):
        """Test file size check when file exceeds limit."""
        test_file = tmp_path / "test.docx"
        test_file.write_bytes(b"x" * 2000)  # 2KB file
        
        validator = FileValidator()
        assert validator.check_file_size(str(test_file), 1000) is False
    
    def test_check_file_readable_with_readable_file(self, tmp_path):
        """Test readability check with a readable file."""
        test_file = tmp_path / "test.docx"
        test_file.write_text("test")
        
        validator = FileValidator()
        assert validator.check_file_readable(str(test_file)) is True
    
    def test_validate_file_success(self, tmp_path):
        """Test complete validation with a valid file."""
        test_file = tmp_path / "test.docx"
        test_file.write_text("test content")
        
        validator = FileValidator()
        result = validator.validate_file(str(test_file))
        
        assert result.valid is True
        assert result.file_format == FileFormat.DOCX
        assert result.error_type is None
        assert result.error_message is None
    
    def test_validate_file_not_found(self):
        """Test validation with non-existent file."""
        validator = FileValidator()
        result = validator.validate_file("/nonexistent/file.docx")
        
        assert result.valid is False
        assert result.error_type == ErrorType.FILE_NOT_FOUND
        assert "not found" in result.error_message.lower()
    
    def test_validate_file_invalid_format(self, tmp_path):
        """Test validation with invalid file format."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        validator = FileValidator()
        result = validator.validate_file(str(test_file))
        
        assert result.valid is False
        assert result.file_format == FileFormat.UNKNOWN
        assert result.error_type == ErrorType.INVALID_FORMAT
        assert "invalid file format" in result.error_message.lower()
    
    def test_validate_file_too_large(self, tmp_path):
        """Test validation with file exceeding size limit."""
        test_file = tmp_path / "test.docx"
        # Create a file larger than 1MB
        test_file.write_bytes(b"x" * (2 * 1024 * 1024))
        
        validator = FileValidator(max_size_mb=1)
        result = validator.validate_file(str(test_file))
        
        assert result.valid is False
        assert result.file_format == FileFormat.DOCX
        assert result.error_type == ErrorType.FILE_TOO_LARGE
        assert "exceeds maximum" in result.error_message.lower()
    
    def test_validator_custom_max_size(self, tmp_path):
        """Test FileValidator with custom maximum size."""
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"x" * (50 * 1024 * 1024))  # 50MB
        
        # Should fail with 10MB limit
        validator_small = FileValidator(max_size_mb=10)
        result_small = validator_small.validate_file(str(test_file))
        assert result_small.valid is False
        assert result_small.error_type == ErrorType.FILE_TOO_LARGE
        
        # Should pass with 100MB limit
        validator_large = FileValidator(max_size_mb=100)
        result_large = validator_large.validate_file(str(test_file))
        assert result_large.valid is True


# Property-Based Tests

@given(st.text(min_size=1, max_size=20, alphabet=st.characters(min_codepoint=33, max_codepoint=126)).filter(
    lambda x: not x.endswith(('.docx', '.xlsx', '.pdf', '.DOCX', '.XLSX', '.PDF')) and '/' not in x
))
def test_property_18_invalid_format_error_handling(invalid_extension):
    """Feature: document-to-markdown-converter, Property 18: Invalid format error handling
    
    For any file with an invalid format (not .docx, .xlsx, or .pdf), 
    the converter should return a descriptive error message indicating the expected formats.
    
    Validates: Requirements 4.1
    """
    import tempfile
    
    # Create a temporary file with invalid extension
    with tempfile.NamedTemporaryFile(mode='w', suffix=invalid_extension, delete=False) as f:
        f.write("test content")
        test_file = f.name
    
    try:
        validator = FileValidator()
        result = validator.validate_file(test_file)
        
        # Verify error handling
        assert result.valid is False, "File with invalid format should fail validation"
        assert result.error_type == ErrorType.INVALID_FORMAT, "Error type should be INVALID_FORMAT"
        assert result.error_message is not None, "Error message should be provided"
        assert "invalid" in result.error_message.lower() or "expected" in result.error_message.lower(), \
            "Error message should indicate invalid format or expected formats"
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.unlink(test_file)


@given(st.integers(min_value=1, max_value=10))
def test_property_19_corrupted_file_error_handling(size_mb):
    """Feature: document-to-markdown-converter, Property 19: Corrupted file error handling
    
    For any corrupted file that cannot be read, the converter should return 
    an error message indicating the file cannot be read.
    
    Validates: Requirements 4.2
    
    Note: This test simulates unreadable files by removing read permissions.
    Actual file corruption detection would require format-specific parsing.
    """
    import tempfile
    
    # Create a temporary file with valid extension
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.docx', delete=False) as f:
        f.write(b"x" * (size_mb * 1024 * 1024))
        test_file = f.name
    
    try:
        # Remove read permissions to simulate unreadable/corrupted file
        os.chmod(test_file, 0o000)
        
        validator = FileValidator()
        result = validator.validate_file(test_file)
        
        # Verify error handling
        assert result.valid is False, "Unreadable file should fail validation"
        assert result.error_type == ErrorType.FILE_NOT_READABLE, \
            "Error type should be FILE_NOT_READABLE for unreadable files"
        assert result.error_message is not None, "Error message should be provided"
        assert "not readable" in result.error_message.lower() or "permission" in result.error_message.lower(), \
            "Error message should indicate file cannot be read"
    finally:
        # Restore permissions and clean up
        if os.path.exists(test_file):
            os.chmod(test_file, 0o644)
            os.unlink(test_file)


@given(
    st.integers(min_value=1, max_value=200),  # file_size_mb
    st.integers(min_value=1, max_value=100)   # max_size_mb
)
def test_property_20_file_size_limit_enforcement(file_size_mb, max_size_mb):
    """Feature: document-to-markdown-converter, Property 20: File size limit enforcement
    
    For any file exceeding the configured size limit, the converter should return 
    an error message indicating the maximum supported file size.
    
    Validates: Requirements 4.4
    """
    import tempfile
    
    # Create a temporary file with specified size
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as f:
        f.write(b"x" * (file_size_mb * 1024 * 1024))
        test_file = f.name
    
    try:
        validator = FileValidator(max_size_mb=max_size_mb)
        result = validator.validate_file(test_file)
        
        # Verify size limit enforcement
        if file_size_mb > max_size_mb:
            assert result.valid is False, \
                f"File of {file_size_mb}MB should fail validation with {max_size_mb}MB limit"
            assert result.error_type == ErrorType.FILE_TOO_LARGE, \
                "Error type should be FILE_TOO_LARGE when size limit exceeded"
            assert result.error_message is not None, "Error message should be provided"
            assert "exceeds" in result.error_message.lower() or "maximum" in result.error_message.lower(), \
                "Error message should indicate size limit exceeded"
        else:
            # File within limit should pass (assuming it's readable)
            assert result.valid is True, \
                f"File of {file_size_mb}MB should pass validation with {max_size_mb}MB limit"
            assert result.error_type is None, "No error should be reported for valid file"
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.unlink(test_file)
