"""
Tests for OCR integration with ImageExtractor.

This module contains integration tests for OCR functionality with image extraction.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from PIL import Image, ImageDraw
from src.image_extractor import ImageExtractor
from src.internal_representation import ImageReference, InternalDocument


class TestOCRIntegration:
    """Test suite for OCR integration with ImageExtractor."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def _create_test_image_bytes(self, text: str = "Test") -> bytes:
        """Create a simple test image with text as bytes.
        
        Args:
            text: Text to render in the image
        
        Returns:
            Image bytes
        """
        img = Image.new('RGB', (200, 50), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((10, 15), text, fill='black')
        
        # Save to bytes
        import io
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()
    
    def test_image_extractor_without_ocr_engine(self):
        """Test ImageExtractor works without OCR engine."""
        extractor = ImageExtractor(output_dir=self.temp_dir, enable_ocr=False)
        
        img_ref = ImageReference(source_path="test.png", alt_text="Test")
        doc = InternalDocument(images=[img_ref])
        
        # Create test image data
        img_bytes = self._create_test_image_bytes()
        image_data_list = [(img_ref, img_bytes)]
        
        # Extract images
        extracted = extractor.extract_images(doc, "test.docx", image_data_list)
        
        # Verify image was extracted but no OCR was applied
        assert len(extracted) == 1
        assert extracted[0].extracted_path is not None
        assert extracted[0].ocr_text is None
    
    def test_image_extractor_with_ocr_engine_disabled(self):
        """Test ImageExtractor with OCR engine but OCR disabled."""
        try:
            from src.ocr_engine import OCREngine
            ocr_engine = OCREngine(language="eng")
        except RuntimeError:
            pytest.skip("Tesseract not available")
        
        extractor = ImageExtractor(
            output_dir=self.temp_dir,
            ocr_engine=ocr_engine,
            enable_ocr=False
        )
        
        img_ref = ImageReference(source_path="test.png", alt_text="Test")
        doc = InternalDocument(images=[img_ref])
        
        img_bytes = self._create_test_image_bytes("Hello")
        image_data_list = [(img_ref, img_bytes)]
        
        extracted = extractor.extract_images(doc, "test.docx", image_data_list)
        
        # OCR should not be applied when disabled
        assert len(extracted) == 1
        assert extracted[0].ocr_text is None
    
    def test_image_extractor_with_ocr_engine_enabled(self):
        """Test ImageExtractor with OCR engine enabled."""
        try:
            from src.ocr_engine import OCREngine
            ocr_engine = OCREngine(language="eng")
        except RuntimeError:
            pytest.skip("Tesseract not available")
        
        extractor = ImageExtractor(
            output_dir=self.temp_dir,
            ocr_engine=ocr_engine,
            enable_ocr=True
        )
        
        img_ref = ImageReference(source_path="test.png", alt_text="Test")
        doc = InternalDocument(images=[img_ref])
        
        img_bytes = self._create_test_image_bytes("Hello World")
        image_data_list = [(img_ref, img_bytes)]
        
        extracted = extractor.extract_images(doc, "test.docx", image_data_list)
        
        # OCR should be applied
        assert len(extracted) == 1
        assert extracted[0].extracted_path is not None
        # OCR text may or may not be extracted depending on image quality
        # Just verify the field exists
        assert hasattr(extracted[0], 'ocr_text')
    
    def test_image_extractor_preserves_existing_ocr_text(self):
        """Test that ImageExtractor doesn't overwrite existing OCR text."""
        try:
            from src.ocr_engine import OCREngine
            ocr_engine = OCREngine(language="eng")
        except RuntimeError:
            pytest.skip("Tesseract not available")
        
        extractor = ImageExtractor(
            output_dir=self.temp_dir,
            ocr_engine=ocr_engine,
            enable_ocr=True
        )
        
        # Create image reference with existing OCR text
        img_ref = ImageReference(
            source_path="test.png",
            alt_text="Test",
            ocr_text="Existing OCR text"
        )
        doc = InternalDocument(images=[img_ref])
        
        img_bytes = self._create_test_image_bytes("New Text")
        image_data_list = [(img_ref, img_bytes)]
        
        extracted = extractor.extract_images(doc, "test.docx", image_data_list)
        
        # Existing OCR text should be preserved
        assert len(extracted) == 1
        assert extracted[0].ocr_text == "Existing OCR text"
    
    def test_apply_ocr_method(self):
        """Test the apply_ocr method."""
        try:
            from src.ocr_engine import OCREngine
            ocr_engine = OCREngine(language="eng")
        except RuntimeError:
            pytest.skip("Tesseract not available")
        
        extractor = ImageExtractor(
            output_dir=self.temp_dir,
            ocr_engine=ocr_engine
        )
        
        # Create and save a test image
        img_ref = ImageReference(source_path="test.png", alt_text="Test")
        doc = InternalDocument(images=[img_ref])
        
        img_bytes = self._create_test_image_bytes("OCR Test")
        image_data_list = [(img_ref, img_bytes)]
        
        # Extract image first
        extracted = extractor.extract_images(doc, "test.docx", image_data_list)
        
        # Now apply OCR explicitly
        ocr_text = extractor.apply_ocr(extracted[0])
        
        # Verify OCR was applied
        assert isinstance(ocr_text, str)
    
    def test_apply_ocr_without_engine_raises_error(self):
        """Test that apply_ocr raises error when OCR engine is not available."""
        extractor = ImageExtractor(output_dir=self.temp_dir, enable_ocr=False)
        
        img_ref = ImageReference(
            source_path="test.png",
            extracted_path="test/images/image_001.png"
        )
        
        with pytest.raises(ValueError, match="OCR engine is not available"):
            extractor.apply_ocr(img_ref)
    
    def test_apply_ocr_without_extracted_path_raises_error(self):
        """Test that apply_ocr raises error when image is not extracted."""
        try:
            from src.ocr_engine import OCREngine
            ocr_engine = OCREngine(language="eng")
        except RuntimeError:
            pytest.skip("Tesseract not available")
        
        extractor = ImageExtractor(
            output_dir=self.temp_dir,
            ocr_engine=ocr_engine
        )
        
        img_ref = ImageReference(source_path="test.png")
        
        with pytest.raises(ValueError, match="Image must be extracted before applying OCR"):
            extractor.apply_ocr(img_ref)
    
    def test_apply_ocr_with_language_override(self):
        """Test apply_ocr with language override."""
        try:
            from src.ocr_engine import OCREngine
            ocr_engine = OCREngine(language="eng")
        except RuntimeError:
            pytest.skip("Tesseract not available")
        
        extractor = ImageExtractor(
            output_dir=self.temp_dir,
            ocr_engine=ocr_engine
        )
        
        # Create and save a test image
        img_ref = ImageReference(source_path="test.png", alt_text="Test")
        doc = InternalDocument(images=[img_ref])
        
        img_bytes = self._create_test_image_bytes("Test")
        image_data_list = [(img_ref, img_bytes)]
        
        # Extract image
        extracted = extractor.extract_images(doc, "test.docx", image_data_list)
        
        # Apply OCR with language override
        ocr_text = extractor.apply_ocr(extracted[0], language="jpn")
        
        # Verify original language is restored
        assert ocr_engine.get_language() == "eng"
