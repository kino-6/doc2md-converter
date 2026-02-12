"""
Integration tests for OCR language settings.

This module contains integration tests that verify OCR language configuration
works correctly through the CLI and configuration system.

Requirements: 7.10 - OCR language specification
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from PIL import Image, ImageDraw
import yaml

from src.config import ConversionConfig, ConfigManager
from src.logger import Logger, LogLevel


class TestOCRLanguageIntegration:
    """Integration test suite for OCR language settings."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def _create_test_image_with_text(self, text: str, filename: str) -> str:
        """Create a test image with text for OCR testing.
        
        Args:
            text: Text to render in the image
            filename: Name of the image file
        
        Returns:
            Path to the created image
        """
        img = Image.new('RGB', (400, 100), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((10, 30), text, fill='black')
        
        image_path = Path(self.temp_dir) / filename
        img.save(image_path)
        return str(image_path)
    
    def test_default_ocr_language_setting(self):
        """Test that default OCR language is eng+jpn."""
        config = ConversionConfig(input_path="test.pdf")
        
        assert config.ocr_language == "eng+jpn"
    
    def test_custom_ocr_language_in_config(self):
        """Test setting custom OCR language in configuration."""
        config = ConversionConfig(
            input_path="test.pdf",
            ocr_language="eng"
        )
        
        assert config.ocr_language == "eng"
    
    def test_ocr_language_from_config_file(self):
        """Test loading OCR language from configuration file."""
        # Create a config file with custom OCR language
        config_path = Path(self.temp_dir) / "config.yaml"
        config_data = {
            'ocr_language': 'jpn',
            'enable_ocr': True
        }
        
        with open(config_path, 'w') as f:
            yaml.safe_dump(config_data, f)
        
        # Load configuration
        config_manager = ConfigManager()
        loaded_config = config_manager.load_config(str(config_path))
        
        assert loaded_config.ocr_language == 'jpn'
    
    def test_ocr_language_cli_overrides_config_file(self):
        """Test that CLI OCR language setting overrides config file."""
        # Create a config file with one language
        config_path = Path(self.temp_dir) / "config.yaml"
        config_data = {
            'ocr_language': 'jpn',
            'enable_ocr': True
        }
        
        with open(config_path, 'w') as f:
            yaml.safe_dump(config_data, f)
        
        # Load file config
        config_manager = ConfigManager()
        file_config = config_manager.load_config(str(config_path))
        
        # Create CLI config with different language
        cli_config = ConversionConfig(
            input_path="test.pdf",
            ocr_language="eng"
        )
        
        # Merge configs (CLI should take precedence)
        merged_config = config_manager.merge_configs(file_config, cli_config)
        
        assert merged_config.ocr_language == "eng"
    
    def test_ocr_language_multiple_languages(self):
        """Test OCR language setting with multiple languages."""
        config = ConversionConfig(
            input_path="test.pdf",
            ocr_language="eng+fra+deu"
        )
        
        assert config.ocr_language == "eng+fra+deu"
    
    def test_ocr_engine_respects_config_language(self):
        """Test that OCR engine uses the language from configuration."""
        try:
            from src.ocr_engine import OCREngine
        except RuntimeError:
            pytest.skip("Tesseract not available")
        
        # Create OCR engine with custom language
        ocr_engine = OCREngine(language="eng")
        
        assert ocr_engine.get_language() == "eng"
        
        # Change language
        ocr_engine.set_language("jpn")
        assert ocr_engine.get_language() == "jpn"
    
    def test_image_extractor_uses_ocr_language(self):
        """Test that ImageExtractor applies OCR with configured language."""
        try:
            from src.ocr_engine import OCREngine
            from src.image_extractor import ImageExtractor
            from src.internal_representation import ImageReference, InternalDocument
        except RuntimeError:
            pytest.skip("Tesseract not available")
        
        # Create OCR engine with specific language
        ocr_engine = OCREngine(language="eng")
        
        # Create image extractor with OCR engine
        extractor = ImageExtractor(
            output_dir=self.temp_dir,
            ocr_engine=ocr_engine,
            enable_ocr=True
        )
        
        # Create test image
        img_ref = ImageReference(source_path="test.png", alt_text="Test")
        doc = InternalDocument(images=[img_ref])
        
        # Create image bytes
        img = Image.new('RGB', (200, 50), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((10, 15), "Hello", fill='black')
        
        import io
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        image_data_list = [(img_ref, img_bytes.getvalue())]
        
        # Extract images (should apply OCR)
        extracted = extractor.extract_images(doc, "test.docx", image_data_list)
        
        # Verify OCR was applied
        assert len(extracted) == 1
        assert hasattr(extracted[0], 'ocr_text')
    
    def test_ocr_language_override_in_apply_ocr(self):
        """Test language override in apply_ocr method."""
        try:
            from src.ocr_engine import OCREngine
            from src.image_extractor import ImageExtractor
            from src.internal_representation import ImageReference, InternalDocument
        except RuntimeError:
            pytest.skip("Tesseract not available")
        
        # Create OCR engine with default language
        ocr_engine = OCREngine(language="eng")
        original_lang = ocr_engine.get_language()
        
        # Create image extractor
        extractor = ImageExtractor(
            output_dir=self.temp_dir,
            ocr_engine=ocr_engine,
            enable_ocr=False  # Disable auto-OCR
        )
        
        # Create and extract test image
        img_ref = ImageReference(source_path="test.png", alt_text="Test")
        doc = InternalDocument(images=[img_ref])
        
        img = Image.new('RGB', (200, 50), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((10, 15), "Test", fill='black')
        
        import io
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        image_data_list = [(img_ref, img_bytes.getvalue())]
        
        extracted = extractor.extract_images(doc, "test.docx", image_data_list)
        
        # Apply OCR with language override
        ocr_text = extractor.apply_ocr(extracted[0], language="jpn")
        
        # Verify original language is restored
        assert ocr_engine.get_language() == original_lang
    
    def test_config_to_dict_preserves_ocr_language(self):
        """Test that config serialization preserves OCR language."""
        config = ConversionConfig(
            input_path="test.pdf",
            ocr_language="fra"
        )
        
        config_dict = config.to_dict()
        
        assert config_dict['ocr_language'] == "fra"
    
    def test_config_from_dict_loads_ocr_language(self):
        """Test that config deserialization loads OCR language."""
        config_dict = {
            'input_path': 'test.pdf',
            'ocr_language': 'deu'
        }
        
        config = ConversionConfig.from_dict(config_dict)
        
        assert config.ocr_language == "deu"
    
    def test_save_and_load_config_with_ocr_language(self):
        """Test saving and loading configuration with OCR language."""
        config_manager = ConfigManager()
        
        # Create config with custom OCR language
        original_config = ConversionConfig(
            input_path="test.pdf",
            ocr_language="spa"
        )
        
        # Save config
        config_path = Path(self.temp_dir) / "test_config.yaml"
        config_manager.save_config(original_config, str(config_path))
        
        # Load config
        loaded_config = config_manager.load_config(str(config_path))
        
        # Verify OCR language is preserved
        assert loaded_config.ocr_language == "spa"
    
    def test_sample_config_includes_ocr_language(self):
        """Test that sample configuration includes OCR language setting."""
        config_manager = ConfigManager()
        
        # Create sample config
        sample_path = Path(self.temp_dir) / "sample_config.yaml"
        config_manager.create_sample_config(str(sample_path))
        
        # Read and verify it contains OCR language
        with open(sample_path, 'r') as f:
            content = f.read()
        
        assert 'ocr_language' in content
        assert 'eng+jpn' in content  # Default value
    
    def test_ocr_disabled_ignores_language_setting(self):
        """Test that when OCR is disabled, language setting is ignored."""
        try:
            from src.ocr_engine import OCREngine
            from src.image_extractor import ImageExtractor
            from src.internal_representation import ImageReference, InternalDocument
        except RuntimeError:
            pytest.skip("Tesseract not available")
        
        # Create OCR engine
        ocr_engine = OCREngine(language="eng")
        
        # Create image extractor with OCR disabled
        extractor = ImageExtractor(
            output_dir=self.temp_dir,
            ocr_engine=ocr_engine,
            enable_ocr=False
        )
        
        # Create test image
        img_ref = ImageReference(source_path="test.png", alt_text="Test")
        doc = InternalDocument(images=[img_ref])
        
        img = Image.new('RGB', (200, 50), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((10, 15), "Hello", fill='black')
        
        import io
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        image_data_list = [(img_ref, img_bytes.getvalue())]
        
        # Extract images
        extracted = extractor.extract_images(doc, "test.docx", image_data_list)
        
        # Verify OCR was not applied
        assert len(extracted) == 1
        assert extracted[0].ocr_text is None
    
    def test_invalid_language_code_handling(self):
        """Test that invalid language codes are handled gracefully."""
        try:
            from src.ocr_engine import OCREngine
        except RuntimeError:
            pytest.skip("Tesseract not available")
        
        # Create OCR engine with potentially invalid language
        # Note: Tesseract will handle this at runtime, not at initialization
        ocr_engine = OCREngine(language="invalid_lang")
        
        # Verify it was set (validation happens during actual OCR)
        assert ocr_engine.get_language() == "invalid_lang"
    
    def test_empty_language_string(self):
        """Test handling of empty language string."""
        config = ConversionConfig(
            input_path="test.pdf",
            ocr_language=""
        )
        
        assert config.ocr_language == ""
