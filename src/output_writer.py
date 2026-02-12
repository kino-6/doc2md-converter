"""Output writer for Markdown conversion results."""

import sys
from pathlib import Path
from typing import Optional


class OutputWriter:
    """Handles writing conversion output to various destinations."""
    
    def write_to_file(self, content: str, output_path: str, encoding: str = 'utf-8') -> None:
        """Write content to a file.
        
        Args:
            content: The Markdown content to write
            output_path: Path to the output file
            encoding: Character encoding for the output file (default: 'utf-8')
            
        Raises:
            IOError: If file cannot be written
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            # Handle encoding errors gracefully
            try:
                output_file.write_text(content, encoding=encoding)
            except (LookupError, UnicodeEncodeError) as enc_error:
                # If encoding fails, fall back to UTF-8 with error handling
                if encoding != 'utf-8':
                    # Try with error replacement
                    output_file.write_text(content, encoding=encoding, errors='replace')
                else:
                    raise enc_error
        except Exception as e:
            raise IOError(f"Failed to write to file {output_path}: {str(e)}") from e
    
    def write_to_stdout(self, content: str) -> None:
        """Write content to standard output.
        
        Args:
            content: The Markdown content to write
        """
        sys.stdout.write(content)
        sys.stdout.flush()
    
    def preview(self, content: str, lines: int = 50) -> None:
        """Display a preview of the content without saving to file.
        
        Args:
            content: The Markdown content to preview
            lines: Number of lines to display (default: 50)
        """
        content_lines = content.split('\n')
        preview_lines = content_lines[:lines]
        
        print("=" * 80)
        print(f"PREVIEW (showing first {lines} lines)")
        print("=" * 80)
        print('\n'.join(preview_lines))
        
        if len(content_lines) > lines:
            remaining = len(content_lines) - lines
            print("=" * 80)
            print(f"... {remaining} more lines not shown ...")
            print("=" * 80)
