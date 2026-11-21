import { AnimatePresence, motion } from "motion/react";
import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "react-router";
import { ComplaintDraft } from "../components/complaint/ComplaintDraft";
import { ComplaintTrack } from "../components/complaint/ComplaintTrack";
import { StartComplaint } from "../components/complaint/StartComplaint";
import { Icon } from "../components/Icon";
import { PageHead } from "../components/PageHead";
import { useI18n } from "../i18n/I18nProvider";
import type { StringKey } from "../i18n/strings";
import { api, type Claim, type Complaint, type Situation } from "../lib/api";
import { formatDate } from "../lib/format";

function Steps({ at }: { at: 0 | 1 | 2 }) {
  const { t } = useI18n();
  const steps: StringKey[] = ["comp_step_route", "comp_step_draft", "comp_step_track"];
  return (
    <ol className="m-0 mb-5 flex list-none flex-wrap items-center gap-2 p-0 text-[13px]">
      {steps.map((s, i) => (
        <li key={s} className="flex items-center gap-2">
          <span className={`grid h-6 w-6 place-items-center rounded-full text-[12px] font-semibold ${i < at ? "bg-sage text-accent-ink" : i === at ? "bg-accent text-accent-ink" : "bg-surface-2 text-muted"}`}>
            {i < at ? "✓" : i + 1}
          </span>
          <span className={i === at ? "font-semibold" : "text-muted"}>{t(s)}</span>
          {i < steps.length - 1 && <span className="mx-1 h-px w-6 bg-line" aria-hidden="true" />}
        </li>
      ))}
    </ol>
  );
}

export function ComplaintPage() {
  const { t, lang } = useI18n();
  const [params, setParams] = useSearchParams();
  const [complaints, setComplaints] = useState<Complaint[] | null>(null);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [failed, setFailed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [confirming, setConfirming] = useState(false);

  const id = params.get("id");
  const fromClaim = Number(params.get("claim")) || null;

  const load = useCallback(async () => {
    try {
      const [cs, cl] = await Promise.all([api.listComplaints(), api.listClaims()]);
      setComplaints(cs);
      setClaims(cl);
      setFailed(false);
    } catch {
      setFailed(true);
    }
  }, []);
  useEffect(() => {
    load();
  }, [load]);

  // Which complaint is open: ?id=, else the one for ?claim=, else the latest (unless starting a new one).
  const current: Complaint | null = (() => {
    if (!complaints || id === "new") return null;
    if (id) return complaints.find((c) => c.id === Number(id)) ?? null;
    if (fromClaim) return complaints.find((c) => c.claim_id === fromClaim) ?? null;
    return complaints[0] ?? null;
  })();

  function open(next: number | "new") {
    setParams({ id: String(next) }, { replace: true });
    setConfirming(false);
  }

  function replace(c: Complaint) {
    setComplaints((cs) => (cs ? cs.map((x) => (x.id === c.id ? c : x)) : [c]));
  }

  async function start(claimId: number | null, situation: Situation) {
    setBusy(true);
    try {
      const c = await api.createComplaint({ claim_id: claimId, situation });
      setComplaints((cs) => [c, ...(cs ?? [])]);
      open(c.id);
    } finally {
      setBusy(false);
    }
  }

  async function remove() {
    if (!current) return;
    await api.deleteComplaint(current.id);
    const rest = (complaints ?? []).filter((c) => c.id !== current.id);
    setComplaints(rest);
    open(rest[0]?.id ?? "new");
  }

  const stage: 0 | 1 | 2 = !current ? 0 : current.status === "draft" ? 1 : 2;
  const others = (complaints ?? []).filter((c) => c.id !== current?.id);

  return (
    <>
      <PageHead
        eyebrow={t("comp_eyebrow")}
        title={t("nav_comp")}
        lede={t("comp_sub")}
        actions={
          current ? (
            <button type="button" className="btn" onClick={() => open("new")}>
              <Icon name="plus" />
              {t("comp_new")}
            </button>
          ) : undefined
        }
      />

      {failed ? (
        <div className="panel flex flex-wrap items-center gap-3">
          <Icon name="alert" className="h-5 w-5 text-bad" />
          <p className="flex-1">{t("err_network")}</p>
          <button type="button" className="btn" onClick={load}>
            {t("retry")}
          </button>
        </div>
      ) : complaints === null ? (
        <div className="h-40 animate-pulse rounded-2xl bg-surface-2" aria-busy="true" />
      ) : (
        <>
          <Steps at={stage} />
          <AnimatePresence mode="wait">
            <motion.div key={current ? `${current.id}-${current.status}-${current.stage}` : "start"} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.18 }}>
              {!current ? (
                <StartComplaint claims={claims} initialClaim={fromClaim} onStart={start} busy={busy} />
              ) : current.status === "draft" ? (
                <ComplaintDraft complaint={current} onChange={replace} />
              ) : (
                <ComplaintTrack complaint={current} onChange={replace} />
              )}
            </motion.div>
          </AnimatePresence>

          {current && (
            <div className="mt-6 flex flex-wrap items-center gap-2 border-t border-line pt-4 text-[13px]">
              <p className="muted flex-1">{t("comp_disclaimer")}</p>
              {confirming ? (
                <>
                  <span>{t("confirm_delete_complaint")}</span>
                  <button type="button" className="btn px-3 py-1.5 text-[13px]" onClick={() => setConfirming(false)}>
                    {t("cancel")}
                  </button>
                  <button type="button" className="btn px-3 py-1.5 text-[13px] text-bad" onClick={() => remove()}>
                    <Icon name="trash" />
                    {t("yes_delete")}
                  </button>
                </>
              ) : (
                <button type="button" className="btn px-3 py-1.5 text-[13px] hover:text-bad" onClick={() => setConfirming(true)}>
                  <Icon name="trash" />
                  {t("delete_complaint")}
                </button>
              )}
            </div>
          )}
          {!current && <p className="disclaimer">{t("comp_disclaimer")}</p>}
        </>
      )}

      {others.length > 0 && (
        <section className="mt-8" aria-labelledby="prev-complaints">
          <h3 id="prev-complaints" className="mb-2.5">
            {t("comp_previous")}
          </h3>
          <ul className="m-0 grid list-none gap-2 p-0">
            {others.map((c) => (
              <li key={c.id}>
                <button type="button" className="flex w-full flex-wrap items-center gap-3 rounded-xl border border-line bg-surface px-4 py-2.5 text-left text-sm hover:border-accent" onClick={() => open(c.id)}>
                  <Icon name="flag" className="h-4 w-4 text-accent" />
                  <b className="font-semibold">{c.fields.claim_number || `#${c.id}`}</b>
                  <span className="muted flex-1 truncate">{t(`stage_${c.stage}` as StringKey)}</span>
                  <span className="muted text-[12.5px]">{formatDate(c.created_at.slice(0, 10), lang)}</span>
                  <span className={`chip text-[11.5px] ${c.status === "resolved" ? "ok" : c.status === "sent" ? "sage" : ""}`}>{t(`comp_status_${c.status}` as StringKey)}</span>
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}
    </>
  );
}
