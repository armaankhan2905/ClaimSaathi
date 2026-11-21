"""The fictional sample documents in /samples read correctly (digital and scanned alike)."""

from pathlib import Path

import pytest

from app.extraction import extract

SAMPLES = Path(__file__).resolve().parents[2] / "samples"
pytestmark = pytest.mark.skipif(not SAMPLES.exists(), reason="run scripts/make_sample_docs.py first")


def _read(name: str, content_type: str = "application/pdf"):
    return extract((SAMPLES / name).read_bytes(), content_type)


def test_scanned_wording_matches_digital_wording():
    digital = _read("suraksha-health-plus-policy-wording.pdf")
    scanned = _read("suraksha-health-plus-policy-wording-scanned.pdf")
    assert len(digital) == len(scanned)
    assert all(p.method == "ocr" and p.confidence > 0.95 for p in scanned)
    key = "The 24 months are counted from the First Policy Date"
    assert any(key in p.text for p in digital)
    assert any(key in p.text for p in scanned)
    # running header and footer are gone from every page
    for p in digital + scanned:
        assert "SAMPLE DOCUMENT" not in p.text and "Page " not in p.text.splitlines()[-1]


def test_rejection_letter_photo():
    text = _read("rejection-letter-CLM-26-08817-photo.jpg", "image/jpeg")[0].text
    for expected in ("CLM-26-08817", "NGI/HL/2026/448812", "14 Sep 2026", "1,80,000", "Clause 4.2"):
        assert expected in text
