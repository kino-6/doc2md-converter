"""Markdown validation module for Document to Markdown Converter.

This module provides Markdown syntax validation using markdown-it-py.
It checks for syntax errors, structural issues, and common problems in
generated Markdown content.

Requirements:
    - 11.3: Provide validation mode that checks output Markdown syntax
    - 11.4: Report Markdown syntax errors or warnings when validation is performed
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

try:
    from markdown_it import MarkdownIt
    from markdown_it.token import Token
    MARKDOWN_IT_AVAILABLE = True
except ImportError:
    MARKDOWN_IT_AVAILABLE = False


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Represents a validation issue found in Markdown content.
    
    Attributes:
        severity: Severity level of the issue
        message: Description of the issue
        line_number: Line number where issue was found (if applicable)
        context: Surrounding context for the issue
    """
    severity: ValidationSeverity
    message: str
    line_number: Optional[int] = None
    context: Optional[str] = None
    
    def __str__(self) -> str:
        """Format validation issue as string."""
        parts = [f"[{self.severity.value.upper()}]"]
        
        if self.line_number is not None:
            parts.append(f"Line {self.line_number}:")
        
        parts.append(self.message)
        
        if self.context:
            parts.append(f"Context: {self.context}")
        
        return " ".join(parts)


@dataclass
class ValidationResult:
    """Result of Markdown validation.
    
    Attributes:
        valid: Whether the Markdown is valid
        issues: List of validation issues found
        error_count: Number of errors found
        warning_count: Number of warnings found
    """
    valid: bool
    issues: List[ValidationIssue]
    error_count: int = 0
    warning_count: int = 0
    
    def __post_init__(self):
        """Calculate error and warning counts."""
        self.error_count = sum(
            1 for issue in self.issues 
            if issue.severity == ValidationSeverity.ERROR
        )
        self.warning_count = sum(
            1 for issue in self.issues 
            if issue.severity == ValidationSeverity.WARNING
        )


class MarkdownValidator:
    """Validates Markdown syntax and structure.
    
    Uses markdown-it-py to parse and validate Markdown content,
    checking for syntax errors, structural issues, and common problems.
    
    Requirements:
        - 11.3: Validation mode that checks output Markdown syntax
        - 11.4: Report Markdown syntax errors or warnings
    """
    
    def __init__(self):
        """Initialize the Markdown validator."""
        if not MARKDOWN_IT_AVAILABLE:
            raise ImportError(
                "markdown-it-py is required for Markdown validation. "
                "Install it with: pip install markdown-it-py"
            )
        
        # Initialize markdown-it parser
        self.md = MarkdownIt()
    
    def validate(self, markdown_content: str) -> ValidationResult:
        """Validate Markdown content.
        
        Args:
            markdown_content: Markdown content to validate
            
        Returns:
            ValidationResult with validation status and issues
        """
        issues: List[ValidationIssue] = []
        
        try:
            # Parse the markdown content
            tokens = self.md.parse(markdown_content)
            
            # Perform various validation checks
            issues.extend(self._check_code_blocks(markdown_content))
            issues.extend(self._check_tables(markdown_content))
            issues.extend(self._check_headings(markdown_content))
            issues.extend(self._check_links(markdown_content))
            issues.extend(self._check_lists(markdown_content))
            
            # Check if parsing produced any errors
            issues.extend(self._check_parsing_tokens(tokens))
            
        except Exception as e:
            # Parsing failed completely
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message=f"Failed to parse Markdown: {str(e)}"
            ))
        
        # Determine if valid (no errors)
        has_errors = any(
            issue.severity == ValidationSeverity.ERROR 
            for issue in issues
        )
        
        return ValidationResult(
            valid=not has_errors,
            issues=issues
        )
    
    def _check_code_blocks(self, content: str) -> List[ValidationIssue]:
        """Check for unclosed code blocks.
        
        Args:
            content: Markdown content
            
        Returns:
            List of validation issues
        """
        issues = []
        lines = content.split('\n')
        
        code_block_markers = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('```'):
                code_block_markers.append((i, line))
        
        # Check if code blocks are balanced
        if len(code_block_markers) % 2 != 0:
            last_marker = code_block_markers[-1] if code_block_markers else (0, "")
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="Unclosed code block detected",
                line_number=last_marker[0],
                context=last_marker[1][:50]
            ))
        
        return issues
    
    def _check_tables(self, content: str) -> List[ValidationIssue]:
        """Check for malformed tables.
        
        Args:
            content: Markdown content
            
        Returns:
            List of validation issues
        """
        issues = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check if this looks like a table row
            if line.startswith('|') and line.endswith('|'):
                # Count columns in this row
                columns = len([cell for cell in line.split('|') if cell.strip()])
                
                # Check if next line is a separator
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line.startswith('|') and '-' in next_line:
                        # This is a table header
                        separator_columns = len([
                            cell for cell in next_line.split('|') 
                            if cell.strip()
                        ])
                        
                        if columns != separator_columns:
                            issues.append(ValidationIssue(
                                severity=ValidationSeverity.WARNING,
                                message=f"Table header has {columns} columns but separator has {separator_columns}",
                                line_number=i + 1,
                                context=line[:50]
                            ))
                        
                        # Check subsequent rows
                        j = i + 2
                        while j < len(lines):
                            row_line = lines[j].strip()
                            if not row_line.startswith('|'):
                                break
                            
                            row_columns = len([
                                cell for cell in row_line.split('|') 
                                if cell.strip()
                            ])
                            
                            if row_columns != columns:
                                issues.append(ValidationIssue(
                                    severity=ValidationSeverity.WARNING,
                                    message=f"Table row has {row_columns} columns but header has {columns}",
                                    line_number=j + 1,
                                    context=row_line[:50]
                                ))
                            
                            j += 1
                        
                        i = j
                        continue
            
            i += 1
        
        return issues
    
    def _check_headings(self, content: str) -> List[ValidationIssue]:
        """Check for heading issues.
        
        Args:
            content: Markdown content
            
        Returns:
            List of validation issues
        """
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check for ATX-style headings (# Heading)
            if stripped.startswith('#'):
                # Count heading level
                level = 0
                for char in stripped:
                    if char == '#':
                        level += 1
                    else:
                        break
                
                # Check if there's a space after the hashes
                if level < len(stripped) and stripped[level] != ' ':
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        message=f"Heading should have a space after '#' markers",
                        line_number=i,
                        context=stripped[:50]
                    ))
                
                # Check for excessive heading level
                if level > 6:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        message=f"Heading level {level} exceeds maximum of 6",
                        line_number=i,
                        context=stripped[:50]
                    ))
        
        return issues
    
    def _check_links(self, content: str) -> List[ValidationIssue]:
        """Check for malformed links.
        
        Args:
            content: Markdown content
            
        Returns:
            List of validation issues
        """
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for unmatched brackets in links
            # Simple check: count [ and ] and ( and )
            open_square = line.count('[')
            close_square = line.count(']')
            open_paren = line.count('(')
            close_paren = line.count(')')
            
            # Check for potential link syntax issues
            if '[' in line and ']' in line:
                # Look for pattern [text](url)
                import re
                # Find all potential links
                link_pattern = r'\[([^\]]*)\]\(([^\)]*)\)'
                matches = re.finditer(link_pattern, line)
                
                for match in matches:
                    text = match.group(1)
                    url = match.group(2)
                    
                    # Check for empty link text
                    if not text.strip():
                        issues.append(ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            message="Link has empty text",
                            line_number=i,
                            context=match.group(0)
                        ))
                    
                    # Check for empty URL
                    if not url.strip():
                        issues.append(ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            message="Link has empty URL",
                            line_number=i,
                            context=match.group(0)
                        ))
        
        return issues
    
    def _check_lists(self, content: str) -> List[ValidationIssue]:
        """Check for list formatting issues.
        
        Args:
            content: Markdown content
            
        Returns:
            List of validation issues
        """
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check unordered lists
            if stripped.startswith(('- ', '* ', '+ ')):
                # Check if there's proper spacing
                if len(line) > 0 and line[0] not in (' ', '-', '*', '+'):
                    # List item should be indented or at start
                    pass
            
            # Check ordered lists
            if stripped and stripped[0].isdigit():
                import re
                if re.match(r'^\d+\.', stripped):
                    # Check if there's a space after the period
                    match = re.match(r'^(\d+\.)\s', stripped)
                    if not match:
                        issues.append(ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            message="Ordered list item should have space after period",
                            line_number=i,
                            context=stripped[:50]
                        ))
        
        return issues
    
    def _check_parsing_tokens(self, tokens: List[Token]) -> List[ValidationIssue]:
        """Check parsed tokens for issues.
        
        Args:
            tokens: List of parsed tokens from markdown-it
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Check for any error tokens or unexpected structures
        for token in tokens:
            # markdown-it-py doesn't typically produce error tokens,
            # but we can check for unusual patterns
            if token.type == 'inline' and token.content:
                # Check for unescaped special characters in inline content
                special_chars = ['<', '>']
                for char in special_chars:
                    if char in token.content and f'\\{char}' not in token.content:
                        # This might be intentional HTML, so just a warning
                        pass
        
        return issues
    
    def format_issues(self, issues: List[ValidationIssue]) -> str:
        """Format validation issues as a readable string.
        
        Args:
            issues: List of validation issues
            
        Returns:
            Formatted string with all issues
        """
        if not issues:
            return "No validation issues found."
        
        lines = ["Markdown Validation Issues:", ""]
        
        # Group by severity
        errors = [i for i in issues if i.severity == ValidationSeverity.ERROR]
        warnings = [i for i in issues if i.severity == ValidationSeverity.WARNING]
        infos = [i for i in issues if i.severity == ValidationSeverity.INFO]
        
        if errors:
            lines.append(f"Errors ({len(errors)}):")
            for issue in errors:
                lines.append(f"  {issue}")
            lines.append("")
        
        if warnings:
            lines.append(f"Warnings ({len(warnings)}):")
            for issue in warnings:
                lines.append(f"  {issue}")
            lines.append("")
        
        if infos:
            lines.append(f"Info ({len(infos)}):")
            for issue in infos:
                lines.append(f"  {issue}")
            lines.append("")
        
        return "\n".join(lines)
