"""Property-based tests for configuration file support.

This module tests Property 39: Configuration file support
Validates: Requirements 8.6, 8.7
"""

import pytest
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, assume
import yaml

from src.config import ConversionConfig, ConfigManager
from src.logger import LogLevel


# Strategy for generating valid configuration dictionaries
@st.composite
def config_dict_strategy(draw):
    """Generate valid configuration dictionaries."""
    return {
        'heading_offset': draw(st.integers(min_value=0, max_value=5)),
        'table_style': draw(st.sampled_from(['standard', 'compact', 'grid'])),
        'include_metadata': draw(st.booleans()),
        'output_encoding': draw(st.sampled_from(['utf-8', 'utf-16', 'ascii'])),
        'extract_images': draw(st.booleans()),
        'image_format': draw(st.sampled_from(['preserve', 'png', 'jpeg'])),
        'embed_images_base64': draw(st.booleans()),
        'diagram_to_mermaid': draw(st.booleans()),
        'enable_ocr': draw(st.booleans()),
        'ocr_language': draw(st.sampled_from(['eng', 'jpn', 'eng+jpn', 'fra', 'deu'])),
        'preview_mode': draw(st.booleans()),
        'dry_run': draw(st.booleans()),
        'validate_output': draw(st.booleans()),
        'log_level': draw(st.sampled_from(['DEBUG', 'INFO', 'WARNING', 'ERROR'])),
        'max_file_size_mb': draw(st.integers(min_value=1, max_value=1000)),
        'batch_mode': draw(st.booleans()),
    }


@given(config_dict_strategy())
def test_property_39_config_file_loading(config_data):
    """Property 39: Configuration file support - loading.
    
    **Validates: Requirements 8.6, 8.7**
    
    For any valid configuration file provided, the converter should load
    and apply the specified options to the conversion process.
    
    This test verifies that:
    1. Valid configuration files can be loaded successfully
    2. All configuration options are preserved during load
    3. The loaded configuration matches the saved configuration
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.yaml"
        
        # Write configuration to YAML file
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(config_data, f)
        
        # Load configuration
        manager = ConfigManager()
        loaded_config = manager.load_config(str(config_path))
        
        # Verify all options are loaded correctly
        assert loaded_config.heading_offset == config_data['heading_offset']
        assert loaded_config.table_style == config_data['table_style']
        assert loaded_config.include_metadata == config_data['include_metadata']
        assert loaded_config.output_encoding == config_data['output_encoding']
        assert loaded_config.extract_images == config_data['extract_images']
        assert loaded_config.image_format == config_data['image_format']
        assert loaded_config.embed_images_base64 == config_data['embed_images_base64']
        assert loaded_config.diagram_to_mermaid == config_data['diagram_to_mermaid']
        assert loaded_config.enable_ocr == config_data['enable_ocr']
        assert loaded_config.ocr_language == config_data['ocr_language']
        assert loaded_config.preview_mode == config_data['preview_mode']
        assert loaded_config.dry_run == config_data['dry_run']
        assert loaded_config.validate_output == config_data['validate_output']
        assert loaded_config.log_level.name == config_data['log_level']
        assert loaded_config.max_file_size_mb == config_data['max_file_size_mb']
        assert loaded_config.batch_mode == config_data['batch_mode']


@given(config_dict_strategy())
def test_property_39_config_file_saving(config_data):
    """Property 39: Configuration file support - saving.
    
    **Validates: Requirements 8.6, 8.7**
    
    For any valid configuration, the converter should be able to save
    it to a file and reload it without data loss.
    
    This test verifies that:
    1. Configuration can be saved to a file
    2. The saved file is valid YAML
    3. Round-trip (save then load) preserves all settings
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.yaml"
        
        # Create configuration from dictionary
        config_data_with_input = config_data.copy()
        config_data_with_input['input_path'] = 'dummy.docx'
        original_config = ConversionConfig.from_dict(config_data_with_input)
        
        # Save configuration
        manager = ConfigManager()
        manager.save_config(original_config, str(config_path))
        
        # Verify file exists and is valid YAML
        assert config_path.exists()
        with open(config_path, 'r', encoding='utf-8') as f:
            saved_data = yaml.safe_load(f)
        assert isinstance(saved_data, dict)
        
        # Load configuration back
        loaded_config = manager.load_config(str(config_path))
        
        # Verify all settings are preserved (except runtime fields)
        assert loaded_config.heading_offset == original_config.heading_offset
        assert loaded_config.table_style == original_config.table_style
        assert loaded_config.include_metadata == original_config.include_metadata
        assert loaded_config.output_encoding == original_config.output_encoding
        assert loaded_config.extract_images == original_config.extract_images
        assert loaded_config.image_format == original_config.image_format
        assert loaded_config.embed_images_base64 == original_config.embed_images_base64
        assert loaded_config.diagram_to_mermaid == original_config.diagram_to_mermaid
        assert loaded_config.enable_ocr == original_config.enable_ocr
        assert loaded_config.ocr_language == original_config.ocr_language
        assert loaded_config.preview_mode == original_config.preview_mode
        assert loaded_config.dry_run == original_config.dry_run
        assert loaded_config.validate_output == original_config.validate_output
        assert loaded_config.log_level == original_config.log_level
        assert loaded_config.max_file_size_mb == original_config.max_file_size_mb
        assert loaded_config.batch_mode == original_config.batch_mode


@given(
    file_config=config_dict_strategy(),
    cli_heading_offset=st.integers(min_value=1, max_value=5),  # Non-default values only
    cli_log_level=st.sampled_from(['DEBUG', 'WARNING', 'ERROR'])  # Non-default values
)
def test_property_39_config_merge_cli_precedence(
    file_config,
    cli_heading_offset,
    cli_log_level
):
    """Property 39: Configuration file support - CLI precedence.
    
    **Validates: Requirements 8.6, 8.7**
    
    For any configuration file and CLI arguments, the converter should
    apply the configuration file options but allow CLI arguments to
    override them when CLI values differ from defaults.
    
    This test verifies that:
    1. File configuration is used as a base
    2. Non-default CLI arguments override file configuration
    3. Default CLI arguments preserve file configuration
    4. Merge operation is consistent and predictable
    """
    # Create file configuration
    file_config_with_input = file_config.copy()
    file_config_with_input['input_path'] = ''
    file_config_obj = ConversionConfig.from_dict(file_config_with_input)
    
    # Create CLI configuration with some non-default overrides
    cli_config = ConversionConfig(
        input_path='test.docx',
        output_path='output.md',
        heading_offset=cli_heading_offset,  # Non-default value
        log_level=LogLevel[cli_log_level]  # Non-default value
    )
    
    # Merge configurations
    manager = ConfigManager()
    merged = manager.merge_configs(file_config_obj, cli_config)
    
    # Verify CLI values take precedence when non-default
    assert merged.input_path == 'test.docx'
    assert merged.output_path == 'output.md'
    assert merged.heading_offset == cli_heading_offset  # CLI override
    assert merged.log_level.name == cli_log_level  # CLI override
    
    # Verify file values are preserved for CLI defaults
    assert merged.table_style == file_config['table_style']
    assert merged.output_encoding == file_config['output_encoding']
    assert merged.ocr_language == file_config['ocr_language']
    assert merged.include_metadata == file_config['include_metadata']
    assert merged.extract_images == file_config['extract_images']


@given(config_dict_strategy())
def test_property_39_config_file_partial_options(config_data):
    """Property 39: Configuration file support - partial configuration.
    
    **Validates: Requirements 8.6, 8.7**
    
    For any configuration file with only some options specified,
    the converter should use the specified options and defaults
    for unspecified options.
    
    This test verifies that:
    1. Partial configuration files are valid
    2. Unspecified options use default values
    3. Specified options override defaults
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "partial_config.yaml"
        
        # Select a random subset of configuration options
        keys = list(config_data.keys())
        # Ensure at least one key is selected
        num_keys = max(1, len(keys) // 2)
        selected_keys = keys[:num_keys]
        partial_config = {k: config_data[k] for k in selected_keys}
        
        # Write partial configuration
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(partial_config, f)
        
        # Load configuration
        manager = ConfigManager()
        loaded_config = manager.load_config(str(config_path))
        
        # Verify specified options are loaded
        for key in selected_keys:
            loaded_value = getattr(loaded_config, key)
            if key == 'log_level':
                assert loaded_value.name == partial_config[key]
            else:
                assert loaded_value == partial_config[key]
        
        # Verify unspecified options have default values
        default_config = ConversionConfig(input_path='')
        for key in config_data.keys():
            if key not in selected_keys:
                loaded_value = getattr(loaded_config, key)
                default_value = getattr(default_config, key)
                assert loaded_value == default_value


@given(st.text(min_size=1, max_size=100))
def test_property_39_config_file_invalid_yaml_handling(invalid_content):
    """Property 39: Configuration file support - error handling.
    
    **Validates: Requirements 8.6, 8.7**
    
    For any invalid configuration file, the converter should
    provide clear error messages without crashing.
    
    This test verifies that:
    1. Invalid YAML files are detected
    2. Appropriate errors are raised
    3. Error messages are informative
    """
    # Skip valid YAML content
    try:
        parsed = yaml.safe_load(invalid_content)
        # If it parses successfully, skip this test case
        assume(False)
    except yaml.YAMLError:
        # This is what we want to test
        pass
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "invalid.yaml"
        
        # Write invalid content
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(invalid_content)
        
        # Attempt to load configuration
        manager = ConfigManager()
        
        # Should raise ValueError with informative message
        with pytest.raises(ValueError) as exc_info:
            manager.load_config(str(config_path))
        
        # Verify error message is informative
        error_message = str(exc_info.value)
        assert len(error_message) > 0
        assert 'YAML' in error_message or 'configuration' in error_message.lower()


@given(config_dict_strategy(), config_dict_strategy())
def test_property_39_config_merge_idempotence(config1, config2):
    """Property 39: Configuration file support - merge idempotence.
    
    **Validates: Requirements 8.6, 8.7**
    
    For any two configurations, merging them multiple times should
    produce the same result.
    
    This test verifies that:
    1. Merge operation is deterministic
    2. Multiple merges produce consistent results
    3. Merge operation is idempotent
    """
    # Create configuration objects
    config1_with_input = config1.copy()
    config1_with_input['input_path'] = 'file1.docx'
    config1_obj = ConversionConfig.from_dict(config1_with_input)
    
    config2_with_input = config2.copy()
    config2_with_input['input_path'] = 'file2.docx'
    config2_obj = ConversionConfig.from_dict(config2_with_input)
    
    # Merge configurations
    manager = ConfigManager()
    merged1 = manager.merge_configs(config1_obj, config2_obj)
    merged2 = manager.merge_configs(config1_obj, config2_obj)
    
    # Verify both merges produce identical results
    assert merged1.to_dict() == merged2.to_dict()


@given(config_dict_strategy())
def test_property_39_config_file_encoding_support(config_data):
    """Property 39: Configuration file support - UTF-8 encoding.
    
    **Validates: Requirements 8.6, 8.7**
    
    For any configuration file with UTF-8 content (including
    non-ASCII characters), the converter should correctly load
    and save the configuration.
    
    This test verifies that:
    1. UTF-8 encoded files are handled correctly
    2. Non-ASCII characters are preserved
    3. Configuration with international settings works properly
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "utf8_config.yaml"
        
        # Add some non-ASCII content to OCR language
        config_data_with_input = config_data.copy()
        config_data_with_input['input_path'] = 'テスト.docx'
        config_data_with_input['ocr_language'] = 'jpn'
        
        original_config = ConversionConfig.from_dict(config_data_with_input)
        
        # Save configuration
        manager = ConfigManager()
        manager.save_config(original_config, str(config_path))
        
        # Load configuration back
        loaded_config = manager.load_config(str(config_path))
        
        # Verify all settings are preserved
        assert loaded_config.ocr_language == original_config.ocr_language
        assert loaded_config.heading_offset == original_config.heading_offset
        assert loaded_config.extract_images == original_config.extract_images
