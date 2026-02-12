"""Tests for configuration management.

This module tests the ConversionConfig dataclass and ConfigManager
for loading, saving, and merging configuration.
"""

import pytest
import tempfile
from pathlib import Path

from src.config import ConversionConfig, ConfigManager, TableStyle, ImageFormat
from src.logger import LogLevel


class TestConversionConfig:
    """Tests for ConversionConfig dataclass."""
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        config = ConversionConfig(input_path="test.docx")
        
        assert config.input_path == "test.docx"
        assert config.output_path is None
        assert config.heading_offset == 0
        assert config.table_style == "standard"
        assert config.include_metadata is False
        assert config.output_encoding == "utf-8"
        assert config.extract_images is True
        assert config.enable_ocr is True
        assert config.ocr_language == "eng+jpn"
        assert config.preview_mode is False
        assert config.dry_run is False
        assert config.validate_output is True
        assert config.log_level == LogLevel.INFO
        assert config.max_file_size_mb == 100
    
    def test_custom_values(self):
        """Test setting custom values."""
        config = ConversionConfig(
            input_path="test.docx",
            output_path="output.md",
            heading_offset=1,
            include_metadata=True,
            extract_images=False,
            log_level=LogLevel.DEBUG
        )
        
        assert config.input_path == "test.docx"
        assert config.output_path == "output.md"
        assert config.heading_offset == 1
        assert config.include_metadata is True
        assert config.extract_images is False
        assert config.log_level == LogLevel.DEBUG
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = ConversionConfig(
            input_path="test.docx",
            heading_offset=2,
            log_level=LogLevel.WARNING
        )
        
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict['input_path'] == "test.docx"
        assert config_dict['heading_offset'] == 2
        assert config_dict['log_level'] == "WARNING"
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            'input_path': 'test.docx',
            'output_path': 'output.md',
            'heading_offset': 1,
            'include_metadata': True,
            'log_level': 'DEBUG'
        }
        
        config = ConversionConfig.from_dict(data)
        
        assert config.input_path == 'test.docx'
        assert config.output_path == 'output.md'
        assert config.heading_offset == 1
        assert config.include_metadata is True
        assert config.log_level == LogLevel.DEBUG
    
    def test_from_dict_filters_invalid_keys(self):
        """Test that from_dict filters out invalid keys."""
        data = {
            'input_path': 'test.docx',
            'invalid_key': 'should_be_ignored',
            'another_invalid': 123
        }
        
        config = ConversionConfig.from_dict(data)
        
        assert config.input_path == 'test.docx'
        assert not hasattr(config, 'invalid_key')
        assert not hasattr(config, 'another_invalid')


class TestConfigManager:
    """Tests for ConfigManager class."""
    
    def test_save_and_load_config(self):
        """Test saving and loading configuration from YAML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            
            # Create a config
            original_config = ConversionConfig(
                input_path="test.docx",
                heading_offset=2,
                include_metadata=True,
                extract_images=False,
                ocr_language="eng",
                log_level=LogLevel.DEBUG
            )
            
            # Save it
            manager = ConfigManager()
            manager.save_config(original_config, str(config_path))
            
            # Load it back
            loaded_config = manager.load_config(str(config_path))
            
            # Verify (note: input_path is not saved)
            assert loaded_config.heading_offset == 2
            assert loaded_config.include_metadata is True
            assert loaded_config.extract_images is False
            assert loaded_config.ocr_language == "eng"
            assert loaded_config.log_level == LogLevel.DEBUG
    
    def test_load_nonexistent_file(self):
        """Test loading from non-existent file raises error."""
        manager = ConfigManager()
        
        with pytest.raises(FileNotFoundError):
            manager.load_config("nonexistent.yaml")
    
    def test_load_invalid_yaml(self):
        """Test loading invalid YAML raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "invalid.yaml"
            
            # Write invalid YAML
            with open(config_path, 'w') as f:
                f.write("invalid: yaml: content: [")
            
            manager = ConfigManager()
            
            with pytest.raises(ValueError, match="Invalid YAML"):
                manager.load_config(str(config_path))
    
    def test_merge_configs_cli_precedence(self):
        """Test that CLI config takes precedence over file config."""
        file_config = ConversionConfig(
            input_path="",
            heading_offset=1,
            include_metadata=True,
            extract_images=False,
            log_level=LogLevel.WARNING
        )
        
        cli_config = ConversionConfig(
            input_path="test.docx",
            output_path="output.md",
            heading_offset=2,  # Different from file
            include_metadata=True,  # Same as file
            # extract_images not specified, should use file value
            log_level=LogLevel.INFO  # Default value
        )
        
        manager = ConfigManager()
        merged = manager.merge_configs(file_config, cli_config)
        
        # CLI values should override
        assert merged.input_path == "test.docx"
        assert merged.output_path == "output.md"
        assert merged.heading_offset == 2  # CLI override
        
        # File values should be preserved when CLI uses defaults
        assert merged.extract_images is False  # From file
        assert merged.log_level == LogLevel.WARNING  # From file (CLI had default)
    
    def test_merge_configs_no_file(self):
        """Test merging when file config is None."""
        cli_config = ConversionConfig(
            input_path="test.docx",
            heading_offset=1
        )
        
        manager = ConfigManager()
        merged = manager.merge_configs(None, cli_config)
        
        # Should return CLI config unchanged
        assert merged.input_path == "test.docx"
        assert merged.heading_offset == 1
    
    def test_create_sample_config(self):
        """Test creating a sample configuration file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "sample.yaml"
            
            manager = ConfigManager()
            manager.create_sample_config(str(config_path))
            
            # Verify file was created
            assert config_path.exists()
            
            # Verify it contains expected content
            content = config_path.read_text()
            assert "heading_offset" in content
            assert "extract_images" in content
            assert "ocr_language" in content
            assert "log_level" in content
    
    def test_save_creates_parent_directories(self):
        """Test that save_config creates parent directories if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "subdir" / "config.yaml"
            
            config = ConversionConfig(input_path="test.docx")
            
            manager = ConfigManager()
            manager.save_config(config, str(config_path))
            
            # Verify file was created
            assert config_path.exists()
    
    def test_round_trip_config(self):
        """Test that config can be saved and loaded without data loss."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            
            # Create config with various settings
            original = ConversionConfig(
                input_path="test.docx",
                heading_offset=3,
                table_style="compact",
                include_metadata=True,
                output_encoding="utf-8",
                extract_images=True,
                embed_images_base64=True,
                enable_ocr=False,
                ocr_language="jpn",
                validate_output=False,
                log_level=LogLevel.ERROR,
                max_file_size_mb=200
            )
            
            manager = ConfigManager()
            
            # Save and load
            manager.save_config(original, str(config_path))
            loaded = manager.load_config(str(config_path))
            
            # Verify all settings (except runtime fields)
            assert loaded.heading_offset == original.heading_offset
            assert loaded.table_style == original.table_style
            assert loaded.include_metadata == original.include_metadata
            assert loaded.output_encoding == original.output_encoding
            assert loaded.extract_images == original.extract_images
            assert loaded.embed_images_base64 == original.embed_images_base64
            assert loaded.enable_ocr == original.enable_ocr
            assert loaded.ocr_language == original.ocr_language
            assert loaded.validate_output == original.validate_output
            assert loaded.log_level == original.log_level
            assert loaded.max_file_size_mb == original.max_file_size_mb
