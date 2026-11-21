"""Split policy text into numbered clauses ("4.2 Specified illnesses and procedures").

Indian policy wordings are numbered documents, so headings are found by their numbering
rather than by an AI model: this is exact, free and works offline. Each clause keeps the
page(s) it came from so every answer can point back to the original.
"""

import re
from dataclasses import dataclass, field

# "4.2 Title", "4.2. Title", "4 Title", "4. Title", "Section 4.2 - Title", "Clause 4.2: Title"
_HEADING = re.compile(
    r"^(?:(?:section|clause|article)\s+)?(?P<ref>\d{1,2}(?:\.\d{1,2}){0,3})\.?\s*[-:–]?\s+(?P<title>[A-Za-z(][^\n]{1,90})$",
    re.IGNORECASE,
)


@dataclass
class SplitClause:
    ref: str  # "4.2"
    title: str  # "Specified illnesses and procedures"
    text: str  # body text (without the heading line)
    section_ref: str  # "4"
    section_title: str  # "Waiting periods"
    page_start: int
    page_end: int
    order: int = 0
    _lines: list[str] = field(default_factory=list, repr=False)


def _is_heading(line: str) -> re.Match | None:
    m = _HEADING.match(line.strip())
    if not m:
        return None
    title = m.group("title").strip()
    # A numbered list item is a sentence ("8. Unproven or experimental treatment."), a heading is a title.
    if title.endswith((".", ";", ",")):
        return None
    if len(title.split()) > 12:
        return None
    if re.match(r"^\d", title) or _DATE_LIKE.match(title):  # "12 Mar 2026", "1 April 2025"
        return None
    return m


_DATE_LIKE = re.compile(r"^(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+\d{2,4}\b", re.IGNORECASE)


def _follows(prev: tuple[int, ...], new: tuple[int, ...]) -> bool:
    """Is `new` a plausible next heading number after `prev`? One skipped number is allowed
    (a heading OCR missed); bigger jumps are list items like "8." inside a section."""
    if not prev:  # first heading: excerpts and endorsements may start at any section
        return True
    next_sections = (prev[0] + 1, prev[0] + 2)
    if len(new) == 1:  # new top-level section: "6" after "5" or "5.3"
        return new[0] in next_sections
    if new[0] == prev[0]:
        if len(new) == 2:  # next sub-clause in the same section: "4.3" after "4.2" or "4"
            prev_sub = prev[1] if len(prev) > 1 else 0
            return new[1] in (prev_sub + 1, prev_sub + 2)
        return new > prev  # deeper numbering ("4.2.1") just has to move forward
    # first sub-clause of the next section when it has no heading of its own ("5.1" after "4.4")
    return new[0] in next_sections and all(n <= 2 for n in new[1:])


def split_clauses(pages: list[tuple[int, str]]) -> list[SplitClause]:
    """`pages` is [(page_number, text)]. Returns clauses in document order.

    Top-level sections with sub-clauses (e.g. "4. Waiting periods" > "4.1", "4.2") become the
    sub-clauses, each remembering its section. A top-level section without sub-clauses
    (e.g. "6. Co-payment") is a clause on its own. Text before the first heading is dropped
    (it is the title block).
    """
    raw: list[SplitClause] = []
    current: SplitClause | None = None
    sections: dict[str, str] = {}
    last_ref_parts: tuple[int, ...] = ()

    for page_no, text in pages:
        for line in text.split("\n"):
            m = _is_heading(line)
            if m:
                ref = m.group("ref")
                parts = tuple(int(p) for p in ref.split("."))
                # Numbering must move forward in order: "3" after "4.2" is a list item, not a new section.
                if _follows(last_ref_parts, parts):
                    last_ref_parts = parts
                    title = m.group("title").strip().rstrip(":")
                    section_ref = ref.split(".")[0]
                    if "." not in ref:
                        sections[section_ref] = title
                    current = SplitClause(
                        ref=ref,
                        title=title,
                        text="",
                        section_ref=section_ref,
                        section_title=sections.get(section_ref, title),
                        page_start=page_no,
                        page_end=page_no,
                    )
                    raw.append(current)
                    continue
            if current is not None:
                current._lines.append(line)
                if line.strip():
                    current.page_end = page_no

    for c in raw:
        c.text = re.sub(r"\n{3,}", "\n\n", "\n".join(c._lines)).strip()

    # Drop section headings whose content is entirely in their sub-clauses.
    has_children = {c.ref.split(".")[0] for c in raw if "." in c.ref}
    clauses = [c for c in raw if "." in c.ref or c.ref not in has_children or len(c.text) > 80]
    for i, c in enumerate(clauses):
        c.order = i
    return clauses
