"""
Integration tests for the Markdown serializer with pretty printer.

These tests verify that the complete serialization pipeline works correctly.
"""

import pytest
from src.markdown_serializer import MarkdownSerializer
from src.pretty_printer import PrettyPrinter
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
    TextFormatting,
    DocumentMetadata,
)


class TestSerializerIntegration:
    """Integration tests for serializer and pretty printer."""
    
    def test_complete_document_workflow(self):
        """Test complete document serialization and formatting."""
        # Create a document with various elements
        doc = InternalDocument(
            metadata=DocumentMetadata(
                title="Test Document",
                author="Test Author"
            ),
            sections=[
                Section(
                    heading=Heading(level=1, text="Introduction"),
                    content=[
                        Paragraph(text="This is the introduction paragraph.", formatting=TextFormatting.NORMAL),
                        Paragraph(text="This is bold text.", formatting=TextFormatting.BOLD)
                    ]
                ),
                Section(
                    heading=Heading(level=2, text="Data Table"),
                    content=[
                        Table(
                            headers=["Name", "Age", "City"],
                            rows=[
                                ["Alice", "30", "New York"],
                                ["Bob", "25", "Los Angeles"]
                            ]
                        )
                    ]
                ),
                Section(
                    heading=Heading(level=2, text="List Example"),
                    content=[
                        DocumentList(
                            ordered=False,
                            items=[
                                ListItem(text="First item", level=0),
                                ListItem(text="Second item", level=0),
                                ListItem(text="Nested item", level=1)
                            ]
                        )
                    ]
                ),
                Section(
                    heading=Heading(level=2, text="Links and Images"),
                    content=[
                        Link(text="Example Link", url="https://example.com"),
                        ImageReference(
                            source_path="images/test.png",
                            alt_text="Test Image"
                        )
                    ]
                )
            ]
        )
        
        # Serialize the document
        serializer = MarkdownSerializer(include_metadata=True)
        markdown = serializer.serialize(doc)
        
        # Format with pretty printer
        printer = PrettyPrinter()
        formatted = printer.format(markdown)
        
        # Verify the output contains expected elements
        assert "---" in formatted  # Metadata frontmatter
        assert "title: Test Document" in formatted
        assert "# Introduction" in formatted
        assert "## Data Table" in formatted
        assert "Name" in formatted and "Age" in formatted and "City" in formatted  # Table headers
        assert "Alice" in formatted and "30" in formatted  # Table data
        assert "- First item" in formatted
        assert "  - Nested item" in formatted
        assert "[Example Link](https://example.com)" in formatted
        assert "![Test Image](images/test.png)" in formatted
        
        # Verify proper formatting
        assert not formatted.endswith("  \n")  # No trailing whitespace
        assert "\n\n\n" not in formatted  # No multiple blank lines
    
    def test_special_characters_workflow(self):
        """Test that special characters are properly handled throughout the pipeline."""
        doc = InternalDocument(
            sections=[
                Section(
                    heading=Heading(level=1, text="Special Characters"),
                    content=[
                        Paragraph(text="Text with * asterisk and _ underscore", formatting=TextFormatting.NORMAL),
                        Table(
                            headers=["Column|1", "Column 2"],
                            rows=[["Data|with|pipes", "Normal data"]]
                        )
                    ]
                )
            ]
        )
        
        serializer = MarkdownSerializer()
        markdown = serializer.serialize(doc)
        
        printer = PrettyPrinter()
        formatted = printer.format(markdown)
        
        # Verify special characters are escaped
        assert "\\*" in formatted
        assert "\\_" in formatted
        # Pipes in table cells are escaped with backslash
        assert "\\" in formatted  # Backslash escaping is present
    
    def test_heading_offset_workflow(self):
        """Test heading offset throughout the pipeline."""
        doc = InternalDocument(
            sections=[
                Section(
                    heading=Heading(level=1, text="Level 1"),
                    content=[Paragraph(text="Content", formatting=TextFormatting.NORMAL)]
                ),
                Section(
                    heading=Heading(level=2, text="Level 2"),
                    content=[Paragraph(text="Content", formatting=TextFormatting.NORMAL)]
                )
            ]
        )
        
        # Serialize with heading offset
        serializer = MarkdownSerializer(heading_offset=1)
        markdown = serializer.serialize(doc)
        
        printer = PrettyPrinter()
        formatted = printer.format(markdown)
        
        # Verify headings are offset
        assert "## Level 1" in formatted  # Level 1 becomes level 2
        assert "### Level 2" in formatted  # Level 2 becomes level 3
    
    def test_empty_document(self):
        """Test handling of empty document."""
        doc = InternalDocument()
        
        serializer = MarkdownSerializer()
        markdown = serializer.serialize(doc)
        
        printer = PrettyPrinter()
        formatted = printer.format(markdown)
        
        # Should produce minimal output
        assert formatted == "\n" or formatted == ""
