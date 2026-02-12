"""Property-based tests for encoding issue logging functionality.

This module contains property-based tests using Hypothesis to verify
that encoding issues are properly logged when detected during conversion.

Feature: document-to-markdown-converter
Property: 41
Validates: Requirements 9.5
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
import logging
import io
from src.encoding_detector import EncodingDetector, EncodingDetectionResult
from src.logger import Logger, LogLevel


# Strategy for generating text with encoding issues
def text_with_replacement_chars():
    """Generate text containing replacement characters."""
    return st.builds(
        lambda base, count: base + '\ufffd' * count,
        st.text(min_size=5, max_size=100),
        st.integers(min_value=1, max_value=10)
    )


def text_with_null_bytes():
    """Generate text containing null bytes."""
    return st.builds(
        lambda base, positions: ''.join(
            '\x00' if i in positions else c 
            for i, c in enumerate(base)
        ),
        st.text(min_size=10, max_size=100),
        st.lists(st.integers(min_value=0, max_value=99), min_size=1, max_size=5)
    )


def text_with_control_chars():
    """Generate text with excessive control characters."""
    return st.builds(
        lambda base, ctrl_chars: base + ''.join(chr(c) for c in ctrl_chars),
        st.text(min_size=10, max_size=50),
        st.lists(
            st.integers(min_value=1, max_value=31).filter(lambda x: x not in [9, 10, 13]),
            min_size=5,
            max_size=20
        )
    )


def text_with_mojibake():
    """Generate text with mojibake patterns."""
    mojibake_patterns = ['Ã©', 'Ã¨', 'â€œ', 'â€', 'Â', 'Ã']
    return st.builds(
        lambda base, pattern: base + pattern,
        st.text(min_size=5, max_size=100),
        st.sampled_from(mojibake_patterns)
    )


# Strategy for clean text (no encoding issues)
# Exclude characters that are commonly part of mojibake patterns
clean_text_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs', 'Po'),
        min_codepoint=32,
        max_codepoint=0x024F,
        blacklist_characters='ÂÃâ€'  # Exclude mojibake pattern characters
    ),
    min_size=10,
    max_size=200
)


class TestEncodingLoggingProperty:
    """Property 41: Encoding issue logging
    
    For any character encoding issue detected during conversion, the converter
    should log a warning with details.
    
    Validates: Requirements 9.5
    """
    
    @given(text=text_with_replacement_chars())
    @settings(max_examples=100, deadline=None)
    def test_property_41_log_replacement_characters(self, text):
        """
        Feature: document-to-markdown-converter
        Property 41: Encoding issue logging (replacement characters)
        
        For any text containing replacement characters, the detector should
        log a warning with details about the issue.
        
        **Validates: Requirements 9.5**
        """
        # Create a logger with string stream to capture logs
        log_stream = io.StringIO()
        logger = logging.getLogger(f'test_replacement_{id(text)}')
        logger.setLevel(logging.WARNING)
        logger.handlers.clear()  # Clear any existing handlers
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(handler)
        
        # Create detector with logger
        detector = EncodingDetector(logger=logger)
        
        # Validate text encoding
        result = detector.validate_text_encoding(text)
        
        # Property: Should detect issues
        assert result.has_issues is True, \
            "Should detect replacement characters as encoding issues"
        
        # Property: Issues list should contain information about replacement characters
        assert any('replacement' in issue.lower() for issue in result.issues), \
            "Issues should mention replacement characters"
        
        # Property: Warning should be logged
        log_output = log_stream.getvalue()
        assert 'WARNING' in log_output, \
            "Should log a WARNING for replacement characters"
        assert 'replacement' in log_output.lower(), \
            "Log should mention replacement characters"
        
        # Property: Log should include count of replacement characters
        replacement_count = text.count('\ufffd')
        assert str(replacement_count) in log_output, \
            f"Log should include count of replacement characters ({replacement_count})"
        
        # Clean up
        logger.removeHandler(handler)
    
    @given(text=text_with_null_bytes())
    @settings(max_examples=100, deadline=None)
    def test_property_41_log_null_bytes(self, text):
        """
        Feature: document-to-markdown-converter
        Property 41: Encoding issue logging (null bytes)
        
        For any text containing null bytes, the detector should log a warning
        with details about the issue.
        
        **Validates: Requirements 9.5**
        """
        # Skip if no null bytes were actually added
        if '\x00' not in text:
            return
        
        # Create a logger with string stream
        log_stream = io.StringIO()
        logger = logging.getLogger(f'test_null_{id(text)}')
        logger.setLevel(logging.WARNING)
        logger.handlers.clear()
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(handler)
        
        # Create detector with logger
        detector = EncodingDetector(logger=logger)
        
        # Validate text encoding
        result = detector.validate_text_encoding(text)
        
        # Property: Should detect issues
        assert result.has_issues is True, \
            "Should detect null bytes as encoding issues"
        
        # Property: Issues list should contain information about null bytes
        assert any('null byte' in issue.lower() for issue in result.issues), \
            "Issues should mention null bytes"
        
        # Property: Warning should be logged
        log_output = log_stream.getvalue()
        assert 'WARNING' in log_output, \
            "Should log a WARNING for null bytes"
        assert 'null byte' in log_output.lower(), \
            "Log should mention null bytes"
        
        # Property: Log should include count of null bytes
        null_count = text.count('\x00')
        assert str(null_count) in log_output, \
            f"Log should include count of null bytes ({null_count})"
        
        # Clean up
        logger.removeHandler(handler)
    
    @given(text=text_with_control_chars())
    @settings(max_examples=100, deadline=None)
    def test_property_41_log_control_characters(self, text):
        """
        Feature: document-to-markdown-converter
        Property 41: Encoding issue logging (control characters)
        
        For any text with excessive control characters, the detector should
        log a warning with details about the issue.
        
        **Validates: Requirements 9.5**
        """
        # Create a logger with string stream
        log_stream = io.StringIO()
        logger = logging.getLogger(f'test_control_{id(text)}')
        logger.setLevel(logging.WARNING)
        logger.handlers.clear()
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(handler)
        
        # Create detector with logger
        detector = EncodingDetector(logger=logger)
        
        # Validate text encoding
        result = detector.validate_text_encoding(text)
        
        # Count control characters (excluding \n, \r, \t)
        control_count = sum(
            1 for char in text 
            if ord(char) < 32 and char not in '\n\r\t'
        )
        
        # Property: If control characters exceed threshold, should detect issues
        if control_count > len(text) * 0.01:
            assert result.has_issues is True, \
                "Should detect excessive control characters as encoding issues"
            
            # Property: Issues list should contain information about control characters
            assert any('control character' in issue.lower() for issue in result.issues), \
                "Issues should mention control characters"
            
            # Property: Warning should be logged
            log_output = log_stream.getvalue()
            assert 'WARNING' in log_output, \
                "Should log a WARNING for excessive control characters"
            assert 'control character' in log_output.lower(), \
                "Log should mention control characters"
            
            # Property: Log should include count of control characters
            assert str(control_count) in log_output, \
                f"Log should include count of control characters ({control_count})"
        
        # Clean up
        logger.removeHandler(handler)
    
    @given(text=text_with_mojibake())
    @settings(max_examples=100, deadline=None)
    def test_property_41_log_mojibake_patterns(self, text):
        """
        Feature: document-to-markdown-converter
        Property 41: Encoding issue logging (mojibake)
        
        For any text containing mojibake patterns, the detector should log
        a warning with details about the issue.
        
        **Validates: Requirements 9.5**
        """
        # Create a logger with string stream
        log_stream = io.StringIO()
        logger = logging.getLogger(f'test_mojibake_{id(text)}')
        logger.setLevel(logging.WARNING)
        logger.handlers.clear()
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(handler)
        
        # Create detector with logger
        detector = EncodingDetector(logger=logger)
        
        # Validate text encoding
        result = detector.validate_text_encoding(text)
        
        # Property: Should detect issues
        assert result.has_issues is True, \
            "Should detect mojibake patterns as encoding issues"
        
        # Property: Issues list should contain information about encoding problems
        assert len(result.issues) > 0, \
            "Issues list should not be empty when mojibake is detected"
        
        # Property: Warning should be logged
        log_output = log_stream.getvalue()
        assert 'WARNING' in log_output, \
            "Should log a WARNING for mojibake patterns"
        assert 'mojibake' in log_output.lower() or 'encoding' in log_output.lower(), \
            "Log should mention mojibake or encoding issues"
        
        # Clean up
        logger.removeHandler(handler)
    
    @given(text=clean_text_strategy)
    @settings(max_examples=100, deadline=None)
    def test_property_41_no_warnings_for_clean_text(self, text):
        """
        Feature: document-to-markdown-converter
        Property 41: Encoding issue logging (clean text)
        
        For any clean text without encoding issues, the detector should not
        log warnings.
        
        **Validates: Requirements 9.5**
        """
        # Skip empty or whitespace-only text
        if not text.strip():
            return
        
        # Create a logger with string stream
        log_stream = io.StringIO()
        logger = logging.getLogger(f'test_clean_{id(text)}')
        logger.setLevel(logging.WARNING)
        logger.handlers.clear()
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(handler)
        
        # Create detector with logger
        detector = EncodingDetector(logger=logger)
        
        # Validate text encoding
        result = detector.validate_text_encoding(text)
        
        # Property: Should not detect issues for clean text
        assert result.has_issues is False, \
            "Should not detect issues in clean text"
        
        # Property: Issues list should be empty
        assert len(result.issues) == 0, \
            "Issues list should be empty for clean text"
        
        # Property: No warnings should be logged
        log_output = log_stream.getvalue()
        assert 'WARNING' not in log_output, \
            "Should not log warnings for clean text"
        
        # Clean up
        logger.removeHandler(handler)
    
    @given(
        content=st.binary(min_size=10, max_size=200),
        encoding=st.sampled_from(['utf-8', 'latin-1', 'cp1252'])
    )
    @settings(max_examples=100, deadline=None)
    def test_property_41_log_decode_failures(self, content, encoding):
        """
        Feature: document-to-markdown-converter
        Property 41: Encoding issue logging (decode failures)
        
        For any decode failure, the detector should log a warning with details
        about the failure and fallback encoding used.
        
        **Validates: Requirements 9.5**
        """
        # Create a logger with string stream
        log_stream = io.StringIO()
        logger = logging.getLogger(f'test_decode_{id(content)}')
        logger.setLevel(logging.WARNING)
        logger.handlers.clear()
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(handler)
        
        # Create detector with logger
        detector = EncodingDetector(logger=logger)
        
        # Try to decode with specified encoding (may fail for binary data)
        text, result = detector.decode_with_fallback(content, encoding=encoding)
        
        # Property: Should always return text (never fail)
        assert text is not None, \
            "decode_with_fallback should always return text"
        assert isinstance(text, str), \
            "Decoded content should be a string"
        
        # Property: Should return a result
        assert result is not None, \
            "decode_with_fallback should always return a result"
        assert isinstance(result, EncodingDetectionResult), \
            "Result should be an EncodingDetectionResult"
        
        # Property: If decoding had issues, should log warnings
        if result.has_issues:
            log_output = log_stream.getvalue()
            assert 'WARNING' in log_output or 'ERROR' in log_output, \
                "Should log warnings or errors when encoding issues are detected"
        
        # Clean up
        logger.removeHandler(handler)
    
    @given(
        text=st.one_of(
            text_with_replacement_chars(),
            text_with_null_bytes(),
            text_with_mojibake()
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_property_41_log_includes_details(self, text):
        """
        Feature: document-to-markdown-converter
        Property 41: Encoding issue logging (detailed information)
        
        For any encoding issue, the logged warning should include detailed
        information about the type and count of issues detected.
        
        **Validates: Requirements 9.5**
        """
        # Create a logger with string stream
        log_stream = io.StringIO()
        logger = logging.getLogger(f'test_details_{id(text)}')
        logger.setLevel(logging.WARNING)
        logger.handlers.clear()
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(handler)
        
        # Create detector with logger
        detector = EncodingDetector(logger=logger)
        
        # Validate text encoding
        result = detector.validate_text_encoding(text)
        
        # Property: If issues detected, log should contain details
        if result.has_issues:
            log_output = log_stream.getvalue()
            
            # Property: Log should not be empty
            assert len(log_output) > 0, \
                "Log output should not be empty when issues are detected"
            
            # Property: Log should contain WARNING level
            assert 'WARNING' in log_output, \
                "Log should contain WARNING level messages"
            
            # Property: Log should contain specific issue information
            # Check for at least one type of issue mentioned
            issue_keywords = ['replacement', 'null byte', 'control character', 'mojibake', 'encoding']
            assert any(keyword in log_output.lower() for keyword in issue_keywords), \
                "Log should mention specific type of encoding issue"
            
            # Property: If there are counts, they should be numeric
            import re
            numbers_in_log = re.findall(r'\d+', log_output)
            if numbers_in_log:
                # Verify that numbers are reasonable (not negative, not absurdly large)
                # Note: byte counts can be larger than character counts for multi-byte characters
                for num_str in numbers_in_log:
                    num = int(num_str)
                    # Allow for byte counts being up to 4x character count (UTF-8 max bytes per char)
                    max_reasonable = len(text) * 4
                    assert 0 <= num <= max_reasonable, \
                        f"Counts in log should be reasonable (0 to {max_reasonable}), got {num}"
        
        # Clean up
        logger.removeHandler(handler)
    
    @given(
        text=st.text(min_size=10, max_size=100)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_41_logging_is_consistent(self, text):
        """
        Feature: document-to-markdown-converter
        Property 41: Encoding issue logging (consistency)
        
        For the same text validated multiple times, the logging behavior
        should be consistent.
        
        **Validates: Requirements 9.5**
        """
        # Create a logger with string stream
        log_stream1 = io.StringIO()
        logger1 = logging.getLogger(f'test_consistent_1_{id(text)}')
        logger1.setLevel(logging.WARNING)
        logger1.handlers.clear()
        handler1 = logging.StreamHandler(log_stream1)
        handler1.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger1.addHandler(handler1)
        
        # Create detector with first logger
        detector1 = EncodingDetector(logger=logger1)
        result1 = detector1.validate_text_encoding(text)
        log_output1 = log_stream1.getvalue()
        
        # Create a second logger with string stream
        log_stream2 = io.StringIO()
        logger2 = logging.getLogger(f'test_consistent_2_{id(text)}')
        logger2.setLevel(logging.WARNING)
        logger2.handlers.clear()
        handler2 = logging.StreamHandler(log_stream2)
        handler2.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger2.addHandler(handler2)
        
        # Create detector with second logger
        detector2 = EncodingDetector(logger=logger2)
        result2 = detector2.validate_text_encoding(text)
        log_output2 = log_stream2.getvalue()
        
        # Property: Results should be identical
        assert result1.has_issues == result2.has_issues, \
            "Issue detection should be consistent"
        assert len(result1.issues) == len(result2.issues), \
            "Number of issues should be consistent"
        
        # Property: Logging behavior should be consistent
        has_warnings1 = 'WARNING' in log_output1
        has_warnings2 = 'WARNING' in log_output2
        assert has_warnings1 == has_warnings2, \
            "Logging behavior should be consistent across multiple validations"
        
        # Clean up
        logger1.removeHandler(handler1)
        logger2.removeHandler(handler2)
    
    @given(
        text=st.text(
            alphabet=st.characters(
                whitelist_categories=('Lu', 'Ll', 'Nd'),
                whitelist_characters='日本語テスト中文测试한국어café',
                min_codepoint=32,
                max_codepoint=0xFFFF,
                blacklist_characters='ÂÃâ€'  # Exclude mojibake pattern characters
            ).filter(lambda c: ord(c) < 0xD800 or ord(c) > 0xDFFF),
            min_size=10,
            max_size=100
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_property_41_multilingual_text_logging(self, text):
        """
        Feature: document-to-markdown-converter
        Property 41: Encoding issue logging (multilingual)
        
        For multilingual text, the detector should correctly identify encoding
        issues without false positives from valid Unicode characters.
        
        **Validates: Requirements 9.5**
        """
        # Skip empty text
        if not text.strip():
            return
        
        # Create a logger with string stream
        log_stream = io.StringIO()
        logger = logging.getLogger(f'test_multilingual_{id(text)}')
        logger.setLevel(logging.WARNING)
        logger.handlers.clear()
        handler = logging.StreamHandler(log_stream)
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logger.addHandler(handler)
        
        # Create detector with logger
        detector = EncodingDetector(logger=logger)
        
        # Validate text encoding
        result = detector.validate_text_encoding(text)
        
        # Property: Valid multilingual text should not trigger false positives
        # (unless it actually contains problematic characters)
        has_replacement_chars = '\ufffd' in text
        has_null_bytes = '\x00' in text
        has_mojibake = any(pattern in text for pattern in ['Ã©', 'â€œ', 'â€', 'Â'])
        
        if not (has_replacement_chars or has_null_bytes or has_mojibake):
            # Clean multilingual text should not have issues
            # (unless it has excessive control characters, which is rare)
            control_count = sum(
                1 for char in text 
                if ord(char) < 32 and char not in '\n\r\t'
            )
            
            if control_count <= len(text) * 0.01:
                assert result.has_issues is False, \
                    "Valid multilingual text should not trigger false positive encoding issues"
                
                log_output = log_stream.getvalue()
                assert 'WARNING' not in log_output, \
                    "Should not log warnings for valid multilingual text"
        
        # Clean up
        logger.removeHandler(handler)


# Run all property tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
