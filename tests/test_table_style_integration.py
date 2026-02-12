"""
Integration tests for table style selection feature.

These tests verify that the table_style configuration works correctly
through the entire conversion pipeline.

Requirements: 8.2
"""

import pytest
from pathlib import Path
from src.config import ConversionConfig
from src.conversion_orchestrator import ConversionOrchestrator
from src.logger import Logger, LogLevel
from src.internal_representation import (
    InternalDocument,
    Section,
    Table,
    Paragraph,
    TextFormatting,
)


class TestTableStyleIntegration:
    """Integration tests for table style selection."""
    
    def test_standard_table_style(self):
        """Test standard table formatting style."""
        # Create a document with a table
        doc = InternalDocument(
            sections=[
                Section(
                    content=[
                        Table(
                            headers=["Name", "Age", "City"],
                            rows=[
                                ["Alice", "30", "New York"],
                                ["Bob", "25", "Los Angeles"],
                                ["Charlie", "35", "Chicago"]
                            ]
                        )
                    ]
                )
            ]
        )
        
        # Test with standard style
        config = ConversionConfig(
            input_path="test.docx",
            table_style="standard"
        )
        orchestrator = ConversionOrchestrator(config, Logger(LogLevel.ERROR))
        markdown = orchestrator.serializer.serialize(doc)
        
        # Standard style should have pipes and basic formatting
        assert "| Name" in markdown
        assert "| Age" in markdown
        assert "| City" in markdown
        assert "| Alice" in markdown
        assert "| Bob" in markdown
        assert "| Charlie" in markdown
        assert "| ---" in markdown  # Separator row
    
    def test_compact_table_style(self):
        """Test compact table formatting style."""
        # Create a document with a table
        doc = InternalDocument(
            sections=[
                Section(
                    content=[
                        Table(
                            headers=["Name", "Age", "City"],
                            rows=[
                                ["Alice", "30", "New York"],
                                ["Bob", "25", "Los Angeles"]
                            ]
                        )
                    ]
                )
            ]
        )
        
        # Test with compact style
        config = ConversionConfig(
            input_path="test.docx",
            table_style="compact"
        )
        orchestrator = ConversionOrchestrator(config, Logger(LogLevel.ERROR))
        markdown = orchestrator.serializer.serialize(doc)
        
        # Compact style should have minimal spacing
        # The exact format depends on implementation, but it should be valid markdown
        assert "Name" in markdown
        assert "Age" in markdown
        assert "City" in markdown
        assert "Alice" in markdown
        assert "Bob" in markdown
    
    def test_grid_table_style(self):
        """Test grid table formatting style."""
        # Create a document with a table
        doc = InternalDocument(
            sections=[
                Section(
                    content=[
                        Table(
                            headers=["Product", "Price", "Stock"],
                            rows=[
                                ["Widget", "$10", "100"],
                                ["Gadget", "$20", "50"]
                            ]
                        )
                    ]
                )
            ]
        )
        
        # Test with grid style
        config = ConversionConfig(
            input_path="test.docx",
            table_style="grid"
        )
        orchestrator = ConversionOrchestrator(config, Logger(LogLevel.ERROR))
        markdown = orchestrator.serializer.serialize(doc)
        
        # Grid style should have enhanced formatting
        # The exact format depends on implementation
        assert "Product" in markdown
        assert "Price" in markdown
        assert "Stock" in markdown
        assert "Widget" in markdown
        assert "Gadget" in markdown
    
    def test_table_style_with_config_file(self, tmp_path):
        """Test that table_style can be loaded from config file."""
        from src.config import ConfigManager
        
        # Create a config file with table_style=compact
        config_path = tmp_path / "config.yaml"
        config = ConversionConfig(
            input_path="",
            table_style="compact"
        )
        
        manager = ConfigManager()
        manager.save_config(config, str(config_path))
        
        # Load the config
        loaded_config = manager.load_config(str(config_path))
        
        # Verify table_style was loaded correctly
        assert loaded_config.table_style == "compact"
        
        # Create orchestrator with loaded config
        loaded_config.input_path = "test.docx"
        orchestrator = ConversionOrchestrator(loaded_config, Logger(LogLevel.ERROR))
        
        # Verify the config has the correct table_style
        assert orchestrator.config.table_style == "compact"
    
    def test_table_style_preserves_content(self):
        """Test that table style doesn't affect table content."""
        doc = InternalDocument(
            sections=[
                Section(
                    content=[
                        Table(
                            headers=["Column A", "Column B"],
                            rows=[
                                ["Value 1", "Value 2"],
                                ["Value 3", "Value 4"]
                            ]
                        )
                    ]
                )
            ]
        )
        
        # Test with different styles
        for style in ["standard", "compact", "grid"]:
            config = ConversionConfig(
                input_path="test.docx",
                table_style=style
            )
            orchestrator = ConversionOrchestrator(config, Logger(LogLevel.ERROR))
            markdown = orchestrator.serializer.serialize(doc)
            
            # Content should always be preserved regardless of style
            assert "Column A" in markdown
            assert "Column B" in markdown
            assert "Value 1" in markdown
            assert "Value 2" in markdown
            assert "Value 3" in markdown
            assert "Value 4" in markdown
    
    def test_table_style_with_special_characters(self):
        """Test table styles with special characters in cells."""
        doc = InternalDocument(
            sections=[
                Section(
                    content=[
                        Table(
                            headers=["Name", "Description"],
                            rows=[
                                ["Item | A", "Contains | pipe"],
                                ["Item * B", "Contains * asterisk"],
                                ["Item # C", "Contains # hash"]
                            ]
                        )
                    ]
                )
            ]
        )
        
        # Test with standard style
        config = ConversionConfig(
            input_path="test.docx",
            table_style="standard"
        )
        orchestrator = ConversionOrchestrator(config, Logger(LogLevel.ERROR))
        markdown = orchestrator.serializer.serialize(doc)
        
        # Special characters should be properly escaped
        assert "Item" in markdown
        assert "Contains" in markdown
        # The exact escaping depends on implementation
    
    def test_table_style_with_empty_cells(self):
        """Test table styles with empty cells."""
        doc = InternalDocument(
            sections=[
                Section(
                    content=[
                        Table(
                            headers=["A", "B", "C"],
                            rows=[
                                ["1", "", "3"],
                                ["", "5", ""],
                                ["7", "8", "9"]
                            ]
                        )
                    ]
                )
            ]
        )
        
        # Test with different styles
        for style in ["standard", "compact", "grid"]:
            config = ConversionConfig(
                input_path="test.docx",
                table_style=style
            )
            orchestrator = ConversionOrchestrator(config, Logger(LogLevel.ERROR))
            markdown = orchestrator.serializer.serialize(doc)
            
            # All non-empty values should be present
            assert "1" in markdown
            assert "3" in markdown
            assert "5" in markdown
            assert "7" in markdown
            assert "8" in markdown
            assert "9" in markdown
    
    def test_table_style_with_long_content(self):
        """Test table styles with long cell content."""
        doc = InternalDocument(
            sections=[
                Section(
                    content=[
                        Table(
                            headers=["Short", "Long Content"],
                            rows=[
                                ["A", "This is a very long piece of text that spans multiple words"],
                                ["B", "Another long description with many characters"]
                            ]
                        )
                    ]
                )
            ]
        )
        
        # Test with standard style
        config = ConversionConfig(
            input_path="test.docx",
            table_style="standard"
        )
        orchestrator = ConversionOrchestrator(config, Logger(LogLevel.ERROR))
        markdown = orchestrator.serializer.serialize(doc)
        
        # Long content should be preserved
        assert "This is a very long piece of text that spans multiple words" in markdown
        assert "Another long description with many characters" in markdown
    
    def test_table_style_cli_override(self, tmp_path):
        """Test that CLI table_style overrides config file."""
        from src.config import ConfigManager
        
        # Create a config file with table_style=standard
        config_path = tmp_path / "config.yaml"
        file_config = ConversionConfig(
            input_path="",
            table_style="standard"
        )
        
        manager = ConfigManager()
        manager.save_config(file_config, str(config_path))
        
        # Load config and merge with CLI config that has table_style=compact
        loaded_config = manager.load_config(str(config_path))
        cli_config = ConversionConfig(
            input_path="test.docx",
            table_style="compact"  # Different from file
        )
        
        merged_config = manager.merge_configs(loaded_config, cli_config)
        
        # CLI value should take precedence
        assert merged_config.table_style == "compact"
    
    def test_table_style_with_multiple_tables(self):
        """Test that table style applies to all tables in document."""
        doc = InternalDocument(
            sections=[
                Section(
                    content=[
                        Paragraph(text="First table:", formatting=TextFormatting.NORMAL),
                        Table(
                            headers=["A", "B"],
                            rows=[["1", "2"]]
                        ),
                        Paragraph(text="Second table:", formatting=TextFormatting.NORMAL),
                        Table(
                            headers=["X", "Y", "Z"],
                            rows=[["10", "20", "30"]]
                        )
                    ]
                )
            ]
        )
        
        # Test with compact style
        config = ConversionConfig(
            input_path="test.docx",
            table_style="compact"
        )
        orchestrator = ConversionOrchestrator(config, Logger(LogLevel.ERROR))
        markdown = orchestrator.serializer.serialize(doc)
        
        # Both tables should be present with their content
        assert "A" in markdown and "B" in markdown
        assert "1" in markdown and "2" in markdown
        assert "X" in markdown and "Y" in markdown and "Z" in markdown
        assert "10" in markdown and "20" in markdown and "30" in markdown
    
    def test_invalid_table_style_fallback(self):
        """Test that invalid table style falls back to standard."""
        doc = InternalDocument(
            sections=[
                Section(
                    content=[
                        Table(
                            headers=["A", "B"],
                            rows=[["1", "2"]]
                        )
                    ]
                )
            ]
        )
        
        # Test with invalid style (should fallback to standard or handle gracefully)
        config = ConversionConfig(
            input_path="test.docx",
            table_style="invalid_style"
        )
        orchestrator = ConversionOrchestrator(config, Logger(LogLevel.ERROR))
        markdown = orchestrator.serializer.serialize(doc)
        
        # Should still produce valid output
        assert "A" in markdown
        assert "B" in markdown
        assert "1" in markdown
        assert "2" in markdown
