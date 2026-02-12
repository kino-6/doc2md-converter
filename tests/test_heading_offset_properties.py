"""
Property-based tests for heading level offset feature.

This module contains property-based tests using Hypothesis to verify
that heading level offset is correctly applied during conversion.

Feature: document-to-markdown-converter
Property: 35
Validates: Requirements 8.1
"""

import pytest
from hypothesis import given, strategies as st, settings
from src.markdown_serializer import MarkdownSerializer
from src.internal_representation import (
    InternalDocument,
    Section,
    Heading,
    Paragraph,
    TextFormatting,
)


class TestHeadingOffsetProperty:
    """Property 35: Heading level offset
    
    For any document with headings, when a heading offset is configured, the converter
    should apply the offset to all heading levels in the output.
    
    Validates: Requirements 8.1
    """
    
    @given(
        original_level=st.integers(min_value=1, max_value=6),
        offset=st.integers(min_value=-10, max_value=10),
        heading_text=st.text(min_size=1, max_size=100)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_35_heading_level_offset(self, original_level, offset, heading_text):
        """
        Feature: document-to-markdown-converter
        Property 35: Heading level offset
        
        For any document with headings, when a heading offset is configured, the converter
        should apply the offset to all heading levels in the output.
        
        **Validates: Requirements 8.1**
        """
        # Skip empty or whitespace-only text
        if not heading_text.strip():
            return
        
        # Create serializer with the specified offset
        serializer = MarkdownSerializer(heading_offset=offset)
        
        # Create a heading with the original level
        heading = Heading(level=original_level, text=heading_text)
        
        # Serialize the heading
        result = serializer.serialize_heading(heading)
        
        # Property: Result should be a non-empty string
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Property: Calculate expected level (clamped to 1-6)
        expected_level = max(1, min(6, original_level + offset))
        
        # Property: Result should start with the correct number of # characters
        assert result.startswith("#" * expected_level + " "), \
            f"Expected heading to start with {expected_level} '#' characters, got: {result[:10]}"
        
        # Property: Count the number of # characters at the start
        hash_count = 0
        for char in result:
            if char == "#":
                hash_count += 1
            else:
                break
        
        assert hash_count == expected_level, \
            f"Expected {expected_level} '#' characters, got {hash_count}"
        
        # Property: The heading text should be preserved (possibly escaped)
        # The text appears after "# " (hashes + space)
        text_part = result[expected_level + 1:]  # Skip hashes and space
        assert len(text_part) > 0, "Heading text should not be empty"
    
    @given(
        num_headings=st.integers(min_value=2, max_value=10),
        offset=st.integers(min_value=-5, max_value=5),
        data=st.data()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_35_offset_applied_to_all_headings(self, num_headings, offset, data):
        """
        Feature: document-to-markdown-converter
        Property 35: Heading level offset (multiple headings)
        
        For documents with multiple headings, the offset should be consistently
        applied to all headings.
        
        **Validates: Requirements 8.1**
        """
        # Create serializer with the specified offset
        serializer = MarkdownSerializer(heading_offset=offset)
        
        # Generate multiple sections with headings
        sections = []
        heading_data = []
        
        for i in range(num_headings):
            level = data.draw(st.integers(min_value=1, max_value=6))
            text = data.draw(st.text(min_size=1, max_size=50))
            
            # Skip empty or whitespace-only text
            if not text.strip():
                continue
            
            heading = Heading(level=level, text=text)
            section = Section(
                heading=heading,
                content=[Paragraph(text=f"Content {i}", formatting=TextFormatting.NORMAL)]
            )
            sections.append(section)
            heading_data.append((level, text))
        
        # Skip test if no valid headings were generated
        if not heading_data:
            return
        
        # Create document
        doc = InternalDocument(sections=sections)
        
        # Serialize the document
        result = serializer.serialize(doc)
        
        # Property: Result should be a non-empty string
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Property: Each heading should have the offset applied
        for original_level, text in heading_data:
            expected_level = max(1, min(6, original_level + offset))
            expected_prefix = "#" * expected_level + " "
            
            # The heading with the expected prefix should appear in the result
            # Note: We can't do exact text matching due to escaping, but we can
            # verify that headings with the correct level exist
            assert expected_prefix in result, \
                f"Expected to find heading with {expected_level} '#' characters in output"
    
    @given(
        original_level=st.integers(min_value=1, max_value=6),
        offset=st.integers(min_value=-10, max_value=10)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_35_offset_clamping(self, original_level, offset):
        """
        Feature: document-to-markdown-converter
        Property 35: Heading level offset (clamping)
        
        The offset should be applied with proper clamping to ensure the resulting
        level stays within the valid range of 1-6.
        
        **Validates: Requirements 8.1**
        """
        # Create serializer with the specified offset
        serializer = MarkdownSerializer(heading_offset=offset)
        
        # Create a heading
        heading = Heading(level=original_level, text="Test Heading")
        
        # Serialize the heading
        result = serializer.serialize_heading(heading)
        
        # Property: Calculate expected level (clamped to 1-6)
        expected_level = max(1, min(6, original_level + offset))
        
        # Property: The result should have the clamped level
        hash_count = 0
        for char in result:
            if char == "#":
                hash_count += 1
            else:
                break
        
        assert hash_count == expected_level, \
            f"Expected {expected_level} '#' characters (clamped), got {hash_count}"
        
        # Property: Level should never be less than 1
        assert hash_count >= 1, \
            "Heading level should never be less than 1"
        
        # Property: Level should never be greater than 6
        assert hash_count <= 6, \
            "Heading level should never be greater than 6"
    
    @given(
        offset=st.integers(min_value=-10, max_value=10)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_35_offset_preserves_relative_hierarchy(self, offset):
        """
        Feature: document-to-markdown-converter
        Property 35: Heading level offset (hierarchy preservation)
        
        When offset is applied, the relative hierarchy of headings should be
        preserved (unless clamping occurs).
        
        **Validates: Requirements 8.1**
        """
        # Create serializer with the specified offset
        serializer = MarkdownSerializer(heading_offset=offset)
        
        # Create headings at different levels
        h1 = Heading(level=1, text="Level 1")
        h2 = Heading(level=2, text="Level 2")
        h3 = Heading(level=3, text="Level 3")
        
        # Serialize all headings
        result_h1 = serializer.serialize_heading(h1)
        result_h2 = serializer.serialize_heading(h2)
        result_h3 = serializer.serialize_heading(h3)
        
        # Count hashes for each
        def count_hashes(s):
            count = 0
            for char in s:
                if char == "#":
                    count += 1
                else:
                    break
            return count
        
        level_h1 = count_hashes(result_h1)
        level_h2 = count_hashes(result_h2)
        level_h3 = count_hashes(result_h3)
        
        # Property: If no clamping occurs, relative order should be preserved
        # Calculate expected levels
        expected_h1 = max(1, min(6, 1 + offset))
        expected_h2 = max(1, min(6, 2 + offset))
        expected_h3 = max(1, min(6, 3 + offset))
        
        # Verify levels match expected
        assert level_h1 == expected_h1, \
            f"H1 with offset {offset}: expected level {expected_h1}, got {level_h1}"
        assert level_h2 == expected_h2, \
            f"H2 with offset {offset}: expected level {expected_h2}, got {level_h2}"
        assert level_h3 == expected_h3, \
            f"H3 with offset {offset}: expected level {expected_h3}, got {level_h3}"
        
        # Property: If no clamping, h1 <= h2 <= h3 should hold
        if 1 + offset >= 1 and 3 + offset <= 6:
            # No clamping occurred
            assert level_h1 <= level_h2 <= level_h3, \
                "Relative hierarchy should be preserved when no clamping occurs"
    
    @given(
        offset=st.integers(min_value=-10, max_value=10)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_35_zero_offset_is_identity(self, offset):
        """
        Feature: document-to-markdown-converter
        Property 35: Heading level offset (zero offset)
        
        When offset is 0, heading levels should remain unchanged.
        
        **Validates: Requirements 8.1**
        """
        # Create serializer with zero offset
        serializer_zero = MarkdownSerializer(heading_offset=0)
        
        # Test all valid heading levels
        for level in range(1, 7):
            heading = Heading(level=level, text=f"Level {level}")
            result = serializer_zero.serialize_heading(heading)
            
            # Count hashes
            hash_count = 0
            for char in result:
                if char == "#":
                    hash_count += 1
                else:
                    break
            
            # Property: With zero offset, level should be unchanged
            assert hash_count == level, \
                f"With zero offset, level {level} should remain {level}, got {hash_count}"
    
    @given(
        original_level=st.integers(min_value=1, max_value=6),
        offset=st.integers(min_value=-10, max_value=10),
        heading_text=st.text(
            alphabet=st.characters(
                whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'),
                whitelist_characters='!@#$%^&*()_+-=[]{}|;:,.<>?日本語'
            ),
            min_size=1,
            max_size=100
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_property_35_offset_with_special_characters(self, original_level, offset, heading_text):
        """
        Feature: document-to-markdown-converter
        Property 35: Heading level offset (special characters)
        
        Offset should work correctly regardless of the heading text content,
        including special characters and non-ASCII text.
        
        **Validates: Requirements 8.1**
        """
        # Skip empty or whitespace-only text
        if not heading_text.strip():
            return
        
        # Create serializer with the specified offset
        serializer = MarkdownSerializer(heading_offset=offset)
        
        # Create a heading
        heading = Heading(level=original_level, text=heading_text)
        
        # Serialize the heading
        result = serializer.serialize_heading(heading)
        
        # Property: Calculate expected level (clamped to 1-6)
        expected_level = max(1, min(6, original_level + offset))
        
        # Property: Result should start with the correct number of # characters
        hash_count = 0
        for char in result:
            if char == "#":
                hash_count += 1
            else:
                break
        
        assert hash_count == expected_level, \
            f"Expected {expected_level} '#' characters, got {hash_count}"
        
        # Property: Result should have a space after the hashes
        assert result[expected_level] == " ", \
            "There should be a space after the '#' characters"
        
        # Property: The text part should not be empty
        text_part = result[expected_level + 1:]
        assert len(text_part) > 0, \
            "Heading text should not be empty after serialization"


# Run all property tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
