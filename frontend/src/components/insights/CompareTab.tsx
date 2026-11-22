import { AnimatePresence, motion } from "motion/react";
import { useEffect, useId, useMemo, useState, type FormEvent, type ReactNode } from "react";
import { useNavigate } from "react-router";
import { useI18n } from "../../i18n/I18nProvider";
import type { StringKey } from "../../i18n/strings";
import { api, type CompareResult, type FeatureRow, type Policy, type PolicyDetail, type PolicyVerdict, type Verdict } from "../../lib/api";
import { formatRupees } from "../../lib/format";
import { Icon } from "../Icon";

const SCENARIOS: Record<"health" | "motor", string[]> = {
  health: ["knee_year3", "private_room", "maternity_year2", "diabetes_year3", "cataract_year4", "accident_ambulance", "abroad"],
  motor: ["flood_engine", "bumper_zero_dep", "no_licence"],
};

const VERDICT: Record<Verdict, { key: StringKey; cls: string; icon: string }> = {
  covered: { key: "verdict_covered", cls: "ok", icon: "✓" },
  partly_covered: { key: "verdict_partly_covered", cls: "warn", icon: "!" },
  not_covered: { key: "verdict_not_covered", cls: "bad", icon: "✕" },
  unclear: { key: "verdict_unclear", cls: "", icon: "?" },
};

const ROWS: Record<string, StringKey> = {
  sum_insured: "row_sum_insured",
  premium: "row_premium",
  room_rent: "row_room_rent",
  copay: "row_copay",
  wait_initial: "row_wait_initial",
  wait_specified: "row_wait_specified",
  wait_ped: "row_wait_ped",
  wait_maternity: "row_wait_maternity",
  maternity: "row_maternity",
  exclusions_count: "row_exclusions_count",
};

function VerdictPanel({ name, result, onOpenClause, highlight }: { name: string; result: PolicyVerdict; onOpenClause: (ref: string) => void; highlight: boolean }) {
  const { t } = useI18n();
  const v = VERDICT[result.verdict] ?? VERDICT.unclear;
  const reason = result.reason
    ? t(`reason_${result.reason.code}` as StringKey, { n: result.reason.months ?? "" })
    : null;
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={`panel grid content-start gap-2.5 ${highlight ? "border-[color-mix(in_srgb,var(--ok)_55%,transparent)] shadow-[0_0_0_3px_var(--ok-bg)]" : ""}`}
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-[15.5px]">{name}</h3>
        <span className={`chip ${v.cls} text-[13px] font-semibold`}>
          {v.icon} {t(v.key)}
        </span>
      </div>
      {result.summary ? <p className="text-[14.5px]">{result.summary}</p> : reason && <p className="text-[14.5px]">{reason}</p>}
      {result.what_you_pay && (
        <p className="rounded-[10px] bg-[var(--warn-bg)] px-3 py-2 text-[13px]">
          <b className="font-semibold">{t("limits_label")}: </b>
          {result.what_you_pay}
        </p>
      )}
      {result.citations.map((c) => (
        <blockquote key={c.ref} className="m-0 rounded-[10px] bg-paper px-3 py-2.5 font-mono text-[13px] text-paper-ink">
          <button type="button" onClick={() => onOpenClause(c.ref)} className="mb-1 block font-mono text-[11px] text-accent hover:underline" aria-label={t("open_clause", { ref: c.ref })}>
            §{c.ref} · {c.title} →
          </button>
          “{c.quote}”
        </blockquote>
      ))}
    </motion.div>
  );
}

function Cell({ row, side }: { row: FeatureRow; side: "a" | "b" }) {
  const { t, lang } = useI18n();
  const value = row[side];
  let shown: ReactNode = value ?? <span className="text-muted">—</span>;
  if (value != null) {
    if (row.key === "sum_insured" || row.key === "premium") shown = formatRupees(Number(value), lang);
    else if (row.key.startsWith("wait_")) shown = Number(value) === 1 ? t("month_1") : t("months_n", { n: value });
    else if (row.key === "maternity") shown = t(value === "covered" ? "verdict_covered" : "verdict_not_covered");
  }
  const better = row.better === side;
  return (
    <td className={`px-4 py-3 align-top ${better ? "font-semibold text-ok" : row.better ? "text-muted" : ""}`}>
      {shown}
      {better && <span className="chip ok ml-2 px-2 py-0 text-[11px] font-normal">{t("better")}</span>}
    </td>
  );
}

export function CompareTab({ policy, policies, onOpenClause }: { policy: PolicyDetail; policies: Policy[]; onOpenClause: (ref: string) => void }) {
  const { t, lang } = useI18n();
  const navigate = useNavigate();
  const pickerId = useId();
  const category = policy.category === "motor" ? "motor" : "health";

  // Only the same kind of policy (health with health, motor with motor) whose clauses have been read.
  const others = useMemo(
    () => policies.filter((p) => p.id !== policy.id && p.clause_count > 0 && p.category === policy.category),
    [policies, policy.id, policy.category],
  );
  const [otherId, setOtherId] = useState<number | null>(null);
  const other = others.find((p) => p.id === otherId) ?? others[0] ?? null;

  const [rows, setRows] = useState<FeatureRow[] | null>(null);
  const [result, setResult] = useState<CompareResult | null>(null);
  const [active, setActive] = useState<string | null>(null);
  const [custom, setCustom] = useState("");
  const [busy, setBusy] = useState(false);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    setRows(null);
    setResult(null);
    setActive(null);
    if (!other) return;
    api.compareTable(policy.id, other.id).then(setRows).catch(() => setRows([]));
  }, [policy.id, other?.id]); // only when the pair changes, not on every render of `other`

  async function run(body: { scenario?: string; custom?: string }, label: string) {
    if (!other || busy) return;
    setBusy(true);
    setFailed(false);
    setActive(label);
    try {
      setResult(await api.compareScenario({ a: policy.id, b: other.id, lang, ...body }));
    } catch {
      setFailed(true);
      setResult(null);
    } finally {
      setBusy(false);
    }
  }

  function onCustom(e: FormEvent) {
    e.preventDefault();
    if (custom.trim().length >= 3) run({ custom: custom.trim() }, `custom:${custom.trim()}`);
  }

  // Re-run the chosen situation when the language changes, so the explanation follows it.
  useEffect(() => {
    if (!result || !active) return;
    run(active.startsWith("custom:") ? { custom: active.slice(7) } : { scenario: active }, active);
  }, [lang]); // only on a language change

  if (policy.clause_count === 0)
    return (
      <div className="panel flex items-start gap-3">
        <span className="grid h-10 w-10 flex-none place-items-center rounded-xl bg-[var(--warn-bg)] text-warn">
          <Icon name="alert" className="h-5 w-5" />
        </span>
        <p className="muted mt-2">{t("compare_no_clauses")}</p>
      </div>
    );

  if (!other)
    return (
      <div className="panel flex items-start gap-3">
        <span className="grid h-10 w-10 flex-none place-items-center rounded-xl bg-[var(--accent-soft)] text-accent">
          <Icon name="doc" className="h-5 w-5" />
        </span>
        <div>
          <p className="muted mt-2">{t("compare_need_other")}</p>
          <button type="button" className="btn primary mt-3" onClick={() => navigate(`/policy?id=${policy.id}&tab=compare&upload=1`)}>
            <Icon name="upload" />
            {t("upload_documents")}
          </button>
        </div>
      </div>
    );

  const openA = onOpenClause;
  const openB = (ref: string) => navigate(`/policy?id=${other.id}&tab=clauses&cat=all&ref=${encodeURIComponent(ref)}`);
  const winnerName = result?.winner === "a" ? policy.name : result?.winner === "b" ? other.name : null;

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.2 }}>
      <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
        <div className="min-w-0">
          <h2 className="text-xl">
            {policy.name} <span className="font-medium text-muted">vs</span> {other.name}
          </h2>
          <p className="muted mt-1 text-[13.5px]">{t("compare_intro")}</p>
        </div>
        {others.length > 1 && (
          <label className="field" htmlFor={pickerId}>
            {t("compare_with")}
            <select id={pickerId} className="input py-2" value={other.id} onChange={(e) => setOtherId(Number(e.target.value))}>
              {others.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </label>
        )}
      </div>

      <div className="mb-3 flex flex-wrap gap-2" role="group" aria-label={t("compare_intro")}>
        {SCENARIOS[category].map((key) => (
          <button
            key={key}
            type="button"
            disabled={busy}
            aria-pressed={active === key}
            onClick={() => run({ scenario: key }, key)}
            className={`rounded-[10px] border px-3 py-2 text-[13.5px] disabled:opacity-60 ${active === key ? "border-accent bg-surface-2 text-fg" : "border-line bg-surface text-muted hover:text-fg"}`}
          >
            {t(`sc_${key}` as StringKey)}
          </button>
        ))}
      </div>
      <form onSubmit={onCustom} className="mb-5 flex gap-2">
        <input
          value={custom}
          onChange={(e) => setCustom(e.target.value)}
          placeholder={t("compare_custom_ph")}
          aria-label={t("compare_custom_ph")}
          maxLength={300}
          className="input min-w-0 flex-1"
        />
        <button type="submit" className="btn primary" disabled={busy || custom.trim().length < 3}>
          {t("compare_run")}
        </button>
      </form>

      <AnimatePresence mode="wait">
        {busy ? (
          <motion.div key="busy" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="mb-5 grid gap-4 md:grid-cols-2" role="status" aria-label={t("comparing")}>
            <div className="h-40 animate-pulse rounded-2xl bg-surface-2" />
            <div className="h-40 animate-pulse rounded-2xl bg-surface-2" />
            <p className="muted text-sm md:col-span-2">{t("comparing")}</p>
          </motion.div>
        ) : failed ? (
          <p key="err" role="alert" className="mb-5 rounded-[10px] bg-[var(--bad-bg)] px-3 py-2 text-[13.5px] text-bad">
            {t("compare_error")}
          </p>
        ) : result ? (
          <motion.div key={`${result.scenario.text}-${lang}`} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="mb-6">
            <p className={`mb-3 flex items-center gap-2 rounded-[10px] px-3 py-2.5 text-[14px] font-semibold ${winnerName ? "bg-[var(--ok-bg)] text-ok" : "bg-surface-2"}`}>
              <Icon name={winnerName ? "check" : "info"} className="h-4 w-4 flex-none" />
              {winnerName ? t("winner_one", { name: winnerName }) : t("winner_tie")}
            </p>
            <div className="grid gap-4 md:grid-cols-2">
              <VerdictPanel name={policy.name} result={result.a} onOpenClause={openA} highlight={result.winner === "a"} />
              <VerdictPanel name={other.name} result={result.b} onOpenClause={openB} highlight={result.winner === "b"} />
            </div>
            {result.a.mode === "basic" && <p className="muted mt-2 text-[12.5px]">{t("compare_basic_note")}</p>}
          </motion.div>
        ) : null}
      </AnimatePresence>

      <h3 className="mb-2.5">{t("feature_table")}</h3>
      {rows === null ? (
        <div className="h-48 animate-pulse rounded-2xl bg-surface-2" />
      ) : (
        <div className="overflow-x-auto rounded-[14px] border border-line">
          <table className="w-full min-w-[560px] border-collapse text-[14px]">
            <thead>
              <tr className="bg-surface-2 text-left text-[12px] tracking-[.06em] text-muted uppercase">
                <th className="px-4 py-3 font-semibold">{t("feature")}</th>
                <th className="px-4 py-3 font-semibold normal-case tracking-normal">{policy.name}</th>
                <th className="px-4 py-3 font-semibold normal-case tracking-normal">{other.name}</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.key} className="border-t border-line">
                  <th scope="row" className="px-4 py-3 text-left align-top font-semibold">
                    {t(ROWS[r.key] ?? "feature")}
                  </th>
                  <Cell row={r} side="a" />
                  <Cell row={r} side="b" />
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </motion.div>
  );
}
