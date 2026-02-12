"""
Tests for the ImageExtractor class.

This module contains unit tests for image extraction functionality.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from src.image_extractor import ImageExtractor
from src.internal_representation import ImageReference, InternalDocument, DocumentMetadata


class TestImageExtractor:
    """Test suite for ImageExtractor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create a temporary directory for test outputs
        self.temp_dir = tempfile.mkdtemp()
        self.extractor = ImageExtractor(output_dir=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_extract_images_creates_directory_structure(self):
        """Test that extract_images creates the correct directory structure."""
        # Create a document with image references
        img_ref = ImageReference(source_path="word/media/image1.png", alt_text="Test Image")
        doc = InternalDocument(images=[img_ref])
        
        # Extract images (without actual image data)
        source_file = "test_document.docx"
        extracted = self.extractor.extract_images(doc, source_file)
        
        # Verify directory was created
        expected_dir = Path(self.temp_dir) / "test_document" / "images"
        assert expected_dir.exists()
        assert expected_dir.is_dir()
    
    def test_extract_images_sequential_naming(self):
        """Test that images are named sequentially by default."""
        # Create document with multiple images
        img1 = ImageReference(source_path="image1.png", alt_text="Image 1")
        img2 = ImageReference(source_path="image2.png", alt_text="Image 2")
        img3 = ImageReference(source_path="image3.png", alt_text="Image 3")
        doc = InternalDocument(images=[img1, img2, img3])
        
        # Extract images
        source_file = "document.docx"
        extracted = self.extractor.extract_images(doc, source_file)
        
        # Verify sequential naming in extracted paths
        assert extracted[0].extracted_path == "document/images/image_001.png"
        assert extracted[1].extracted_path == "document/images/image_002.png"
        assert extracted[2].extracted_path == "document/images/image_003.png"
    
    def test_extract_images_with_actual_data(self):
        """Test extracting and saving actual image data."""
        # Create image reference
        img_ref = ImageReference(source_path="test.png", alt_text="Test")
        doc = InternalDocument(images=[img_ref])
        
        # Create fake image data
        fake_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
        image_data_list = [(img_ref, fake_image_data)]
        
        # Extract images with data
        source_file = "test.docx"
        extracted = self.extractor.extract_images(doc, source_file, image_data_list)
        
        # Verify file was created
        image_path = Path(self.temp_dir) / "test" / "images" / "image_001.png"
        assert image_path.exists()
        
        # Verify content
        with open(image_path, 'rb') as f:
            assert f.read() == fake_image_data
        
        # Verify extracted path is relative
        assert extracted[0].extracted_path == "test/images/image_001.png"
    
    def test_extract_images_preserve_filenames(self):
        """Test preserving original filenames when enabled."""
        extractor = ImageExtractor(output_dir=self.temp_dir, preserve_filenames=True)
        
        # Create images with specific filenames
        img1 = ImageReference(source_path="word/media/logo.png", alt_text="Logo")
        img2 = ImageReference(source_path="word/media/chart.jpg", alt_text="Chart")
        doc = InternalDocument(images=[img1, img2])
        
        # Extract images
        source_file = "report.docx"
        extracted = extractor.extract_images(doc, source_file)
        
        # Verify original filenames are preserved
        assert extracted[0].extracted_path == "report/images/logo.png"
        assert extracted[1].extracted_path == "report/images/chart.jpg"
    
    def test_extract_images_empty_document(self):
        """Test extracting images from document with no images."""
        doc = InternalDocument(images=[])
        
        source_file = "empty.docx"
        extracted = self.extractor.extract_images(doc, source_file)
        
        # Should return empty list
        assert extracted == []
    
    def test_save_image_creates_parent_directories(self):
        """Test that save_image creates parent directories if needed."""
        image_data = b'\x89PNG\r\n\x1a\n'
        output_path = Path(self.temp_dir) / "nested" / "dir" / "image.png"
        
        # Save image
        saved_path = self.extractor.save_image(image_data, str(output_path))
        
        # Verify file exists
        assert Path(saved_path).exists()
        assert Path(saved_path).parent.exists()
    
    def test_get_images_directory(self):
        """Test getting the images directory path for a source file."""
        source_file = "my_document.docx"
        images_dir = self.extractor.get_images_directory(source_file)
        
        expected = Path(self.temp_dir) / "my_document" / "images"
        assert images_dir == expected
    
    def test_extract_filename_with_extension(self):
        """Test extracting filename from path with extension."""
        filename = self.extractor._extract_filename("word/media/image.png", 1)
        assert filename == "image.png"
    
    def test_extract_filename_without_extension(self):
        """Test extracting filename from path without extension."""
        filename = self.extractor._extract_filename("word/media/image", 1)
        assert filename == "image.png"
    
    def test_extract_filename_fallback(self):
        """Test fallback filename generation."""
        filename = self.extractor._extract_filename("", 5)
        assert filename == "image_005.png"


class TestImageReferenceInMarkdown:
    """Test suite for image reference serialization in Markdown."""
    
    def test_serialize_image_with_extracted_path(self):
        """Test serializing image with extracted path (relative)."""
        from src.markdown_serializer import MarkdownSerializer
        
        serializer = MarkdownSerializer()
        img = ImageReference(
            source_path="word/media/image1.png",
            extracted_path="document/images/image_001.png",
            alt_text="Test Image"
        )
        
        result = serializer.serialize_image(img)
        assert result == "![Test Image](document/images/image_001.png)"
    
    def test_serialize_image_extraction_failed(self):
        """Test serializing image when extraction failed (placeholder)."""
        from src.markdown_serializer import MarkdownSerializer
        
        serializer = MarkdownSerializer()
        img = ImageReference(
            source_path=None,
            extracted_path=None,
            alt_text="Failed Image"
        )
        
        result = serializer.serialize_image(img)
        assert result == "<!-- Image extraction failed: Failed Image -->"
    
    def test_serialize_image_with_ocr_text(self):
        """Test serializing image with OCR text."""
        from src.markdown_serializer import MarkdownSerializer
        
        serializer = MarkdownSerializer()
        img = ImageReference(
            source_path="image.png",
            extracted_path="doc/images/image_001.png",
            alt_text="Chart",
            ocr_text="Sales: $1000"
        )
        
        result = serializer.serialize_image(img)
        assert "![Chart](doc/images/image_001.png)" in result
        assert "*OCR extracted text: Sales: $1000*" in result
    
    def test_serialize_image_fallback_to_source_path(self):
        """Test that serializer falls back to source_path if no extracted_path."""
        from src.markdown_serializer import MarkdownSerializer
        
        serializer = MarkdownSerializer()
        img = ImageReference(
            source_path="original/path/image.png",
            extracted_path=None,
            alt_text="Image"
        )
        
        result = serializer.serialize_image(img)
        assert result == "![Image](original/path/image.png)"
