"""Conversion orchestrator for Document to Markdown Converter.

This module provides the ConversionOrchestrator class which coordinates
the entire conversion process including validation, parsing, serialization,
and output writing.
"""

import os
import time
from dataclasses import dataclass, field
from typing import List, Optional

from src.config import ConversionConfig
from src.file_validator import FileValidator, ValidationResult, ErrorType
from src.format_router import FormatRouter
from src.logger import Logger, LogLevel
from src.markdown_serializer import MarkdownSerializer
from src.markdown_validator import MarkdownValidator
from src.pretty_printer import PrettyPrinter
from src.output_writer import OutputWriter


@dataclass
class ConversionStats:
    """Statistics about the conversion process.
    
    Attributes:
        total_pages: Total number of pages processed
        total_images: Total number of images found
        images_extracted: Number of images successfully extracted
        ocr_applied: Number of times OCR was applied
        tables_converted: Number of tables converted
        headings_detected: Number of headings detected
    """
    total_pages: int = 0
    total_images: int = 0
    images_extracted: int = 0
    ocr_applied: int = 0
    tables_converted: int = 0
    headings_detected: int = 0


@dataclass
class ConversionResult:
    """Result of a document conversion.
    
    Attributes:
        success: Whether conversion was successful
        input_path: Path to input file
        output_path: Path to output file (None for stdout)
        markdown_content: Converted Markdown content
        duration: Conversion duration in seconds
        errors: List of error messages
        warnings: List of warning messages
        stats: Conversion statistics
    """
    success: bool
    input_path: str
    output_path: Optional[str] = None
    markdown_content: Optional[str] = None
    duration: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    stats: ConversionStats = field(default_factory=ConversionStats)


class ConversionOrchestrator:
    """Orchestrates the document conversion process.
    
    The orchestrator coordinates all components of the conversion pipeline:
    - File validation
    - Format detection and parser selection
    - Document parsing
    - Markdown serialization
    - Output writing
    - Error handling and logging
    """
    
    def __init__(self, config: ConversionConfig, logger: Logger):
        """Initialize the conversion orchestrator.
        
        Args:
            config: Conversion configuration
            logger: Logger instance for logging operations
        """
        self.config = config
        self.logger = logger
        
        # Initialize components
        self.validator = FileValidator(max_size_mb=config.max_file_size_mb)
        self.router = FormatRouter(logger=logger.logger)  # Pass the underlying logger
        self.serializer = MarkdownSerializer(
            heading_offset=config.heading_offset,
            include_metadata=config.include_metadata
        )
        self.pretty_printer = PrettyPrinter()
        self.output_writer = OutputWriter()
        
        # Initialize markdown validator if validation is enabled
        self.markdown_validator = None
        if config.validate_output:
            try:
                self.markdown_validator = MarkdownValidator()
            except ImportError as e:
                logger.warning(f"Markdown validation disabled: {str(e)}")
                self.markdown_validator = None
    
    def convert(self, input_path: str) -> ConversionResult:
        """Convert a document to Markdown format.
        
        Args:
            input_path: Path to the input document
            
        Returns:
            ConversionResult with conversion status and details
        """
        start_time = time.time()
        result = ConversionResult(
            success=False,
            input_path=input_path,
            output_path=self.config.output_path
        )
        
        try:
            # Log conversion start
            file_size = os.path.getsize(input_path) if os.path.exists(input_path) else 0
            self.logger.log_conversion_start(input_path, file_size)
            
            # Step 1: Validate input file
            self.logger.debug("Validating input file")
            validation_result = self.validator.validate_file(input_path)
            
            if not validation_result.valid:
                error_msg = self._format_validation_error(validation_result)
                result.errors.append(error_msg)
                self.logger.error(error_msg)
                return result
            
            self.logger.info(f"File validated successfully: {validation_result.file_format.value}")
            
            # Step 2: Get appropriate parser
            self.logger.debug("Selecting parser for file format")
            try:
                parser = self.router.get_parser(validation_result.file_format)
            except ValueError as e:
                result.errors.append(str(e))
                self.logger.error(str(e))
                return result
            
            # Step 3: Parse document
            self.logger.info("Parsing document")
            try:
                internal_doc = parser.parse(input_path)
                self.logger.info("Document parsed successfully")
                
                # Update statistics
                result.stats.headings_detected = sum(
                    1 for section in internal_doc.sections if section.heading
                )
                result.stats.total_images = len(internal_doc.images)
                
                self.logger.debug(f"Document has {len(internal_doc.images)} images")
                self.logger.debug(f"Config extract_images: {self.config.extract_images}")
                
                # Count tables
                from src.internal_representation import Table
                for section in internal_doc.sections:
                    result.stats.tables_converted += sum(
                        1 for content in section.content if isinstance(content, Table)
                    )
                
                # Step 3.5: Extract images if enabled
                if self.config.extract_images and internal_doc.images:
                    self.logger.info(f"Extracting {len(internal_doc.images)} images")
                    try:
                        from src.image_extractor import ImageExtractor
                        from pathlib import Path
                        
                        # Determine output directory for images
                        if self.config.output_path:
                            output_dir = Path(self.config.output_path).parent
                        else:
                            output_dir = Path.cwd() / "output"
                        
                        # Initialize image extractor
                        image_extractor = ImageExtractor(
                            output_dir=str(output_dir),
                            preserve_filenames=False,
                            ocr_engine=None,  # OCR will be added later if needed
                            enable_ocr=self.config.enable_ocr
                        )
                        
                        # Get image data from parser if available
                        image_data_list = None
                        if hasattr(parser, '_image_data'):
                            image_data_list = parser._image_data
                        
                        # Extract images (this will create the directory structure and save files)
                        extracted_images = image_extractor.extract_images(
                            document=internal_doc,
                            source_file_path=input_path,
                            image_data_list=image_data_list
                        )
                        
                        result.stats.images_extracted = len(extracted_images)
                        self.logger.info(f"Extracted {len(extracted_images)} images")
                        
                    except Exception as e:
                        warning_msg = f"Image extraction failed: {str(e)}"
                        result.warnings.append(warning_msg)
                        self.logger.warning(warning_msg)
                
            except NotImplementedError as e:
                error_msg = f"Parser not yet implemented: {str(e)}"
                result.errors.append(error_msg)
                result.warnings.append("Partial conversion may be available in future versions")
                self.logger.error(error_msg)
                return result
            except Exception as e:
                error_msg = f"Failed to parse document: {str(e)}"
                result.errors.append(error_msg)
                self.logger.error(error_msg, exception=e)
                
                # Attempt graceful degradation
                if self.config.dry_run or self.config.preview_mode:
                    result.warnings.append("Partial output may be incomplete due to parsing errors")
                    result.markdown_content = f"# Parsing Error\n\n{error_msg}\n"
                    result.success = True  # Partial success
                
                return result
            
            # Step 4: Serialize to Markdown
            self.logger.info("Serializing to Markdown")
            try:
                markdown_content = self.serializer.serialize(internal_doc)
                self.logger.debug(f"Serialized {len(markdown_content)} characters")
            except Exception as e:
                error_msg = f"Failed to serialize to Markdown: {str(e)}"
                result.errors.append(error_msg)
                self.logger.error(error_msg, exception=e)
                return result
            
            # Step 5: Pretty print
            self.logger.debug("Formatting Markdown output")
            try:
                markdown_content = self.pretty_printer.format(markdown_content)
            except Exception as e:
                # Pretty printing failure is not critical
                warning_msg = f"Pretty printing failed, using unformatted output: {str(e)}"
                result.warnings.append(warning_msg)
                self.logger.warning(warning_msg)
            
            # Step 6: Validate output (if enabled)
            if self.config.validate_output and self.markdown_validator:
                self.logger.debug("Validating Markdown output")
                validation_result = self.markdown_validator.validate(markdown_content)
                
                if not validation_result.valid:
                    self.logger.warning(
                        f"Markdown validation found {validation_result.error_count} errors "
                        f"and {validation_result.warning_count} warnings"
                    )
                
                # Add validation issues to result
                for issue in validation_result.issues:
                    issue_str = str(issue)
                    if issue.severity.value == "error":
                        result.warnings.append(f"Validation error: {issue_str}")
                        self.logger.warning(f"Validation error: {issue_str}")
                    else:
                        result.warnings.append(f"Validation {issue.severity.value}: {issue_str}")
                        self.logger.debug(f"Validation {issue.severity.value}: {issue_str}")
                
                if validation_result.valid:
                    self.logger.info("Markdown validation passed")
                else:
                    self.logger.warning("Markdown validation completed with issues")
            
            # Step 7: Write output
            result.markdown_content = markdown_content
            
            if self.config.preview_mode:
                self._write_preview(markdown_content)
            elif self.config.dry_run:
                self.logger.info("Dry-run mode: skipping file write")
            else:
                self._write_output(markdown_content, self.config.output_path)
            
            # Mark as successful
            result.success = True
            
            # Calculate duration
            result.duration = time.time() - start_time
            
            # Log completion
            output_desc = self.config.output_path or "stdout"
            if self.config.preview_mode:
                output_desc = "preview"
            elif self.config.dry_run:
                output_desc = "dry-run"
            
            self.logger.log_conversion_complete(output_desc, result.duration)
            
        except Exception as e:
            # Catch-all for unexpected errors
            error_msg = f"Unexpected error during conversion: {str(e)}"
            result.errors.append(error_msg)
            self.logger.error(error_msg, exception=e)
            result.duration = time.time() - start_time
        
        return result
    
    def batch_convert(self, input_paths: List[str]) -> List[ConversionResult]:
        """Convert multiple documents in batch mode.
        
        Args:
            input_paths: List of input file paths
            
        Returns:
            List of ConversionResult objects
        """
        self.logger.info(f"Starting batch conversion of {len(input_paths)} files")
        results = []
        
        for i, input_path in enumerate(input_paths, 1):
            self.logger.info(f"Processing file {i}/{len(input_paths)}: {input_path}")
            
            # Create a new config for this file
            file_config = ConversionConfig(
                input_path=input_path,
                output_path=self._generate_output_path(input_path),
                **{k: v for k, v in self.config.__dict__.items() 
                   if k not in ['input_path', 'output_path']}
            )
            
            # Create new orchestrator with file-specific config
            orchestrator = ConversionOrchestrator(config=file_config, logger=self.logger)
            result = orchestrator.convert(input_path)
            results.append(result)
            
            if result.success:
                self.logger.info(f"Successfully converted: {input_path}")
            else:
                self.logger.error(f"Failed to convert: {input_path}")
        
        # Summary
        successful = sum(1 for r in results if r.success)
        self.logger.info(f"Batch conversion complete: {successful}/{len(input_paths)} successful")
        
        return results
    
    def _format_validation_error(self, validation_result: ValidationResult) -> str:
        """Format validation error message.
        
        Args:
            validation_result: Validation result with error details
            
        Returns:
            Formatted error message
        """
        if validation_result.error_message:
            return validation_result.error_message
        
        error_type = validation_result.error_type
        if error_type == ErrorType.FILE_NOT_FOUND:
            return f"File not found: {self.config.input_path}"
        elif error_type == ErrorType.INVALID_FORMAT:
            return f"Invalid file format. Expected .docx, .xlsx, or .pdf"
        elif error_type == ErrorType.FILE_TOO_LARGE:
            return f"File size exceeds maximum allowed size ({self.config.max_file_size_mb} MB)"
        elif error_type == ErrorType.FILE_NOT_READABLE:
            return f"File is not readable. Check file permissions"
        elif error_type == ErrorType.FILE_CORRUPTED:
            return f"File appears to be corrupted or malformed"
        else:
            return "File validation failed"
    
    def _write_preview(self, content: str, lines: int = 50) -> None:
        """Write preview of content to stdout.
        
        Args:
            content: Content to preview
            lines: Number of lines to display
        """
        self.output_writer.preview(content, lines)
    
    def _write_output(self, content: str, output_path: Optional[str]) -> None:
        """Write content to output destination.
        
        Args:
            content: Content to write
            output_path: Output file path (None for stdout)
        """
        if output_path:
            # Write to file with configured encoding
            try:
                encoding = self.config.output_encoding
                self.output_writer.write_to_file(content, output_path, encoding=encoding)
                self.logger.info(f"Output written to: {output_path} (encoding: {encoding})")
            except Exception as e:
                raise Exception(f"Failed to write output file: {str(e)}")
        else:
            # Write to stdout
            self.output_writer.write_to_stdout(content)
    
    def _generate_output_path(self, input_path: str) -> str:
        """Generate output path for batch conversion.
        
        Args:
            input_path: Input file path
            
        Returns:
            Generated output file path
        """
        from pathlib import Path
        
        input_file = Path(input_path)
        output_file = input_file.with_suffix('.md')
        
        return str(output_file)
