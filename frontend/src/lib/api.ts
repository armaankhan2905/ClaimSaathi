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

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const headers: Record<string, string> = {};
  const token = tokenStore.get();
  if (token) headers.Authorization = `Bearer ${token}`;
  if (body !== undefined) headers["Content-Type"] = "application/json";

  let res: Response;
  try {
    res = await fetch(`/api${path}`, { method, headers, body: body === undefined ? undefined : JSON.stringify(body) });
  } catch {
    throw new ApiError(0, "network");
  }
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
};
