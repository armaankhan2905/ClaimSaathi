"""Turn uploaded files (digital PDFs, scanned PDFs, phone photos) into clean page text."""

from .reader import ExtractionError, ExtractedPage, extract, sniff_content_type

__all__ = ["ExtractionError", "ExtractedPage", "extract", "sniff_content_type"]
