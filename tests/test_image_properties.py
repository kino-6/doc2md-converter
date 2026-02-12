"""
Property-based tests for image extraction.

This module contains property-based tests using Hypothesis to verify
image extraction functionality across a wide range of inputs.

Feature: document-to-markdown-converter
Properties: 28, 29, 31
Validates: Requirements 7.1, 7.2, 7.3, 7.6
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from pathlib import Path
import tempfile
import shutil
import string

from src.image_extractor import ImageExtractor
from src.internal_representation import ImageReference, InternalDocument


# Helper strategies for generating image-related data
def image_filename_strategy():
    """Generate valid image filenames."""
    safe_chars = string.ascii_letters + string.digits + '_-'
    return st.text(alphabet=safe_chars, min_size=1, max_size=20)


def source_filename_strategy():
    """Generate valid source document filenames."""
    safe_chars = string.ascii_letters + string.digits + '_-'
    extensions = ['.docx', '.xlsx', '.pdf']
    return st.builds(
        lambda name, ext: f"{name}{ext}",
        st.text(alphabet=safe_chars, min_size=1, max_size=30),
        st.sampled_from(extensions)
    )


def image_format_strategy():
    """Generate valid image format extensions."""
    return st.sampled_from(['.png', '.jpg', '.jpeg', '.gif', '.svg'])


class TestImagePropertyDirectoryCreation:
    """Property 28: Image directory creation
    
    For any document containing images, the converter should extract and save
    them to a dedicated images directory following the naming convention
    {filename}/images/
    
    Validates: Requirements 7.1, 7.2
    """
    
    @given(
        source_filename=source_filename_strategy(),
        num_images=st.integers(min_value=1, max_value=10)
    )
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_28_image_directory_creation(self, source_filename, num_images):
        """
        Feature: document-to-markdown-converter
        Property 28: Image directory creation
        
        For any document containing images, the converter should extract and save
        them to a dedicated images directory following the naming convention
        {filename}/images/
        
        Validates: Requirements 7.1, 7.2
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create image extractor
            extractor = ImageExtractor(output_dir=tmp_dir)
            
            # Create document with image references
            images = [
                ImageReference(
                    source_path=f"word/media/image{i}.png",
                    alt_text=f"Image {i}"
                )
                for i in range(num_images)
            ]
            doc = InternalDocument(images=images)
            
            # Extract images (without actual data, just directory structure)
            extracted = extractor.extract_images(doc, source_filename)
            
            # Property: Images directory should be created
            source_path = Path(source_filename)
            base_name = source_path.stem
            expected_dir = Path(tmp_dir) / base_name / "images"
            
            assert expected_dir.exists(), \
                f"Images directory should exist at {expected_dir}"
            assert expected_dir.is_dir(), \
                f"Images path should be a directory: {expected_dir}"
            
            # Property: All images should have extracted paths
            assert len(extracted) == num_images, \
                f"Expected {num_images} extracted images, got {len(extracted)}"
            
            # Property: All extracted paths should follow the naming convention
            for img in extracted:
                assert img.extracted_path is not None, \
                    "Extracted image should have extracted_path set"
                assert img.extracted_path.startswith(f"{base_name}/images/"), \
                    f"Extracted path should start with '{base_name}/images/', got '{img.extracted_path}'"


class TestImagePropertyNamingConvention:
    """Property 29: Image naming convention
    
    For any extracted images, the converter should use either sequential naming
    (image_001.png, etc.) or preserve original filenames where available.
    
    Validates: Requirements 7.3
    """
    
    @given(
        source_filename=source_filename_strategy(),
        num_images=st.integers(min_value=1, max_value=20),
        preserve_filenames=st.booleans()
    )
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_29_sequential_naming(self, source_filename, num_images, preserve_filenames):
        """
        Feature: document-to-markdown-converter
        Property 29: Image naming convention
        
        For any extracted images, the converter should use either sequential naming
        (image_001.png, etc.) or preserve original filenames where available.
        
        Validates: Requirements 7.3
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create image extractor
            extractor = ImageExtractor(output_dir=tmp_dir, preserve_filenames=preserve_filenames)
            
            # Create document with image references
            images = [
                ImageReference(
                    source_path=f"word/media/photo_{i}.png",
                    alt_text=f"Photo {i}"
                )
                for i in range(num_images)
            ]
            doc = InternalDocument(images=images)
            
            # Extract images
            extracted = extractor.extract_images(doc, source_filename)
            
            # Property: All images should have unique extracted paths
            extracted_paths = [img.extracted_path for img in extracted]
            assert len(extracted_paths) == len(set(extracted_paths)), \
                "All extracted paths should be unique"
            
            # Property: Naming convention should be consistent
            source_path = Path(source_filename)
            base_name = source_path.stem
            
            if preserve_filenames:
                # Property: Original filenames should be preserved
                for i, img in enumerate(extracted):
                    expected_filename = f"photo_{i}.png"
                    assert img.extracted_path == f"{base_name}/images/{expected_filename}", \
                        f"Expected preserved filename '{expected_filename}' in path, got '{img.extracted_path}'"
            else:
                # Property: Sequential naming should be used
                for i, img in enumerate(extracted, start=1):
                    expected_filename = f"image_{i:03d}.png"
                    assert img.extracted_path == f"{base_name}/images/{expected_filename}", \
                        f"Expected sequential filename '{expected_filename}' in path, got '{img.extracted_path}'"
    
    @given(
        source_filename=source_filename_strategy(),
        data=st.data()
    )
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_29_preserve_original_filenames(self, source_filename, data):
        """
        Feature: document-to-markdown-converter
        Property 29: Image naming convention (preserve original)
        
        When preserve_filenames is enabled, original filenames should be preserved.
        
        Validates: Requirements 7.3
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create image extractor with preserve_filenames enabled
            extractor = ImageExtractor(output_dir=tmp_dir, preserve_filenames=True)
            
            # Generate random image filenames
            num_images = data.draw(st.integers(min_value=1, max_value=10))
            original_filenames = []
            
            for i in range(num_images):
                filename = data.draw(image_filename_strategy())
                extension = data.draw(image_format_strategy())
                original_filenames.append(f"{filename}{extension}")
            
            # Create document with image references using original filenames
            images = [
                ImageReference(
                    source_path=f"word/media/{fname}",
                    alt_text=f"Image {i}"
                )
                for i, fname in enumerate(original_filenames)
            ]
            doc = InternalDocument(images=images)
            
            # Extract images
            extracted = extractor.extract_images(doc, source_filename)
            
            # Property: Original filenames should be preserved
            source_path = Path(source_filename)
            base_name = source_path.stem
            
            for i, img in enumerate(extracted):
                expected_path = f"{base_name}/images/{original_filenames[i]}"
                assert img.extracted_path == expected_path, \
                    f"Expected preserved filename '{original_filenames[i]}', got '{img.extracted_path}'"


class TestImagePropertyFormatSupport:
    """Property 31: Image format support
    
    For any common image format (PNG, JPEG, GIF, SVG), the converter should
    successfully extract and save the image.
    
    Validates: Requirements 7.6
    """
    
    @given(
        source_filename=source_filename_strategy(),
        image_format=image_format_strategy(),
        num_images=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_31_image_format_support(self, source_filename, image_format, num_images):
        """
        Feature: document-to-markdown-converter
        Property 31: Image format support
        
        For any common image format (PNG, JPEG, GIF, SVG), the converter should
        successfully extract and save the image.
        
        Validates: Requirements 7.6
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create image extractor
            extractor = ImageExtractor(output_dir=tmp_dir)
            
            # Create document with images of the specified format
            images = [
                ImageReference(
                    source_path=f"word/media/image{i}{image_format}",
                    alt_text=f"Image {i}"
                )
                for i in range(num_images)
            ]
            doc = InternalDocument(images=images)
            
            # Create fake image data for each format
            # Different formats have different magic bytes
            format_magic_bytes = {
                '.png': b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR',
                '.jpg': b'\xff\xd8\xff\xe0\x00\x10JFIF',
                '.jpeg': b'\xff\xd8\xff\xe0\x00\x10JFIF',
                '.gif': b'GIF89a',
                '.svg': b'<svg xmlns="http://www.w3.org/2000/svg"></svg>'
            }
            
            image_data = format_magic_bytes.get(image_format, b'\x00\x00\x00\x00')
            image_data_list = [(img, image_data) for img in images]
            
            # Extract and save images
            extracted = extractor.extract_images(doc, source_filename, image_data_list)
            
            # Property: All images should be extracted
            assert len(extracted) == num_images, \
                f"Expected {num_images} extracted images, got {len(extracted)}"
            
            # Property: All image files should exist on disk
            source_path = Path(source_filename)
            base_name = source_path.stem
            images_dir = Path(tmp_dir) / base_name / "images"
            
            for img in extracted:
                assert img.extracted_path is not None, \
                    "Extracted image should have extracted_path set"
                
                # Construct full path
                full_path = Path(tmp_dir) / img.extracted_path
                assert full_path.exists(), \
                    f"Image file should exist at {full_path}"
                
                # Property: File should contain the image data
                with open(full_path, 'rb') as f:
                    saved_data = f.read()
                    assert saved_data == image_data, \
                        f"Saved image data should match original data"
    
    @given(
        source_filename=source_filename_strategy(),
        data=st.data()
    )
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_31_mixed_format_support(self, source_filename, data):
        """
        Feature: document-to-markdown-converter
        Property 31: Image format support (mixed formats)
        
        For documents with images in multiple formats, all formats should be
        successfully extracted and saved.
        
        Validates: Requirements 7.6
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create image extractor
            extractor = ImageExtractor(output_dir=tmp_dir)
            
            # Generate images with different formats
            num_images = data.draw(st.integers(min_value=2, max_value=8))
            formats = ['.png', '.jpg', '.jpeg', '.gif', '.svg']
            
            images = []
            image_data_list = []
            
            format_magic_bytes = {
                '.png': b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR',
                '.jpg': b'\xff\xd8\xff\xe0\x00\x10JFIF',
                '.jpeg': b'\xff\xd8\xff\xe0\x00\x10JFIF',
                '.gif': b'GIF89a',
                '.svg': b'<svg xmlns="http://www.w3.org/2000/svg"></svg>'
            }
            
            for i in range(num_images):
                img_format = data.draw(st.sampled_from(formats))
                img_ref = ImageReference(
                    source_path=f"word/media/image{i}{img_format}",
                    alt_text=f"Image {i}"
                )
                images.append(img_ref)
                
                img_data = format_magic_bytes.get(img_format, b'\x00\x00\x00\x00')
                image_data_list.append((img_ref, img_data))
            
            doc = InternalDocument(images=images)
            
            # Extract and save images
            extracted = extractor.extract_images(doc, source_filename, image_data_list)
            
            # Property: All images should be extracted regardless of format
            assert len(extracted) == num_images, \
                f"Expected {num_images} extracted images, got {len(extracted)}"
            
            # Property: All image files should exist and contain correct data
            for i, img in enumerate(extracted):
                full_path = Path(tmp_dir) / img.extracted_path
                assert full_path.exists(), \
                    f"Image file should exist at {full_path}"
                
                # Verify data integrity
                with open(full_path, 'rb') as f:
                    saved_data = f.read()
                    expected_data = image_data_list[i][1]
                    assert saved_data == expected_data, \
                        f"Saved image data should match original data for image {i}"


class TestImagePropertyRelativePathReferences:
    """Property 30: Relative path references
    
    For any extracted image, the Markdown output should reference it using a
    relative path pointing to the images directory.
    
    Validates: Requirements 7.4
    """
    
    @given(
        source_filename=source_filename_strategy(),
        num_images=st.integers(min_value=1, max_value=10)
    )
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_30_relative_path_references(self, source_filename, num_images):
        """
        Feature: document-to-markdown-converter
        Property 30: Relative path references
        
        For any extracted image, the Markdown output should reference it using a
        relative path pointing to the images directory.
        
        Validates: Requirements 7.4
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create image extractor
            extractor = ImageExtractor(output_dir=tmp_dir)
            
            # Create document with image references
            images = [
                ImageReference(
                    source_path=f"word/media/image{i}.png",
                    alt_text=f"Image {i}"
                )
                for i in range(num_images)
            ]
            doc = InternalDocument(images=images)
            
            # Extract images
            extracted = extractor.extract_images(doc, source_filename)
            
            # Property: All extracted images should have relative paths
            source_path = Path(source_filename)
            base_name = source_path.stem
            
            for img in extracted:
                assert img.extracted_path is not None, \
                    "Extracted image should have extracted_path set"
                
                # Property: Path should be relative (not absolute)
                assert not Path(img.extracted_path).is_absolute(), \
                    f"Extracted path should be relative, got '{img.extracted_path}'"
                
                # Property: Path should point to images directory
                assert img.extracted_path.startswith(f"{base_name}/images/"), \
                    f"Extracted path should point to images directory, got '{img.extracted_path}'"
                
                # Property: Path should be in format {base_name}/images/{filename}
                path_parts = img.extracted_path.split('/')
                assert len(path_parts) == 3, \
                    f"Relative path should have 3 parts (base/images/filename), got {len(path_parts)}"
                assert path_parts[0] == base_name, \
                    f"First part should be base name '{base_name}', got '{path_parts[0]}'"
                assert path_parts[1] == "images", \
                    f"Second part should be 'images', got '{path_parts[1]}'"
                assert path_parts[2], \
                    "Third part (filename) should not be empty"

    
    @given(
        source_filename=source_filename_strategy(),
        num_images=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_30_markdown_uses_relative_paths(self, source_filename, num_images):
        """
        Feature: document-to-markdown-converter
        Property 30: Relative path references (Markdown serialization)
        
        For any extracted image, the Markdown output should reference it using a
        relative path pointing to the images directory.
        
        Validates: Requirements 7.4
        """
        from src.markdown_serializer import MarkdownSerializer
        from src.internal_representation import Section
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create image extractor
            extractor = ImageExtractor(output_dir=tmp_dir)
            
            # Create document with image references
            images = [
                ImageReference(
                    source_path=f"word/media/image{i}.png",
                    alt_text=f"Test Image {i}"
                )
                for i in range(num_images)
            ]
            
            # Extract images
            extracted = extractor.extract_images(
                InternalDocument(images=images), 
                source_filename
            )
            
            # Create document with extracted images in a section
            section = Section(content=extracted)
            doc = InternalDocument(sections=[section], images=extracted)
            
            # Serialize to Markdown
            serializer = MarkdownSerializer()
            markdown_output = serializer.serialize(doc)
            
            # Property: Markdown should contain relative path references
            source_path = Path(source_filename)
            base_name = source_path.stem
            
            for i, img in enumerate(extracted, start=1):
                # Property: Markdown should contain the relative path
                assert img.extracted_path in markdown_output, \
                    f"Markdown output should contain relative path '{img.extracted_path}'"
                
                # Property: Markdown should use proper image syntax with relative path
                expected_pattern = f"![Test Image {i-1}]({base_name}/images/image_{i:03d}.png)"
                assert expected_pattern in markdown_output, \
                    f"Markdown should contain image reference '{expected_pattern}'"
                
                # Property: Path should not be absolute
                assert not any(
                    line.startswith('![') and ('C:' in line or line.startswith('/'))
                    for line in markdown_output.split('\n')
                ), "Markdown should not contain absolute paths"



class TestImagePropertyExtractionFailureHandling:
    """Property 32: Image extraction failure handling
    
    For any image that cannot be extracted, the converter should include a
    placeholder comment in the Markdown output.
    
    Validates: Requirements 7.7
    """
    
    @given(
        num_failed_images=st.integers(min_value=1, max_value=5),
        alt_texts=st.lists(
            st.text(alphabet=string.ascii_letters + string.digits + ' ', min_size=1, max_size=30),
            min_size=1,
            max_size=5
        )
    )
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_32_extraction_failure_placeholder(self, num_failed_images, alt_texts):
        """
        Feature: document-to-markdown-converter
        Property 32: Image extraction failure handling
        
        For any image that cannot be extracted, the converter should include a
        placeholder comment in the Markdown output.
        
        Validates: Requirements 7.7
        """
        from src.markdown_serializer import MarkdownSerializer
        from src.internal_representation import Section
        
        # Ensure we have enough alt texts
        while len(alt_texts) < num_failed_images:
            alt_texts.append(f"Image {len(alt_texts) + 1}")
        
        # Create images with no extracted_path (simulating extraction failure)
        failed_images = [
            ImageReference(
                source_path=None,  # No source path
                extracted_path=None,  # No extracted path (extraction failed)
                alt_text=alt_texts[i]
            )
            for i in range(num_failed_images)
        ]
        
        # Create document with failed images in a section
        section = Section(content=failed_images)
        doc = InternalDocument(sections=[section], images=failed_images)
        
        # Serialize to Markdown
        serializer = MarkdownSerializer()
        markdown_output = serializer.serialize(doc)
        
        # Property: Markdown should contain placeholder comments for failed extractions
        for img in failed_images:
            # Property: Should contain a comment indicating extraction failure
            assert "<!-- Image extraction failed:" in markdown_output, \
                "Markdown should contain placeholder comment for failed extraction"
            
            # Property: Comment should include the alt text
            expected_comment = f"<!-- Image extraction failed: {img.alt_text} -->"
            assert expected_comment in markdown_output, \
                f"Markdown should contain placeholder '{expected_comment}'"
        
        # Property: Should NOT contain regular image syntax for failed images
        for img in failed_images:
            # Should not have ![alt](path) format for failed images
            assert f"![{img.alt_text}](" not in markdown_output or \
                   f"<!-- Image extraction failed: {img.alt_text} -->" in markdown_output, \
                "Failed images should use placeholder comments, not regular image syntax"

    
    @given(
        num_successful=st.integers(min_value=1, max_value=3),
        num_failed=st.integers(min_value=1, max_value=3)
    )
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_32_mixed_success_and_failure(self, num_successful, num_failed):
        """
        Feature: document-to-markdown-converter
        Property 32: Image extraction failure handling (mixed scenario)
        
        For documents with both successful and failed image extractions,
        the converter should handle each appropriately.
        
        Validates: Requirements 7.7
        """
        from src.markdown_serializer import MarkdownSerializer
        from src.internal_representation import Section
        
        # Create successful images (with extracted_path)
        successful_images = [
            ImageReference(
                source_path=f"word/media/image{i}.png",
                extracted_path=f"document/images/image_{i:03d}.png",
                alt_text=f"Success Image {i}"
            )
            for i in range(num_successful)
        ]
        
        # Create failed images (without extracted_path)
        failed_images = [
            ImageReference(
                source_path=None,
                extracted_path=None,
                alt_text=f"Failed Image {i}"
            )
            for i in range(num_failed)
        ]
        
        # Mix them together
        all_images = successful_images + failed_images
        section = Section(content=all_images)
        doc = InternalDocument(sections=[section], images=all_images)
        
        # Serialize to Markdown
        serializer = MarkdownSerializer()
        markdown_output = serializer.serialize(doc)
        
        # Property: Successful images should use regular image syntax
        for img in successful_images:
            expected_syntax = f"![{img.alt_text}]({img.extracted_path})"
            assert expected_syntax in markdown_output, \
                f"Successful image should use regular syntax: '{expected_syntax}'"
        
        # Property: Failed images should use placeholder comments
        for img in failed_images:
            expected_comment = f"<!-- Image extraction failed: {img.alt_text} -->"
            assert expected_comment in markdown_output, \
                f"Failed image should use placeholder comment: '{expected_comment}'"
        
        # Property: Total number of image references should match
        image_references = markdown_output.count('![') + markdown_output.count('<!-- Image extraction failed:')
        assert image_references >= len(all_images), \
            f"Should have at least {len(all_images)} image references, got {image_references}"

    
    @given(
        has_source_path=st.booleans(),
        has_extracted_path=st.booleans()
    )
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_32_various_failure_scenarios(self, has_source_path, has_extracted_path):
        """
        Feature: document-to-markdown-converter
        Property 32: Image extraction failure handling (various scenarios)
        
        Test different combinations of source_path and extracted_path to ensure
        proper failure handling.
        
        Validates: Requirements 7.7
        """
        from src.markdown_serializer import MarkdownSerializer
        from src.internal_representation import Section
        
        # Create image with various path combinations
        img = ImageReference(
            source_path="word/media/image.png" if has_source_path else None,
            extracted_path="document/images/image_001.png" if has_extracted_path else None,
            alt_text="Test Image"
        )
        
        section = Section(content=[img])
        doc = InternalDocument(sections=[section], images=[img])
        
        # Serialize to Markdown
        serializer = MarkdownSerializer()
        markdown_output = serializer.serialize(doc)
        
        if has_extracted_path:
            # Property: If extracted_path exists, use it (successful extraction)
            expected_syntax = f"![Test Image](document/images/image_001.png)"
            assert expected_syntax in markdown_output, \
                "Should use regular image syntax when extracted_path is available"
            assert "<!-- Image extraction failed:" not in markdown_output, \
                "Should not show failure comment when extraction succeeded"
        elif has_source_path:
            # Property: If only source_path exists, use it as fallback
            expected_syntax = f"![Test Image](word/media/image.png)"
            assert expected_syntax in markdown_output, \
                "Should use source_path as fallback when extracted_path is not available"
        else:
            # Property: If neither path exists, show failure placeholder
            expected_comment = "<!-- Image extraction failed: Test Image -->"
            assert expected_comment in markdown_output, \
                "Should show failure placeholder when no paths are available"
