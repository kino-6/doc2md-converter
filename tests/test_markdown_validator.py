"""Unit tests for Markdown validator.

Tests the MarkdownValidator class for syntax validation functionality.

Requirements:
    - 11.3: Validation mode that checks output Markdown syntax
    - 11.4: Report Markdown syntax errors or warnings
"""

import pytest
from src.markdown_validator import (
    MarkdownValidator,
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
    MARKDOWN_IT_AVAILABLE
)


# Skip all tests if markdown-it-py is not available
pytestmark = pytest.mark.skipif(
    not MARKDOWN_IT_AVAILABLE,
    reason="markdown-it-py not available"
)


class TestMarkdownValidator:
    """Test suite for MarkdownValidator."""
    
    def test_validator_initialization(self):
        """Test that validator initializes correctly."""
        validator = MarkdownValidator()
        assert validator is not None
        assert validator.md is not None
    
    def test_valid_markdown(self):
        """Test validation of valid Markdown content."""
        validator = MarkdownValidator()
        
        markdown = """# Heading 1

This is a paragraph with **bold** and *italic* text.

## Heading 2

- Item 1
- Item 2
- Item 3

1. First
2. Second
3. Third

[Link text](https://example.com)

```python
def hello():
    print("Hello, world!")
```

| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
"""
        
        result = validator.validate(markdown)
        assert result.valid
        assert result.error_count == 0
    
    def test_unclosed_code_block(self):
        """Test detection of unclosed code blocks."""
        validator = MarkdownValidator()
        
        markdown = """# Test

```python
def hello():
    print("Hello")
# Missing closing ```
"""
        
        result = validator.validate(markdown)
        assert not result.valid
        assert result.error_count > 0
        assert any("code block" in issue.message.lower() for issue in result.issues)
    
    def test_malformed_table_columns(self):
        """Test detection of tables with mismatched columns."""
        validator = MarkdownValidator()
        
        markdown = """# Test

| Header 1 | Header 2 | Header 3 |
|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
"""
        
        result = validator.validate(markdown)
        # Should have warnings about column mismatch
        assert result.warning_count > 0
        assert any("column" in issue.message.lower() for issue in result.issues)
    
    def test_heading_without_space(self):
        """Test detection of headings without space after #."""
        validator = MarkdownValidator()
        
        markdown = """#Heading without space

##Another one
"""
        
        result = validator.validate(markdown)
        assert result.warning_count > 0
        assert any("space" in issue.message.lower() for issue in result.issues)
    
    def test_excessive_heading_level(self):
        """Test detection of heading levels > 6."""
        validator = MarkdownValidator()
        
        markdown = """####### Level 7 heading
"""
        
        result = validator.validate(markdown)
        assert result.warning_count > 0
        assert any("level" in issue.message.lower() for issue in result.issues)
    
    def test_empty_link_text(self):
        """Test detection of links with empty text."""
        validator = MarkdownValidator()
        
        markdown = """[](https://example.com)
"""
        
        result = validator.validate(markdown)
        assert result.warning_count > 0
        assert any("empty" in issue.message.lower() for issue in result.issues)
    
    def test_empty_link_url(self):
        """Test detection of links with empty URL."""
        validator = MarkdownValidator()
        
        markdown = """[Link text]()
"""
        
        result = validator.validate(markdown)
        assert result.warning_count > 0
        assert any("empty" in issue.message.lower() for issue in result.issues)
    
    def test_ordered_list_without_space(self):
        """Test detection of ordered lists without space after period."""
        validator = MarkdownValidator()
        
        markdown = """1.First item
2.Second item
"""
        
        result = validator.validate(markdown)
        assert result.warning_count > 0
        assert any("space" in issue.message.lower() for issue in result.issues)
    
    def test_multiple_issues(self):
        """Test detection of multiple issues in one document."""
        validator = MarkdownValidator()
        
        markdown = """#Heading without space

```python
def test():
    pass
# Unclosed code block

| Col1 | Col2 |
|------|
| A | B | C |

[](empty-link.com)
"""
        
        result = validator.validate(markdown)
        assert len(result.issues) > 1
        assert result.error_count > 0 or result.warning_count > 0
    
    def test_validation_issue_string_format(self):
        """Test ValidationIssue string formatting."""
        issue = ValidationIssue(
            severity=ValidationSeverity.ERROR,
            message="Test error",
            line_number=10,
            context="Some context"
        )
        
        issue_str = str(issue)
        assert "ERROR" in issue_str
        assert "Line 10" in issue_str
        assert "Test error" in issue_str
        assert "Some context" in issue_str
    
    def test_validation_result_counts(self):
        """Test ValidationResult error and warning counts."""
        issues = [
            ValidationIssue(ValidationSeverity.ERROR, "Error 1"),
            ValidationIssue(ValidationSeverity.ERROR, "Error 2"),
            ValidationIssue(ValidationSeverity.WARNING, "Warning 1"),
            ValidationIssue(ValidationSeverity.INFO, "Info 1"),
        ]
        
        result = ValidationResult(valid=False, issues=issues)
        assert result.error_count == 2
        assert result.warning_count == 1
    
    def test_format_issues_empty(self):
        """Test formatting of empty issues list."""
        validator = MarkdownValidator()
        formatted = validator.format_issues([])
        assert "No validation issues" in formatted
    
    def test_format_issues_with_errors(self):
        """Test formatting of issues with errors."""
        validator = MarkdownValidator()
        issues = [
            ValidationIssue(ValidationSeverity.ERROR, "Error 1", line_number=5),
            ValidationIssue(ValidationSeverity.WARNING, "Warning 1", line_number=10),
        ]
        
        formatted = validator.format_issues(issues)
        assert "Errors (1)" in formatted
        assert "Warnings (1)" in formatted
        assert "Error 1" in formatted
        assert "Warning 1" in formatted
    
    def test_complex_valid_markdown(self):
        """Test validation of complex but valid Markdown."""
        validator = MarkdownValidator()
        
        markdown = """# Document Title

## Introduction

This document contains various Markdown elements.

### Lists

Unordered list:
- Item 1
  - Nested item 1.1
  - Nested item 1.2
- Item 2

Ordered list:
1. First item
2. Second item
   1. Nested 2.1
   2. Nested 2.2

### Code

Inline code: `print("hello")`

Code block:
```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

### Tables

| Name | Age | City |
|------|-----|------|
| Alice | 30 | NYC |
| Bob | 25 | LA |

### Links and Images

[GitHub](https://github.com)

![Alt text](image.png)

### Formatting

**Bold text** and *italic text* and ***bold italic***.

> Blockquote text
> Multiple lines

---

Horizontal rule above.
"""
        
        result = validator.validate(markdown)
        assert result.valid
        assert result.error_count == 0


class TestValidationIntegration:
    """Integration tests for validation with conversion."""
    
    def test_validate_simple_conversion_output(self):
        """Test validation of typical conversion output."""
        validator = MarkdownValidator()
        
        # Simulate output from a Word document conversion
        markdown = """# Document Title

## Section 1

This is a paragraph with some text.

### Subsection 1.1

- Point 1
- Point 2
- Point 3

## Section 2

| Column A | Column B |
|----------|----------|
| Value 1  | Value 2  |
| Value 3  | Value 4  |
"""
        
        result = validator.validate(markdown)
        assert result.valid
        assert result.error_count == 0
    
    def test_validate_with_ocr_markers(self):
        """Test validation of Markdown with OCR markers."""
        validator = MarkdownValidator()
        
        markdown = """# Document

![Image](images/image_001.png)

*[OCR extracted text: This is extracted text]*

Regular paragraph continues here.
"""
        
        result = validator.validate(markdown)
        # Should be valid even with OCR markers
        assert result.valid or result.error_count == 0
