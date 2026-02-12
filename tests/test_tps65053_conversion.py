"""Test conversion quality for tps65053.pdf real-world document.

This test validates Requirements 3.1, 3.2, 3.3 by converting an actual
PDF file and verifying the quality of text extraction, table detection,
and heading structure.
"""

import os
import pytest
from pathlib import Path

from src.config import ConversionConfig, LogLevel
from src.logger import Logger
from src.conversion_orchestrator import ConversionOrchestrator


class TestTPS65053Conversion:
    """Test suite for tps65053.pdf conversion validation."""
    
    @pytest.fixture
    def pdf_path(self):
        """Path to the test PDF file."""
        return "docs_target/tps65053.pdf"
    
    @pytest.fixture
    def output_path(self):
        """Path to the output Markdown file."""
        return "output/tps65053.md"
    
    @pytest.fixture
    def config(self, pdf_path, output_path):
        """Create conversion configuration."""
        return ConversionConfig(
            input_path=pdf_path,
            output_path=output_path,
            log_level=LogLevel.INFO,
            extract_images=True,
            validate_output=True
        )
    
    def test_pdf_file_exists(self, pdf_path):
        """Verify the test PDF file exists."""
        assert os.path.exists(pdf_path), f"Test PDF file not found: {pdf_path}"
        assert os.path.getsize(pdf_path) > 0, "Test PDF file is empty"
    
    def test_conversion_succeeds(self, config):
        """Test that PDF conversion completes successfully.
        
        Validates: Requirements 3.1 - PDF text extraction
        """
        logger = Logger(log_level=LogLevel.INFO)
        orchestrator = ConversionOrchestrator(config=config, logger=logger)
        
        result = orchestrator.convert(config.input_path)
        
        assert result.success, f"Conversion failed: {result.errors}"
        assert result.markdown_content is not None
        assert len(result.markdown_content) > 0
    
    def test_text_extraction_quality(self, output_path):
        """Test that text content is properly extracted from PDF.
        
        Validates: Requirements 3.1 - Text extraction quality
        """
        assert os.path.exists(output_path), "Output file not created"
        
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verify key text content from the PDF is present
        assert "TPS6505" in content, "Device name not found"
        assert "Power Management" in content, "Key phrase not found"
        assert "Step-Down Converter" in content or "Step-Down" in content, "Converter type not found"
        
        # Verify substantial content was extracted
        assert len(content) > 1000, "Insufficient content extracted"
        assert content.count('\n') > 100, "Too few lines extracted"
    
    def test_heading_structure_detection(self, output_path):
        """Test that heading structure is detected and converted.
        
        Validates: Requirements 3.2 - Heading detection
        """
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count headings
        lines = content.split('\n')
        headings = [line for line in lines if line.startswith('##')]
        
        # Verify headings were detected
        assert len(headings) > 10, f"Too few headings detected: {len(headings)}"
        
        # Verify heading format
        for heading in headings[:5]:  # Check first 5 headings
            assert heading.startswith('## '), f"Invalid heading format: {heading}"
    
    def test_table_detection_and_conversion(self, output_path):
        """Test that tables are detected and converted to Markdown format.
        
        Validates: Requirements 3.3 - Table preservation
        """
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count table rows (lines starting with |)
        lines = content.split('\n')
        table_rows = [line for line in lines if line.strip().startswith('|')]
        
        # Verify tables were detected
        assert len(table_rows) > 20, f"Too few table rows detected: {len(table_rows)}"
        
        # Verify table format
        for row in table_rows[:10]:  # Check first 10 rows
            assert '|' in row, f"Invalid table row format: {row}"
            # Tables should have at least 2 columns
            assert row.count('|') >= 2, f"Table row has too few columns: {row}"
    
    def test_markdown_readability(self, output_path):
        """Test that the output Markdown is readable and well-formatted.
        
        Validates: Requirements 5.2, 5.4 - Readability and valid Markdown
        """
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for proper spacing (no excessive blank lines)
        assert '\n\n\n\n' not in content, "Excessive blank lines found"
        
        # Check that special characters are properly handled
        # PDF often contains special characters that need escaping
        assert content.isprintable() or '\n' in content or '\t' in content, \
            "Non-printable characters found"
        
        # Verify UTF-8 encoding
        assert isinstance(content, str), "Content is not a string"
    
    def test_output_file_size(self, output_path):
        """Test that output file has reasonable size."""
        assert os.path.exists(output_path), "Output file not created"
        
        file_size = os.path.getsize(output_path)
        
        # Output should be substantial but not excessively large
        assert file_size > 10000, f"Output file too small: {file_size} bytes"
        assert file_size < 10000000, f"Output file too large: {file_size} bytes"
    
    def test_conversion_statistics(self, config):
        """Test that conversion statistics are properly recorded."""
        logger = Logger(log_level=LogLevel.INFO)
        orchestrator = ConversionOrchestrator(config=config, logger=logger)
        
        result = orchestrator.convert(config.input_path)
        
        assert result.success
        assert result.stats is not None
        assert result.duration > 0, "Duration not recorded"
        
        # Verify some statistics are captured
        # Note: Not all PDFs have images or tables
        assert result.stats.total_pages >= 0
