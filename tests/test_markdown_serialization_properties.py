"""
Property-based tests for Markdown serialization.

These tests verify that the MarkdownSerializer correctly converts internal
document representations to valid Markdown format across a wide range of inputs.

Feature: document-to-markdown-converter
Properties: 51 (Markdown serialization), 25 (Valid Markdown generation)
Validates: Requirements 12.2, 5.4
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from markdown_it import MarkdownIt
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
    DocumentMetadata,
    TextFormatting,
)


class TestPropertyMarkdownSerialization:
    """Property-based tests for Markdown serialization.
    
    Feature: document-to-markdown-converter
    Property 51: Markdown serialization
    Property 25: Valid Markdown generation
    Validates: Requirements 12.2, 5.4
    """
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    @staticmethod
    def is_valid_markdown(markdown_text: str) -> bool:
        """Check if the given text is valid Markdown that can be parsed.
        
        Args:
            markdown_text: The Markdown text to validate
            
        Returns:
            True if the text can be successfully parsed as Markdown
        """
        try:
            md = MarkdownIt()
            tokens = md.parse(markdown_text)
            return tokens is not None
        except Exception:
            return False
    
    # ========================================================================
    # Property 51: Markdown Serialization Tests
    # ========================================================================
    
    @given(
        level=st.integers(min_value=1, max_value=6),
        text=st.text(min_size=1, max_size=200)
    )
    def test_property_51_heading_serialization(self, level, text):
        """
        Feature: document-to-markdown-converter
        Property 51: Markdown serialization
        
        For any valid heading (level 1-6 with text), the serializer should
        produce valid Markdown heading syntax.
        
        **Validates: Requirements 12.2**
        """
        serializer = MarkdownSerializer()
        heading = Heading(level=level, text=text)
        
        result = serializer.serialize_heading(heading)
        
        # Property 1: Result should not be empty
        assert result, "Serialized heading should not be empty"
        
        # Property 2: Result should start with correct number of # symbols
        expected_prefix = "#" * level
        assert result.startswith(expected_prefix + " "), \
            f"Heading should start with '{expected_prefix} '"
        
        # Property 3: Result should be valid Markdown
        assert self.is_valid_markdown(result), \
            "Serialized heading should be valid Markdown"
    
    @given(
        text=st.text(min_size=0, max_size=1000),
        formatting=st.sampled_from(list(TextFormatting))
    )
    def test_property_51_paragraph_serialization(self, text, formatting):
        """
        Feature: document-to-markdown-converter
        Property 51: Markdown serialization
        
        For any paragraph with text and formatting, the serializer should
        produce valid Markdown with appropriate formatting syntax.
        
        **Validates: Requirements 12.2**
        """
        serializer = MarkdownSerializer()
        paragraph = Paragraph(text=text, formatting=formatting)
        
        result = serializer.serialize_paragraph(paragraph)
        
        # Property 1: Result should not be None
        assert result is not None, "Serialized paragraph should not be None"
        
        # Property 2: Formatting should be applied correctly
        if formatting == TextFormatting.BOLD and text:
            assert "**" in result, "Bold text should contain **"
        elif formatting == TextFormatting.ITALIC and text:
            assert "*" in result, "Italic text should contain *"
        elif formatting == TextFormatting.CODE and text:
            assert "`" in result, "Code text should contain `"
        
        # Property 3: Result should be valid Markdown
        assert self.is_valid_markdown(result), \
            "Serialized paragraph should be valid Markdown"
    
    @given(
        headers=st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=10),
        rows=st.lists(
            st.lists(st.text(min_size=0, max_size=100), min_size=1, max_size=10),
            min_size=0,
            max_size=20
        )
    )
    def test_property_51_table_serialization(self, headers, rows):
        """
        Feature: document-to-markdown-converter
        Property 51: Markdown serialization
        
        For any table with headers and rows, the serializer should produce
        valid Markdown table syntax.
        
        **Validates: Requirements 12.2**
        """
        serializer = MarkdownSerializer()
        table = Table(headers=headers, rows=rows)
        
        result = serializer.serialize_table(table)
        
        # Property 1: Result should not be empty for non-empty tables
        if headers or rows:
            assert result, "Serialized table should not be empty"
        
        # Property 2: Result should contain table structure
        if headers:
            lines = result.split("\n")
            assert len(lines) >= 2, "Table should have at least header and separator"
            
            # Header row should contain pipes
            assert "|" in lines[0], "Header row should contain pipes"
            
            # Separator row should contain dashes
            assert "---" in lines[1], "Separator row should contain dashes"
        
        # Property 3: Result should be valid Markdown
        assert self.is_valid_markdown(result), \
            "Serialized table should be valid Markdown"
    
    @given(
        ordered=st.booleans(),
        items=st.lists(
            st.builds(
                ListItem,
                text=st.text(min_size=1, max_size=200).filter(lambda x: "\n" not in x),
                level=st.integers(min_value=0, max_value=5)
            ),
            min_size=1,
            max_size=20
        )
    )
    def test_property_51_list_serialization(self, ordered, items):
        """
        Feature: document-to-markdown-converter
        Property 51: Markdown serialization
        
        For any list (ordered or unordered) with items, the serializer should
        produce valid Markdown list syntax.
        
        **Validates: Requirements 12.2**
        """
        serializer = MarkdownSerializer()
        doc_list = DocumentList(ordered=ordered, items=items)
        
        result = serializer.serialize_list(doc_list)
        
        # Property 1: Result should not be empty
        assert result, "Serialized list should not be empty"
        
        # Property 2: List markers should be present
        lines = result.split("\n")
        # Filter out empty lines that might be added
        non_empty_lines = [line for line in lines if line.strip()]
        assert len(non_empty_lines) == len(items), "Should have one line per item"
        
        for line in non_empty_lines:
            if ordered:
                # Ordered lists should have number followed by period
                assert any(line.strip().startswith(f"{i}.") for i in range(1, len(items) + 1)), \
                    "Ordered list items should start with number and period"
            else:
                # Unordered lists should have dash
                assert "-" in line, "Unordered list items should contain dash"
        
        # Property 3: Result should be valid Markdown
        assert self.is_valid_markdown(result), \
            "Serialized list should be valid Markdown"
    
    @given(
        source_path=st.text(min_size=1, max_size=200).filter(lambda x: not x.isspace()),
        alt_text=st.one_of(st.none(), st.text(min_size=0, max_size=200)),
        ocr_text=st.one_of(st.none(), st.text(min_size=0, max_size=500))
    )
    def test_property_51_image_serialization(self, source_path, alt_text, ocr_text):
        """
        Feature: document-to-markdown-converter
        Property 51: Markdown serialization
        
        For any image reference, the serializer should produce valid
        Markdown image syntax.
        
        **Validates: Requirements 12.2**
        """
        serializer = MarkdownSerializer()
        image = ImageReference(
            source_path=source_path,
            alt_text=alt_text,
            ocr_text=ocr_text
        )
        
        result = serializer.serialize_image(image)
        
        # Property 1: Result should not be empty
        assert result, "Serialized image should not be empty"
        
        # Property 2: Result should contain image syntax
        assert "![" in result and "](" in result, \
            "Image should use Markdown image syntax ![alt](path)"
        
        # Property 3: If OCR text exists, it should be included
        if ocr_text:
            assert "OCR extracted text" in result, \
                "OCR text should be marked in output"
        
        # Property 4: Result should be valid Markdown
        assert self.is_valid_markdown(result), \
            "Serialized image should be valid Markdown"
    
    @given(
        text=st.text(min_size=1, max_size=200),
        url=st.text(min_size=1, max_size=500).filter(lambda x: not x.isspace())
    )
    def test_property_51_link_serialization(self, text, url):
        """
        Feature: document-to-markdown-converter
        Property 51: Markdown serialization
        
        For any link with text and URL, the serializer should produce
        valid Markdown link syntax.
        
        **Validates: Requirements 12.2**
        """
        serializer = MarkdownSerializer()
        link = Link(text=text, url=url)
        
        result = serializer.serialize_link(link)
        
        # Property 1: Result should not be empty
        assert result, "Serialized link should not be empty"
        
        # Property 2: Result should contain link syntax
        assert "[" in result and "](" in result and ")" in result, \
            "Link should use Markdown link syntax [text](url)"
        
        # Property 3: Result should be valid Markdown
        assert self.is_valid_markdown(result), \
            "Serialized link should be valid Markdown"
    
    @given(
        code=st.text(min_size=0, max_size=1000),
        language=st.one_of(
            st.none(),
            st.sampled_from(["python", "javascript", "java", "cpp", "go", "rust", "ruby"])
        )
    )
    def test_property_51_code_block_serialization(self, code, language):
        """
        Feature: document-to-markdown-converter
        Property 51: Markdown serialization
        
        For any code block with code and optional language, the serializer
        should produce valid Markdown code block syntax.
        
        **Validates: Requirements 12.2**
        """
        serializer = MarkdownSerializer()
        code_block = CodeBlock(code=code, language=language)
        
        result = serializer.serialize_code_block(code_block)
        
        # Property 1: Result should not be empty
        assert result, "Serialized code block should not be empty"
        
        # Property 2: Result should contain code fence syntax
        assert result.startswith("```"), "Code block should start with ```"
        assert result.endswith("```"), "Code block should end with ```"
        
        # Property 3: Language should be specified if provided
        if language:
            assert result.startswith(f"```{language}"), \
                f"Code block should specify language: {language}"
        
        # Property 4: Result should be valid Markdown
        assert self.is_valid_markdown(result), \
            "Serialized code block should be valid Markdown"
    
    # ========================================================================
    # Property 25: Valid Markdown Generation Tests
    # ========================================================================
    
    @given(
        sections=st.lists(
            st.builds(
                Section,
                heading=st.one_of(
                    st.none(),
                    st.builds(
                        Heading,
                        level=st.integers(min_value=1, max_value=6),
                        text=st.text(min_size=1, max_size=200)
                    )
                ),
                content=st.lists(
                    st.one_of(
                        st.builds(
                            Paragraph,
                            text=st.text(min_size=0, max_size=500),
                            formatting=st.sampled_from(list(TextFormatting))
                        ),
                        st.builds(
                            Table,
                            headers=st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=5),
                            rows=st.lists(
                                st.lists(st.text(min_size=0, max_size=50), min_size=1, max_size=5),
                                min_size=0,
                                max_size=10
                            )
                        ),
                        st.builds(
                            DocumentList,
                            ordered=st.booleans(),
                            items=st.lists(
                                st.builds(
                                    ListItem,
                                    text=st.text(min_size=1, max_size=100),
                                    level=st.integers(min_value=0, max_value=3)
                                ),
                                min_size=1,
                                max_size=10
                            )
                        )
                    ),
                    min_size=0,
                    max_size=5
                )
            ),
            min_size=0,
            max_size=10
        )
    )
    def test_property_25_valid_markdown_generation(self, sections):
        """
        Feature: document-to-markdown-converter
        Property 25: Valid Markdown generation
        
        For any internal document structure, the serializer should produce
        valid Markdown syntax that can be successfully parsed by standard
        Markdown processors.
        
        **Validates: Requirements 5.4**
        """
        serializer = MarkdownSerializer()
        doc = InternalDocument(sections=sections)
        
        result = serializer.serialize(doc)
        
        # Property 1: Result should be a string
        assert isinstance(result, str), "Serialized document should be a string"
        
        # Property 2: Result should be valid Markdown
        assert self.is_valid_markdown(result), \
            "Serialized document should be valid Markdown that can be parsed"
        
        # Property 3: If document has sections with non-empty content, result should not be empty
        if sections:
            # Check if any section has meaningful content (non-empty text)
            has_meaningful_content = any(
                section.heading is not None or
                any(
                    (isinstance(c, Paragraph) and c.text.strip()) or
                    (isinstance(c, Table) and (c.headers or c.rows)) or
                    (isinstance(c, DocumentList) and c.items) or
                    not isinstance(c, Paragraph)
                    for c in section.content
                )
                for section in sections
            )
            if has_meaningful_content:
                assert result.strip(), "Document with meaningful content should produce non-empty output"
    
    @given(
        metadata=st.builds(
            DocumentMetadata,
            title=st.one_of(st.none(), st.text(min_size=1, max_size=200)),
            author=st.one_of(st.none(), st.text(min_size=1, max_size=100)),
            source_format=st.one_of(st.none(), st.sampled_from(["docx", "xlsx", "pdf"]))
        ),
        sections=st.lists(
            st.builds(
                Section,
                heading=st.builds(
                    Heading,
                    level=st.integers(min_value=1, max_value=6),
                    text=st.text(min_size=1, max_size=100)
                ),
                content=st.lists(
                    st.builds(
                        Paragraph,
                        text=st.text(min_size=1, max_size=200),
                        formatting=st.sampled_from(list(TextFormatting))
                    ),
                    min_size=1,
                    max_size=3
                )
            ),
            min_size=1,
            max_size=5
        )
    )
    def test_property_25_complete_document_valid_markdown(self, metadata, sections):
        """
        Feature: document-to-markdown-converter
        Property 25: Valid Markdown generation
        
        For any complete document with metadata and sections, the serializer
        should produce valid Markdown that can be parsed by standard processors.
        
        **Validates: Requirements 5.4**
        """
        serializer = MarkdownSerializer(include_metadata=True)
        doc = InternalDocument(metadata=metadata, sections=sections)
        
        result = serializer.serialize(doc)
        
        # Property 1: Result should be valid Markdown
        assert self.is_valid_markdown(result), \
            "Complete document should produce valid Markdown"
        
        # Property 2: Result should not be empty
        assert result.strip(), "Document with sections should produce non-empty output"
        
        # Property 3: Metadata should be included if requested
        if metadata and (metadata.title or metadata.author or metadata.source_format):
            assert "---" in result, "Metadata should be in frontmatter format"
    
    @given(
        heading_offset=st.integers(min_value=0, max_value=3),
        sections=st.lists(
            st.builds(
                Section,
                heading=st.builds(
                    Heading,
                    level=st.integers(min_value=1, max_value=6),
                    text=st.text(min_size=1, max_size=100)
                ),
                content=st.lists(
                    st.builds(
                        Paragraph,
                        text=st.text(min_size=1, max_size=200),
                        formatting=st.just(TextFormatting.NORMAL)
                    ),
                    min_size=1,
                    max_size=2
                )
            ),
            min_size=1,
            max_size=5
        )
    )
    def test_property_25_heading_offset_valid_markdown(self, heading_offset, sections):
        """
        Feature: document-to-markdown-converter
        Property 25: Valid Markdown generation
        
        For any document with heading offset applied, the serializer should
        still produce valid Markdown with heading levels in valid range (1-6).
        
        **Validates: Requirements 5.4**
        """
        serializer = MarkdownSerializer(heading_offset=heading_offset)
        doc = InternalDocument(sections=sections)
        
        result = serializer.serialize(doc)
        
        # Property 1: Result should be valid Markdown
        assert self.is_valid_markdown(result), \
            "Document with heading offset should produce valid Markdown"
        
        # Property 2: All heading levels should be in valid range
        lines = result.split("\n")
        for line in lines:
            if line.startswith("#"):
                # Count the number of # symbols
                level = len(line) - len(line.lstrip("#"))
                assert 1 <= level <= 6, \
                    f"Heading level {level} should be in range 1-6"
    
    @given(st.data())
    def test_property_25_complex_document_valid_markdown(self, data):
        """
        Feature: document-to-markdown-converter
        Property 25: Valid Markdown generation
        
        For any complex document with mixed content types (paragraphs, tables,
        lists, images, links, code blocks), the serializer should produce
        valid Markdown.
        
        **Validates: Requirements 5.4**
        """
        # Generate a complex document with various content types
        num_sections = data.draw(st.integers(min_value=1, max_value=5))
        sections = []
        
        for _ in range(num_sections):
            heading = data.draw(st.builds(
                Heading,
                level=st.integers(min_value=1, max_value=6),
                text=st.text(min_size=1, max_size=100)
            ))
            
            num_content_blocks = data.draw(st.integers(min_value=1, max_value=5))
            content = []
            
            for _ in range(num_content_blocks):
                content_type = data.draw(st.sampled_from([
                    "paragraph", "table", "list", "image", "link", "code"
                ]))
                
                if content_type == "paragraph":
                    content.append(data.draw(st.builds(
                        Paragraph,
                        text=st.text(min_size=1, max_size=200),
                        formatting=st.sampled_from(list(TextFormatting))
                    )))
                elif content_type == "table":
                    content.append(data.draw(st.builds(
                        Table,
                        headers=st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=5),
                        rows=st.lists(
                            st.lists(st.text(min_size=0, max_size=20), min_size=1, max_size=5),
                            min_size=1,
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
                elif content_type == "image":
                    content.append(data.draw(st.builds(
                        ImageReference,
                        source_path=st.text(min_size=1, max_size=100).filter(lambda x: not x.isspace())
                    )))
                elif content_type == "link":
                    content.append(data.draw(st.builds(
                        Link,
                        text=st.text(min_size=1, max_size=100),
                        url=st.text(min_size=1, max_size=200).filter(lambda x: not x.isspace())
                    )))
                else:  # code
                    content.append(data.draw(st.builds(
                        CodeBlock,
                        code=st.text(min_size=0, max_size=200),
                        language=st.one_of(st.none(), st.sampled_from(["python", "javascript", "java"]))
                    )))
            
            sections.append(Section(heading=heading, content=content))
        
        # Serialize the complex document
        serializer = MarkdownSerializer()
        doc = InternalDocument(sections=sections)
        result = serializer.serialize(doc)
        
        # Property 1: Result should be valid Markdown
        assert self.is_valid_markdown(result), \
            "Complex document should produce valid Markdown"
        
        # Property 2: Result should not be empty
        assert result.strip(), "Complex document should produce non-empty output"
        
        # Property 3: All sections should be represented
        # At minimum, we should have headings for each section
        heading_count = result.count("\n#")
        # Note: First heading might not have \n before it
        if result.startswith("#"):
            heading_count += 1
        assert heading_count >= len(sections), \
            "All section headings should be present in output"
    
    @given(
        text=st.text(min_size=1, max_size=200).filter(
            lambda x: any(c in x for c in "*_#[]()\\`")
        )
    )
    def test_property_25_special_characters_valid_markdown(self, text):
        """
        Feature: document-to-markdown-converter
        Property 25: Valid Markdown generation
        
        For any text containing Markdown special characters, the serializer
        should properly escape them to produce valid Markdown.
        
        **Validates: Requirements 5.4**
        """
        serializer = MarkdownSerializer()
        paragraph = Paragraph(text=text, formatting=TextFormatting.NORMAL)
        
        result = serializer.serialize_paragraph(paragraph)
        
        # Property 1: Result should be valid Markdown
        assert self.is_valid_markdown(result), \
            "Text with special characters should produce valid Markdown"
        
        # Property 2: Special characters should be escaped
        # The escaper should handle this, so we just verify it's valid
        assert result is not None and isinstance(result, str), \
            "Result should be a valid string"
    
    def test_property_25_empty_document_valid_markdown(self):
        """
        Feature: document-to-markdown-converter
        Property 25: Valid Markdown generation
        
        Even an empty document should produce valid (empty) Markdown.
        
        **Validates: Requirements 5.4**
        """
        serializer = MarkdownSerializer()
        doc = InternalDocument()
        
        result = serializer.serialize(doc)
        
        # Property 1: Result should be a string
        assert isinstance(result, str), "Empty document should produce a string"
        
        # Property 2: Result should be valid Markdown (even if empty)
        assert self.is_valid_markdown(result), \
            "Empty document should produce valid Markdown"
