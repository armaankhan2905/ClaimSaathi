"""Complaint letter PDF, and the complaint package (letter + evidence report + attached documents in one PDF)."""

import html
import io
import logging

import pymupdf

from . import storage

log = logging.getLogger(__name__)

A4 = pymupdf.paper_rect("a4")
CSS = """
* { font-family: serif; }
body { font-size: 11pt; line-height: 1.5; color: #111; }
p { margin: 0 0 8pt 0; }
ol { margin: 0 0 8pt 0; }
li { margin: 0 0 5pt 0; }
.meta { font-family: sans-serif; font-size: 9.5pt; color: #333; }
.subject { font-weight: bold; }
.ref { font-family: sans-serif; font-size: 8.5pt; color: #10264a; }
.small { font-size: 9.5pt; }
"""


def _e(s) -> str:
    return html.escape(str(s or ""))


def letter_pdf(letter: dict) -> bytes:
    parts = [
        f"<p class='meta'>To: {_e(letter['to'])}<br>Date: {_e(letter['date'])}</p>",
        f"<p class='subject'>Subject: {_e(letter['subject'])}</p>",
    ]
    parts += [f"<p>{_e(p)}</p>" for p in letter["paragraphs"]]
    if letter["grounds"]:
        parts.append(f"<p>{_e(letter['grounds_intro'])}</p><ol>")
        for g in letter["grounds"]:
            ref = f" <span class='ref'>[Clause {_e(g['ref'])}]</span>" if g.get("ref") else ""
            parts.append(f"<li>{_e(g['text'])}{ref}</li>")
        parts.append("</ol>")
    if letter["ask"]:
        parts.append(f"<p><b>{_e(letter['ask_label'])}:</b> {_e(letter['ask'])}</p>")
    parts.append(f"<p>{_e(letter['closing_note'])}</p>")
    if letter["attachments"]:
        parts.append("<p class='small'><b>Enclosures:</b><br>" + "<br>".join(f"{i}. {_e(a)}" for i, a in enumerate(letter["attachments"], 1)) + "</p>")
    if letter["sign_off"]:
        parts.append(f"<p>{_e(letter['sign_off'])}</p>")
    if letter["contact"]:
        parts.append("<p>" + "<br>".join(_e(c) for c in letter["contact"]) + "</p>")

    story = pymupdf.Story(html="".join(parts), user_css=CSS)
    buf = io.BytesIO()
    writer = pymupdf.DocumentWriter(buf)
    more = True
    while more:
        dev = writer.begin_page(A4)
        more, _ = story.place(A4 + (60, 60, -60, -60))
        story.draw(dev)
        writer.end_page()
    writer.close()
    return buf.getvalue()


def _document_pdf(doc) -> pymupdf.Document | None:
    """An uploaded file as PDF pages (photos become one page each)."""
    try:
        data = storage.load(doc.storage_key)
        if doc.content_type == "application/pdf":
            return pymupdf.open(stream=data, filetype="pdf")
        img = pymupdf.open(stream=data, filetype=doc.content_type.split("/")[-1])
        return pymupdf.open("pdf", img.convert_to_pdf())
    except Exception:  # an unreadable attachment shouldn't stop the package
        log.exception("could not add document %s to the complaint package", doc.id)
        return None


def package_pdf(letter: dict, report: bytes | None, documents: list) -> bytes:
    """Letter first, then the evidence report, then each attachment, with a small label on every page."""
    out = pymupdf.open("pdf", letter_pdf(letter))
    sections: list[tuple[str, pymupdf.Document]] = []
    if report:
        sections.append(("ClaimSaathi evidence report", pymupdf.open("pdf", report)))
    for d in documents:
        pdf = _document_pdf(d)
        if pdf is not None:
            sections.append((d.filename, pdf))
    for i, (label, pdf) in enumerate(sections, 1):
        start = out.page_count
        out.insert_pdf(pdf)
        for pno in range(start, out.page_count):
            out[pno].insert_text((24, 16), f"Enclosure {i}: {label}"[:110], fontsize=7, color=(0.35, 0.35, 0.35))
    return out.tobytes(garbage=3, deflate=True)
