"""Property-based tests for image handling mode feature.

This module contains property-based tests using Hypothesis to verify
that image handling mode (file extraction vs Base64 embedding) works correctly.

Feature: document-to-markdown-converter
Property: 37
Validates: Requirements 8.4
"""

import pytest
import base64
from hypothesis import given, strategies as st, settings
from src.markdown_serializer import MarkdownSerializer
from src.internal_representation import (
    InternalDocument,
    Section,
    Heading,
    Paragraph,
    ImageReference,
    TextFormatting,
)


# Strategy for generating valid image paths
image_path_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='_-.',
        min_codepoint=ord('a'),
        max_codepoint=ord('z')
    ),
    min_size=5,
    max_size=50
).filter(lambda x: '.' in x)  # Ensure it looks like a filename

# Strategy for generating alt text
alt_text_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'),
        min_codepoint=32,
        max_codepoint=126
    ),
    min_size=1,
    max_size=100
)

# Strategy for generating base64 data (simulated)
def generate_base64_data():
    """Generate valid base64-encoded data."""
    # Create some random bytes and encode them
    return st.binary(min_size=10, max_size=100).map(
        lambda b: base64.b64encode(b).decode('ascii')
    )

base64_strategy = generate_base64_data()

# Strategy for MIME types
mime_type_strategy = st.sampled_from([
    'image/png',
    'image/jpeg',
    'image/gif',
    'image/svg+xml'
])


class TestImageHandlingModeProperty:
    """Property 37: Image handling mode
    
    For any document with images, the converter should either extract images to files
    or embed them as base64 based on the configuration setting.
    
    Validates: Requirements 8.4
    """
    
    @given(
        image_path=image_path_strategy,
        alt_text=st.one_of(st.none(), alt_text_strategy),
        base64_data=base64_strategy,
        mime_type=mime_type_strategy
    )
    @settings(max_examples=100, deadline=None)
    def test_property_37_base64_embedding_mode(
        self, image_path, alt_text, base64_data, mime_type
    ):
        """
        Feature: document-to-markdown-converter
        Property 37: Image handling mode (base64 embedding)
        
        For any document with images, when base64 embedding is enabled, the converter
        should embed images as base64 data URLs in the output.
        
        **Validates: Requirements 8.4**
        """
        # Create image reference with base64 data
        image_ref = ImageReference(
            source_path=image_path,
            alt_text=alt_text,
            base64_data=base64_data,
            mime_type=mime_type
        )
        
        # Create document with image
        doc = InternalDocument(
            sections=[
                Section(
                    heading=Heading(level=1, text="Test Document"),
                    content=[
                        Paragraph(text="Document with image", formatting=TextFormatting.NORMAL),
                        image_ref
                    ]
                )
            ],
            images=[image_ref]
        )
        
        # Serialize the document
        serializer = MarkdownSerializer()
        result = serializer.serialize(doc)
        
        # Property: Result should be a non-empty string
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Property: Result should contain base64 data URL
        assert "data:" in result, \
            "Output should contain data URL when base64 data is present"
        
        # Property: Result should contain the MIME type
        assert mime_type in result, \
            f"Output should contain MIME type '{mime_type}'"
        
        # Property: Result should contain base64 marker
        assert "base64," in result, \
            "Output should contain 'base64,' marker in data URL"
        
        # Property: Result should contain the base64 data
        assert base64_data in result, \
            "Output should contain the base64-encoded image data"
        
        # Property: Result should NOT contain file path reference
        assert image_path not in result or "data:" in result, \
            "When base64 data is present, should use data URL instead of file path"
    
    @given(
        image_path=image_path_strategy,
        alt_text=st.one_of(st.none(), alt_text_strategy)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_37_file_extraction_mode(self, image_path, alt_text):
        """
        Feature: document-to-markdown-converter
        Property 37: Image handling mode (file extraction)
        
        For any document with images, when file extraction is enabled (no base64 data),
        the converter should reference images as file paths in the output.
        
        **Validates: Requirements 8.4**
        """
        # Create image reference without base64 data (file extraction mode)
        extracted_path = f"test_doc/images/{image_path}"
        image_ref = ImageReference(
            source_path=image_path,
            extracted_path=extracted_path,
            alt_text=alt_text,
            base64_data=None  # No base64 data = file extraction mode
        )
        
        # Create document with image
        doc = InternalDocument(
            sections=[
                Section(
                    heading=Heading(level=1, text="Test Document"),
                    content=[
                        Paragraph(text="Document with image", formatting=TextFormatting.NORMAL),
                        image_ref
                    ]
                )
            ],
            images=[image_ref]
        )
        
        # Serialize the document
        serializer = MarkdownSerializer()
        result = serializer.serialize(doc)
        
        # Property: Result should be a non-empty string
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Property: Result should contain the extracted file path
        assert extracted_path in result, \
            f"Output should contain extracted file path '{extracted_path}'"
        
        # Property: Result should NOT contain base64 data URL
        assert "data:" not in result or extracted_path in result, \
            "When no base64 data is present, should use file path"
        
        # Property: Result should NOT contain base64 marker
        assert "base64," not in result, \
            "File extraction mode should not contain base64 marker"
        
        # Property: Result should use Markdown image syntax
        assert "![" in result and "](" in result, \
            "Output should use Markdown image syntax ![alt](path)"
    
    @given(
        num_images=st.integers(min_value=1, max_value=10),
        use_base64=st.booleans(),
        data=st.data()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_37_consistent_mode_for_all_images(
        self, num_images, use_base64, data
    ):
        """
        Feature: document-to-markdown-converter
        Property 37: Image handling mode (consistency)
        
        For any document with multiple images, the handling mode should be
        consistently applied to all images.
        
        **Validates: Requirements 8.4**
        """
        # Generate multiple images
        images = []
        content = [Paragraph(text="Document with multiple images", formatting=TextFormatting.NORMAL)]
        
        for i in range(num_images):
            path = f"image_{i}.png"
            alt = data.draw(st.one_of(st.none(), alt_text_strategy))
            
            if use_base64:
                # Base64 embedding mode
                b64_data = data.draw(base64_strategy)
                mime = data.draw(mime_type_strategy)
                img_ref = ImageReference(
                    source_path=path,
                    alt_text=alt,
                    base64_data=b64_data,
                    mime_type=mime
                )
            else:
                # File extraction mode
                extracted = f"test_doc/images/image_{i}.png"
                img_ref = ImageReference(
                    source_path=path,
                    extracted_path=extracted,
                    alt_text=alt,
                    base64_data=None
                )
            
            images.append(img_ref)
            content.append(img_ref)
        
        # Create document
        doc = InternalDocument(
            sections=[
                Section(
                    heading=Heading(level=1, text="Test Document"),
                    content=content
                )
            ],
            images=images
        )
        
        # Serialize the document
        serializer = MarkdownSerializer()
        result = serializer.serialize(doc)
        
        # Property: Result should be a non-empty string
        assert isinstance(result, str)
        assert len(result) > 0
        
        if use_base64:
            # Property: All images should use base64 data URLs
            data_url_count = result.count("data:")
            assert data_url_count >= num_images, \
                f"Expected at least {num_images} data URLs, found {data_url_count}"
            
            # Property: Should contain base64 markers
            base64_count = result.count("base64,")
            assert base64_count >= num_images, \
                f"Expected at least {num_images} base64 markers, found {base64_count}"
        else:
            # Property: All images should use file paths
            # Count image references (![...](...)
            image_ref_count = result.count("![")
            assert image_ref_count >= num_images, \
                f"Expected at least {num_images} image references, found {image_ref_count}"
            
            # Property: Should NOT contain base64 data URLs
            assert "data:" not in result or "test_doc/images/" in result, \
                "File extraction mode should not use data URLs"
    
    @given(
        image_path=image_path_strategy,
        alt_text=alt_text_strategy,
        base64_data=base64_strategy,
        mime_type=mime_type_strategy
    )
    @settings(max_examples=100, deadline=None)
    def test_property_37_base64_preserves_alt_text(
        self, image_path, alt_text, base64_data, mime_type
    ):
        """
        Feature: document-to-markdown-converter
        Property 37: Image handling mode (alt text preservation in base64)
        
        For any image with alt text, base64 embedding should preserve the alt text
        in the Markdown output.
        
        **Validates: Requirements 8.4**
        """
        # Create image reference with base64 data and alt text
        image_ref = ImageReference(
            source_path=image_path,
            alt_text=alt_text,
            base64_data=base64_data,
            mime_type=mime_type
        )
        
        # Serialize the image
        serializer = MarkdownSerializer()
        result = serializer.serialize_image(image_ref)
        
        # Property: Result should be a non-empty string
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Property: Result should use Markdown image syntax
        assert result.startswith("!["), \
            "Image should use Markdown syntax starting with ![" 
        
        # Property: Result should contain data URL
        assert "data:" in result, \
            "Base64 image should use data URL"
        
        # Property: Alt text should be preserved (possibly escaped)
        # The alt text appears between ![ and ]
        assert "![" in result and "](" in result, \
            "Image should have proper Markdown structure"
    
    @given(
        image_path=image_path_strategy,
        alt_text=alt_text_strategy
    )
    @settings(max_examples=100, deadline=None)
    def test_property_37_file_extraction_preserves_alt_text(
        self, image_path, alt_text
    ):
        """
        Feature: document-to-markdown-converter
        Property 37: Image handling mode (alt text preservation in file extraction)
        
        For any image with alt text, file extraction should preserve the alt text
        in the Markdown output.
        
        **Validates: Requirements 8.4**
        """
        # Create image reference without base64 data
        extracted_path = f"test_doc/images/{image_path}"
        image_ref = ImageReference(
            source_path=image_path,
            extracted_path=extracted_path,
            alt_text=alt_text,
            base64_data=None
        )
        
        # Serialize the image
        serializer = MarkdownSerializer()
        result = serializer.serialize_image(image_ref)
        
        # Property: Result should be a non-empty string
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Property: Result should use Markdown image syntax
        assert result.startswith("!["), \
            "Image should use Markdown syntax starting with !["
        
        # Property: Result should contain file path
        assert extracted_path in result, \
            f"Image should reference file path '{extracted_path}'"
        
        # Property: Alt text should be preserved (possibly escaped)
        assert "![" in result and "](" in result, \
            "Image should have proper Markdown structure"
    
    @given(
        image_path=image_path_strategy,
        base64_data=base64_strategy,
        mime_type=mime_type_strategy
    )
    @settings(max_examples=100, deadline=None)
    def test_property_37_base64_data_url_format(
        self, image_path, base64_data, mime_type
    ):
        """
        Feature: document-to-markdown-converter
        Property 37: Image handling mode (data URL format)
        
        For any image with base64 data, the output should use proper data URL format:
        data:<mime_type>;base64,<data>
        
        **Validates: Requirements 8.4**
        """
        # Create image reference with base64 data
        image_ref = ImageReference(
            source_path=image_path,
            base64_data=base64_data,
            mime_type=mime_type
        )
        
        # Serialize the image
        serializer = MarkdownSerializer()
        result = serializer.serialize_image(image_ref)
        
        # Property: Result should contain proper data URL format
        expected_prefix = f"data:{mime_type};base64,"
        assert expected_prefix in result, \
            f"Data URL should have format 'data:{mime_type};base64,...'"
        
        # Property: Base64 data should follow the prefix
        assert base64_data in result, \
            "Data URL should contain the base64-encoded data"
        
        # Property: Data URL should be in the path part of Markdown image syntax
        # Format: ![alt](data:...)
        assert "](data:" in result, \
            "Data URL should be in the path part of Markdown image syntax"
    
    @given(
        image_path=image_path_strategy,
        ocr_text=st.text(min_size=1, max_size=100),
        use_base64=st.booleans(),
        base64_data=base64_strategy,
        mime_type=mime_type_strategy
    )
    @settings(max_examples=100, deadline=None)
    def test_property_37_ocr_text_preserved_in_both_modes(
        self, image_path, ocr_text, use_base64, base64_data, mime_type
    ):
        """
        Feature: document-to-markdown-converter
        Property 37: Image handling mode (OCR text preservation)
        
        For any image with OCR text, both base64 and file extraction modes should
        preserve the OCR text in the output.
        
        **Validates: Requirements 8.4**
        """
        # Skip empty or whitespace-only OCR text
        if not ocr_text.strip():
            return
        
        # Create image reference with OCR text
        if use_base64:
            image_ref = ImageReference(
                source_path=image_path,
                ocr_text=ocr_text,
                base64_data=base64_data,
                mime_type=mime_type
            )
        else:
            extracted_path = f"test_doc/images/{image_path}"
            image_ref = ImageReference(
                source_path=image_path,
                extracted_path=extracted_path,
                ocr_text=ocr_text,
                base64_data=None
            )
        
        # Serialize the image
        serializer = MarkdownSerializer()
        result = serializer.serialize_image(image_ref)
        
        # Property: Result should be a non-empty string
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Property: OCR text should be present in the output
        # The serializer adds OCR text as "*OCR extracted text: ...*"
        assert "OCR extracted text:" in result or ocr_text in result, \
            "OCR text should be preserved in the output"
    
    @given(
        image_path=image_path_strategy,
        base64_data=base64_strategy
    )
    @settings(max_examples=100, deadline=None)
    def test_property_37_base64_without_mime_type_uses_default(
        self, image_path, base64_data
    ):
        """
        Feature: document-to-markdown-converter
        Property 37: Image handling mode (default MIME type)
        
        For any image with base64 data but no MIME type, the converter should
        use a default MIME type (image/png).
        
        **Validates: Requirements 8.4**
        """
        # Create image reference with base64 data but no MIME type
        image_ref = ImageReference(
            source_path=image_path,
            base64_data=base64_data,
            mime_type=None  # No MIME type specified
        )
        
        # Serialize the image
        serializer = MarkdownSerializer()
        result = serializer.serialize_image(image_ref)
        
        # Property: Result should contain data URL
        assert "data:" in result, \
            "Base64 image should use data URL"
        
        # Property: Should use default MIME type (image/png)
        assert "data:image/png;base64," in result, \
            "Should use default MIME type 'image/png' when none is specified"
    
    @given(
        num_base64=st.integers(min_value=0, max_value=5),
        num_file=st.integers(min_value=0, max_value=5),
        data=st.data()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_37_mixed_mode_handling(self, num_base64, num_file, data):
        """
        Feature: document-to-markdown-converter
        Property 37: Image handling mode (mixed mode)
        
        For any document with both base64 and file-extracted images, the converter
        should handle each image according to its configuration.
        
        **Validates: Requirements 8.4**
        """
        # Skip if no images
        if num_base64 == 0 and num_file == 0:
            return
        
        images = []
        content = [Paragraph(text="Document with mixed images", formatting=TextFormatting.NORMAL)]
        
        # Add base64 images
        for i in range(num_base64):
            b64_data = data.draw(base64_strategy)
            mime = data.draw(mime_type_strategy)
            img_ref = ImageReference(
                source_path=f"base64_image_{i}.png",
                base64_data=b64_data,
                mime_type=mime
            )
            images.append(img_ref)
            content.append(img_ref)
        
        # Add file-extracted images
        for i in range(num_file):
            img_ref = ImageReference(
                source_path=f"file_image_{i}.png",
                extracted_path=f"test_doc/images/file_image_{i}.png",
                base64_data=None
            )
            images.append(img_ref)
            content.append(img_ref)
        
        # Create document
        doc = InternalDocument(
            sections=[
                Section(
                    heading=Heading(level=1, text="Test Document"),
                    content=content
                )
            ],
            images=images
        )
        
        # Serialize the document
        serializer = MarkdownSerializer()
        result = serializer.serialize(doc)
        
        # Property: Result should be a non-empty string
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Property: Should contain data URLs for base64 images
        if num_base64 > 0:
            data_url_count = result.count("data:")
            assert data_url_count >= num_base64, \
                f"Expected at least {num_base64} data URLs, found {data_url_count}"
        
        # Property: Should contain file paths for file-extracted images
        if num_file > 0:
            file_path_count = result.count("test_doc/images/")
            assert file_path_count >= num_file, \
                f"Expected at least {num_file} file paths, found {file_path_count}"
        
        # Property: Total image references should match total images
        total_images = num_base64 + num_file
        image_ref_count = result.count("![")
        assert image_ref_count >= total_images, \
            f"Expected at least {total_images} image references, found {image_ref_count}"


# Run all property tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
