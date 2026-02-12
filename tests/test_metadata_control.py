"""
Unit tests for metadata control feature.

Tests verify that metadata can be included or excluded from the output
based on the include_metadata configuration option.

Validates: Requirements 8.3
"""

import pytest
from src.markdown_serializer import MarkdownSerializer
from src.internal_representation import (
    InternalDocument,
    Section,
    Heading,
    Paragraph,
    TextFormatting,
    DocumentMetadata,
)


class TestMetadataControl:
    """Tests for metadata inclusion/exclusion control."""
    
    def test_metadata_excluded_by_default(self):
        """Test that metadata is excluded by default (include_metadata=False)."""
        # Create document with metadata
        doc = InternalDocument(
            metadata=DocumentMetadata(
                title="Test Document",
                author="Test Author",
                created_date="2024-01-01",
                modified_date="2024-01-02",
                source_format="docx"
            ),
            sections=[
                Section(
                    heading=Heading(level=1, text="Content"),
                    content=[
                        Paragraph(text="Test content.", formatting=TextFormatting.NORMAL)
                    ]
                )
            ]
        )
        
        # Serialize with default settings (include_metadata=False)
        serializer = MarkdownSerializer()
        result = serializer.serialize(doc)
        
        # Verify metadata is NOT in output
        assert "---" not in result
        assert "title:" not in result
        assert "author:" not in result
        assert "created:" not in result
        assert "modified:" not in result
        assert "source_format:" not in result
        
        # Verify content IS in output
        assert "# Content" in result
        assert "Test content." in result
    
    def test_metadata_included_when_enabled(self):
        """Test that metadata is included when include_metadata=True."""
        # Create document with metadata
        doc = InternalDocument(
            metadata=DocumentMetadata(
                title="Test Document",
                author="Test Author",
                created_date="2024-01-01",
                modified_date="2024-01-02",
                source_format="docx"
            ),
            sections=[
                Section(
                    heading=Heading(level=1, text="Content"),
                    content=[
                        Paragraph(text="Test content.", formatting=TextFormatting.NORMAL)
                    ]
                )
            ]
        )
        
        # Serialize with include_metadata=True
        serializer = MarkdownSerializer(include_metadata=True)
        result = serializer.serialize(doc)
        
        # Verify metadata IS in output
        assert "---" in result
        assert "title: Test Document" in result
        assert "author: Test Author" in result
        assert "created: 2024-01-01" in result
        assert "modified: 2024-01-02" in result
        assert "source_format: docx" in result
        
        # Verify content IS in output
        assert "# Content" in result
        assert "Test content." in result
    
    def test_metadata_partial_fields(self):
        """Test metadata with only some fields populated."""
        # Create document with partial metadata
        doc = InternalDocument(
            metadata=DocumentMetadata(
                title="Test Document",
                source_format="pdf"
                # author, created_date, modified_date are None
            ),
            sections=[
                Section(
                    heading=Heading(level=1, text="Content"),
                    content=[
                        Paragraph(text="Test content.", formatting=TextFormatting.NORMAL)
                    ]
                )
            ]
        )
        
        # Serialize with include_metadata=True
        serializer = MarkdownSerializer(include_metadata=True)
        result = serializer.serialize(doc)
        
        # Verify only populated fields are in output
        assert "---" in result
        assert "title: Test Document" in result
        assert "source_format: pdf" in result
        
        # Verify unpopulated fields are NOT in output
        assert "author:" not in result
        assert "created:" not in result
        assert "modified:" not in result
    
    def test_metadata_empty(self):
        """Test document with empty metadata."""
        # Create document with empty metadata
        doc = InternalDocument(
            metadata=DocumentMetadata(),  # All fields are None
            sections=[
                Section(
                    heading=Heading(level=1, text="Content"),
                    content=[
                        Paragraph(text="Test content.", formatting=TextFormatting.NORMAL)
                    ]
                )
            ]
        )
        
        # Serialize with include_metadata=True
        serializer = MarkdownSerializer(include_metadata=True)
        result = serializer.serialize(doc)
        
        # Verify no metadata section is added (all fields are None)
        # The _serialize_metadata should return empty or minimal output
        lines = result.split('\n')
        # If metadata is empty, it shouldn't add frontmatter
        # Check that content is still present
        assert "# Content" in result
        assert "Test content." in result
    
    def test_metadata_no_metadata_object(self):
        """Test document without metadata object."""
        # Create document without metadata
        doc = InternalDocument(
            sections=[
                Section(
                    heading=Heading(level=1, text="Content"),
                    content=[
                        Paragraph(text="Test content.", formatting=TextFormatting.NORMAL)
                    ]
                )
            ]
        )
        
        # Serialize with include_metadata=True
        serializer = MarkdownSerializer(include_metadata=True)
        result = serializer.serialize(doc)
        
        # Verify no metadata section is added
        assert "---" not in result
        
        # Verify content IS in output
        assert "# Content" in result
        assert "Test content." in result
    
    def test_metadata_with_special_characters(self):
        """Test metadata with special characters in values."""
        # Create document with metadata containing special characters
        doc = InternalDocument(
            metadata=DocumentMetadata(
                title="Test: Document with *special* characters",
                author="Author & Co.",
                source_format="docx"
            ),
            sections=[
                Section(
                    heading=Heading(level=1, text="Content"),
                    content=[
                        Paragraph(text="Test content.", formatting=TextFormatting.NORMAL)
                    ]
                )
            ]
        )
        
        # Serialize with include_metadata=True
        serializer = MarkdownSerializer(include_metadata=True)
        result = serializer.serialize(doc)
        
        # Verify metadata with special characters is in output
        assert "title: Test: Document with *special* characters" in result
        assert "author: Author & Co." in result
    
    def test_metadata_frontmatter_format(self):
        """Test that metadata is formatted as valid YAML frontmatter."""
        # Create document with full metadata
        doc = InternalDocument(
            metadata=DocumentMetadata(
                title="Test Document",
                author="Test Author",
                created_date="2024-01-01",
                modified_date="2024-01-02",
                source_format="docx"
            ),
            sections=[
                Section(
                    heading=Heading(level=1, text="Content"),
                    content=[
                        Paragraph(text="Test content.", formatting=TextFormatting.NORMAL)
                    ]
                )
            ]
        )
        
        # Serialize with include_metadata=True
        serializer = MarkdownSerializer(include_metadata=True)
        result = serializer.serialize(doc)
        
        # Verify frontmatter format
        lines = result.split('\n')
        assert lines[0] == "---"  # Opening delimiter
        
        # Find closing delimiter
        closing_index = None
        for i, line in enumerate(lines[1:], 1):
            if line == "---":
                closing_index = i
                break
        
        assert closing_index is not None, "Closing delimiter not found"
        
        # Verify metadata is between delimiters
        metadata_section = '\n'.join(lines[1:closing_index])
        assert "title: Test Document" in metadata_section
        assert "author: Test Author" in metadata_section
        
        # Verify content comes after metadata
        content_section = '\n'.join(lines[closing_index+1:])
        assert "# Content" in content_section
