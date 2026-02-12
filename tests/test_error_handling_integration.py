"""
Comprehensive integration tests for error handling.

This test suite validates all error categories and error message quality
across the entire conversion pipeline.

Tests cover:
- Invalid file format errors (Requirements 4.1)
- Corrupted file errors (Requirements 4.2)
- Empty file handling (Requirements 4.3)
- File size limit errors (Requirements 4.4)
- Graceful degradation with partial output (Requirements 4.5)

Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5
"""

import pytest
import os
import tempfile
from pathlib import Path

from src.conversion_orchestrator import ConversionOrchestrator
from src.config import ConversionConfig
from src.logger import Logger, LogLevel
from src.file_validator import ErrorType


class TestErrorHandlingIntegration:
    """Comprehensive integration tests for error handling."""
    
    # ========================================================================
    # Category 1: Invalid File Format Errors (Requirements 4.1)
    # ========================================================================
    
    def test_invalid_format_txt_file(self, tmp_path):
        """Test error handling for .txt file (invalid format).
        
        Validates: Requirements 4.1 - Invalid format error with descriptive message
        """
        # Create a .txt file
        txt_file = tmp_path / "document.txt"
        txt_file.write_text("This is a text file, not a supported format.")
        
        # Configure conversion
        config = ConversionConfig(
            input_path=str(txt_file),
            output_path=None
        )
        
        logger = Logger(log_level=LogLevel.ERROR)
        orchestrator = ConversionOrchestrator(config, logger)
        
        # Attempt conversion
        result = orchestrator.convert(str(txt_file))
        
        # Verify error handling
        assert result.success is False, "Conversion should fail for invalid format"
        assert len(result.errors) > 0, "Should have error messages"
        
        # Check error message quality
        error_msg = result.errors[0].lower()
        assert "invalid" in error_msg or "format" in error_msg, \
            "Error message should mention invalid format"
        assert any(fmt in error_msg for fmt in [".docx", ".xlsx", ".pdf", "docx", "xlsx", "pdf"]), \
            "Error message should indicate expected formats"
    
    def test_invalid_format_json_file(self, tmp_path):
        """Test error handling for .json file (invalid format).
        
        Validates: Requirements 4.1 - Invalid format error with descriptive message
        """
        # Create a .json file
        json_file = tmp_path / "data.json"
        json_file.write_text('{"key": "value"}')
        
        config = ConversionConfig(input_path=str(json_file), output_path=None)
        logger = Logger(log_level=LogLevel.ERROR)
        orchestrator = ConversionOrchestrator(config, logger)
        
        result = orchestrator.convert(str(json_file))
        
        assert result.success is False
        assert len(result.errors) > 0
        assert "invalid" in result.errors[0].lower() or "format" in result.errors[0].lower()
    
    def test_invalid_format_no_extension(self, tmp_path):
        """Test error handling for file without extension.
        
        Validates: Requirements 4.1 - Invalid format error for extensionless files
        """
        # Create a file without extension
        no_ext_file = tmp_path / "document"
        no_ext_file.write_text("Content without extension")
        
        config = ConversionConfig(input_path=str(no_ext_file), output_path=None)
        logger = Logger(log_level=LogLevel.ERROR)
        orchestrator = ConversionOrchestrator(config, logger)
        
        result = orchestrator.convert(str(no_ext_file))
        
        assert result.success is False
        assert len(result.errors) > 0
        error_msg = result.errors[0].lower()
        assert "invalid" in error_msg or "format" in error_msg
    
    # ========================================================================
    # Category 2: Corrupted File Errors (Requirements 4.2)
    # ========================================================================
    
    def test_corrupted_docx_file(self, tmp_path):
        """Test error handling for corrupted .docx file.
        
        Validates: Requirements 4.2 - Corrupted file error with descriptive message
        """
        # Create a fake .docx file with invalid content
        docx_file = tmp_path / "corrupted.docx"
        docx_file.write_bytes(b"This is not a valid DOCX file content")
        
        config = ConversionConfig(input_path=str(docx_file), output_path=None)
        logger = Logger(log_level=LogLevel.ERROR)
        orchestrator = ConversionOrchestrator(config, logger)
        
        result = orchestrator.convert(str(docx_file))
        
        # Should fail during parsing
        assert result.success is False, "Corrupted file should fail conversion"
        assert len(result.errors) > 0, "Should have error messages"
        
        # Error message should indicate parsing/reading failure
        error_msg = result.errors[0].lower()
        assert any(word in error_msg for word in ["parse", "read", "corrupt", "invalid", "failed"]), \
            "Error message should indicate file cannot be read/parsed"
    
    def test_corrupted_xlsx_file(self, tmp_path):
        """Test error handling for corrupted .xlsx file.
        
        Validates: Requirements 4.2 - Corrupted Excel file error
        """
        # Create a fake .xlsx file with invalid content
        xlsx_file = tmp_path / "corrupted.xlsx"
        xlsx_file.write_bytes(b"Not a valid Excel file")
        
        config = ConversionConfig(input_path=str(xlsx_file), output_path=None)
        logger = Logger(log_level=LogLevel.ERROR)
        orchestrator = ConversionOrchestrator(config, logger)
        
        result = orchestrator.convert(str(xlsx_file))
        
        assert result.success is False
        assert len(result.errors) > 0
        error_msg = result.errors[0].lower()
        assert any(word in error_msg for word in ["parse", "read", "corrupt", "invalid", "failed"])
    
    def test_corrupted_pdf_file(self, tmp_path):
        """Test error handling for corrupted .pdf file.
        
        Validates: Requirements 4.2 - Corrupted PDF file error
        """
        # Create a fake .pdf file with invalid content
        pdf_file = tmp_path / "corrupted.pdf"
        pdf_file.write_bytes(b"Not a valid PDF file")
        
        config = ConversionConfig(input_path=str(pdf_file), output_path=None)
        logger = Logger(log_level=LogLevel.ERROR)
        orchestrator = ConversionOrchestrator(config, logger)
        
        result = orchestrator.convert(str(pdf_file))
        
        assert result.success is False
        assert len(result.errors) > 0
        error_msg = result.errors[0].lower()
        assert any(word in error_msg for word in ["parse", "read", "corrupt", "invalid", "failed"])
    
    def test_unreadable_file_no_permissions(self, tmp_path):
        """Test error handling for file without read permissions.
        
        Validates: Requirements 4.2 - Unreadable file error
        """
        # Create a file and remove read permissions
        docx_file = tmp_path / "no_read.docx"
        docx_file.write_text("content")
        
        # Remove read permissions
        os.chmod(docx_file, 0o000)
        
        try:
            config = ConversionConfig(input_path=str(docx_file), output_path=None)
            logger = Logger(log_level=LogLevel.ERROR)
            orchestrator = ConversionOrchestrator(config, logger)
            
            result = orchestrator.convert(str(docx_file))
            
            # Should fail validation
            assert result.success is False
            assert len(result.errors) > 0
            error_msg = result.errors[0].lower()
            assert "readable" in error_msg or "permission" in error_msg
        finally:
            # Restore permissions for cleanup
            os.chmod(docx_file, 0o644)
    
    # ========================================================================
    # Category 3: Empty File Handling (Requirements 4.3)
    # ========================================================================
    
    def test_empty_docx_warning_message(self, tmp_path):
        """Test that empty Word documents produce appropriate warning.
        
        Validates: Requirements 4.3 - Empty file handling with warning
        """
        try:
            import docx
        except ImportError:
            pytest.skip("python-docx not installed")
        
        # Create empty Word document
        docx_file = tmp_path / "empty.docx"
        doc = docx.Document()
        doc.save(docx_file)
        
        config = ConversionConfig(input_path=str(docx_file), output_path=None)
        logger = Logger(log_level=LogLevel.INFO)
        orchestrator = ConversionOrchestrator(config, logger)
        
        result = orchestrator.convert(str(docx_file))
        
        # Should succeed but with minimal output
        assert result.success is True, "Empty file should succeed"
        assert result.markdown_content is not None
        
        # Should produce minimal output or have warnings
        content_length = len(result.markdown_content.strip())
        has_warnings = len(result.warnings) > 0
        
        assert content_length < 100 or has_warnings, \
            "Empty file should produce minimal output or warnings"
    
    def test_empty_xlsx_indication(self, tmp_path):
        """Test that empty Excel files indicate empty sheets.
        
        Validates: Requirements 4.3 - Empty Excel sheet indication
        """
        try:
            import openpyxl
        except ImportError:
            pytest.skip("openpyxl not installed")
        
        # Create empty Excel file
        xlsx_file = tmp_path / "empty.xlsx"
        workbook = openpyxl.Workbook()
        workbook.save(xlsx_file)
        
        config = ConversionConfig(input_path=str(xlsx_file), output_path=None)
        logger = Logger(log_level=LogLevel.INFO)
        orchestrator = ConversionOrchestrator(config, logger)
        
        result = orchestrator.convert(str(xlsx_file))
        
        assert result.success is True
        assert result.markdown_content is not None
        
        # Should indicate empty sheet
        assert "(Empty sheet)" in result.markdown_content or \
               len(result.markdown_content.strip()) < 100
    
    def test_zero_byte_file_error(self, tmp_path):
        """Test that zero-byte files produce appropriate error.
        
        Validates: Requirements 4.3 - Zero-byte file handling
        """
        # Create zero-byte file
        docx_file = tmp_path / "zero.docx"
        docx_file.touch()
        
        config = ConversionConfig(input_path=str(docx_file), output_path=None)
        logger = Logger(log_level=LogLevel.ERROR)
        orchestrator = ConversionOrchestrator(config, logger)
        
        result = orchestrator.convert(str(docx_file))
        
        # Zero-byte files should fail or warn
        assert result.success is False or len(result.warnings) > 0
        
        if not result.success:
            assert len(result.errors) > 0
            # Error message should be descriptive
            error_msg = result.errors[0].lower()
            assert any(word in error_msg for word in ["empty", "corrupt", "invalid", "parse", "read"])
    
    # ========================================================================
    # Category 4: File Size Limit Errors (Requirements 4.4)
    # ========================================================================
    
    def test_file_exceeds_size_limit(self, tmp_path):
        """Test error handling when file exceeds size limit.
        
        Validates: Requirements 4.4 - File size limit error with descriptive message
        """
        # Create a large file (2MB)
        large_file = tmp_path / "large.docx"
        large_file.write_bytes(b"x" * (2 * 1024 * 1024))
        
        # Set max size to 1MB
        config = ConversionConfig(
            input_path=str(large_file),
            output_path=None,
            max_file_size_mb=1
        )
        
        logger = Logger(log_level=LogLevel.ERROR)
        orchestrator = ConversionOrchestrator(config, logger)
        
        result = orchestrator.convert(str(large_file))
        
        # Should fail validation
        assert result.success is False, "Large file should fail validation"
        assert len(result.errors) > 0, "Should have error messages"
        
        # Check error message quality
        error_msg = result.errors[0].lower()
        assert "size" in error_msg or "exceeds" in error_msg or "maximum" in error_msg, \
            "Error message should mention size limit"
        assert "mb" in error_msg or "megabyte" in error_msg, \
            "Error message should indicate size unit"
    
    def test_file_size_limit_boundary(self, tmp_path):
        """Test file size limit at boundary condition.
        
        Validates: Requirements 4.4 - Exact size limit boundary
        """
        # Create a file exactly at 1MB
        boundary_file = tmp_path / "boundary.pdf"
        boundary_file.write_bytes(b"x" * (1024 * 1024))
        
        # Set max size to 1MB
        config = ConversionConfig(
            input_path=str(boundary_file),
            output_path=None,
            max_file_size_mb=1
        )
        
        logger = Logger(log_level=LogLevel.ERROR)
        orchestrator = ConversionOrchestrator(config, logger)
        
        result = orchestrator.convert(str(boundary_file))
        
        # File at exact limit should pass validation
        # (may fail parsing if content is invalid, but not size validation)
        if not result.success:
            # If it fails, it should not be due to size
            error_msg = result.errors[0].lower() if result.errors else ""
            assert "size" not in error_msg and "exceeds" not in error_msg, \
                "File at exact size limit should not fail size validation"
    
    def test_file_size_error_message_includes_actual_size(self, tmp_path):
        """Test that size error message includes actual file size.
        
        Validates: Requirements 4.4 - Error message quality with size details
        """
        # Create a 5MB file
        large_file = tmp_path / "5mb.xlsx"
        large_file.write_bytes(b"x" * (5 * 1024 * 1024))
        
        # Set max size to 2MB
        config = ConversionConfig(
            input_path=str(large_file),
            output_path=None,
            max_file_size_mb=2
        )
        
        logger = Logger(log_level=LogLevel.ERROR)
        orchestrator = ConversionOrchestrator(config, logger)
        
        result = orchestrator.convert(str(large_file))
        
        assert result.success is False
        assert len(result.errors) > 0
        
        error_msg = result.errors[0]
        # Should mention both actual size and limit
        assert "mb" in error_msg.lower()
        # Should contain numbers indicating sizes
        import re
        numbers = re.findall(r'\d+', error_msg)
        assert len(numbers) >= 1, "Error message should include size information"
    
    # ========================================================================
    # Category 5: Graceful Degradation (Requirements 4.5)
    # ========================================================================
    
    def test_graceful_degradation_with_partial_output(self, tmp_path):
        """Test that conversion errors provide partial output when possible.
        
        Validates: Requirements 4.5 - Graceful degradation with partial output
        """
        # Create a corrupted DOCX file
        docx_file = tmp_path / "partial.docx"
        docx_file.write_bytes(b"Invalid DOCX content")
        
        # Use preview mode to enable graceful degradation
        config = ConversionConfig(
            input_path=str(docx_file),
            output_path=None,
            preview_mode=True
        )
        
        logger = Logger(log_level=LogLevel.ERROR)
        orchestrator = ConversionOrchestrator(config, logger)
        
        result = orchestrator.convert(str(docx_file))
        
        # In preview/dry-run mode, should attempt graceful degradation
        if result.success:
            # If it succeeded with graceful degradation
            assert result.markdown_content is not None, \
                "Should provide partial output"
            assert len(result.warnings) > 0, \
                "Should have warnings about partial output"
        else:
            # If it failed completely, should have error details
            assert len(result.errors) > 0, \
                "Should provide error details"
    
    def test_error_details_in_result(self, tmp_path):
        """Test that conversion errors include detailed error information.
        
        Validates: Requirements 4.5 - Detailed error information
        """
        # Create invalid file
        invalid_file = tmp_path / "invalid.docx"
        invalid_file.write_bytes(b"Not valid")
        
        config = ConversionConfig(input_path=str(invalid_file), output_path=None)
        logger = Logger(log_level=LogLevel.ERROR)
        orchestrator = ConversionOrchestrator(config, logger)
        
        result = orchestrator.convert(str(invalid_file))
        
        # Should have detailed error information
        assert result.success is False
        assert len(result.errors) > 0, "Should have error messages"
        
        # Error message should be descriptive (not just "Error")
        error_msg = result.errors[0]
        assert len(error_msg) > 10, "Error message should be descriptive"
        assert error_msg != "Error", "Error message should be specific"
    
    # ========================================================================
    # Error Message Quality Tests
    # ========================================================================
    
    def test_error_message_clarity_file_not_found(self):
        """Test error message clarity for non-existent file.
        
        Validates: Error message quality
        """
        config = ConversionConfig(
            input_path="/nonexistent/file.docx",
            output_path=None
        )
        
        logger = Logger(log_level=LogLevel.ERROR)
        orchestrator = ConversionOrchestrator(config, logger)
        
        result = orchestrator.convert("/nonexistent/file.docx")
        
        assert result.success is False
        assert len(result.errors) > 0
        
        error_msg = result.errors[0].lower()
        assert "not found" in error_msg or "does not exist" in error_msg, \
            "Error message should clearly indicate file not found"
        assert "/nonexistent/file.docx" in result.errors[0], \
            "Error message should include the file path"
    
    def test_error_message_includes_file_path(self, tmp_path):
        """Test that error messages include the problematic file path.
        
        Validates: Error message quality - context information
        """
        # Create invalid format file
        txt_file = tmp_path / "document.txt"
        txt_file.write_text("content")
        
        config = ConversionConfig(input_path=str(txt_file), output_path=None)
        logger = Logger(log_level=LogLevel.ERROR)
        orchestrator = ConversionOrchestrator(config, logger)
        
        result = orchestrator.convert(str(txt_file))
        
        assert result.success is False
        assert len(result.errors) > 0
        
        # Error message should reference the file or its extension
        error_msg = result.errors[0]
        assert ".txt" in error_msg or str(txt_file) in error_msg, \
            "Error message should include file information"
    
    def test_multiple_error_categories_in_batch(self, tmp_path):
        """Test handling of multiple error types in batch conversion.
        
        Validates: Error handling across multiple files with different error types
        """
        # Create files with different error conditions
        files = []
        
        # 1. Valid file (will fail parsing but pass validation)
        valid_file = tmp_path / "valid.docx"
        valid_file.write_bytes(b"x" * 100)
        files.append(str(valid_file))
        
        # 2. Invalid format
        txt_file = tmp_path / "invalid.txt"
        txt_file.write_text("text")
        files.append(str(txt_file))
        
        # 3. Non-existent file
        files.append(str(tmp_path / "nonexistent.docx"))
        
        # 4. Too large file
        large_file = tmp_path / "large.pdf"
        large_file.write_bytes(b"x" * (2 * 1024 * 1024))
        files.append(str(large_file))
        
        # Configure batch conversion with 1MB limit
        config = ConversionConfig(
            input_path=files[0],  # Required but will be overridden
            output_path=None,
            max_file_size_mb=1
        )
        
        logger = Logger(log_level=LogLevel.ERROR)
        orchestrator = ConversionOrchestrator(config, logger)
        
        # Convert each file
        results = []
        for file_path in files:
            result = orchestrator.convert(file_path)
            results.append(result)
        
        # Verify each error type is handled appropriately
        assert len(results) == 4
        
        # File 2: Invalid format
        assert results[1].success is False
        assert any("invalid" in e.lower() or "format" in e.lower() 
                   for e in results[1].errors)
        
        # File 3: Not found
        assert results[2].success is False
        assert any("not found" in e.lower() for e in results[2].errors)
        
        # File 4: Too large
        assert results[3].success is False
        assert any("size" in e.lower() or "exceeds" in e.lower() 
                   for e in results[3].errors)
    
    def test_error_recovery_information(self, tmp_path):
        """Test that error messages include recovery suggestions when appropriate.
        
        Validates: Error message quality - actionable information
        """
        # Test invalid format error
        txt_file = tmp_path / "doc.txt"
        txt_file.write_text("content")
        
        config = ConversionConfig(input_path=str(txt_file), output_path=None)
        logger = Logger(log_level=LogLevel.ERROR)
        orchestrator = ConversionOrchestrator(config, logger)
        
        result = orchestrator.convert(str(txt_file))
        
        assert result.success is False
        error_msg = result.errors[0]
        
        # Should mention expected formats (actionable information)
        assert any(fmt in error_msg.lower() for fmt in ["docx", "xlsx", "pdf"]), \
            "Error message should suggest valid formats"
