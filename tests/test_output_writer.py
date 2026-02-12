"""Tests for OutputWriter class."""

import pytest
import sys
from io import StringIO
from pathlib import Path
from src.output_writer import OutputWriter


class TestOutputWriter:
    """Test suite for OutputWriter class."""
    
    def test_write_to_file_creates_file(self, tmp_path):
        """Test that write_to_file creates a file with correct content."""
        writer = OutputWriter()
        output_path = tmp_path / "output.md"
        content = "# Test Markdown\n\nThis is a test."
        
        writer.write_to_file(content, str(output_path))
        
        assert output_path.exists()
        assert output_path.read_text(encoding='utf-8') == content
    
    def test_write_to_file_creates_parent_directories(self, tmp_path):
        """Test that write_to_file creates parent directories if they don't exist."""
        writer = OutputWriter()
        output_path = tmp_path / "subdir" / "nested" / "output.md"
        content = "# Test"
        
        writer.write_to_file(content, str(output_path))
        
        assert output_path.exists()
        assert output_path.read_text(encoding='utf-8') == content
    
    def test_write_to_file_overwrites_existing(self, tmp_path):
        """Test that write_to_file overwrites existing files."""
        writer = OutputWriter()
        output_path = tmp_path / "output.md"
        
        # Write initial content
        output_path.write_text("Old content", encoding='utf-8')
        
        # Overwrite with new content
        new_content = "# New Content"
        writer.write_to_file(new_content, str(output_path))
        
        assert output_path.read_text(encoding='utf-8') == new_content
    
    def test_write_to_file_handles_utf8(self, tmp_path):
        """Test that write_to_file correctly handles UTF-8 content."""
        writer = OutputWriter()
        output_path = tmp_path / "output.md"
        content = "# 日本語テスト\n\n漢字、ひらがな、カタカナ"
        
        writer.write_to_file(content, str(output_path))
        
        assert output_path.read_text(encoding='utf-8') == content
    
    def test_write_to_file_raises_on_invalid_path(self):
        """Test that write_to_file raises IOError for invalid paths."""
        writer = OutputWriter()
        
        with pytest.raises(IOError):
            writer.write_to_file("content", "/invalid/path/that/cannot/exist/output.md")
    
    def test_write_to_stdout(self, capsys):
        """Test that write_to_stdout writes to stdout."""
        writer = OutputWriter()
        content = "# Test Output\n\nThis goes to stdout."
        
        writer.write_to_stdout(content)
        
        captured = capsys.readouterr()
        assert captured.out == content
    
    def test_write_to_stdout_with_special_chars(self, capsys):
        """Test that write_to_stdout handles special characters."""
        writer = OutputWriter()
        content = "# 日本語\n\n特殊文字: ©®™"
        
        writer.write_to_stdout(content)
        
        captured = capsys.readouterr()
        assert captured.out == content
    
    def test_preview_shows_all_lines_when_content_is_short(self, capsys):
        """Test that preview shows all lines when content is shorter than limit."""
        writer = OutputWriter()
        content = "Line 1\nLine 2\nLine 3"
        
        writer.preview(content, lines=50)
        
        captured = capsys.readouterr()
        assert "Line 1" in captured.out
        assert "Line 2" in captured.out
        assert "Line 3" in captured.out
        assert "PREVIEW" in captured.out
    
    def test_preview_truncates_long_content(self, capsys):
        """Test that preview truncates content longer than specified lines."""
        writer = OutputWriter()
        lines_list = [f"Line {i}" for i in range(100)]
        content = '\n'.join(lines_list)
        
        writer.preview(content, lines=10)
        
        captured = capsys.readouterr()
        assert "Line 0" in captured.out
        assert "Line 9" in captured.out
        assert "Line 10" not in captured.out
        assert "90 more lines not shown" in captured.out
    
    def test_preview_default_lines(self, capsys):
        """Test that preview uses default of 50 lines."""
        writer = OutputWriter()
        lines_list = [f"Line {i}" for i in range(100)]
        content = '\n'.join(lines_list)
        
        writer.preview(content)
        
        captured = capsys.readouterr()
        assert "Line 49" in captured.out
        assert "Line 50" not in captured.out
        assert "50 more lines not shown" in captured.out
    
    def test_preview_shows_separator_lines(self, capsys):
        """Test that preview shows separator lines."""
        writer = OutputWriter()
        content = "Test content"
        
        writer.preview(content, lines=10)
        
        captured = capsys.readouterr()
        assert "=" * 80 in captured.out
        assert "PREVIEW" in captured.out
