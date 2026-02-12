"""CLI tests for batch conversion functionality."""

import tempfile
from pathlib import Path
from click.testing import CliRunner
from docx import Document

from src.cli import main


def create_test_docx(path: str, content: str):
    """Create a test Word document."""
    doc = Document()
    doc.add_paragraph(content)
    doc.save(path)


def test_cli_batch_conversion():
    """Test CLI batch conversion with multiple input files.
    
    Requirements: 6.5
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        file1 = Path(tmpdir) / "doc1.docx"
        file2 = Path(tmpdir) / "doc2.docx"
        
        create_test_docx(str(file1), "Content 1")
        create_test_docx(str(file2), "Content 2")
        
        # Run CLI with multiple input files
        runner = CliRunner()
        result = runner.invoke(main, [
            '-i', str(file1),
            '-i', str(file2),
            '--dry-run'
        ])
        
        # Verify success
        assert result.exit_code == 0
        assert "Batch conversion complete" in result.output


def test_cli_batch_conversion_with_output_warning():
    """Test CLI batch conversion warns about ignored output path.
    
    Requirements: 6.5
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        file1 = Path(tmpdir) / "doc1.docx"
        file2 = Path(tmpdir) / "doc2.docx"
        output_file = Path(tmpdir) / "output.md"
        
        create_test_docx(str(file1), "Content 1")
        create_test_docx(str(file2), "Content 2")
        
        # Run CLI with multiple input files and output path
        runner = CliRunner()
        result = runner.invoke(main, [
            '-i', str(file1),
            '-i', str(file2),
            '-o', str(output_file),
            '--dry-run'
        ])
        
        # Verify warning about ignored output path
        assert "Output path ignored in batch mode" in result.output


def test_cli_single_file_still_works():
    """Test CLI single file conversion still works correctly.
    
    Requirements: 6.1
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test file
        file1 = Path(tmpdir) / "doc1.docx"
        create_test_docx(str(file1), "Content 1")
        
        # Run CLI with single input file
        runner = CliRunner()
        result = runner.invoke(main, [
            '-i', str(file1),
            '--dry-run'
        ])
        
        # Verify success (single file mode)
        assert result.exit_code == 0
        assert "Batch conversion" not in result.output
