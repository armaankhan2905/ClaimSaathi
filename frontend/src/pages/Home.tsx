import { motion } from "motion/react";
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router";
import { Icon, type IconName } from "../components/Icon";
import { PolicyCard } from "../components/PolicyCard";
import { useI18n } from "../i18n/I18nProvider";
import type { StringKey } from "../i18n/strings";
import { api, type Policy } from "../lib/api";
import { useAuth } from "../lib/auth";

const FEATURES: { to: string; icon: IconName; eyebrow: StringKey; title: StringKey; items: StringKey[] }[] = [
  {
    to: "/policy",
    icon: "doc",
    eyebrow: "policy_eyebrow",
    title: "nav_policy",
    items: ["feat_policy_1", "feat_policy_2", "feat_policy_3", "feat_policy_4"],
  },
  { to: "/rejection", icon: "search", eyebrow: "rej_eyebrow", title: "nav_rej", items: ["feat_rej_1", "feat_rej_2", "feat_rej_3", "feat_rej_4"] },
  { to: "/complaint", icon: "flag", eyebrow: "comp_eyebrow", title: "nav_comp", items: ["feat_comp_1", "feat_comp_2", "feat_comp_3", "feat_comp_4"] },
];

function HeroShield() {
  return (
    <motion.svg
      viewBox="0 0 270 330"
      aria-hidden="true"
      className="w-[150px] drop-shadow-[0_18px_20px_rgba(16,38,74,.3)] md:w-[190px]"
      animate={{ y: [0, -10, 0] }}
      transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
    >
      <defs>
        <linearGradient id="hs-a" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#5b97e6" />
          <stop offset="1" stopColor="#164a9a" />
        </linearGradient>
        <linearGradient id="hs-b" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#d6e5f9" />
          <stop offset="1" stopColor="#7ea7dd" />
        </linearGradient>
      </defs>
      <path d="M135 8 250 52v108c0 80-52 135-115 162C72 295 20 240 20 160V52z" fill="url(#hs-b)" />
      <path d="M135 26 234 62v98c0 70-45 118-99 142C81 278 36 230 36 160V62z" fill="url(#hs-a)" />
      <path d="M135 26 234 62v98c0 70-45 118-99 142z" fill="#000" opacity=".14" />
      <path d="M88 168l34 36 62-76" fill="none" stroke="#fff" strokeWidth="22" strokeLinecap="round" strokeLinejoin="round" />
    </motion.svg>
  );
}

function PolicySkeleton() {
  return (
    <div className="panel grid animate-pulse gap-3" aria-hidden="true">
      <div className="h-3 w-16 rounded bg-surface-2" />
      <div className="h-5 w-48 rounded bg-surface-2" />
      <div className="grid grid-cols-3 gap-2.5">
        <div className="h-14 rounded-[10px] bg-surface-2" />
        <div className="h-14 rounded-[10px] bg-surface-2" />
        <div className="h-14 rounded-[10px] bg-surface-2" />
      </div>
    </div>
  );
}

function usePolicies() {
  const [policies, setPolicies] = useState<Policy[] | null>(null);
  const [failed, setFailed] = useState(false);
  const load = useCallback(() => {
    setFailed(false);
    setPolicies(null);
    api.listPolicies().then(setPolicies).catch(() => setFailed(true));
  }, []);
  useEffect(load, [load]);
  return { policies, failed, reload: load };
}

export function Home() {
  const { t } = useI18n();
  const { user } = useAuth();
  const { policies, failed, reload } = usePolicies();
  const firstName = user?.full_name.split(/\s+/)[0];

  return (
    <section aria-labelledby="h-home">
      {/* Hero */}
      <div className="relative grid items-center gap-6 overflow-hidden rounded-[28px] border border-line bg-[linear-gradient(165deg,var(--hero-from)_0%,var(--hero-mid)_60%,var(--hero-to)_100%)] px-5 py-7 md:grid-cols-[1.4fr_1fr] md:px-10 md:py-11">
        <div className="relative">
          <span className="eyebrow">
            {firstName ? `${t("greeting")}, ${firstName}` : t("hero_eyebrow")}
          </span>
          <h1 id="h-home" className="mt-2.5">
            {t("hero_title_1")}
            <br />
            <span className="text-accent">{t("hero_title_2")}</span>
          </h1>
          <p className="muted mt-3.5 max-w-[54ch] text-[16.5px]">{t("hero_sub")}</p>
          <div className="mt-[22px] flex flex-wrap gap-2.5">
            <Link to="/policy" className="btn primary">
              <Icon name="upload" />
              {t("cta_upload")}
            </Link>
            <Link to="/rejection" className="btn">
              <Icon name="search" />
              {t("cta_check")}
            </Link>
          </div>
        </div>
        <div className="relative hidden justify-center md:flex">
          <div className="absolute top-1/2 left-1/2 h-[220px] w-[220px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-[radial-gradient(circle_at_40%_35%,color-mix(in_srgb,var(--accent)_25%,transparent),transparent_70%)]" />
          <HeroShield />
        </div>
      </div>

      {/* Features */}
      <div className="mt-6 grid gap-4 md:grid-cols-3">
        {FEATURES.map((f) => (
          <motion.div key={f.to} whileHover={{ y: -4 }} transition={{ duration: 0.2 }}>
            <Link
              to={f.to}
              className="flex h-full flex-col gap-3 rounded-2xl border border-line bg-surface p-[22px] text-fg no-underline shadow-[var(--shadow)] transition-colors hover:border-sage"
            >
              <span className="grid h-11 w-11 place-items-center rounded-xl bg-[var(--accent-soft)] text-accent">
                <Icon name={f.icon} className="h-[22px] w-[22px]" />
              </span>
              <div>
                <span className="eyebrow">{t(f.eyebrow)}</span>
                <h2 className="mt-1.5">{t(f.title)}</h2>
              </div>
              <ul className="m-0 grid gap-1 pl-[18px] text-sm text-muted">
                {f.items.map((k) => (
                  <li key={k}>{t(k)}</li>
                ))}
              </ul>
              <span className="mt-auto text-sm font-semibold text-accent">
                {t("open_section")} {t(f.title)} →
              </span>
            </Link>
          </motion.div>
        ))}
      </div>

      {/* Saved policies */}
      <div className="mt-[34px] mb-3.5 flex flex-wrap items-baseline justify-between gap-3">
        <h2>{t("your_policies")}</h2>
      </div>
      {failed ? (
        <div className="panel flex flex-wrap items-center gap-3">
          <Icon name="alert" className="h-5 w-5 text-bad" />
          <p className="flex-1">{t("load_error")}</p>
          <button type="button" className="btn" onClick={reload}>
            {t("retry")}
          </button>
        </div>
      ) : policies === null ? (
        <div className="grid gap-4 md:grid-cols-2">
          <PolicySkeleton />
          <PolicySkeleton />
        </div>
      ) : policies.length === 0 ? (
        <div className="panel grid justify-items-center gap-2 py-10 text-center">
          <span className="grid h-14 w-14 place-items-center rounded-2xl bg-[var(--accent-soft)] text-accent">
            <Icon name="doc" className="h-7 w-7" />
          </span>
          <h3 className="mt-1 text-lg">{t("no_policies_title")}</h3>
          <p className="muted max-w-[44ch] text-sm">{t("no_policies_text")}</p>
          <Link to="/policy" className="btn primary mt-2">
            <Icon name="upload" />
            {t("cta_upload")}
          </Link>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {policies.map((p, i) => (
            <PolicyCard key={p.id} policy={p} index={i} />
          ))}
        </div>
      )}

      <p className="disclaimer">{t("disclaimer")}</p>
    </section>
  );
}
