"""
Markdown serializer for converting internal document representation to Markdown format.

This module provides the MarkdownSerializer class that converts InternalDocument
structures into valid Markdown syntax.
"""

import re
from typing import List, Optional
from src.internal_representation import (
    InternalDocument,
    Section,
    ContentBlock,
    Heading,
    Paragraph,
    Table,
    DocumentList,
    ImageReference,
    Link,
    CodeBlock,
    TextFormatting,
)
from src.markdown_escaper import MarkdownEscaper


class MarkdownSerializer:
    """Converts internal document representation to Markdown format.
    
    This class handles the serialization of InternalDocument structures into
    valid Markdown syntax, including headings, paragraphs, lists, tables,
    images, and links.
    
    Attributes:
        heading_offset: Offset to apply to all heading levels (default: 0)
        include_metadata: Whether to include document metadata in output (default: False)
    """
    
    def __init__(self, heading_offset: int = 0, include_metadata: bool = False):
        """Initialize the Markdown serializer.
        
        Args:
            heading_offset: Offset to apply to all heading levels
            include_metadata: Whether to include document metadata in output
        """
        self.heading_offset = heading_offset
        self.include_metadata = include_metadata
    
    def serialize(self, document: InternalDocument) -> str:
        """Serialize an internal document to Markdown format.
        
        Args:
            document: The internal document to serialize
            
        Returns:
            Markdown-formatted string representation of the document
        """
        parts = []
        
        # Add metadata if requested
        if self.include_metadata and document.metadata:
            metadata_md = self._serialize_metadata(document.metadata)
            if metadata_md:
                parts.append(metadata_md)
                parts.append("")  # Blank line after metadata
        
        # Serialize each section
        for section in document.sections:
            section_md = self._serialize_section(section)
            if section_md:
                parts.append(section_md)
        
        return "\n".join(parts)
    
    def _serialize_metadata(self, metadata) -> str:
        """Serialize document metadata to Markdown frontmatter.
        
        Args:
            metadata: DocumentMetadata object
            
        Returns:
            Markdown frontmatter string (empty if no metadata fields are populated)
        """
        lines = []
        
        if metadata.title:
            lines.append(f"title: {metadata.title}")
        if metadata.author:
            lines.append(f"author: {metadata.author}")
        if metadata.created_date:
            lines.append(f"created: {metadata.created_date}")
        if metadata.modified_date:
            lines.append(f"modified: {metadata.modified_date}")
        if metadata.source_format:
            lines.append(f"source_format: {metadata.source_format}")
        
        # Only add frontmatter delimiters if there's actual metadata
        if lines:
            lines.insert(0, "---")
            lines.append("---")
            return "\n".join(lines)
        else:
            return ""
    
    def _serialize_section(self, section: Section) -> str:
        """Serialize a document section to Markdown.
        
        Args:
            section: Section object to serialize
            
        Returns:
            Markdown string representation of the section
        """
        parts = []
        
        # Add heading if present
        if section.heading:
            parts.append(self.serialize_heading(section.heading))
            parts.append("")  # Blank line after heading
        
        # Add content blocks
        for content in section.content:
            content_md = self._serialize_content_block(content)
            if content_md:
                parts.append(content_md)
                parts.append("")  # Blank line after content block
        
        # Remove trailing blank line
        while parts and parts[-1] == "":
            parts.pop()
        
        return "\n".join(parts)
    
    def _serialize_content_block(self, content: ContentBlock) -> str:
        """Serialize a content block to Markdown.
        
        Args:
            content: Content block to serialize
            
        Returns:
            Markdown string representation of the content
        """
        if isinstance(content, Paragraph):
            return self.serialize_paragraph(content)
        elif isinstance(content, Table):
            return self.serialize_table(content)
        elif isinstance(content, DocumentList):
            return self.serialize_list(content)
        elif isinstance(content, ImageReference):
            return self.serialize_image(content)
        elif isinstance(content, Link):
            return self.serialize_link(content)
        elif isinstance(content, CodeBlock):
            return self.serialize_code_block(content)
        else:
            return ""
    
    def serialize_heading(self, heading: Heading) -> str:
        """Serialize a heading to Markdown format.
        
        Args:
            heading: Heading object to serialize
            
        Returns:
            Markdown heading string (e.g., "## Heading Text")
        """
        # Apply heading offset and ensure level stays within valid range (1-6)
        level = max(1, min(6, heading.level + self.heading_offset))
        prefix = "#" * level
        # Escape special characters in heading text
        escaped_text = MarkdownEscaper.escape_text(heading.text, context="heading")
        return f"{prefix} {escaped_text}"
    
    def serialize_paragraph(self, paragraph: Paragraph) -> str:
        """Serialize a paragraph to Markdown format.
        
        Args:
            paragraph: Paragraph object to serialize
            
        Returns:
            Markdown paragraph string with appropriate formatting
        """
        text = paragraph.text
        
        # Escape special characters in normal text (but not in code)
        if paragraph.formatting != TextFormatting.CODE:
            text = MarkdownEscaper.escape_text(text, context="normal")
        
        # Apply formatting based on paragraph formatting type
        if paragraph.formatting == TextFormatting.BOLD:
            text = f"**{text}**"
        elif paragraph.formatting == TextFormatting.ITALIC:
            text = f"*{text}*"
        elif paragraph.formatting == TextFormatting.BOLD_ITALIC:
            text = f"***{text}***"
        elif paragraph.formatting == TextFormatting.CODE:
            # Code doesn't need escaping
            text = f"`{text}`"
        
        return text
    
    def serialize_table(self, table: Table) -> str:
        """Serialize a table to Markdown format.
        
        Args:
            table: Table object to serialize
            
        Returns:
            Markdown table string
        """
        if not table.headers and not table.rows:
            return ""
        
        lines = []
        
        # Add headers
        if table.headers:
            # Escape special characters in header cells
            escaped_headers = [MarkdownEscaper.escape_text(h, context="table") for h in table.headers]
            header_row = "| " + " | ".join(escaped_headers) + " |"
            lines.append(header_row)
            
            # Add separator row
            separator = "| " + " | ".join(["---"] * len(table.headers)) + " |"
            lines.append(separator)
        
        # Add data rows
        for row in table.rows:
            # Ensure row has same number of columns as headers
            if table.headers:
                row_data = row + [""] * (len(table.headers) - len(row))
                row_data = row_data[:len(table.headers)]
            else:
                row_data = row
            
            # Escape special characters in cells
            escaped_cells = [MarkdownEscaper.escape_text(str(cell), context="table") for cell in row_data]
            row_str = "| " + " | ".join(escaped_cells) + " |"
            lines.append(row_str)
        
        return "\n".join(lines)
    
    def serialize_list(self, doc_list: DocumentList) -> str:
        """Serialize a list to Markdown format.
        
        Args:
            doc_list: DocumentList object to serialize
            
        Returns:
            Markdown list string (ordered or unordered)
        """
        if not doc_list.items:
            return ""
        
        lines = []
        for i, item in enumerate(doc_list.items):
            indent = "  " * item.level
            
            if doc_list.ordered:
                prefix = f"{i + 1}."
            else:
                prefix = "-"
            
            # Escape special characters in list item text
            escaped_text = MarkdownEscaper.escape_text(item.text, context="normal")
            lines.append(f"{indent}{prefix} {escaped_text}")
        
        return "\n".join(lines)
    
    def serialize_image(self, image: ImageReference) -> str:
        """Serialize an image reference to Markdown format.
        
        Handles:
        - Base64 data URL embedding (when base64_data is available)
        - Relative path references (using extracted_path if available)
        - Placeholder comments for extraction failures
        - OCR text inclusion
        
        Args:
            image: ImageReference object to serialize
            
        Returns:
            Markdown image string (e.g., "![alt text](path)" or "![alt text](data:image/png;base64,...)") 
            or placeholder comment
        """
        # Check if we have base64 data for embedding
        if image.base64_data:
            # Use base64 data URL
            mime_type = image.mime_type or "image/png"
            data_url = f"data:{mime_type};base64,{image.base64_data}"
            
            # Use alt text if available, otherwise use empty string
            alt_text = image.alt_text if image.alt_text else ""
            # Escape special characters in alt text
            escaped_alt = MarkdownEscaper.escape_text(alt_text, context="link")
            
            # Add OCR text as additional context if available
            if image.ocr_text:
                escaped_ocr = MarkdownEscaper.escape_text(image.ocr_text, context="normal")
                return f"![{escaped_alt}]({data_url})\n\n*OCR extracted text: {escaped_ocr}*"
            
            return f"![{escaped_alt}]({data_url})"
        
        # Check if image extraction failed (no extracted_path and no valid source_path)
        if not image.extracted_path and not image.source_path:
            # Return placeholder comment for failed extraction
            alt_text = image.alt_text if image.alt_text else "Image"
            return f"<!-- Image extraction failed: {alt_text} -->"
        
        # Use extracted path (relative) if available, otherwise use source path
        path = image.extracted_path if image.extracted_path else image.source_path
        
        # If path is still None or empty, return placeholder
        if not path:
            alt_text = image.alt_text if image.alt_text else "Image"
            return f"<!-- Image extraction failed: {alt_text} -->"
        
        # Escape URL special characters
        escaped_path = MarkdownEscaper.escape_url(path)
        
        # Use alt text if available, otherwise use empty string
        alt_text = image.alt_text if image.alt_text else ""
        # Escape special characters in alt text
        escaped_alt = MarkdownEscaper.escape_text(alt_text, context="link")
        
        # Add OCR text as additional context if available
        if image.ocr_text:
            escaped_ocr = MarkdownEscaper.escape_text(image.ocr_text, context="normal")
            return f"![{escaped_alt}]({escaped_path})\n\n*OCR extracted text: {escaped_ocr}*"
        
        return f"![{escaped_alt}]({escaped_path})"
    
    def serialize_link(self, link: Link) -> str:
        """Serialize a hyperlink to Markdown format.
        
        Args:
            link: Link object to serialize
            
        Returns:
            Markdown link string (e.g., "[text](url)")
        """
        # Escape special characters in link text
        escaped_text = MarkdownEscaper.escape_text(link.text, context="link")
        # Escape URL special characters
        escaped_url = MarkdownEscaper.escape_url(link.url)
        return f"[{escaped_text}]({escaped_url})"
    
    def serialize_code_block(self, code_block: CodeBlock) -> str:
        """Serialize a code block to Markdown format.
        
        Args:
            code_block: CodeBlock object to serialize
            
        Returns:
            Markdown code block string with optional language specification
        """
        language = code_block.language if code_block.language else ""
        return f"```{language}\n{code_block.code}\n```"
