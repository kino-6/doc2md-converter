"""
Unit tests for the Markdown escaper.

These tests verify that special characters are properly escaped
in different Markdown contexts.
"""

import pytest
from src.markdown_escaper import MarkdownEscaper


class TestMarkdownEscaper:
    """Test suite for MarkdownEscaper class."""
    
    def test_escape_normal_text_asterisk(self):
        """Test escaping asterisks in normal text."""
        text = "Text with * asterisk"
        result = MarkdownEscaper.escape_text(text, context="normal")
        
        assert "\\*" in result
    
    def test_escape_normal_text_underscore(self):
        """Test escaping underscores in normal text."""
        text = "Text with _ underscore"
        result = MarkdownEscaper.escape_text(text, context="normal")
        
        assert "\\_" in result
    
    def test_escape_normal_text_hash(self):
        """Test escaping hash symbols in normal text."""
        text = "Text with # hash"
        result = MarkdownEscaper.escape_text(text, context="normal")
        
        assert "\\#" in result
    
    def test_escape_normal_text_backslash(self):
        """Test escaping backslashes in normal text."""
        text = "Text with \\ backslash"
        result = MarkdownEscaper.escape_text(text, context="normal")
        
        assert "\\\\" in result
    
    def test_escape_table_text_pipe(self):
        """Test escaping pipes in table cells."""
        text = "Data | with pipe"
        result = MarkdownEscaper.escape_text(text, context="table")
        
        assert "\\|" in result
    
    def test_escape_table_text_newline(self):
        """Test escaping newlines in table cells."""
        text = "Data\nwith newline"
        result = MarkdownEscaper.escape_text(text, context="table")
        
        assert "<br>" in result
        assert "\n" not in result
    
    def test_escape_link_text_brackets(self):
        """Test escaping brackets in link text."""
        text = "Link [with] brackets"
        result = MarkdownEscaper.escape_text(text, context="link")
        
        assert "\\[" in result
        assert "\\]" in result
    
    def test_escape_heading_text_leading_hash(self):
        """Test escaping leading hash in heading text."""
        text = "#NotAHeading"
        result = MarkdownEscaper.escape_text(text, context="heading")
        
        assert result.startswith("\\#")
    
    def test_escape_url_spaces(self):
        """Test escaping spaces in URLs."""
        url = "https://example.com/path with spaces"
        result = MarkdownEscaper.escape_url(url)
        
        assert "%20" in result
        assert " " not in result
    
    def test_escape_url_parentheses(self):
        """Test escaping parentheses in URLs."""
        url = "https://example.com/path(with)parens"
        result = MarkdownEscaper.escape_url(url)
        
        assert "%28" in result
        assert "%29" in result
    
    def test_escape_multiple_special_chars(self):
        """Test escaping multiple special characters."""
        text = "Text with * and _ and #"
        result = MarkdownEscaper.escape_text(text, context="normal")
        
        assert "\\*" in result
        assert "\\_" in result
        assert "\\#" in result
    
    def test_escape_empty_text(self):
        """Test escaping empty text."""
        result = MarkdownEscaper.escape_text("", context="normal")
        assert result == ""
    
    def test_escape_none_text(self):
        """Test escaping None text."""
        result = MarkdownEscaper.escape_text(None, context="normal")
        assert result is None
    
    def test_unescape_code(self):
        """Test that code text is not escaped."""
        text = "code with * and _"
        result = MarkdownEscaper.unescape_code(text)
        
        # Code should remain unchanged
        assert result == text
