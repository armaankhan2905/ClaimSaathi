"""Build small test documents in memory (all text is fictional)."""

import io

import pymupdf
from PIL import Image

CLAUSE_LINES = [
    "4.2 Waiting period for joint replacement",
    "Expenses for joint replacement surgery are covered after 24 months",
    "of continuous coverage from the date of the first policy.",
]


def text_pdf(pages: list[list[str]], header: str | None = None, footer: bool = False) -> bytes:
    doc = pymupdf.open()
    for n, lines in enumerate(pages, 1):
        page = doc.new_page()
        if header:
            page.insert_text((72, 40), header, fontsize=9)
        y = 100
        for line in lines:
            page.insert_text((72, y), line, fontsize=11)
            y += 18
        if footer:
            page.insert_text((280, 800), f"Page {n} of {len(pages)}", fontsize=9)
    return doc.tobytes()


def scanned_pdf(pages: list[list[str]]) -> bytes:
    """Like a scanner output: every page is just a picture, with no text layer."""
    src = pymupdf.open(stream=text_pdf(pages), filetype="pdf")
    out = pymupdf.open()
    for page in src:
        pix = page.get_pixmap(dpi=150)
        new = out.new_page(width=page.rect.width, height=page.rect.height)
        new.insert_image(new.rect, pixmap=pix)
    return out.tobytes()


def password_pdf() -> bytes:
    doc = pymupdf.open(stream=text_pdf([CLAUSE_LINES]), filetype="pdf")
    return doc.tobytes(encryption=pymupdf.PDF_ENCRYPT_AES_256, owner_pw="owner-x", user_pw="user-x")


def photo(lines: list[str] = CLAUSE_LINES, fmt: str = "JPEG", sideways: bool = False) -> bytes:
    """A 'phone photo' of a page. sideways=True stores it rotated with an EXIF orientation tag."""
    src = pymupdf.open(stream=text_pdf([lines]), filetype="pdf")
    pix = src[0].get_pixmap(dpi=150, clip=pymupdf.Rect(50, 70, 560, 70 + 20 * len(lines) + 30))
    img = Image.frombytes("RGB", (pix.w, pix.h), pix.samples)
    buf = io.BytesIO()
    if sideways:
        img = img.rotate(90, expand=True)  # stored turned left...
        exif = Image.Exif()
        exif[0x0112] = 6  # ...with a tag saying "rotate 90° clockwise to display"
        img.save(buf, fmt, exif=exif)
    else:
        img.save(buf, fmt)
    return buf.getvalue()
