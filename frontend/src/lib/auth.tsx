import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { Navigate, useLocation } from "react-router";
import { useI18n } from "../i18n/I18nProvider";
import type { Lang } from "../i18n/strings";
import { api, ApiError, tokenStore, type TokenResponse, type User } from "./api";

export const isLocalhost =
  typeof window !== "undefined" &&
  (window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1" ||
    window.location.hostname === "::1" ||
    window.location.hostname.endsWith(".localhost"));

export const DEV_LOGGED_OUT_KEY = "claimsaathi-dev-logged-out";

type AuthState = {
  user: User | null;
  ready: boolean; // finished checking a saved token
  login: (email: string, password: string) => Promise<void>;
  signup: (full_name: string, email: string, password: string, preferred_language: Lang) => Promise<void>;
  logout: () => void;
  devBypass: () => Promise<void>;
  isLocalhost: boolean;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const { lang, setLang } = useI18n();
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);

  const applySession = useCallback(
    (r: TokenResponse) => {
      tokenStore.set(r.access_token);
      lastSynced.current = r.user.preferred_language;
      setLang(r.user.preferred_language);
      setUser(r.user);
    },
    [setLang],
  );

  const devBypass = useCallback(async () => {
    try {
      sessionStorage.removeItem(DEV_LOGGED_OUT_KEY);
    } catch {}
    try {
      const r = await api.devBypass();
      applySession(r);
    } catch (e) {
      // Backend unreachable: let the error reach the page ("Can't reach the server") instead of
      // pretending to be signed in, which would only make every page fail afterwards.
      if (e instanceof ApiError && e.status === 0) throw e;
      console.warn("API dev-bypass failed, falling back to demo login:", e);
      applySession(await api.login({ email: "rohit.demo@example.com", password: "demo-pass-2026" }));
    }
  }, [applySession]);

  // Restore the session from a saved token.
  useEffect(() => {
    const savedToken = tokenStore.get();
    if (!savedToken) {
      setReady(true);
      return;
    }
    api
      .me()
      .then(setUser)
      .catch((e) => {
        if (e instanceof ApiError && e.status === 401) {
          tokenStore.set(null);
        }
      })
      .finally(() => setReady(true));
  }, []);

  // Remember the language choice on the account.
  const lastSynced = useRef<Lang | null>(null);
  useEffect(() => {
    if (!user || user.preferred_language === lang || lastSynced.current === lang) return;
    lastSynced.current = lang;
    api.updateMe({ preferred_language: lang }).then(setUser).catch(() => {});
  }, [lang, user]);

  const login = useCallback(
    async (email: string, password: string) => {
      try {
        sessionStorage.removeItem(DEV_LOGGED_OUT_KEY);
      } catch {}
      applySession(await api.login({ email, password }));
    },
    [applySession],
  );

  const signup = useCallback(
    async (full_name: string, email: string, password: string, preferred_language: Lang) => {
      try {
        sessionStorage.removeItem(DEV_LOGGED_OUT_KEY);
      } catch {}
      applySession(await api.signup({ full_name, email, password, preferred_language }));
    },
    [applySession],
  );

  const logout = useCallback(() => {
    try {
      sessionStorage.setItem(DEV_LOGGED_OUT_KEY, "true");
    } catch {}
    tokenStore.set(null);
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, ready, login, signup, logout, devBypass, isLocalhost }),
    [user, ready, login, signup, logout, devBypass],
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}

/** Sends signed-out visitors to /login and brings them back afterwards. */
export function RequireAuth({ children }: { children: ReactNode }) {
  const { user, ready } = useAuth();
  const location = useLocation();
  if (!ready) return <div className="muted py-16 text-center" aria-busy="true" />;
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  return <>{children}</>;
}
