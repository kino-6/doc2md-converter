"""
Unit tests for image base64 embedding feature.

Tests the ability to embed images as base64 data URLs instead of extracting to files.
"""

import base64
import pytest
from io import BytesIO
from PIL import Image

from src.internal_representation import ImageReference, InternalDocument, Section
from src.markdown_serializer import MarkdownSerializer


class TestImageBase64Embedding:
    """Test suite for base64 image embedding functionality."""
    
    def test_serialize_image_with_base64_data(self):
        """Test that images with base64 data are serialized as data URLs."""
        # Create a simple test image
        img = Image.new('RGB', (10, 10), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Convert to base64
        base64_data = base64.b64encode(img_bytes.read()).decode('utf-8')
        
        # Create image reference with base64 data
        img_ref = ImageReference(
            source_path="test.png",
            alt_text="Test Image",
            base64_data=base64_data,
            mime_type="image/png"
        )
        
        # Serialize
        serializer = MarkdownSerializer()
        result = serializer.serialize_image(img_ref)
        
        # Verify data URL format
        assert result.startswith("![Test Image](data:image/png;base64,")
        assert base64_data in result
    
    def test_serialize_image_with_base64_and_ocr(self):
        """Test that images with base64 data and OCR text include both."""
        # Create base64 data
        img = Image.new('RGB', (10, 10), color='blue')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        base64_data = base64.b64encode(img_bytes.read()).decode('utf-8')
        
        # Create image reference with base64 and OCR
        img_ref = ImageReference(
            source_path="test.jpg",
            alt_text="Chart",
            base64_data=base64_data,
            mime_type="image/jpeg",
            ocr_text="Sales Data 2024"
        )
        
        # Serialize
        serializer = MarkdownSerializer()
        result = serializer.serialize_image(img_ref)
        
        # Verify both data URL and OCR text
        assert "data:image/jpeg;base64," in result
        assert "OCR extracted text: Sales Data 2024" in result
    
    def test_serialize_image_prefers_base64_over_path(self):
        """Test that base64 data takes precedence over file paths."""
        # Create base64 data
        img = Image.new('RGB', (5, 5), color='green')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        base64_data = base64.b64encode(img_bytes.read()).decode('utf-8')
        
        # Create image reference with both base64 and extracted path
        img_ref = ImageReference(
            source_path="original.png",
            extracted_path="output/images/image_001.png",
            alt_text="Logo",
            base64_data=base64_data,
            mime_type="image/png"
        )
        
        # Serialize
        serializer = MarkdownSerializer()
        result = serializer.serialize_image(img_ref)
        
        # Should use base64, not file path
        assert "data:image/png;base64," in result
        assert "output/images/image_001.png" not in result
    
    def test_serialize_image_without_base64_uses_path(self):
        """Test that images without base64 data use file paths."""
        # Create image reference without base64
        img_ref = ImageReference(
            source_path="original.png",
            extracted_path="output/images/image_001.png",
            alt_text="Diagram"
        )
        
        # Serialize
        serializer = MarkdownSerializer()
        result = serializer.serialize_image(img_ref)
        
        # Should use file path
        assert result == "![Diagram](output/images/image_001.png)"
        assert "data:" not in result
    
    def test_serialize_image_base64_with_default_mime_type(self):
        """Test that images with base64 but no mime_type default to image/png."""
        # Create base64 data
        img = Image.new('RGB', (8, 8), color='yellow')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        base64_data = base64.b64encode(img_bytes.read()).decode('utf-8')
        
        # Create image reference without mime_type
        img_ref = ImageReference(
            source_path="test.png",
            base64_data=base64_data
        )
        
        # Serialize
        serializer = MarkdownSerializer()
        result = serializer.serialize_image(img_ref)
        
        # Should default to image/png
        assert "data:image/png;base64," in result
    
    def test_serialize_document_with_base64_images(self):
        """Test serializing a complete document with base64 embedded images."""
        # Create base64 image data
        img = Image.new('RGB', (10, 10), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        base64_data = base64.b64encode(img_bytes.read()).decode('utf-8')
        
        # Create image reference
        img_ref = ImageReference(
            source_path="chart.png",
            alt_text="Sales Chart",
            base64_data=base64_data,
            mime_type="image/png"
        )
        
        # Create document with image
        doc = InternalDocument(
            sections=[
                Section(content=[img_ref])
            ],
            images=[img_ref]
        )
        
        # Serialize
        serializer = MarkdownSerializer()
        result = serializer.serialize(doc)
        
        # Verify image is embedded as base64
        assert "![Sales Chart](data:image/png;base64," in result
        assert base64_data in result
    
    def test_base64_embedding_with_empty_alt_text(self):
        """Test base64 embedding works with empty alt text."""
        # Create base64 data
        img = Image.new('RGB', (5, 5), color='white')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        base64_data = base64.b64encode(img_bytes.read()).decode('utf-8')
        
        # Create image reference without alt text
        img_ref = ImageReference(
            source_path="image.png",
            base64_data=base64_data,
            mime_type="image/png"
        )
        
        # Serialize
        serializer = MarkdownSerializer()
        result = serializer.serialize_image(img_ref)
        
        # Should have empty alt text
        assert result.startswith("![](data:image/png;base64,")
    
    def test_base64_embedding_with_special_characters_in_alt_text(self):
        """Test base64 embedding handles special characters in alt text."""
        # Create base64 data
        img = Image.new('RGB', (5, 5), color='black')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        base64_data = base64.b64encode(img_bytes.read()).decode('utf-8')
        
        # Create image reference with special characters
        img_ref = ImageReference(
            source_path="image.png",
            alt_text="Image [with] special *chars*",
            base64_data=base64_data,
            mime_type="image/png"
        )
        
        # Serialize
        serializer = MarkdownSerializer()
        result = serializer.serialize_image(img_ref)
        
        # Should escape special characters
        assert "data:image/png;base64," in result
        # The escaper should handle the special characters
        assert "![" in result and "](" in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
