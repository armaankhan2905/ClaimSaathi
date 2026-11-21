# ClaimSaathi

**Understand your coverage. Defend your rights.**

ClaimSaathi is an AI-powered insurance companion for Indian policyholders. You upload your insurance policy, and ClaimSaathi explains it in simple words, compares it with other plans, checks a rejected claim against your own policy clauses and helps you file a complaint that holds up.

Built by **OverCooked Brains** for The Builder's Theory 1.0 (Finance & FinTech track).

> **Status:** the full app is being built in `frontend/` and `backend/`. Accounts, saved policies, languages and dark mode work so far; the AI features are in progress. The original clickable demo is in `demo/`. All policies, insurers, people and claims in the sample data are fictional.

---

## The idea

People buy insurance for security, but most can't tell what their policy actually covers until a claim is refused. Policies are long, written in legal language, and full of exclusions, limits and waiting periods that are easy to miss.

When a claim is rejected, the policyholder usually has no easy way to check whether the insurer's reason is supported by the policy itself. Finding the right clause, collecting evidence and working through the complaint process is slow and confusing. The result is an information gap between insurers and policyholders.

For example, a car owner may assume a "comprehensive" motor policy covers flood damage to the engine, only to learn after the incident that this needed a separate add-on.

ClaimSaathi closes that gap. It works with the user's **own** policy documents, so every answer points to the exact clause it relies on, not to general insurance knowledge.

## What the website does

ClaimSaathi supports the policyholder at every stage: before buying, while covered, and after a disputed claim. It has four parts:

| | What it does |
|---|---|
| **Decode** | Turns a policy PDF into a plain summary of what is covered, what is not, the limits and the waiting periods. |
| **Compare** | Tests two policies against real situations (such as knee surgery in year 3 or a private hospital room) and shows which one pays. |
| **Verify** | Checks an insurer's rejection reason against the policy wording, the user's coverage dates and their documents. |
| **Act** | Drafts a complaint, lists the documents to attach and shows where to file it next. |

Everything can be read in **English, Hindi or Hinglish**.

## How it works: a walk through the website

### Home

The home page introduces ClaimSaathi and shows the user's saved policies (in the demo, a health policy and a motor policy). From here the user can upload a policy or check a rejected claim.

### Policy Insights

1. **Upload policy.** The user uploads the policy wording, and optionally the schedule, endorsements and older policies. Scanned copies and phone photos are accepted.
2. **Reading policy.** ClaimSaathi extracts the text (using OCR for scanned pages), finds and labels every clause, reads the schedule and works out the waiting periods from the date of the first policy.
3. **Your insights.** The results are shown in four tabs:
   - **Details:** sum insured, policy period, room-rent limit, co-payment and premium, plus lists of what is covered, not covered, limited, and the waiting periods with their end dates.
   - **Clauses:** every clause shown next to a plain-language explanation of what it means, with search and filters for coverage, exclusions, limits and waiting periods.
   - **Compare:** a side-by-side test of two policies against a chosen situation, followed by a feature-by-feature table.
   - **Ask ClaimSaathi:** a chat where the user asks questions about their own policy in English, Hindi or Hinglish. Each answer quotes the clause it is based on.

### Rejection Check

1. **Upload documents.** The user uploads the insurer's rejection letter and adds supporting documents: renewal receipts, discharge summary, hospital bills and doctor's notes. The policy is already linked from Policy Insights.
2. **Checking rejection.** ClaimSaathi reads the rejection reason, finds the clause the insurer cited, rebuilds the coverage timeline from the renewal receipts, compares the dates and checks the evidence.
3. **Findings.** The user sees:
   - an overall assessment (for example, "Possible inconsistency found") with a short explanation,
   - a **coverage timeline** from the first policy to the rejection date,
   - an **evidence map** that lists each of the insurer's grounds, what the policy actually says, the user's evidence and a status (contradicted, no break, or ask the insurer),
   - an evidence checklist and the questions to raise with the insurer,
   - a downloadable evidence report.

### File a Complaint

1. **Choose where to file.** Based on where the user is in the process, ClaimSaathi recommends the next step: the insurer's grievance officer first, then IRDAI's Bima Bharosa portal, then the Insurance Ombudsman.
2. **Review draft.** The complaint is pre-filled from the Rejection Check: the grounds for review, the clause references and the attached documents. The user can edit every field and sees a live preview of the letter.
3. **Track complaint.** After sending, the user gets a reference number, a tracker with the reply deadline, reminders by SMS, WhatsApp or email, and an option to escalate to Bima Bharosa if the insurer does not resolve it.

## Example case

*A fictional case used throughout the demo.*

Rohit's claim of ₹1,80,000 for a knee replacement is rejected. The insurer says the surgery falls within the 24-month waiting period for joint replacement.

ClaimSaathi finds that the insurer counted the waiting period from the **latest renewal (2025)**, but the policy's own clause counts it from the **first policy (2022)**. Rohit's renewal receipts show continuous cover with no break, so the waiting period had ended 18 months before the surgery.

ClaimSaathi flags this as a possible inconsistency, builds an evidence report and drafts a complaint asking the insurer to review the decision.

This does not prove the claim must be paid. It gives Rohit a clear explanation, the evidence that supports him and a concrete next step.

## What makes it different

- **Clause-to-claim evidence mapping.** Each rejection reason is linked to the exact clause and the user's documents, showing what supports the user, what contradicts the insurer and what is still unclear.
- **Policy timeline.** Rebuilds the start date, renewals, waiting-period end dates, the incident and the rejection, so gaps in coverage (or the lack of them) are easy to see.
- **Comparison by situation.** Compares policies on real situations instead of brochure features.
- **A complete complaint package.** Grounds, clause references, a missing-documents checklist and a draft the user reviews before sending.
- **Answers you can check.** Every answer cites the user's own policy, and the user always decides what to send.

## Planned technology

The demo in this repository is a front-end preview. The full product is planned on this stack:

| Layer | Technology | Role |
|---|---|---|
| Frontend | React, Tailwind CSS | Responsive, accessible interface |
| Backend | Python, FastAPI | APIs and document workflows |
| Document reading | PyMuPDF, OCR | Reads digital and scanned documents |
| AI | LLM with retrieval (RAG) | Understands policy language and answers with citations |
| Clause search | pgvector | Finds the clauses relevant to a question |
| Database | PostgreSQL | Case data and structured policy terms |
| Verification | Python rules engine | Checks dates, waiting periods and amounts |
| Reports | PDF generator | Evidence reports and complaint letters |

The AI explains complex wording, while a rules engine does the exact date and amount checks. ClaimSaathi gives guidance based on the user's documents; it does not decide legal entitlement or replace professional advice.

## Running the app locally

You need Python 3.12+ and Node.js 20+.

**Backend** (FastAPI, runs on port 8000):

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate        # Windows; on macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then set your own JWT_SECRET
python -m app.seed            # creates the fictional demo account and sample policies
uvicorn app.main:app --reload --port 8000
```

Run the tests with `pytest` from the `backend` folder.

**Frontend** (React, runs on port 5173):

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 and sign in with the demo account from `backend/.env.example`, or create your own. The frontend forwards `/api` requests to the backend.

| Folder | What's in it |
|---|---|
| `backend/app/` | API (`main.py`, `routers/`), database models, auth, seed data |
| `backend/tests/` | API tests |
| `frontend/src/` | React app: pages, components, translations (`i18n/strings.ts`) |
| `demo/` | The original single-file clickable demo |

## Running the demo

The demo is a single HTML file with no build step or dependencies.

1. Open `demo/claimsaathi-demo.html` in any modern browser.
2. Use the top menu to move between **Home**, **Policy Insights**, **Rejection Check** and **File a Complaint**.
3. On each page, click **Play walkthrough** to see the upload, processing and results steps in order.
4. Switch languages with **EN / हिं / Hinglish**, and between light and dark mode with the theme button.

Buttons that would need a real backend (such as file upload or sending a complaint) show a short "not connected yet" message.

## Roadmap

1. **Now: build and validate.** A working MVP with the policy decoder, Ask ClaimSaathi, two-policy comparison, rejection report and complaint draft, tested on sample health and motor policies with fictional cases.
2. **Next: pilot.** Test with a small group of policyholders and measure clause-retrieval accuracy, citation validity, how well users understand their policy, and how complete the complaints are.
3. **Then: improve and scale.** More regional languages, voice explanations, renewal alerts, more insurance types and human expert review for complex disputes.

Privacy is built in from the start: documents are encrypted, never shared with the insurer, and can be deleted at any time.

## Team

**OverCooked Brains**

- Armaan Khan (team leader)
- Pranav Pushya
- Nandita
- Govind
- Ryan Sharma

## Useful links

- [IRDAI](https://irdai.gov.in/): India's insurance regulator, with rules and policyholder guidance.
- [Bima Bharosa](https://bimabharosa.irdai.gov.in/): IRDAI's portal for registering and tracking insurance complaints.
- [Council for Insurance Ombudsmen](https://www.cioins.co.in/): free resolution of insurance disputes.
