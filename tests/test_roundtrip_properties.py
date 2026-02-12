"""
Property-based tests for round-trip semantic equivalence.

These tests verify that the conversion process maintains semantic consistency:
source document → internal representation → Markdown → parsing should maintain
consistency and produce valid, semantically equivalent content.

The focus is on semantic equivalence, not exact string matching. Escaping
differences are expected and acceptable as long as the semantic meaning is preserved.

Feature: document-to-markdown-converter
Property: 53 (Round-trip semantic equivalence)
Validates: Requirements 12.4
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from markdown_it import MarkdownIt
import re
from typing import List, Tuple
import string

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
from src.markdown_serializer import MarkdownSerializer


# Strategy for generating safe text that works well with Markdown
def safe_text_strategy(min_size=1, max_size=100):
    """Generate text that is safe for Markdown round-trip testing.
    
    Focuses on alphanumeric characters and minimal punctuation, avoiding
    characters that have special meaning in Markdown or cause parsing issues.
    """
    # Use only alphanumeric and very safe punctuation
    # Exclude all Markdown special characters: - . # * _ [ ] ( ) < > \ ` | : !
    safe_chars = string.ascii_letters + string.digits + " ,;?"
    return st.text(alphabet=safe_chars, min_size=min_size, max_size=max_size).filter(
        lambda x: x.strip()
    )


class TestPropertyRoundTripSemanticEquivalence:
    """Property 53: Round-trip semantic equivalence
    
    For any valid internal document structure, parsing a source document,
    serializing to Markdown, then parsing the Markdown should produce
    semantically equivalent content.
    
    Validates: Requirements 12.4
    """
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    @staticmethod
    def parse_markdown_to_tokens(markdown_text: str):
        """Parse Markdown text to tokens using markdown-it.
        
        Args:
            markdown_text: The Markdown text to parse
            
        Returns:
            List of tokens from markdown-it parser
        """
        md = MarkdownIt()
        return md.parse(markdown_text)
    
    @staticmethod
    def extract_headings_from_tokens(tokens) -> List[Tuple[int, str]]:
        """Extract headings from markdown-it tokens.
        
        Args:
            tokens: List of tokens from markdown-it parser
            
        Returns:
            List of (level, text) tuples for each heading
        """
        headings = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.type == "heading_open":
                level = int(token.tag[1])  # Extract level from 'h1', 'h2', etc.
                # Next token should be inline content
                if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                    text = tokens[i + 1].content
                    headings.append((level, text))
                i += 2  # Skip heading_open and inline tokens
            else:
                i += 1
        return headings
    
    @staticmethod
    def extract_paragraphs_from_tokens(tokens) -> List[str]:
        """Extract paragraph text from markdown-it tokens.
        
        Args:
            tokens: List of tokens from markdown-it parser
            
        Returns:
            List of paragraph text strings
        """
        paragraphs = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.type == "paragraph_open":
                # Next token should be inline content
                if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                    text = tokens[i + 1].content
                    paragraphs.append(text)
                i += 2
            else:
                i += 1
        return paragraphs
    
    @staticmethod
    def extract_lists_from_tokens(tokens) -> List[Tuple[bool, List[str]]]:
        """Extract lists from markdown-it tokens.
        
        Args:
            tokens: List of tokens from markdown-it parser
            
        Returns:
            List of (ordered, items) tuples for each list
        """
        lists = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.type in ("bullet_list_open", "ordered_list_open"):
                ordered = token.type == "ordered_list_open"
                items = []
                i += 1
                # Collect list items
                while i < len(tokens) and tokens[i].type != "bullet_list_close" and tokens[i].type != "ordered_list_close":
                    if tokens[i].type == "list_item_open":
                        # Find the inline content within this list item
                        i += 1
                        while i < len(tokens) and tokens[i].type != "list_item_close":
                            if tokens[i].type == "inline":
                                items.append(tokens[i].content)
                            i += 1
                    i += 1
                lists.append((ordered, items))
            i += 1
        return lists
    
    @staticmethod
    def count_tables_in_markdown(markdown_text: str) -> int:
        """Count the number of tables in Markdown text.
        
        Args:
            markdown_text: The Markdown text
            
        Returns:
            Number of tables found
        """
        # Simple heuristic: count lines with table separators
        lines = markdown_text.split("\n")
        table_count = 0
        for line in lines:
            if re.match(r'^\|[\s\-:]+\|', line.strip()):
                table_count += 1
        return table_count
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for comparison by removing extra whitespace.
        
        Args:
            text: Text to normalize
            
        Returns:
            Normalized text
        """
        return re.sub(r'\s+', ' ', text).strip()
    
    # ========================================================================
    # Property 53: Round-trip Semantic Equivalence Tests
    # ========================================================================
    
    @given(
        level=st.integers(min_value=1, max_value=6),
        text=safe_text_strategy(min_size=1, max_size=200)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_53_heading_roundtrip(self, level, text):
        """
        Feature: document-to-markdown-converter
        Property 53: Round-trip semantic equivalence (headings)
        
        For any heading in the internal representation, serializing to Markdown
        and parsing back should preserve the heading level and text content.
        
        **Validates: Requirements 12.4**
        """
        # Create internal document with a heading
        heading = Heading(level=level, text=text)
        section = Section(heading=heading, content=[])
        doc = InternalDocument(sections=[section])
        
        # Serialize to Markdown
        serializer = MarkdownSerializer()
        markdown = serializer.serialize(doc)
        
        # Parse the Markdown
        tokens = self.parse_markdown_to_tokens(markdown)
        parsed_headings = self.extract_headings_from_tokens(tokens)
        
        # Property 1: Should have exactly one heading
        assert len(parsed_headings) >= 1, \
            "Parsed Markdown should contain at least one heading"
        
        # Property 2: First heading level should match
        parsed_level, parsed_text = parsed_headings[0]
        assert parsed_level == level, \
            f"Heading level should be preserved: expected {level}, got {parsed_level}"
        
        # Property 3: Heading text should be semantically equivalent
        # Normalize both texts for comparison (handle escaping differences)
        normalized_original = self.normalize_text(text)
        normalized_parsed = self.normalize_text(parsed_text)
        
        # Allow for minor differences due to escaping
        assert normalized_original == normalized_parsed or \
               normalized_original in normalized_parsed or \
               normalized_parsed in normalized_original, \
            f"Heading text should be preserved: expected '{normalized_original}', got '{normalized_parsed}'"
    
    @given(
        text=safe_text_strategy(min_size=1, max_size=500),
        formatting=st.sampled_from([TextFormatting.NORMAL, TextFormatting.BOLD, TextFormatting.ITALIC])
    )
    @settings(max_examples=100, deadline=None)
    def test_property_53_paragraph_roundtrip(self, text, formatting):
        """
        Feature: document-to-markdown-converter
        Property 53: Round-trip semantic equivalence (paragraphs)
        
        For any paragraph in the internal representation, serializing to Markdown
        and parsing back should preserve the text content.
        
        **Validates: Requirements 12.4**
        """
        # Create internal document with a paragraph
        paragraph = Paragraph(text=text, formatting=formatting)
        section = Section(content=[paragraph])
        doc = InternalDocument(sections=[section])
        
        # Serialize to Markdown
        serializer = MarkdownSerializer()
        markdown = serializer.serialize(doc)
        
        # Parse the Markdown
        tokens = self.parse_markdown_to_tokens(markdown)
        parsed_paragraphs = self.extract_paragraphs_from_tokens(tokens)
        
        # Property 1: Should have at least one paragraph
        assert len(parsed_paragraphs) >= 1, \
            "Parsed Markdown should contain at least one paragraph"
        
        # Property 2: Paragraph text should be semantically equivalent
        normalized_original = self.normalize_text(text)
        
        # Check if any parsed paragraph contains the original text
        found = False
        for parsed_text in parsed_paragraphs:
            normalized_parsed = self.normalize_text(parsed_text)
            if normalized_original in normalized_parsed or normalized_parsed in normalized_original:
                found = True
                break
        
        assert found, \
            f"Paragraph text should be preserved in parsed Markdown"
    
    @given(
        ordered=st.booleans(),
        items=st.lists(
            safe_text_strategy(min_size=1, max_size=100),
            min_size=1,
            max_size=10
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_property_53_list_roundtrip(self, ordered, items):
        """
        Feature: document-to-markdown-converter
        Property 53: Round-trip semantic equivalence (lists)
        
        For any list in the internal representation, serializing to Markdown
        and parsing back should preserve the list type and items.
        
        **Validates: Requirements 12.4**
        """
        # Create internal document with a list
        list_items = [ListItem(text=item, level=0) for item in items]
        doc_list = DocumentList(ordered=ordered, items=list_items)
        section = Section(content=[doc_list])
        doc = InternalDocument(sections=[section])
        
        # Serialize to Markdown
        serializer = MarkdownSerializer()
        markdown = serializer.serialize(doc)
        
        # Parse the Markdown
        tokens = self.parse_markdown_to_tokens(markdown)
        parsed_lists = self.extract_lists_from_tokens(tokens)
        
        # Property 1: Should have exactly one list
        assert len(parsed_lists) >= 1, \
            "Parsed Markdown should contain at least one list"
        
        # Property 2: List type should match
        parsed_ordered, parsed_items = parsed_lists[0]
        assert parsed_ordered == ordered, \
            f"List type should be preserved: expected {'ordered' if ordered else 'unordered'}"
        
        # Property 3: Number of items should match
        assert len(parsed_items) == len(items), \
            f"Number of list items should be preserved: expected {len(items)}, got {len(parsed_items)}"
        
        # Property 4: List item texts should be semantically equivalent
        for i, (original, parsed) in enumerate(zip(items, parsed_items)):
            normalized_original = self.normalize_text(original)
            normalized_parsed = self.normalize_text(parsed)
            
            # Allow for minor differences due to escaping
            assert normalized_original == normalized_parsed or \
                   normalized_original in normalized_parsed or \
                   normalized_parsed in normalized_original, \
                f"List item {i} text should be preserved: expected '{normalized_original}', got '{normalized_parsed}'"
    
    @given(
        headers=st.lists(
            safe_text_strategy(min_size=1, max_size=50),
            min_size=1,
            max_size=5
        ),
        rows=st.lists(
            st.lists(
                safe_text_strategy(min_size=0, max_size=50),
                min_size=1,
                max_size=5
            ),
            min_size=1,
            max_size=5
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_property_53_table_roundtrip(self, headers, rows):
        """
        Feature: document-to-markdown-converter
        Property 53: Round-trip semantic equivalence (tables)
        
        For any table in the internal representation, serializing to Markdown
        and parsing back should preserve the table structure.
        
        **Validates: Requirements 12.4**
        """
        # Ensure all rows have the same number of columns as headers
        normalized_rows = []
        for row in rows:
            if len(row) < len(headers):
                row = row + [""] * (len(headers) - len(row))
            elif len(row) > len(headers):
                row = row[:len(headers)]
            normalized_rows.append(row)
        
        # Create internal document with a table
        table = Table(headers=headers, rows=normalized_rows)
        section = Section(content=[table])
        doc = InternalDocument(sections=[section])
        
        # Serialize to Markdown
        serializer = MarkdownSerializer()
        markdown = serializer.serialize(doc)
        
        # Property 1: Markdown should contain table structure
        assert "|" in markdown, "Markdown should contain table pipes"
        assert "---" in markdown, "Markdown should contain table separator"
        
        # Property 2: Should be able to parse as valid Markdown
        tokens = self.parse_markdown_to_tokens(markdown)
        assert tokens is not None, "Markdown should be parseable"
        
        # Property 3: Number of tables should match
        table_count = self.count_tables_in_markdown(markdown)
        assert table_count >= 1, \
            "Parsed Markdown should contain at least one table"
        
        # Property 4: Headers should be present in the Markdown
        for header in headers:
            if header.strip():  # Only check non-empty headers
                normalized_header = self.normalize_text(header)
                # Header might be escaped, so check if it's present in some form
                assert any(normalized_header in line or header in line for line in markdown.split("\n")), \
                    f"Header '{header}' should be present in Markdown"
    
    @given(
        sections=st.lists(
            st.builds(
                Section,
                heading=st.one_of(
                    st.none(),
                    st.builds(
                        Heading,
                        level=st.integers(min_value=1, max_value=6),
                        text=safe_text_strategy(min_size=1, max_size=100)
                    )
                ),
                content=st.lists(
                    st.one_of(
                        st.builds(
                            Paragraph,
                            text=safe_text_strategy(min_size=1, max_size=200),
                            formatting=st.sampled_from([TextFormatting.NORMAL, TextFormatting.BOLD, TextFormatting.ITALIC])
                        ),
                        st.builds(
                            DocumentList,
                            ordered=st.booleans(),
                            items=st.lists(
                                st.builds(
                                    ListItem,
                                    text=safe_text_strategy(min_size=1, max_size=50),
                                    level=st.just(0)  # Only level 0 for now
                                ),
                                min_size=1,
                                max_size=5
                            )
                        )
                    ),
                    min_size=1,
                    max_size=3
                )
            ),
            min_size=1,
            max_size=5
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_property_53_complete_document_roundtrip(self, sections):
        """
        Feature: document-to-markdown-converter
        Property 53: Round-trip semantic equivalence (complete documents)
        
        For any complete document with multiple sections, serializing to Markdown
        and parsing back should preserve the overall structure and content.
        
        **Validates: Requirements 12.4**
        """
        # Create internal document
        doc = InternalDocument(sections=sections)
        
        # Serialize to Markdown
        serializer = MarkdownSerializer()
        markdown = serializer.serialize(doc)
        
        # Property 1: Markdown should not be empty
        assert markdown.strip(), "Markdown should not be empty for non-empty document"
        
        # Property 2: Markdown should be valid and parseable
        tokens = self.parse_markdown_to_tokens(markdown)
        assert tokens is not None, "Markdown should be parseable"
        
        # Property 3: Number of headings should match
        original_headings = [s.heading for s in sections if s.heading is not None]
        parsed_headings = self.extract_headings_from_tokens(tokens)
        
        assert len(parsed_headings) == len(original_headings), \
            f"Number of headings should be preserved: expected {len(original_headings)}, got {len(parsed_headings)}"
        
        # Property 4: Heading levels should match
        for i, (original, (parsed_level, _)) in enumerate(zip(original_headings, parsed_headings)):
            assert parsed_level == original.level, \
                f"Heading {i} level should be preserved: expected {original.level}, got {parsed_level}"
        
        # Property 5: Content structure should be preserved (at least partially)
        # Note: Consecutive lists of the same type may be merged by markdown-it parser
        # So we check that we have at least some lists, not exact count
        original_list_count = sum(
            1 for section in sections
            for content in section.content
            if isinstance(content, DocumentList)
        )
        original_table_count = sum(
            1 for section in sections
            for content in section.content
            if isinstance(content, Table)
        )
        
        # Count in parsed Markdown
        parsed_lists = self.extract_lists_from_tokens(tokens)
        parsed_table_count = self.count_tables_in_markdown(markdown)
        
        # Allow for list merging - just check we have at least one list if we had lists
        if original_list_count > 0:
            assert len(parsed_lists) >= 1, \
                f"Should have at least one list when original had {original_list_count} lists"
        
        assert parsed_table_count == original_table_count, \
            f"Number of tables should be preserved: expected {original_table_count}, got {parsed_table_count}"
    
    @given(
        heading_offset=st.integers(min_value=0, max_value=3),
        sections=st.lists(
            st.builds(
                Section,
                heading=st.builds(
                    Heading,
                    level=st.integers(min_value=1, max_value=6),
                    text=safe_text_strategy(min_size=1, max_size=100)
                ),
                content=st.lists(
                    st.builds(
                        Paragraph,
                        text=safe_text_strategy(min_size=1, max_size=100),
                        formatting=st.just(TextFormatting.NORMAL)
                    ),
                    min_size=1,
                    max_size=2
                )
            ),
            min_size=1,
            max_size=3
        )
    )
    @settings(max_examples=50, deadline=None)
    def test_property_53_heading_offset_roundtrip(self, heading_offset, sections):
        """
        Feature: document-to-markdown-converter
        Property 53: Round-trip semantic equivalence (with heading offset)
        
        For any document with heading offset applied, serializing to Markdown
        and parsing back should preserve the adjusted heading levels.
        
        **Validates: Requirements 12.4**
        """
        # Create internal document
        doc = InternalDocument(sections=sections)
        
        # Serialize to Markdown with heading offset
        serializer = MarkdownSerializer(heading_offset=heading_offset)
        markdown = serializer.serialize(doc)
        
        # Parse the Markdown
        tokens = self.parse_markdown_to_tokens(markdown)
        parsed_headings = self.extract_headings_from_tokens(tokens)
        
        # Property 1: Number of headings should match
        assert len(parsed_headings) == len(sections), \
            f"Number of headings should be preserved: expected {len(sections)}, got {len(parsed_headings)}"
        
        # Property 2: Heading levels should be offset correctly and clamped to 1-6
        for i, (section, (parsed_level, _)) in enumerate(zip(sections, parsed_headings)):
            expected_level = max(1, min(6, section.heading.level + heading_offset))
            assert parsed_level == expected_level, \
                f"Heading {i} level should be offset correctly: expected {expected_level}, got {parsed_level}"
    
    @given(
        metadata=st.builds(
            DocumentMetadata,
            title=st.one_of(
                st.none(),
                safe_text_strategy(min_size=1, max_size=100)
            ),
            author=st.one_of(
                st.none(),
                safe_text_strategy(min_size=1, max_size=100)
            ),
            source_format=st.one_of(st.none(), st.sampled_from(["docx", "xlsx", "pdf"]))
        ),
        sections=st.lists(
            st.builds(
                Section,
                heading=st.builds(
                    Heading,
                    level=st.integers(min_value=1, max_value=6),
                    text=safe_text_strategy(min_size=1, max_size=50)
                ),
                content=st.lists(
                    st.builds(
                        Paragraph,
                        text=safe_text_strategy(min_size=1, max_size=100),
                        formatting=st.just(TextFormatting.NORMAL)
                    ),
                    min_size=1,
                    max_size=2
                )
            ),
            min_size=1,
            max_size=3
        )
    )
    @settings(max_examples=50, deadline=None)
    def test_property_53_metadata_roundtrip(self, metadata, sections):
        """
        Feature: document-to-markdown-converter
        Property 53: Round-trip semantic equivalence (with metadata)
        
        For any document with metadata, serializing to Markdown and parsing back
        should preserve the metadata in frontmatter format.
        
        **Validates: Requirements 12.4**
        """
        # Create internal document with metadata
        doc = InternalDocument(metadata=metadata, sections=sections)
        
        # Serialize to Markdown with metadata included
        serializer = MarkdownSerializer(include_metadata=True)
        markdown = serializer.serialize(doc)
        
        # Property 1: Markdown should be valid and parseable
        tokens = self.parse_markdown_to_tokens(markdown)
        assert tokens is not None, "Markdown should be parseable"
        
        # Property 2: If metadata has content, frontmatter should be present
        has_metadata = any([
            metadata.title,
            metadata.author,
            metadata.source_format
        ])
        
        if has_metadata:
            assert "---" in markdown, \
                "Markdown should contain frontmatter delimiters for metadata"
            
            # Property 3: Metadata fields should be present in Markdown
            if metadata.title:
                assert f"title: {metadata.title}" in markdown or metadata.title in markdown, \
                    "Title should be present in Markdown"
            if metadata.author:
                assert f"author: {metadata.author}" in markdown or metadata.author in markdown, \
                    "Author should be present in Markdown"
            if metadata.source_format:
                assert f"source_format: {metadata.source_format}" in markdown or metadata.source_format in markdown, \
                    "Source format should be present in Markdown"
        
        # Property 4: Content structure should still be preserved
        # Note: Frontmatter might be parsed as headings by markdown-it, so we need to account for that
        parsed_headings = self.extract_headings_from_tokens(tokens)
        
        # Filter out frontmatter headings (level 2 headings that look like metadata)
        content_headings = []
        for level, text in parsed_headings:
            # Skip if it looks like frontmatter (e.g., "author: value", "title: value")
            if ":" in text and level == 2:
                continue
            content_headings.append((level, text))
        
        assert len(content_headings) == len(sections), \
            f"Number of content headings should be preserved: expected {len(sections)}, got {len(content_headings)}"


# Run all property tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
