import numpy as np
import pytest

from app.extraction import ExtractionError, extract, sniff_content_type
from app.extraction.cleanup import clean_text, remove_running_headers
from app.extraction.ocr import assemble_lines

from .doc_factory import CLAUSE_LINES, password_pdf, photo, scanned_pdf, text_pdf


# ---------- clean-up ----------

def test_clean_text_fixes_ligatures_hyphens_and_spaces():
    raw = "The ﬁrst  policy date.\nContinuous cover-\nage applies.\n\n\n\nCo-\nPayment 10%"
    assert clean_text(raw) == "The first policy date.\nContinuous coverage\napplies.\n\nCo-\nPayment 10%"


def test_remove_running_headers_and_page_numbers():
    bodies = ["covers day care", "excludes cosmetic surgery", "limits room rent", "explains the claim process"]
    pages = [f"NAVJEEVAN GENERAL INSURANCE\nClause {i} text here\n{b}\nPage {i} of 4" for i, b in enumerate(bodies, 1)]
    out = remove_running_headers(pages)
    assert out[0] == "Clause 1 text here\ncovers day care"
    assert all("NAVJEEVAN" not in p and "Page" not in p for p in out)
    assert out[3] == "Clause 4 text here\nexplains the claim process"


def test_headers_kept_when_document_is_short():
    pages = ["HEADER\nbody one", "HEADER\nbody two"]
    assert remove_running_headers(pages) == pages


def test_assemble_lines_orders_boxes_and_adds_paragraph_breaks():
    def box(x, y, w=100, h=20):
        return np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]], dtype=float)

    boxes = [box(300, 102), box(50, 100), box(50, 130), box(50, 200)]
    texts = ["right", "left", "second line", "new paragraph"]
    assert assemble_lines(boxes, texts) == "left right\nsecond line\n\nnew paragraph"


# ---------- file type ----------

@pytest.mark.parametrize(
    "data,expected",
    [
        (b"%PDF-1.7 ...", "application/pdf"),
        (b"\xff\xd8\xff\xe0....", "image/jpeg"),
        (b"\x89PNG\r\n\x1a\n....", "image/png"),
        (b"RIFF\x00\x00\x00\x00WEBPVP8 ", "image/webp"),
        (b"PK\x03\x04 a zip or docx", None),
        (b"<html>", None),
    ],
)
def test_sniff_content_type(data, expected):
    assert sniff_content_type(data) == expected


# ---------- reading ----------

def test_digital_pdf_uses_text_layer():
    pdf = text_pdf([CLAUSE_LINES, ["5.1 Room rent", "Room rent is limited to 1% of the sum insured per day."]])
    pages = extract(pdf, "application/pdf")
    assert [p.method for p in pages] == ["text", "text"]
    assert pages[0].text.splitlines()[0] == "4.2 Waiting period for joint replacement"
    assert "1% of the sum insured" in pages[1].text


def test_digital_pdf_drops_header_and_footer():
    pdf = text_pdf([CLAUSE_LINES] * 3, header="Suraksha Health Plus - Policy Wording", footer=True)
    pages = extract(pdf, "application/pdf")
    assert all("Policy Wording" not in p.text and "Page" not in p.text for p in pages)


def test_scanned_pdf_is_ocrd():
    pages = extract(scanned_pdf([CLAUSE_LINES]), "application/pdf")
    assert pages[0].method == "ocr"
    assert pages[0].confidence and pages[0].confidence > 0.9
    assert "Waiting period for joint replacement" in pages[0].text
    assert "24 months" in pages[0].text


def test_photo_is_ocrd():
    page = extract(photo(fmt="PNG"), "image/png")[0]
    assert page.method == "ocr"
    assert "continuous coverage" in page.text


def test_sideways_phone_photo_is_straightened():
    page = extract(photo(sideways=True), "image/jpeg")[0]
    assert "joint replacement" in page.text


def test_password_protected_pdf():
    with pytest.raises(ExtractionError) as e:
        extract(password_pdf(), "application/pdf")
    assert e.value.code == "password_protected"


def test_corrupt_pdf():
    with pytest.raises(ExtractionError) as e:
        extract(b"%PDF-1.7 this is not really a pdf", "application/pdf")
    assert e.value.code == "unreadable_file"


def test_blank_document():
    with pytest.raises(ExtractionError) as e:
        extract(text_pdf([[]]), "application/pdf")
    assert e.value.code == "no_text_found"
