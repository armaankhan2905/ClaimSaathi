"""Guess what kind of document an upload is from its text.

Used to catch a wrong label (a rejection letter uploaded as "Policy wording") and shown to the
user as a suggestion; it never silently changes what they chose.
"""

import re

POLICY_KINDS = {"policy_wording", "policy_schedule", "endorsement", "previous_policy"}
CLAIM_KINDS = {"rejection_letter", "renewal_receipt", "discharge_summary", "hospital_bill", "doctor_note", "other"}

# Checked in order against the start of the document; the first match wins.
_RULES: list[tuple[str, str]] = [
    ("rejection_letter", r"repudiat|regret to inform|claim (?:is|has been) (?:rejected|denied|declined|not payable)|not admissible|claim .{0,40}not payable"),
    ("renewal_receipt", r"renewal (?:premium )?receipt|premium (?:payment )?receipt|receipt (?:for|of) premium"),
    ("discharge_summary", r"discharge summary|date of discharge"),
    ("hospital_bill", r"\b(?:final|hospital|interim) bill\b|\bbill (?:no|number)\b|\binvoice\b"),
    ("doctor_note", r"\bprescription\b|medical certificate|doctor'?s (?:note|certificate)|\bRx\b"),
    ("endorsement", r"endorsement (?:no|number|schedule)|this endorsement"),
    ("policy_schedule", r"policy schedule|schedule of (?:insurance|benefits)|certificate of insurance"),
    ("policy_wording", r"policy wording|terms (?:and|&) conditions|what is (?:not )?covered|exclusions"),
]


def suggest_kind(text: str) -> str | None:
    head = text[:2500]
    for kind, pattern in _RULES:
        if re.search(pattern, head, re.IGNORECASE):
            return kind
    return None


def is_policy_document(kind: str, suggested: str | None) -> bool:
    """Counts as part of the policy unless the text clearly says it's a claim document."""
    return kind in POLICY_KINDS and suggested not in CLAIM_KINDS
