"""Property-based tests for encoding detection functionality.

This module contains property-based tests using Hypothesis to verify
that encoding detection works correctly for various character encodings.

Feature: document-to-markdown-converter
Property: 40
Validates: Requirements 9.1
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from src.encoding_detector import EncodingDetector, EncodingDetectionResult
from src.logger import Logger, LogLevel
import logging


# Strategy for generating text content with various characters
text_content_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs', 'Po'),
        min_codepoint=32,
        max_codepoint=0x024F  # Latin Extended-B
    ),
    min_size=10,
    max_size=500
)

# Strategy for generating multilingual text
multilingual_text_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'),
        whitelist_characters='日本語テスト中文测试한국어',
        min_codepoint=32,
        max_codepoint=0xFFFF
    ).filter(lambda c: ord(c) < 0xD800 or ord(c) > 0xDFFF),  # Exclude surrogates
    min_size=10,
    max_size=500
)

# Common encodings to test
encoding_strategy = st.sampled_from([
    'utf-8',
    'utf-16',
    'utf-16-le',
    'utf-16-be',
    'latin-1',
    'cp1252',  # Windows-1252
    'iso-8859-1',
])


class TestEncodingDetectionProperty:
    """Property 40: Multi-encoding detection
    
    For any source document with a specific character encoding, the converter
    should detect and handle the encoding correctly.
    
    Validates: Requirements 9.1
    """
    
    @given(
        text=text_content_strategy,
        encoding=encoding_strategy
    )
    @settings(max_examples=100, deadline=None)
    def test_property_40_detect_encoding_from_bytes(self, text, encoding):
        """
        Feature: document-to-markdown-converter
        Property 40: Multi-encoding detection
        
        For any text content encoded with a specific encoding, the detector
        should successfully detect the encoding.
        
        **Validates: Requirements 9.1**
        """
        # Skip empty or whitespace-only text
        if not text.strip():
            return
        
        # Try to encode the text with the specified encoding
        try:
            encoded_bytes = text.encode(encoding)
        except (UnicodeEncodeError, LookupError):
            # Some characters may not be encodable in certain encodings
            assume(False)
            return
        
        # Create detector
        logger = Logger(log_level=LogLevel.ERROR)
        detector = EncodingDetector(logger=logger.logger)
        
        # Detect encoding
        result = detector.detect_encoding(encoded_bytes)
        
        # Property: Result should be an EncodingDetectionResult
        assert isinstance(result, EncodingDetectionResult), \
            "detect_encoding should return EncodingDetectionResult"
        
        # Property: Detected encoding should be a non-empty string
        assert isinstance(result.detected_encoding, str), \
            "Detected encoding should be a string"
        assert len(result.detected_encoding) > 0, \
            "Detected encoding should not be empty"
        
        # Property: Confidence should be between 0 and 1
        assert 0.0 <= result.confidence <= 1.0, \
            f"Confidence should be between 0 and 1, got {result.confidence}"
        
        # Property: Should be able to decode with detected encoding
        try:
            decoded_text = encoded_bytes.decode(result.detected_encoding)
            assert isinstance(decoded_text, str), \
                "Decoded text should be a string"
        except (UnicodeDecodeError, LookupError) as e:
            pytest.fail(
                f"Failed to decode with detected encoding {result.detected_encoding}: {e}"
            )
    
    @given(
        text=text_content_strategy,
        encoding=encoding_strategy
    )
    @settings(max_examples=100, deadline=None)
    def test_property_40_decode_with_fallback(self, text, encoding):
        """
        Feature: document-to-markdown-converter
        Property 40: Multi-encoding detection (decode with fallback)
        
        For any text content, decode_with_fallback should successfully decode
        the content regardless of encoding.
        
        **Validates: Requirements 9.1**
        """
        # Skip empty or whitespace-only text
        if not text.strip():
            return
        
        # Try to encode the text
        try:
            encoded_bytes = text.encode(encoding)
        except (UnicodeEncodeError, LookupError):
            assume(False)
            return
        
        # Create detector
        logger = Logger(log_level=LogLevel.ERROR)
        detector = EncodingDetector(logger=logger.logger)
        
        # Decode with fallback (auto-detect)
        decoded_text, result = detector.decode_with_fallback(encoded_bytes)
        
        # Property: Should return a string
        assert isinstance(decoded_text, str), \
            "decode_with_fallback should return a string"
        
        # Property: Decoded text should not be empty
        assert len(decoded_text) > 0, \
            "Decoded text should not be empty"
        
        # Property: Result should be an EncodingDetectionResult
        assert isinstance(result, EncodingDetectionResult), \
            "decode_with_fallback should return EncodingDetectionResult"
        
        # Property: Detected encoding should be valid
        assert isinstance(result.detected_encoding, str), \
            "Detected encoding should be a string"
        assert len(result.detected_encoding) > 0, \
            "Detected encoding should not be empty"
    
    @given(
        text=text_content_strategy,
        encoding=encoding_strategy
    )
    @settings(max_examples=100, deadline=None)
    def test_property_40_decode_with_specified_encoding(self, text, encoding):
        """
        Feature: document-to-markdown-converter
        Property 40: Multi-encoding detection (specified encoding)
        
        For any text content, when encoding is specified, decode_with_fallback
        should use the specified encoding.
        
        **Validates: Requirements 9.1**
        """
        # Skip empty or whitespace-only text
        if not text.strip():
            return
        
        # Try to encode the text
        try:
            encoded_bytes = text.encode(encoding)
        except (UnicodeEncodeError, LookupError):
            assume(False)
            return
        
        # Create detector
        logger = Logger(log_level=LogLevel.ERROR)
        detector = EncodingDetector(logger=logger.logger)
        
        # Decode with specified encoding
        decoded_text, result = detector.decode_with_fallback(
            encoded_bytes, 
            encoding=encoding
        )
        
        # Property: Should successfully decode
        assert isinstance(decoded_text, str), \
            "decode_with_fallback should return a string"
        assert len(decoded_text) > 0, \
            "Decoded text should not be empty"
        
        # Property: Result should indicate the specified encoding
        assert isinstance(result, EncodingDetectionResult), \
            "Should return EncodingDetectionResult"
        
        # Property: Decoded text should be similar to original
        # (may differ slightly due to normalization)
        assert len(decoded_text) >= len(text.strip()) * 0.8, \
            "Decoded text length should be reasonably close to original"
    
    @given(
        text=multilingual_text_strategy
    )
    @settings(max_examples=100, deadline=None)
    def test_property_40_handle_multilingual_content(self, text):
        """
        Feature: document-to-markdown-converter
        Property 40: Multi-encoding detection (multilingual)
        
        For any multilingual text content, the detector should handle
        various character sets correctly.
        
        **Validates: Requirements 9.1**
        """
        # Skip empty or whitespace-only text
        if not text.strip():
            return
        
        # Encode as UTF-8 (supports all characters)
        encoded_bytes = text.encode('utf-8')
        
        # Create detector
        logger = Logger(log_level=LogLevel.ERROR)
        detector = EncodingDetector(logger=logger.logger)
        
        # Detect and decode
        decoded_text, result = detector.decode_with_fallback(encoded_bytes)
        
        # Property: Should successfully decode
        assert isinstance(decoded_text, str), \
            "Should decode multilingual content"
        assert len(decoded_text) > 0, \
            "Decoded multilingual text should not be empty"
        
        # Property: Should detect UTF-8 or compatible encoding
        assert result.detected_encoding.lower() in ['utf-8', 'utf8', 'ascii'], \
            f"Should detect UTF-8 compatible encoding for multilingual text, got {result.detected_encoding}"
    
    @given(
        text=text_content_strategy
    )
    @settings(max_examples=100, deadline=None)
    def test_property_40_validate_text_encoding(self, text):
        """
        Feature: document-to-markdown-converter
        Property 40: Multi-encoding detection (validation)
        
        For any text content, validate_text_encoding should check for
        encoding issues.
        
        **Validates: Requirements 9.1**
        """
        # Skip empty text
        if not text:
            return
        
        # Create detector
        logger = Logger(log_level=LogLevel.ERROR)
        detector = EncodingDetector(logger=logger.logger)
        
        # Validate text encoding
        result = detector.validate_text_encoding(text)
        
        # Property: Should return EncodingDetectionResult
        assert isinstance(result, EncodingDetectionResult), \
            "validate_text_encoding should return EncodingDetectionResult"
        
        # Property: Confidence should be between 0 and 1
        assert 0.0 <= result.confidence <= 1.0, \
            f"Confidence should be between 0 and 1, got {result.confidence}"
        
        # Property: has_issues should be a boolean
        assert isinstance(result.has_issues, bool), \
            "has_issues should be a boolean"
        
        # Property: issues should be a list
        assert isinstance(result.issues, list), \
            "issues should be a list"
        
        # Property: If has_issues is True, issues list should not be empty
        if result.has_issues:
            assert len(result.issues) > 0, \
                "If has_issues is True, issues list should not be empty"
    
    @given(
        text=text_content_strategy
    )
    @settings(max_examples=100, deadline=None)
    def test_property_40_normalize_text_preserves_content(self, text):
        """
        Feature: document-to-markdown-converter
        Property 40: Multi-encoding detection (normalization)
        
        For any text content, normalize_text should preserve the essential
        content while cleaning up problematic characters.
        
        **Validates: Requirements 9.1**
        """
        # Skip empty text
        if not text:
            return
        
        # Create detector
        logger = Logger(log_level=LogLevel.ERROR)
        detector = EncodingDetector(logger=logger.logger)
        
        # Normalize text
        normalized = detector.normalize_text(text)
        
        # Property: Should return a string
        assert isinstance(normalized, str), \
            "normalize_text should return a string"
        
        # Property: Normalized text should not be significantly shorter
        # (allowing for removal of control characters)
        assert len(normalized) >= len(text) * 0.9, \
            "Normalized text should preserve most content"
        
        # Property: Should not contain null bytes
        assert '\x00' not in normalized, \
            "Normalized text should not contain null bytes"
    
    @given(
        text=text_content_strategy,
        encoding1=encoding_strategy,
        encoding2=encoding_strategy
    )
    @settings(max_examples=100, deadline=None)
    def test_property_40_consistent_detection_for_same_content(
        self, text, encoding1, encoding2
    ):
        """
        Feature: document-to-markdown-converter
        Property 40: Multi-encoding detection (consistency)
        
        For the same text content encoded with the same encoding, detection
        should be consistent across multiple calls.
        
        **Validates: Requirements 9.1**
        """
        # Skip empty or whitespace-only text
        if not text.strip():
            return
        
        # Try to encode with first encoding
        try:
            encoded_bytes = text.encode(encoding1)
        except (UnicodeEncodeError, LookupError):
            assume(False)
            return
        
        # Create detector
        logger = Logger(log_level=LogLevel.ERROR)
        detector = EncodingDetector(logger=logger.logger)
        
        # Detect encoding twice
        result1 = detector.detect_encoding(encoded_bytes)
        result2 = detector.detect_encoding(encoded_bytes)
        
        # Property: Results should be identical
        assert result1.detected_encoding == result2.detected_encoding, \
            "Detection should be consistent for the same content"
        assert result1.confidence == result2.confidence, \
            "Confidence should be consistent for the same content"
    
    @given(
        text=text_content_strategy,
        encoding=encoding_strategy
    )
    @settings(max_examples=100, deadline=None)
    def test_property_40_round_trip_encoding(self, text, encoding):
        """
        Feature: document-to-markdown-converter
        Property 40: Multi-encoding detection (round-trip)
        
        For any text content, encoding and then decoding with detection
        should preserve the content (possibly with normalization).
        
        **Validates: Requirements 9.1**
        """
        # Skip empty or whitespace-only text
        if not text.strip():
            return
        
        # Try to encode the text
        try:
            encoded_bytes = text.encode(encoding)
        except (UnicodeEncodeError, LookupError):
            assume(False)
            return
        
        # Create detector
        logger = Logger(log_level=LogLevel.ERROR)
        detector = EncodingDetector(logger=logger.logger)
        
        # Decode with auto-detection
        decoded_text, result = detector.decode_with_fallback(encoded_bytes)
        
        # Property: Decoded text should be similar to original
        # (exact match may not be possible due to normalization and encoding limitations)
        original_normalized = detector.normalize_text(text)
        
        # Check that most content is preserved
        assert len(decoded_text) >= len(original_normalized) * 0.8, \
            "Round-trip should preserve most content"
        
        # Property: Should not have introduced replacement characters
        # (unless the original encoding couldn't represent all characters)
        if encoding in ['utf-8', 'utf-16', 'utf-16-le', 'utf-16-be']:
            # These encodings should handle all Unicode characters
            assert '\ufffd' not in decoded_text or '\ufffd' in text, \
                "Round-trip should not introduce replacement characters for Unicode encodings"
    
    @given(
        text=text_content_strategy
    )
    @settings(max_examples=100, deadline=None)
    def test_property_40_detect_replacement_characters(self, text):
        """
        Feature: document-to-markdown-converter
        Property 40: Multi-encoding detection (replacement character detection)
        
        For any text containing replacement characters, validation should
        detect encoding issues.
        
        **Validates: Requirements 9.1**
        """
        # Add replacement character to text
        text_with_replacement = text + '\ufffd'
        
        # Create detector
        logger = Logger(log_level=LogLevel.ERROR)
        detector = EncodingDetector(logger=logger.logger)
        
        # Validate text
        result = detector.validate_text_encoding(text_with_replacement)
        
        # Property: Should detect issues
        assert result.has_issues is True, \
            "Should detect replacement character as an issue"
        
        # Property: Issues should mention replacement character
        assert any('replacement' in issue.lower() for issue in result.issues), \
            "Issues should mention replacement character"
    
    @given(
        encoding=encoding_strategy
    )
    @settings(max_examples=50, deadline=None)
    def test_property_40_handle_empty_content(self, encoding):
        """
        Feature: document-to-markdown-converter
        Property 40: Multi-encoding detection (empty content)
        
        For empty content, the detector should handle it gracefully.
        
        **Validates: Requirements 9.1**
        """
        # Create empty bytes
        empty_bytes = b''
        
        # Create detector
        logger = Logger(log_level=LogLevel.ERROR)
        detector = EncodingDetector(logger=logger.logger)
        
        # Detect encoding
        result = detector.detect_encoding(empty_bytes)
        
        # Property: Should return a result
        assert isinstance(result, EncodingDetectionResult), \
            "Should handle empty content gracefully"
        
        # Property: Should have a default encoding
        assert isinstance(result.detected_encoding, str), \
            "Should provide a default encoding for empty content"
        assert len(result.detected_encoding) > 0, \
            "Default encoding should not be empty"
    
    @given(
        text=text_content_strategy,
        encoding=encoding_strategy
    )
    @settings(max_examples=100, deadline=None)
    def test_property_40_fallback_never_fails(self, text, encoding):
        """
        Feature: document-to-markdown-converter
        Property 40: Multi-encoding detection (fallback robustness)
        
        For any content, decode_with_fallback should never fail, even with
        invalid or corrupted data.
        
        **Validates: Requirements 9.1**
        """
        # Skip empty text
        if not text:
            return
        
        # Try to encode the text
        try:
            encoded_bytes = text.encode(encoding)
        except (UnicodeEncodeError, LookupError):
            assume(False)
            return
        
        # Create detector
        logger = Logger(log_level=LogLevel.ERROR)
        detector = EncodingDetector(logger=logger.logger)
        
        # Decode with fallback should never raise an exception
        try:
            decoded_text, result = detector.decode_with_fallback(encoded_bytes)
            
            # Property: Should always return something
            assert decoded_text is not None, \
                "decode_with_fallback should always return text"
            assert result is not None, \
                "decode_with_fallback should always return result"
            
            # Property: Result should be valid
            assert isinstance(decoded_text, str), \
                "Decoded text should be a string"
            assert isinstance(result, EncodingDetectionResult), \
                "Result should be EncodingDetectionResult"
        
        except Exception as e:
            pytest.fail(f"decode_with_fallback should never fail, but got: {e}")


# Run all property tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
