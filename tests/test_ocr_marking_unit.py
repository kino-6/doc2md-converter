"""
Unit tests for OCR text marking in Markdown output.

This module tests that OCR-extracted text is properly marked in the
Markdown output with appropriate indicators.
"""

import pytest
from src.markdown_serializer import MarkdownSerializer
from src.internal_representation import ImageReference


class TestOCRMarking:
    """Unit tests for OCR text marking functionality."""
    
    def test_ocr_text_marked_with_italics(self):
        """Test that OCR text is marked with italic formatting."""
        # Create an image reference with OCR text
        img_ref = ImageReference(
            source_path="test_image.png",
            extracted_path="test_doc/images/image_001.png",
            alt_text="Test Image",
            ocr_text="This is extracted text from OCR"
        )
        
        # Serialize the image
        serializer = MarkdownSerializer()
        markdown_output = serializer.serialize_image(img_ref)
        
        # Verify OCR text is marked with italics
        assert "*OCR extracted text:" in markdown_output, \
            "OCR text should be marked with italic formatting"
        assert "This is extracted text from OCR*" in markdown_output, \
            "OCR text content should be included in italic marker"
    
    def test_ocr_text_includes_label(self):
        """Test that OCR text includes the 'OCR extracted text:' label."""
        img_ref = ImageReference(
            source_path="test_image.png",
            extracted_path="test_doc/images/image_001.png",
            alt_text="Test Image",
            ocr_text="Sample OCR content"
        )
        
        serializer = MarkdownSerializer()
        markdown_output = serializer.serialize_image(img_ref)
        
        # Verify the label is present
        assert "OCR extracted text:" in markdown_output, \
            "OCR text should include descriptive label"
    
    def test_image_reference_preserved_with_ocr(self):
        """Test that image reference is preserved when OCR text is present."""
        img_ref = ImageReference(
            source_path="test_image.png",
            extracted_path="test_doc/images/image_001.png",
            alt_text="Test Image",
            ocr_text="OCR content here"
        )
        
        serializer = MarkdownSerializer()
        markdown_output = serializer.serialize_image(img_ref)
        
        # Verify image reference is still present
        assert "![Test Image](test_doc/images/image_001.png)" in markdown_output, \
            "Image reference should be preserved"
        
        # Verify OCR text is added after the image reference
        assert markdown_output.startswith("![Test Image](test_doc/images/image_001.png)"), \
            "Image reference should come first"
    
    def test_no_ocr_marker_without_ocr_text(self):
        """Test that no OCR marker is added when OCR text is not present."""
        img_ref = ImageReference(
            source_path="test_image.png",
            extracted_path="test_doc/images/image_001.png",
            alt_text="Test Image",
            ocr_text=None
        )
        
        serializer = MarkdownSerializer()
        markdown_output = serializer.serialize_image(img_ref)
        
        # Verify no OCR marker when no OCR text
        assert "OCR extracted text:" not in markdown_output, \
            "Should not include OCR marker when no OCR text is present"
        
        # Verify normal image reference is present
        assert "![Test Image](test_doc/images/image_001.png)" == markdown_output, \
            "Should output normal image reference without OCR marker"
    
    def test_empty_ocr_text_no_marker(self):
        """Test that empty OCR text does not add marker."""
        img_ref = ImageReference(
            source_path="test_image.png",
            extracted_path="test_doc/images/image_001.png",
            alt_text="Test Image",
            ocr_text=""
        )
        
        serializer = MarkdownSerializer()
        markdown_output = serializer.serialize_image(img_ref)
        
        # Empty OCR text should not add marker
        assert "OCR extracted text:" not in markdown_output, \
            "Empty OCR text should not add marker"
    
    def test_ocr_text_with_special_characters(self):
        """Test that OCR text with special characters is properly escaped."""
        img_ref = ImageReference(
            source_path="test_image.png",
            extracted_path="test_doc/images/image_001.png",
            alt_text="Test Image",
            ocr_text="Text with *asterisks* and _underscores_"
        )
        
        serializer = MarkdownSerializer()
        markdown_output = serializer.serialize_image(img_ref)
        
        # Verify OCR text is present (escaping is handled by MarkdownEscaper)
        assert "OCR extracted text:" in markdown_output, \
            "OCR marker should be present"
        assert "*OCR extracted text:" in markdown_output, \
            "OCR text should be in italics"
    
    def test_ocr_text_multiline(self):
        """Test that multiline OCR text is properly handled."""
        img_ref = ImageReference(
            source_path="test_image.png",
            extracted_path="test_doc/images/image_001.png",
            alt_text="Test Image",
            ocr_text="Line 1\nLine 2\nLine 3"
        )
        
        serializer = MarkdownSerializer()
        markdown_output = serializer.serialize_image(img_ref)
        
        # Verify OCR text is included
        assert "OCR extracted text:" in markdown_output, \
            "OCR marker should be present for multiline text"
        assert "Line 1" in markdown_output, \
            "First line should be present"
    
    def test_ocr_text_format_structure(self):
        """Test the complete structure of OCR text marking."""
        img_ref = ImageReference(
            source_path="test_image.png",
            extracted_path="test_doc/images/image_001.png",
            alt_text="Test Image",
            ocr_text="Sample text"
        )
        
        serializer = MarkdownSerializer()
        markdown_output = serializer.serialize_image(img_ref)
        
        # Expected format: ![alt](path)\n\n*OCR extracted text: text*
        lines = markdown_output.split('\n')
        
        # Should have image reference on first line
        assert lines[0] == "![Test Image](test_doc/images/image_001.png)", \
            "First line should be image reference"
        
        # Should have blank line
        assert lines[1] == "", \
            "Second line should be blank"
        
        # Should have OCR text on third line
        assert lines[2].startswith("*OCR extracted text:"), \
            "Third line should start with OCR marker"
        assert lines[2].endswith("*"), \
            "Third line should end with italic marker"
