"""
Image extraction module for the Document to Markdown Converter.

This module provides the ImageExtractor class that handles extracting images
from documents and saving them to appropriate directory structures.
"""

import os
from pathlib import Path
from typing import List, Optional
from src.internal_representation import ImageReference, InternalDocument


class ImageExtractor:
    """Extracts and saves images from documents.
    
    This class handles:
    - Extracting images from documents
    - Saving images to appropriate directory structure ({filename}/images/)
    - Sequential or original filename-based naming
    - Updating image references with extracted paths
    - OCR text extraction from images (when enabled)
    
    Attributes:
        output_dir: Base directory for output files
        preserve_filenames: Whether to preserve original filenames (default: False)
        ocr_engine: Optional OCR engine for text extraction from images
        enable_ocr: Whether to apply OCR to extracted images
    """
    
    def __init__(
        self,
        output_dir: str = ".",
        preserve_filenames: bool = False,
        ocr_engine: Optional['OCREngine'] = None,
        enable_ocr: bool = True
    ):
        """Initialize the ImageExtractor.
        
        Args:
            output_dir: Base directory for output files
            preserve_filenames: Whether to preserve original filenames when possible
            ocr_engine: Optional OCR engine instance for text extraction
            enable_ocr: Whether to apply OCR to images (default: True)
        """
        self.output_dir = Path(output_dir)
        self.preserve_filenames = preserve_filenames
        self.ocr_engine = ocr_engine
        self.enable_ocr = enable_ocr
    
    def extract_images(
        self,
        document: InternalDocument,
        source_file_path: str,
        image_data_list: Optional[List[tuple]] = None
    ) -> List[ImageReference]:
        """Extract images from a document and save them to disk.
        
        Args:
            document: InternalDocument containing image references
            source_file_path: Path to the source document file
            image_data_list: Optional list of (ImageReference, bytes) tuples containing
                           actual image data to save. If None, only updates paths.
        
        Returns:
            List of ImageReference objects with updated extracted_path attributes
        """
        if not document.images:
            return []
        
        # Create images directory based on source filename
        source_path = Path(source_file_path)
        base_name = source_path.stem  # filename without extension
        images_dir = self.output_dir / base_name / "images"
        
        # Create the images directory if it doesn't exist
        images_dir.mkdir(parents=True, exist_ok=True)
        
        extracted_images = []
        
        # If we have actual image data, save it
        if image_data_list:
            for idx, (img_ref, img_bytes) in enumerate(image_data_list, start=1):
                # Determine filename
                if self.preserve_filenames and img_ref.source_path:
                    # Try to extract filename from source_path
                    filename = self._extract_filename(img_ref.source_path, idx)
                else:
                    # Use sequential naming
                    filename = f"image_{idx:03d}.png"
                
                # Save image to disk
                image_path = images_dir / filename
                try:
                    with open(image_path, 'wb') as f:
                        f.write(img_bytes)
                    
                    # Update image reference with relative path
                    relative_path = f"{base_name}/images/{filename}"
                    img_ref.extracted_path = relative_path
                    
                    # Apply OCR if enabled and OCR engine is available
                    if self.enable_ocr and self.ocr_engine and not img_ref.ocr_text:
                        try:
                            ocr_text = self.ocr_engine.extract_text_from_bytes(img_bytes)
                            if ocr_text:  # Only set if text was found
                                img_ref.ocr_text = ocr_text
                        except Exception as e:
                            # OCR failure is not critical, just log and continue
                            print(f"Warning: OCR failed for image {filename}: {e}")
                    
                    extracted_images.append(img_ref)
                
                except Exception as e:
                    # If save fails, keep original reference without extracted_path
                    print(f"Warning: Failed to save image {filename}: {e}")
                    extracted_images.append(img_ref)
        else:
            # No image data provided, just update paths for existing references
            for idx, img_ref in enumerate(document.images, start=1):
                if self.preserve_filenames and img_ref.source_path:
                    filename = self._extract_filename(img_ref.source_path, idx)
                else:
                    filename = f"image_{idx:03d}.png"
                
                relative_path = f"{base_name}/images/{filename}"
                img_ref.extracted_path = relative_path
                extracted_images.append(img_ref)
        
        return extracted_images
    
    def _extract_filename(self, source_path: str, fallback_index: int) -> str:
        """Extract a filename from source path or generate a fallback.
        
        Args:
            source_path: Original source path or identifier
            fallback_index: Index to use if filename cannot be extracted
        
        Returns:
            Filename string
        """
        try:
            # Try to extract filename from path
            path = Path(source_path)
            if path.suffix:
                # Has an extension, use it
                return path.name
            else:
                # No extension, add .png
                return f"{path.name}.png" if path.name else f"image_{fallback_index:03d}.png"
        except:
            # If path parsing fails, use fallback
            return f"image_{fallback_index:03d}.png"
    
    def save_image(
        self,
        image_bytes: bytes,
        output_path: str,
        format: str = "PNG"
    ) -> str:
        """Save image bytes to a file.
        
        Args:
            image_bytes: Raw image data
            output_path: Path where to save the image
            format: Image format (default: PNG)
        
        Returns:
            Path to the saved image
        
        Raises:
            IOError: If image cannot be saved
        """
        output_path = Path(output_path)
        
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(output_path, 'wb') as f:
                f.write(image_bytes)
            return str(output_path)
        except Exception as e:
            raise IOError(f"Failed to save image to {output_path}: {e}")
    
    def apply_ocr(self, image: ImageReference, language: Optional[str] = None) -> str:
        """Apply OCR to an image and extract text.
        
        Args:
            image: ImageReference object with extracted_path set
            language: Optional language override for OCR
        
        Returns:
            Extracted text from the image
        
        Raises:
            ValueError: If OCR engine is not available or image path is not set
            IOError: If OCR extraction fails
        """
        if not self.ocr_engine:
            raise ValueError("OCR engine is not available")
        
        if not image.extracted_path:
            raise ValueError("Image must be extracted before applying OCR")
        
        # If language override is provided, temporarily change the OCR language
        original_language = None
        if language:
            original_language = self.ocr_engine.get_language()
            self.ocr_engine.set_language(language)
        
        try:
            # Extract text from the saved image file
            text = self.ocr_engine.extract_text(str(self.output_dir / image.extracted_path))
            return text
        finally:
            # Restore original language if it was changed
            if original_language:
                self.ocr_engine.set_language(original_language)
    
    def get_images_directory(self, source_file_path: str) -> Path:
        """Get the images directory path for a given source file.
        
        Args:
            source_file_path: Path to the source document file
        
        Returns:
            Path object for the images directory
        """
        source_path = Path(source_file_path)
        base_name = source_path.stem
        return self.output_dir / base_name / "images"
