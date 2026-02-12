"""Tests for encoding issue logging functionality.

This module tests that encoding issues are properly logged when detected
during document conversion, validating Requirement 9.5.
"""

import pytest
import logging
import io
from src.encoding_detector import EncodingDetector
from src.parsers import WordParser, ExcelParser, PDFParser
from docx import Document
import tempfile
from pathlib import Path


class TestEncodingLogging:
    """Test suite for encoding issue logging (Requirement 9.5)."""
    
    def test_encoding_detector_logs_replacement_characters(self):
        """Test that replacement characters trigger warning logs."""
        # Create a logger with string stream to capture output
        log_stream = io.StringIO()
        logger = logging.getLogger('test_replacement_chars')
        logger.setLevel(logging.WARNING)
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(handler)
        
        # Create detector with logger
        detector = EncodingDetector(logger=logger)
        
        # Validate text with replacement characters
        text = "This text has replacement chars: \ufffd\ufffd\ufffd"
        result = detector.validate_text_encoding(text)
        
        # Verify issues were detected
        assert result.has_issues
        assert len(result.issues) > 0
        
        # Verify warning was logged
        log_output = log_stream.getvalue()
        assert 'WARNING' in log_output
        assert 'replacement character' in log_output.lower()
        
        # Clean up
        logger.removeHandler(handler)
    
    def test_encoding_detector_logs_mojibake(self):
        """Test that mojibake patterns trigger warning logs."""
        # Create a logger with string stream
        log_stream = io.StringIO()
        logger = logging.getLogger('test_mojibake')
        logger.setLevel(logging.WARNING)
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(handler)
        
        # Create detector with logger
        detector = EncodingDetector(logger=logger)
        
        # Validate text with mojibake
        text = "This has mojibake: â€œquotesâ€ and Ã©"
        result = detector.validate_text_encoding(text)
        
        # Verify issues were detected
        assert result.has_issues
        
        # Verify warning was logged
        log_output = log_stream.getvalue()
        assert 'WARNING' in log_output
        assert 'mojibake' in log_output.lower() or 'encoding' in log_output.lower()
        
        # Clean up
        logger.removeHandler(handler)
    
    def test_encoding_detector_logs_null_bytes(self):
        """Test that null bytes trigger warning logs."""
        # Create a logger with string stream
        log_stream = io.StringIO()
        logger = logging.getLogger('test_null_bytes')
        logger.setLevel(logging.WARNING)
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(handler)
        
        # Create detector with logger
        detector = EncodingDetector(logger=logger)
        
        # Validate text with null bytes
        text = "Text with\x00null\x00bytes"
        result = detector.validate_text_encoding(text)
        
        # Verify issues were detected
        assert result.has_issues
        assert any('null byte' in issue.lower() for issue in result.issues)
        
        # Verify warning was logged
        log_output = log_stream.getvalue()
        assert 'WARNING' in log_output
        assert 'null byte' in log_output.lower()
        
        # Clean up
        logger.removeHandler(handler)
    
    def test_encoding_detector_logs_control_characters(self):
        """Test that excessive control characters trigger warning logs."""
        # Create a logger with string stream
        log_stream = io.StringIO()
        logger = logging.getLogger('test_control_chars')
        logger.setLevel(logging.WARNING)
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(handler)
        
        # Create detector with logger
        detector = EncodingDetector(logger=logger)
        
        # Create text with many control characters (>1% of text)
        text = "Text" + "\x01\x02\x03\x04\x05" * 10  # Many control chars
        result = detector.validate_text_encoding(text)
        
        # Verify issues were detected
        assert result.has_issues
        
        # Verify warning was logged
        log_output = log_stream.getvalue()
        assert 'WARNING' in log_output
        assert 'control character' in log_output.lower()
        
        # Clean up
        logger.removeHandler(handler)
    
    def test_encoding_detector_logs_decode_failure(self):
        """Test that decode failures trigger warning logs."""
        # Create a logger with string stream
        log_stream = io.StringIO()
        logger = logging.getLogger('test_decode_failure')
        logger.setLevel(logging.WARNING)
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(handler)
        
        # Create detector with logger
        detector = EncodingDetector(logger=logger)
        
        # Create content that will fail ASCII decoding
        content = "Café 世界".encode('utf-8')
        
        # Try to decode as ASCII (will fail and fall back)
        text, result = detector.decode_with_fallback(content, encoding='ascii')
        
        # Verify issues were detected
        assert result.has_issues
        
        # Verify warning was logged
        log_output = log_stream.getvalue()
        assert 'WARNING' in log_output
        assert 'failed' in log_output.lower() or 'fallback' in log_output.lower()
        
        # Clean up
        logger.removeHandler(handler)
    
    def test_word_parser_logs_encoding_issues(self, tmp_path):
        """Test that WordParser logs encoding issues during parsing."""
        # Create a logger with string stream
        log_stream = io.StringIO()
        logger = logging.getLogger('test_word_parser')
        logger.setLevel(logging.WARNING)
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(handler)
        
        # Create parser with logger
        parser = WordParser(logger=logger)
        
        # Test the _process_text_encoding method directly with problematic text
        text_with_issues = "Text with replacement: \ufffd"
        normalized = parser._process_text_encoding(text_with_issues)
        
        # Verify warning was logged
        log_output = log_stream.getvalue()
        assert 'WARNING' in log_output
        assert 'encoding issue' in log_output.lower()
        assert 'word document' in log_output.lower()
        
        # Clean up
        logger.removeHandler(handler)
    
    def test_excel_parser_logs_encoding_issues(self):
        """Test that ExcelParser logs encoding issues during parsing."""
        # Create a logger with string stream
        log_stream = io.StringIO()
        logger = logging.getLogger('test_excel_parser')
        logger.setLevel(logging.WARNING)
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(handler)
        
        # Create parser with logger
        parser = ExcelParser(logger=logger)
        
        # Test the _process_text_encoding method directly with problematic text
        text_with_issues = "Cell with replacement: \ufffd\ufffd"
        normalized = parser._process_text_encoding(text_with_issues)
        
        # Verify warning was logged
        log_output = log_stream.getvalue()
        assert 'WARNING' in log_output
        assert 'encoding issue' in log_output.lower()
        assert 'excel cell' in log_output.lower()
        
        # Clean up
        logger.removeHandler(handler)
    
    def test_pdf_parser_logs_encoding_issues(self):
        """Test that PDFParser logs encoding issues during parsing."""
        # Create a logger with string stream
        log_stream = io.StringIO()
        logger = logging.getLogger('test_pdf_parser')
        logger.setLevel(logging.WARNING)
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(handler)
        
        # Create parser with logger
        parser = PDFParser(logger=logger)
        
        # Test the _process_text_encoding method directly with problematic text
        text_with_issues = "PDF text with mojibake: â€œquotesâ€"
        normalized = parser._process_text_encoding(text_with_issues)
        
        # Verify warning was logged
        log_output = log_stream.getvalue()
        assert 'WARNING' in log_output
        assert 'encoding issue' in log_output.lower()
        assert 'pdf text' in log_output.lower()
        
        # Clean up
        logger.removeHandler(handler)
    
    def test_no_warnings_for_clean_text(self):
        """Test that clean text does not trigger warnings."""
        # Create a logger with string stream
        log_stream = io.StringIO()
        logger = logging.getLogger('test_clean_text')
        logger.setLevel(logging.WARNING)
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(handler)
        
        # Create detector with logger
        detector = EncodingDetector(logger=logger)
        
        # Validate clean text
        text = "This is perfectly clean text with no encoding issues."
        result = detector.validate_text_encoding(text)
        
        # Verify no issues detected
        assert not result.has_issues
        
        # Verify no warnings logged
        log_output = log_stream.getvalue()
        assert 'WARNING' not in log_output
        
        # Clean up
        logger.removeHandler(handler)
    
    def test_encoding_warning_includes_details(self):
        """Test that encoding warnings include detailed information."""
        # Create a logger with string stream
        log_stream = io.StringIO()
        logger = logging.getLogger('test_warning_details')
        logger.setLevel(logging.WARNING)
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(handler)
        
        # Create detector with logger
        detector = EncodingDetector(logger=logger)
        
        # Validate text with multiple issues
        text = "Text with \ufffd\ufffd\ufffd and \x00null\x00"
        result = detector.validate_text_encoding(text)
        
        # Verify multiple issues detected
        assert result.has_issues
        assert len(result.issues) >= 2  # Should have both replacement char and null byte issues
        
        # Verify warnings include details
        log_output = log_stream.getvalue()
        assert 'replacement character' in log_output.lower()
        assert 'null byte' in log_output.lower()
        
        # Verify counts are included
        assert '3' in log_output  # 3 replacement characters
        assert '2' in log_output  # 2 null bytes
        
        # Clean up
        logger.removeHandler(handler)
