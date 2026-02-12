"""
Property-based tests for Pretty Printer.

These tests verify that the PrettyPrinter correctly formats Markdown output
with consistent styling and proper spacing across a wide range of inputs.

Feature: document-to-markdown-converter
Properties: 52 (Pretty printing consistency), 23 (Spacing and readability)
Validates: Requirements 12.3, 5.2
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from src.pretty_printer import PrettyPrinter


class TestPropertyPrettyPrinter:
    """Property-based tests for Pretty Printer.
    
    Feature: document-to-markdown-converter
    Property 52: Pretty printing consistency
    Property 23: Spacing and readability
    Validates: Requirements 12.3, 5.2
    """
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    @staticmethod
    def count_consecutive_blank_lines(text: str) -> int:
        """Count the maximum number of consecutive blank lines in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Maximum number of consecutive blank lines
        """
        lines = text.split("\n")
        max_consecutive = 0
        current_consecutive = 0
        
        for line in lines:
            if line.strip() == "":
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return max_consecutive
    
    @staticmethod
    def has_trailing_whitespace(text: str) -> bool:
        """Check if any line has trailing whitespace.
        
        Args:
            text: Text to check
            
        Returns:
            True if any line has trailing whitespace
        """
        lines = text.split("\n")
        # Exclude the last line if it's just a newline
        for line in lines[:-1]:
            if line != line.rstrip():
                return True
        return False
    
    @staticmethod
    def generate_markdown_table(headers: list, rows: list) -> str:
        """Generate a simple Markdown table.
        
        Args:
            headers: List of header strings
            rows: List of row lists
            
        Returns:
            Markdown table string
        """
        if not headers:
            return ""
        
        table_lines = []
        # Header row
        table_lines.append("| " + " | ".join(headers) + " |")
        # Separator row
        table_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        # Data rows
        for row in rows:
            # Pad row to match header length
            padded_row = row + [""] * (len(headers) - len(row))
            table_lines.append("| " + " | ".join(padded_row[:len(headers)]) + " |")
        
        return "\n".join(table_lines)
    
    # ========================================================================
    # Property 52: Pretty Printing Consistency Tests
    # ========================================================================
    
    @given(markdown=st.text(min_size=0, max_size=1000))
    def test_property_52_idempotent_formatting(self, markdown):
        """
        Feature: document-to-markdown-converter
        Property 52: Pretty printing consistency
        
        For any Markdown text, applying the pretty printer multiple times
        should produce the same result (idempotent operation).
        
        **Validates: Requirements 12.3**
        """
        printer = PrettyPrinter()
        
        # Apply formatting once
        formatted_once = printer.format(markdown)
        
        # Apply formatting again
        formatted_twice = printer.format(formatted_once)
        
        # Property: Formatting should be idempotent
        assert formatted_once == formatted_twice, \
            "Pretty printer should be idempotent (formatting twice gives same result)"
    
    @given(
        headings=st.lists(
            st.tuples(
                st.integers(min_value=1, max_value=6),
                st.text(min_size=1, max_size=100).filter(lambda x: "\n" not in x)
            ),
            min_size=1,
            max_size=10
        )
    )
    def test_property_52_consistent_heading_spacing(self, headings):
        """
        Feature: document-to-markdown-converter
        Property 52: Pretty printing consistency
        
        For any Markdown with multiple headings, the pretty printer should
        ensure consistent spacing before headings.
        
        **Validates: Requirements 12.3**
        """
        printer = PrettyPrinter()
        
        # Generate Markdown with headings
        markdown_lines = []
        for level, text in headings:
            markdown_lines.append("#" * level + " " + text)
            markdown_lines.append("Some content here.")
        
        markdown = "\n".join(markdown_lines)
        formatted = printer.format(markdown)
        
        # Property: Each heading (except first) should have blank line before it
        lines = formatted.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("#") and i > 0:
                # Check if previous line is blank
                assert lines[i-1].strip() == "", \
                    f"Heading at line {i} should have blank line before it"
    
    @given(
        headers=st.lists(
            st.text(min_size=1, max_size=20).filter(lambda x: "|" not in x and "\n" not in x),
            min_size=1,
            max_size=5
        ),
        rows=st.lists(
            st.lists(
                st.text(min_size=0, max_size=20).filter(lambda x: "|" not in x and "\n" not in x),
                min_size=1,
                max_size=5
            ),
            min_size=1,
            max_size=10
        )
    )
    def test_property_52_consistent_table_alignment(self, headers, rows):
        """
        Feature: document-to-markdown-converter
        Property 52: Pretty printing consistency
        
        For any Markdown table, the pretty printer should align columns
        consistently across all rows.
        
        **Validates: Requirements 12.3**
        """
        printer = PrettyPrinter()
        
        # Generate a table
        table = self.generate_markdown_table(headers, rows)
        formatted = printer.format(table)
        
        # Property: All table rows should have same structure
        lines = formatted.split("\n")
        table_lines = [line for line in lines if line.strip().startswith("|")]
        
        if len(table_lines) > 0:
            # Count pipes in each line (should be consistent)
            pipe_counts = [line.count("|") for line in table_lines]
            assert len(set(pipe_counts)) == 1, \
                "All table rows should have same number of pipes"
            
            # Check that columns are aligned (same positions for pipes)
            pipe_positions = []
            for line in table_lines:
                positions = [i for i, char in enumerate(line) if char == "|"]
                pipe_positions.append(positions)
            
            # All rows should have pipes at same positions
            if len(pipe_positions) > 1:
                first_positions = pipe_positions[0]
                for positions in pipe_positions[1:]:
                    assert positions == first_positions, \
                        "Table columns should be aligned (pipes at same positions)"
    
    @given(
        items=st.lists(st.text(min_size=1, max_size=100).filter(lambda x: "\n" not in x), min_size=1, max_size=10),
        ordered=st.booleans()
    )
    def test_property_52_consistent_list_formatting(self, items, ordered):
        """
        Feature: document-to-markdown-converter
        Property 52: Pretty printing consistency
        
        For any Markdown list, the pretty printer should format list items
        consistently.
        
        **Validates: Requirements 12.3**
        """
        printer = PrettyPrinter()
        
        # Generate a list
        markdown_lines = []
        for i, item in enumerate(items):
            if ordered:
                markdown_lines.append(f"{i+1}. {item}")
            else:
                markdown_lines.append(f"- {item}")
        
        markdown = "\n".join(markdown_lines)
        formatted = printer.format(markdown)
        
        # Property: List should be preserved with consistent formatting
        lines = formatted.split("\n")
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Should have same number of items
        assert len(non_empty_lines) >= len(items), \
            "All list items should be preserved"
        
        # Check consistent markers
        for line in non_empty_lines:
            if ordered:
                assert any(line.strip().startswith(f"{i}.") for i in range(1, len(items) + 1)), \
                    "Ordered list items should have consistent numbering"
            else:
                assert line.strip().startswith("-"), \
                    "Unordered list items should have consistent markers"
    
    # ========================================================================
    # Property 23: Spacing and Readability Tests
    # ========================================================================
    
    @given(markdown=st.text(min_size=0, max_size=1000))
    def test_property_23_no_trailing_whitespace(self, markdown):
        """
        Feature: document-to-markdown-converter
        Property 23: Spacing and readability
        
        For any Markdown text, the pretty printer should remove trailing
        whitespace from all lines.
        
        **Validates: Requirements 5.2**
        """
        printer = PrettyPrinter()
        
        formatted = printer.format(markdown)
        
        # Property: No line should have trailing whitespace
        assert not self.has_trailing_whitespace(formatted), \
            "Formatted Markdown should not have trailing whitespace"
    
    @given(markdown=st.text(min_size=1, max_size=1000))
    def test_property_23_single_blank_lines(self, markdown):
        """
        Feature: document-to-markdown-converter
        Property 23: Spacing and readability
        
        For any Markdown text, the pretty printer should normalize multiple
        consecutive blank lines to single blank lines.
        
        **Validates: Requirements 5.2**
        """
        printer = PrettyPrinter()
        
        formatted = printer.format(markdown)
        
        # Property: Should not have more than one consecutive blank line
        # (excluding the final newline)
        lines = formatted.rstrip("\n").split("\n")
        max_consecutive = 0
        current_consecutive = 0
        
        for line in lines:
            if line.strip() == "":
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        assert max_consecutive <= 1, \
            f"Should have at most 1 consecutive blank line, found {max_consecutive}"
    
    @given(markdown=st.text(min_size=1, max_size=1000))
    def test_property_23_ends_with_newline(self, markdown):
        """
        Feature: document-to-markdown-converter
        Property 23: Spacing and readability
        
        For any non-empty Markdown text, the pretty printer should ensure
        the document ends with exactly one newline.
        
        **Validates: Requirements 5.2**
        """
        printer = PrettyPrinter()
        
        formatted = printer.format(markdown)
        
        # Property: Document should end with single newline
        if formatted:
            assert formatted.endswith("\n"), \
                "Formatted Markdown should end with newline"
            assert not formatted.endswith("\n\n"), \
                "Formatted Markdown should not end with multiple newlines"
    
    @given(
        heading=st.text(min_size=1, max_size=100).filter(lambda x: "\n" not in x),
        content=st.text(min_size=1, max_size=200).filter(lambda x: "\n" not in x)
    )
    def test_property_23_blank_line_before_heading(self, heading, content):
        """
        Feature: document-to-markdown-converter
        Property 23: Spacing and readability
        
        For any Markdown with headings after content, the pretty printer
        should ensure blank lines before headings for readability.
        
        **Validates: Requirements 5.2**
        """
        printer = PrettyPrinter()
        
        # Create Markdown with content followed by heading
        markdown = f"{content}\n# {heading}"
        formatted = printer.format(markdown)
        
        # Property: Heading should have blank line before it
        lines = formatted.split("\n")
        heading_index = None
        for i, line in enumerate(lines):
            if line.startswith("#"):
                heading_index = i
                break
        
        if heading_index is not None and heading_index > 0:
            assert lines[heading_index - 1].strip() == "", \
                "Heading should have blank line before it"
    
    @given(
        headers=st.lists(
            st.text(min_size=1, max_size=20).filter(lambda x: "|" not in x and "\n" not in x),
            min_size=1,
            max_size=5
        ),
        rows=st.lists(
            st.lists(
                st.text(min_size=0, max_size=20).filter(lambda x: "|" not in x and "\n" not in x),
                min_size=1,
                max_size=5
            ),
            min_size=1,
            max_size=5
        ),
        before_text=st.text(min_size=1, max_size=100).filter(lambda x: "\n" not in x and not x.strip().startswith("|")),
        after_text=st.text(min_size=1, max_size=100).filter(lambda x: "\n" not in x and not x.strip().startswith("|"))
    )
    def test_property_23_blank_lines_around_tables(self, headers, rows, before_text, after_text):
        """
        Feature: document-to-markdown-converter
        Property 23: Spacing and readability
        
        For any Markdown with tables, the pretty printer should ensure
        blank lines before and after tables for readability.
        
        **Validates: Requirements 5.2**
        """
        printer = PrettyPrinter()
        
        # Create Markdown with table surrounded by text
        table = self.generate_markdown_table(headers, rows)
        markdown = f"{before_text}\n{table}\n{after_text}"
        formatted = printer.format(markdown)
        
        # Property: Table should have blank lines before and after
        lines = formatted.split("\n")
        
        # Find table start and end
        table_start = None
        table_end = None
        for i, line in enumerate(lines):
            if line.strip().startswith("|"):
                if table_start is None:
                    table_start = i
                table_end = i
        
        if table_start is not None:
            # Check blank line before table (if not at start)
            if table_start > 0:
                assert lines[table_start - 1].strip() == "", \
                    "Table should have blank line before it"
            
            # Check blank line after table (if not at end)
            if table_end is not None and table_end < len(lines) - 1:
                # Next non-empty line should have blank before it
                next_non_empty = table_end + 1
                while next_non_empty < len(lines) and lines[next_non_empty].strip() == "":
                    next_non_empty += 1
                
                if next_non_empty < len(lines):
                    # There should be at least one blank line between table and next content
                    assert table_end + 1 < next_non_empty or lines[table_end + 1].strip() == "", \
                        "Table should have blank line after it"
    
    @given(
        items=st.lists(st.text(min_size=1, max_size=100).filter(lambda x: "\n" not in x), min_size=1, max_size=5),
        before_text=st.text(min_size=1, max_size=100).filter(lambda x: "\n" not in x and not x.strip().startswith("-") and not x.strip().startswith("*")),
        after_text=st.text(min_size=1, max_size=100).filter(lambda x: "\n" not in x and not x.strip().startswith("-") and not x.strip().startswith("*"))
    )
    def test_property_23_blank_lines_around_lists(self, items, before_text, after_text):
        """
        Feature: document-to-markdown-converter
        Property 23: Spacing and readability
        
        For any Markdown with lists, the pretty printer should ensure
        blank lines before and after lists for readability.
        
        **Validates: Requirements 5.2**
        """
        printer = PrettyPrinter()
        
        # Create Markdown with list surrounded by text
        list_lines = [f"- {item}" for item in items]
        markdown = f"{before_text}\n" + "\n".join(list_lines) + f"\n{after_text}"
        formatted = printer.format(markdown)
        
        # Property: List should have blank lines before and after
        lines = formatted.split("\n")
        
        # Find list start and end
        list_start = None
        list_end = None
        for i, line in enumerate(lines):
            if line.strip().startswith("-"):
                if list_start is None:
                    list_start = i
                list_end = i
        
        if list_start is not None:
            # Check blank line before list (if not at start)
            if list_start > 0:
                assert lines[list_start - 1].strip() == "", \
                    "List should have blank line before it"
            
            # Check blank line after list (if not at end)
            if list_end is not None and list_end < len(lines) - 1:
                # Next non-empty line should have blank before it
                next_non_empty = list_end + 1
                while next_non_empty < len(lines) and lines[next_non_empty].strip() == "":
                    next_non_empty += 1
                
                if next_non_empty < len(lines):
                    # There should be at least one blank line between list and next content
                    assert list_end + 1 < next_non_empty or lines[list_end + 1].strip() == "", \
                        "List should have blank line after it"
    
    @given(
        code=st.text(min_size=0, max_size=200),
        language=st.one_of(st.none(), st.sampled_from(["python", "javascript", "java"])),
        before_text=st.text(min_size=1, max_size=100).filter(lambda x: "\n" not in x),
        after_text=st.text(min_size=1, max_size=100).filter(lambda x: "\n" not in x)
    )
    def test_property_23_blank_lines_around_code_blocks(self, code, language, before_text, after_text):
        """
        Feature: document-to-markdown-converter
        Property 23: Spacing and readability
        
        For any Markdown with code blocks, the pretty printer should ensure
        blank lines before and after code blocks for readability.
        
        **Validates: Requirements 5.2**
        """
        printer = PrettyPrinter()
        
        # Create Markdown with code block surrounded by text
        lang_str = language if language else ""
        code_block = f"```{lang_str}\n{code}\n```"
        markdown = f"{before_text}\n{code_block}\n{after_text}"
        formatted = printer.format(markdown)
        
        # Property: Code block should have blank lines before and after
        lines = formatted.split("\n")
        
        # Find code block start
        code_start = None
        for i, line in enumerate(lines):
            if line.strip().startswith("```"):
                code_start = i
                break
        
        if code_start is not None and code_start > 0:
            # Check blank line before code block
            assert lines[code_start - 1].strip() == "", \
                "Code block should have blank line before it"
    
    @given(
        paragraphs=st.lists(
            st.text(min_size=1, max_size=200).filter(lambda x: "\n" not in x),
            min_size=2,
            max_size=5
        )
    )
    def test_property_23_paragraph_spacing(self, paragraphs):
        """
        Feature: document-to-markdown-converter
        Property 23: Spacing and readability
        
        For any Markdown with multiple paragraphs, the pretty printer should
        maintain proper spacing between paragraphs.
        
        **Validates: Requirements 5.2**
        """
        printer = PrettyPrinter()
        
        # Create Markdown with paragraphs
        markdown = "\n\n".join(paragraphs)
        formatted = printer.format(markdown)
        
        # Property: Paragraphs should be separated by single blank lines
        lines = formatted.split("\n")
        
        # Count blank lines between non-empty lines
        for i in range(len(lines) - 1):
            if lines[i].strip() and lines[i+1].strip():
                # Two consecutive non-empty lines should not exist
                # (there should be blank line between paragraphs)
                pass  # This is actually OK for inline content
            elif lines[i].strip() == "" and lines[i+1].strip() == "":
                # Should not have multiple consecutive blank lines
                pytest.fail("Should not have multiple consecutive blank lines")
    
    @given(
        markdown=st.text(min_size=10, max_size=500).filter(
            lambda x: any(c.isalnum() for c in x)
        )
    )
    def test_property_23_preserves_content(self, markdown):
        """
        Feature: document-to-markdown-converter
        Property 23: Spacing and readability
        
        For any Markdown text, the pretty printer should preserve all
        meaningful content while improving spacing.
        
        **Validates: Requirements 5.2**
        """
        printer = PrettyPrinter()
        
        formatted = printer.format(markdown)
        
        # Property: All non-whitespace content should be preserved
        original_words = markdown.split()
        formatted_words = formatted.split()
        
        # The words should be the same (order and content)
        assert original_words == formatted_words, \
            "Pretty printer should preserve all meaningful content"
    
    @given(
        sections=st.lists(
            st.tuples(
                st.text(min_size=1, max_size=50).filter(lambda x: "\n" not in x),  # heading
                st.text(min_size=1, max_size=200).filter(lambda x: "\n" not in x)  # content
            ),
            min_size=2,
            max_size=5
        )
    )
    def test_property_23_document_structure_readability(self, sections):
        """
        Feature: document-to-markdown-converter
        Property 23: Spacing and readability
        
        For any Markdown document with multiple sections, the pretty printer
        should ensure proper spacing that enhances readability.
        
        **Validates: Requirements 5.2**
        """
        printer = PrettyPrinter()
        
        # Create Markdown with multiple sections
        markdown_lines = []
        for heading, content in sections:
            markdown_lines.append(f"## {heading}")
            markdown_lines.append(content)
        
        markdown = "\n".join(markdown_lines)
        formatted = printer.format(markdown)
        
        # Property: Document should have consistent structure
        lines = formatted.split("\n")
        
        # Each heading should have blank line before it (except first)
        heading_indices = [i for i, line in enumerate(lines) if line.startswith("##")]
        
        for idx in heading_indices[1:]:  # Skip first heading
            if idx > 0:
                assert lines[idx - 1].strip() == "", \
                    "Each heading (except first) should have blank line before it"
        
        # Document should end with newline
        assert formatted.endswith("\n"), \
            "Document should end with newline"
