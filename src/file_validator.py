"""File validation module for the Document to Markdown Converter.

This module provides validation functionality for input files including
format checking, size validation, and readability verification.
"""

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class FileFormat(Enum):
    """Supported file formats."""
    DOCX = "docx"
    XLSX = "xlsx"
    PDF = "pdf"
    UNKNOWN = "unknown"


class ErrorType(Enum):
    """Error types for validation failures."""
    FILE_NOT_FOUND = "file_not_found"
    INVALID_FORMAT = "invalid_format"
    FILE_TOO_LARGE = "file_too_large"
    FILE_NOT_READABLE = "file_not_readable"
    FILE_CORRUPTED = "file_corrupted"


@dataclass
class ValidationResult:
    """Result of file validation.
    
    Attributes:
        valid: Whether the file passed validation
        file_format: Detected file format
        error_type: Type of error if validation failed
        error_message: Detailed error message if validation failed
    """
    valid: bool
    file_format: FileFormat = FileFormat.UNKNOWN
    error_type: Optional[ErrorType] = None
    error_message: Optional[str] = None


class FileValidator:
    """Validates input files for conversion.
    
    Performs checks including:
    - File existence
    - Format validation (docx, xlsx, pdf)
    - Size limits
    - Read permissions
    """
    
    # Default maximum file size: 100 MB
    DEFAULT_MAX_SIZE_MB = 100
    
    def __init__(self, max_size_mb: int = DEFAULT_MAX_SIZE_MB):
        """Initialize FileValidator with size limit.
        
        Args:
            max_size_mb: Maximum allowed file size in megabytes
        """
        self.max_size_bytes = max_size_mb * 1024 * 1024
    
    def validate_file(self, file_path: str) -> ValidationResult:
        """Perform complete validation on a file.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            ValidationResult with validation status and details
        """
        # Check file exists
        if not self.check_file_exists(file_path):
            return ValidationResult(
                valid=False,
                error_type=ErrorType.FILE_NOT_FOUND,
                error_message=f"File not found: {file_path}"
            )
        
        # Check file format
        file_format = self.check_file_format(file_path)
        if file_format == FileFormat.UNKNOWN:
            return ValidationResult(
                valid=False,
                file_format=file_format,
                error_type=ErrorType.INVALID_FORMAT,
                error_message=f"Invalid file format. Expected .docx, .xlsx, or .pdf, got: {Path(file_path).suffix}"
            )
        
        # Check file size
        if not self.check_file_size(file_path, self.max_size_bytes):
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            max_size_mb = self.max_size_bytes / (1024 * 1024)
            return ValidationResult(
                valid=False,
                file_format=file_format,
                error_type=ErrorType.FILE_TOO_LARGE,
                error_message=f"File size ({file_size_mb:.2f} MB) exceeds maximum allowed size ({max_size_mb:.0f} MB)"
            )
        
        # Check file readable
        if not self.check_file_readable(file_path):
            return ValidationResult(
                valid=False,
                file_format=file_format,
                error_type=ErrorType.FILE_NOT_READABLE,
                error_message=f"File is not readable. Check file permissions: {file_path}"
            )
        
        # All checks passed
        return ValidationResult(
            valid=True,
            file_format=file_format
        )
    
    def check_file_exists(self, file_path: str) -> bool:
        """Check if file exists.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file exists, False otherwise
        """
        return os.path.isfile(file_path)
    
    def check_file_format(self, file_path: str) -> FileFormat:
        """Check and return the file format based on extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            FileFormat enum value
        """
        suffix = Path(file_path).suffix.lower()
        
        format_map = {
            '.docx': FileFormat.DOCX,
            '.xlsx': FileFormat.XLSX,
            '.pdf': FileFormat.PDF
        }
        
        return format_map.get(suffix, FileFormat.UNKNOWN)
    
    def check_file_size(self, file_path: str, max_size: int) -> bool:
        """Check if file size is within limits.
        
        Args:
            file_path: Path to the file
            max_size: Maximum allowed size in bytes
            
        Returns:
            True if file size is within limit, False otherwise
        """
        try:
            file_size = os.path.getsize(file_path)
            return file_size <= max_size
        except OSError:
            return False
    
    def check_file_readable(self, file_path: str) -> bool:
        """Check if file is readable.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file is readable, False otherwise
        """
        return os.access(file_path, os.R_OK)
