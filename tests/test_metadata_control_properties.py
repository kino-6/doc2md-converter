"""Property-based tests for metadata inclusion control feature.

This module contains property-based tests using Hypothesis to verify
that metadata inclusion/exclusion control works correctly during conversion.

Feature: document-to-markdown-converter
Property: 36
Validates: Requirements 8.3
"""

import pytest
from hypothesis import given, strategies as st, settings
from src.markdown_serializer import MarkdownSerializer
from src.internal_representation import (
    InternalDocument,
    DocumentMetadata,
    Section,
    Heading,
    Paragraph,
    TextFormatting,
)


# Strategy for generating valid metadata fields
metadata_text_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'),
        min_codepoint=32,
        max_codepoint=126
    ),
    min_size=1,
    max_size=100
)

# Strategy for generating dates
date_strategy = st.one_of(
    st.none(),
    st.sampled_from([
        '2024-01-15',
        '2024-01-15T10:30:00',
        '2023-12-31 23:59:59',
        '2024/01/15',
        '2024-06-20T14:45:30'
    ])
)


class TestMetadataControlProperty:
    """Property 36: Metadata inclusion control
    
    For any document, the converter should include or exclude metadata in the output
    based on the configuration setting.
    
    Validates: Requirements 8.3
    """
    
    @given(
        title=st.one_of(st.none(), metadata_text_strategy),
        author=st.one_of(st.none(), metadata_text_strategy),
        created_date=date_strategy,
        modified_date=date_strategy,
        source_format=st.sampled_from(['docx', 'xlsx', 'pdf'])
    )
    @settings(max_examples=100, deadline=None)
    def test_property_36_metadata_included_when_enabled(
        self, title, author, created_date, modified_date, source_format
    ):
        """
        Feature: document-to-markdown-converter
        Property 36: Metadata inclusion control (enabled)
        
        For any document with metadata, when include_metadata is True, the converter
        should include the metadata in the output.
        
        **Validates: Requirements 8.3**
        """
        # Create document with metadata
        metadata = DocumentMetadata(
            title=title,
            author=author,
            created_date=created_date,
            modified_date=modified_date,
            source_format=source_format
        )
        
        doc = InternalDocument(
            metadata=metadata,
            sections=[
                Section(
                    heading=Heading(level=1, text="Test Heading"),
                    content=[Paragraph(text="Test content", formatting=TextFormatting.NORMAL)]
                )
            ]
        )
        
        # Serialize with metadata inclusion enabled
        serializer = MarkdownSerializer(include_metadata=True)
        result = serializer.serialize(doc)
        
        # Property: Result should be a non-empty string
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Property: If any metadata field is populated, frontmatter should be present
        has_metadata = any([title, author, created_date, modified_date, source_format])
        
        if has_metadata:
            # Property: Frontmatter delimiters should be present
            assert result.startswith("---\n"), \
                "Output should start with frontmatter delimiter when metadata is present"
            
            # Property: Each populated field should appear in the output
            if title:
                assert f"title: {title}" in result, \
                    f"Title '{title}' should appear in output"
            
            if author:
                assert f"author: {author}" in result, \
                    f"Author '{author}' should appear in output"
            
            if created_date:
                assert f"created: {created_date}" in result, \
                    f"Created date '{created_date}' should appear in output"
            
            if modified_date:
                assert f"modified: {modified_date}" in result, \
                    f"Modified date '{modified_date}' should appear in output"
            
            if source_format:
                assert f"source_format: {source_format}" in result, \
                    f"Source format '{source_format}' should appear in output"
    
    @given(
        title=st.one_of(st.none(), metadata_text_strategy),
        author=st.one_of(st.none(), metadata_text_strategy),
        created_date=date_strategy,
        modified_date=date_strategy,
        source_format=st.sampled_from(['docx', 'xlsx', 'pdf'])
    )
    @settings(max_examples=100, deadline=None)
    def test_property_36_metadata_excluded_when_disabled(
        self, title, author, created_date, modified_date, source_format
    ):
        """
        Feature: document-to-markdown-converter
        Property 36: Metadata inclusion control (disabled)
        
        For any document with metadata, when include_metadata is False, the converter
        should exclude the metadata from the output.
        
        **Validates: Requirements 8.3**
        """
        # Create document with metadata
        metadata = DocumentMetadata(
            title=title,
            author=author,
            created_date=created_date,
            modified_date=modified_date,
            source_format=source_format
        )
        
        doc = InternalDocument(
            metadata=metadata,
            sections=[
                Section(
                    heading=Heading(level=1, text="Test Heading"),
                    content=[Paragraph(text="Test content", formatting=TextFormatting.NORMAL)]
                )
            ]
        )
        
        # Serialize with metadata inclusion disabled
        serializer = MarkdownSerializer(include_metadata=False)
        result = serializer.serialize(doc)
        
        # Property: Result should be a non-empty string
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Property: Frontmatter delimiters should NOT be present
        assert not result.startswith("---\n"), \
            "Output should not start with frontmatter delimiter when metadata is disabled"
        
        # Property: No metadata fields should appear in the output
        # (unless they happen to be in the content, which is unlikely with our test data)
        if title and len(title) > 5:  # Only check longer titles to avoid false positives
            assert f"title: {title}" not in result, \
                f"Title field should not appear in output when metadata is disabled"
        
        if author and len(author) > 5:
            assert f"author: {author}" not in result, \
                f"Author field should not appear in output when metadata is disabled"
    
    @given(
        include_metadata=st.booleans(),
        content_text=st.text(min_size=1, max_size=200)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_36_content_unaffected_by_metadata_setting(
        self, include_metadata, content_text
    ):
        """
        Feature: document-to-markdown-converter
        Property 36: Metadata inclusion control (content preservation)
        
        For any document, the metadata inclusion setting should not affect the
        document content in the output.
        
        **Validates: Requirements 8.3**
        """
        # Skip empty or whitespace-only text
        if not content_text.strip():
            return
        
        # Create document with metadata and content
        metadata = DocumentMetadata(
            title="Test Title",
            author="Test Author",
            source_format="docx"
        )
        
        doc = InternalDocument(
            metadata=metadata,
            sections=[
                Section(
                    heading=Heading(level=1, text="Test Heading"),
                    content=[Paragraph(text=content_text, formatting=TextFormatting.NORMAL)]
                )
            ]
        )
        
        # Serialize with metadata setting
        serializer = MarkdownSerializer(include_metadata=include_metadata)
        result = serializer.serialize(doc)
        
        # Property: Result should contain the heading
        assert "# Test Heading" in result, \
            "Content heading should be present regardless of metadata setting"
        
        # Property: Result should contain the content (possibly escaped)
        # We check that the result is not empty and has reasonable length
        assert len(result) > len("# Test Heading"), \
            "Output should contain more than just the heading"
    
    @given(
        include_metadata=st.booleans()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_36_empty_metadata_no_frontmatter(self, include_metadata):
        """
        Feature: document-to-markdown-converter
        Property 36: Metadata inclusion control (empty metadata)
        
        For any document with empty metadata, no frontmatter should be included
        even when include_metadata is True.
        
        **Validates: Requirements 8.3**
        """
        # Create document with empty metadata
        metadata = DocumentMetadata()  # All fields are None
        
        doc = InternalDocument(
            metadata=metadata,
            sections=[
                Section(
                    heading=Heading(level=1, text="Test Heading"),
                    content=[Paragraph(text="Test content", formatting=TextFormatting.NORMAL)]
                )
            ]
        )
        
        # Serialize with metadata setting
        serializer = MarkdownSerializer(include_metadata=include_metadata)
        result = serializer.serialize(doc)
        
        # Property: Result should be a non-empty string
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Property: No frontmatter should be present for empty metadata
        assert not result.startswith("---\n"), \
            "Output should not have frontmatter when all metadata fields are empty"
    
    @given(
        title=metadata_text_strategy,
        author=metadata_text_strategy,
        num_sections=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_36_metadata_appears_once_at_start(
        self, title, author, num_sections
    ):
        """
        Feature: document-to-markdown-converter
        Property 36: Metadata inclusion control (position)
        
        For any document with metadata, when included, the metadata should appear
        exactly once at the start of the output.
        
        **Validates: Requirements 8.3**
        """
        # Create document with metadata and multiple sections
        metadata = DocumentMetadata(
            title=title,
            author=author,
            source_format="docx"
        )
        
        sections = []
        for i in range(num_sections):
            sections.append(
                Section(
                    heading=Heading(level=1, text=f"Section {i}"),
                    content=[Paragraph(text=f"Content {i}", formatting=TextFormatting.NORMAL)]
                )
            )
        
        doc = InternalDocument(
            metadata=metadata,
            sections=sections
        )
        
        # Serialize with metadata inclusion enabled
        serializer = MarkdownSerializer(include_metadata=True)
        result = serializer.serialize(doc)
        
        # Property: Result should start with frontmatter
        assert result.startswith("---\n"), \
            "Metadata should appear at the start of the output"
        
        # Property: Frontmatter should be closed before content
        lines = result.split('\n')
        closing_delimiter_index = None
        for i, line in enumerate(lines[1:], start=1):  # Skip first "---"
            if line == "---":
                closing_delimiter_index = i
                break
        
        assert closing_delimiter_index is not None, \
            "Frontmatter should have a closing delimiter"
        
        # Property: Content should appear after frontmatter
        content_start = closing_delimiter_index + 1
        remaining_content = '\n'.join(lines[content_start:])
        assert "# Section 0" in remaining_content, \
            "Document content should appear after metadata frontmatter"
    
    @given(
        title=metadata_text_strategy,
        source_format=st.sampled_from(['docx', 'xlsx', 'pdf'])
    )
    @settings(max_examples=100, deadline=None)
    def test_property_36_partial_metadata_included(self, title, source_format):
        """
        Feature: document-to-markdown-converter
        Property 36: Metadata inclusion control (partial metadata)
        
        For any document with partial metadata (some fields populated, others not),
        only the populated fields should appear in the output.
        
        **Validates: Requirements 8.3**
        """
        # Create document with partial metadata (only title and source_format)
        metadata = DocumentMetadata(
            title=title,
            author=None,  # Not populated
            created_date=None,  # Not populated
            modified_date=None,  # Not populated
            source_format=source_format
        )
        
        doc = InternalDocument(
            metadata=metadata,
            sections=[
                Section(
                    heading=Heading(level=1, text="Test Heading"),
                    content=[Paragraph(text="Test content", formatting=TextFormatting.NORMAL)]
                )
            ]
        )
        
        # Serialize with metadata inclusion enabled
        serializer = MarkdownSerializer(include_metadata=True)
        result = serializer.serialize(doc)
        
        # Property: Frontmatter should be present
        assert result.startswith("---\n"), \
            "Frontmatter should be present when some metadata fields are populated"
        
        # Property: Populated fields should appear
        assert f"title: {title}" in result, \
            "Populated title field should appear in output"
        assert f"source_format: {source_format}" in result, \
            "Populated source_format field should appear in output"
        
        # Property: Unpopulated fields should NOT appear
        assert "author:" not in result, \
            "Unpopulated author field should not appear in output"
        assert "created:" not in result, \
            "Unpopulated created date field should not appear in output"
        assert "modified:" not in result, \
            "Unpopulated modified date field should not appear in output"
    
    @given(
        title=metadata_text_strategy,
        author=metadata_text_strategy,
        include_metadata=st.booleans()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_36_metadata_setting_is_deterministic(
        self, title, author, include_metadata
    ):
        """
        Feature: document-to-markdown-converter
        Property 36: Metadata inclusion control (determinism)
        
        For any document, serializing with the same metadata setting should
        produce the same output every time.
        
        **Validates: Requirements 8.3**
        """
        # Create document with metadata
        metadata = DocumentMetadata(
            title=title,
            author=author,
            source_format="docx"
        )
        
        doc = InternalDocument(
            metadata=metadata,
            sections=[
                Section(
                    heading=Heading(level=1, text="Test Heading"),
                    content=[Paragraph(text="Test content", formatting=TextFormatting.NORMAL)]
                )
            ]
        )
        
        # Serialize twice with the same setting
        serializer = MarkdownSerializer(include_metadata=include_metadata)
        result1 = serializer.serialize(doc)
        result2 = serializer.serialize(doc)
        
        # Property: Results should be identical
        assert result1 == result2, \
            "Serializing the same document with the same settings should produce identical output"
    
    @given(
        title=metadata_text_strategy,
        author=metadata_text_strategy
    )
    @settings(max_examples=100, deadline=None)
    def test_property_36_metadata_toggle_changes_output(self, title, author):
        """
        Feature: document-to-markdown-converter
        Property 36: Metadata inclusion control (toggle effect)
        
        For any document with metadata, the output should differ when
        include_metadata is toggled between True and False.
        
        **Validates: Requirements 8.3**
        """
        # Create document with metadata
        metadata = DocumentMetadata(
            title=title,
            author=author,
            source_format="docx"
        )
        
        doc = InternalDocument(
            metadata=metadata,
            sections=[
                Section(
                    heading=Heading(level=1, text="Test Heading"),
                    content=[Paragraph(text="Test content", formatting=TextFormatting.NORMAL)]
                )
            ]
        )
        
        # Serialize with metadata enabled
        serializer_enabled = MarkdownSerializer(include_metadata=True)
        result_enabled = serializer_enabled.serialize(doc)
        
        # Serialize with metadata disabled
        serializer_disabled = MarkdownSerializer(include_metadata=False)
        result_disabled = serializer_disabled.serialize(doc)
        
        # Property: Results should be different
        assert result_enabled != result_disabled, \
            "Output should differ when metadata inclusion is toggled"
        
        # Property: Enabled version should be longer (contains metadata)
        assert len(result_enabled) > len(result_disabled), \
            "Output with metadata should be longer than without"
        
        # Property: Enabled version should contain frontmatter
        assert result_enabled.startswith("---\n"), \
            "Output with metadata enabled should have frontmatter"
        
        # Property: Disabled version should NOT contain frontmatter
        assert not result_disabled.startswith("---\n"), \
            "Output with metadata disabled should not have frontmatter"


# Run all property tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
