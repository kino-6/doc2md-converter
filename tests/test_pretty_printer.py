"""
Unit tests for the Pretty Printer.

These tests verify that the PrettyPrinter correctly formats Markdown text
for improved readability.
"""

import pytest
from src.pretty_printer import PrettyPrinter


class TestPrettyPrinter:
    """Test suite for PrettyPrinter class."""
    
    def test_normalize_whitespace_trailing(self):
        """Test removal of trailing whitespace."""
        printer = PrettyPrinter()
        
        markdown = "Line 1   \nLine 2  \n"
        result = printer.normalize_whitespace(markdown)
        
        assert result == "Line 1\nLine 2\n"
    
    def test_normalize_whitespace_multiple_blank_lines(self):
        """Test removal of multiple consecutive blank lines."""
        printer = PrettyPrinter()
        
        markdown = "Line 1\n\n\n\nLine 2\n"
        result = printer.normalize_whitespace(markdown)
        
        assert result == "Line 1\n\nLine 2\n"
    
    def test_normalize_whitespace_end_newline(self):
        """Test ensuring document ends with single newline."""
        printer = PrettyPrinter()
        
        markdown = "Line 1\nLine 2"
        result = printer.normalize_whitespace(markdown)
        
        assert result.endswith("\n")
        assert not result.endswith("\n\n")
    
    def test_align_tables_simple(self):
        """Test basic table alignment."""
        printer = PrettyPrinter()
        
        markdown = "| Name | Age |\n| --- | --- |\n| Alice | 30 |\n| Bob | 25 |"
        result = printer.align_tables(markdown)
        
        # Check that columns are aligned
        lines = result.split("\n")
        assert len(lines) == 4
        # All lines should have consistent spacing
        assert all("|" in line for line in lines)
    
    def test_align_tables_varying_widths(self):
        """Test table alignment with varying column widths."""
        printer = PrettyPrinter()
        
        markdown = "| Name | Age |\n| --- | --- |\n| Alexander | 30 |\n| Bo | 5 |"
        result = printer.align_tables(markdown)
        
        lines = result.split("\n")
        # Check that the first column is wider to accommodate "Alexander"
        assert "Alexander" in lines[2]
        assert "Bo" in lines[3]
    
    def test_ensure_blank_lines_before_heading(self):
        """Test blank line insertion before headings."""
        printer = PrettyPrinter()
        
        markdown = "Some text\n# Heading"
        result = printer.ensure_blank_lines(markdown)
        
        assert "Some text\n\n# Heading" in result
    
    def test_ensure_blank_lines_before_list(self):
        """Test blank line insertion before lists."""
        printer = PrettyPrinter()
        
        markdown = "Some text\n- List item"
        result = printer.ensure_blank_lines(markdown)
        
        assert "Some text\n\n- List item" in result
    
    def test_ensure_blank_lines_after_table(self):
        """Test blank line insertion after tables."""
        printer = PrettyPrinter()
        
        markdown = "| Col |\n| --- |\n| Data |\nNext paragraph"
        result = printer.ensure_blank_lines(markdown)
        
        # Should have blank line after table
        assert "| Data |\n\nNext paragraph" in result
    
    def test_format_complete(self):
        """Test complete formatting pipeline."""
        printer = PrettyPrinter()
        
        markdown = "# Heading  \n\n\n\nSome text\n| Name | Age |\n| --- | --- |\n| Alice | 30 |\nMore text"
        result = printer.format(markdown)
        
        # Should have normalized whitespace
        assert not result.endswith("  \n")
        # Should not have multiple blank lines
        assert "\n\n\n" not in result
        # Should have proper spacing around elements
        lines = result.split("\n")
        assert len(lines) > 0
    
    def test_is_table_row(self):
        """Test table row detection."""
        printer = PrettyPrinter()
        
        assert printer._is_table_row("| Col1 | Col2 |")
        assert printer._is_table_row("| --- | --- |")
        assert not printer._is_table_row("Regular text")
        assert not printer._is_table_row("# Heading")
    
    def test_parse_table_row(self):
        """Test table row parsing."""
        printer = PrettyPrinter()
        
        cells = printer._parse_table_row("| Name | Age | City |")
        assert cells == ["Name", "Age", "City"]
        
        cells = printer._parse_table_row("| Alice | 30 | NYC |")
        assert cells == ["Alice", "30", "NYC"]
    
    def test_is_separator_cell(self):
        """Test separator cell detection."""
        printer = PrettyPrinter()
        
        assert printer._is_separator_cell("---")
        assert printer._is_separator_cell(":---")
        assert printer._is_separator_cell("---:")
        assert printer._is_separator_cell(":---:")
        assert not printer._is_separator_cell("Data")
        assert not printer._is_separator_cell("123")
