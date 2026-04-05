from __future__ import annotations

from io import BytesIO
from pypdf import PdfReader


def extract_pdf_text(file_content: bytes) -> str:
    """
    Extract text from a PDF file using PyPDF.

    Args:
        file_content: Raw bytes of the PDF file

    Returns:
        Extracted text from all pages
    """
    try:
        pdf_stream = BytesIO(file_content)
        pdf_reader = PdfReader(pdf_stream)

        text_parts = []
        for page_num, page in enumerate(pdf_reader.pages, 1):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(f"--- Page {page_num} ---\n{page_text}")

        return "\n".join(text_parts)
    except Exception as exc:
        raise ValueError(f"Failed to extract PDF text: {str(exc)}") from exc


def extract_text_file(file_content: bytes) -> str:
    """
    Extract text from a .txt file.

    Args:
        file_content: Raw bytes of the text file

    Returns:
        Decoded text content
    """
    try:
        # Try UTF-8 first
        return file_content.decode("utf-8")
    except UnicodeDecodeError:
        # Fall back to latin-1
        try:
            return file_content.decode("latin-1", errors="ignore")
        except Exception as exc:
            raise ValueError(f"Failed to decode text file: {str(exc)}") from exc


def extract_file_text(file_content: bytes, filename: str) -> str:
    """
    Extract text from a file based on its extension.

    Args:
        file_content: Raw bytes of the file
        filename: Name of the file (used to determine type)

    Returns:
        Extracted text content
    """
    file_lower = filename.lower()

    if file_lower.endswith(".pdf"):
        return extract_pdf_text(file_content)
    elif file_lower.endswith(".txt"):
        return extract_text_file(file_content)
    else:
        raise ValueError(
            f"Unsupported file type: {filename}. Supported types: .pdf, .txt"
        )
