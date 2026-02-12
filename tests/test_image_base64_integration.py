"""
Integration tests for base64 image embedding feature.

Tests the complete flow from CLI option to serialized output.
"""

import tempfile
import base64
from pathlib import Path
from io import BytesIO
from PIL import Image
import pytest

from src.config import ConversionConfig
from src.internal_representation import ImageReference, InternalDocument, Section, Paragraph
from src.markdown_serializer import MarkdownSerializer


class TestImageBase64Integration:
    """Integration tests for base64 image embedding."""
    
    def test_config_embed_images_base64_option(self):
        """Test that ConversionConfig supports embed_images_base64 option."""
        config = ConversionConfig(
            input_path="test.docx",
            embed_images_base64=True
        )
        
        assert config.embed_images_base64 is True
    
    def test_config_default_embed_images_base64_is_false(self):
        """Test that embed_images_base64 defaults to False."""
        config = ConversionConfig(
            input_path="test.docx"
        )
        
        assert config.embed_images_base64 is False
    
    def test_config_file_with_embed_images_base64(self):
        """Test loading configuration file with embed_images_base64 option."""
        from src.config import ConfigManager
        import yaml
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                'embed_images_base64': True,
                'extract_images': False
            }
            yaml.dump(config_data, f)
            config_path = f.name
        
        try:
            manager = ConfigManager()
            config = manager.load_config(config_path)
            
            assert config.embed_images_base64 is True
            assert config.extract_images is False
        finally:
            Path(config_path).unlink()
    
    def test_serializer_respects_base64_data_in_images(self):
        """Test that serializer uses base64 data when available."""
        # Create test image
        img = Image.new('RGB', (20, 20), color='blue')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        base64_data = base64.b64encode(img_bytes.read()).decode('utf-8')
        
        # Create document with base64 image
        img_ref = ImageReference(
            source_path="test.png",
            alt_text="Test",
            base64_data=base64_data,
            mime_type="image/png"
        )
        
        doc = InternalDocument(
            sections=[
                Section(content=[
                    Paragraph(text="Here is an image:"),
                    img_ref
                ])
            ],
            images=[img_ref]
        )
        
        # Serialize
        serializer = MarkdownSerializer()
        markdown = serializer.serialize(doc)
        
        # Verify base64 embedding
        assert "data:image/png;base64," in markdown
        assert base64_data in markdown
        assert "test.png" not in markdown  # Should not use file path
    
    def test_multiple_images_with_base64(self):
        """Test document with multiple base64 embedded images."""
        # Create two different images
        img1 = Image.new('RGB', (10, 10), color='red')
        img1_bytes = BytesIO()
        img1.save(img1_bytes, format='PNG')
        img1_bytes.seek(0)
        base64_1 = base64.b64encode(img1_bytes.read()).decode('utf-8')
        
        img2 = Image.new('RGB', (10, 10), color='green')
        img2_bytes = BytesIO()
        img2.save(img2_bytes, format='JPEG')
        img2_bytes.seek(0)
        base64_2 = base64.b64encode(img2_bytes.read()).decode('utf-8')
        
        # Create image references
        img_ref1 = ImageReference(
            source_path="image1.png",
            alt_text="Red Image",
            base64_data=base64_1,
            mime_type="image/png"
        )
        
        img_ref2 = ImageReference(
            source_path="image2.jpg",
            alt_text="Green Image",
            base64_data=base64_2,
            mime_type="image/jpeg"
        )
        
        # Create document
        doc = InternalDocument(
            sections=[
                Section(content=[img_ref1, img_ref2])
            ],
            images=[img_ref1, img_ref2]
        )
        
        # Serialize
        serializer = MarkdownSerializer()
        markdown = serializer.serialize(doc)
        
        # Verify both images are embedded
        assert markdown.count("data:image/png;base64,") == 1
        assert markdown.count("data:image/jpeg;base64,") == 1
        assert base64_1 in markdown
        assert base64_2 in markdown
    
    def test_mixed_base64_and_file_path_images(self):
        """Test document with both base64 and file path images."""
        # Create base64 image
        img = Image.new('RGB', (10, 10), color='yellow')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        base64_data = base64.b64encode(img_bytes.read()).decode('utf-8')
        
        # Image with base64
        img_ref1 = ImageReference(
            source_path="embedded.png",
            alt_text="Embedded",
            base64_data=base64_data,
            mime_type="image/png"
        )
        
        # Image with file path only
        img_ref2 = ImageReference(
            source_path="external.png",
            extracted_path="output/images/external.png",
            alt_text="External"
        )
        
        # Create document
        doc = InternalDocument(
            sections=[
                Section(content=[img_ref1, img_ref2])
            ],
            images=[img_ref1, img_ref2]
        )
        
        # Serialize
        serializer = MarkdownSerializer()
        markdown = serializer.serialize(doc)
        
        # Verify mixed handling
        assert "data:image/png;base64," in markdown
        assert base64_data in markdown
        assert "output/images/external.png" in markdown
    
    def test_base64_embedding_with_metadata_enabled(self):
        """Test base64 embedding works with metadata inclusion."""
        # Create base64 image
        img = Image.new('RGB', (10, 10), color='purple')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        base64_data = base64.b64encode(img_bytes.read()).decode('utf-8')
        
        img_ref = ImageReference(
            source_path="test.png",
            base64_data=base64_data,
            mime_type="image/png"
        )
        
        from src.internal_representation import DocumentMetadata
        doc = InternalDocument(
            metadata=DocumentMetadata(
                title="Test Document",
                author="Test Author"
            ),
            sections=[Section(content=[img_ref])],
            images=[img_ref]
        )
        
        # Serialize with metadata
        serializer = MarkdownSerializer(include_metadata=True)
        markdown = serializer.serialize(doc)
        
        # Verify both metadata and base64 image
        assert "Test Document" in markdown
        assert "Test Author" in markdown
        assert "data:image/png;base64," in markdown
    
    def test_base64_embedding_with_heading_offset(self):
        """Test base64 embedding works with heading offset."""
        # Create base64 image
        img = Image.new('RGB', (10, 10), color='orange')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        base64_data = base64.b64encode(img_bytes.read()).decode('utf-8')
        
        img_ref = ImageReference(
            source_path="test.png",
            base64_data=base64_data,
            mime_type="image/png"
        )
        
        from src.internal_representation import Heading
        doc = InternalDocument(
            sections=[
                Section(
                    heading=Heading(level=1, text="Main Section"),
                    content=[img_ref]
                )
            ],
            images=[img_ref]
        )
        
        # Serialize with heading offset
        serializer = MarkdownSerializer(heading_offset=2)
        markdown = serializer.serialize(doc)
        
        # Verify heading offset applied and base64 image present
        assert "### Main Section" in markdown  # Level 1 + offset 2 = level 3
        assert "data:image/png;base64," in markdown


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
