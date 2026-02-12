"""
Internal document representation for the Document to Markdown Converter.

This module defines the data structures used to represent documents internally
before serialization to Markdown format. All document formats (Word, Excel, PDF)
are parsed into these common structures.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Union
from enum import Enum


class TextFormatting(Enum):
    """Text formatting options."""
    NORMAL = "normal"
    BOLD = "bold"
    ITALIC = "italic"
    BOLD_ITALIC = "bold_italic"
    CODE = "code"


@dataclass
class DocumentMetadata:
    """Metadata about the source document.
    
    Attributes:
        title: Document title
        author: Document author
        created_date: Document creation date
        modified_date: Document last modified date
        source_format: Original file format (docx, xlsx, pdf)
    """
    title: Optional[str] = None
    author: Optional[str] = None
    created_date: Optional[str] = None
    modified_date: Optional[str] = None
    source_format: Optional[str] = None


@dataclass
class Heading:
    """Represents a heading in the document.
    
    Attributes:
        level: Heading level (1-6, where 1 is the highest level)
        text: The heading text content
    """
    level: int
    text: str
    
    def __post_init__(self):
        """Validate heading level is within valid range."""
        if not 1 <= self.level <= 6:
            raise ValueError(f"Heading level must be between 1 and 6, got {self.level}")


@dataclass
class Paragraph:
    """Represents a paragraph of text.
    
    Attributes:
        text: The paragraph text content
        formatting: Text formatting style
    """
    text: str
    formatting: TextFormatting = TextFormatting.NORMAL


@dataclass
class Table:
    """Represents a table structure.
    
    Attributes:
        headers: List of column header names
        rows: List of rows, where each row is a list of cell values
    """
    headers: List[str]
    rows: List[List[str]]


@dataclass
class ListItem:
    """Represents a single item in a list.
    
    Attributes:
        text: The list item text content
        level: Indentation level (0 for top level, 1 for nested, etc.)
    """
    text: str
    level: int = 0


@dataclass
class DocumentList:
    """Represents a list (ordered or unordered).
    
    Attributes:
        ordered: True for ordered lists (numbered), False for unordered (bullets)
        items: List of list items
    """
    ordered: bool
    items: List[ListItem]


@dataclass
class ImageReference:
    """Represents a reference to an image in the document.
    
    Attributes:
        source_path: Original path or identifier of the image in the source document
        extracted_path: Path where the image was extracted to (if extracted)
        alt_text: Alternative text description for the image
        ocr_text: Text extracted from the image via OCR (if applicable)
        base64_data: Base64-encoded image data for embedding (if applicable)
        mime_type: MIME type of the image (e.g., 'image/png', 'image/jpeg')
        page_number: Page number where the image appears (for PDF documents)
    """
    source_path: str
    extracted_path: Optional[str] = None
    alt_text: Optional[str] = None
    ocr_text: Optional[str] = None
    base64_data: Optional[str] = None
    mime_type: Optional[str] = None
    page_number: Optional[int] = None


@dataclass
class Link:
    """Represents a hyperlink.
    
    Attributes:
        text: The link display text
        url: The link target URL
    """
    text: str
    url: str


@dataclass
class CodeBlock:
    """Represents a code block.
    
    Attributes:
        code: The code content
        language: Programming language for syntax highlighting (optional)
    """
    code: str
    language: Optional[str] = None


# Union type for all possible content block types
ContentBlock = Union[Paragraph, Table, DocumentList, ImageReference, Link, CodeBlock]


@dataclass
class Section:
    """Represents a section of the document.
    
    A section typically starts with a heading and contains various content blocks.
    
    Attributes:
        heading: Optional heading for this section
        content: List of content blocks in this section
    """
    heading: Optional[Heading] = None
    content: List[ContentBlock] = field(default_factory=list)


@dataclass
class InternalDocument:
    """Top-level internal representation of a document.
    
    This is the unified structure that all document parsers (Word, Excel, PDF)
    convert their input into, and that the Markdown serializer converts from.
    
    Attributes:
        metadata: Document metadata
        sections: List of document sections
        images: List of all image references in the document
    """
    metadata: DocumentMetadata = field(default_factory=DocumentMetadata)
    sections: List[Section] = field(default_factory=list)
    images: List[ImageReference] = field(default_factory=list)
