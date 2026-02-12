"""Setup configuration for Document to Markdown Converter."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

setup(
    name="doc2md-converter",
    version="1.0.0",
    description="Convert Word, Excel, and PDF documents to Markdown format with OCR support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Document Converter Team",
    python_requires=">=3.9",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=[
        "python-docx>=0.8.11",
        "openpyxl>=3.1.0",
        "PyPDF2>=3.0.0",
        "pdfplumber>=0.10.0",
        "PyMuPDF>=1.23.0",  # fitz for image extraction
        "pytesseract>=0.3.10",
        "PyYAML>=6.0",
        "click>=8.1.0",
        "markdown-it-py>=3.0.0",
        "tqdm>=4.65.0",  # Progress bars
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "hypothesis>=6.82.0",
            "pytest-cov>=4.1.0",
        ],
        "llm": [
            "ollama>=0.1.0",  # Optional: Quality evaluation (scoring only, no auto-correction)
        ],
    },
    entry_points={
        "console_scripts": [
            "doc2md=src.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Text Processing :: Markup :: Markdown",
        "Topic :: Office/Business",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
