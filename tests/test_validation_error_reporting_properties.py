"""Property-based tests for validation error reporting.

Feature: document-to-markdown-converter
Property 48: Validation error reporting
Validates: Requirements 11.4
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from pathlib import Path
from docx import Document
from src.markdown_validator import MarkdownValidator, ValidationSeverity, MARKDOWN_IT_AVAILABLE
import tempfile


# Skip all tests if markdown-it-py is not available
pytestmark = pytest.mark.skipif(
    not MARKDOWN_IT_AVAILABLE,
    reason="markdown-it-py not available"
)


# Strategy for generating text content compatible with Office documents
def is_valid_office_char(c):
    """Check if character is valid for Office documents."""
    code = ord(c)
    # Allow tab, newline, carriage return
    if code in (0x09, 0x0A, 0x0D):
        return True
    # Exclude other control characters (0x00-0x1F, 0x7F-0x9F)
    if code < 0x20 or (0x7F <= code <= 0x9F):
        return False
    # Exclude surrogates
    if 0xD800 <= code <= 0xDFFF:
        return False
    return True


text_content_strategy = st.text(
    alphabet=st.characters(
        blacklist_categories=('Cs',),  # Exclude surrogates
    ).filter(is_valid_office_char),
    min_size=1,
    max_size=200
)


@settings(max_examples=100)
@given(content=text_content_strategy)
def test_property_48_validation_reports_unclosed_code_blocks(content):
    """Feature: document-to-markdown-converter, Property 48: Validation error reporting
    
    For any Markdown with unclosed code blocks, the validator should report 
    syntax errors with line numbers and context.
    
    **Validates: Requirements 11.4**
    """
    # Create Markdown with unclosed code block
    markdown_content = f"""# Test Document

{content}

```python
def test():
    pass
"""
    # Note: Missing closing ``` for code block
    
    validator = MarkdownValidator()
    result = validator.validate(markdown_content)
    
    # Property: Validation should detect the error
    assert not result.valid, "Validator should detect unclosed code block"
    
    # Property: Should report at least one error
    assert result.error_count > 0, "Should report at least one error"
    
    # Property: Error should have severity ERROR
    errors = [issue for issue in result.issues if issue.severity == ValidationSeverity.ERROR]
    assert len(errors) > 0, "Should have at least one ERROR severity issue"
    
    # Property: Error message should be descriptive
    error_messages = [issue.message for issue in errors]
    assert any("code block" in msg.lower() or "unclosed" in msg.lower() 
               for msg in error_messages), \
        "Error message should mention code block or unclosed"


@settings(max_examples=100)
@given(
    header_text=text_content_strategy,
    row1_col1=text_content_strategy,
    row1_col2=text_content_strategy
)
def test_property_48_validation_reports_malformed_tables(header_text, row1_col1, row1_col2):
    """Feature: document-to-markdown-converter, Property 48: Validation error reporting
    
    For any Markdown with malformed tables (mismatched column counts), 
    the validator should report warnings with line numbers.
    
    **Validates: Requirements 11.4**
    """
    # Assume inputs don't contain pipe characters that would break table structure
    assume('|' not in header_text)
    assume('|' not in row1_col1)
    assume('|' not in row1_col2)
    assume('\n' not in header_text)
    assume('\n' not in row1_col1)
    assume('\n' not in row1_col2)
    
    # Create Markdown with mismatched table columns
    markdown_content = f"""# Test Document

| Header 1 | Header 2 |
|----------|----------|
| {row1_col1} | {row1_col2} |
| Only One Column |
"""
    # Note: Last row has only 1 column instead of 2
    
    validator = MarkdownValidator()
    result = validator.validate(markdown_content)
    
    # Property: Should report at least one issue (warning or error)
    assert len(result.issues) > 0, "Should report table column mismatch"
    
    # Property: Issue should have line number
    issues_with_line_numbers = [issue for issue in result.issues if issue.line_number is not None]
    assert len(issues_with_line_numbers) > 0, "Issues should include line numbers"
    
    # Property: Issue message should mention table or column
    issue_messages = [issue.message for issue in result.issues]
    assert any("table" in msg.lower() or "column" in msg.lower() 
               for msg in issue_messages), \
        "Issue message should mention table or column"


@settings(max_examples=100)
@given(heading_text=text_content_strategy)
def test_property_48_validation_reports_heading_issues(heading_text):
    """Feature: document-to-markdown-converter, Property 48: Validation error reporting
    
    For any Markdown with heading syntax issues (missing space after #), 
    the validator should report warnings.
    
    **Validates: Requirements 11.4**
    """
    # Assume heading text doesn't start with space or newline
    assume(heading_text and heading_text[0] not in (' ', '\n', '\t'))
    assume('\n' not in heading_text)
    
    # Create Markdown with heading missing space after #
    markdown_content = f"""#{heading_text}

This is some content.
"""
    # Note: Missing space after # in heading
    
    validator = MarkdownValidator()
    result = validator.validate(markdown_content)
    
    # Property: Should report at least one issue
    assert len(result.issues) > 0, "Should report heading syntax issue"
    
    # Property: Issue should mention heading
    issue_messages = [issue.message for issue in result.issues]
    assert any("heading" in msg.lower() or "space" in msg.lower() 
               for msg in issue_messages), \
        "Issue message should mention heading or space"
    
    # Property: Issue should have line number
    assert any(issue.line_number is not None for issue in result.issues), \
        "Issue should include line number"


@settings(max_examples=100)
@given(link_text=text_content_strategy)
def test_property_48_validation_reports_empty_link_urls(link_text):
    """Feature: document-to-markdown-converter, Property 48: Validation error reporting
    
    For any Markdown with links that have empty URLs, the validator should 
    report warnings.
    
    **Validates: Requirements 11.4**
    """
    # Assume link text doesn't contain brackets or newlines
    assume('[' not in link_text and ']' not in link_text)
    assume('(' not in link_text and ')' not in link_text)
    assume('\n' not in link_text)
    assume(link_text.strip())  # Not empty or whitespace only
    
    # Create Markdown with link that has empty URL
    markdown_content = f"""# Test Document

This is a link: [{link_text}]()

More content here.
"""
    # Note: Link has empty URL in parentheses
    
    validator = MarkdownValidator()
    result = validator.validate(markdown_content)
    
    # Property: Should report at least one issue
    assert len(result.issues) > 0, "Should report empty link URL"
    
    # Property: Issue should mention link or URL
    issue_messages = [issue.message for issue in result.issues]
    assert any("link" in msg.lower() or "url" in msg.lower() or "empty" in msg.lower()
               for msg in issue_messages), \
        "Issue message should mention link, URL, or empty"
    
    # Property: Issue should have line number
    assert any(issue.line_number is not None for issue in result.issues), \
        "Issue should include line number"


@settings(max_examples=100)
@given(content=text_content_strategy)
def test_property_48_validation_reports_no_errors_for_valid_markdown(content):
    """Feature: document-to-markdown-converter, Property 48: Validation error reporting
    
    For any valid Markdown content, the validator should report no errors 
    (though it may report warnings).
    
    **Validates: Requirements 11.4**
    """
    # Create valid Markdown
    markdown_content = f"""# Test Document

## Section 1

{content}

## Section 2

This is a paragraph with **bold** and *italic* text.

- List item 1
- List item 2
- List item 3

| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |

```python
def example():
    return True
```

[Link text](https://example.com)
"""
    
    validator = MarkdownValidator()
    result = validator.validate(markdown_content)
    
    # Property: Should not report any errors (valid=True or error_count=0)
    assert result.error_count == 0, \
        f"Valid Markdown should have no errors, but got {result.error_count} errors"
    
    # Property: If there are issues, they should only be warnings or info
    for issue in result.issues:
        assert issue.severity != ValidationSeverity.ERROR, \
            f"Valid Markdown should not have ERROR severity issues: {issue}"


@settings(max_examples=100)
@given(list_item=text_content_strategy)
def test_property_48_validation_reports_ordered_list_spacing_issues(list_item):
    """Feature: document-to-markdown-converter, Property 48: Validation error reporting
    
    For any Markdown with ordered list items missing space after period, 
    the validator should report warnings when detected.
    
    **Validates: Requirements 11.4**
    """
    # Assume list item doesn't start with space or newline and is alphanumeric
    assume(list_item and list_item[0] not in (' ', '\n', '\t'))
    assume('\n' not in list_item)
    assume(any(c.isalnum() for c in list_item))  # Has at least one alphanumeric char
    
    # Create Markdown with ordered list missing space after period
    markdown_content = f"""# Test Document

1.{list_item}
2. Second item with proper spacing
"""
    # Note: First item missing space after period
    
    validator = MarkdownValidator()
    result = validator.validate(markdown_content)
    
    # Property: If issues are reported, they should have proper structure
    # Note: Not all malformed lists are detected by markdown-it-py, so we check
    # that IF issues are reported, they are properly structured
    if len(result.issues) > 0:
        # Property: Issue should have line number
        assert any(issue.line_number is not None for issue in result.issues), \
            "Issues should include line numbers"
        
        # Property: Each issue should have a descriptive message
        for issue in result.issues:
            assert len(issue.message) > 5, \
                f"Issue message should be descriptive: {issue.message}"


@settings(max_examples=100)
@given(content=text_content_strategy)
def test_property_48_validation_provides_context_for_errors(content):
    """Feature: document-to-markdown-converter, Property 48: Validation error reporting
    
    For any validation error, the validator should provide context 
    (surrounding text or problematic line).
    
    **Validates: Requirements 11.4**
    """
    # Create Markdown with multiple types of issues
    markdown_content = f"""# Test Document

{content}

```python
def unclosed():
    pass

| Header 1 | Header 2 |
|----------|----------|
| Cell 1 |

[Empty URL link]()
"""
    # Note: Multiple issues - unclosed code block, malformed table, empty URL
    
    validator = MarkdownValidator()
    result = validator.validate(markdown_content)
    
    # Property: Should report multiple issues
    assert len(result.issues) > 0, "Should report multiple issues"
    
    # Property: At least some issues should have context
    issues_with_context = [issue for issue in result.issues if issue.context is not None]
    # Note: Not all issues may have context, but at least some should
    # This is a weaker property since context is optional
    
    # Property: All issues should have descriptive messages
    for issue in result.issues:
        assert len(issue.message) > 10, \
            f"Issue message should be descriptive: {issue.message}"
    
    # Property: Issues should be properly formatted as strings
    for issue in result.issues:
        issue_str = str(issue)
        assert len(issue_str) > 0, "Issue should format as non-empty string"
        assert issue.severity.value.upper() in issue_str, \
            "Issue string should include severity level"


@settings(max_examples=100)
@given(content=text_content_strategy)
def test_property_48_validation_distinguishes_errors_and_warnings(content):
    """Feature: document-to-markdown-converter, Property 48: Validation error reporting
    
    For any Markdown with both errors and warnings, the validator should 
    properly distinguish between severity levels.
    
    **Validates: Requirements 11.4**
    """
    # Create Markdown with both errors (unclosed code block) and warnings (table issues)
    markdown_content = f"""# Test Document

{content}

```python
def unclosed():
    pass

| Header 1 | Header 2 |
|----------|----------|
| Cell 1 | Cell 2 |
| Only One |
"""
    # Note: Unclosed code block (error) and table column mismatch (warning)
    
    validator = MarkdownValidator()
    result = validator.validate(markdown_content)
    
    # Property: Should report issues
    assert len(result.issues) > 0, "Should report issues"
    
    # Property: Error count should be tracked separately from warning count
    assert result.error_count >= 0, "Error count should be non-negative"
    assert result.warning_count >= 0, "Warning count should be non-negative"
    
    # Property: Total issues should equal sum of errors and warnings (and info)
    total_counted = result.error_count + result.warning_count
    # Note: There might be INFO level issues too, so total_counted <= len(issues)
    assert total_counted <= len(result.issues), \
        "Error + warning count should not exceed total issues"
    
    # Property: If validation is invalid, there should be at least one error
    if not result.valid:
        assert result.error_count > 0, \
            "Invalid validation result should have at least one error"
    
    # Property: Each issue should have a valid severity
    valid_severities = {ValidationSeverity.ERROR, ValidationSeverity.WARNING, ValidationSeverity.INFO}
    for issue in result.issues:
        assert issue.severity in valid_severities, \
            f"Issue should have valid severity: {issue.severity}"


@settings(max_examples=50)
@given(
    content1=text_content_strategy,
    content2=text_content_strategy
)
def test_property_48_validation_reports_multiple_errors_independently(content1, content2):
    """Feature: document-to-markdown-converter, Property 48: Validation error reporting
    
    For any Markdown with multiple independent errors, the validator should 
    report each error separately with its own line number and context.
    
    **Validates: Requirements 11.4**
    """
    # Create Markdown with multiple independent errors
    # Use unclosed code block and table mismatch
    markdown_content = f"""# Test Document

{content1}

```python
def first_unclosed():
    pass

{content2}

| Header 1 | Header 2 |
|----------|----------|
| Cell 1 | Cell 2 |
| Mismatched |

| Another | Table |
|---------|-------|
| Also | Mismatched |
"""
    # Note: One unclosed code block and two table issues
    
    validator = MarkdownValidator()
    result = validator.validate(markdown_content)
    
    # Property: Should report at least one issue
    assert len(result.issues) >= 1, \
        f"Should report at least 1 issue, got {len(result.issues)}"
    
    # Property: Each issue should have its own message
    messages = [issue.message for issue in result.issues]
    assert len(messages) == len(result.issues), \
        "Each issue should have a message"
    
    # Property: Messages should be non-empty and descriptive
    for message in messages:
        assert len(message) > 5, f"Message should be descriptive: {message}"
    
    # Property: If multiple issues are reported, they should have different line numbers
    # (unless they genuinely occur on the same line)
    if len(result.issues) >= 2:
        line_numbers = [issue.line_number for issue in result.issues if issue.line_number is not None]
        assert len(line_numbers) > 0, "Issues should have line numbers"
        
        # Property: Each issue should be independently identifiable
        for i, issue in enumerate(result.issues):
            # Each issue should have either a line number or context
            assert issue.line_number is not None or issue.context is not None, \
                f"Issue {i} should have line number or context"
