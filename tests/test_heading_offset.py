"""
Unit tests for heading level offset feature.

These tests verify that the heading_offset configuration correctly adjusts
heading levels throughout the conversion process.

Requirements: 8.1
"""

import pytest
from src.markdown_serializer import MarkdownSerializer
from src.internal_representation import (
    InternalDocument,
    Section,
    Heading,
    Paragraph,
    TextFormatting,
)


class TestHeadingOffset:
    """Test suite for heading level offset feature."""
    
    def test_no_offset(self):
        """Test that headings remain unchanged with offset=0."""
        serializer = MarkdownSerializer(heading_offset=0)
        
        # Test all heading levels
        for level in range(1, 7):
            heading = Heading(level=level, text=f"Level {level}")
            result = serializer.serialize_heading(heading)
            expected = "#" * level + f" Level {level}"
            assert result == expected
    
    def test_positive_offset(self):
        """Test that positive offset increases heading levels."""
        serializer = MarkdownSerializer(heading_offset=1)
        
        # H1 becomes H2
        heading = Heading(level=1, text="Title")
        assert serializer.serialize_heading(heading) == "## Title"
        
        # H2 becomes H3
        heading = Heading(level=2, text="Section")
        assert serializer.serialize_heading(heading) == "### Section"
        
        # H3 becomes H4
        heading = Heading(level=3, text="Subsection")
        assert serializer.serialize_heading(heading) == "#### Subsection"
    
    def test_negative_offset(self):
        """Test that negative offset decreases heading levels."""
        serializer = MarkdownSerializer(heading_offset=-1)
        
        # H2 becomes H1
        heading = Heading(level=2, text="Title")
        assert serializer.serialize_heading(heading) == "# Title"
        
        # H3 becomes H2
        heading = Heading(level=3, text="Section")
        assert serializer.serialize_heading(heading) == "## Section"
        
        # H4 becomes H3
        heading = Heading(level=4, text="Subsection")
        assert serializer.serialize_heading(heading) == "### Subsection"
    
    def test_offset_clamping_upper_bound(self):
        """Test that heading levels are clamped to maximum of 6."""
        serializer = MarkdownSerializer(heading_offset=2)
        
        # H5 + 2 = H7, but should be clamped to H6
        heading = Heading(level=5, text="Deep Section")
        result = serializer.serialize_heading(heading)
        assert result == "###### Deep Section"
        assert result.count("#") == 6
        
        # H6 + 2 = H8, but should be clamped to H6
        heading = Heading(level=6, text="Deepest Section")
        result = serializer.serialize_heading(heading)
        assert result == "###### Deepest Section"
        assert result.count("#") == 6
    
    def test_offset_clamping_lower_bound(self):
        """Test that heading levels are clamped to minimum of 1."""
        serializer = MarkdownSerializer(heading_offset=-2)
        
        # H2 - 2 = H0, but should be clamped to H1
        heading = Heading(level=2, text="Section")
        result = serializer.serialize_heading(heading)
        assert result == "# Section"
        assert result.count("#") == 1
        
        # H1 - 2 = H-1, but should be clamped to H1
        heading = Heading(level=1, text="Title")
        result = serializer.serialize_heading(heading)
        assert result == "# Title"
        assert result.count("#") == 1
    
    def test_large_positive_offset(self):
        """Test that large positive offsets are handled correctly."""
        serializer = MarkdownSerializer(heading_offset=10)
        
        # Any heading + 10 should be clamped to H6
        for level in range(1, 7):
            heading = Heading(level=level, text=f"Level {level}")
            result = serializer.serialize_heading(heading)
            assert result.count("#") == 6
    
    def test_large_negative_offset(self):
        """Test that large negative offsets are handled correctly."""
        serializer = MarkdownSerializer(heading_offset=-10)
        
        # Any heading - 10 should be clamped to H1
        for level in range(1, 7):
            heading = Heading(level=level, text=f"Level {level}")
            result = serializer.serialize_heading(heading)
            assert result.count("#") == 1
    
    def test_offset_in_document_context(self):
        """Test heading offset in a full document."""
        serializer = MarkdownSerializer(heading_offset=1)
        
        doc = InternalDocument(
            sections=[
                Section(
                    heading=Heading(level=1, text="Main Title"),
                    content=[
                        Paragraph(text="Introduction text.", formatting=TextFormatting.NORMAL)
                    ]
                ),
                Section(
                    heading=Heading(level=2, text="Section"),
                    content=[
                        Paragraph(text="Section content.", formatting=TextFormatting.NORMAL)
                    ]
                ),
                Section(
                    heading=Heading(level=3, text="Subsection"),
                    content=[
                        Paragraph(text="Subsection content.", formatting=TextFormatting.NORMAL)
                    ]
                )
            ]
        )
        
        result = serializer.serialize(doc)
        
        # Verify all headings are offset by 1
        assert "## Main Title" in result  # H1 -> H2
        assert "### Section" in result     # H2 -> H3
        assert "#### Subsection" in result # H3 -> H4
        
        # Verify content is preserved
        assert "Introduction text." in result
        assert "Section content." in result
        assert "Subsection content." in result
    
    def test_offset_preserves_heading_text(self):
        """Test that offset doesn't affect heading text content."""
        serializer = MarkdownSerializer(heading_offset=2)
        
        # Test with various text content
        test_cases = [
            "Simple Title",
            "Title with Numbers 123",
            "Title with Special Characters: @#$%",
            "日本語のタイトル",
            "Mixed 日本語 and English",
        ]
        
        for text in test_cases:
            heading = Heading(level=1, text=text)
            result = serializer.serialize_heading(heading)
            # Should have 3 hashes (1 + 2 offset) and the original text
            assert result.startswith("### ")
            assert text in result or "\\" in result  # Text or escaped version
    
    def test_offset_with_multiple_sections(self):
        """Test offset consistency across multiple sections."""
        serializer = MarkdownSerializer(heading_offset=1)
        
        # Create document with multiple sections at different levels
        sections = []
        for i in range(1, 6):
            sections.append(
                Section(
                    heading=Heading(level=i, text=f"Heading Level {i}"),
                    content=[
                        Paragraph(text=f"Content {i}", formatting=TextFormatting.NORMAL)
                    ]
                )
            )
        
        doc = InternalDocument(sections=sections)
        result = serializer.serialize(doc)
        
        # Verify each heading is offset correctly
        assert "## Heading Level 1" in result  # H1 -> H2
        assert "### Heading Level 2" in result # H2 -> H3
        assert "#### Heading Level 3" in result # H3 -> H4
        assert "##### Heading Level 4" in result # H4 -> H5
        assert "###### Heading Level 5" in result # H5 -> H6
    
    def test_zero_offset_is_default(self):
        """Test that default serializer has no offset."""
        serializer = MarkdownSerializer()
        
        assert serializer.heading_offset == 0
        
        heading = Heading(level=1, text="Test")
        result = serializer.serialize_heading(heading)
        assert result == "# Test"
    
    def test_offset_boundary_values(self):
        """Test offset with boundary values."""
        # Test offset that brings H1 to H6
        serializer = MarkdownSerializer(heading_offset=5)
        heading = Heading(level=1, text="Test")
        result = serializer.serialize_heading(heading)
        assert result == "###### Test"
        
        # Test offset that brings H6 to H1
        serializer = MarkdownSerializer(heading_offset=-5)
        heading = Heading(level=6, text="Test")
        result = serializer.serialize_heading(heading)
        assert result == "# Test"
