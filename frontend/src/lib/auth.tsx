import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { Navigate, useLocation } from "react-router";
import { useI18n } from "../i18n/I18nProvider";
import type { Lang } from "../i18n/strings";
import { api, ApiError, tokenStore, type TokenResponse, type User } from "./api";

type AuthState = {
  user: User | null;
  ready: boolean; // finished checking a saved token
  login: (email: string, password: string) => Promise<void>;
  signup: (full_name: string, email: string, password: string, preferred_language: Lang) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const { lang, setLang } = useI18n();
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(() => tokenStore.get() === null);

  // Restore the session from a saved token.
  useEffect(() => {
    if (!tokenStore.get()) return;
    api
      .me()
      .then(setUser)
      .catch((e) => {
        if (e instanceof ApiError && e.status === 401) tokenStore.set(null);
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

  const applySession = useCallback(
    (r: TokenResponse) => {
      tokenStore.set(r.access_token);
      lastSynced.current = r.user.preferred_language;
      setLang(r.user.preferred_language);
      setUser(r.user);
    },
    [setLang],
  );

  const login = useCallback(async (email: string, password: string) => applySession(await api.login({ email, password })), [applySession]);

  const signup = useCallback(
    async (full_name: string, email: string, password: string, preferred_language: Lang) =>
      applySession(await api.signup({ full_name, email, password, preferred_language })),
    [applySession],
  );

  const logout = useCallback(() => {
    tokenStore.set(null);
    setUser(null);
  }, []);

  const value = useMemo(() => ({ user, ready, login, signup, logout }), [user, ready, login, signup, logout]);
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
