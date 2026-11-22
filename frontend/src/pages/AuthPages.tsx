import { motion } from "motion/react";
import { useState, type FormEvent, type ReactNode } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router";
import { Icon } from "../components/Icon";
import { usePageTitle } from "../components/PageHead";
import { useI18n } from "../i18n/I18nProvider";
import { LANG_OPTIONS, type Lang, type StringKey } from "../i18n/strings";
import { ApiError } from "../lib/api";
import { useAuth } from "../lib/auth";

function AuthCard({ title, sub, children }: { title: string; sub: string; children: ReactNode }) {
  usePageTitle(title);
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: "easeOut" }}
      className="panel mx-auto mt-4 w-full max-w-[440px] p-6 sm:p-8"
    >
      <span className="mb-4 grid h-11 w-11 place-items-center rounded-xl bg-accent text-accent-ink">
        <Icon name="shield" className="h-[22px] w-[22px]" />
      </span>
      <h1 className="text-[28px]">{title}</h1>
      <p className="muted mt-1.5 text-sm">{sub}</p>
      {children}
    </motion.div>
  );
}

// Server messages are English only, so known failures are mapped to translated text.
function useSubmit(statusMessages: Partial<Record<number, StringKey>>) {
  const { t } = useI18n();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run(fn: () => Promise<void>) {
    setBusy(true);
    setError(null);
    try {
      await fn();
    } catch (e) {
      const key = e instanceof ApiError ? (e.status === 0 ? "err_network" : statusMessages[e.status]) : undefined;
      setError(t(key ?? "err_generic"));
    } finally {
      setBusy(false);
    }
  }
  return { busy, error, run };
}

function ErrorNote({ message }: { message: string | null }) {
  if (!message) return null;
  return (
    <p role="alert" className="flex items-start gap-2 rounded-[10px] bg-[var(--bad-bg)] px-3 py-2.5 text-[13.5px] text-bad">
      <Icon name="alert" className="mt-0.5 h-4 w-4 flex-none" />
      {message}
    </p>
  );
}

function useRedirectTarget() {
  const location = useLocation();
  return (location.state as { from?: string } | null)?.from ?? "/";
}

export function LoginPage() {
  const { t } = useI18n();
  const { user, login, devBypass, isLocalhost } = useAuth();
  const navigate = useNavigate();
  const target = useRedirectTarget();
  const { busy, error, run } = useSubmit({ 401: "err_wrong_login", 422: "err_invalid", 429: "err_too_many" });
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  if (user) return <Navigate to={target} replace />;

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run(async () => {
      await login(email, password);
      navigate(target, { replace: true });
    });
  }

  return (
    <AuthCard title={t("login_title")} sub={t("login_sub")}>
      {isLocalhost && (
        <div className="mt-4 rounded-xl border border-accent/25 bg-accent/5 p-3.5 text-xs">
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-1.5 font-semibold text-accent">
              <Icon name="shield" className="h-4 w-4" />
              Localhost Dev Bypass
            </span>
            <span className="rounded bg-accent/20 px-1.5 py-0.5 text-[10.5px] font-semibold text-accent">DEV</span>
          </div>
          <p className="muted mt-1 text-[12px] leading-relaxed">
            Running locally on localhost. Bypass login and sign in immediately as demo user.
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            <button
              type="button"
              className="btn primary flex-1 py-1.5 text-xs font-semibold"
              disabled={busy}
              onClick={() => {
                run(async () => {
                  await devBypass();
                  navigate(target, { replace: true });
                });
              }}
            >
              ⚡ Bypass Login (Demo Rohit)
            </button>
            <button
              type="button"
              className="btn py-1.5 px-2.5 text-xs"
              disabled={busy}
              onClick={() => {
                setEmail("rohit.demo@example.com");
                setPassword("demo-pass-2026");
              }}
            >
              Fill Credentials
            </button>
          </div>
        </div>
      )}
      <form onSubmit={onSubmit} className="mt-5 grid gap-4">
        <label className="field">
          {t("email")}
          <input className="input" type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <label className="field">
          {t("password")}
          <input
            className="input"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>
        <ErrorNote message={error} />
        <button type="submit" className="btn primary w-full" disabled={busy}>
          {busy ? t("working") : t("sign_in")}
        </button>
      </form>
      <p className="muted mt-5 text-center text-sm">
        {t("no_account")}{" "}
        <Link to="/signup" state={{ from: target }} className="font-semibold">
          {t("sign_up")}
        </Link>
      </p>
    </AuthCard>
  );
}

export function SignupPage() {
  const { t, lang } = useI18n();
  const { user, signup } = useAuth();
  const navigate = useNavigate();
  const target = useRedirectTarget();
  const { busy, error, run } = useSubmit({ 409: "err_email_taken", 422: "err_invalid" });
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [preferred, setPreferred] = useState<Lang>(lang);

  if (user) return <Navigate to={target} replace />;

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run(async () => {
      await signup(fullName, email, password, preferred);
      navigate(target, { replace: true });
    });
  }

  return (
    <AuthCard title={t("signup_title")} sub={t("signup_sub")}>
      <form onSubmit={onSubmit} className="mt-6 grid gap-4">
        <label className="field">
          {t("full_name")}
          <input className="input" autoComplete="name" required maxLength={120} value={fullName} onChange={(e) => setFullName(e.target.value)} />
        </label>
        <label className="field">
          {t("email")}
          <input className="input" type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <label className="field">
          {t("password")}
          <input
            className="input"
            type="password"
            autoComplete="new-password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <span className="text-[12px] font-normal">{t("password_hint")}</span>
        </label>
        <fieldset className="field m-0 border-0 p-0">
          <legend className="mb-1.5">{t("preferred_language")}</legend>
          <div className="seg w-fit">
            {LANG_OPTIONS.map((o) => (
              <button key={o.code} type="button" aria-pressed={preferred === o.code} onClick={() => setPreferred(o.code)}>
                {o.label}
              </button>
            ))}
          </div>
        </fieldset>
        <ErrorNote message={error} />
        <button type="submit" className="btn primary w-full" disabled={busy}>
          {busy ? t("working") : t("sign_up")}
        </button>
      </form>
      <p className="muted mt-5 text-center text-sm">
        {t("have_account")}{" "}
        <Link to="/login" state={{ from: target }} className="font-semibold">
          {t("sign_in")}
        </Link>
      </p>
    </AuthCard>
  );
}
