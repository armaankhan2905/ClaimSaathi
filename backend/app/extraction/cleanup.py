"""Text clean-up shared by the PDF and OCR paths."""

import re
import unicodedata
from collections import Counter

_PAGE_NUMBER = re.compile(r"^\s*(page\s*)?\d{1,4}(\s*(of|/)\s*\d{1,4})?\s*$", re.IGNORECASE)
# "Page 3 of 12" (or "Page 3") inside a longer header/footer line, and at the end of one
_PAGE_COUNTER = re.compile(r"\bpage\s*\d{1,4}(\s*(of|/)\s*\d{1,4})?\b", re.IGNORECASE)
_TRAILING_PAGE_COUNTER = re.compile(r"[\s\-|·]*\bpage\s*\d{1,4}\s*(of|/)\s*\d{1,4}\s*$", re.IGNORECASE)
# OCR reads bullet symbols as U+FFFD or similar look-alikes at the start of a line
_OCR_BULLET = re.compile(r"^[�·▪●○◦■□►‣⁃]\s*", re.MULTILINE)


def clean_text(text: str) -> str:
    """Normalise one page of text without changing its meaning."""
    # NFKC turns ligatures (ﬁ, ﬂ), full-width digits and non-breaking spaces into plain characters.
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\t", " ")
    text = text.replace("­", "")  # soft hyphen
    text = re.sub(r"[‘’]", "'", text)
    text = re.sub(r"[“”]", '"', text)
    text = _OCR_BULLET.sub("• ", text)
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
    # Only page counters are masked, so "... Page 2 of 4" / "... Page 3 of 4" match, while
    # numbered content like "Clause 1" / "Clause 2" stays distinct.
    # Letters and digits only, so small OCR differences ("Wording -" vs "Wording-") still match.
    line = _PAGE_COUNTER.sub("page#", line.lower())
    return re.sub(r"[^a-z0-9#ऀ-ॿ]", "", line)


def remove_running_headers(pages: list[str]) -> list[str]:
    """Drop page numbers and lines repeated at the top/bottom of most pages (headers, footers)."""
    if not pages:
        return pages
    repeated: set[str] = set()
    if len(pages) >= 2:
        counts = Counter(_normalise_edge(l) for p in pages for l in set(_edge_lines(p)))
        # On 2 pages a line must repeat on both; on longer documents on most pages.
        needed = 2 if len(pages) == 2 else max(3, 0.6 * len(pages))
        repeated = {line for line, c in counts.items() if c >= needed and line}

    cleaned = []
    for page in pages:
        lines = page.split("\n")
        non_empty = [i for i, l in enumerate(lines) if l.strip()]
        edge_idx = set(non_empty[:2] + non_empty[-2:])
        kept = []
        for i, l in enumerate(lines):
            if i in edge_idx:
                if _PAGE_NUMBER.match(l) or _normalise_edge(l) in repeated:
                    continue
                # a footer like "Company name   Page 1 of 1" on a short document: keep the text, drop the counter
                l = _TRAILING_PAGE_COUNTER.sub("", l)
                if not l.strip():
                    continue
            kept.append(l)
        cleaned.append(re.sub(r"\n{3,}", "\n\n", "\n".join(kept)).strip())
    return cleaned
