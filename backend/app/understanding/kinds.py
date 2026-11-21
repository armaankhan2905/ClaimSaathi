"""Guess what kind of document an upload is from its text.

Used to catch a wrong label (a rejection letter uploaded as "Policy wording") and shown to the
user as a suggestion; it never silently changes what they chose.
"""

import re

POLICY_KINDS = {"policy_wording", "policy_schedule", "endorsement", "previous_policy"}
CLAIM_KINDS = {"rejection_letter", "renewal_receipt", "discharge_summary", "hospital_bill", "doctor_note", "other"}

# Checked in order; the first match wins. "title" rules look only at the first lines (what the
# document calls itself), "head" rules at the first 2500 characters. A wording that mentions
# "the Policy Schedule" in its preamble is still a wording: its title says so.
_RULES: list[tuple[str, str, str]] = [
    ("rejection_letter", "head", r"repudiat|regret to inform|claim (?:is|has been) (?:rejected|denied|declined|not payable)|not admissible|claim .{0,40}not payable"),
    ("renewal_receipt", "head", r"renewal (?:premium )?receipt|premium (?:payment )?receipt|receipt (?:for|of) premium"),
    ("discharge_summary", "head", r"discharge summary|date of discharge"),
    ("hospital_bill", "head", r"\b(?:final|hospital|interim) bill\b|\bbill (?:no|number)\b|\binvoice\b"),
    ("doctor_note", "head", r"\bprescription\b|medical certificate|doctor'?s (?:note|certificate)|\bRx\b"),
    ("endorsement", "title", r"^\s*endorsement"),
    ("policy_wording", "title", r"policy wording|terms (?:and|&) conditions"),
    ("policy_schedule", "title", r"policy schedule|schedule of (?:insurance|benefits)|certificate of insurance"),
    ("endorsement", "head", r"endorsement (?:no|number|schedule)|this endorsement"),
    ("policy_wording", "head", r"policy wording|terms (?:and|&) conditions|what is (?:not )?covered|exclusions|waiting period"),
    ("policy_schedule", "head", r"policy schedule|schedule of (?:insurance|benefits)|certificate of insurance"),
]


def suggest_kind(text: str) -> str | None:
    # The title block: the first few short, heading-like lines (body sentences are longer).
    title = "\n".join(l for l in [l for l in text.split("\n") if l.strip()][:4] if len(l.strip()) <= 80)
    head = text[:2500]
    flags = re.IGNORECASE | re.MULTILINE
    # Claim documents first (a rejection letter may quote the policy wording).
    for kind, scope, pattern in _RULES:
        if scope == "head" and kind in CLAIM_KINDS and re.search(pattern, head, flags):
            return kind
    # Then whichever document type the title names first ("Policy Schedule ... read with the Policy Wording").
    in_title = [(m.start(), kind) for kind, scope, pattern in _RULES if scope == "title" and (m := re.search(pattern, title, flags))]
    if in_title:
        return min(in_title)[1]
    for kind, scope, pattern in _RULES:
        if scope == "head" and kind not in CLAIM_KINDS and re.search(pattern, head, flags):
            return kind
    return None


def is_policy_document(kind: str, suggested: str | None) -> bool:
    """Counts as part of the policy unless the text clearly says it's a claim document."""
    return kind in POLICY_KINDS and suggested not in CLAIM_KINDS
