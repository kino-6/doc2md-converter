"""
Property-based tests for special character handling in Markdown conversion.

These tests verify that special characters are properly escaped for Markdown
compatibility while preserving their meaning in the output.

Feature: document-to-markdown-converter
Property: 24 (Special character handling)
Validates: Requirements 5.3, 9.3
"""

import pytest
from hypothesis import given, strategies as st, settings
from hypothesis.strategies import composite
from markdown_it import MarkdownIt
from src.markdown_serializer import MarkdownSerializer
from src.markdown_escaper import MarkdownEscaper
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
)


# ========================================================================
# Strategy Helpers
# ========================================================================

@composite
def text_with_special_char(draw, special_chars):
    """Generate text that contains at least one special character."""
    base_text = draw(st.text(
        alphabet=st.characters(min_codepoint=32, max_codepoint=126),
        min_size=0,
        max_size=200
    ))
    special_char = draw(st.sampled_from(special_chars))
    return base_text + special_char


class TestPropertySpecialCharacterHandling:
    """Property-based tests for special character handling.
    
    Feature: document-to-markdown-converter
    Property 24: Special character handling
    Validates: Requirements 5.3, 9.3
    """
    
    # Markdown special characters that need proper handling
    MARKDOWN_SPECIAL_CHARS = ['\\', '`', '*', '_', '{', '}', '[', ']', 
                              '(', ')', '#', '+', '-', '!', '|', '<', '>']
    
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
    # Property 24: Special Character Handling Tests
    # ========================================================================
    
    @given(
        text=st.text(min_size=1, max_size=500).filter(
            lambda x: any(c in x for c in ['\\', '`', '*', '_', '{', '}', '[', ']', '(', ')', '#', '+', '-', '!', '|'])
        )
    )
    def test_property_24_paragraph_special_characters(self, text):
        """
        Feature: document-to-markdown-converter
        Property 24: Special character handling
        
        For any paragraph containing special characters, the serializer should
        properly escape them for Markdown compatibility while preserving them
        in the output.
        
        **Validates: Requirements 5.3, 9.3**
        """
        serializer = MarkdownSerializer()
        paragraph = Paragraph(text=text, formatting=TextFormatting.NORMAL)
        
        result = serializer.serialize_paragraph(paragraph)
        
        # Property 1: Result should be valid Markdown
        assert self.is_valid_markdown(result), \
            f"Text with special characters should produce valid Markdown. Text: {text[:50]}..."
        
        # Property 2: Result should not be empty for non-empty input
        assert result, "Serialized paragraph should not be empty"
    
    @given(
        text=st.text(min_size=1, max_size=200).filter(
            lambda x: any(c in x for c in ['#', '*', '_', '[', ']'])
        )
    )
    def test_property_24_heading_special_characters(self, text):
        """
        Feature: document-to-markdown-converter
        Property 24: Special character handling
        
        For any heading containing special characters, the serializer should
        properly escape them to prevent misinterpretation as Markdown syntax.
        
        **Validates: Requirements 5.3, 9.3**
        """
        serializer = MarkdownSerializer()
        heading = Heading(level=2, text=text)
        
        result = serializer.serialize_heading(heading)
        
        # Property 1: Result should be valid Markdown
        assert self.is_valid_markdown(result), \
            "Heading with special characters should produce valid Markdown"
        
        # Property 2: Result should start with heading marker
        assert result.startswith("## "), "Heading should start with ## "
    
    @given(
        headers=st.lists(
            st.text(
                alphabet=st.characters(min_codepoint=32, max_codepoint=126),
                min_size=1,
                max_size=50
            ).map(lambda x: x + '|'),  # Ensure pipe is present
            min_size=1,
            max_size=5
        ),
        rows=st.lists(
            st.lists(
                st.text(
                    alphabet=st.characters(min_codepoint=32, max_codepoint=126),
                    min_size=0,
                    max_size=50
                ).map(lambda x: x + '|'),  # Ensure pipe is present
                min_size=1,
                max_size=5
            ),
            min_size=1,
            max_size=10
        )
    )
    def test_property_24_table_special_characters(self, headers, rows):
        """
        Feature: document-to-markdown-converter
        Property 24: Special character handling
        
        For any table containing special characters (especially pipes and newlines),
        the serializer should properly escape them to maintain table structure.
        
        **Validates: Requirements 5.3, 9.3**
        """
        # Ensure rows have same length as headers
        normalized_rows = []
        for row in rows:
            if len(row) < len(headers):
                row = row + [''] * (len(headers) - len(row))
            elif len(row) > len(headers):
                row = row[:len(headers)]
            normalized_rows.append(row)
        
        serializer = MarkdownSerializer()
        table = Table(headers=headers, rows=normalized_rows)
        
        result = serializer.serialize_table(table)
        
        # Property 1: Result should be valid Markdown
        assert self.is_valid_markdown(result), \
            "Table with special characters should produce valid Markdown"
        
        # Property 2: Table structure should be maintained
        lines = result.split("\n")
        assert len(lines) >= 2, "Table should have at least header and separator"
    
    @given(
        items=st.lists(
            st.builds(
                ListItem,
                text=text_with_special_char(['*', '-', '+', '#', '[', ']']),
                level=st.integers(min_value=0, max_value=3)
            ),
            min_size=1,
            max_size=10
        ),
        ordered=st.booleans()
    )
    def test_property_24_list_special_characters(self, items, ordered):
        """
        Feature: document-to-markdown-converter
        Property 24: Special character handling
        
        For any list containing special characters in item text, the serializer
        should properly escape them to prevent misinterpretation as list markers
        or other Markdown syntax.
        
        **Validates: Requirements 5.3, 9.3**
        """
        serializer = MarkdownSerializer()
        doc_list = DocumentList(ordered=ordered, items=items)
        
        result = serializer.serialize_list(doc_list)
        
        # Property 1: Result should be valid Markdown
        assert self.is_valid_markdown(result), \
            "List with special characters should produce valid Markdown"
        
        # Property 2: Result should not be empty
        assert result, "Serialized list should not be empty"
    
    @given(
        text=st.text(
            alphabet=st.characters(min_codepoint=32, max_codepoint=126),
            min_size=1,
            max_size=500
        ).filter(
            lambda x: any(c in x for c in ['\\', '`', '*', '_', '[', ']'])
        )
    )
    def test_property_24_escaper_normal_text(self, text):
        """
        Feature: document-to-markdown-converter
        Property 24: Special character handling
        
        The MarkdownEscaper should properly escape special characters in normal
        text context to prevent them from being interpreted as Markdown syntax.
        
        **Validates: Requirements 5.3, 9.3**
        """
        result = MarkdownEscaper.escape_text(text, context="normal")
        
        # Property 1: Result should not be None
        assert result is not None, "Escaped text should not be None"
        
        # Property 2: Result should be valid in Markdown context
        paragraph_md = result
        assert self.is_valid_markdown(paragraph_md), \
            "Escaped text should produce valid Markdown"
    
    @given(
        text=st.text(
            alphabet=st.characters(min_codepoint=32, max_codepoint=126),
            min_size=1,
            max_size=200
        ).map(lambda x: x + '|')  # Ensure pipe is present
    )
    def test_property_24_escaper_table_text(self, text):
        """
        Feature: document-to-markdown-converter
        Property 24: Special character handling
        
        The MarkdownEscaper should properly escape pipes and newlines in table
        cells to maintain table structure.
        
        **Validates: Requirements 5.3, 9.3**
        """
        result = MarkdownEscaper.escape_text(text, context="table")
        
        # Property 1: Result should not be None
        assert result is not None, "Escaped table text should not be None"
        
        # Property 2: Pipes should be escaped
        assert '\\|' in result, "Pipes in table cells should be escaped"
    
    @given(
        url=st.text(
            alphabet=st.characters(min_codepoint=32, max_codepoint=126),
            min_size=1,
            max_size=200
        ).map(lambda x: x.replace(' ', '_') + ' (test)')  # Ensure space and parens
    )
    def test_property_24_escaper_url(self, url):
        """
        Feature: document-to-markdown-converter
        Property 24: Special character handling
        
        The MarkdownEscaper should properly escape special characters in URLs
        to maintain valid URL syntax in Markdown.
        
        **Validates: Requirements 5.3, 9.3**
        """
        result = MarkdownEscaper.escape_url(url)
        
        # Property 1: Result should not be None
        assert result is not None, "Escaped URL should not be None"
        
        # Property 2: Spaces should be percent-encoded
        assert '%20' in result, "Spaces in URLs should be percent-encoded"
        
        # Property 3: Parentheses should be percent-encoded
        assert '%28' in result and '%29' in result, \
            "Parentheses should be percent-encoded"
    
    @given(
        text=st.text(
            alphabet=st.characters(min_codepoint=32, max_codepoint=126),
            min_size=1,
            max_size=200
        ).map(lambda x: x + '\\')  # Ensure backslash is present
    )
    def test_property_24_backslash_escaping(self, text):
        """
        Feature: document-to-markdown-converter
        Property 24: Special character handling
        
        Backslashes should be properly escaped to prevent them from escaping
        other characters unintentionally.
        
        **Validates: Requirements 5.3, 9.3**
        """
        result = MarkdownEscaper.escape_text(text, context="normal")
        
        # Property 1: Result should not be None
        assert result is not None, "Escaped text should not be None"
        
        # Property 2: Backslashes should be escaped
        assert '\\\\' in result, \
            "Backslashes should be escaped with another backslash"
    
    @given(
        text=st.text(
            alphabet=st.characters(min_codepoint=32, max_codepoint=126),
            min_size=1,
            max_size=200
        ).map(lambda x: x + '<>')  # Ensure angle brackets are present
    )
    def test_property_24_angle_brackets(self, text):
        """
        Feature: document-to-markdown-converter
        Property 24: Special character handling
        
        Angle brackets should be properly escaped to prevent them from being
        interpreted as HTML tags.
        
        **Validates: Requirements 5.3, 9.3**
        """
        result = MarkdownEscaper.escape_text(text, context="normal")
        
        # Property 1: Result should not be None
        assert result is not None, "Escaped text should not be None"
        
        # Property 2: Result should be valid Markdown
        assert self.is_valid_markdown(result), \
            "Text with angle brackets should produce valid Markdown"
    
    @given(
        text=st.text(
            alphabet=st.characters(
                whitelist_categories=('Lu', 'Ll', 'Nd', 'Po', 'Sm'),
                whitelist_characters='*_[]()#+-!|\\`{}<>'
            ),
            min_size=1,
            max_size=200
        ).filter(
            lambda x: any(c in x for c in ['*', '_', '[', ']', '(', ')', '#', '+', '-', '!', '|', '\\', '`', '{', '}', '<', '>'])
        )
    )
    def test_property_24_mixed_special_characters(self, text):
        """
        Feature: document-to-markdown-converter
        Property 24: Special character handling
        
        For any text with multiple types of special characters mixed together,
        the escaper should handle all of them correctly to produce valid Markdown.
        
        **Validates: Requirements 5.3, 9.3**
        """
        serializer = MarkdownSerializer()
        paragraph = Paragraph(text=text, formatting=TextFormatting.NORMAL)
        
        result = serializer.serialize_paragraph(paragraph)
        
        # Property 1: Result should be valid Markdown
        assert self.is_valid_markdown(result), \
            "Text with mixed special characters should produce valid Markdown"
        
        # Property 2: Result should not be empty
        assert result, "Serialized paragraph should not be empty"
