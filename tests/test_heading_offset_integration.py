"""
Integration tests for heading level offset feature.

These tests verify that the heading_offset configuration works correctly
through the entire conversion pipeline from CLI to output.

Requirements: 8.1
"""

import pytest
from pathlib import Path
from src.config import ConversionConfig
from src.conversion_orchestrator import ConversionOrchestrator
from src.logger import Logger, LogLevel
from src.internal_representation import (
    InternalDocument,
    Section,
    Heading,
    Paragraph,
    TextFormatting,
)


class TestHeadingOffsetIntegration:
    """Integration tests for heading offset feature."""
    
    def test_heading_offset_through_orchestrator(self, tmp_path):
        """Test that heading offset works through the conversion orchestrator."""
        # Create a simple test document
        doc = InternalDocument(
            sections=[
                Section(
                    heading=Heading(level=1, text="Main Title"),
                    content=[
                        Paragraph(text="Introduction", formatting=TextFormatting.NORMAL)
                    ]
                ),
                Section(
                    heading=Heading(level=2, text="Section One"),
                    content=[
                        Paragraph(text="Content one", formatting=TextFormatting.NORMAL)
                    ]
                ),
                Section(
                    heading=Heading(level=3, text="Subsection"),
                    content=[
                        Paragraph(text="Content two", formatting=TextFormatting.NORMAL)
                    ]
                )
            ]
        )
        
        # Test with offset=0 (no change)
        config = ConversionConfig(
            input_path="test.docx",
            heading_offset=0
        )
        orchestrator = ConversionOrchestrator(config, Logger(LogLevel.ERROR))
        markdown = orchestrator.serializer.serialize(doc)
        
        assert "# Main Title" in markdown
        assert "## Section One" in markdown
        assert "### Subsection" in markdown
        
        # Test with offset=1 (increase by 1)
        config = ConversionConfig(
            input_path="test.docx",
            heading_offset=1
        )
        orchestrator = ConversionOrchestrator(config, Logger(LogLevel.ERROR))
        markdown = orchestrator.serializer.serialize(doc)
        
        assert "## Main Title" in markdown
        assert "### Section One" in markdown
        assert "#### Subsection" in markdown
        
        # Test with offset=-1 (decrease by 1)
        config = ConversionConfig(
            input_path="test.docx",
            heading_offset=-1
        )
        orchestrator = ConversionOrchestrator(config, Logger(LogLevel.ERROR))
        markdown = orchestrator.serializer.serialize(doc)
        
        # H1 - 1 = H0, clamped to H1
        assert "# Main Title" in markdown
        # H2 - 1 = H1
        assert "# Section One" in markdown
        # H3 - 1 = H2
        assert "## Subsection" in markdown
    
    def test_heading_offset_with_config_file(self, tmp_path):
        """Test that heading offset can be loaded from config file."""
        from src.config import ConfigManager
        
        # Create a config file with heading_offset=2
        config_path = tmp_path / "config.yaml"
        config = ConversionConfig(
            input_path="",
            heading_offset=2,
            include_metadata=False
        )
        
        manager = ConfigManager()
        manager.save_config(config, str(config_path))
        
        # Load the config
        loaded_config = manager.load_config(str(config_path))
        
        # Verify heading_offset was loaded correctly
        assert loaded_config.heading_offset == 2
        
        # Create orchestrator with loaded config
        loaded_config.input_path = "test.docx"
        orchestrator = ConversionOrchestrator(loaded_config, Logger(LogLevel.ERROR))
        
        # Verify the serializer has the correct offset
        assert orchestrator.serializer.heading_offset == 2
    
    def test_heading_offset_preserves_content(self):
        """Test that heading offset doesn't affect document content."""
        doc = InternalDocument(
            sections=[
                Section(
                    heading=Heading(level=1, text="Title"),
                    content=[
                        Paragraph(text="This is important content.", formatting=TextFormatting.NORMAL),
                        Paragraph(text="More content here.", formatting=TextFormatting.BOLD)
                    ]
                )
            ]
        )
        
        # Test with different offsets
        for offset in [-2, -1, 0, 1, 2]:
            config = ConversionConfig(
                input_path="test.docx",
                heading_offset=offset
            )
            orchestrator = ConversionOrchestrator(config, Logger(LogLevel.ERROR))
            markdown = orchestrator.serializer.serialize(doc)
            
            # Content should always be preserved regardless of offset
            assert "This is important content." in markdown
            assert "**More content here.**" in markdown
    
    def test_heading_offset_with_deep_hierarchy(self):
        """Test heading offset with a deep document hierarchy."""
        sections = []
        for level in range(1, 7):
            sections.append(
                Section(
                    heading=Heading(level=level, text=f"Level {level} Heading"),
                    content=[
                        Paragraph(text=f"Content at level {level}", formatting=TextFormatting.NORMAL)
                    ]
                )
            )
        
        doc = InternalDocument(sections=sections)
        
        # Test with offset=1
        config = ConversionConfig(
            input_path="test.docx",
            heading_offset=1
        )
        orchestrator = ConversionOrchestrator(config, Logger(LogLevel.ERROR))
        markdown = orchestrator.serializer.serialize(doc)
        
        # Verify all headings are offset correctly
        assert "## Level 1 Heading" in markdown  # H1 -> H2
        assert "### Level 2 Heading" in markdown # H2 -> H3
        assert "#### Level 3 Heading" in markdown # H3 -> H4
        assert "##### Level 4 Heading" in markdown # H4 -> H5
        assert "###### Level 5 Heading" in markdown # H5 -> H6
        assert "###### Level 6 Heading" in markdown # H6 -> H6 (clamped)
        
        # Verify all content is preserved
        for level in range(1, 7):
            assert f"Content at level {level}" in markdown
    
    def test_heading_offset_cli_override(self, tmp_path):
        """Test that CLI heading_offset overrides config file."""
        from src.config import ConfigManager
        
        # Create a config file with heading_offset=1
        config_path = tmp_path / "config.yaml"
        file_config = ConversionConfig(
            input_path="",
            heading_offset=1
        )
        
        manager = ConfigManager()
        manager.save_config(file_config, str(config_path))
        
        # Load config and merge with CLI config that has heading_offset=2
        loaded_config = manager.load_config(str(config_path))
        cli_config = ConversionConfig(
            input_path="test.docx",
            heading_offset=2  # Different from file
        )
        
        merged_config = manager.merge_configs(loaded_config, cli_config)
        
        # CLI value should take precedence
        assert merged_config.heading_offset == 2
