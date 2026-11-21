"""File a Complaint: pre-fill from a Rejection Check, write the letter for each stage, work out deadlines.

The complaint goes up three levels, one after the other:
  1. the insurer's Grievance Redressal Officer (they should reply within 14 days),
  2. IRDAI's Bima Bharosa portal (if the reply is late or doesn't resolve it),
  3. the Insurance Ombudsman (once the insurer has rejected the complaint or not replied within a month,
     and within a year of the insurer's reply).
Letters are written in English so they can go straight to the insurer, IRDAI or the Ombudsman.
Timelines are general guidance; the page says to check the current IRDAI rules.
"""

from datetime import date, timedelta

from .report import _money, _row_explanation
from .understanding.claims import human_date

STAGES = ("insurer", "bima_bharosa", "ombudsman")
SITUATIONS = {  # where the user is right now -> the stage ClaimSaathi recommends
    "not_yet": "insurer",
    "unsatisfied": "bima_bharosa",
    "no_reply": "bima_bharosa",
    "bb_unresolved": "ombudsman",
}
GRIEVANCE_TYPES = {
    "claim_rejected": "Claim rejected (repudiated)",
    "claim_partly_paid": "Claim partly paid",
    "claim_delay": "Delay in claim settlement",
    "policy_service": "Policy servicing",
    "other": "Other",
}
INSURER_REPLY_DAYS = 14  # IRDAI: grievances should be resolved within 14 days
OMBUDSMAN_WAIT_DAYS = 30  # Ombudsman Rules 2017: insurer rejected it, or no reply within one month
OMBUDSMAN_LIMIT_DAYS = 365  # ...and within one year of the insurer's reply
OMBUDSMAN_DECISION_DAYS = 90  # award due within three months of a complete complaint

FIELD_KEYS = {
    "name", "phone", "email", "address", "insurer", "to_email", "policy_number", "claim_number", "amount",
    "patient", "hospital", "treatment", "admission_date", "letter_date", "grievance_type", "ask", "grounds",
    "attachments", "include_report", "situation", "earlier_complaint_date", "earlier_reference", "insurer_reply_date",
}


def _iso(d: date | None) -> str | None:
    return d.isoformat() if d else None


def _date(s) -> date | None:
    try:
        return date.fromisoformat(str(s)[:10]) if s else None
    except ValueError:
        return None


# ---------- pre-fill ----------

def grounds_from_findings(findings: dict | None) -> list[dict]:
    """Grounds for review: every reason the check found unsupported, then reasons the insurer must explain."""
    if not findings:
        return []
    grounds: list[dict] = []
    continuity_added = False
    for r in findings.get("rows", []):
        ref = (r.get("policy_quote") or {}).get("ref") or r.get("clause_ref")
        if r.get("status") == "contradicted":
            text = _row_explanation(r).replace("The insurer counted it from", "The rejection counts it from")
            q = r.get("policy_quote")
            if q and q.get("quote"):
                text = f'Clause {q["ref"]} says: "{q["quote"]}" ' + text
            grounds.append({"text": text, "ref": ref})
            d = r.get("data") or {}
            if d.get("periods_checked") and not d.get("breaks") and not continuity_added:
                grounds.append({
                    "text": f"The enclosed policy schedule and renewal receipts show {d['periods_checked']} policy periods "
                            f"renewed without a break since {human_date(d.get('continuous_since'))}.",
                    "ref": None,
                })
                continuity_added = True
            if r.get("code") == "waiting_over_counted_wrongly" and d.get("insurer_counted_from"):
                grounds.append({
                    "text": f"The rejection letter treats the policy as starting on {human_date(d['insurer_counted_from'])}, "
                            "which is only the latest renewal date, not the First Policy Date.",
                    "ref": ref,
                })
        elif r.get("status") == "unclear" and r.get("question_en"):
            grounds.append({"text": f"The letter says: \"{r.get('insurer_reason')}\". {r['question_en']}", "ref": ref})
    return grounds


def default_ask(facts: dict, findings: dict | None) -> str:
    amount = facts.get("claimed_amount")
    text = "Please review the rejection and settle my claim" + (f" of {_money(amount)}" if amount else "") + " as per the policy terms"
    for r in (findings or {}).get("rows", []):
        d = r.get("data") or {}
        if r.get("status") == "contradicted" and r.get("code", "").startswith("waiting_over") and d.get("waiting_ends"):
            ref = (r.get("policy_quote") or {}).get("ref") or r.get("clause_ref")
            text += f", since the waiting period under Clause {ref} ended on {human_date(d['waiting_ends'])}, before my admission"
            break
    return text + "."


def prefill(user, claim, policy, documents: list) -> dict:
    """Complaint fields filled in from the account, the policy and the Rejection Check (all editable)."""
    facts = (claim.facts if claim else None) or {}
    findings = claim.findings if claim else None
    return {
        "name": user.full_name,
        "phone": "",
        "email": user.email,
        "address": "",
        "insurer": (policy.insurer if policy else "") or "",
        "to_email": "",
        "policy_number": (policy.policy_number if policy and policy.policy_number else facts.get("policy_number")) or "",
        "claim_number": facts.get("claim_number") or "",
        "amount": facts.get("claimed_amount"),
        "patient": facts.get("patient") or "",
        "hospital": facts.get("hospital") or "",
        "treatment": facts.get("treatment") or "",
        "admission_date": facts.get("admission_date"),
        "letter_date": facts.get("letter_date"),
        "grievance_type": "claim_rejected",
        "ask": default_ask(facts, findings),
        "grounds": grounds_from_findings(findings),
        "attachments": [d.id for d in documents if d.status == "ready" and d.kind != "policy_wording"],
        "include_report": bool(claim and claim.status == "ready" and claim.findings),
        "situation": "not_yet",
        "earlier_complaint_date": None,
        "earlier_reference": "",
        "insurer_reply_date": None,
    }


def clean_fields(current: dict, changes: dict) -> dict:
    """Merge edits into the fields, keeping only known keys and sane shapes."""
    out = dict(current)
    for k, v in changes.items():
        if k not in FIELD_KEYS:
            continue
        if k == "grounds":
            v = [{"text": str(g.get("text", ""))[:2000], "ref": (str(g["ref"])[:20] if g.get("ref") else None)} for g in (v or []) if isinstance(g, dict)][:12]
        elif k == "attachments":
            v = [int(x) for x in (v or []) if str(x).isdigit()][:30]
        elif k == "amount":
            v = int(v) if v not in (None, "") and str(v).isdigit() else None
        elif k == "include_report":
            v = bool(v)
        elif k in ("admission_date", "letter_date", "earlier_complaint_date", "insurer_reply_date"):
            v = _iso(_date(v))
        elif k == "situation" and v not in SITUATIONS:
            continue
        elif k == "grievance_type" and v not in GRIEVANCE_TYPES:
            continue
        else:
            v = str(v or "")[:3000]
        out[k] = v
    return out


# ---------- history and deadlines ----------

def last_event(history: list[dict], kind: str, stage: str | None = None) -> dict | None:
    for e in reversed(history or []):
        if e.get("kind") == kind and (stage is None or e.get("stage") == stage):
            return e
    return None


def insurer_complaint(fields: dict, history: list[dict]) -> tuple[date | None, str, date | None, str | None]:
    """When the insurer was written to, its reference, when it replied and how (from ClaimSaathi or what the user told us)."""
    sent = last_event(history, "sent", "insurer")
    reply = last_event(history, "reply", "insurer")
    sent_on = _date(sent["date"]) if sent else _date(fields.get("earlier_complaint_date"))
    reference = (sent.get("reference") if sent else None) or fields.get("earlier_reference") or ""
    reply_on = _date(reply["date"]) if reply else _date(fields.get("insurer_reply_date"))
    outcome = reply.get("outcome") if reply else ("unsatisfied" if fields.get("insurer_reply_date") else None)
    return sent_on, reference, reply_on, outcome


def tracker(stage: str, status: str, fields: dict, history: list[dict], today: date | None = None) -> dict:
    today = today or date.today()
    sent = last_event(history, "sent", stage)
    sent_on = _date(sent["date"]) if sent else None
    reply = last_event(history, "reply", stage)
    if sent_on and reply and _date(reply["date"]) and _date(reply["date"]) < sent_on:
        reply = None
    days = OMBUDSMAN_DECISION_DAYS if stage == "ombudsman" else INSURER_REPLY_DAYS
    reply_due = sent_on + timedelta(days=days) if sent_on else None

    ins_sent, _, ins_reply, ins_outcome = insurer_complaint(fields, history)
    if ins_reply and ins_outcome == "unsatisfied":
        ombudsman_from, ombudsman_by = ins_reply, ins_reply + timedelta(days=OMBUDSMAN_LIMIT_DAYS)
    elif ins_sent:
        ombudsman_from = ins_sent + timedelta(days=OMBUDSMAN_WAIT_DAYS)
        ombudsman_by = ombudsman_from + timedelta(days=OMBUDSMAN_LIMIT_DAYS)
    else:
        ombudsman_from = ombudsman_by = None

    unsatisfied = bool(reply and reply.get("outcome") == "unsatisfied")
    can_escalate: list[str] = []
    if status == "sent" and stage != "ombudsman":
        if stage == "insurer" and (unsatisfied or (reply_due and today >= reply_due)):
            can_escalate.append("bima_bharosa")
        if ombudsman_from and today >= ombudsman_from and (not ombudsman_by or today <= ombudsman_by):
            can_escalate.append("ombudsman")
        elif stage == "bima_bharosa" and (unsatisfied or (reply_due and today >= reply_due)) and ombudsman_from:
            can_escalate.append("ombudsman")
    return {
        "sent_on": _iso(sent_on),
        "reference": (sent or {}).get("reference") or "",
        "reply_due": _iso(reply_due),
        "days_left": (reply_due - today).days if reply_due and status == "sent" and not reply else None,
        "replied": reply.get("outcome") if reply else None,
        "replied_on": reply.get("date") if reply else None,
        "can_escalate": can_escalate,
        "escalate_after": _iso(reply_due) if stage != "ombudsman" else None,
        "ombudsman_from": _iso(ombudsman_from),
        "ombudsman_by": _iso(ombudsman_by),
    }


def recommended_stage(fields: dict) -> str:
    return SITUATIONS.get(fields.get("situation") or "not_yet", "insurer")


# ---------- the letter ----------

def _attachment_names(fields: dict, documents: list, has_report: bool) -> list[str]:
    by_id = {d.id: d for d in documents}
    names = [by_id[i].filename for i in fields.get("attachments") or [] if i in by_id]
    if fields.get("include_report") and has_report:
        names.append("ClaimSaathi evidence report (PDF)")
    return names


def build_letter(stage: str, fields: dict, history: list[dict], documents: list, has_report: bool, today: date | None = None) -> dict:
    """The letter as structured text: shown as a live preview, copied, e-mailed and printed to PDF."""
    today = today or date.today()
    f = fields
    insurer = f.get("insurer") or "the insurer"
    claim_no = f.get("claim_number") or "(claim number)"
    policy_no = f.get("policy_number") or "(policy number)"
    amount = _money(f.get("amount")) if f.get("amount") else None
    treatment = f.get("treatment") or "treatment"

    what = f"my claim{' of ' + amount if amount else ''} for {treatment}"
    if f.get("patient"):
        what += f" for {f['patient']}"
    if f.get("hospital"):
        what += f" at {f['hospital']}"
    if f.get("admission_date"):
        what += f" (admitted on {human_date(f['admission_date'])})"
    rejected = f"was rejected by your letter dated {human_date(f['letter_date'])}" if f.get("letter_date") else "was rejected"
    rejected_3p = rejected.replace("your letter", "the insurer's letter")
    gtype = GRIEVANCE_TYPES.get(f.get("grievance_type") or "claim_rejected", "Claim rejected")

    ins_sent, ins_ref, ins_reply, ins_outcome = insurer_complaint(f, history)
    earlier = ""
    if ins_sent:
        earlier = f"I complained to the insurer's Grievance Redressal Officer on {human_date(_iso(ins_sent))}" + (f" (reference {ins_ref})" if ins_ref else "") + ". "
        if ins_reply and ins_outcome == "unsatisfied":
            earlier += f"The insurer replied on {human_date(_iso(ins_reply))}, but the reply does not resolve my complaint."
        else:
            earlier += "I have not received a reply that resolves it."
    bb = last_event(history, "sent", "bima_bharosa")

    grounds = [g for g in (f.get("grounds") or []) if (g.get("text") or "").strip()]
    paragraphs: list[str]
    closing_note: str
    if stage == "insurer":
        to = f"The Grievance Redressal Officer, {insurer}"
        subject = f"Request to review the rejection of claim {claim_no} under policy {policy_no}"
        paragraphs = [f"Dear Sir/Madam,", f"I hold policy {policy_no} with you. {what[0].upper() + what[1:]} {rejected}."]
        intro = "I request a review of this decision on the following grounds:"
        closing_note = (
            "If you rely on any other ground, please state it in writing with the clause reference. "
            "Please acknowledge this complaint and send your reply within 14 days, as required by IRDAI."
        )
    elif stage == "bima_bharosa":
        to = "IRDAI Bima Bharosa grievance portal (bimabharosa.irdai.gov.in)"
        subject = f"Complaint against {insurer}: {gtype.lower()}, claim {claim_no}, policy {policy_no}"
        paragraphs = [f"{what[0].upper() + what[1:]} under policy {policy_no} with {insurer} {rejected_3p}."]
        if earlier:
            paragraphs.append(earlier)
        intro = "The rejection is not supported by the policy, for these reasons:"
        closing_note = "I request IRDAI to take up this complaint with the insurer."
    else:
        to = "The Insurance Ombudsman (office covering the policyholder's area, see cioins.co.in)"
        subject = f"Complaint under Rule 14 of the Insurance Ombudsman Rules, 2017 against {insurer}"
        paragraphs = [
            "Respected Sir/Madam,",
            f"I hold policy {policy_no} with {insurer}. {what[0].upper() + what[1:]} {rejected_3p}. "
            f"Nature of complaint: {gtype}.",
        ]
        if earlier:
            paragraphs.append(earlier)
        if bb:
            paragraphs.append(f"I also registered the complaint on IRDAI's Bima Bharosa portal on {human_date(bb['date'])}" + (f" (reference {bb['reference']})" if bb.get("reference") else "") + ".")
        intro = "Grounds of complaint:"
        closing_note = (
            (f"Amount in dispute: {amount}. " if amount else "")
            + "I declare that this complaint is not pending before, and has not been decided by, any court, consumer forum or arbitrator, "
            "and that it is made within one year of the insurer's reply."
        )

    ask_label = {"insurer": "What I am asking for", "bima_bharosa": "Relief sought", "ombudsman": "Relief sought"}[stage]
    contact = [x for x in (f.get("name"), f.get("address"), f.get("phone") and f"Mobile: {f['phone']}", f.get("email") and f"Email: {f['email']}") if x]
    return {
        "to": to,
        "date": human_date(_iso(today)),
        "subject": subject,
        "paragraphs": paragraphs,
        "grounds_intro": intro,
        "grounds": grounds,
        "ask_label": ask_label,
        "ask": (f.get("ask") or "").strip(),
        "closing_note": closing_note,
        "sign_off": "Yours faithfully," if stage != "bima_bharosa" else "",
        "contact": contact,
        "attachments": _attachment_names(f, documents, has_report),
    }


def letter_text(letter: dict) -> str:
    """Plain text of the letter (for copying, e-mail, or pasting into the Bima Bharosa form)."""
    lines = [f"To: {letter['to']}", f"Date: {letter['date']}", "", f"Subject: {letter['subject']}", ""]
    for p in letter["paragraphs"]:
        lines += [p, ""]
    if letter["grounds"]:
        lines.append(letter["grounds_intro"])
        for i, g in enumerate(letter["grounds"], 1):
            lines.append(f"{i}. {g['text'].strip()}" + (f" [Clause {g['ref']}]" if g.get("ref") else ""))
        lines.append("")
    if letter["ask"]:
        lines += [f"{letter['ask_label']}: {letter['ask']}", ""]
    lines += [letter["closing_note"], ""]
    if letter["attachments"]:
        lines.append("Enclosures:")
        lines += [f"- {a}" for a in letter["attachments"]]
        lines.append("")
    if letter["sign_off"]:
        lines.append(letter["sign_off"])
    lines += letter["contact"]
    return "\n".join(lines).strip() + "\n"


# ---------- calendar reminder ----------

def reminder_ics(complaint_id: int, stage: str, fields: dict, track: dict) -> str | None:
    """An all-day calendar event on the reply due date (day before as the alarm)."""
    due = _date(track.get("reply_due"))
    if not due:
        return None
    who = {"insurer": "insurer", "bima_bharosa": "Bima Bharosa", "ombudsman": "Insurance Ombudsman"}[stage]
    summary = f"ClaimSaathi: reply due from {who} (claim {fields.get('claim_number') or ''})".strip()
    desc = (
        f"Your complaint about claim {fields.get('claim_number') or ''} was sent on {human_date(track.get('sent_on'))}. "
        f"If there is no reply that resolves it, open ClaimSaathi to escalate."
    )
    stamp = date.today().strftime("%Y%m%d")
    return "\r\n".join([
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//ClaimSaathi//Complaint reminder//EN", "CALSCALE:GREGORIAN",
        "BEGIN:VEVENT",
        f"UID:claimsaathi-complaint-{complaint_id}-{stage}@claimsaathi",
        f"DTSTAMP:{stamp}T000000Z",
        f"DTSTART;VALUE=DATE:{due.strftime('%Y%m%d')}",
        f"DTEND;VALUE=DATE:{(due + timedelta(days=1)).strftime('%Y%m%d')}",
        f"SUMMARY:{_ics_escape(summary)}",
        f"DESCRIPTION:{_ics_escape(desc)}",
        "BEGIN:VALARM", "ACTION:DISPLAY", "TRIGGER:-P1D", f"DESCRIPTION:{_ics_escape(summary)}", "END:VALARM",
        "END:VEVENT", "END:VCALENDAR", "",
    ])


def _ics_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")
