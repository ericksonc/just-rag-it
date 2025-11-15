"""PDF text extraction for RAG indexing.

This module provides functionality to extract text content from PDF files
for semantic search and RAG applications.
"""

from pathlib import Path
from typing import Optional
import logging

try:
    from pypdf import PdfReader
except ImportError:
    raise ImportError(
        "pypdf is required for PDF support. Install it with: pip install pypdf"
    ) from None

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: Path, max_pages: Optional[int] = None) -> str:
    """Extract text content from a PDF file.

    Args:
        file_path: Path to the PDF file
        max_pages: Optional maximum number of pages to extract (None = all pages)

    Returns:
        Extracted text content as a string

    Raises:
        ValueError: If the PDF is encrypted or corrupted
        FileNotFoundError: If the file doesn't exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    try:
        reader = PdfReader(str(file_path))

        # Check if PDF is encrypted
        if reader.is_encrypted:
            logger.warning(f"Encrypted PDF file, attempting to decrypt: {file_path}")
            # Try to decrypt with empty password (common for many PDFs)
            if not reader.decrypt(""):
                raise ValueError(f"Cannot decrypt encrypted PDF: {file_path}")

        # Determine number of pages to process
        num_pages = len(reader.pages)
        pages_to_process = min(num_pages, max_pages) if max_pages else num_pages

        # Extract text from each page
        text_parts = []
        for page_num in range(pages_to_process):
            try:
                page = reader.pages[page_num]
                page_text = page.extract_text()

                if page_text and page_text.strip():
                    # Add page separator for context
                    text_parts.append(f"--- Page {page_num + 1} ---\n{page_text}")
                else:
                    logger.debug(f"No text found on page {page_num + 1} of {file_path}")

            except Exception as e:
                logger.warning(f"Error extracting text from page {page_num + 1} of {file_path}: {e}")
                continue

        if not text_parts:
            logger.warning(f"No text content extracted from PDF: {file_path}")
            return ""

        # Join all pages with double newline for paragraph separation
        full_text = "\n\n".join(text_parts)

        logger.debug(f"Extracted {len(full_text)} characters from {pages_to_process} pages of {file_path}")

        return full_text

    except Exception as e:
        logger.exception(f"Failed to extract text from PDF {file_path}: {e}")
        raise ValueError(f"Error processing PDF file {file_path}: {e}") from e


def is_valid_pdf(file_path: Path) -> bool:
    """Check if a file is a valid PDF that can be processed.

    Args:
        file_path: Path to the file to check

    Returns:
        True if the file is a valid, processable PDF
    """
    if not file_path.exists() or not file_path.suffix.lower() == '.pdf':
        return False

    try:
        reader = PdfReader(str(file_path))
        # Try to access pages to ensure it's a valid PDF
        _ = len(reader.pages)
        return True
    except Exception:
        return False
