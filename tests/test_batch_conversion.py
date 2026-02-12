"""Tests for batch conversion functionality."""

import tempfile
from pathlib import Path
import pytest
from docx import Document

from src.cli import main
from src.conversion_orchestrator import ConversionOrchestrator
from src.config import ConversionConfig
from src.logger import Logger, LogLevel


def create_test_docx(path: str, content: str):
    """Create a test Word document."""
    doc = Document()
    doc.add_paragraph(content)
    doc.save(path)


def test_batch_convert_multiple_files():
    """Test batch conversion of multiple files.
    
    Requirements: 6.5
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        file1 = Path(tmpdir) / "doc1.docx"
        file2 = Path(tmpdir) / "doc2.docx"
        file3 = Path(tmpdir) / "doc3.docx"
        
        create_test_docx(str(file1), "Content of document 1")
        create_test_docx(str(file2), "Content of document 2")
        create_test_docx(str(file3), "Content of document 3")
        
        # Create orchestrator
        config = ConversionConfig(
            input_path="",
            batch_mode=True,
            dry_run=True  # Don't write files
        )
        logger = Logger(log_level=LogLevel.INFO)
        orchestrator = ConversionOrchestrator(config=config, logger=logger)
        
        # Perform batch conversion
        results = orchestrator.batch_convert([str(file1), str(file2), str(file3)])
        
        # Verify results
        assert len(results) == 3
        assert all(r.success for r in results)
        assert all(r.markdown_content is not None for r in results)
        
        # Verify content
        assert "Content of document 1" in results[0].markdown_content
        assert "Content of document 2" in results[1].markdown_content
        assert "Content of document 3" in results[2].markdown_content


def test_batch_convert_with_failures():
    """Test batch conversion handles failures gracefully.
    
    Requirements: 6.5
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create one valid file and one invalid file
        valid_file = Path(tmpdir) / "valid.docx"
        invalid_file = Path(tmpdir) / "invalid.txt"
        
        create_test_docx(str(valid_file), "Valid content")
        invalid_file.write_text("Invalid content")
        
        # Create orchestrator
        config = ConversionConfig(
            input_path="",
            batch_mode=True,
            dry_run=True
        )
        logger = Logger(log_level=LogLevel.INFO)
        orchestrator = ConversionOrchestrator(config=config, logger=logger)
        
        # Perform batch conversion
        results = orchestrator.batch_convert([str(valid_file), str(invalid_file)])
        
        # Verify results
        assert len(results) == 2
        assert results[0].success is True
        assert results[1].success is False
        assert "Valid content" in results[0].markdown_content


def test_batch_convert_aggregates_results():
    """Test batch conversion aggregates results correctly.
    
    Requirements: 6.5
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files with different content
        files = []
        for i in range(5):
            file_path = Path(tmpdir) / f"doc{i}.docx"
            create_test_docx(str(file_path), f"Document {i} content")
            files.append(str(file_path))
        
        # Create orchestrator
        config = ConversionConfig(
            input_path="",
            batch_mode=True,
            dry_run=True
        )
        logger = Logger(log_level=LogLevel.INFO)
        orchestrator = ConversionOrchestrator(config=config, logger=logger)
        
        # Perform batch conversion
        results = orchestrator.batch_convert(files)
        
        # Verify aggregation
        assert len(results) == 5
        
        # Check each result has correct input path
        for i, result in enumerate(results):
            assert result.input_path == files[i]
            assert result.success is True
            assert f"Document {i} content" in result.markdown_content


def test_batch_convert_generates_output_paths():
    """Test batch conversion generates appropriate output paths.
    
    Requirements: 6.5
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        file1 = Path(tmpdir) / "document.docx"
        create_test_docx(str(file1), "Test content")
        
        # Create orchestrator
        config = ConversionConfig(
            input_path="",
            batch_mode=True,
            dry_run=False  # Actually generate output paths
        )
        logger = Logger(log_level=LogLevel.INFO)
        orchestrator = ConversionOrchestrator(config=config, logger=logger)
        
        # Perform batch conversion
        results = orchestrator.batch_convert([str(file1)])
        
        # Verify output path generation
        assert len(results) == 1
        assert results[0].output_path is not None
        assert results[0].output_path.endswith('.md')
        assert 'document.md' in results[0].output_path
