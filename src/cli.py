"""Command-line interface for Document to Markdown Converter.

This module provides the CLI interface using Click framework for parsing
command-line arguments and orchestrating the conversion process.
"""

import sys
from pathlib import Path
from typing import Optional

import click

from src.config import ConversionConfig, ConfigManager
from src.logger import Logger, LogLevel
from src.conversion_orchestrator import ConversionOrchestrator


@click.command()
@click.option(
    '--input', '-i',
    'input_path',
    multiple=True,
    required=True,
    type=click.Path(exists=True),
    help='Input file path(s) (required). Supported formats: .docx, .xlsx, .pdf. Can be specified multiple times for batch conversion.'
)
@click.option(
    '--output', '-o',
    'output_path',
    type=click.Path(),
    help='Output file path. If not specified, outputs to stdout'
)
@click.option(
    '--config', '-c',
    'config_file',
    type=click.Path(exists=True),
    help='Configuration file path (YAML format)'
)
@click.option(
    '--preview', '-p',
    'preview_mode',
    is_flag=True,
    help='Preview mode: display first 50 lines without saving to file'
)
@click.option(
    '--dry-run',
    'dry_run',
    is_flag=True,
    help='Dry-run mode: perform conversion without writing output files'
)
@click.option(
    '--log-level',
    'log_level',
    type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR'], case_sensitive=False),
    default='INFO',
    help='Logging level (default: INFO)'
)
@click.option(
    '--log-file',
    'log_file',
    type=click.Path(),
    help='Log file path. If not specified, logs to stderr only'
)
@click.option(
    '--extract-images',
    'extract_images',
    is_flag=True,
    help='Extract images from documents (enabled by default, use --no-extract-images to disable)'
)
@click.option(
    '--no-extract-images',
    'no_extract_images',
    is_flag=True,
    help='Disable image extraction'
)
@click.option(
    '--embed-images-base64',
    'embed_images_base64',
    is_flag=True,
    help='Embed images as base64 data URLs instead of extracting to files'
)
@click.option(
    '--ocr-lang',
    'ocr_language',
    default='eng+jpn',
    help='OCR language setting (default: eng+jpn)'
)
@click.option(
    '--heading-offset',
    'heading_offset',
    type=int,
    default=0,
    help='Heading level offset (default: 0)'
)
@click.option(
    '--include-metadata',
    'include_metadata',
    is_flag=True,
    help='Include document metadata in output'
)
@click.option(
    '--validate',
    'validate_output',
    is_flag=True,
    default=True,
    help='Validate Markdown output syntax (default: enabled)'
)
@click.option(
    '--no-validate',
    'no_validate',
    is_flag=True,
    help='Disable Markdown output validation'
)
@click.option(
    '--max-file-size',
    'max_file_size_mb',
    type=int,
    default=100,
    help='Maximum file size in MB (default: 100)'
)
@click.version_option(version='0.1.0', prog_name='doc2md')
def main(
    input_path: tuple,
    output_path: Optional[str],
    config_file: Optional[str],
    preview_mode: bool,
    dry_run: bool,
    log_level: str,
    log_file: Optional[str],
    extract_images: bool,
    no_extract_images: bool,
    embed_images_base64: bool,
    ocr_language: str,
    heading_offset: int,
    include_metadata: bool,
    validate_output: bool,
    no_validate: bool,
    max_file_size_mb: int
):
    """Convert Word, Excel, and PDF documents to Markdown format.
    
    Examples:
    
        # Convert a Word document to Markdown
        doc2md -i document.docx -o output.md
        
        # Convert multiple documents (batch mode)
        doc2md -i doc1.docx -i doc2.xlsx -i doc3.pdf
        
        # Preview conversion without saving
        doc2md -i document.docx --preview
        
        # Convert with custom configuration
        doc2md -i document.docx -o output.md -c config.yaml
        
        # Dry-run mode (no file output)
        doc2md -i document.docx --dry-run
    """
    # Convert tuple to list
    input_paths = list(input_path)
    
    # Handle conflicting flags
    # Default: extract_images = True (unless --no-extract-images is specified)
    if no_extract_images:
        extract_images = False
    elif not extract_images:
        # If neither flag is specified, default to True
        extract_images = True
    
    if no_validate:
        validate_output = False
    
    # Map log level string to enum
    log_level_map = {
        'DEBUG': LogLevel.DEBUG,
        'INFO': LogLevel.INFO,
        'WARNING': LogLevel.WARNING,
        'ERROR': LogLevel.ERROR
    }
    log_level_enum = log_level_map[log_level.upper()]
    
    # Initialize logger
    logger = Logger(log_level=log_level_enum, output_path=log_file)
    
    try:
        # Initialize config manager
        config_manager = ConfigManager()
        
        # Load configuration from file if provided
        file_config = None
        if config_file:
            try:
                file_config = config_manager.load_config(config_file)
                logger.info(f"Loaded configuration from: {config_file}")
            except FileNotFoundError as e:
                logger.error(str(e))
                sys.exit(1)
            except ValueError as e:
                logger.error(f"Invalid configuration file: {str(e)}")
                sys.exit(1)
        
        # Create CLI configuration
        cli_config = ConversionConfig(
            input_path=input_paths[0] if len(input_paths) == 1 else "",
            output_path=output_path,
            config_file=config_file,
            heading_offset=heading_offset,
            include_metadata=include_metadata,
            extract_images=extract_images,
            embed_images_base64=embed_images_base64,
            ocr_language=ocr_language,
            preview_mode=preview_mode,
            dry_run=dry_run,
            validate_output=validate_output,
            log_level=log_level_enum,
            log_file=log_file,
            max_file_size_mb=max_file_size_mb,
            batch_mode=len(input_paths) > 1
        )
        
        # Merge configurations (CLI takes precedence)
        config = config_manager.merge_configs(file_config, cli_config)
        
        # Create orchestrator
        orchestrator = ConversionOrchestrator(config=config, logger=logger)
        
        # Perform conversion (single or batch)
        if len(input_paths) == 1:
            # Single file conversion
            result = orchestrator.convert(input_paths[0])
            
            # Handle result
            if result.success:
                if preview_mode:
                    logger.info("Preview mode: displaying first 50 lines")
                elif dry_run:
                    logger.info("Dry-run mode: conversion completed without writing files")
                else:
                    logger.info(f"Conversion successful: {result.output_path or 'stdout'}")
                
                # Exit with success
                sys.exit(0)
            else:
                # Log errors
                for error in result.errors:
                    logger.error(error)
                
                # Exit with error code
                sys.exit(1)
        else:
            # Batch conversion
            if output_path:
                logger.warning("Output path ignored in batch mode. Files will be saved with .md extension.")
            
            results = orchestrator.batch_convert(input_paths)
            
            # Summary
            successful = sum(1 for r in results if r.success)
            failed = len(results) - successful
            
            logger.info(f"Batch conversion complete: {successful} successful, {failed} failed")
            
            # Exit with appropriate code
            if failed > 0:
                sys.exit(1)
            else:
                sys.exit(0)
    
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}", exception=e)
        sys.exit(1)


def display_help():
    """Display help information."""
    ctx = click.Context(main)
    click.echo(main.get_help(ctx))


def display_version():
    """Display version information."""
    click.echo("doc2md version 0.1.0")


if __name__ == '__main__':
    main()
