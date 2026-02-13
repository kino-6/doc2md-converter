"""Command-line interface using argparse for Document to Markdown Converter.

This module provides an alternative CLI interface using argparse framework.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional, List

from src.config import ConversionConfig, ConfigManager
from src.logger import Logger, LogLevel
from src.conversion_orchestrator import ConversionOrchestrator


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog='doc2md',
        description='Convert Word, Excel, and PDF documents to Markdown format.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert a Word document to Markdown
  doc2md -i document.docx -o output.md
  
  # Full feature conversion (recommended)
  doc2md -i document.pdf -o output.md --full
  
  # Convert with all features enabled
  doc2md -i document.pdf -o output.md --extract-images --proofread --diagram-to-mermaid
  
  # Convert multiple documents (batch mode)
  doc2md -i doc1.docx -i doc2.xlsx -i doc3.pdf
  
  # Preview conversion without saving
  doc2md -i document.docx --preview
  
  # Convert with custom configuration
  doc2md -i document.docx -o output.md -c config.yaml

For more information, visit: https://github.com/kino-6/doc2md-converter
        """
    )
    
    # Required arguments
    parser.add_argument(
        '-i', '--input',
        dest='input_path',
        action='append',
        required=True,
        help='Input file path(s). Supported formats: .docx, .xlsx, .pdf. Can be specified multiple times for batch conversion.'
    )
    
    # Output options
    parser.add_argument(
        '-o', '--output',
        dest='output_path',
        help='Output file path. If not specified, outputs to stdout'
    )
    
    parser.add_argument(
        '-c', '--config',
        dest='config_file',
        help='Configuration file path (YAML format)'
    )
    
    # Full feature mode
    parser.add_argument(
        '--full',
        action='store_true',
        help='Enable all features (extract-images, proofread, diagram-to-mermaid). Recommended for best results.'
    )
    
    # Mode options
    parser.add_argument(
        '-p', '--preview',
        dest='preview_mode',
        action='store_true',
        help='Preview mode: display first 50 lines without saving to file'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry-run mode: perform conversion without writing output files'
    )
    
    # Logging options
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--log-file',
        help='Log file path. If not specified, logs to stderr only'
    )
    
    # Image options
    parser.add_argument(
        '--extract-images',
        action='store_true',
        help='Extract images from documents (enabled by default with --full)'
    )
    
    parser.add_argument(
        '--no-extract-images',
        action='store_true',
        help='Disable image extraction'
    )
    
    parser.add_argument(
        '--embed-images-base64',
        action='store_true',
        help='Embed images as base64 data URLs instead of extracting to files'
    )
    
    # Diagram conversion options
    parser.add_argument(
        '--diagram-to-mermaid',
        action='store_true',
        help='Convert diagrams to Mermaid syntax using multimodal LLM (enabled by default with --full)'
    )
    
    parser.add_argument(
        '--diagram-model',
        default='llama3.2-vision:latest',
        help='Multimodal LLM model for diagram conversion (default: llama3.2-vision:latest)'
    )
    
    # OCR options
    parser.add_argument(
        '--ocr-lang',
        dest='ocr_language',
        default='eng+jpn',
        help='OCR language setting (default: eng+jpn)'
    )
    
    # Proofreading options
    parser.add_argument(
        '--proofread',
        dest='enable_proofread',
        action='store_true',
        help='Enable proofreading of converted Markdown text (enabled by default with --full)'
    )
    
    parser.add_argument(
        '--proofread-mode',
        choices=['auto', 'interactive', 'dry-run'],
        default='auto',
        help='Proofreading mode: auto (apply all), interactive (confirm each), dry-run (show only). Default: auto'
    )
    
    parser.add_argument(
        '--proofread-model',
        default='llama3.2:latest',
        help='LLM model to use for proofreading (default: llama3.2:latest)'
    )
    
    parser.add_argument(
        '--proofread-output',
        dest='proofread_output_path',
        help='Save proofread result to a separate file (optional)'
    )
    
    # Formatting options
    parser.add_argument(
        '--heading-offset',
        type=int,
        default=0,
        help='Heading level offset (default: 0)'
    )
    
    parser.add_argument(
        '--include-metadata',
        action='store_true',
        help='Include document metadata in output'
    )
    
    # Validation options
    parser.add_argument(
        '--validate',
        dest='validate_output',
        action='store_true',
        default=True,
        help='Validate Markdown output syntax (default: enabled)'
    )
    
    parser.add_argument(
        '--no-validate',
        action='store_true',
        help='Disable Markdown output validation'
    )
    
    # Performance options
    parser.add_argument(
        '--max-file-size',
        dest='max_file_size_mb',
        type=int,
        default=100,
        help='Maximum file size in MB (default: 100)'
    )
    
    # Version
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 0.1.0'
    )
    
    return parser


def main_argparse():
    """Main entry point for argparse-based CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle --full flag
    if args.full:
        args.extract_images = True
        args.enable_proofread = True
        args.diagram_to_mermaid = True
        print("🚀 Full feature mode enabled: extract-images, proofread, diagram-to-mermaid")
        print()
    
    # Handle conflicting flags
    if args.no_extract_images:
        args.extract_images = False
    elif not args.extract_images and not args.full:
        # Default to True if not specified
        args.extract_images = True
    
    if args.no_validate:
        args.validate_output = False
    
    # Map log level string to enum
    log_level_map = {
        'DEBUG': LogLevel.DEBUG,
        'INFO': LogLevel.INFO,
        'WARNING': LogLevel.WARNING,
        'ERROR': LogLevel.ERROR
    }
    log_level_enum = log_level_map[args.log_level.upper()]
    
    # Initialize logger
    logger = Logger(log_level=log_level_enum, output_path=args.log_file)
    
    try:
        # Initialize config manager
        config_manager = ConfigManager()
        
        # Load configuration from file if provided
        file_config = None
        if args.config_file:
            try:
                file_config = config_manager.load_config(args.config_file)
                logger.info(f"Loaded configuration from: {args.config_file}")
            except FileNotFoundError as e:
                logger.error(str(e))
                sys.exit(1)
            except ValueError as e:
                logger.error(f"Invalid configuration file: {str(e)}")
                sys.exit(1)
        
        # Create CLI configuration
        cli_config = ConversionConfig(
            input_path=args.input_path[0] if len(args.input_path) == 1 else "",
            output_path=args.output_path,
            config_file=args.config_file,
            heading_offset=args.heading_offset,
            include_metadata=args.include_metadata,
            extract_images=args.extract_images,
            embed_images_base64=args.embed_images_base64,
            diagram_to_mermaid=args.diagram_to_mermaid,
            diagram_model=args.diagram_model,
            ocr_language=args.ocr_language,
            preview_mode=args.preview_mode,
            dry_run=args.dry_run,
            validate_output=args.validate_output,
            log_level=log_level_enum,
            log_file=args.log_file,
            max_file_size_mb=args.max_file_size_mb,
            batch_mode=len(args.input_path) > 1,
            enable_proofread=args.enable_proofread,
            proofread_mode=args.proofread_mode,
            proofread_model=args.proofread_model,
            proofread_output_path=args.proofread_output_path
        )
        
        # Merge configurations (CLI takes precedence)
        config = config_manager.merge_configs(file_config, cli_config)
        
        # Create orchestrator
        orchestrator = ConversionOrchestrator(config=config, logger=logger)
        
        # Perform conversion (single or batch)
        if len(args.input_path) == 1:
            # Single file conversion
            result = orchestrator.convert(args.input_path[0])
            
            # Handle result
            if result.success:
                if args.preview_mode:
                    logger.info("Preview mode: displaying first 50 lines")
                elif args.dry_run:
                    logger.info("Dry-run mode: conversion completed without writing files")
                else:
                    logger.info(f"Conversion successful: {result.output_path or 'stdout'}")
                
                # Apply proofreading if enabled
                if args.enable_proofread and result.markdown_content:
                    logger.info("Applying proofreading...")
                    from src.cli import _apply_proofreading
                    proofread_result = _apply_proofreading(
                        result.markdown_content,
                        args.proofread_mode,
                        args.proofread_model,
                        logger
                    )
                    
                    # Save proofread result
                    if args.proofread_output_path:
                        with open(args.proofread_output_path, 'w', encoding='utf-8') as f:
                            f.write(proofread_result.corrected_text)
                        logger.info(f"Proofread result saved to: {args.proofread_output_path}")
                    elif not args.preview_mode and not args.dry_run:
                        if result.output_path:
                            with open(result.output_path, 'w', encoding='utf-8') as f:
                                f.write(proofread_result.corrected_text)
                            logger.info(f"Proofread result saved to: {result.output_path}")
                    
                    logger.info(f"Proofreading complete: {proofread_result.corrections_applied} corrections applied")
                
                sys.exit(0)
            else:
                for error in result.errors:
                    logger.error(error)
                sys.exit(1)
        else:
            # Batch conversion
            if args.output_path:
                logger.warning("Output path ignored in batch mode. Files will be saved with .md extension.")
            
            if args.enable_proofread:
                logger.warning("Proofreading in batch mode: applying to all files")
            
            results = orchestrator.batch_convert(args.input_path)
            
            # Apply proofreading to batch results if enabled
            if args.enable_proofread:
                from src.cli import _apply_proofreading
                for result in results:
                    if result.success and result.markdown_content and result.output_path:
                        logger.info(f"Proofreading: {result.output_path}")
                        proofread_result = _apply_proofreading(
                            result.markdown_content,
                            args.proofread_mode,
                            args.proofread_model,
                            logger
                        )
                        
                        with open(result.output_path, 'w', encoding='utf-8') as f:
                            f.write(proofread_result.corrected_text)
                        
                        logger.info(f"  {proofread_result.corrections_applied} corrections applied")
            
            # Summary
            successful = sum(1 for r in results if r.success)
            failed = len(results) - successful
            
            logger.info(f"Batch conversion complete: {successful} successful, {failed} failed")
            
            if failed > 0:
                sys.exit(1)
            else:
                sys.exit(0)
    
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}", exception=e)
        sys.exit(1)


if __name__ == '__main__':
    main_argparse()
