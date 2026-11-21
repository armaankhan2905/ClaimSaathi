"""The downloadable evidence report for a Rejection Check (PDF, in English for the insurer)."""

import html
import io
from datetime import date

import pymupdf

from .understanding.claims import human_date

A4 = pymupdf.paper_rect("a4")
CSS = """
* { font-family: sans-serif; }
body { font-size: 9.8pt; line-height: 1.45; color: #111; }
h1 { font-size: 17pt; margin: 0 0 2pt 0; color: #10264a; }
h2 { font-size: 12pt; margin: 14pt 0 5pt 0; color: #10264a; }
p { margin: 0 0 5pt 0; }
table { border-collapse: collapse; width: 100%; margin: 4pt 0 6pt 0; }
td, th { border: 1px solid #b8c3d4; padding: 4pt 5pt; vertical-align: top; text-align: left; font-size: 9pt; }
th { background: #eaf1fb; }
.muted { color: #5a6b85; font-size: 8.5pt; }
.box { border: 1px solid #b7791f; background: #fbf3e6; padding: 6pt 8pt; margin: 4pt 0 8pt 0; }
.ok { color: #178a5c; font-weight: bold; } .bad { color: #c0453a; font-weight: bold; } .warn { color: #b7791f; font-weight: bold; }
.quote { font-family: serif; font-style: italic; }
"""

ASSESSMENT = {
    "inconsistency": ("Possible inconsistency found", "At least one reason given for the rejection is not supported by the policy wording or the documents."),
    "consistent": ("Rejection appears consistent with the policy", "The reasons given match the policy wording, based on the documents provided."),
    "needs_info": ("More information needed", "Some reasons could not be confirmed or ruled out from the documents provided."),
}
STATUS = {"contradicted": ("Not supported by the policy", "bad"), "supported": ("Supported by the policy", "ok"), "unclear": ("Ask the insurer", "warn")}
TIMELINE = {
    "first_policy": "First policy starts (continuous cover begins)",
    "renewal": "Renewed without a break",
    "break": "Break in cover",
    "waiting_ends": "Waiting period ends",
    "insurer_start": "Date the insurer counted the waiting period from",
    "admission": "Hospital admission",
    "rejection": "Rejection letter",
}
CHECKLIST = {
    "rejection_letter": "Rejection letter",
    "policy_wording": "Policy wording",
    "policy_history": "Policy schedule / renewal receipts showing continuous cover",
    "discharge_summary": "Discharge summary",
    "hospital_bill": "Hospital bills and payment receipts",
    "doctor_note": "Doctor's notes / first diagnosis date",
}


def _e(s) -> str:
    return html.escape(str(s or ""))


def _money(n: int | None) -> str:
    if not n:
        return "-"
    s = str(n)
    head, tail = s[:-3], s[-3:]
    groups = []
    while len(head) > 2:
        groups.insert(0, head[-2:])
        head = head[:-2]
    return "Rs. " + ",".join(([head] if head else []) + groups + [tail])


def _row_explanation(r: dict) -> str:
    d = r.get("data") or {}
    code = r.get("code") or ""
    if r["type"] == "waiting_period" and code.startswith("waiting_over"):
        text = (
            f"The policy counts the {d.get('months')}-month waiting period from the First Policy Date "
            f"({human_date(d.get('policy_start_for_waiting'))}) with continuous cover. It ended on {human_date(d.get('waiting_ends'))}, "
            f"before the admission on {human_date(d.get('admission_date'))}."
        )
        if code == "waiting_over_counted_wrongly":
            text += f" The insurer counted it from {human_date(d.get('insurer_counted_from'))}, the start of the current policy period, which the wording does not provide for."
        return text
    if r["type"] == "waiting_period" and code.startswith("waiting_not_over"):
        return f"The {d.get('months')}-month waiting period ends on {human_date(d.get('waiting_ends'))}, after the admission on {human_date(d.get('admission_date'))}."
    return r.get("explanation_en") or "This reason could not be checked from the documents provided."


def build_report(claim, policy) -> bytes:
    f = claim.facts or {}
    fd = claim.findings or {}
    title, summary = ASSESSMENT.get(fd.get("assessment"), ASSESSMENT["needs_info"])
    parts = [
        "<h1>ClaimSaathi evidence report</h1>",
        f"<p class='muted'>Prepared on {date.today().strftime('%d %b %Y')} from the policyholder's own documents. "
        "This report gives guidance based on those documents; it does not decide legal entitlement.</p>",
        "<h2>Claim</h2><table>",
        f"<tr><th>Claim number</th><td>{_e(f.get('claim_number'))}</td><th>Policy</th><td>{_e(policy.name if policy else '')} ({_e(f.get('policy_number'))})</td></tr>",
        f"<tr><th>Patient</th><td>{_e(f.get('patient'))}</td><th>Hospital</th><td>{_e(f.get('hospital'))}</td></tr>",
        f"<tr><th>Treatment</th><td>{_e(f.get('treatment'))}</td><th>Claimed amount</th><td>{_money(f.get('claimed_amount'))}</td></tr>",
        f"<tr><th>Admission</th><td>{human_date(f.get('admission_date'))}</td><th>Rejection letter</th><td>{human_date(f.get('letter_date'))}</td></tr>",
        "</table>",
        f"<div class='box'><b>{_e(title)}.</b> {_e(summary)}</div>",
        "<h2>Evidence map</h2><table><tr><th>Insurer's reason</th><th>What the policy says</th><th>Evidence</th><th>Finding</th></tr>",
    ]
    for r in fd.get("rows", []):
        q = r.get("policy_quote") or {}
        policy_says = (f"<b>Clause {_e(q.get('ref'))}</b>: <span class='quote'>\"{_e(q.get('quote'))}\"</span>") if q else "-"
        evidence = []
        d = r.get("data") or {}
        if d.get("periods_checked"):
            evidence.append(f"{d['periods_checked']} policy periods, continuous since {human_date(d.get('continuous_since'))}" + ("" if not d.get("breaks") else f"; {len(d['breaks'])} break(s)"))
        evidence += [_e(x) for x in r.get("evidence", []) if x != "policy_history"]
        label, cls = STATUS.get(r["status"], STATUS["unclear"])
        parts.append(
            f"<tr><td>{_e(r.get('insurer_reason'))}</td><td>{policy_says}</td><td>{'<br>'.join(evidence) or '-'}</td>"
            f"<td><span class='{cls}'>{label}</span><br>{_e(_row_explanation(r))}</td></tr>"
        )
    parts.append("</table>")

    parts.append("<h2>Timeline</h2><table><tr><th>Date</th><th>Event</th></tr>")
    for e in fd.get("timeline", []):
        label = TIMELINE.get(e["kind"], e["kind"])
        if e["kind"] == "waiting_ends":
            label = f"{e.get('months')}-month waiting period ends (clause {e.get('clause_ref')})"
        parts.append(f"<tr><td>{human_date(e['date'])}</td><td>{_e(label)}</td></tr>")
    parts.append("</table>")

    parts.append("<h2>Documents</h2><table><tr><th>Document</th><th>Status</th></tr>")
    for c in fd.get("checklist", []):
        status = "<span class='ok'>Provided</span>" if c["have"] else ("<span class='warn'>Missing</span>" if c["important"] else "Optional")
        parts.append(f"<tr><td>{_e(CHECKLIST.get(c['item'], c['item']))}</td><td>{status}</td></tr>")
    parts.append("</table>")

    questions = [q["en"] for q in fd.get("questions", []) if q.get("en")]
    if questions:
        parts.append("<h2>Questions for the insurer</h2><ol>" + "".join(f"<li>{_e(q)}</li>" for q in questions) + "</ol>")
    parts.append(
        "<p class='muted'>Next step: write to the insurer's Grievance Officer with this report. If there is no satisfactory reply "
        "within 30 days, the complaint can be registered on IRDAI's Bima Bharosa portal or taken to the Insurance Ombudsman.</p>"
    )

    story = pymupdf.Story(html="".join(parts), user_css=CSS)
    buf = io.BytesIO()
    writer = pymupdf.DocumentWriter(buf)
    more = True
    while more:
        dev = writer.begin_page(A4)
        more, _ = story.place(A4 + (48, 48, -48, -48))
        story.draw(dev)
        writer.end_page()
    writer.close()
    doc = pymupdf.open(stream=buf.getvalue(), filetype="pdf")
    for page in doc:
        page.insert_text((48, A4.height - 24), f"ClaimSaathi evidence report - claim {f.get('claim_number') or ''} - page {page.number + 1} of {doc.page_count}", fontsize=7, color=(0.45, 0.45, 0.45))
    return doc.tobytes(garbage=3, deflate=True)
