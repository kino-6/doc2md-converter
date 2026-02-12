"""Encoding detection and handling module.

This module provides functionality to detect and handle character encodings
in source documents, ensuring proper text extraction and conversion.
"""

import logging
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class EncodingDetectionResult:
    """Result of encoding detection.
    
    Attributes:
        detected_encoding: The detected character encoding
        confidence: Confidence level of detection (0.0 to 1.0)
        has_issues: Whether encoding issues were detected
        issues: List of detected encoding issues
    """
    detected_encoding: str
    confidence: float
    has_issues: bool = False
    issues: list = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []


class EncodingDetector:
    """Detects and handles character encoding in documents.
    
    This class provides methods to:
    - Detect character encoding in text content
    - Identify encoding issues (mojibake, invalid characters)
    - Normalize text to UTF-8
    - Log encoding warnings
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize the encoding detector.
        
        Args:
            logger: Optional logger for recording encoding issues
        """
        self.logger = logger
    
    def detect_encoding(self, content: bytes) -> EncodingDetectionResult:
        """Detect the character encoding of byte content.
        
        Uses chardet library if available, otherwise falls back to
        common encoding detection heuristics.
        
        Args:
            content: Byte content to analyze
            
        Returns:
            EncodingDetectionResult with detected encoding and confidence
        """
        # Try using chardet if available
        try:
            import chardet
            result = chardet.detect(content)
            
            detected = result.get('encoding', 'utf-8')
            confidence = result.get('confidence', 0.0)
            
            if self.logger:
                self.logger.debug(
                    f"Detected encoding: {detected} (confidence: {confidence:.2f})"
                )
            
            return EncodingDetectionResult(
                detected_encoding=detected or 'utf-8',
                confidence=confidence
            )
        
        except ImportError:
            # chardet not available, use fallback detection
            if self.logger:
                self.logger.debug(
                    "chardet not available, using fallback encoding detection"
                )
            return self._detect_encoding_fallback(content)
    
    def _detect_encoding_fallback(self, content: bytes) -> EncodingDetectionResult:
        """Fallback encoding detection without chardet.
        
        Tries common encodings in order of likelihood.
        
        Args:
            content: Byte content to analyze
            
        Returns:
            EncodingDetectionResult with best guess encoding
        """
        # Try common encodings in order
        encodings_to_try = [
            ('utf-8', 1.0),
            ('utf-16', 0.8),
            ('latin-1', 0.6),
            ('cp1252', 0.5),  # Windows-1252
            ('shift_jis', 0.5),  # Japanese
            ('euc-jp', 0.5),  # Japanese
            ('gb2312', 0.5),  # Simplified Chinese
            ('big5', 0.5),  # Traditional Chinese
            ('euc-kr', 0.5),  # Korean
        ]
        
        for encoding, confidence in encodings_to_try:
            try:
                content.decode(encoding)
                if self.logger:
                    self.logger.debug(
                        f"Fallback detected encoding: {encoding} (confidence: {confidence:.2f})"
                    )
                return EncodingDetectionResult(
                    detected_encoding=encoding,
                    confidence=confidence
                )
            except (UnicodeDecodeError, LookupError):
                continue
        
        # If all fail, default to utf-8 with replacement
        if self.logger:
            self.logger.warning(
                "Could not detect encoding reliably, defaulting to utf-8"
            )
        
        return EncodingDetectionResult(
            detected_encoding='utf-8',
            confidence=0.3,
            has_issues=True,
            issues=['Could not reliably detect encoding']
        )
    
    def validate_text_encoding(self, text: str) -> EncodingDetectionResult:
        """Validate that text is properly encoded and detect issues.
        
        Checks for:
        - Invalid Unicode characters
        - Mojibake (garbled text from encoding mismatches)
        - Replacement characters (�)
        - Control characters
        
        Args:
            text: Text string to validate
            
        Returns:
            EncodingDetectionResult with validation results
        """
        issues = []
        
        # Check for replacement characters (indicates encoding problems)
        if '\ufffd' in text:
            replacement_count = text.count('\ufffd')
            issues.append(
                f"Found {replacement_count} replacement character(s) (�) - "
                "indicates encoding issues"
            )
            if self.logger:
                self.logger.warning(
                    f"Detected {replacement_count} replacement characters in text"
                )
        
        # Check for common mojibake patterns
        mojibake_patterns = [
            ('Ã', 'Possible UTF-8 text decoded as Latin-1'),
            ('â€', 'Possible UTF-8 quotes decoded incorrectly'),
            ('Â', 'Possible encoding mismatch'),
        ]
        
        for pattern, description in mojibake_patterns:
            if pattern in text:
                issues.append(description)
                if self.logger:
                    self.logger.warning(f"Possible mojibake detected: {description}")
        
        # Check for excessive control characters (excluding common ones)
        control_chars = sum(
            1 for char in text 
            if ord(char) < 32 and char not in '\n\r\t'
        )
        
        if control_chars > len(text) * 0.01:  # More than 1% control chars
            issues.append(
                f"High number of control characters ({control_chars}) detected"
            )
            if self.logger:
                self.logger.warning(
                    f"Detected {control_chars} control characters in text"
                )
        
        # Check for null bytes
        if '\x00' in text:
            null_count = text.count('\x00')
            issues.append(f"Found {null_count} null byte(s) in text")
            if self.logger:
                self.logger.warning(f"Detected {null_count} null bytes in text")
        
        has_issues = len(issues) > 0
        
        return EncodingDetectionResult(
            detected_encoding='utf-8',  # Assuming input is already decoded
            confidence=1.0 if not has_issues else 0.7,
            has_issues=has_issues,
            issues=issues
        )
    
    def normalize_text(self, text: str) -> str:
        """Normalize text to ensure proper UTF-8 encoding.
        
        Performs:
        - Unicode normalization (NFC form)
        - Removal of null bytes
        - Replacement of invalid characters
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text string
        """
        import unicodedata
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Normalize Unicode to NFC form (canonical composition)
        # This ensures consistent representation of characters
        text = unicodedata.normalize('NFC', text)
        
        # Remove other problematic control characters (keep newlines, tabs, carriage returns)
        cleaned_chars = []
        for char in text:
            code = ord(char)
            # Keep printable characters and common whitespace
            if code >= 32 or char in '\n\r\t':
                cleaned_chars.append(char)
            elif self.logger:
                self.logger.debug(f"Removed control character: U+{code:04X}")
        
        return ''.join(cleaned_chars)
    
    def decode_with_fallback(
        self, 
        content: bytes, 
        encoding: Optional[str] = None
    ) -> Tuple[str, EncodingDetectionResult]:
        """Decode byte content to string with automatic encoding detection.
        
        If encoding is not specified, attempts to detect it automatically.
        Falls back to UTF-8 with error replacement if decoding fails.
        
        Args:
            content: Byte content to decode
            encoding: Optional encoding to use (if None, will auto-detect)
            
        Returns:
            Tuple of (decoded text, EncodingDetectionResult)
        """
        detection_result = None
        
        # Auto-detect encoding if not specified
        if encoding is None:
            detection_result = self.detect_encoding(content)
            encoding = detection_result.detected_encoding
        
        # Try to decode with detected/specified encoding
        try:
            text = content.decode(encoding)
            
            if detection_result is None:
                detection_result = EncodingDetectionResult(
                    detected_encoding=encoding,
                    confidence=1.0
                )
            
            # Validate the decoded text
            validation_result = self.validate_text_encoding(text)
            
            # Merge validation issues into detection result
            if validation_result.has_issues:
                detection_result.has_issues = True
                detection_result.issues.extend(validation_result.issues)
            
            # Normalize the text
            text = self.normalize_text(text)
            
            return text, detection_result
        
        except (UnicodeDecodeError, LookupError) as e:
            # Decoding failed, try UTF-8 with error replacement
            if self.logger:
                self.logger.warning(
                    f"Failed to decode with {encoding}, falling back to UTF-8 with replacement"
                )
            
            try:
                text = content.decode('utf-8', errors='replace')
                text = self.normalize_text(text)
                
                return text, EncodingDetectionResult(
                    detected_encoding='utf-8',
                    confidence=0.5,
                    has_issues=True,
                    issues=[f"Decoding failed with {encoding}: {str(e)}"]
                )
            except Exception as fallback_error:
                # Last resort: decode with latin-1 (never fails)
                if self.logger:
                    self.logger.error(
                        f"UTF-8 fallback failed, using latin-1: {str(fallback_error)}"
                    )
                
                text = content.decode('latin-1', errors='replace')
                text = self.normalize_text(text)
                
                return text, EncodingDetectionResult(
                    detected_encoding='latin-1',
                    confidence=0.3,
                    has_issues=True,
                    issues=[
                        f"Decoding failed with {encoding}",
                        f"UTF-8 fallback also failed: {str(fallback_error)}"
                    ]
                )
