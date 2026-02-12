"""
Pretty printer for formatting Markdown output.

This module provides the PrettyPrinter class that formats Markdown text
for improved readability and consistency.
"""

import re
from typing import List


class PrettyPrinter:
    """Formats Markdown text for improved readability.
    
    This class provides methods to normalize whitespace, align table columns,
    and ensure proper blank lines in Markdown output.
    """
    
    def format(self, markdown: str) -> str:
        """Apply all formatting operations to Markdown text.
        
        Args:
            markdown: Raw Markdown text to format
            
        Returns:
            Formatted Markdown text
        """
        # Apply formatting operations in sequence
        formatted = self.normalize_whitespace(markdown)
        formatted = self.align_tables(formatted)
        formatted = self.ensure_blank_lines(formatted)
        
        return formatted
    
    def normalize_whitespace(self, markdown: str) -> str:
        """Normalize whitespace in Markdown text.
        
        This method:
        - Removes trailing whitespace from lines
        - Converts multiple consecutive blank lines to single blank lines
        - Ensures the document ends with a single newline
        
        Args:
            markdown: Markdown text to normalize
            
        Returns:
            Markdown text with normalized whitespace
        """
        # Split into lines
        lines = markdown.split("\n")
        
        # Remove trailing whitespace from each line
        lines = [line.rstrip() for line in lines]
        
        # Remove multiple consecutive blank lines
        normalized_lines = []
        prev_blank = False
        
        for line in lines:
            is_blank = line == ""
            
            # Skip consecutive blank lines
            if is_blank and prev_blank:
                continue
            
            normalized_lines.append(line)
            prev_blank = is_blank
        
        # Join lines back together
        result = "\n".join(normalized_lines)
        
        # Ensure document ends with single newline
        result = result.rstrip("\n") + "\n"
        
        return result
    
    def align_tables(self, markdown: str) -> str:
        """Align table columns for improved readability.
        
        This method adjusts the spacing in Markdown tables so that columns
        are properly aligned, making tables easier to read in plain text.
        
        Args:
            markdown: Markdown text containing tables
            
        Returns:
            Markdown text with aligned tables
        """
        lines = markdown.split("\n")
        result_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if this line is a table row
            if self._is_table_row(line):
                # Collect all consecutive table rows
                table_lines = []
                while i < len(lines) and self._is_table_row(lines[i]):
                    table_lines.append(lines[i])
                    i += 1
                
                # Align the table
                aligned_table = self._align_table_lines(table_lines)
                result_lines.extend(aligned_table)
            else:
                result_lines.append(line)
                i += 1
        
        return "\n".join(result_lines)
    
    def _is_table_row(self, line: str) -> bool:
        """Check if a line is a table row.
        
        Args:
            line: Line to check
            
        Returns:
            True if the line is a table row, False otherwise
        """
        stripped = line.strip()
        return stripped.startswith("|") and stripped.endswith("|")
    
    def _align_table_lines(self, table_lines: List[str]) -> List[str]:
        """Align a group of table lines.
        
        Args:
            table_lines: List of table row strings
            
        Returns:
            List of aligned table row strings
        """
        if not table_lines:
            return []
        
        # Parse each row into cells
        rows = []
        for line in table_lines:
            cells = self._parse_table_row(line)
            rows.append(cells)
        
        # Calculate maximum width for each column
        num_columns = max(len(row) for row in rows) if rows else 0
        column_widths = [0] * num_columns
        
        for row in rows:
            for i, cell in enumerate(row):
                # For separator rows, use minimum width of 3
                if self._is_separator_cell(cell):
                    column_widths[i] = max(column_widths[i], 3)
                else:
                    column_widths[i] = max(column_widths[i], len(cell))
        
        # Format each row with aligned columns
        aligned_lines = []
        for row in rows:
            aligned_cells = []
            for i, cell in enumerate(row):
                if i < len(column_widths):
                    if self._is_separator_cell(cell):
                        # Separator cells use dashes
                        aligned_cell = "-" * column_widths[i]
                    else:
                        # Regular cells are left-aligned with padding
                        aligned_cell = cell.ljust(column_widths[i])
                    aligned_cells.append(aligned_cell)
                else:
                    aligned_cells.append(cell)
            
            aligned_line = "| " + " | ".join(aligned_cells) + " |"
            aligned_lines.append(aligned_line)
        
        return aligned_lines
    
    def _parse_table_row(self, line: str) -> List[str]:
        """Parse a table row into individual cells.
        
        Args:
            line: Table row string
            
        Returns:
            List of cell contents
        """
        # Remove leading/trailing pipes and whitespace
        line = line.strip()
        if line.startswith("|"):
            line = line[1:]
        if line.endswith("|"):
            line = line[:-1]
        
        # Split by pipe and strip whitespace from each cell
        cells = [cell.strip() for cell in line.split("|")]
        
        return cells
    
    def _is_separator_cell(self, cell: str) -> bool:
        """Check if a cell is a separator cell (contains only dashes and colons).
        
        Args:
            cell: Cell content to check
            
        Returns:
            True if the cell is a separator, False otherwise
        """
        return bool(re.match(r'^:?-+:?$', cell))
    
    def ensure_blank_lines(self, markdown: str) -> str:
        """Ensure proper blank lines around block elements.
        
        This method ensures that:
        - Headings have a blank line before them (except at document start)
        - Code blocks have blank lines before and after
        - Lists have blank lines before and after
        - Tables have blank lines before and after
        
        Args:
            markdown: Markdown text to process
            
        Returns:
            Markdown text with proper blank lines
        """
        lines = markdown.split("\n")
        result_lines = []
        
        for i, line in enumerate(lines):
            # Check if we need a blank line before this line
            if i > 0 and self._needs_blank_before(line, lines[i-1]):
                # Add blank line if previous line is not already blank
                if result_lines and result_lines[-1] != "":
                    result_lines.append("")
            
            result_lines.append(line)
            
            # Check if we need a blank line after this line
            if i < len(lines) - 1 and self._needs_blank_after(line, lines[i+1]):
                # Add blank line if next line is not already blank
                if lines[i+1] != "":
                    result_lines.append("")
        
        return "\n".join(result_lines)
    
    def _needs_blank_before(self, current_line: str, previous_line: str) -> bool:
        """Check if a blank line is needed before the current line.
        
        Args:
            current_line: Current line to check
            previous_line: Previous line
            
        Returns:
            True if a blank line is needed, False otherwise
        """
        # Blank line before headings (unless previous is blank)
        if current_line.strip().startswith("#") and previous_line.strip() != "":
            return True
        
        # Blank line before code blocks
        if current_line.strip().startswith("```"):
            return True
        
        # Blank line before tables
        if self._is_table_row(current_line) and not self._is_table_row(previous_line):
            return True
        
        # Blank line before lists (starting with -, *, or number.)
        if re.match(r'^\s*[-*]|\d+\.', current_line) and not re.match(r'^\s*[-*]|\d+\.', previous_line):
            return True
        
        return False
    
    def _needs_blank_after(self, current_line: str, next_line: str) -> bool:
        """Check if a blank line is needed after the current line.
        
        Args:
            current_line: Current line to check
            next_line: Next line
            
        Returns:
            True if a blank line is needed, False otherwise
        """
        # Blank line after code blocks
        if current_line.strip().startswith("```") and current_line.strip() != "```":
            return True
        
        # Blank line after tables
        if self._is_table_row(current_line) and not self._is_table_row(next_line):
            return True
        
        # Blank line after lists
        if re.match(r'^\s*[-*]|\d+\.', current_line) and not re.match(r'^\s*[-*]|\d+\.', next_line):
            return True
        
        return False
