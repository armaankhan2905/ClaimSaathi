# Sample documents

**Everything here is fictional**: the insurers, people, policy numbers and clauses are made up for testing and demonstrating ClaimSaathi. Regenerate the files with `python scripts/make_sample_docs.py` from the `backend` folder.

| File | What it is | Tests |
|---|---|---|
| `suraksha-health-plus-policy-wording.pdf` | 4-page health policy wording (digital PDF) | Text layer, header/footer removal |
| `suraksha-health-plus-policy-wording-scanned.pdf` | The same wording as a slightly tilted grey scan | OCR |
| `suraksha-health-plus-policy-schedule.pdf` | Policy schedule: sum insured, limits, First Policy Date, renewal history | Tables |
| `rejection-letter-CLM-26-08817-photo.jpg` | Phone photo of a claim rejection letter | OCR on photos |
| `drivesure-comprehensive-policy-wording.pdf` | Motor policy wording with the engine-protect exclusion | Motor policies |

**The demo case:** Rohit's knee replacement claim (₹1,80,000, admitted 14 Sep 2026) is rejected under clause 4.2. The insurer counted the 24-month waiting period from the current policy's start (12 Mar 2026), but clause 4.2 counts it from the First Policy Date (12 Mar 2022). The schedule shows continuous renewals since then.
