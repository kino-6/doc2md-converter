"""Format routing module for the Document to Markdown Converter.

This module provides the FormatRouter class which selects the appropriate
parser based on the file format.
"""

from src.file_validator import FileFormat
from src.parsers import DocumentParser, WordParser, ExcelParser, PDFParser


class FormatRouter:
    """Routes files to appropriate parsers based on format.
    
    The FormatRouter maintains a mapping of file formats to their
    corresponding parser implementations and returns the appropriate
    parser for a given file format.
    """
    
    def __init__(self, logger=None):
        """Initialize FormatRouter with parser mappings.
        
        Args:
            logger: Optional logger to pass to parsers for encoding warnings
        """
        self.logger = logger
        self._parsers = {
            FileFormat.DOCX: WordParser(logger=logger),
            FileFormat.XLSX: ExcelParser(logger=logger),
            FileFormat.PDF: PDFParser(logger=logger)
        }
    
    def get_parser(self, file_format: FileFormat) -> DocumentParser:
        """Get the appropriate parser for a file format.
        
        Args:
            file_format: The file format to get a parser for
            
        Returns:
            DocumentParser instance for the specified format
            
        Raises:
            ValueError: If the file format is not supported
        """
        if file_format not in self._parsers:
            raise ValueError(
                f"Unsupported file format: {file_format}. "
                f"Supported formats: {', '.join(f.value for f in self._parsers.keys())}"
            )
        
        return self._parsers[file_format]
