# ClaimSaathi

**Understand your coverage. Defend your rights.**

ClaimSaathi is an AI-powered insurance companion for Indian policyholders. You upload your insurance policy, and ClaimSaathi explains it in simple words, compares it with other plans, checks a rejected claim against your own policy clauses and helps you file a complaint that holds up.

Built by **OverCooked Brains** for The Builder's Theory 1.0 (Finance & FinTech track).

> **Status:** the full app works end to end in `frontend/` and `backend/`: accounts, document upload with OCR, Policy Insights (details, clauses, Compare, Ask ClaimSaathi), Rejection Check with an evidence report, and File a Complaint with tracking and escalation, in English, Hindi and Hinglish, light and dark. The original clickable demo is in `demo/`. All policies, insurers, people and claims in the sample data are fictional.

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
   - an **evidence map** that lists each of the insurer's grounds, what the policy actually says, the user's evidence and a status (not supported by your policy, supported, or ask the insurer),
   - an evidence checklist and the questions to raise with the insurer,
   - a downloadable evidence report.

### File a Complaint

1. **Choose where to file.** Based on where the user is in the process, ClaimSaathi recommends the next step: the insurer's grievance officer first, then IRDAI's Bima Bharosa portal, then the Insurance Ombudsman.
2. **Review draft.** The complaint is pre-filled from the Rejection Check: the grounds for review, the clause references and the attached documents. The user can edit every field and sees a live preview of the letter.
3. **Track complaint.** The user sends the letter themselves (email, post or the portal; ClaimSaathi never sends anything on their behalf) and records the date and reference. They get a tracker with the reply deadline, a calendar reminder, and an option to escalate to Bima Bharosa or the Ombudsman when the reply is late or doesn't resolve it.

## Example case

*A fictional case used throughout the demo.*

Rohit's claim of ₹1,80,000 for a knee replacement is rejected. The insurer says the surgery falls within the 24-month waiting period for joint replacement.

ClaimSaathi finds that the insurer counted the waiting period from the **latest renewal (March 2026)**, but the policy's own clause counts it from the **first policy (March 2022)**. Rohit's policy schedule shows continuous cover with no break, so the waiting period ended in March 2024, two and a half years before the surgery.

ClaimSaathi flags this as a possible inconsistency, builds an evidence report and drafts a complaint asking the insurer to review the decision.

This does not prove the claim must be paid. It gives Rohit a clear explanation, the evidence that supports him and a concrete next step.

## What makes it different

- **Clause-to-claim evidence mapping.** Each rejection reason is linked to the exact clause and the user's documents, showing what supports the user, what contradicts the insurer and what is still unclear.
- **Policy timeline.** Rebuilds the start date, renewals, waiting-period end dates, the incident and the rejection, so gaps in coverage (or the lack of them) are easy to see.
- **Comparison by situation.** Compares policies on real situations instead of brochure features.
- **A complete complaint package.** Grounds, clause references, a missing-documents checklist and a draft the user reviews before sending.
- **Answers you can check.** Every answer cites the user's own policy, and the user always decides what to send.

## Technology

| Layer | Technology | Role |
|---|---|---|
| Frontend | React 19, TypeScript, Tailwind CSS, Motion | Responsive, accessible interface in three languages, light and dark |
| Backend | Python, FastAPI, SQLAlchemy | APIs and document workflows |
| Database | SQLite (PostgreSQL also works) | Accounts, policies, clauses, checks and complaints |
| Document reading | PyMuPDF, RapidOCR | Reads digital PDFs, scanned copies and phone photos |
| AI | Groq (gpt-oss-120b, free plan) or Claude | Reads key terms, explains clauses, answers questions with citations, checks rejection reasons |
| Clause search | Local multilingual embeddings (fastembed) + keywords | Finds the clauses relevant to a question, in English, Hindi or Hinglish |
| Verification | Python rules engine | Exact dates: continuous cover, waiting-period end dates, what the insurer counted from |
| Reports | PyMuPDF | Evidence reports, complaint letters and complaint packages (PDF) |
| Security | Argon2 passwords, JWT, Fernet encryption | Uploaded files are encrypted at rest and only visible to their owner |

The AI explains complex wording, while the rules engine does the exact date checks, and every AI answer must quote a real clause. Without an AI key, everything still works in "basic mode" using rules. ClaimSaathi gives guidance based on the user's documents; it does not decide legal entitlement or replace professional advice.

## Running the app locally

You need Python 3.12+ and Node.js 20+.

**Quick start on Windows:** run these from the project folder. `setup.ps1` builds everything for your computer and is safe to re-run; `start.ps1` opens the backend and the website in two windows.

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

Sharing the project? Send the git repository, or a copy without `backend/.venv`, `frontend/node_modules` and `backend/.env`. A copied `.venv` points at the original computer's Python, so the backend won't start and sign-in shows "Can't reach the server". Running `setup.ps1` repairs a copied folder.

**Backend** (FastAPI, runs on port 8000):

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate        # Windows; on macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then set your own JWT_SECRET
python -m app.seed            # creates the fictional demo account and sample policies
                              # add --with-documents to also load and read the files in samples/
uvicorn app.main:app --reload --port 8000
```

Run the tests with `pytest` from the `backend` folder. To try uploads, use the fictional files in `samples/` (a digital policy, a scanned copy, a schedule and a photo of a rejection letter). Uploaded files are encrypted in `backend/storage/`.

**AI:** add `GROQ_API_KEY=...` (free plan at console.groq.com) or `ANTHROPIC_API_KEY=...` to `backend/.env` and restart the backend to get plain-language explanations of every clause (English, Hindi, Hinglish) and AI-checked key terms. With Groq's free plan (8K tokens a minute) reading a policy takes a few minutes in the background. Without a key the app runs in basic mode: clauses, key terms and waiting periods are read with rules. Use **Read again** on Policy Insights to re-read a policy after adding the key. Clause search uses a local model that downloads once (about 220 MB) on first use.

**Frontend** (React, runs on port 5173):

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 and sign in with the demo account from `backend/.env.example`, or create your own. The frontend forwards `/api` requests to the backend.

**One server instead of two:** run `npm run build` in `frontend/`, then start only the backend. It serves the built website too, at http://localhost:8000.

| Folder | What's in it |
|---|---|
| `backend/app/` | API (`main.py`, `routers/`), database models, auth, seed data |
| `backend/tests/` | API tests |
| `frontend/src/` | React app: pages, components, translations (`i18n/strings.ts`) |
| `backend/app/extraction/` | Reads PDFs, scans and photos into clean page text (PyMuPDF + RapidOCR) |
| `backend/app/understanding/` | Splits clauses, extracts key terms (Claude or rules), labels clauses, clause search |
| `backend/app/rules/` | Exact date checks: continuous cover and waiting-period end dates |
| `backend/app/understanding/claims.py` | Rejection Check: reads the letter and tests each reason |
| `backend/app/complaints.py` | File a Complaint: letters for each stage, deadlines, reminders |
| `backend/app/report.py`, `complaint_pdf.py` | Evidence report, complaint letter and complaint package PDFs |
| `samples/` | Fictional policy documents for testing |
| `demo/` | The original single-file clickable demo |

## Deploying

ClaimSaathi runs as **one container** that serves both the website and the API (see `Dockerfile`). It is not deployed yet; these are the steps for when you are ready.

1. **Settings.** Copy `backend/.env.production.example` to `backend/.env.production` (ignored by git and Docker), or paste the values into your host's environment-variable page:
   - `APP_ENV=production`
   - `JWT_SECRET` and `FILE_ENCRYPTION_KEY`, generated with the commands in the file. The server refuses to start in production without them. **Back up the encryption key**, because stored documents can't be read without it.
   - `GROQ_API_KEY` for AI (optional).
   - `SEED_DEMO=true` with your own `DEMO_PASSWORD`, if you want the fictional demo account on the hosted site.
2. **Build and run.**
   ```bash
   docker build -t claimsaathi .
   docker run -p 8000:8000 -v claimsaathi-data:/data --env-file backend/.env.production claimsaathi
   ```
3. **Storage.** The database, encrypted uploads and the search model live in `/data`, so give the container a **persistent volume** there (on Render, Railway or Fly.io this is a "disk" or "volume"). Without it, everything is lost on every restart.
4. **One instance.** Run a single instance: background reading, the AI rate limit and the sign-in limit are kept in memory.
5. **Demo data (optional).** To load and read the sample files into the demo account, run this once inside the container: `python -m app.seed --with-documents` (a few minutes with the Groq free plan).
6. **Check.** `/api/health` returns `{"status": "ok"}`; the container also has a built-in health check.

In production the API docs (`/docs`) are switched off, security headers and HSTS are sent, and repeated wrong sign-ins are slowed down. The Docker image hasn't been test-built yet (Docker isn't installed on the build machine), so build it once before the demo.

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
