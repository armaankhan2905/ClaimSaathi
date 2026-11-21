import { motion } from "motion/react";
import { useState } from "react";
import { Link } from "react-router";
import { useI18n } from "../../i18n/I18nProvider";
import type { StringKey } from "../../i18n/strings";
import { api, type Claim, type FindingRow } from "../../lib/api";
import { formatDate, formatRupees } from "../../lib/format";
import { Icon } from "../Icon";

const ASSESS: Record<string, { title: StringKey; text: StringKey; tone: string; icon: "alert" | "check" | "info" }> = {
  inconsistency: { title: "assess_inconsistency", text: "assess_inconsistency_text", tone: "warn", icon: "alert" },
  consistent: { title: "assess_consistent", text: "assess_consistent_text", tone: "neutral", icon: "check" },
  needs_info: { title: "assess_needs_info", text: "assess_needs_info_text", tone: "neutral", icon: "info" },
};

// Green when the insurer's reason is NOT supported (good news for the policyholder).
const STATUS: Record<FindingRow["status"], { key: StringKey; cls: string }> = {
  contradicted: { key: "st_contradicted", cls: "ok" },
  supported: { key: "st_supported", cls: "bad" },
  unclear: { key: "st_unclear", cls: "warn" },
};

const TL_DOT: Record<string, string> = {
  first_policy: "bg-accent",
  renewal: "bg-sage",
  waiting_ends: "bg-ok",
  insurer_start: "bg-warn",
  break: "bg-bad",
  admission: "bg-accent",
  rejection: "bg-bad",
};

function useExplain() {
  const { t, lang } = useI18n();
  return (row: FindingRow, claimLang: string) => {
    const d = row.data ?? {};
    const vars = {
      months: d.months ?? "",
      start: formatDate(d.policy_start_for_waiting, lang),
      ends: formatDate(d.waiting_ends, lang),
      admission: formatDate(d.admission_date, lang),
      insurer: formatDate(d.insurer_counted_from, lang),
    };
    const code = row.code ?? "";
    const known = ["waiting_over_counted_wrongly", "waiting_over", "waiting_not_over", "waiting_not_over_break", "waiting_basis_unclear", "waiting_unknown", "clause_not_found"];
    if (known.includes(code)) return t(`ex_${code}` as StringKey, vars);
    // AI-written explanation: in the language the check ran in, else English.
    if (row.explanation_local && claimLang === lang) return row.explanation_local;
    return row.explanation_en || t("ex_generic");
  };
}

function Fact({ label, value }: { label: string; value: string | null | undefined }) {
  return (
    <div className="min-w-0 rounded-xl border border-line bg-surface px-4 py-3">
      <dt className="text-[12px] text-muted">{label}</dt>
      <dd className="m-0 mt-1 truncate font-semibold" title={value ?? ""}>
        {value || "—"}
      </dd>
    </div>
  );
}

export function ClaimFindings({ claim, onDelete }: { claim: Claim; onDelete: () => void }) {
  const { t, lang } = useI18n();
  const explain = useExplain();
  const [copied, setCopied] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const f = claim.facts ?? {};
  const fd = claim.findings!;
  const a = ASSESS[fd.assessment] ?? ASSESS.needs_info!;
  const questions = fd.questions.map((q) => (q.local && claim.lang === lang ? q.local : q.en)).filter(Boolean);

  async function copy() {
    await navigator.clipboard.writeText(questions.map((q, i) => `${i + 1}. ${q}`).join("\n")).catch(() => {});
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  }

  async function download() {
    setDownloading(true);
    await api.downloadReport(claim.id, `ClaimSaathi-evidence-${f.claim_number ?? claim.id}.pdf`).catch(() => {});
    setDownloading(false);
  }

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25 }} className="grid gap-5">
      {/* Assessment */}
      <div
        className={`flex flex-wrap items-start gap-4 rounded-2xl border px-5 py-4 ${
          a.tone === "warn" ? "border-[color-mix(in_srgb,var(--warn)_40%,transparent)] bg-[var(--warn-bg)]" : "border-line bg-surface"
        }`}
        role="status"
      >
        <span className={`grid h-11 w-11 flex-none place-items-center rounded-xl ${a.tone === "warn" ? "bg-[color-mix(in_srgb,var(--warn)_18%,transparent)] text-warn" : "bg-surface-2 text-accent"}`}>
          <Icon name={a.icon} className="h-[22px] w-[22px]" />
        </span>
        <div className="min-w-[220px] flex-1">
          <h2 className={`text-xl ${a.tone === "warn" ? "text-warn" : ""}`}>{t(a.title)}</h2>
          <p className="mt-1.5 text-[14.5px]">{t(a.text)}</p>
        </div>
      </div>

      {claim.error === "no_policy" && <p className="rounded-[10px] bg-[var(--warn-bg)] px-3 py-2 text-[13.5px]">{t("rej_no_policy")}</p>}

      {/* Claim facts */}
      <dl className="num m-0 grid grid-cols-[repeat(auto-fit,minmax(150px,1fr))] gap-2">
        <Fact label={t("claim_number")} value={f.claim_number} />
        <Fact label={t("treatment")} value={f.treatment} />
        <Fact label={t("claimed_amount")} value={f.claimed_amount ? formatRupees(f.claimed_amount, lang) : null} />
        <Fact label={t("admission_date")} value={f.admission_date ? formatDate(f.admission_date, lang) : null} />
        <Fact label={t("letter_date")} value={f.letter_date ? formatDate(f.letter_date, lang) : null} />
      </dl>

      {/* Evidence map */}
      <section aria-labelledby="em-title">
        <h3 id="em-title" className="mb-2.5">
          {t("evidence_map")}
        </h3>
        <div className="grid gap-3">
          {fd.rows.map((r, i) => {
            const st = STATUS[r.status] ?? STATUS.unclear;
            const d = r.data ?? {};
            const evidence = [
              d.periods_checked ? t("ev_periods", { n: d.periods_checked, date: formatDate(d.continuous_since, lang) }) : null,
              d.breaks?.length ? t("ev_breaks", { n: d.breaks.length }) : null,
              ...r.evidence.filter((e) => e !== "policy_history"),
            ].filter(Boolean) as string[];
            return (
              <article key={i} className="panel grid gap-3 p-4 md:grid-cols-3">
                <div className="min-w-0">
                  <span className="eyebrow">{t("em_insurer")}</span>
                  <p className="mt-1 text-[14px]">{r.insurer_reason}</p>
                </div>
                <div className="min-w-0">
                  <span className="eyebrow">{t("em_policy")}</span>
                  {r.policy_quote ? (
                    <blockquote className="m-0 mt-1 rounded-[10px] bg-paper px-3 py-2.5 font-[Georgia,'Times_New_Roman',serif] text-[13px] text-paper-ink">
                      {r.policy_quote && claim.policy_id ? (
                        <Link to={`/policy?id=${claim.policy_id}&tab=clauses&cat=all&ref=${encodeURIComponent(r.policy_quote.ref)}`} className="mb-1 block font-mono text-[11px] no-underline hover:underline" aria-label={t("open_clause", { ref: r.policy_quote.ref })}>
                          §{r.policy_quote.ref} · {r.policy_quote.title} →
                        </Link>
                      ) : null}
                      “{r.policy_quote.quote}”
                    </blockquote>
                  ) : (
                    <p className="muted mt-1 text-[13.5px]">—</p>
                  )}
                </div>
                <div className="min-w-0">
                  <span className="eyebrow">{t("em_evidence")}</span>
                  {evidence.length ? (
                    <ul className="m-0 mt-1 grid gap-1 pl-4 text-[13.5px]">
                      {evidence.map((e) => (
                        <li key={e}>{e}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="muted mt-1 text-[13.5px]">{t("ev_none")}</p>
                  )}
                </div>
                <div className="border-t border-line pt-3 md:col-span-3">
                  <span className={`chip ${st.cls} font-semibold`}>
                    <span className="dot" />
                    {t(st.key)}
                  </span>
                  <p className="mt-2 text-[14.5px]">{explain(r, claim.lang)}</p>
                </div>
              </article>
            );
          })}
        </div>
      </section>

      <div className="grid items-start gap-4 lg:grid-cols-2">
        {/* Timeline */}
        <section className="panel" aria-labelledby="tl-claim">
          <h3 id="tl-claim" className="mb-3">
            {t("timeline_claim")}
          </h3>
          <ol className="relative m-0 grid list-none gap-0 p-0">
            {fd.timeline.map((e, i) => (
              <li key={`${e.date}-${e.kind}`} className="relative grid grid-cols-[18px_1fr] gap-3 pb-3.5 last:pb-0">
                {i < fd.timeline.length - 1 && <span className="absolute top-4 left-[8px] h-full w-0.5 bg-line" aria-hidden="true" />}
                <span className={`relative mt-1 h-[14px] w-[14px] rounded-full ring-2 ring-surface ${TL_DOT[e.kind] ?? "bg-line"}`} />
                <div className="min-w-0">
                  <span className="num text-[12.5px] text-muted">{formatDate(e.date, lang)}</span>
                  <p className={`text-[14px] ${e.kind === "insurer_start" ? "font-semibold text-warn" : e.kind === "waiting_ends" ? "font-semibold text-ok" : ""}`}>
                    {t(`tl_${e.kind}` as StringKey, { months: e.months ?? "", ref: e.clause_ref ?? "" })}
                  </p>
                </div>
              </li>
            ))}
          </ol>
        </section>

        <div className="grid gap-4">
          {/* Checklist */}
          <section className="panel" aria-labelledby="cl-title">
            <h3 id="cl-title" className="mb-3">
              {t("checklist_title")}
            </h3>
            <ul className="m-0 grid list-none gap-2.5 p-0">
              {fd.checklist.map((c) => (
                <li key={c.item} className="flex items-start gap-2.5 text-[14px]">
                  <span className={`mt-0.5 grid h-[18px] w-[18px] flex-none place-items-center rounded-[5px] border text-[11px] ${c.have ? "border-sage bg-sage text-accent-ink" : "border-line"}`} aria-hidden="true">
                    {c.have ? "✓" : ""}
                  </span>
                  <span className="flex-1">{t(`cl_${c.item}` as StringKey)}</span>
                  <span className={`chip ${c.have ? "ok" : c.important ? "warn" : ""} text-[11.5px]`}>{t(c.have ? "cl_have" : c.important ? "cl_missing" : "cl_optional")}</span>
                </li>
              ))}
            </ul>
          </section>

          {/* Questions */}
          {questions.length > 0 && (
            <section className="panel" aria-labelledby="q-title">
              <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
                <h3 id="q-title">{t("questions_title")}</h3>
                <button type="button" className="btn px-3 py-1.5 text-[13px]" onClick={() => copy()}>
                  <Icon name={copied ? "check" : "doc"} />
                  {copied ? t("copied") : t("copy_questions")}
                </button>
              </div>
              <ol className="m-0 grid gap-2 pl-5 text-[14px]">
                {questions.map((q) => (
                  <li key={q}>{q}</li>
                ))}
              </ol>
            </section>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="flex flex-wrap items-center gap-2.5">
        <button type="button" className="btn primary" onClick={() => download()} disabled={downloading}>
          <Icon name="upload" className="rotate-180" />
          {t("download_report")}
        </button>
        <Link to={`/complaint?claim=${claim.id}`} className="btn">
          <Icon name="flag" />
          {t("next_complaint")}
        </Link>
        <span className="muted text-[12.5px]">{t("report_english_note")}</span>
      </div>

      <div className="flex flex-wrap items-center gap-2 border-t border-line pt-4 text-[13px]">
        <p className="muted flex-1">{t("rej_disclaimer")}</p>
        {confirming ? (
          <>
            <span>{t("confirm_delete_check")}</span>
            <button type="button" className="btn px-3 py-1.5 text-[13px]" onClick={() => setConfirming(false)}>
              {t("cancel")}
            </button>
            <button type="button" className="btn px-3 py-1.5 text-[13px] text-bad" onClick={onDelete}>
              <Icon name="trash" />
              {t("yes_delete")}
            </button>
          </>
        ) : (
          <button type="button" className="btn px-3 py-1.5 text-[13px] hover:text-bad" onClick={() => setConfirming(true)}>
            <Icon name="trash" />
            {t("delete_check")}
          </button>
        )}
      </div>
    </motion.div>
  );
}
