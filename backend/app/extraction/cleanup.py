"""Text clean-up shared by the PDF and OCR paths."""

import re
import unicodedata
from collections import Counter

_PAGE_NUMBER = re.compile(r"^\s*(page\s*)?\d{1,4}(\s*(of|/)\s*\d{1,4})?\s*$", re.IGNORECASE)


def clean_text(text: str) -> str:
    """Normalise one page of text without changing its meaning."""
    # NFKC turns ligatures (ﬁ, ﬂ), full-width digits and non-breaking spaces into plain characters.
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\t", " ")
    text = text.replace("­", "")  # soft hyphen
    text = re.sub(r"[‘’]", "'", text)
    text = re.sub(r"[“”]", '"', text)
    # "cover-\nage" -> "coverage\n" only when both sides are lowercase letters (keeps "Co-\nPayment")
    text = re.sub(r"([a-z])-\n([a-z]+)", lambda m: f"{m.group(1)}{m.group(2)}\n", text)
    lines = [re.sub(r" {2,}", " ", line).strip() for line in text.split("\n")]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _edge_lines(text: str, n: int = 2) -> list[str]:
    lines = [l for l in text.split("\n") if l.strip()]
    return lines[:n] + lines[-n:]


def _normalise_edge(line: str) -> str:
    # Exact text only: numbered lines like "Clause 1" / "Clause 2" are content, not a header.
    # Page numbers ("Page 3 of 12") are caught separately by _PAGE_NUMBER.
    return re.sub(r"\s+", " ", line.lower()).strip()


def remove_running_headers(pages: list[str]) -> list[str]:
    """Drop page numbers and lines repeated at the top/bottom of most pages (headers, footers)."""
    if not pages:
        return pages
    repeated: set[str] = set()
    if len(pages) >= 3:
        counts = Counter(_normalise_edge(l) for p in pages for l in set(_edge_lines(p)))
        repeated = {line for line, c in counts.items() if c >= max(3, 0.6 * len(pages))}

    cleaned = []
    for page in pages:
        lines = page.split("\n")
        non_empty = [i for i, l in enumerate(lines) if l.strip()]
        edge_idx = set(non_empty[:2] + non_empty[-2:])
        kept = [
            l
            for i, l in enumerate(lines)
            if not (i in edge_idx and (_PAGE_NUMBER.match(l) or _normalise_edge(l) in repeated))
        ]
        cleaned.append(re.sub(r"\n{3,}", "\n\n", "\n".join(kept)).strip())
    return cleaned
