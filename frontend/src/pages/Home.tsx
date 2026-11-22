import { motion } from "motion/react";
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router";
import { StampMark } from "../components/AppBar";
import { Icon, type IconName } from "../components/Icon";
import { usePageTitle } from "../components/PageHead";
import { PolicyCard } from "../components/PolicyCard";
import { RecentCases } from "../components/RecentCases";
import { useI18n } from "../i18n/I18nProvider";
import type { StringKey } from "../i18n/strings";
import { api, type Policy, type User } from "../lib/api";
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

/** The example case as a dossier: the insurer's letter clipped over the clause that answers it,
 *  stamped "not supported". The letter and clause are quoted documents, so they stay in English. */
function Dossier() {
  const { t } = useI18n();
  return (
    <figure className="relative m-0 min-h-[440px] min-w-0">
      {/* folder behind the sheet, with its tab */}
      <div aria-hidden="true" className="absolute inset-[18px_0_0_24px] rotate-[3deg] bg-folder shadow-[0_2px_0_rgba(0,0,0,.12)]" />
      <div aria-hidden="true" className="absolute top-0 left-[44px] h-7 w-[140px] rotate-[3deg] bg-folder" />
      <motion.article
        initial={{ opacity: 0, y: 18, rotate: -1.5 }}
        animate={{ opacity: 1, y: 0, rotate: 0 }}
        transition={{ duration: 0.5, ease: [0.2, 0.8, 0.2, 1] }}
        className="relative mt-8 mr-2 border border-line bg-paper px-6 pt-7 pb-14 font-mono text-paper-ink shadow-[0_14px_30px_rgba(60,45,20,.18)] sm:px-8"
      >
        {/* paper clip */}
        <svg aria-hidden="true" viewBox="0 0 34 74" className="absolute -top-5 right-12 h-[74px] w-[34px]">
          <path d="M10 70V14a7 7 0 0 1 14 0v46a4 4 0 0 1-8 0V20" fill="none" stroke="#7d7f86" strokeWidth="3" strokeLinecap="round" />
        </svg>
        <p className="text-[13px] text-paper-muted uppercase">{t("cf_letter_label")} · 03 Oct 2026</p>
        <p lang="en" className="mt-2 text-[16px] font-bold">Re: Claim CLM-26-08817 — Repudiation</p>
        <p lang="en" className="mt-3 text-[14.5px] leading-relaxed">
          Your claim of ₹1,80,000 for left total knee replacement is not payable, as the treatment falls within the{" "}
          <span className="bg-[var(--bad-bg)] px-0.5">24-month waiting period under Clause 4.2</span>, counted from 12 Mar 2026.
        </p>
        <hr className="my-5 border-0 border-t-[1.5px] border-dashed border-line" />
        <p className="text-[13px] text-paper-muted uppercase">{t("cf_clause_label")}</p>
        <p lang="en" className="mt-2 text-[14.5px] leading-relaxed">
          “The 24 months are counted from the <b className="bg-[var(--accent-soft)] px-0.5">First Policy Date</b> and not from the start of the current Policy Period.”
        </p>
        <p className="mt-3 text-[13.5px] leading-snug text-accent">{t("cf_dates")}</p>
        <motion.div
          initial={{ opacity: 0, scale: 1.6, rotate: -4 }}
          animate={{ opacity: 1, scale: 1, rotate: -11 }}
          transition={{ duration: 0.35, delay: 0.55, ease: [0.3, 1.4, 0.5, 1] }}
          className="stamp absolute right-3 -bottom-7 bg-paper text-[24px] sm:right-6"
          role="img"
          aria-label={`${t("cf_stamp_1")} ${t("cf_stamp_2")}`}
        >
          {t("cf_stamp_1")}
          <span className="mt-1 block text-[13px] tracking-[.12em]">{t("cf_stamp_2")}</span>
        </motion.div>
      </motion.article>
    </figure>
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

function usePolicies(user: User | null) {
  const [policies, setPolicies] = useState<Policy[] | null>(null);
  const [failed, setFailed] = useState(false);
  const load = useCallback(() => {
    if (!user) {
      setPolicies(null);
      setFailed(false);
      return;
    }
    setFailed(false);
    setPolicies(null);
    api.listPolicies().then(setPolicies).catch(() => setFailed(true));
  }, [user]);
  useEffect(load, [load]);

  // Refresh quietly while a policy is still being read, so its card fills in by itself.
  const reading = policies?.some((p) => p.status === "processing" || p.analysis_status === "running") ?? false;
  useEffect(() => {
    if (!reading || !user) return;
    const id = setInterval(() => api.listPolicies().then(setPolicies).catch(() => {}), 2000);
    return () => clearInterval(id);
  }, [reading, user]);

  return { policies, failed, reload: load };
}

export function Home() {
  const { t } = useI18n();
  const { user } = useAuth();
  const { policies, failed, reload } = usePolicies(user);
  usePageTitle();

  return (
    <section aria-labelledby="h-home">
      {/* Hero */}
      <div className="grid items-center gap-12 pt-1 pb-12 md:grid-cols-[1.1fr_1fr] md:gap-14">
        <div className="min-w-0">
          <p className="font-mono text-[14px] tracking-[.06em] text-muted uppercase">
            {t("cf_file_no")} CLM-26-08817 · {t("cf_example")}
          </p>
          <h1 id="h-home" className="mt-4 text-[clamp(46px,7.2vw,94px)] leading-[0.9]">
            {t("cf_hero_1")}
            <br />
            <span className="text-stamp">{t("cf_hero_2")}</span>
          </h1>
          <p className="mt-7 max-w-[54ch] text-[18px] leading-relaxed text-fg/85">{t("hero_sub")}</p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link to="/policy" className="btn primary px-6 py-3.5 text-[16px]">
              <Icon name="upload" />
              {t("cta_upload")}
            </Link>
            <Link to="/rejection" className="btn px-6 py-3.5 text-[16px]">
              <Icon name="search" />
              {t("cta_check")}
            </Link>
          </div>
        </div>
        <Dossier />
      </div>

      {/* The three tools, as exhibits in the file */}
      <div className="-mx-4 border-y-2 border-rule bg-surface-2 px-4 py-12 md:-mx-8 md:px-8">
        <h2 className="text-[clamp(28px,3.6vw,42px)] font-black uppercase [font-stretch:80%]">{t("cf_exhibits_title")}</h2>
        <div className="mt-8 grid gap-6 md:grid-cols-3">
          {FEATURES.map((f, i) => (
            <motion.div key={f.to} whileHover={{ y: -3, rotate: i === 1 ? 0.4 : -0.4 }} transition={{ duration: 0.2 }}>
              <Link
                to={f.to}
                className="flex h-full flex-col border-[1.5px] border-rule bg-surface p-6 text-fg no-underline shadow-[var(--shadow)] hover:text-fg"
              >
                <span className="eyebrow">
                  {t("cf_exhibit")} {"ABC"[i]} · {t(f.eyebrow)}
                </span>
                <h3 className="mt-2.5 text-[26px] font-extrabold">{t(f.title)}</h3>
                <ul className="m-0 mt-4 grid list-none gap-2 p-0 font-mono text-[14.5px] leading-snug">
                  {f.items.map((k) => (
                    <li key={k} className="flex gap-2">
                      <span aria-hidden="true" className="flex-none font-bold text-stamp">[x]</span>
                      {t(k)}
                    </li>
                  ))}
                </ul>
                <span className="mt-auto pt-5 font-bold text-accent">
                  {t("open_section")} {t(f.title)} →
                </span>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Where a complaint goes, as a docket */}
      <div className="pt-12">
        <p className="eyebrow text-muted">{t("cf_route_title")}</p>
        <ol className="m-0 mt-4 flex list-none flex-wrap items-center gap-3 p-0">
          {(["stage_insurer", "stage_bima_bharosa", "stage_ombudsman"] as const).map((k, i) => (
            <li key={k} className="flex items-center gap-3">
              <span
                className={`border-[3px] px-4 py-2.5 font-display text-[19px] font-extrabold uppercase [font-stretch:85%] ${
                  i === 2 ? "border-stamp text-stamp" : "border-rule"
                }`}
              >
                {i + 1} · {t(k)}
              </span>
              {i < 2 && (
                <span aria-hidden="true" className="text-[24px] font-black">
                  →
                </span>
              )}
            </li>
          ))}
        </ol>
      </div>

      {!user ? (
        <div className="panel mt-12 flex flex-col items-start justify-between gap-4 py-7 sm:flex-row sm:items-center">
          <div className="flex items-center gap-3.5">
            <span className="grid h-12 w-12 flex-none place-items-center text-stamp">
              <StampMark className="h-12 w-12" />
            </span>
            <div>
              <h3 className="text-base font-semibold">{t("guest_cta_title")}</h3>
              <p className="muted text-sm">{t("guest_cta_sub")}</p>
            </div>
          </div>
          <div className="flex w-full flex-wrap gap-2 sm:w-auto">
            <Link to="/login" className="btn primary flex-1 sm:flex-none">
              <Icon name="user" />
              {t("sign_in")}
            </Link>
            <Link to="/signup" className="btn flex-1 sm:flex-none">
              {t("sign_up")}
            </Link>
          </div>
        </div>
      ) : (
        <>
          {/* Saved policies */}
          <div className="mt-12 mb-5 flex flex-wrap items-baseline justify-between gap-3 border-t-[1.5px] border-dashed border-line pt-6">
            <h2 className="text-[clamp(26px,3vw,34px)] font-black uppercase [font-stretch:80%]">{t("your_policies")}</h2>
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

          <RecentCases />
        </>
      )}

      <p className="disclaimer">{t("disclaimer")}</p>
    </section>
  );
}
