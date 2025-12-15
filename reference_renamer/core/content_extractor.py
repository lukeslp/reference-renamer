"""
Content extraction module for Reference Renamer.
Handles extraction of text and metadata from various file formats.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import logging
import io

import PyPDF2
import pytesseract

from ..utils.exceptions import ContentExtractionError
from ..utils.logging import get_logger


class ContentExtractor:
    """Extracts text content from various file formats."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the content extractor.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or get_logger(__name__)

    def extract_content(self, file_path: Path) -> Dict[str, Any]:
        """
        Extracts content from a file based on its type.

        Args:
            file_path: Path to the file

        Returns:
            Dict containing:
                - text: Extracted text content
                - metadata: Any metadata found during extraction
                - format: The format of the original file

        Raises:
            ContentExtractionError: If extraction fails
        """
        suffix = file_path.suffix.lower()

        try:
            if suffix == ".pdf":
                return self._extract_pdf(file_path)
            elif suffix in [".txt", ".py", ".md", ".doc", ".docx"]:
                return self._extract_text(file_path)
            else:
                raise ContentExtractionError(f"Unsupported file format: {suffix}")

        except Exception as e:
            raise ContentExtractionError(f"Error extracting content: {str(e)}")

    def _extract_pdf(self, file_path: Path) -> Dict[str, Any]:
        """
        Extracts content from a PDF file with OCR fallback.

        Args:
            file_path: Path to the PDF file

        Returns:
            Dict containing extracted content and metadata
        """
        try:
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                metadata = reader.metadata or {}

                for i, page in enumerate(reader.pages):
                    self.logger.debug(f"Processing page {i + 1}/{len(reader.pages)}")
                    page_text = page.extract_text()

                    if not page_text.strip():
                        self.logger.info(
                            f"No text found on page {i + 1}, attempting OCR"
                        )
                        page_text = self._ocr_pdf_page(page)

                    text += page_text + "\n"

                return {"text": text.strip(), "metadata": metadata, "format": "pdf"}

        except Exception as e:
            raise ContentExtractionError(f"Error extracting PDF content: {str(e)}")

    def _extract_text(self, file_path: Path) -> Dict[str, Any]:
        """
        Extracts content from a text-based file.

        Args:
            file_path: Path to the text file

        Returns:
            Dict containing extracted content
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()

            format_type = file_path.suffix.lower().lstrip('.')
            return {"text": text.strip(), "metadata": {}, "format": format_type}

        except UnicodeDecodeError:
            self.logger.warning("UTF-8 decode failed, trying alternative encodings")
            for encoding in ["latin-1", "cp1252", "iso-8859-1"]:
                try:
                    with open(file_path, "r", encoding=encoding) as file:
                        text = file.read()
                    self.logger.info(f"Successfully decoded with {encoding}")
                    format_type = file_path.suffix.lower().lstrip('.')
                    return {
                        "text": text.strip(),
                        "metadata": {"encoding": encoding},
                        "format": format_type,
                    }
                except UnicodeDecodeError:
                    continue

            raise ContentExtractionError("Failed to decode text file with any encoding")

    def _ocr_pdf_page(self, page: Any) -> str:
        """
        Performs OCR on a PDF page.

        Args:
            page: PyPDF2 page object

        Returns:
            Extracted text from the page
        """
        try:
            # Convert PDF page to image
            from pdf2image import convert_from_bytes

            # Get page as bytes
            writer = PyPDF2.PdfWriter()
            writer.add_page(page)
            page_bytes = io.BytesIO()
            writer.write(page_bytes)
            page_bytes.seek(0)

            # Convert to image
            images = convert_from_bytes(page_bytes.getvalue())
            if not images:
                return ""

            # Perform OCR on the first image
            image = images[0]
            return pytesseract.image_to_string(image)

        except Exception as e:
            self.logger.error(f"OCR failed: {str(e)}")
            return ""
