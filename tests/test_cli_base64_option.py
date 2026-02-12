"""
CLI integration tests for base64 image embedding option.

Tests the --embed-images-base64 CLI option.
"""

import pytest
from click.testing import CliRunner
from src.cli import main


class TestCLIBase64Option:
    """Test CLI option for base64 image embedding."""
    
    def test_cli_has_embed_images_base64_option(self):
        """Test that CLI accepts --embed-images-base64 option."""
        runner = CliRunner()
        result = runner.invoke(main, ['--help'])
        
        assert result.exit_code == 0
        assert '--embed-images-base64' in result.output
        assert 'Embed images as base64 data URLs' in result.output
    
    def test_cli_embed_images_base64_flag_parsing(self):
        """Test that --embed-images-base64 flag is parsed correctly."""
        # This test verifies the option is recognized by the CLI
        # We can't test full conversion without a real document file
        runner = CliRunner()
        
        # Test with a non-existent file to verify option parsing
        # (will fail at file validation, but option should be parsed)
        result = runner.invoke(main, [
            '-i', 'nonexistent.docx',
            '--embed-images-base64'
        ])
        
        # Should fail due to file not found, not due to unknown option
        assert result.exit_code != 0
        assert 'Unknown option' not in result.output
        assert 'embed-images-base64' not in result.output.lower() or 'File not found' in result.output


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
