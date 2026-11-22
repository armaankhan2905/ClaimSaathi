import type { Lang } from "../i18n/strings";

const TOKEN_KEY = "claimsaathi-token";

// Where the API lives. Empty = the same site (local dev proxy, or the one-container deploy).
// A separately hosted website (e.g. Vercel) sets VITE_API_URL to the backend's address at build time.
const API_BASE = ((import.meta.env.VITE_API_URL as string | undefined) ?? "").replace(/\/+$/, "");

export type User = { id: number; email: string; full_name: string; preferred_language: Lang };

export type Policy = {
  id: number;
  category: "health" | "motor" | "life" | "travel" | "other";
  name: string;
  insurer: string;
  policy_number: string | null;
  status: "active" | "lapsed" | "processing";
  sum_insured: number | null;
  cover_since: string | null; // ISO date
  renews_on: string | null; // ISO date
  highlights: { addons?: string[]; warnings?: string[] };
  auto_created: boolean;
  analysis_status: "none" | "running" | "ready" | "failed";
  analysis_mode: "ai" | "basic" | null;
  analyzed_at: string | null;
  clause_count: number;
};

export type WaitingStatus = {
  name: string;
  clause_ref: string | null;
  months: number;
  counted_from: "first_policy_date" | "policy_start" | "unclear";
  starts: string | null;
  ends: string | null;
  completed: boolean | null;
  days_left: number | null;
  note: "break_in_cover" | "basis_unclear" | "missing_dates" | null;
};

export type PolicyDetail = Policy & {
  terms: Record<string, unknown> | null;
  timeline: {
    continuous_since: string | null;
    breaks: { previous_end: string; next_start: string; gap_days: number }[];
    periods_checked: number;
    waiting_periods: WaitingStatus[];
  } | null;
};

export type Clause = {
  id: number;
  ref: string;
  title: string;
  section_title: string;
  text: string;
  category: "coverage" | "exclusion" | "limit" | "waiting_period" | "definition" | "condition" | "claim_process" | "grievance" | "other";
  plain: { en: string; hi: string; hn: string } | null;
  page_start: number;
  page_end: number;
  document_id: number | null;
};

export type Verdict = "covered" | "partly_covered" | "not_covered" | "unclear";

export type PolicyVerdict = {
  policy_id: number;
  verdict: Verdict;
  summary: string;
  what_you_pay: string;
  citations: { ref: string; title: string; quote: string }[];
  mode: "ai" | "basic";
  reason: { code: "waiting_not_over" | "waiting_over" | "excluded" | "limited" | "mentioned" | "not_mentioned"; months?: number } | null;
};

export type CompareResult = {
  scenario: { key: string | null; text: string; month: number | null };
  a: PolicyVerdict;
  b: PolicyVerdict;
  winner: "a" | "b" | "tie";
};

export type FeatureRow = { key: string; a: number | string | null; b: number | string | null; better: "a" | "b" | null };

export type FindingRow = {
  type: string;
  insurer_reason: string;
  clause_ref: string | null;
  policy_quote: { ref: string; title: string; quote: string } | null;
  status: "contradicted" | "supported" | "unclear";
  code: string | null;
  data: {
    months?: number;
    policy_start_for_waiting?: string | null;
    waiting_ends?: string | null;
    admission_date?: string | null;
    insurer_counted_from?: string | null;
    continuous_since?: string | null;
    periods_checked?: number;
    breaks?: unknown[];
  };
  explanation_en: string;
  explanation_local: string;
  question_en: string;
  question_local: string;
  evidence: string[];
};

export type Claim = {
  id: number;
  policy_id: number | null;
  status: "draft" | "checking" | "ready" | "failed";
  error: string | null;
  lang: string;
  mode: "ai" | "basic" | null;
  facts: {
    claim_number?: string | null;
    policy_number?: string | null;
    patient?: string | null;
    hospital?: string | null;
    treatment?: string | null;
    admission_date?: string | null;
    letter_date?: string | null;
    claimed_amount?: number | null;
  } | null;
  findings: {
    assessment: "inconsistency" | "consistent" | "needs_info";
    rows: FindingRow[];
    timeline: { date: string; kind: string; months?: number; clause_ref?: string; until?: string; days?: number }[];
    checklist: { item: string; have: boolean; important: boolean }[];
    questions: { en: string; local: string }[];
  } | null;
  created_at: string;
  checked_at: string | null;
};

export type Stage = "insurer" | "bima_bharosa" | "ombudsman";
export type Situation = "not_yet" | "unsatisfied" | "no_reply" | "bb_unresolved";
export type Ground = { text: string; ref: string | null };

export type ComplaintFields = {
  name: string;
  phone: string;
  email: string;
  address: string;
  insurer: string;
  to_email: string;
  policy_number: string;
  claim_number: string;
  amount: number | null;
  patient: string;
  hospital: string;
  treatment: string;
  admission_date: string | null;
  letter_date: string | null;
  grievance_type: "claim_rejected" | "claim_partly_paid" | "claim_delay" | "policy_service" | "other";
  ask: string;
  grounds: Ground[];
  attachments: number[];
  include_report: boolean;
  situation: Situation;
  earlier_complaint_date: string | null;
  earlier_reference: string;
  insurer_reply_date: string | null;
};

export type ComplaintLetter = {
  to: string;
  date: string;
  subject: string;
  paragraphs: string[];
  grounds_intro: string;
  grounds: Ground[];
  ask_label: string;
  ask: string;
  closing_note: string;
  sign_off: string;
  contact: string[];
  attachments: string[];
};

export type Complaint = {
  id: number;
  claim_id: number | null;
  stage: Stage;
  status: "draft" | "sent" | "resolved";
  fields: ComplaintFields;
  history: { kind: "created" | "sent" | "reply" | "escalated" | "resolved"; stage: Stage; date: string; reference?: string; outcome?: string; to?: Stage }[];
  recommended_stage: Stage;
  tracker: {
    sent_on: string | null;
    reference: string;
    reply_due: string | null;
    days_left: number | null;
    replied: "resolved" | "unsatisfied" | null;
    replied_on: string | null;
    can_escalate: ("bima_bharosa" | "ombudsman")[];
    escalate_after: string | null;
    ombudsman_from: string | null;
    ombudsman_by: string | null;
  };
  letter: ComplaintLetter;
  letter_text: string;
  attachment_options: { id: number; filename: string; kind: DocumentKind }[];
  has_report: boolean;
  created_at: string;
  updated_at: string;
};

export type ChatMessage = {
  id: number;
  role: "user" | "assistant";
  content: string;
  lang: string;
  answer_type: "answered" | "not_in_policy" | "needs_more_info" | "search_only" | null;
  citations: { ref: string; title: string; quote: string; clause_id: number }[];
  follow_ups: string[];
  mode: "ai" | "basic" | null;
  created_at: string;
};

export type TokenResponse = { access_token: string; token_type: string; user: User };

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

export const tokenStore = {
  get(): string | null {
    try {
      return localStorage.getItem(TOKEN_KEY);
    } catch {
      return null;
    }
  },
  set(token: string | null) {
    try {
      if (token) localStorage.setItem(TOKEN_KEY, token);
      else localStorage.removeItem(TOKEN_KEY);
    } catch {
      /* storage unavailable */
    }
  },
};

async function send(method: string, path: string, body?: unknown): Promise<Response> {
  const headers: Record<string, string> = {};
  const token = tokenStore.get();
  if (token) headers.Authorization = `Bearer ${token}`;
  let payload: BodyInit | undefined;
  if (body instanceof FormData) {
    payload = body; // the browser sets the multipart Content-Type with its boundary
  } else if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }
  let res: Response;
  try {
    res = await fetch(`${API_BASE}/api${path}`, { method, headers, body: payload });
  } catch {
    throw new ApiError(0, "network");
  }
  // The dev server (or a hosting proxy) answers 502/503/504 when the backend isn't running.
  if (res.status === 502 || res.status === 503 || res.status === 504) throw new ApiError(0, "network");
  return res;
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const res = await send(method, path, body);
  if (res.status === 204) return undefined as T;
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const detail = data?.detail;
    const message = typeof detail === "string" ? detail : Array.isArray(detail) ? detail[0]?.msg : res.statusText;
    throw new ApiError(res.status, message || "error");
  }
  return data as T;
}

/** Fetches a file with the login token and hands it to the browser to save. */
async function downloadFile(path: string, fallbackName: string) {
  const res = await send("GET", path);
  if (!res.ok) throw new ApiError(res.status, "download_failed");
  const name = /filename="([^"]+)"/.exec(res.headers.get("content-disposition") ?? "")?.[1] ?? fallbackName;
  const url = URL.createObjectURL(await res.blob());
  const a = Object.assign(document.createElement("a"), { href: url, download: name });
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 30_000);
}

export const api = {
  signup: (b: { full_name: string; email: string; password: string; preferred_language: Lang }) =>
    request<TokenResponse>("POST", "/auth/signup", b),
  login: (b: { email: string; password: string }) => request<TokenResponse>("POST", "/auth/login", b),
  devBypass: () => request<TokenResponse>("POST", "/auth/dev-bypass"),
  me: () => request<User>("GET", "/auth/me"),
  updateMe: (b: Partial<Pick<User, "full_name" | "preferred_language">>) => request<User>("PATCH", "/auth/me", b),
  listPolicies: () => request<Policy[]>("GET", "/policies"),
  getPolicy: (id: number) => request<PolicyDetail>("GET", `/policies/${id}`),
  analyzePolicy: (id: number) => request<Policy>("POST", `/policies/${id}/analyze`),
  listClauses: (id: number) => request<Clause[]>("GET", `/policies/${id}/clauses`),
  searchClauses: (id: number, q: string, k = 5) =>
    request<{ clause: Clause; score: number }[]>("GET", `/policies/${id}/search?q=${encodeURIComponent(q)}&k=${k}`),
  deletePolicy: (id: number) => request<void>("DELETE", `/policies/${id}`),
  compareTable: (a: number, b: number) => request<FeatureRow[]>("GET", `/compare/table?a=${a}&b=${b}`),
  compareScenario: (b: { a: number; b: number; scenario?: string; custom?: string; lang: Lang }) => request<CompareResult>("POST", "/compare", b),
  getChat: (id: number) => request<ChatMessage[]>("GET", `/policies/${id}/chat`),
  ask: (id: number, question: string, lang: Lang) => request<ChatMessage[]>("POST", `/policies/${id}/chat`, { question, lang }),
  clearChat: (id: number) => request<void>("DELETE", `/policies/${id}/chat`),

  uploadDocument: (file: File, kind: DocumentKind, policyId?: number | null, claimId?: number | null) => {
    const form = new FormData();
    form.append("file", file);
    form.append("kind", kind);
    if (policyId != null) form.append("policy_id", String(policyId));
    if (claimId != null) form.append("claim_id", String(claimId));
    return request<DocumentInfo>("POST", "/documents", form);
  },
  listDocuments: (policyId?: number | null, claimId?: number | null) => {
    const q = new URLSearchParams();
    if (policyId != null) q.set("policy_id", String(policyId));
    if (claimId != null) q.set("claim_id", String(claimId));
    return request<DocumentInfo[]>("GET", `/documents${q.size ? `?${q}` : ""}`);
  },
  getDocument: (id: number) => request<DocumentInfo>("GET", `/documents/${id}`),
  updateDocument: (id: number, b: { kind?: DocumentKind; claim_id?: number | null }) => request<DocumentInfo>("PATCH", `/documents/${id}`, b),
  listClaims: () => request<Claim[]>("GET", "/claims"),
  createClaim: (b: { policy_id?: number | null; lang: Lang }) => request<Claim>("POST", "/claims", b),
  getClaim: (id: number) => request<Claim>("GET", `/claims/${id}`),
  updateClaim: (id: number, b: { policy_id: number | null }) => request<Claim>("PATCH", `/claims/${id}`, b),
  checkClaim: (id: number, lang: Lang) => request<Claim>("POST", `/claims/${id}/check`, { lang }),
  deleteClaim: (id: number) => request<void>("DELETE", `/claims/${id}`),
  /** Downloads the evidence report PDF (fetched with the login token, then saved by the browser). */
  downloadReport: (id: number, fallbackName: string) => downloadFile(`/claims/${id}/report`, fallbackName),
  listComplaints: () => request<Complaint[]>("GET", "/complaints"),
  createComplaint: (b: { claim_id?: number | null; situation: Situation }) => request<Complaint>("POST", "/complaints", b),
  getComplaint: (id: number) => request<Complaint>("GET", `/complaints/${id}`),
  updateComplaint: (id: number, b: { fields?: Partial<ComplaintFields>; stage?: Stage }) => request<Complaint>("PATCH", `/complaints/${id}`, b),
  markSent: (id: number, b: { sent_on?: string; reference?: string }) => request<Complaint>("POST", `/complaints/${id}/sent`, b),
  recordReply: (id: number, b: { outcome: "resolved" | "unsatisfied"; reply_on?: string }) => request<Complaint>("POST", `/complaints/${id}/reply`, b),
  escalate: (id: number, to: "bima_bharosa" | "ombudsman") => request<Complaint>("POST", `/complaints/${id}/escalate`, { to }),
  deleteComplaint: (id: number) => request<void>("DELETE", `/complaints/${id}`),
  downloadComplaint: (id: number, what: "letter" | "package" | "reminder", fallbackName: string) => downloadFile(`/complaints/${id}/${what}`, fallbackName),
  getPages: (id: number) => request<DocumentPage[]>("GET", `/documents/${id}/pages`),
  deleteDocument: (id: number) => request<void>("DELETE", `/documents/${id}`),
  /** Opens the original file in a new tab (fetched with the login token, so it can't be a plain link). */
  openDocumentFile: async (id: number) => {
    const tab = window.open("", "_blank"); // open now, while we still have the click, so pop-up blockers allow it
    const res = await send("GET", `/documents/${id}/file`);
    if (!res.ok) {
      tab?.close();
      throw new ApiError(res.status, "download_failed");
    }
    const url = URL.createObjectURL(await res.blob());
    if (tab) tab.location.href = url;
    else window.location.href = url;
    setTimeout(() => URL.revokeObjectURL(url), 60_000);
  },
};

export const POLICY_DOCUMENT_KINDS = ["policy_wording", "policy_schedule", "endorsement", "previous_policy"] as const;
export const CLAIM_DOCUMENT_KINDS = [
  "rejection_letter",
  "renewal_receipt",
  "discharge_summary",
  "hospital_bill",
  "doctor_note",
  "other",
] as const;
export type DocumentKind = (typeof POLICY_DOCUMENT_KINDS)[number] | (typeof CLAIM_DOCUMENT_KINDS)[number];

export type DocumentInfo = {
  id: number;
  policy_id: number | null;
  kind: DocumentKind;
  filename: string;
  content_type: string;
  size_bytes: number;
  status: "processing" | "ready" | "failed";
  error: string | null;
  page_count: number | null;
  ocr_pages: number;
  suggested_kind: DocumentKind | null;
  claim_id: number | null;
  created_at: string;
};

export type DocumentPage = {
  page_number: number;
  text: string;
  method: "text" | "ocr";
  ocr_confidence: number | null;
};
