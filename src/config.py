"""Configuration management for Document to Markdown Converter.

This module provides configuration data classes and the ConfigManager
for loading, saving, and merging configuration from files and CLI arguments.
"""

from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any
import yaml

from src.logger import LogLevel


class TableStyle(Enum):
    """Table formatting styles."""
    STANDARD = "standard"
    COMPACT = "compact"
    GRID = "grid"


class ImageFormat(Enum):
    """Image format handling modes."""
    PRESERVE = "preserve"
    PNG = "png"
    JPEG = "jpeg"


@dataclass
class ConversionConfig:
    """Configuration for document conversion.

    This dataclass contains all configuration options for the conversion process,
    including input/output paths, formatting options, image handling, OCR settings,
    proofreading options, and operational modes.

    Attributes:
        input_path: Path to input file
        output_path: Path to output file (None for stdout)
        config_file: Path to configuration file
        heading_offset: Offset for heading levels (Requirements 8.1)
        table_style: Table formatting style (Requirements 8.2)
        include_metadata: Include document metadata in output (Requirements 8.3)
        output_encoding: Output file encoding (Requirements 8.5, 9.2)
        extract_images: Enable image extraction
        image_format: Image format preservation mode
        embed_images_base64: Embed images as base64 (Requirements 8.4)
        diagram_to_mermaid: Convert diagrams to Mermaid syntax
        enable_ocr: Enable OCR for images
        ocr_language: OCR language setting
        preview_mode: Preview mode (display without saving)
        dry_run: Dry-run mode (no file writes)
        validate_output: Validate Markdown output
        log_level: Logging level
        log_file: Log file path
        max_file_size_mb: Maximum file size in MB
        batch_mode: Batch conversion mode
        enable_proofread: Enable proofreading
        proofread_mode: Proofreading mode (auto/interactive/dry-run)
        proofread_model: LLM model for proofreading
        proofread_output_path: Separate output path for proofread result
    """
    input_path: str
    output_path: Optional[str] = None
    config_file: Optional[str] = None

    # Output options (Requirements 8.1, 8.2, 8.3, 8.5)
    heading_offset: int = 0
    table_style: str = "standard"
    include_metadata: bool = False
    output_encoding: str = "utf-8"

    # Image options (Requirements 8.4)
    extract_images: bool = True
    image_format: str = "preserve"
    embed_images_base64: bool = False
    diagram_to_mermaid: bool = False

    # OCR options
    enable_ocr: bool = True
    ocr_language: str = "eng+jpn"

    # Mode options
    preview_mode: bool = False
    dry_run: bool = False
    validate_output: bool = True

    # Logging options
    log_level: LogLevel = LogLevel.INFO
    log_file: Optional[str] = None

    # Performance options
    max_file_size_mb: int = 100
    batch_mode: bool = False

    # Proofreading options
    enable_proofread: bool = False
    proofread_mode: str = "auto"
    proofread_model: str = "llama3.2:latest"
    proofread_output_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.

        Returns:
            Dictionary representation of configuration
        """
        config_dict = asdict(self)

        # Convert LogLevel enum to string
        if isinstance(config_dict.get('log_level'), LogLevel):
            config_dict['log_level'] = config_dict['log_level'].name

        return config_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversionConfig':
        """Create configuration from dictionary.

        Args:
            data: Dictionary with configuration values

        Returns:
            ConversionConfig instance
        """
        # Convert log_level string to enum if present
        if 'log_level' in data and isinstance(data['log_level'], str):
            try:
                data['log_level'] = LogLevel[data['log_level'].upper()]
            except KeyError:
                # Invalid log level, use default
                data['log_level'] = LogLevel.INFO

        # Filter out keys that aren't in the dataclass
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}

        return cls(**filtered_data)


class ConfigManager:
    """Manager for loading, saving, and merging configuration.
    
    This class handles YAML configuration files and merges them with
    CLI arguments according to the precedence rules.
    
    Requirements:
        - 8.6: Support configuration files for saving and reusing conversion options
        - 8.7: Apply configuration file options to conversion process
    """
    
    def __init__(self):
        """Initialize the configuration manager."""
        pass
    
    def load_config(self, config_path: str) -> ConversionConfig:
        """Load configuration from a YAML file.
        
        Args:
            config_path: Path to the YAML configuration file
            
        Returns:
            ConversionConfig loaded from file
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is invalid
        """
        path = Path(config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if data is None:
                data = {}
            
            if not isinstance(data, dict):
                raise ValueError("Configuration file must contain a YAML dictionary")
            
            # Create config from loaded data
            # Provide a dummy input_path since it's required
            if 'input_path' not in data:
                data['input_path'] = ''
            
            return ConversionConfig.from_dict(data)
        
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in configuration file: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to load configuration file: {str(e)}")
    
    def save_config(self, config: ConversionConfig, config_path: str) -> None:
        """Save configuration to a YAML file.
        
        Args:
            config: Configuration to save
            config_path: Path where to save the configuration file
            
        Raises:
            IOError: If file cannot be written
        """
        path = Path(config_path)
        
        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Convert config to dictionary
            config_dict = config.to_dict()
            
            # Remove runtime-specific fields that shouldn't be saved
            runtime_fields = ['input_path', 'output_path', 'config_file']
            for field in runtime_fields:
                config_dict.pop(field, None)
            
            # Write to YAML file
            with open(path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(
                    config_dict,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True
                )
        
        except Exception as e:
            raise IOError(f"Failed to save configuration file: {str(e)}")
    
    def merge_configs(
        self,
        file_config: Optional[ConversionConfig],
        cli_config: ConversionConfig
    ) -> ConversionConfig:
        """Merge configuration from file and CLI arguments.
        
        CLI arguments take precedence over file configuration.
        Only non-default CLI values override file configuration.
        
        Args:
            file_config: Configuration loaded from file (can be None)
            cli_config: Configuration from CLI arguments
            
        Returns:
            Merged configuration with CLI taking precedence
        """
        if file_config is None:
            return cli_config
        
        # Start with file config as base
        merged_dict = file_config.to_dict()
        cli_dict = cli_config.to_dict()
        
        # Create a default config to identify which CLI values are non-default
        default_config = ConversionConfig(input_path='')
        default_dict = default_config.to_dict()
        
        # Override with CLI values that differ from defaults
        # Always override: input_path, output_path, config_file
        always_override = ['input_path', 'output_path', 'config_file']
        
        for key in always_override:
            if key in cli_dict:
                merged_dict[key] = cli_dict[key]
        
        # For other fields, only override if CLI value differs from default
        for key, cli_value in cli_dict.items():
            if key in always_override:
                continue
            
            # Check if CLI value is different from default
            default_value = default_dict.get(key)
            if cli_value != default_value:
                merged_dict[key] = cli_value
        
        return ConversionConfig.from_dict(merged_dict)
    
    def create_sample_config(self, output_path: str) -> None:
        """Create a sample configuration file with all options documented.
        
        Args:
            output_path: Path where to save the sample configuration
        """
        sample_config = ConversionConfig(
            input_path='',  # Will be provided via CLI
            output_path=None,
            heading_offset=0,
            table_style='standard',
            include_metadata=False,
            output_encoding='utf-8',
            extract_images=True,
            image_format='preserve',
            embed_images_base64=False,
            diagram_to_mermaid=False,
            enable_ocr=True,
            ocr_language='eng+jpn',
            preview_mode=False,
            dry_run=False,
            validate_output=True,
            log_level=LogLevel.INFO,
            log_file=None,
            max_file_size_mb=100,
            batch_mode=False
        )
        
        # Add comments to the YAML file
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write("# Document to Markdown Converter - Configuration File\n")
            f.write("# This file contains default settings for conversion operations\n")
            f.write("# CLI arguments will override these settings\n\n")
            
            f.write("# Output formatting options\n")
            f.write("heading_offset: 0  # Offset for heading levels (0 = no change)\n")
            f.write("table_style: standard  # Options: standard, compact, grid\n")
            f.write("include_metadata: false  # Include document metadata in output\n")
            f.write("output_encoding: utf-8  # Output file encoding\n\n")
            
            f.write("# Image handling options\n")
            f.write("extract_images: true  # Extract images from documents\n")
            f.write("image_format: preserve  # Options: preserve, png, jpeg\n")
            f.write("embed_images_base64: false  # Embed images as base64 instead of files\n")
            f.write("diagram_to_mermaid: false  # Convert diagrams to Mermaid syntax\n\n")
            
            f.write("# OCR options\n")
            f.write("enable_ocr: true  # Enable OCR for image text extraction\n")
            f.write("ocr_language: eng+jpn  # OCR language (e.g., eng, jpn, eng+jpn)\n\n")
            
            f.write("# Operation modes\n")
            f.write("preview_mode: false  # Preview output without saving\n")
            f.write("dry_run: false  # Run conversion without writing files\n")
            f.write("validate_output: true  # Validate Markdown syntax\n\n")
            
            f.write("# Logging options\n")
            f.write("log_level: INFO  # Options: DEBUG, INFO, WARNING, ERROR\n")
            f.write("log_file: null  # Path to log file (null = stderr only)\n\n")
            
            f.write("# Performance options\n")
            f.write("max_file_size_mb: 100  # Maximum file size in MB\n")
            f.write("batch_mode: false  # Batch conversion mode\n")
