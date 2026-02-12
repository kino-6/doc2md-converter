"""Tests for format routing functionality."""

import pytest

from src.format_router import FormatRouter
from src.file_validator import FileFormat
from src.parsers import WordParser, ExcelParser, PDFParser, DocumentParser


class TestFormatRouter:
    """Test suite for FormatRouter class."""
    
    def test_get_parser_for_docx(self):
        """Test that FormatRouter returns WordParser for DOCX format."""
        router = FormatRouter()
        parser = router.get_parser(FileFormat.DOCX)
        
        assert isinstance(parser, WordParser)
        assert isinstance(parser, DocumentParser)
    
    def test_get_parser_for_xlsx(self):
        """Test that FormatRouter returns ExcelParser for XLSX format."""
        router = FormatRouter()
        parser = router.get_parser(FileFormat.XLSX)
        
        assert isinstance(parser, ExcelParser)
        assert isinstance(parser, DocumentParser)
    
    def test_get_parser_for_pdf(self):
        """Test that FormatRouter returns PDFParser for PDF format."""
        router = FormatRouter()
        parser = router.get_parser(FileFormat.PDF)
        
        assert isinstance(parser, PDFParser)
        assert isinstance(parser, DocumentParser)
    
    def test_get_parser_for_unknown_format(self):
        """Test that FormatRouter raises ValueError for unknown format."""
        router = FormatRouter()
        
        with pytest.raises(ValueError) as exc_info:
            router.get_parser(FileFormat.UNKNOWN)
        
        assert "unsupported file format" in str(exc_info.value).lower()
    
    def test_get_parser_returns_same_instance(self):
        """Test that FormatRouter returns the same parser instance for repeated calls."""
        router = FormatRouter()
        
        parser1 = router.get_parser(FileFormat.DOCX)
        parser2 = router.get_parser(FileFormat.DOCX)
        
        # Should return the same instance
        assert parser1 is parser2
    
    def test_router_supports_all_valid_formats(self):
        """Test that FormatRouter supports all valid file formats."""
        router = FormatRouter()
        
        # Should not raise exceptions for valid formats
        router.get_parser(FileFormat.DOCX)
        router.get_parser(FileFormat.XLSX)
        router.get_parser(FileFormat.PDF)
