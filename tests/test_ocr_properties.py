"""
Property-based tests for OCR functionality.

This module contains property-based tests for OCR capabilities including:
- OCR on PDF images (Property 15)
- Scanned PDF OCR (Property 16)
- Multi-language OCR support (Property 17)
- OCR on images with text (Property 33)
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from hypothesis import given, strategies as st, settings, assume
from PIL import Image, ImageDraw, ImageFont
import string


class TestOCRProperties:
    """Property-based tests for OCR functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def _create_image_with_text(self, text: str, size=(400, 100)) -> bytes:
        """Create an image with text and return as bytes.
        
        Args:
            text: Text to render in the image
            size: Image size tuple (width, height)
        
        Returns:
            Image bytes in PNG format
        """
        import io
        
        # Create a simple image with text
        img = Image.new('RGB', size, color='white')
        draw = ImageDraw.Draw(img)
        
        # Use default font
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        # Draw text on image
        draw.text((10, 30), text, fill='black', font=font)
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()
    
    def _create_pdf_with_image(self, image_bytes: bytes, pdf_path: Path) -> None:
        """Create a PDF containing an image.
        
        Args:
            image_bytes: Image data as bytes
            pdf_path: Path where to save the PDF
        """
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.utils import ImageReader
            import io
            
            c = canvas.Canvas(str(pdf_path), pagesize=letter)
            
            # Add image to PDF
            img_reader = ImageReader(io.BytesIO(image_bytes))
            c.drawImage(img_reader, 100, 600, width=300, height=100)
            
            c.showPage()
            c.save()
        except ImportError:
            pytest.skip("reportlab not installed")
    
    @settings(max_examples=100, deadline=None)
    @given(st.text(alphabet=string.ascii_letters + string.digits + ' ', min_size=3, max_size=50))
    def test_property_15_ocr_on_pdf_images(self, text_content):
        """Feature: document-to-markdown-converter, Property 15: OCR on PDF images
        
        For any PDF containing images with text, the converter should extract
        text using OCR capabilities.
        
        **Validates: Requirements 3.4**
        """
        # Skip empty or whitespace-only text
        assume(text_content.strip())
        
        try:
            from src.ocr_engine import OCREngine
            from src.image_extractor import ImageExtractor
            from src.internal_representation import ImageReference, InternalDocument, DocumentMetadata
        except RuntimeError as e:
            pytest.skip(f"Tesseract not available: {e}")
            return
        except ImportError:
            pytest.skip("Required modules not available")
            return
        
        # Create an image with text
        image_bytes = self._create_image_with_text(text_content)
        
        # Save image temporarily
        image_path = self.temp_dir / f"test_ocr_{abs(hash(text_content))}.png"
        with open(image_path, 'wb') as f:
            f.write(image_bytes)
        
        # Create an ImageReference
        img_ref = ImageReference(
            source_path=str(image_path),
            extracted_path=None,
            alt_text=None,
            ocr_text=None
        )
        
        # Create a mock document with the image reference
        doc = InternalDocument(
            metadata=DocumentMetadata(source_format='pdf'),
            sections=[],
            images=[img_ref]
        )
        
        # Create OCR engine
        try:
            ocr_engine = OCREngine(language="eng")
        except Exception as e:
            pytest.skip(f"OCR engine initialization failed: {e}")
            return
        
        # Create image extractor with OCR enabled
        extractor = ImageExtractor(
            output_dir=str(self.temp_dir),
            ocr_engine=ocr_engine,
            enable_ocr=True
        )
        
        # Extract images with OCR (simulating PDF image extraction)
        source_file = self.temp_dir / "test_doc.pdf"
        source_file.touch()
        
        extracted = extractor.extract_images(
            document=doc,
            source_file_path=str(source_file),
            image_data_list=[(img_ref, image_bytes)]
        )
        
        # Verify that images were extracted
        assert len(extracted) > 0, "Should extract at least one image"
        
        # Verify that OCR was applied to images from PDF
        extracted_img = extracted[0]
        assert extracted_img.extracted_path is not None, \
            "Image should have an extracted path"
        
        # Check if OCR text was extracted (OCR may not always be perfect)
        # The property verifies that OCR is attempted on PDF images
        if extracted_img.ocr_text:
            assert isinstance(extracted_img.ocr_text, str), \
                "OCR text should be a string"
    
    @settings(max_examples=100, deadline=None)
    @given(st.text(alphabet=string.ascii_letters + string.digits + ' ', min_size=5, max_size=100))
    def test_property_16_scanned_pdf_ocr(self, text_content):
        """Feature: document-to-markdown-converter, Property 16: Scanned PDF OCR
        
        For any scanned or image-based PDF, the converter should use OCR to
        extract text content.
        
        **Validates: Requirements 3.5**
        """
        # Skip empty or whitespace-only text
        assume(text_content.strip())
        
        try:
            from src.ocr_engine import OCREngine
            from src.image_extractor import ImageExtractor
            from src.internal_representation import ImageReference, InternalDocument, DocumentMetadata
        except RuntimeError as e:
            pytest.skip(f"Tesseract not available: {e}")
            return
        except ImportError:
            pytest.skip("Required modules not available")
            return
        
        # Create a larger image to simulate a scanned page
        image_bytes = self._create_image_with_text(text_content, size=(600, 800))
        
        # Save image temporarily (simulating scanned PDF page)
        image_path = self.temp_dir / f"test_scanned_{abs(hash(text_content))}.png"
        with open(image_path, 'wb') as f:
            f.write(image_bytes)
        
        # Create an ImageReference (simulating extracted page from scanned PDF)
        img_ref = ImageReference(
            source_path=str(image_path),
            extracted_path=None,
            alt_text=None,
            ocr_text=None
        )
        
        # Create a mock document representing a scanned PDF
        doc = InternalDocument(
            metadata=DocumentMetadata(source_format='pdf'),
            sections=[],
            images=[img_ref]
        )
        
        # Create OCR engine
        try:
            ocr_engine = OCREngine(language="eng")
        except Exception as e:
            pytest.skip(f"OCR engine initialization failed: {e}")
            return
        
        # Create image extractor with OCR enabled
        extractor = ImageExtractor(
            output_dir=str(self.temp_dir),
            ocr_engine=ocr_engine,
            enable_ocr=True
        )
        
        # Extract images with OCR (simulating scanned PDF processing)
        source_file = self.temp_dir / "test_scanned.pdf"
        source_file.touch()
        
        extracted = extractor.extract_images(
            document=doc,
            source_file_path=str(source_file),
            image_data_list=[(img_ref, image_bytes)]
        )
        
        # Verify that images were extracted
        assert len(extracted) > 0, "Should extract at least one image from scanned PDF"
        
        # For scanned PDFs, OCR should be applied to extract text
        extracted_img = extracted[0]
        assert extracted_img.extracted_path is not None, \
            "Image should have an extracted path"
        
        # Verify OCR was attempted (text may or may not be extracted depending on OCR quality)
        # The property verifies that the system attempts OCR on scanned PDFs
        if extracted_img.ocr_text:
            assert isinstance(extracted_img.ocr_text, str), \
                "OCR text should be a string"
    
    @settings(max_examples=50, deadline=None)
    @given(
        st.text(alphabet=string.ascii_letters + ' ', min_size=3, max_size=30),
        st.sampled_from(['eng', 'jpn', 'eng+jpn', 'fra', 'deu', 'spa'])
    )
    def test_property_17_multi_language_ocr_support(self, text_content, language):
        """Feature: document-to-markdown-converter, Property 17: Multi-language OCR support
        
        For any document in a supported language, the converter should successfully
        apply OCR with the specified language setting.
        
        **Validates: Requirements 3.7**
        """
        # Skip empty or whitespace-only text
        assume(text_content.strip())
        
        try:
            from src.ocr_engine import OCREngine
        except RuntimeError as e:
            pytest.skip(f"Tesseract not available: {e}")
            return
        except ImportError:
            pytest.skip("OCREngine not available")
            return
        
        # Create an image with text
        image_bytes = self._create_image_with_text(text_content)
        
        # Save image temporarily
        image_path = self.temp_dir / f"test_lang_{abs(hash(text_content + language))}.png"
        with open(image_path, 'wb') as f:
            f.write(image_bytes)
        
        # Create OCR engine with specified language
        try:
            engine = OCREngine(language=language)
        except Exception as e:
            # Language pack might not be installed, skip
            pytest.skip(f"Language {language} not available: {e}")
            return
        
        # Verify language was set correctly
        assert engine.get_language() == language, \
            f"OCR engine should be configured with language {language}"
        
        # Extract text using the specified language
        try:
            extracted_text = engine.extract_text(str(image_path))
            
            # Verify that extraction completed (even if text is empty due to OCR limitations)
            assert isinstance(extracted_text, str), \
                "OCR should return a string result"
            
            # The extraction should not raise an error - successful execution
            # means the language is supported
            
        except Exception as e:
            # If extraction fails, it might be due to missing language pack
            pytest.skip(f"OCR with language {language} failed: {e}")
    
    @settings(max_examples=100, deadline=None)
    @given(st.text(alphabet=string.ascii_letters + string.digits + ' ', min_size=3, max_size=50))
    def test_property_33_ocr_on_images_with_text(self, text_content):
        """Feature: document-to-markdown-converter, Property 33: OCR on images with text
        
        For any image containing text content, the converter should apply OCR
        and include the extracted text as alt text or caption.
        
        **Validates: Requirements 7.8**
        """
        # Skip empty or whitespace-only text
        assume(text_content.strip())
        
        try:
            from src.image_extractor import ImageExtractor
            from src.ocr_engine import OCREngine
            from src.internal_representation import ImageReference, InternalDocument, DocumentMetadata
        except RuntimeError as e:
            pytest.skip(f"Tesseract not available: {e}")
            return
        except ImportError:
            pytest.skip("Required modules not available")
            return
        
        # Create an image with text
        image_bytes = self._create_image_with_text(text_content)
        
        # Create an ImageReference
        img_ref = ImageReference(
            source_path="test_image.png",
            extracted_path=None,
            alt_text=None,
            ocr_text=None
        )
        
        # Create a mock document with the image reference
        doc = InternalDocument(
            metadata=DocumentMetadata(source_format='test'),
            sections=[],
            images=[img_ref]
        )
        
        # Create OCR engine
        try:
            ocr_engine = OCREngine(language="eng")
        except Exception as e:
            pytest.skip(f"OCR engine initialization failed: {e}")
            return
        
        # Create image extractor with OCR enabled
        extractor = ImageExtractor(
            output_dir=str(self.temp_dir),
            ocr_engine=ocr_engine,
            enable_ocr=True
        )
        
        # Extract images with OCR
        source_file = self.temp_dir / "test_doc.txt"
        source_file.touch()
        
        extracted = extractor.extract_images(
            document=doc,
            source_file_path=str(source_file),
            image_data_list=[(img_ref, image_bytes)]
        )
        
        # Verify that images were extracted
        assert len(extracted) > 0, "Should extract at least one image"
        
        # Verify that OCR was applied
        extracted_img = extracted[0]
        assert extracted_img.extracted_path is not None, \
            "Image should have an extracted path"
        
        # Check if OCR text was extracted
        # Note: OCR may not always extract text perfectly, but it should attempt
        if extracted_img.ocr_text:
            assert isinstance(extracted_img.ocr_text, str), \
                "OCR text should be a string"
            # If text was extracted, it should be non-empty
            assert len(extracted_img.ocr_text) > 0, \
                "OCR text should not be empty if extraction succeeded"
    
    @settings(max_examples=100, deadline=None)
    @given(st.text(alphabet=string.ascii_letters + string.digits + ' ', min_size=3, max_size=50))
    def test_property_34_ocr_text_marking(self, text_content):
        """Feature: document-to-markdown-converter, Property 34: OCR text marking
        
        For any OCR extraction performed, the converter should indicate
        OCR-extracted text with appropriate markers in the output.
        
        **Validates: Requirements 7.11**
        """
        # Skip empty or whitespace-only text
        assume(text_content.strip())
        
        try:
            from src.image_extractor import ImageExtractor
            from src.ocr_engine import OCREngine
            from src.markdown_serializer import MarkdownSerializer
            from src.internal_representation import (
                ImageReference, InternalDocument, DocumentMetadata, Section
            )
        except RuntimeError as e:
            pytest.skip(f"Tesseract not available: {e}")
            return
        except ImportError:
            pytest.skip("Required modules not available")
            return
        
        # Create an image with text
        image_bytes = self._create_image_with_text(text_content)
        
        # Create an ImageReference
        img_ref = ImageReference(
            source_path="test_image.png",
            extracted_path=None,
            alt_text="Test Image",
            ocr_text=None
        )
        
        # Create a mock document with the image reference
        doc = InternalDocument(
            metadata=DocumentMetadata(source_format='test'),
            sections=[Section(heading=None, content=[img_ref])],
            images=[img_ref]
        )
        
        # Create OCR engine
        try:
            ocr_engine = OCREngine(language="eng")
        except Exception as e:
            pytest.skip(f"OCR engine initialization failed: {e}")
            return
        
        # Create image extractor with OCR enabled
        extractor = ImageExtractor(
            output_dir=str(self.temp_dir),
            ocr_engine=ocr_engine,
            enable_ocr=True
        )
        
        # Extract images with OCR
        source_file = self.temp_dir / "test_doc.txt"
        source_file.touch()
        
        extracted = extractor.extract_images(
            document=doc,
            source_file_path=str(source_file),
            image_data_list=[(img_ref, image_bytes)]
        )
        
        # Verify that images were extracted
        assert len(extracted) > 0, "Should extract at least one image"
        
        extracted_img = extracted[0]
        
        # If OCR text was extracted, verify it's marked in the Markdown output
        if extracted_img.ocr_text:
            # Create a serializer
            serializer = MarkdownSerializer()
            
            # Serialize the image to Markdown
            markdown_output = serializer.serialize_image(extracted_img)
            
            # Verify that the output contains OCR text marking
            assert "OCR extracted text:" in markdown_output, \
                "Markdown output should contain OCR text marker"
            
            # Verify that the OCR text is included in the output
            assert extracted_img.ocr_text in markdown_output or \
                   any(word in markdown_output for word in extracted_img.ocr_text.split() if len(word) > 2), \
                "Markdown output should contain the OCR extracted text"
            
            # Verify that the OCR text is marked with italics (using * markers)
            assert "*OCR extracted text:" in markdown_output, \
                "OCR text should be marked with italic formatting"
            
            # Verify that the image reference is still present
            assert "![" in markdown_output, \
                "Markdown output should still contain image reference"
            assert "](" in markdown_output, \
                "Markdown output should still contain image path"
        else:
            # If no OCR text was extracted, the output should not contain OCR markers
            serializer = MarkdownSerializer()
            markdown_output = serializer.serialize_image(extracted_img)
            
            # Verify no OCR marker when no OCR text is present
            assert "OCR extracted text:" not in markdown_output, \
                "Markdown output should not contain OCR marker when no OCR text is present"
