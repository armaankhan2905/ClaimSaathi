import type { Lang } from "../i18n/strings";

const TOKEN_KEY = "claimsaathi-token";

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
  try {
    return await fetch(`/api${path}`, { method, headers, body: payload });
  } catch {
    throw new ApiError(0, "network");
  }
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

export const api = {
  signup: (b: { full_name: string; email: string; password: string; preferred_language: Lang }) =>
    request<TokenResponse>("POST", "/auth/signup", b),
  login: (b: { email: string; password: string }) => request<TokenResponse>("POST", "/auth/login", b),
  me: () => request<User>("GET", "/auth/me"),
  updateMe: (b: Partial<Pick<User, "full_name" | "preferred_language">>) => request<User>("PATCH", "/auth/me", b),
  listPolicies: () => request<Policy[]>("GET", "/policies"),
  deletePolicy: (id: number) => request<void>("DELETE", `/policies/${id}`),

  uploadDocument: (file: File, kind: DocumentKind, policyId?: number | null) => {
    const form = new FormData();
    form.append("file", file);
    form.append("kind", kind);
    if (policyId != null) form.append("policy_id", String(policyId));
    return request<DocumentInfo>("POST", "/documents", form);
  },
  listDocuments: (policyId?: number | null) =>
    request<DocumentInfo[]>("GET", policyId != null ? `/documents?policy_id=${policyId}` : "/documents"),
  getDocument: (id: number) => request<DocumentInfo>("GET", `/documents/${id}`),
  updateDocument: (id: number, b: { kind: DocumentKind }) => request<DocumentInfo>("PATCH", `/documents/${id}`, b),
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
  created_at: string;
};

export type DocumentPage = {
  page_number: number;
  text: string;
  method: "text" | "ocr";
  ocr_confidence: number | null;
};
