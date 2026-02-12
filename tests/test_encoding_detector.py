"""Unit tests for encoding detection functionality."""

import pytest
from src.encoding_detector import EncodingDetector, EncodingDetectionResult


class TestEncodingDetector:
    """Test suite for EncodingDetector class."""
    
    def test_detect_encoding_utf8(self):
        """Test detection of UTF-8 encoded content."""
        detector = EncodingDetector()
        content = "Hello, 世界! こんにちは".encode('utf-8')
        
        result = detector.detect_encoding(content)
        
        assert result.detected_encoding in ['utf-8', 'UTF-8']
        assert result.confidence > 0.5
    
    def test_detect_encoding_latin1(self):
        """Test detection of Latin-1 encoded content."""
        detector = EncodingDetector()
        content = "Café résumé naïve".encode('latin-1')
        
        result = detector.detect_encoding(content)
        
        # Should detect some encoding (may be latin-1 or utf-8 depending on chardet)
        assert result.detected_encoding is not None
        assert result.confidence > 0.0
    
    def test_validate_text_encoding_clean(self):
        """Test validation of clean text without encoding issues."""
        detector = EncodingDetector()
        text = "This is clean text with no encoding issues."
        
        result = detector.validate_text_encoding(text)
        
        assert not result.has_issues
        assert len(result.issues) == 0
        assert result.confidence == 1.0
    
    def test_validate_text_encoding_replacement_chars(self):
        """Test detection of replacement characters."""
        detector = EncodingDetector()
        text = "This text has replacement chars: \ufffd\ufffd"
        
        result = detector.validate_text_encoding(text)
        
        assert result.has_issues
        assert any('replacement character' in issue.lower() for issue in result.issues)
        assert result.confidence < 1.0
    
    def test_validate_text_encoding_mojibake(self):
        """Test detection of mojibake patterns."""
        detector = EncodingDetector()
        # More obvious mojibake pattern
        text = "This has mojibake: â€œquotesâ€ and Ã©"
        
        result = detector.validate_text_encoding(text)
        
        # The text contains mojibake patterns that should be detected
        assert result.has_issues
        assert len(result.issues) > 0
    
    def test_validate_text_encoding_null_bytes(self):
        """Test detection of null bytes."""
        detector = EncodingDetector()
        text = "Text with\x00null\x00bytes"
        
        result = detector.validate_text_encoding(text)
        
        assert result.has_issues
        assert any('null byte' in issue.lower() for issue in result.issues)
    
    def test_normalize_text_removes_null_bytes(self):
        """Test that normalize_text removes null bytes."""
        detector = EncodingDetector()
        text = "Text\x00with\x00nulls"
        
        normalized = detector.normalize_text(text)
        
        assert '\x00' not in normalized
        assert normalized == "Textwithnulls"
    
    def test_normalize_text_removes_control_chars(self):
        """Test that normalize_text removes control characters."""
        detector = EncodingDetector()
        text = "Text\x01with\x02control\x03chars"
        
        normalized = detector.normalize_text(text)
        
        # Control chars should be removed, but regular text preserved
        assert '\x01' not in normalized
        assert '\x02' not in normalized
        assert '\x03' not in normalized
        assert 'Text' in normalized
        assert 'with' in normalized
    
    def test_normalize_text_preserves_whitespace(self):
        """Test that normalize_text preserves newlines, tabs, etc."""
        detector = EncodingDetector()
        text = "Line 1\nLine 2\tTabbed\rCarriage"
        
        normalized = detector.normalize_text(text)
        
        assert '\n' in normalized
        assert '\t' in normalized
        assert '\r' in normalized
    
    def test_normalize_text_unicode_normalization(self):
        """Test Unicode normalization (NFC form)."""
        detector = EncodingDetector()
        # Using combining characters that should be normalized
        text = "café"  # This might be composed or decomposed
        
        normalized = detector.normalize_text(text)
        
        # Should be in NFC form
        import unicodedata
        assert normalized == unicodedata.normalize('NFC', text)
    
    def test_decode_with_fallback_utf8(self):
        """Test decoding UTF-8 content."""
        detector = EncodingDetector()
        content = "Hello, 世界!".encode('utf-8')
        
        text, result = detector.decode_with_fallback(content)
        
        assert "Hello" in text
        assert "世界" in text
        assert result.detected_encoding in ['utf-8', 'UTF-8']
    
    def test_decode_with_fallback_specified_encoding(self):
        """Test decoding with specified encoding."""
        detector = EncodingDetector()
        content = "Café".encode('latin-1')
        
        text, result = detector.decode_with_fallback(content, encoding='latin-1')
        
        assert "Café" in text
        assert result.detected_encoding == 'latin-1'
    
    def test_decode_with_fallback_invalid_encoding(self):
        """Test fallback when decoding fails."""
        detector = EncodingDetector()
        # Create content that will fail to decode as ASCII
        content = "Café 世界".encode('utf-8')
        
        # Try to decode as ASCII (will fail)
        text, result = detector.decode_with_fallback(content, encoding='ascii')
        
        # Should fall back to UTF-8 or latin-1
        assert text is not None
        assert result.has_issues
        assert len(result.issues) > 0
    
    def test_encoding_detector_with_logger(self):
        """Test that encoding detector logs warnings when logger is provided."""
        import logging
        import io
        
        # Create a logger with string stream
        log_stream = io.StringIO()
        logger = logging.getLogger('test_encoding')
        logger.setLevel(logging.WARNING)
        handler = logging.StreamHandler(log_stream)
        logger.addHandler(handler)
        
        detector = EncodingDetector(logger=logger)
        
        # Validate text with issues
        text = "Text with replacement: \ufffd"
        result = detector.validate_text_encoding(text)
        
        # Check that warning was logged
        log_output = log_stream.getvalue()
        assert 'replacement character' in log_output.lower()
    
    def test_detect_encoding_fallback_without_chardet(self):
        """Test fallback encoding detection when chardet is not available."""
        detector = EncodingDetector()
        
        # Test with UTF-8 content
        content = "Hello, world!".encode('utf-8')
        result = detector._detect_encoding_fallback(content)
        
        assert result.detected_encoding is not None
        assert result.confidence > 0.0
    
    def test_validate_text_encoding_multilingual(self):
        """Test validation of multilingual text."""
        detector = EncodingDetector()
        text = "English, 日本語, 中文, Español, Français"
        
        result = detector.validate_text_encoding(text)
        
        # Multilingual text should be valid if properly encoded
        assert not result.has_issues or len(result.issues) == 0
    
    def test_normalize_text_empty_string(self):
        """Test normalization of empty string."""
        detector = EncodingDetector()
        text = ""
        
        normalized = detector.normalize_text(text)
        
        assert normalized == ""
    
    def test_decode_with_fallback_empty_content(self):
        """Test decoding empty content."""
        detector = EncodingDetector()
        content = b""
        
        text, result = detector.decode_with_fallback(content)
        
        assert text == ""
        assert result.detected_encoding is not None
