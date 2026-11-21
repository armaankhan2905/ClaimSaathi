import { motion } from "motion/react";
import { useId, useState } from "react";
import { useI18n } from "../../i18n/I18nProvider";
import type { StringKey } from "../../i18n/strings";
import { api, type Complaint } from "../../lib/api";
import { formatDate } from "../../lib/format";
import { Icon } from "../Icon";
import { LetterPreview } from "./ComplaintDraft";

const localIso = () => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
};

type StepState = "done" | "now" | "next";

export function ComplaintTrack({ complaint, onChange }: { complaint: Complaint; onChange: (c: Complaint) => void }) {
  const { t, lang } = useI18n();
  const tr = complaint.tracker;
  const resolved = complaint.status === "resolved";
  const stageName = t(`stage_${complaint.stage}` as StringKey);
  const [replyOn, setReplyOn] = useState(localIso());
  const [busy, setBusy] = useState(false);
  const [showLetter, setShowLetter] = useState(false);
  const replyId = useId();

  async function run(fn: () => Promise<Complaint>) {
    setBusy(true);
    try {
      onChange(await fn());
    } finally {
      setBusy(false);
    }
  }

  const steps: { label: string; when?: string; state: StepState }[] = [
    { label: t("tr_draft"), when: formatDate(complaint.created_at.slice(0, 10), lang), state: "done" },
    { label: t("tr_sent", { to: stageName }), when: formatDate(tr.sent_on, lang), state: "done" },
    resolved
      ? { label: t("tr_resolved"), when: formatDate(tr.replied_on, lang), state: "done" }
      : { label: t("tr_waiting"), when: tr.reply_due ? t("tr_due", { date: formatDate(tr.reply_due, lang) }) : undefined, state: tr.replied ? "done" : "now" },
  ];
  if (!resolved && complaint.stage === "insurer")
    steps.push({ label: t("tr_escalate_bb"), when: tr.escalate_after ? t("tr_after", { date: formatDate(tr.escalate_after, lang) }) : undefined, state: tr.can_escalate.includes("bima_bharosa") ? "now" : "next" });
  if (!resolved && complaint.stage !== "ombudsman")
    steps.push({ label: t("tr_ombudsman"), when: tr.ombudsman_by ? t("tr_by", { date: formatDate(tr.ombudsman_by, lang) }) : undefined, state: tr.can_escalate.includes("ombudsman") ? "now" : "next" });

  const overdue = tr.days_left !== null && tr.days_left < 0;

  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="grid gap-5">
      <div className={`flex flex-wrap items-center gap-4 rounded-2xl border px-5 py-4 ${resolved ? "border-[color-mix(in_srgb,var(--ok)_40%,transparent)] bg-[var(--ok-bg)]" : "border-line bg-surface"}`} role="status">
        <span className={`grid h-11 w-11 flex-none place-items-center rounded-full ${resolved ? "bg-ok text-white" : "bg-sage text-accent-ink"}`}>
          <Icon name="check" className="h-5 w-5" />
        </span>
        <div className="min-w-[220px] flex-1">
          <h2 className="text-xl">{resolved ? t("resolved_title") : t("sent_title", { to: stageName })}</h2>
          <p className="mt-1 text-[14px]">{resolved ? t("resolved_text") : t("sent_text", { date: formatDate(tr.sent_on, lang) })}</p>
        </div>
        {tr.reference && (
          <div>
            <span className="muted text-[12px]">{t("reference")}</span>
            <div className="mono text-[15px]">{tr.reference}</div>
          </div>
        )}
      </div>

      <div className="grid items-start gap-4 lg:grid-cols-3">
        <section className="panel" aria-labelledby="tracker-title">
          <h3 id="tracker-title" className="mb-3.5">
            {t("tracker_title")}
          </h3>
          <ol className="m-0 grid list-none gap-0 p-0">
            {steps.map((s, i) => (
              <li key={i} className="relative grid grid-cols-[22px_1fr] gap-3 pb-4 last:pb-0">
                {i < steps.length - 1 && <span className="absolute top-5 left-[10px] h-full w-0.5 bg-line" aria-hidden="true" />}
                <span
                  className={`relative grid h-[22px] w-[22px] place-items-center rounded-full text-[11px] ${
                    s.state === "done" ? "bg-sage text-accent-ink" : s.state === "now" ? "bg-accent text-accent-ink ring-4 ring-[var(--accent-soft)]" : "border-2 border-line bg-surface"
                  }`}
                >
                  {s.state === "done" ? "✓" : ""}
                </span>
                <div className="min-w-0">
                  <b className={`block text-[14px] ${s.state === "next" ? "font-medium text-muted" : "font-semibold"}`}>{s.label}</b>
                  {s.when && <span className="num text-[12.5px] text-muted">{s.when}</span>}
                </div>
              </li>
            ))}
          </ol>
        </section>

        {!resolved && (
          <section className="panel grid gap-3" aria-labelledby="due-title">
            <h3 id="due-title">{t("reply_due_title")}</h3>
            {tr.replied === "unsatisfied" ? (
              <p className="rounded-[10px] bg-[var(--warn-bg)] px-3 py-2 text-[13.5px]">{t("replied_unsatisfied_note", { date: formatDate(tr.replied_on, lang) })}</p>
            ) : (
              <>
                <div className="num flex items-baseline gap-2">
                  {overdue ? (
                    <b className="font-display text-xl text-warn">{t("overdue", { n: Math.abs(tr.days_left!) })}</b>
                  ) : (
                    <>
                      <b className="font-display text-4xl text-accent">{tr.days_left ?? "—"}</b>
                      <span className="muted">{t("days_left")}</span>
                    </>
                  )}
                </div>
                <p className="muted text-[13.5px]">{t("reply_due_text", { date: formatDate(tr.reply_due, lang) })}</p>
                <button type="button" className="btn justify-self-start" onClick={() => api.downloadComplaint(complaint.id, "reminder", "ClaimSaathi-reminder.ics").catch(() => {})}>
                  <Icon name="calendar" />
                  {t("reminder_add")}
                </button>
                <p className="muted text-[12px]">{t("reminder_hint")}</p>
              </>
            )}
          </section>
        )}

        {!resolved && (
          <section className="panel grid gap-3" aria-labelledby="reply-title">
            {!tr.replied && (
              <>
                <h3 id="reply-title">{t("replied_title")}</h3>
                <label className="field" htmlFor={replyId}>
                  {t("reply_on")}
                  <input id={replyId} type="date" className="input" min={tr.sent_on ?? undefined} max={localIso()} value={replyOn} onChange={(e) => setReplyOn(e.target.value)} />
                </label>
                <div className="flex flex-wrap gap-2">
                  <button type="button" className="btn" disabled={busy} onClick={() => run(() => api.recordReply(complaint.id, { outcome: "resolved", reply_on: replyOn }))}>
                    <Icon name="check" />
                    {t("replied_resolved")}
                  </button>
                  <button type="button" className="btn" disabled={busy} onClick={() => run(() => api.recordReply(complaint.id, { outcome: "unsatisfied", reply_on: replyOn }))}>
                    <Icon name="alert" />
                    {t("replied_unsatisfied")}
                  </button>
                </div>
              </>
            )}
            {complaint.stage !== "ombudsman" && (
              <div className={`grid gap-2 ${tr.replied ? "" : "border-t border-line pt-3"}`}>
                <h3 className="text-[16px]" id={tr.replied ? "reply-title" : undefined}>
                  {t("escalate_title")}
                </h3>
                <div className="flex flex-wrap gap-2">
                  {complaint.stage === "insurer" && (
                    <button type="button" className={`btn ${tr.can_escalate.includes("bima_bharosa") ? "primary" : ""}`} disabled={busy || !tr.can_escalate.includes("bima_bharosa")} onClick={() => run(() => api.escalate(complaint.id, "bima_bharosa"))}>
                      <Icon name="flag" />
                      {t("escalate_to_bb")}
                    </button>
                  )}
                  <button type="button" className={`btn ${tr.can_escalate.includes("ombudsman") && complaint.stage === "bima_bharosa" ? "primary" : ""}`} disabled={busy || !tr.can_escalate.includes("ombudsman")} onClick={() => run(() => api.escalate(complaint.id, "ombudsman"))}>
                    <Icon name="flag" />
                    {t("escalate_to_om")}
                  </button>
                </div>
                {!tr.can_escalate.length && tr.escalate_after && <p className="muted text-[12.5px]">{t("escalate_locked", { date: formatDate(tr.escalate_after, lang) })}</p>}
                {tr.ombudsman_from && tr.ombudsman_by && (
                  <p className="muted text-[12.5px]">{t("om_window", { from: formatDate(tr.ombudsman_from, lang), by: formatDate(tr.ombudsman_by, lang) })}</p>
                )}
              </div>
            )}
          </section>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <button type="button" className="btn" onClick={() => api.downloadComplaint(complaint.id, "package", "ClaimSaathi-complaint-package.pdf").catch(() => {})}>
          <Icon name="download" />
          {t("dl_package")}
        </button>
        <button type="button" className="btn" aria-expanded={showLetter} onClick={() => setShowLetter((v) => !v)}>
          <Icon name="eye" />
          {t("preview_title")}
        </button>
      </div>
      {showLetter && (
        <div className="max-w-3xl">
          <LetterPreview letter={complaint.letter} />
        </div>
      )}
    </motion.div>
  );
}
