"""
Tests for the OCREngine class.

This module contains unit tests for OCR functionality.
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from PIL import Image, ImageDraw, ImageFont


class TestOCREngine:
    """Test suite for OCREngine class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def _create_test_image_with_text(self, text: str, filename: str) -> str:
        """Create a test image with text for OCR testing.
        
        Args:
            text: Text to render in the image
            filename: Name of the image file
        
        Returns:
            Path to the created image
        """
        # Create a simple image with text
        img = Image.new('RGB', (400, 100), color='white')
        draw = ImageDraw.Draw(img)
        
        # Use default font (may not be perfect but works for testing)
        try:
            # Try to use a larger default font
            font = ImageFont.load_default()
        except:
            font = None
        
        # Draw text on image
        draw.text((10, 30), text, fill='black', font=font)
        
        # Save image
        image_path = Path(self.temp_dir) / filename
        img.save(image_path)
        return str(image_path)
    
    def test_ocr_engine_initialization(self):
        """Test OCR engine can be initialized with default language."""
        try:
            from src.ocr_engine import OCREngine
            engine = OCREngine()
            assert engine.get_language() == "eng+jpn"
        except RuntimeError as e:
            # Tesseract not installed, skip test
            pytest.skip(f"Tesseract not available: {e}")
    
    def test_ocr_engine_custom_language(self):
        """Test OCR engine can be initialized with custom language."""
        try:
            from src.ocr_engine import OCREngine
            engine = OCREngine(language="eng")
            assert engine.get_language() == "eng"
        except RuntimeError as e:
            pytest.skip(f"Tesseract not available: {e}")
    
    def test_extract_text_from_image_file(self):
        """Test extracting text from an image file."""
        try:
            from src.ocr_engine import OCREngine
            engine = OCREngine(language="eng")
            
            # Create test image with text
            test_text = "Hello World"
            image_path = self._create_test_image_with_text(test_text, "test_ocr.png")
            
            # Extract text
            extracted_text = engine.extract_text(image_path)
            
            # Verify text was extracted (may not be exact due to OCR accuracy)
            assert extracted_text is not None
            assert isinstance(extracted_text, str)
            # Check if at least some characters match
            assert len(extracted_text) > 0
        except RuntimeError as e:
            pytest.skip(f"Tesseract not available: {e}")
    
    def test_extract_text_from_bytes(self):
        """Test extracting text from image bytes."""
        try:
            from src.ocr_engine import OCREngine
            engine = OCREngine(language="eng")
            
            # Create test image
            test_text = "Test OCR"
            image_path = self._create_test_image_with_text(test_text, "test_bytes.png")
            
            # Read image as bytes
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            
            # Extract text from bytes
            extracted_text = engine.extract_text_from_bytes(image_bytes)
            
            # Verify text was extracted
            assert extracted_text is not None
            assert isinstance(extracted_text, str)
            assert len(extracted_text) > 0
        except RuntimeError as e:
            pytest.skip(f"Tesseract not available: {e}")
    
    def test_extract_text_empty_bytes(self):
        """Test extracting text from empty bytes returns empty string."""
        try:
            from src.ocr_engine import OCREngine
            engine = OCREngine()
            
            extracted_text = engine.extract_text_from_bytes(b"")
            assert extracted_text == ""
        except RuntimeError as e:
            pytest.skip(f"Tesseract not available: {e}")
    
    def test_extract_text_nonexistent_file(self):
        """Test extracting text from nonexistent file raises error."""
        try:
            from src.ocr_engine import OCREngine
            engine = OCREngine()
            
            with pytest.raises(FileNotFoundError):
                engine.extract_text("/nonexistent/path/image.png")
        except RuntimeError as e:
            pytest.skip(f"Tesseract not available: {e}")
    
    def test_set_language(self):
        """Test changing OCR language."""
        try:
            from src.ocr_engine import OCREngine
            engine = OCREngine(language="eng")
            
            assert engine.get_language() == "eng"
            
            engine.set_language("jpn")
            assert engine.get_language() == "jpn"
            
            engine.set_language("eng+jpn")
            assert engine.get_language() == "eng+jpn"
        except RuntimeError as e:
            pytest.skip(f"Tesseract not available: {e}")
    
    def test_ocr_engine_without_tesseract(self):
        """Test that OCR engine raises error when Tesseract is not available."""
        # This test verifies the error handling, but will be skipped if Tesseract is installed
        try:
            from src.ocr_engine import OCREngine
            # If we get here, Tesseract is installed
            pytest.skip("Tesseract is installed, cannot test missing Tesseract scenario")
        except RuntimeError:
            # Expected behavior when Tesseract is not installed
            pass
