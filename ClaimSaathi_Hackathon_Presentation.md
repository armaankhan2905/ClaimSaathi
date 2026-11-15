# ClaimSaathi – Hackathon Presentation Content

**Project:** ClaimSaathi  
**Tagline:** Understand Your Coverage. Defend Your Rights.  
**Description:** AI-Powered Insurance Policy Intelligence & Policyholder Protection Platform  
**Track:** Human Empowerment & Assistive Innovation

> **Template note:** This draft uses a proposed 11-slide structure. The linked Google Slides template could not be inspected, so the headings and slide count have not been matched to the organiser's exact requirements.

---

## Slide 1 – Project Title

### ClaimSaathi – Your AI Insurance Rights Companion

**Subtitle:** Making Insurance Transparent, Understandable and Accountable

ClaimSaathi is an AI-powered platform that helps Indian policyholders decode complicated insurance policies, compare coverage options, verify rejected claims against policy conditions and prepare evidence-backed complaints through official grievance channels.

**Include on slide:** Team name, member details, institution and hackathon logo, according to the organiser's requirements.

---

## Slide 2 – Problem Statement

### The Insurance Protection Gap

Insurance is purchased for financial security, yet many policyholders struggle to understand what their coverage actually provides.

**Four major problems:**

1. **Complex policies:** Lengthy legal language, exclusions and conditional benefits make policies difficult to understand.
2. **Unexpected coverage gaps:** Customers may discover restrictions only when an accident, illness or emergency occurs.
3. **Claim rejection uncertainty:** Policyholders often lack the knowledge to assess whether an insurer's rejection explanation is contractually supported.
4. **Difficult grievance resolution:** Identifying relevant clauses, gathering evidence and navigating complaint procedures can be overwhelming.

**Example:** A vehicle owner assumes comprehensive motor insurance covers flood-related engine damage, but later discovers that consequential engine damage may require additional protection.

> The problem isn't only claim rejection. It's the information imbalance between insurers and policyholders.

---

## Slide 3 – Proposed Solution

### Introducing ClaimSaathi

ClaimSaathi creates a policyholder-first intelligence layer between complex insurance contracts and everyday users.

**Four pillars:**

- **Decode:** Understand policy clauses.
- **Compare:** Evaluate coverage options.
- **Verify:** Examine claim rejections.
- **Act:** Prepare supported complaints.

**Solution highlights:**

- Converts complex policy documents into simple, understandable explanations.
- Enables natural-language questions about real-life insurance scenarios.
- Compares two policies with clause-backed conclusions.
- Evaluates rejection reasons against policy wording, timelines and submitted evidence.
- Generates a structured grievance draft and guides users toward official resolution mechanisms.

**Value proposition:** One platform supporting policyholders before purchase, during coverage and after a disputed claim.

---

## Slide 4 – Key Features

### An End-to-End AI Policyholder Assistant

| Feature | Function | User benefit |
|---|---|---|
| Policy Decoder | Extracts coverage, exclusions, limits and waiting periods | Understand complex insurance documents |
| Ask ClaimSaathi | Answers scenario-based policy questions with citations | Get clear answers before emergencies |
| ClaimSaathi Compare | Compares two uploaded policies | Identify relevant coverage differences |
| Rejection Analyzer | Cross-checks rejection grounds against policy evidence | Discover potentially questionable decisions |
| Evidence Report | Documents findings, contradictions and missing information | Understand whether a dispute merits review |
| Grievance Assistant | Drafts complaints and provides official filing guidance | Take informed action |
| Multilingual Support | Explains results in Hindi, English or Hinglish | Improve accessibility |

**Presentation emphasis:** Visually highlight the **Rejection Analyzer** and **Evidence Report**, central to the project's differentiation.

---

## Slide 5 – How ClaimSaathi Works

### From Complex Documents to Actionable Guidance

1. **Document Upload:** Insurance policy, schedules, endorsements and rejection letters.
2. **Document Intelligence:** PDF extraction, OCR and clause classification.
3. **Policy Knowledge Base:** Structured policy conditions and searchable document sections.
4. **AI Reasoning + Verification:** RAG retrieval, contractual comparison and rule-based checks.
5. **User-Facing Results:** Simple explanations, comparisons and evidence-backed reports.
6. **Grievance Assistance:** Complaint drafting, document checklist and official escalation guidance.

**Key technical principle:** ClaimSaathi retrieves relevant passages from the user's actual policy and cites them rather than relying entirely on an AI model's general insurance knowledge.

---

## Slide 6 – Technology Stack & Architecture

### Technology Behind ClaimSaathi

| Layer | Technology | Role |
|---|---|---|
| Frontend | React, Tailwind CSS | Responsive, accessible UI |
| Backend | Python, FastAPI | API orchestration and document workflows |
| Document extraction | PyMuPDF, OCR | Read digital and scanned documents |
| AI intelligence | LLM with RAG | Policy understanding and evidence-based reasoning |
| Vector search | pgvector | Retrieve relevant policy clauses |
| Database | PostgreSQL | Secure case metadata and structured terms |
| Verification logic | Python rules engine | Calculate waiting periods, dates and financial conditions |
| Report generation | PDF/document generator | Export assessments and complaints |

**Important distinction:** The LLM interprets complex language, while the rules engine performs structured checks. Neither substitutes for professional adjudication of a disputed insurance claim.

---

## Slide 7 – Innovation & Differentiation

### Beyond a Generic Insurance Chatbot

Existing tools already offer AI-based policy summaries and some claim appeal assistance. ClaimSaathi's proposed differentiation is a transparent, evidence-centred verification workflow.

**Innovation 1 – Clause-to-Claim Evidence Mapping**

Each insurer rejection reason is linked to the exact policy clause and relevant user documents. The system marks supporting evidence, apparent contradictions and unresolved questions.

**Innovation 2 – Policy Timeline Intelligence**

The platform reconstructs key dates: policy commencement, renewals, waiting-period expiry, incident and rejection. This helps identify potential discrepancies involving coverage continuity.

**Innovation 3 – Scenario-Based Policy Comparison**

Instead of simply comparing policy brochures, ClaimSaathi evaluates situations such as waterlogged engine damage, maternity expenses or specific medical procedures against both policies.

**Innovation 4 – Actionable Grievance Package**

The final output includes the disputed grounds, clause references, missing-evidence checklist and a human-reviewable complaint draft.

> ClaimSaathi doesn't just tell users what an insurance document says. It helps them understand what those terms mean for their specific situation and what evidence supports their next step.

---

## Slide 8 – Real-World Use Case

### When Insurance Protection Becomes a Dispute

**Illustrative fictional health insurance case**

A policyholder undergoes hospital treatment costing **₹1,80,000**. The insurer rejects the claim, citing a two-year waiting-period restriction. The policyholder believes they have maintained continuous coverage for three years.

**How ClaimSaathi responds:**

1. Extracts the rejection reason and applicable waiting-period clause.
2. Reviews policy start dates, renewal records and possible waiting-period exceptions.
3. Identifies an apparent inconsistency requiring further verification.
4. Generates a report citing the original policy and uploaded evidence.
5. Prepares a grievance draft requesting a review of the rejection.

**Expected benefit:** The policyholder gains a clear explanation, supporting evidence and an actionable route for seeking clarification or reconsideration.

*This example uses fictional facts and does not establish that a particular medical claim must be approved.*

---

## Slide 9 – Feasibility & Implementation Plan

### Building ClaimSaathi as a Practical, Scalable Solution

**Phase 1 – Document Intelligence**

Implement secure PDF upload, clause extraction, structured summaries and policy-specific AI questions.

**Phase 2 – Comparative Intelligence**

Build two-policy comparison, aligned coverage tables and scenario-based evaluation.

**Phase 3 – Claim Verification**

Analyse rejection letters, reconstruct policy timelines, validate structured conditions and prepare evidence-backed reports.

**Phase 4 – Grievance Assistance**

Generate complaint documents and guide users to appropriate official grievance channels.

**Phase 5 – Validation & Accessibility**

Test accuracy against annotated documents, assess evidence completeness, add multilingual explanations and implement privacy safeguards. Privacy safeguards should be designed in from Phase 1.

**Hackathon MVP scope:** A working demonstration using representative motor and health insurance policy documents, with synthetic or redacted claim cases.

**Expected deliverables:** Functional web application, policy chatbot, two-policy comparison, claim rejection report and downloadable complaint draft.

*These are proposed deliverables, not claims about features already implemented.*

---

## Slide 10 – Expected Impact & Beneficiaries

### Empowering India's Insurance Policyholders

**Primary beneficiaries:** Individual health, motor and life insurance policyholders, particularly people who struggle with complicated insurance terminology or grievance procedures.

**Expected social benefits:**

- Better understanding of contractual coverage and exclusions.
- More informed policy purchase decisions.
- Reduced confusion around claim rejection reasons.
- Greater access to structured, evidence-backed grievance assistance.
- Improved accessibility through simple-language and multilingual explanations.

**Measurable goals for pilot evaluation:**

| Metric | Proposed evaluation |
|---|---|
| Clause retrieval accuracy | Compare retrieved clauses against manually annotated references |
| Policy comparison correctness | Review scenario-specific results against source documents |
| Rejection assessment reliability | Test against expert-labelled fictional cases |
| Citation validity | Check whether cited passages support each conclusion |
| User understanding | Measure comprehension before and after using ClaimSaathi |
| Complaint completeness | Check generated drafts against a predefined document and information checklist |

Do not present these as achieved results until the MVP has been tested.

**Long-term vision:** Make trustworthy, understandable insurance guidance more accessible to policyholders across India.

---

## Slide 11 – Future Scope & Conclusion

### The Future of Policyholder Empowerment

After validating the hackathon MVP, ClaimSaathi could expand into:

- Support for additional insurance categories and regional languages.
- Speech-based explanations for users with limited literacy.
- Policy renewal and coverage-change alerts.
- Automated checks for missing claim documentation.
- Consent-based connections with insurers or authorised grievance services.
- Human expert review for complicated disputes.
- Anonymised insights into recurring policyholder confusion, subject to privacy protections.

**Conclusion:**

Insurance should provide confidence, not confusion. ClaimSaathi aims to empower people throughout the insurance journey—from understanding and comparing policies to verifying rejected claims and pursuing fair resolution.

**ClaimSaathi — Understand Your Coverage. Defend Your Rights.**

AI for Insurance Transparency & Policyholder Empowerment.

---

## Sources and Verification

Use official or primary sources wherever possible:

1. **Insurance Regulatory and Development Authority of India (IRDAI):** https://irdai.gov.in/ — Regulations, consumer protection and policyholder guidance.
2. **Bima Bharosa:** https://bimabharosa.irdai.gov.in/ — Insurance grievance registration and tracking.
3. **Council for Insurance Ombudsmen:** https://www.cioins.co.in/ — Insurance dispute redressal processes.
4. **India Code:** https://www.indiacode.nic.in/ — Applicable Indian legislation and regulations.

For any problem-size slide, use statistics with a specific source and reporting year. Distinguish total grievances from rejected claims. Do not claim that every rejection is unfair, or that AI can conclusively determine legal entitlement.
