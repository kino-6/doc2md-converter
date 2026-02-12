"""
Markdown special character escaping utilities.

This module provides functions to properly escape special characters
in Markdown text to ensure valid Markdown output.
"""

import re


class MarkdownEscaper:
    """Handles escaping of special characters in Markdown text.
    
    This class provides methods to escape Markdown special characters
    to prevent them from being interpreted as Markdown syntax.
    """
    
    # Markdown special characters that need escaping in regular text
    SPECIAL_CHARS = r'\`*_{}[]()#+-.!|'
    
    # Characters that need escaping in table cells
    TABLE_SPECIAL_CHARS = r'\`*_{}[]()#+-.!|'
    
    @staticmethod
    def escape_text(text: str, context: str = "normal") -> str:
        """Escape special characters in text based on context.
        
        Args:
            text: Text to escape
            context: Context where the text appears ("normal", "table", "link", "heading")
            
        Returns:
            Text with special characters escaped
        """
        if not text:
            return text
        
        if context == "table":
            return MarkdownEscaper._escape_table_text(text)
        elif context == "link":
            return MarkdownEscaper._escape_link_text(text)
        elif context == "heading":
            return MarkdownEscaper._escape_heading_text(text)
        else:
            return MarkdownEscaper._escape_normal_text(text)
    
    @staticmethod
    def _escape_normal_text(text: str) -> str:
        """Escape special characters in normal paragraph text.
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text
        """
        # Escape backslashes first to avoid double-escaping
        text = text.replace("\\", "\\\\")
        
        # Escape other special characters
        # Note: We don't escape periods (.) as they're commonly used in normal text
        special_chars = ['`', '*', '_', '{', '}', '[', ']', '(', ')', 
                        '#', '+', '-', '!', '|', '<', '>']
        
        for char in special_chars:
            # Only escape if not already escaped
            text = re.sub(f'(?<!\\\\){re.escape(char)}', f'\\{char}', text)
        
        return text
    
    @staticmethod
    def _escape_table_text(text: str) -> str:
        """Escape special characters in table cells.
        
        In tables, we need to be especially careful with pipes (|)
        as they are used as column separators.
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text
        """
        # Escape backslashes first
        text = text.replace("\\", "\\\\")
        
        # Escape pipe character (critical for tables)
        text = text.replace("|", "\\|")
        
        # Escape newlines in table cells (replace with <br>)
        text = text.replace("\n", "<br>")
        
        return text
    
    @staticmethod
    def _escape_link_text(text: str) -> str:
        """Escape special characters in link text.
        
        Args:
            text: Link text to escape
            
        Returns:
            Escaped text
        """
        # In link text, we need to escape brackets
        text = text.replace("\\", "\\\\")
        text = text.replace("[", "\\[")
        text = text.replace("]", "\\]")
        
        return text
    
    @staticmethod
    def _escape_heading_text(text: str) -> str:
        """Escape special characters in heading text.
        
        Headings have fewer restrictions, but we still need to handle
        some special cases.
        
        Args:
            text: Heading text to escape
            
        Returns:
            Escaped text
        """
        # Escape backslashes
        text = text.replace("\\", "\\\\")
        
        # Escape hash symbols that could be confused with heading markers
        # Only escape if they appear at the start
        if text.startswith("#"):
            text = "\\" + text
        
        return text
    
    @staticmethod
    def escape_url(url: str) -> str:
        """Escape special characters in URLs.
        
        Args:
            url: URL to escape
            
        Returns:
            Escaped URL
        """
        # URLs need special handling - we need to escape spaces and parentheses
        # but preserve other URL-valid characters
        url = url.replace(" ", "%20")
        url = url.replace("(", "%28")
        url = url.replace(")", "%29")
        
        return url
    
    @staticmethod
    def unescape_code(text: str) -> str:
        """Remove escaping from code blocks and inline code.
        
        Code blocks should not have escaped characters as they are
        displayed literally.
        
        Args:
            text: Code text to unescape
            
        Returns:
            Unescaped text
        """
        # In code blocks, we don't want escaped characters
        # This is a no-op for now, but included for completeness
        return text
