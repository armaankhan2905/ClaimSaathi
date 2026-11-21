"""Parse the date formats Indian policy documents use."""

import re
from datetime import date

_MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
DATE_PATTERN = (
    r"(?:\d{1,2}[\s\-]+[A-Za-z]{3,9}\.?[\s\-,]+\d{4}"  # 12 Mar 2026, 12-Mar-2026
    r"|[A-Za-z]{3,9}\.?\s+\d{1,2},?\s+\d{4}"  # March 12, 2026
    r"|\d{4}-\d{2}-\d{2}"  # 2026-03-12
    r"|\d{1,2}[/.\-]\d{1,2}[/.\-]\d{4})"  # 12/03/2026 (day first, as in India)
)


def parse_date(s: str | None) -> date | None:
    if not s:
        return None
    s = s.strip().replace(",", " ")
    try:
        if m := re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s):
            return date(int(m[1]), int(m[2]), int(m[3]))
        if m := re.fullmatch(r"(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{4})", s):
            return date(int(m[3]), int(m[2]), int(m[1]))
        if m := re.fullmatch(r"(\d{1,2})[\s\-]+([A-Za-z]{3,9})\.?[\s\-]+(\d{4})", s):
            return date(int(m[3]), _MONTHS[m[2][:3].lower()], int(m[1]))
        if m := re.fullmatch(r"([A-Za-z]{3,9})\.?\s+(\d{1,2})\s+(\d{4})", s):
            return date(int(m[3]), _MONTHS[m[1][:3].lower()], int(m[2]))
    except (KeyError, ValueError):
        return None
    return None


def iso(d: date | None) -> str | None:
    return d.isoformat() if d else None
