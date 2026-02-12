"""
Tests for internal document representation data structures.
"""

import pytest
from hypothesis import given, strategies as st
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
    DocumentMetadata,
    TextFormatting,
)


class TestHeading:
    """Tests for Heading data class."""
    
    def test_heading_creation(self):
        """Test creating a valid heading."""
        heading = Heading(level=1, text="Test Heading")
        assert heading.level == 1
        assert heading.text == "Test Heading"
    
    def test_heading_level_validation(self):
        """Test that invalid heading levels raise ValueError."""
        with pytest.raises(ValueError):
            Heading(level=0, text="Invalid")
        
        with pytest.raises(ValueError):
            Heading(level=7, text="Invalid")
    
    def test_valid_heading_levels(self):
        """Test all valid heading levels (1-6)."""
        for level in range(1, 7):
            heading = Heading(level=level, text=f"Level {level}")
            assert heading.level == level


class TestParagraph:
    """Tests for Paragraph data class."""
    
    def test_paragraph_creation(self):
        """Test creating a paragraph."""
        para = Paragraph(text="Test paragraph")
        assert para.text == "Test paragraph"
        assert para.formatting == TextFormatting.NORMAL
    
    def test_paragraph_with_formatting(self):
        """Test creating a paragraph with formatting."""
        para = Paragraph(text="Bold text", formatting=TextFormatting.BOLD)
        assert para.formatting == TextFormatting.BOLD


class TestTable:
    """Tests for Table data class."""
    
    def test_table_creation(self):
        """Test creating a table."""
        table = Table(
            headers=["Name", "Age"],
            rows=[["Alice", "30"], ["Bob", "25"]]
        )
        assert len(table.headers) == 2
        assert len(table.rows) == 2
        assert table.rows[0] == ["Alice", "30"]


class TestDocumentList:
    """Tests for DocumentList data class."""
    
    def test_ordered_list_creation(self):
        """Test creating an ordered list."""
        items = [ListItem(text="First"), ListItem(text="Second")]
        lst = DocumentList(ordered=True, items=items)
        assert lst.ordered is True
        assert len(lst.items) == 2
    
    def test_unordered_list_creation(self):
        """Test creating an unordered list."""
        items = [ListItem(text="Item 1"), ListItem(text="Item 2")]
        lst = DocumentList(ordered=False, items=items)
        assert lst.ordered is False
    
    def test_nested_list_items(self):
        """Test list items with different nesting levels."""
        items = [
            ListItem(text="Top level", level=0),
            ListItem(text="Nested", level=1),
        ]
        lst = DocumentList(ordered=False, items=items)
        assert lst.items[0].level == 0
        assert lst.items[1].level == 1


class TestImageReference:
    """Tests for ImageReference data class."""
    
    def test_image_reference_creation(self):
        """Test creating an image reference."""
        img = ImageReference(source_path="image.png")
        assert img.source_path == "image.png"
        assert img.extracted_path is None
        assert img.alt_text is None
        assert img.ocr_text is None
    
    def test_image_reference_with_all_fields(self):
        """Test creating an image reference with all fields."""
        img = ImageReference(
            source_path="source.png",
            extracted_path="output/image_001.png",
            alt_text="A test image",
            ocr_text="Text from image"
        )
        assert img.extracted_path == "output/image_001.png"
        assert img.alt_text == "A test image"
        assert img.ocr_text == "Text from image"


class TestSection:
    """Tests for Section data class."""
    
    def test_section_creation(self):
        """Test creating a section."""
        heading = Heading(level=1, text="Section Title")
        para = Paragraph(text="Section content")
        section = Section(heading=heading, content=[para])
        
        assert section.heading == heading
        assert len(section.content) == 1
        assert section.content[0] == para
    
    def test_section_without_heading(self):
        """Test creating a section without a heading."""
        para = Paragraph(text="Content without heading")
        section = Section(content=[para])
        
        assert section.heading is None
        assert len(section.content) == 1


class TestInternalDocument:
    """Tests for InternalDocument data class."""
    
    def test_empty_document_creation(self):
        """Test creating an empty document."""
        doc = InternalDocument()
        assert doc.metadata is not None
        assert len(doc.sections) == 0
        assert len(doc.images) == 0
    
    def test_document_with_metadata(self):
        """Test creating a document with metadata."""
        metadata = DocumentMetadata(
            title="Test Document",
            author="Test Author",
            source_format="docx"
        )
        doc = InternalDocument(metadata=metadata)
        
        assert doc.metadata.title == "Test Document"
        assert doc.metadata.author == "Test Author"
        assert doc.metadata.source_format == "docx"
    
    def test_document_with_sections(self):
        """Test creating a document with sections."""
        section1 = Section(
            heading=Heading(level=1, text="Introduction"),
            content=[Paragraph(text="Intro text")]
        )
        section2 = Section(
            heading=Heading(level=1, text="Conclusion"),
            content=[Paragraph(text="Conclusion text")]
        )
        
        doc = InternalDocument(sections=[section1, section2])
        assert len(doc.sections) == 2
        assert doc.sections[0].heading.text == "Introduction"
        assert doc.sections[1].heading.text == "Conclusion"
    
    def test_document_with_images(self):
        """Test creating a document with image references."""
        img1 = ImageReference(source_path="img1.png")
        img2 = ImageReference(source_path="img2.png")
        
        doc = InternalDocument(images=[img1, img2])
        assert len(doc.images) == 2
        assert doc.images[0].source_path == "img1.png"


class TestComplexDocument:
    """Tests for complex document structures."""
    
    def test_document_with_mixed_content(self):
        """Test creating a document with various content types."""
        metadata = DocumentMetadata(title="Complex Doc", source_format="docx")
        
        section = Section(
            heading=Heading(level=1, text="Main Section"),
            content=[
                Paragraph(text="Introduction paragraph"),
                Table(headers=["Col1", "Col2"], rows=[["A", "B"]]),
                DocumentList(ordered=True, items=[ListItem(text="Item 1")]),
                ImageReference(source_path="diagram.png"),
            ]
        )
        
        doc = InternalDocument(
            metadata=metadata,
            sections=[section],
            images=[ImageReference(source_path="diagram.png")]
        )
        
        assert doc.metadata.title == "Complex Doc"
        assert len(doc.sections) == 1
        assert len(doc.sections[0].content) == 4
        assert isinstance(doc.sections[0].content[0], Paragraph)
        assert isinstance(doc.sections[0].content[1], Table)
        assert isinstance(doc.sections[0].content[2], DocumentList)
        assert isinstance(doc.sections[0].content[3], ImageReference)



# ============================================================================
# Property-Based Tests
# ============================================================================

class TestPropertyDocumentParsing:
    """Property-based tests for document parsing into internal representation.
    
    Feature: document-to-markdown-converter
    Property 50: Document parsing
    Validates: Requirements 12.1
    """
    
    # Custom strategies for generating valid document structures
    
    @staticmethod
    def text_formatting_strategy():
        """Strategy for generating text formatting options."""
        return st.sampled_from(list(TextFormatting))
    
    @staticmethod
    def heading_strategy():
        """Strategy for generating valid headings."""
        return st.builds(
            Heading,
            level=st.integers(min_value=1, max_value=6),
            text=st.text(min_size=1, max_size=200)
        )
    
    @staticmethod
    def paragraph_strategy():
        """Strategy for generating paragraphs."""
        return st.builds(
            Paragraph,
            text=st.text(min_size=0, max_size=1000),
            formatting=st.sampled_from(list(TextFormatting))
        )
    
    @staticmethod
    def table_strategy():
        """Strategy for generating tables."""
        return st.builds(
            Table,
            headers=st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=10),
            rows=st.lists(
                st.lists(st.text(min_size=0, max_size=100), min_size=1, max_size=10),
                min_size=0,
                max_size=20
            )
        )
    
    @staticmethod
    def list_item_strategy():
        """Strategy for generating list items."""
        return st.builds(
            ListItem,
            text=st.text(min_size=1, max_size=200),
            level=st.integers(min_value=0, max_value=5)
        )
    
    @staticmethod
    def document_list_strategy():
        """Strategy for generating document lists."""
        return st.builds(
            DocumentList,
            ordered=st.booleans(),
            items=st.lists(
                st.builds(
                    ListItem,
                    text=st.text(min_size=1, max_size=200),
                    level=st.integers(min_value=0, max_value=5)
                ),
                min_size=1,
                max_size=20
            )
        )
    
    @staticmethod
    def image_reference_strategy():
        """Strategy for generating image references."""
        return st.builds(
            ImageReference,
            source_path=st.text(min_size=1, max_size=200),
            extracted_path=st.one_of(st.none(), st.text(min_size=1, max_size=200)),
            alt_text=st.one_of(st.none(), st.text(min_size=0, max_size=200)),
            ocr_text=st.one_of(st.none(), st.text(min_size=0, max_size=500))
        )
    
    @staticmethod
    def link_strategy():
        """Strategy for generating links."""
        return st.builds(
            Link,
            text=st.text(min_size=1, max_size=200),
            url=st.text(min_size=1, max_size=500)
        )
    
    @staticmethod
    def code_block_strategy():
        """Strategy for generating code blocks."""
        return st.builds(
            CodeBlock,
            code=st.text(min_size=0, max_size=1000),
            language=st.one_of(st.none(), st.sampled_from(["python", "javascript", "java", "cpp", "go"]))
        )
    
    @staticmethod
    def content_block_strategy():
        """Strategy for generating any content block type."""
        return st.one_of(
            TestPropertyDocumentParsing.paragraph_strategy(),
            TestPropertyDocumentParsing.table_strategy(),
            TestPropertyDocumentParsing.document_list_strategy(),
            TestPropertyDocumentParsing.image_reference_strategy(),
            TestPropertyDocumentParsing.link_strategy(),
            TestPropertyDocumentParsing.code_block_strategy()
        )
    
    @staticmethod
    def section_strategy():
        """Strategy for generating sections."""
        return st.builds(
            Section,
            heading=st.one_of(st.none(), TestPropertyDocumentParsing.heading_strategy()),
            content=st.lists(
                TestPropertyDocumentParsing.content_block_strategy(),
                min_size=0,
                max_size=10
            )
        )
    
    @staticmethod
    def metadata_strategy():
        """Strategy for generating document metadata."""
        return st.builds(
            DocumentMetadata,
            title=st.one_of(st.none(), st.text(min_size=0, max_size=200)),
            author=st.one_of(st.none(), st.text(min_size=0, max_size=100)),
            created_date=st.one_of(st.none(), st.text(min_size=0, max_size=50)),
            modified_date=st.one_of(st.none(), st.text(min_size=0, max_size=50)),
            source_format=st.one_of(st.none(), st.sampled_from(["docx", "xlsx", "pdf"]))
        )
    
    @given(
        metadata=st.builds(
            DocumentMetadata,
            title=st.one_of(st.none(), st.text(min_size=0, max_size=200)),
            author=st.one_of(st.none(), st.text(min_size=0, max_size=100)),
            source_format=st.one_of(st.none(), st.sampled_from(["docx", "xlsx", "pdf"]))
        ),
        sections=st.lists(
            st.builds(
                Section,
                heading=st.one_of(st.none(), st.builds(
                    Heading,
                    level=st.integers(min_value=1, max_value=6),
                    text=st.text(min_size=1, max_size=200)
                )),
                content=st.lists(
                    st.one_of(
                        st.builds(
                            Paragraph,
                            text=st.text(min_size=0, max_size=1000),
                            formatting=st.sampled_from(list(TextFormatting))
                        ),
                        st.builds(
                            Table,
                            headers=st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=10),
                            rows=st.lists(
                                st.lists(st.text(min_size=0, max_size=100), min_size=1, max_size=10),
                                min_size=0,
                                max_size=20
                            )
                        ),
                        st.builds(
                            ImageReference,
                            source_path=st.text(min_size=1, max_size=200),
                            extracted_path=st.one_of(st.none(), st.text(min_size=1, max_size=200)),
                            alt_text=st.one_of(st.none(), st.text(min_size=0, max_size=200)),
                            ocr_text=st.one_of(st.none(), st.text(min_size=0, max_size=500))
                        )
                    ),
                    min_size=0,
                    max_size=10
                )
            ),
            min_size=0,
            max_size=10
        ),
        images=st.lists(
            st.builds(
                ImageReference,
                source_path=st.text(min_size=1, max_size=200),
                extracted_path=st.one_of(st.none(), st.text(min_size=1, max_size=200)),
                alt_text=st.one_of(st.none(), st.text(min_size=0, max_size=200)),
                ocr_text=st.one_of(st.none(), st.text(min_size=0, max_size=500))
            ),
            min_size=0,
            max_size=20
        )
    )
    def test_property_50_document_parsing(self, metadata, sections, images):
        """
        Feature: document-to-markdown-converter
        Property 50: Document parsing
        
        For any valid document structure components (metadata, sections, images),
        the InternalDocument should successfully parse and store them.
        
        Validates: Requirements 12.1
        """
        # Create an internal document with the generated components
        doc = InternalDocument(
            metadata=metadata,
            sections=sections,
            images=images
        )
        
        # Property 1: Document should be successfully created
        assert doc is not None
        assert isinstance(doc, InternalDocument)
        
        # Property 2: Metadata should be preserved
        assert doc.metadata == metadata
        
        # Property 3: All sections should be preserved
        assert len(doc.sections) == len(sections)
        for i, section in enumerate(sections):
            assert doc.sections[i] == section
        
        # Property 4: All images should be preserved
        assert len(doc.images) == len(images)
        for i, image in enumerate(images):
            assert doc.images[i] == image
        
        # Property 5: Document structure should be accessible
        # We should be able to iterate through sections
        for section in doc.sections:
            assert isinstance(section, Section)
            if section.heading is not None:
                assert isinstance(section.heading, Heading)
                assert 1 <= section.heading.level <= 6
            
            # We should be able to iterate through content blocks
            for content_block in section.content:
                assert content_block is not None
    
    @given(level=st.integers(min_value=1, max_value=6), text=st.text(min_size=1))
    def test_property_50_heading_parsing(self, level, text):
        """
        Feature: document-to-markdown-converter
        Property 50: Document parsing (Heading component)
        
        For any valid heading level (1-6) and text, a Heading should be successfully created.
        
        Validates: Requirements 12.1
        """
        heading = Heading(level=level, text=text)
        
        assert heading.level == level
        assert heading.text == text
        assert 1 <= heading.level <= 6
    
    @given(level=st.integers().filter(lambda x: x < 1 or x > 6), text=st.text())
    def test_property_50_invalid_heading_level_rejected(self, level, text):
        """
        Feature: document-to-markdown-converter
        Property 50: Document parsing (Invalid heading validation)
        
        For any invalid heading level (not 1-6), the parser should reject it.
        
        Validates: Requirements 12.1
        """
        with pytest.raises(ValueError):
            Heading(level=level, text=text)
    
    @given(
        text=st.text(min_size=0, max_size=1000),
        formatting=st.sampled_from(list(TextFormatting))
    )
    def test_property_50_paragraph_parsing(self, text, formatting):
        """
        Feature: document-to-markdown-converter
        Property 50: Document parsing (Paragraph component)
        
        For any text and formatting, a Paragraph should be successfully created.
        
        Validates: Requirements 12.1
        """
        para = Paragraph(text=text, formatting=formatting)
        
        assert para.text == text
        assert para.formatting == formatting
    
    @given(
        headers=st.lists(st.text(min_size=1), min_size=1, max_size=10),
        rows=st.lists(
            st.lists(st.text(min_size=0), min_size=1, max_size=10),
            min_size=0,
            max_size=20
        )
    )
    def test_property_50_table_parsing(self, headers, rows):
        """
        Feature: document-to-markdown-converter
        Property 50: Document parsing (Table component)
        
        For any valid table structure (headers and rows), a Table should be successfully created.
        
        Validates: Requirements 12.1
        """
        table = Table(headers=headers, rows=rows)
        
        assert table.headers == headers
        assert table.rows == rows
        assert len(table.headers) >= 1
    
    @given(
        ordered=st.booleans(),
        items=st.lists(
            st.builds(
                ListItem,
                text=st.text(min_size=1, max_size=200),
                level=st.integers(min_value=0, max_value=5)
            ),
            min_size=1,
            max_size=20
        )
    )
    def test_property_50_list_parsing(self, ordered, items):
        """
        Feature: document-to-markdown-converter
        Property 50: Document parsing (List component)
        
        For any list type (ordered/unordered) and items, a DocumentList should be successfully created.
        
        Validates: Requirements 12.1
        """
        doc_list = DocumentList(ordered=ordered, items=items)
        
        assert doc_list.ordered == ordered
        assert doc_list.items == items
        assert len(doc_list.items) >= 1
        
        # All items should have valid nesting levels
        for item in doc_list.items:
            assert item.level >= 0
    
    @given(
        source_path=st.text(min_size=1, max_size=200),
        extracted_path=st.one_of(st.none(), st.text(min_size=1, max_size=200)),
        alt_text=st.one_of(st.none(), st.text(min_size=0, max_size=200)),
        ocr_text=st.one_of(st.none(), st.text(min_size=0, max_size=500))
    )
    def test_property_50_image_reference_parsing(self, source_path, extracted_path, alt_text, ocr_text):
        """
        Feature: document-to-markdown-converter
        Property 50: Document parsing (Image reference component)
        
        For any image reference data, an ImageReference should be successfully created.
        
        Validates: Requirements 12.1
        """
        img = ImageReference(
            source_path=source_path,
            extracted_path=extracted_path,
            alt_text=alt_text,
            ocr_text=ocr_text
        )
        
        assert img.source_path == source_path
        assert img.extracted_path == extracted_path
        assert img.alt_text == alt_text
        assert img.ocr_text == ocr_text
    
    @given(
        sections=st.lists(
            st.builds(
                Section,
                heading=st.one_of(st.none(), st.builds(
                    Heading,
                    level=st.integers(min_value=1, max_value=6),
                    text=st.text(min_size=1, max_size=200)
                )),
                content=st.lists(
                    st.builds(
                        Paragraph,
                        text=st.text(min_size=0, max_size=500),
                        formatting=st.sampled_from(list(TextFormatting))
                    ),
                    min_size=0,
                    max_size=5
                )
            ),
            min_size=0,
            max_size=10
        )
    )
    def test_property_50_document_section_structure(self, sections):
        """
        Feature: document-to-markdown-converter
        Property 50: Document parsing (Section structure preservation)
        
        For any collection of sections, the document should preserve the section structure.
        
        Validates: Requirements 12.1
        """
        doc = InternalDocument(sections=sections)
        
        # The document should preserve all sections
        assert len(doc.sections) == len(sections)
        
        # Each section should maintain its structure
        for i, section in enumerate(sections):
            assert doc.sections[i].heading == section.heading
            assert len(doc.sections[i].content) == len(section.content)
            
            # If section has a heading, it should be valid
            if section.heading is not None:
                assert 1 <= section.heading.level <= 6
                assert len(section.heading.text) > 0
    
    @given(st.data())
    def test_property_50_complex_document_structure(self, data):
        """
        Feature: document-to-markdown-converter
        Property 50: Document parsing (Complex document structures)
        
        For any complex document with mixed content types, the parser should successfully
        create and preserve the entire structure.
        
        Validates: Requirements 12.1
        """
        # Generate a complex document with various content types
        metadata = data.draw(st.builds(
            DocumentMetadata,
            title=st.one_of(st.none(), st.text(min_size=1, max_size=100)),
            author=st.one_of(st.none(), st.text(min_size=1, max_size=100)),
            source_format=st.sampled_from(["docx", "xlsx", "pdf"])
        ))
        
        num_sections = data.draw(st.integers(min_value=1, max_value=5))
        sections = []
        
        for _ in range(num_sections):
            heading = data.draw(st.one_of(
                st.none(),
                st.builds(
                    Heading,
                    level=st.integers(min_value=1, max_value=6),
                    text=st.text(min_size=1, max_size=100)
                )
            ))
            
            num_content_blocks = data.draw(st.integers(min_value=0, max_value=5))
            content = []
            
            for _ in range(num_content_blocks):
                content_type = data.draw(st.sampled_from(["paragraph", "table", "list", "image"]))
                
                if content_type == "paragraph":
                    content.append(data.draw(st.builds(
                        Paragraph,
                        text=st.text(min_size=0, max_size=200),
                        formatting=st.sampled_from(list(TextFormatting))
                    )))
                elif content_type == "table":
                    content.append(data.draw(st.builds(
                        Table,
                        headers=st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=5),
                        rows=st.lists(
                            st.lists(st.text(min_size=0, max_size=20), min_size=1, max_size=5),
                            min_size=0,
                            max_size=5
                        )
                    )))
                elif content_type == "list":
                    content.append(data.draw(st.builds(
                        DocumentList,
                        ordered=st.booleans(),
                        items=st.lists(
                            st.builds(
                                ListItem,
                                text=st.text(min_size=1, max_size=100),
                                level=st.integers(min_value=0, max_value=3)
                            ),
                            min_size=1,
                            max_size=5
                        )
                    )))
                else:  # image
                    content.append(data.draw(st.builds(
                        ImageReference,
                        source_path=st.text(min_size=1, max_size=100)
                    )))
            
            sections.append(Section(heading=heading, content=content))
        
        # Create the document
        doc = InternalDocument(metadata=metadata, sections=sections)
        
        # Verify the document structure is preserved
        assert doc.metadata == metadata
        assert len(doc.sections) == len(sections)
        
        for i, section in enumerate(sections):
            assert doc.sections[i].heading == section.heading
            assert len(doc.sections[i].content) == len(section.content)
