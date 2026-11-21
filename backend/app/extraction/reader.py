"""Read text out of a PDF or image, page by page.

- Digital PDFs: text is taken straight from the file (fast and exact).
- Scanned PDFs: pages with almost no text layer are rendered and OCR'd.
- Photos (JPEG/PNG/WebP): straightened using the camera's orientation tag, then OCR'd.
"""

import io
from dataclasses import dataclass

import numpy as np

from ..config import get_settings
from .cleanup import clean_text, remove_running_headers
from .ocr import ocr_image

# A page with fewer real characters than this in its text layer is treated as scanned.
MIN_TEXT_CHARS = 40
MAX_IMAGE_SIDE = 2400


class ExtractionError(Exception):
    """`code` is shown to users through a translated message."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass
class ExtractedPage:
    number: int  # 1-based
    text: str
    method: str  # "text" | "ocr"
    confidence: float | None = None


def sniff_content_type(data: bytes) -> str | None:
    """Identify the file from its first bytes; the extension and browser-sent type can't be trusted."""
    head = data[:16]
    if head.startswith(b"%PDF-"):
        return "application/pdf"
    if head.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "image/webp"
    return None


def extract(data: bytes, content_type: str) -> list[ExtractedPage]:
    if content_type == "application/pdf":
        pages = _extract_pdf(data)
    elif content_type.startswith("image/"):
        pages = [_extract_image(data)]
    else:
        raise ExtractionError("unsupported_type")

    cleaned = remove_running_headers([p.text for p in pages])
    for page, text in zip(pages, cleaned):
        page.text = text
    if not any(len(p.text) >= 20 for p in pages):
        raise ExtractionError("no_text_found")
    return pages


def _extract_pdf(data: bytes) -> list[ExtractedPage]:
    import pymupdf

    try:
        doc = pymupdf.open(stream=data, filetype="pdf")
    except Exception as e:  # corrupt or not really a PDF
        raise ExtractionError("unreadable_file") from e
    with doc:
        if doc.needs_pass:
            raise ExtractionError("password_protected")
        if doc.page_count == 0:
            raise ExtractionError("unreadable_file")
        if doc.page_count > get_settings().max_pages:
            raise ExtractionError("too_many_pages")

        pages: list[ExtractedPage] = []
        for page in doc:
            text = clean_text(page.get_text("text", sort=True))
            if sum(c.isalnum() for c in text) >= MIN_TEXT_CHARS:
                pages.append(ExtractedPage(page.number + 1, text, "text"))
                continue
            # Scanned page: render (rotation is applied by MuPDF) and OCR it.
            pix = page.get_pixmap(dpi=get_settings().ocr_dpi, colorspace=pymupdf.csRGB, alpha=False)
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
            result = ocr_image(img)
            ocr_text = clean_text(result.text)
            if len(ocr_text) > len(text):
                pages.append(ExtractedPage(page.number + 1, ocr_text, "ocr", result.confidence))
            else:
                pages.append(ExtractedPage(page.number + 1, text, "text"))
        return pages


def _extract_image(data: bytes) -> ExtractedPage:
    from PIL import Image, ImageOps, UnidentifiedImageError

    try:
        img = Image.open(io.BytesIO(data))
        img = ImageOps.exif_transpose(img)  # phone photos are often stored sideways
        img = img.convert("RGB")
    except (UnidentifiedImageError, OSError) as e:
        raise ExtractionError("unreadable_file") from e
    if max(img.size) > MAX_IMAGE_SIDE:
        img.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE))
    result = ocr_image(np.asarray(img))
    return ExtractedPage(1, clean_text(result.text), "ocr", result.confidence)
