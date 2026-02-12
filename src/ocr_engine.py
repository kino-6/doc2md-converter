"""
OCR Engine module for the Document to Markdown Converter.

This module provides the OCREngine class that handles text extraction from images
using Tesseract OCR with multi-language support.
"""

from pathlib import Path
from typing import Optional, Union
import io


class OCREngine:
    """Extracts text from images using Tesseract OCR.
    
    This class provides OCR capabilities with:
    - Multi-language support (default: eng+jpn)
    - Text extraction from file paths or image bytes
    - Configurable language settings
    
    Attributes:
        language: OCR language setting (e.g., 'eng', 'jpn', 'eng+jpn')
    """
    
    def __init__(self, language: str = "eng+jpn"):
        """Initialize the OCR engine.
        
        Args:
            language: Language(s) for OCR recognition. Can be a single language
                     (e.g., 'eng', 'jpn') or multiple languages separated by '+'
                     (e.g., 'eng+jpn'). Default is 'eng+jpn'.
        """
        self.language = language
        self._validate_tesseract()
    
    def _validate_tesseract(self) -> None:
        """Validate that Tesseract OCR is available.
        
        Raises:
            RuntimeError: If Tesseract is not installed or not accessible
        """
        try:
            import pytesseract
            # Try to get tesseract version to verify it's installed
            pytesseract.get_tesseract_version()
        except ImportError:
            raise RuntimeError(
                "pytesseract is not installed. Install it with: pip install pytesseract"
            )
        except Exception as e:
            raise RuntimeError(
                f"Tesseract OCR is not installed or not accessible. "
                f"Please install Tesseract OCR: {e}"
            )
    
    def extract_text(self, image_path: str) -> str:
        """Extract text from an image file.
        
        Args:
            image_path: Path to the image file
        
        Returns:
            Extracted text as a string. Returns empty string if no text is found
            or if extraction fails.
        
        Raises:
            FileNotFoundError: If the image file does not exist
            IOError: If the image cannot be read
        """
        import pytesseract
        from PIL import Image
        
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        try:
            # Open and process the image
            with Image.open(path) as img:
                # Extract text using pytesseract
                text = pytesseract.image_to_string(img, lang=self.language)
                return text.strip()
        except Exception as e:
            raise IOError(f"Failed to extract text from image {image_path}: {e}")
    
    def extract_text_from_bytes(self, image_bytes: bytes) -> str:
        """Extract text from image bytes.
        
        Args:
            image_bytes: Raw image data as bytes
        
        Returns:
            Extracted text as a string. Returns empty string if no text is found
            or if extraction fails.
        
        Raises:
            IOError: If the image bytes cannot be processed
        """
        import pytesseract
        from PIL import Image
        
        if not image_bytes:
            return ""
        
        try:
            # Create image from bytes
            image_stream = io.BytesIO(image_bytes)
            with Image.open(image_stream) as img:
                # Extract text using pytesseract
                text = pytesseract.image_to_string(img, lang=self.language)
                return text.strip()
        except Exception as e:
            raise IOError(f"Failed to extract text from image bytes: {e}")
    
    def set_language(self, language: str) -> None:
        """Set the OCR language.
        
        Args:
            language: Language(s) for OCR recognition. Can be a single language
                     (e.g., 'eng', 'jpn') or multiple languages separated by '+'
                     (e.g., 'eng+jpn').
        """
        self.language = language
    
    def get_language(self) -> str:
        """Get the current OCR language setting.
        
        Returns:
            Current language setting
        """
        return self.language
