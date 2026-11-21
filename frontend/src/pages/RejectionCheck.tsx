import { AnimatePresence, motion } from "motion/react";
import { useCallback, useEffect, useId, useState } from "react";
import { useSearchParams } from "react-router";
import { DocumentList } from "../components/DocumentList";
import { DocumentUploader } from "../components/DocumentUploader";
import { DocumentViewer } from "../components/DocumentViewer";
import { Icon } from "../components/Icon";
import { PageHead } from "../components/PageHead";
import { ClaimFindings } from "../components/rejection/ClaimFindings";
import { useI18n } from "../i18n/I18nProvider";
import type { StringKey } from "../i18n/strings";
import { api, CLAIM_DOCUMENT_KINDS, type Claim, type DocumentInfo, type Policy } from "../lib/api";
import { useDocuments } from "../lib/documents";
import { formatDate } from "../lib/format";

const CLAIM_KINDS = new Set<string>(CLAIM_DOCUMENT_KINDS);
const CHECKING_STEPS: StringKey[] = ["rej_checking_1", "rej_checking_2", "rej_checking_3", "rej_checking_4"];

function Steps({ at }: { at: 0 | 1 | 2 }) {
  const { t } = useI18n();
  const steps: StringKey[] = ["rej_step_upload", "rej_step_check", "rej_step_findings"];
  return (
    <ol className="m-0 mb-5 flex list-none flex-wrap items-center gap-2 p-0 text-[13px]">
      {steps.map((s, i) => (
        <li key={s} className="flex items-center gap-2">
          <span
            className={`grid h-6 w-6 place-items-center rounded-full text-[12px] font-semibold ${
              i < at ? "bg-sage text-accent-ink" : i === at ? "bg-accent text-accent-ink" : "bg-surface-2 text-muted"
            }`}
          >
            {i < at ? "✓" : i + 1}
          </span>
          <span className={i === at ? "font-semibold" : "text-muted"}>{t(s)}</span>
          {i < steps.length - 1 && <span className="mx-1 h-px w-6 bg-line" aria-hidden="true" />}
        </li>
      ))}
    </ol>
  );
}

function Checking() {
  const { t } = useI18n();
  const [step, setStep] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setStep((s) => Math.min(s + 1, CHECKING_STEPS.length - 1)), 1600);
    return () => clearInterval(id);
  }, []);
  return (
    <div className="panel grid gap-3" role="status" aria-live="polite">
      {CHECKING_STEPS.map((k, i) => (
        <motion.div key={k} initial={{ opacity: 0.4 }} animate={{ opacity: i <= step ? 1 : 0.4 }} className="flex items-center gap-3 text-[14.5px]">
          <span className={`grid h-6 w-6 flex-none place-items-center rounded-full ${i < step ? "bg-sage text-accent-ink" : i === step ? "bg-accent/15 text-accent" : "bg-surface-2"}`}>
            {i < step ? (
              <Icon name="check" className="h-3.5 w-3.5" />
            ) : i === step ? (
              <span className="h-3 w-3 animate-spin rounded-full border-2 border-current border-t-transparent" />
            ) : null}
          </span>
          {t(k)}
        </motion.div>
      ))}
    </div>
  );
}

/** Upload, reuse and list the documents of one claim, plus the Check button. */
function ClaimDocuments({ claim, policies, onPolicy, onCheck, busy }: {
  claim: Claim;
  policies: Policy[];
  onPolicy: (id: number | null) => void;
  onCheck: () => void;
  busy: boolean;
}) {
  const { t } = useI18n();
  const selectId = useId();
  const { docs, pending, upload, remove, changeKind, dismissPending, reload } = useDocuments(null, undefined, claim.id);
  const [viewing, setViewing] = useState<DocumentInfo | null>(null);
  const [spare, setSpare] = useState<DocumentInfo[]>([]);

  // Claim documents uploaded earlier (e.g. on Policy Insights) and not part of any check yet.
  const loadSpare = useCallback(async () => {
    const all = await api.listDocuments().catch(() => []);
    setSpare(all.filter((d) => d.claim_id == null && d.status === "ready" && (CLAIM_KINDS.has(d.kind) || (d.suggested_kind && CLAIM_KINDS.has(d.suggested_kind)))));
  }, []);
  useEffect(() => {
    loadSpare();
  }, [loadSpare, docs?.length]);

  async function addSpare(d: DocumentInfo) {
    const kind = CLAIM_KINDS.has(d.kind) ? undefined : d.suggested_kind!;
    await api.updateDocument(d.id, { claim_id: claim.id, ...(kind ? { kind } : {}) });
    setSpare((s) => s.filter((x) => x.id !== d.id));
    reload();
  }

  const hasLetter = docs?.some((d) => d.status === "ready" && (d.kind === "rejection_letter" || d.suggested_kind === "rejection_letter")) ?? false;
  const reading = (docs?.some((d) => d.status === "processing") ?? false) || pending.some((p) => !p.error);
  const canCheck = hasLetter && !reading && !busy;

  const picker = (
    <label className="field text-left" htmlFor={selectId}>
      {t("rej_which_policy")}
      <select id={selectId} className="input py-2" value={claim.policy_id ?? ""} onChange={(e) => onPolicy(e.target.value ? Number(e.target.value) : null)}>
        <option value="">{t("rej_policy_auto")}</option>
        {policies.map((p) => (
          <option key={p.id} value={p.id}>
            {p.name}
          </option>
        ))}
      </select>
    </label>
  );

  return (
    <div className="grid gap-5">
      <div className="grid items-start gap-4 lg:grid-cols-[1.4fr_1fr]">
        <div className="grid gap-2">
          <h2 className="text-xl">{t("rej_upload_title")}</h2>
          <p className="muted text-[14px]">{t("rej_upload_hint")}</p>
          <DocumentUploader kinds={CLAIM_DOCUMENT_KINDS} onFiles={upload} extra={picker} />
        </div>
        <aside className="panel grid gap-3">
          <h3>{t("rej_reuse")}</h3>
          {spare.length ? (
            <ul className="m-0 grid list-none gap-2 p-0">
              {spare.map((d) => (
                <li key={d.id} className="flex items-center gap-2.5 rounded-[10px] bg-surface-2 px-3 py-2 text-sm">
                  <Icon name="doc" className="h-4 w-4 flex-none text-accent" />
                  <span className="min-w-0 flex-1">
                    <b className="block truncate font-semibold" title={d.filename}>
                      {d.filename}
                    </b>
                    <small className="text-[12px] text-muted">{t(`kind_${CLAIM_KINDS.has(d.kind) ? d.kind : d.suggested_kind}` as StringKey)}</small>
                  </span>
                  <button type="button" className="btn px-3 py-1 text-[13px]" onClick={() => addSpare(d)}>
                    {t("rej_add")}
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <p className="muted text-[13.5px]">{t("ev_none")}</p>
          )}
          <p className="flex gap-2.5 rounded-[10px] bg-surface-2 px-3 py-2.5 text-[13px] text-muted">
            <Icon name="lock" className="mt-0.5 h-4 w-4 flex-none text-accent" />
            {t("privacy_note")}
          </p>
        </aside>
      </div>

      <section aria-labelledby="claim-docs">
        <h3 id="claim-docs" className="mb-3">
          {t("your_documents")}
        </h3>
        {docs === null ? (
          <div className="h-[72px] animate-pulse rounded-xl bg-surface-2" />
        ) : (
          <DocumentList docs={docs} pending={pending} onView={setViewing} onDelete={remove} onChangeKind={changeKind} onDismissPending={dismissPending} />
        )}
      </section>

      <div className="flex flex-wrap items-center gap-3">
        <button type="button" className="btn primary" disabled={!canCheck} onClick={onCheck}>
          <Icon name="search" />
          {claim.status === "ready" ? t("rej_check_again") : t("rej_check_button")}
        </button>
        {!hasLetter && docs !== null && <span className="muted text-[13px]">{t("rej_need_letter")}</span>}
        {hasLetter && reading && <span className="muted text-[13px]">{t("rej_wait_reading")}</span>}
      </div>
      <DocumentViewer doc={viewing} onClose={() => setViewing(null)} />
    </div>
  );
}

export function RejectionCheck() {
  const { t, lang } = useI18n();
  const [params, setParams] = useSearchParams();
  const [claims, setClaims] = useState<Claim[] | null>(null);
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [claim, setClaim] = useState<Claim | null>(null);
  const [failed, setFailed] = useState(false);
  const [startPolicy, setStartPolicy] = useState<number | null>(null);
  const [showDocs, setShowDocs] = useState(false);
  const startId = useId();

  const raw = params.get("claim");
  const startingNew = raw === "new";
  const wanted = Number(raw) || null;

  const loadAll = useCallback(async () => {
    try {
      const [cs, ps] = await Promise.all([api.listClaims(), api.listPolicies()]);
      setClaims(cs);
      setPolicies(ps);
      setFailed(false);
    } catch {
      setFailed(true);
    }
  }, []);
  useEffect(() => {
    loadAll();
  }, [loadAll]);

  // The claim shown: ?claim=id, else the latest.
  useEffect(() => {
    if (!claims) return;
    const pick = startingNew ? null : (claims.find((c) => c.id === wanted) ?? (wanted ? null : claims[0]) ?? null);
    setClaim(pick);
    setShowDocs(false);
  }, [claims, wanted, startingNew]);

  // Poll while the check runs.
  const checking = claim?.status === "checking";
  useEffect(() => {
    if (!checking || !claim) return;
    const id = setInterval(async () => {
      const c = await api.getClaim(claim.id).catch(() => null);
      if (c && c.status !== "checking") {
        setClaim(c);
        setClaims((cs) => cs?.map((x) => (x.id === c.id ? c : x)) ?? null);
      }
    }, 1500);
    return () => clearInterval(id);
  }, [checking, claim]);

  function select(id: number | "new" | null) {
    const next = new URLSearchParams(params);
    if (id) next.set("claim", String(id));
    else next.delete("claim");
    setParams(next, { replace: true });
  }

  async function start() {
    const c = await api.createClaim({ policy_id: startPolicy, lang });
    setClaims((cs) => [c, ...(cs ?? [])]);
    select(c.id);
  }

  async function setPolicy(id: number | null) {
    if (!claim) return;
    const c = await api.updateClaim(claim.id, { policy_id: id });
    setClaim(c);
  }

  async function check() {
    if (!claim) return;
    try {
      await api.checkClaim(claim.id, lang);
      setClaim({ ...claim, status: "checking", error: null });
      setShowDocs(false);
    } catch {
      setClaim({ ...claim, status: "failed", error: "internal_error" });
    }
  }

  async function remove() {
    if (!claim) return;
    await api.deleteClaim(claim.id);
    const rest = (claims ?? []).filter((c) => c.id !== claim.id);
    setClaims(rest);
    select(rest[0]?.id ?? null);
  }

  const startForm = (
    <div className="panel grid max-w-2xl gap-4">
      <div className="flex items-start gap-4">
        <span className="grid h-11 w-11 flex-none place-items-center rounded-xl bg-surface-2 text-accent">
          <Icon name="search" className="h-[22px] w-[22px]" />
        </span>
        <div>
          <h2 className="text-xl">{t("rej_start_title")}</h2>
          <p className="muted mt-1.5 text-[14.5px]">{t("rej_start_text")}</p>
        </div>
      </div>
      <div className="flex flex-wrap items-end gap-3">
        <label className="field min-w-[220px] flex-1" htmlFor={startId}>
          {t("rej_which_policy")}
          <select id={startId} className="input py-2" value={startPolicy ?? ""} onChange={(e) => setStartPolicy(e.target.value ? Number(e.target.value) : null)}>
            <option value="">{t("rej_policy_auto")}</option>
            {policies.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </label>
        <button type="button" className="btn primary" onClick={() => start()}>
          {t("rej_start_button")}
          <Icon name="arrow" />
        </button>
      </div>
    </div>
  );

  const stage: 0 | 1 | 2 = !claim ? 0 : claim.status === "checking" ? 1 : claim.status === "ready" ? 2 : 0;
  const others = (claims ?? []).filter((c) => c.id !== claim?.id);

  return (
    <>
      <PageHead
        eyebrow={t("rej_eyebrow")}
        title={t("nav_rej")}
        lede={t("rej_sub")}
        actions={
          claim ? (
            <button type="button" className="btn" onClick={() => select("new")}>
              <Icon name="upload" />
              {t("rej_new")}
            </button>
          ) : undefined
        }
      />

      {failed ? (
        <div className="panel flex flex-wrap items-center gap-3">
          <Icon name="alert" className="h-5 w-5 text-bad" />
          <p className="flex-1">{t("err_network")}</p>
          <button type="button" className="btn" onClick={loadAll}>
            {t("retry")}
          </button>
        </div>
      ) : claims === null ? (
        <div className="h-40 animate-pulse rounded-2xl bg-surface-2" aria-busy="true" />
      ) : !claim ? (
        startForm
      ) : (
        <>
          <Steps at={stage} />
          <AnimatePresence mode="wait">
            {claim.status === "checking" ? (
              <motion.div key="checking" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <Checking />
              </motion.div>
            ) : claim.status === "ready" && claim.findings && !showDocs ? (
              <motion.div key="findings" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="grid gap-4">
                <div className="flex flex-wrap items-center gap-2 text-[13px] text-muted">
                  {claim.checked_at && <span>{formatDate(claim.checked_at.slice(0, 10), lang)}</span>}
                  {claim.mode === "basic" && <span className="chip">{t("rej_basic_note")}</span>}
                  <button type="button" className="btn ml-auto px-3 py-1.5 text-[13px]" onClick={() => setShowDocs(true)}>
                    <Icon name="doc" />
                    {t("rej_check_again")}
                  </button>
                </div>
                <ClaimFindings claim={claim} onDelete={remove} />
              </motion.div>
            ) : (
              <motion.div key="docs" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="grid gap-4">
                {claim.status === "failed" && (
                  <p className="flex items-start gap-2.5 rounded-[10px] bg-[var(--warn-bg)] px-3 py-2.5 text-[14px]" role="alert">
                    <Icon name="alert" className="mt-0.5 h-4 w-4 flex-none text-warn" />
                    {t(claim.error === "no_letter" ? "rej_failed_no_letter" : claim.error === "no_policy" ? "rej_no_policy" : "rej_failed")}
                  </p>
                )}
                <ClaimDocuments claim={claim} policies={policies} onPolicy={setPolicy} onCheck={check} busy={false} />
              </motion.div>
            )}
          </AnimatePresence>
        </>
      )}

      {others.length > 0 && (
        <section className="mt-8" aria-labelledby="prev-checks">
          <h3 id="prev-checks" className="mb-2.5">
            {t("rej_previous")}
          </h3>
          <ul className="m-0 grid list-none gap-2 p-0">
            {others.map((c) => (
              <li key={c.id}>
                <button type="button" className="flex w-full flex-wrap items-center gap-3 rounded-xl border border-line bg-surface px-4 py-2.5 text-left text-sm hover:border-accent" onClick={() => select(c.id)}>
                  <Icon name="doc" className="h-4 w-4 text-accent" />
                  <b className="font-semibold">{c.facts?.claim_number ?? `#${c.id}`}</b>
                  <span className="muted flex-1 truncate">{c.facts?.treatment ?? ""}</span>
                  <span className="muted text-[12.5px]">{formatDate(c.created_at.slice(0, 10), lang)}</span>
                  {c.findings && (
                    <span className={`chip text-[11.5px] ${c.findings.assessment === "inconsistency" ? "warn" : ""}`}>{t(`assess_${c.findings.assessment}` as StringKey)}</span>
                  )}
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}
    </>
  );
}
