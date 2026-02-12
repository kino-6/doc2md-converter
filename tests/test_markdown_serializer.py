"""
Unit tests for the Markdown serializer.

These tests verify that the MarkdownSerializer correctly converts
internal document representations to valid Markdown format.
"""

import pytest
from src.markdown_serializer import MarkdownSerializer
from src.internal_representation import (
    InternalDocument,
    Section,
    Heading,
    Paragraph,
    Table,
    DocumentList,
    ListItem,
    ImageReference,
    Link,
    CodeBlock,
    TextFormatting,
    DocumentMetadata,
)


class TestMarkdownSerializer:
    """Test suite for MarkdownSerializer class."""
    
    def test_serialize_heading(self):
        """Test heading serialization."""
        serializer = MarkdownSerializer()
        
        heading = Heading(level=1, text="Test Heading")
        result = serializer.serialize_heading(heading)
        
        assert result == "# Test Heading"
    
    def test_serialize_heading_with_offset(self):
        """Test heading serialization with offset."""
        serializer = MarkdownSerializer(heading_offset=1)
        
        heading = Heading(level=1, text="Test Heading")
        result = serializer.serialize_heading(heading)
        
        assert result == "## Test Heading"
    
    def test_serialize_paragraph_normal(self):
        """Test normal paragraph serialization."""
        serializer = MarkdownSerializer()
        
        paragraph = Paragraph(text="This is a test paragraph.", formatting=TextFormatting.NORMAL)
        result = serializer.serialize_paragraph(paragraph)
        
        assert "This is a test paragraph." in result
    
    def test_serialize_paragraph_bold(self):
        """Test bold paragraph serialization."""
        serializer = MarkdownSerializer()
        
        paragraph = Paragraph(text="Bold text", formatting=TextFormatting.BOLD)
        result = serializer.serialize_paragraph(paragraph)
        
        assert result == "**Bold text**"
    
    def test_serialize_paragraph_italic(self):
        """Test italic paragraph serialization."""
        serializer = MarkdownSerializer()
        
        paragraph = Paragraph(text="Italic text", formatting=TextFormatting.ITALIC)
        result = serializer.serialize_paragraph(paragraph)
        
        assert result == "*Italic text*"
    
    def test_serialize_table(self):
        """Test table serialization."""
        serializer = MarkdownSerializer()
        
        table = Table(
            headers=["Name", "Age", "City"],
            rows=[
                ["Alice", "30", "NYC"],
                ["Bob", "25", "LA"]
            ]
        )
        result = serializer.serialize_table(table)
        
        assert "| Name | Age | City |" in result
        assert "| --- | --- | --- |" in result
        assert "| Alice | 30 | NYC |" in result
        assert "| Bob | 25 | LA |" in result
    
    def test_serialize_unordered_list(self):
        """Test unordered list serialization."""
        serializer = MarkdownSerializer()
        
        doc_list = DocumentList(
            ordered=False,
            items=[
                ListItem(text="First item", level=0),
                ListItem(text="Second item", level=0),
                ListItem(text="Nested item", level=1)
            ]
        )
        result = serializer.serialize_list(doc_list)
        
        assert "- First item" in result
        assert "- Second item" in result
        assert "  - Nested item" in result
    
    def test_serialize_ordered_list(self):
        """Test ordered list serialization."""
        serializer = MarkdownSerializer()
        
        doc_list = DocumentList(
            ordered=True,
            items=[
                ListItem(text="First item", level=0),
                ListItem(text="Second item", level=0)
            ]
        )
        result = serializer.serialize_list(doc_list)
        
        assert "1. First item" in result
        assert "2. Second item" in result
    
    def test_serialize_image(self):
        """Test image serialization."""
        serializer = MarkdownSerializer()
        
        image = ImageReference(
            source_path="images/test.png",
            alt_text="Test image"
        )
        result = serializer.serialize_image(image)
        
        assert result == "![Test image](images/test.png)"
    
    def test_serialize_image_with_ocr(self):
        """Test image serialization with OCR text."""
        serializer = MarkdownSerializer()
        
        image = ImageReference(
            source_path="images/test.png",
            alt_text="Test image",
            ocr_text="Extracted text"
        )
        result = serializer.serialize_image(image)
        
        assert "![Test image](images/test.png)" in result
        assert "*OCR extracted text: Extracted text*" in result
    
    def test_serialize_link(self):
        """Test link serialization."""
        serializer = MarkdownSerializer()
        
        link = Link(text="Click here", url="https://example.com")
        result = serializer.serialize_link(link)
        
        assert result == "[Click here](https://example.com)"
    
    def test_serialize_code_block(self):
        """Test code block serialization."""
        serializer = MarkdownSerializer()
        
        code = CodeBlock(code="print('Hello')", language="python")
        result = serializer.serialize_code_block(code)
        
        assert "```python" in result
        assert "print('Hello')" in result
        assert "```" in result
    
    def test_serialize_document(self):
        """Test full document serialization."""
        serializer = MarkdownSerializer()
        
        doc = InternalDocument(
            sections=[
                Section(
                    heading=Heading(level=1, text="Introduction"),
                    content=[
                        Paragraph(text="This is the introduction.", formatting=TextFormatting.NORMAL)
                    ]
                ),
                Section(
                    heading=Heading(level=2, text="Details"),
                    content=[
                        Paragraph(text="More details here.", formatting=TextFormatting.NORMAL)
                    ]
                )
            ]
        )
        result = serializer.serialize(doc)
        
        assert "# Introduction" in result
        assert "This is the introduction." in result
        assert "## Details" in result
        assert "More details here." in result
    
    def test_serialize_document_with_metadata(self):
        """Test document serialization with metadata."""
        serializer = MarkdownSerializer(include_metadata=True)
        
        doc = InternalDocument(
            metadata=DocumentMetadata(
                title="Test Document",
                author="Test Author",
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
        result = serializer.serialize(doc)
        
        assert "---" in result
        assert "title: Test Document" in result
        assert "author: Test Author" in result
        assert "source_format: docx" in result
        assert "# Content" in result
    
    def test_serialize_special_characters_in_text(self):
        """Test that special characters are properly escaped."""
        serializer = MarkdownSerializer()
        
        paragraph = Paragraph(text="Text with * and _ and #", formatting=TextFormatting.NORMAL)
        result = serializer.serialize_paragraph(paragraph)
        
        # Special characters should be escaped
        assert "\\" in result
    
    def test_serialize_special_characters_in_table(self):
        """Test that special characters in tables are properly escaped."""
        serializer = MarkdownSerializer()
        
        table = Table(
            headers=["Column|1", "Column 2"],
            rows=[["Data|1", "Data 2"]]
        )
        result = serializer.serialize_table(table)
        
        # Pipes should be escaped in table cells
        assert "\\|" in result
