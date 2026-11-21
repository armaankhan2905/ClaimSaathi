"""Generate the fictional sample documents in /samples.

Run from the backend folder:  python scripts/make_sample_docs.py

Every insurer, person, policy number and clause here is made up for testing ClaimSaathi.
The health policy is written so the demo case works: the insurer rejects a knee replacement
claim by counting the 24-month waiting period from the latest renewal, while clause 4.2
counts it from the First Policy Date.
"""

import io
import random
from pathlib import Path

import pymupdf
from PIL import Image, ImageFilter

OUT = Path(__file__).resolve().parents[2] / "samples"
A4 = pymupdf.paper_rect("a4")
SAMPLE_NOTE = "SAMPLE DOCUMENT - fictional, for testing ClaimSaathi only"

CSS = """
* { font-family: sans-serif; }
body { font-size: 10pt; line-height: 1.4; color: #111; }
h1 { font-size: 17pt; margin: 0 0 4pt 0; }
h2 { font-size: 12pt; margin: 14pt 0 4pt 0; }
h3 { font-size: 10.5pt; margin: 8pt 0 2pt 0; }
p { margin: 0 0 5pt 0; text-align: justify; }
li { margin-bottom: 2pt; }
table { border-collapse: collapse; width: 100%; margin: 6pt 0; }
td, th { border: 1px solid #888; padding: 3pt 5pt; font-size: 9.5pt; text-align: left; vertical-align: top; }
th { background: #eee; }
.small { font-size: 8.5pt; color: #444; }
"""

# --------------------------------------------------------------------------- health policy wording

HEALTH_WORDING = """
<h1>Suraksha Health Plus</h1>
<p><b>Navjeevan General Insurance Company Limited</b><br>
Individual Health Insurance Policy - Policy Wording<br>
UIN: NGIHLIP26001V012526</p>

<h2>1. Preamble</h2>
<p>This Policy is a contract between the Policyholder and Navjeevan General Insurance Company Limited
(the Company). In return for the premium paid, the Company will pay the expenses described in this
Policy, subject to its terms, conditions, limits and exclusions, for treatment taken during the Policy
Period. The Policy Schedule, the proposal form and any endorsements form part of this Policy.</p>

<h2>2. Definitions</h2>
<h3>2.1 Accident</h3>
<p>A sudden, unforeseen and involuntary event caused by external, visible and violent means.</p>
<h3>2.2 Continuous Coverage</h3>
<p>Uninterrupted coverage under this Policy, or under an earlier health insurance policy with the
Company, that has been renewed on or before its expiry or within the Grace Period, without any break.
Coverage transferred to the Company under the portability rules also counts as Continuous Coverage.</p>
<h3>2.3 First Policy Date</h3>
<p>The start date of the first health insurance policy issued by the Company to the Insured Person,
from which Continuous Coverage has been maintained up to the current Policy Period. The First Policy
Date is shown in the Policy Schedule.</p>
<h3>2.4 Grace Period</h3>
<p>The period of 30 days immediately after the expiry of the Policy Period during which the Policy may
be renewed without losing Continuous Coverage. No claim is payable for treatment taken during the
Grace Period itself.</p>
<h3>2.5 Hospital</h3>
<p>An institution registered with the local authorities for in-patient care and treatment, with at least
10 in-patient beds, qualified nursing staff round the clock, qualified medical practitioners in charge
round the clock, and a fully equipped operation theatre.</p>
<h3>2.6 Pre-existing Disease</h3>
<p>Any condition, ailment, injury or disease that was diagnosed by a physician, or for which medical
advice or treatment was received, within 36 months before the First Policy Date.</p>
<h3>2.7 Sum Insured</h3>
<p>The maximum amount the Company will pay for all claims made during one Policy Period, as shown in the
Policy Schedule.</p>
<h3>2.8 Waiting Period</h3>
<p>A period, counted as described in Section 4, during which the Company will not pay for specified
treatment.</p>

<h2>3. What is covered</h2>
<h3>3.1 In-patient hospitalisation</h3>
<p>Medical expenses for hospitalisation of more than 24 consecutive hours for an illness or injury that
starts during the Policy Period, up to the Sum Insured.</p>
<h3>3.2 Room, boarding and nursing</h3>
<p>Room rent, boarding and nursing charges are payable up to 1% of the Sum Insured per day. Intensive
care unit charges are payable up to 2% of the Sum Insured per day. If the Insured Person stays in a
room whose rent is higher than the limit, all associated medical expenses (except medicines, implants
and consumables) will be paid in the same proportion as the eligible room rent bears to the actual
room rent.</p>
<h3>3.3 Pre-hospitalisation expenses</h3>
<p>Medical expenses incurred in the 30 days before admission, for the same condition.</p>
<h3>3.4 Post-hospitalisation expenses</h3>
<p>Medical expenses incurred in the 60 days after discharge, for the same condition.</p>
<h3>3.5 Day care treatment</h3>
<p>Treatment listed as day care that needs less than 24 hours of hospitalisation because of technological
advancement, up to the Sum Insured.</p>
<h3>3.6 Road ambulance</h3>
<p>Ambulance charges up to Rs. 2,000 per hospitalisation.</p>
<h3>3.7 Maternity expenses</h3>
<p>Expenses for childbirth, including caesarean section, up to Rs. 50,000 per Policy Period, after a
Waiting Period of 36 months from the First Policy Date.</p>
<h3>3.8 AYUSH treatment</h3>
<p>In-patient Ayurveda, Yoga, Unani, Siddha and Homeopathy treatment in a government-recognised hospital,
up to 25% of the Sum Insured.</p>

<h2>4. Waiting periods</h2>
<h3>4.1 Initial waiting period</h3>
<p>No expenses are payable for any illness contracted within the first 30 days from the First Policy
Date, except for treatment needed because of an Accident. This waiting period does not apply on renewal
with Continuous Coverage.</p>
<h3>4.2 Specified illnesses and procedures</h3>
<p>Expenses for the following illnesses and procedures are payable only after 24 months of Continuous
Coverage from the First Policy Date, unless the treatment is needed because of an Accident:</p>
<ul>
<li>joint replacement surgery, including knee and hip replacement;</li>
<li>cataract;</li>
<li>hernia, hydrocele and piles;</li>
<li>benign prostatic hypertrophy;</li>
<li>gall bladder and kidney stones;</li>
<li>surgery for varicose veins;</li>
<li>hysterectomy for benign conditions.</li>
</ul>
<p>The 24 months are counted from the First Policy Date and not from the start of the current Policy
Period. Time already served under earlier policies with Continuous Coverage is credited in full on
renewal.</p>
<h3>4.3 Pre-existing diseases</h3>
<p>Expenses related to a Pre-existing Disease are payable only after 36 months of Continuous Coverage
from the First Policy Date.</p>
<h3>4.4 Increase in Sum Insured</h3>
<p>If the Sum Insured is increased on renewal, the waiting periods in 4.1 to 4.3 apply afresh only to the
amount of the increase, from the date of the increase.</p>

<h2>5. What is not covered (exclusions)</h2>
<p>The Company will not pay for:</p>
<ol>
<li>Cosmetic or plastic surgery, unless needed to treat an injury from an Accident or a burn.</li>
<li>Treatment of obesity or weight control, except bariatric surgery meeting the regulator's criteria.</li>
<li>Intentional self-injury or attempted suicide.</li>
<li>Injury from participation in hazardous or adventure sports.</li>
<li>Treatment arising from abuse of alcohol, drugs or other intoxicating substances.</li>
<li>Dental treatment, unless needing hospitalisation because of an Accident.</li>
<li>Spectacles, contact lenses, hearing aids and other external aids.</li>
<li>Unproven or experimental treatment.</li>
<li>War, invasion, act of foreign enemy, or nuclear contamination.</li>
<li>Admission mainly for investigation or diagnosis with no active treatment.</li>
</ol>

<h2>6. Co-payment</h2>
<p>The Insured Person bears 10% of every admissible claim for treatment in a hospital outside the
Company's network. If the Insured Person was aged 61 or more on the First Policy Date, a co-payment of
20% applies to every admissible claim instead.</p>

<h2>7. How to make a claim</h2>
<h3>7.1 Telling the Company</h3>
<p>For planned admission, inform the Company or its claims administrator at least 48 hours before
admission. For emergency admission, inform within 24 hours of admission.</p>
<h3>7.2 Cashless treatment</h3>
<p>Cashless treatment is available at network hospitals after pre-authorisation. Approval or denial of
pre-authorisation will be given within one hour of receiving the complete request.</p>
<h3>7.3 Reimbursement</h3>
<p>Submit the claim form with the following within 30 days of discharge: discharge summary, final bill
with break-up, payment receipts, investigation reports, prescriptions, and the doctor's certificate
where applicable.</p>

<h2>8. Settling or rejecting a claim</h2>
<p>The Company will settle or reject a claim within 30 days of receiving the last necessary document.
If a claim is rejected, the Company will tell the Insured Person in writing, giving the specific reasons
and the clause of this Policy relied on. If settlement is delayed beyond 30 days, the Company will pay
interest at 2% above the bank rate for the period of delay.</p>

<h2>9. Grievances</h2>
<p>For any complaint, write to the Grievance Officer at grievance@navjeevan-gi.example or call
1800-000-0000. The Company will acknowledge the complaint and reply within 14 days. If the Insured
Person is not satisfied with the reply, or gets no reply within 30 days, they may register the complaint
on the Bima Bharosa portal of IRDAI, and may approach the Insurance Ombudsman within one year of the
Company's final reply.</p>

<h2>10. Renewal</h2>
<p>The Policy is ordinarily renewable for life. Renewal will not be refused because of claims made
earlier. The Policy may be renewed within the Grace Period without losing Continuous Coverage.</p>

<h2>11. Free look period and cancellation</h2>
<p>The Policyholder may return a new policy within 30 days of receiving it if they do not agree with its
terms. The Policyholder may cancel the Policy at any time; the premium for the unexpired period will be
refunded on a pro-rata basis if no claim has been made.</p>
"""

HEALTH_SCHEDULE = """
<h1>Policy Schedule</h1>
<p><b>Suraksha Health Plus</b> - Navjeevan General Insurance Company Limited</p>
<table>
<tr><th>Policy number</th><td>NGI/HL/2026/448812</td></tr>
<tr><th>Policyholder</th><td>Rohit Sharma</td></tr>
<tr><th>Address</th><td>14 Sample Lane, Indiranagar, Bengaluru 560038</td></tr>
<tr><th>Policy period</th><td>12 Mar 2026 to 11 Mar 2027 (both days inclusive)</td></tr>
<tr><th>First Policy Date</th><td>12 Mar 2022</td></tr>
<tr><th>Plan</th><td>Individual</td></tr>
<tr><th>Sum Insured</th><td>Rs. 5,00,000</td></tr>
<tr><th>Room rent limit</th><td>1% of Sum Insured per day (Rs. 5,000)</td></tr>
<tr><th>ICU limit</th><td>2% of Sum Insured per day (Rs. 10,000)</td></tr>
<tr><th>Co-payment</th><td>10% outside network hospitals</td></tr>
<tr><th>Premium</th><td>Rs. 10,576 + GST Rs. 1,904 = Rs. 12,480</td></tr>
</table>
<h2>Insured person</h2>
<table>
<tr><th>Name</th><th>Relationship</th><th>Date of birth</th><th>Pre-existing diseases declared</th></tr>
<tr><td>Rohit Sharma</td><td>Self</td><td>08 Jul 1979</td><td>None</td></tr>
</table>
<h2>Policy history (Continuous Coverage)</h2>
<table>
<tr><th>Policy number</th><th>Period</th><th>Sum Insured</th></tr>
<tr><td>NGI/HL/2022/118204</td><td>12 Mar 2022 - 11 Mar 2023</td><td>Rs. 5,00,000</td></tr>
<tr><td>NGI/HL/2023/207731</td><td>12 Mar 2023 - 11 Mar 2024</td><td>Rs. 5,00,000</td></tr>
<tr><td>NGI/HL/2024/310962</td><td>12 Mar 2024 - 11 Mar 2025</td><td>Rs. 5,00,000</td></tr>
<tr><td>NGI/HL/2025/389457</td><td>12 Mar 2025 - 11 Mar 2026</td><td>Rs. 5,00,000</td></tr>
<tr><td>NGI/HL/2026/448812</td><td>12 Mar 2026 - 11 Mar 2027</td><td>Rs. 5,00,000</td></tr>
</table>
<h2>Nominee</h2>
<p>Meera Sharma (spouse)</p>
<p class="small">This schedule must be read with the Policy Wording. Issued at Bengaluru on 10 Mar 2026.</p>
"""

REJECTION_LETTER = """
<p><b>Navjeevan General Insurance Company Limited</b><br>Claims Department, Bengaluru</p>
<p>Date: 03 Oct 2026</p>
<p>To<br>Mr. Rohit Sharma<br>14 Sample Lane, Indiranagar, Bengaluru 560038</p>
<p><b>Subject: Repudiation of claim CLM-26-08817</b><br>
Policy number: NGI/HL/2026/448812<br>
Patient: Rohit Sharma<br>
Hospital: Sample Multispeciality Hospital, Bengaluru<br>
Date of admission: 14 Sep 2026<br>
Claimed amount: Rs. 1,80,000</p>
<p>Dear Sir,</p>
<p>We have reviewed your claim for left total knee replacement surgery. We regret to inform you that the
claim is not payable.</p>
<p>Reason: The treatment falls within the 24-month waiting period for joint replacement surgery under
Clause 4.2 of the policy wording. The current policy commenced on 12 Mar 2026 and the date of admission
is within 24 months of the policy start date.</p>
<p>If you are not satisfied with this decision, you may write to our Grievance Officer within 30 days.</p>
<p>Yours faithfully,<br>Claims Manager</p>
"""

MOTOR_WORDING = """
<h1>DriveSure Comprehensive</h1>
<p><b>Kavach Motor Insurance Limited</b><br>Private Car Package Policy - Policy Wording</p>

<h2>1. Section I - Own damage</h2>
<p>The Company will pay for loss of or damage to the insured vehicle and its accessories caused by fire,
explosion, theft, riot, flood, cyclone, earthquake, landslide, accidental external means, or while in
transit by road, rail or water.</p>
<h3>1.1 Depreciation</h3>
<p>Claims for parts replaced are paid after deducting depreciation: 50% on rubber, nylon and plastic
parts, tyres and batteries; 30% on fibreglass parts; and depreciation on metal parts according to the
age of the vehicle. This deduction does not apply if the Zero Depreciation add-on is shown in the
schedule.</p>

<h2>2. Section II - Liability to third parties</h2>
<p>The Company will pay amounts the insured is legally liable to pay for death of or bodily injury to any
person, and for damage to third-party property up to Rs. 7,50,000, arising out of the use of the
insured vehicle.</p>

<h2>3. Exclusions (Section I)</h2>
<ol>
<li>Consequential loss, wear and tear, and mechanical or electrical breakdown.</li>
<li>Damage to the engine caused by water entering it (hydrostatic lock), or by continuing to drive or
attempting to start a vehicle that has been in water, unless the Engine Protect add-on is shown in the
schedule.</li>
<li>Damage while the vehicle is driven by a person without a valid driving licence.</li>
<li>Damage while driving under the influence of alcohol or drugs.</li>
<li>Damage to tyres unless the vehicle is damaged at the same time.</li>
</ol>

<h2>4. Add-ons (only if shown in the schedule)</h2>
<h3>4.1 Zero Depreciation</h3>
<p>Claims for replaced parts are paid without deduction for depreciation, for up to two claims per
Policy Period.</p>
<h3>4.2 Engine Protect</h3>
<p>Covers damage to the engine and gearbox from water ingression, oil leakage or hydrostatic lock.</p>

<h2>5. Claims</h2>
<p>Inform the Company immediately after an accident or loss, and within 7 days at the latest. Do not
attempt to start a vehicle that has been in floodwater. For theft, a police report is required.</p>
"""


def _write_story(html: str, header: str) -> bytes:
    story = pymupdf.Story(html=html, user_css=CSS)
    buf = io.BytesIO()
    writer = pymupdf.DocumentWriter(buf)
    body = A4 + (56, 64, -56, -60)
    more = True
    while more:
        dev = writer.begin_page(A4)
        more, _ = story.place(body)
        story.draw(dev)
        writer.end_page()
    writer.close()

    # Running header and footer, like real policy documents
    doc = pymupdf.open(stream=buf.getvalue(), filetype="pdf")
    for page in doc:
        page.insert_text((56, 38), header, fontsize=8, color=(0.35, 0.35, 0.35))
        footer = f"{SAMPLE_NOTE}    Page {page.number + 1} of {doc.page_count}"
        page.insert_text((56, A4.height - 30), footer, fontsize=7.5, color=(0.45, 0.45, 0.45))
    return doc.tobytes(garbage=3, deflate=True)


def _scan(pdf: bytes, dpi: int = 150, max_pages: int | None = None) -> bytes:
    """Turn a PDF into a 'scanned' one: grey JPEG images, slightly tilted, no text layer."""
    rnd = random.Random(7)
    src = pymupdf.open(stream=pdf, filetype="pdf")
    out = pymupdf.open()
    for i, page in enumerate(src):
        if max_pages and i >= max_pages:
            break
        pix = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY)
        img = Image.frombytes("L", (pix.w, pix.h), pix.samples)
        img = img.rotate(rnd.uniform(-0.6, 0.6), fillcolor=255, resample=Image.BICUBIC)
        jpg = io.BytesIO()
        img.save(jpg, "JPEG", quality=70)
        new = out.new_page(width=page.rect.width, height=page.rect.height)
        new.insert_image(new.rect, stream=jpg.getvalue())
    return out.tobytes(garbage=3, deflate=True)


def _photo(pdf: bytes) -> bytes:
    """A phone photo of a one-page letter: warm paper tint, slight angle and blur, JPEG."""
    page = pymupdf.open(stream=pdf, filetype="pdf")[0]
    pix = page.get_pixmap(dpi=170)
    img = Image.frombytes("RGB", (pix.w, pix.h), pix.samples)
    tint = Image.new("RGB", img.size, (246, 240, 226))
    img = Image.blend(img, tint, 0.18)
    img = img.rotate(1.4, expand=True, fillcolor=(120, 110, 100), resample=Image.BICUBIC)
    img = img.filter(ImageFilter.GaussianBlur(0.6))
    out = io.BytesIO()
    img.save(out, "JPEG", quality=82)
    return out.getvalue()


def main() -> None:
    OUT.mkdir(exist_ok=True)
    wording = _write_story(HEALTH_WORDING, "Suraksha Health Plus - Policy Wording - UIN NGIHLIP26001V012526")
    files = {
        "suraksha-health-plus-policy-wording.pdf": wording,
        "suraksha-health-plus-policy-schedule.pdf": _write_story(HEALTH_SCHEDULE, "Navjeevan General Insurance - Policy Schedule"),
        "suraksha-health-plus-policy-wording-scanned.pdf": _scan(wording),
        "rejection-letter-CLM-26-08817-photo.jpg": _photo(_write_story(REJECTION_LETTER, "Navjeevan General Insurance - Claims")),
        "drivesure-comprehensive-policy-wording.pdf": _write_story(MOTOR_WORDING, "DriveSure Comprehensive - Policy Wording"),
    }
    for name, data in files.items():
        (OUT / name).write_bytes(data)
        print(f"{name:52s} {len(data) / 1024:8.0f} KB")


if __name__ == "__main__":
    main()
