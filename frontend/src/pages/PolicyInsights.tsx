import { AnimatePresence, motion } from "motion/react";
import { useEffect, useId, useState } from "react";
import { useSearchParams } from "react-router";
import { DocumentList } from "../components/DocumentList";
import { DocumentUploader } from "../components/DocumentUploader";
import { DocumentViewer } from "../components/DocumentViewer";
import { Icon, type IconName } from "../components/Icon";
import { AskTab } from "../components/insights/AskTab";
import { ClausesTab, type ClauseFilter } from "../components/insights/ClausesTab";
import { CompareTab } from "../components/insights/CompareTab";
import { DetailsTab } from "../components/insights/DetailsTab";
import { PageHead } from "../components/PageHead";
import { PolicyStatusBanner } from "../components/PolicyStatusBanner";
import { useI18n } from "../i18n/I18nProvider";
import type { StringKey } from "../i18n/strings";
import { api, POLICY_DOCUMENT_KINDS, type Clause, type DocumentInfo, type Policy } from "../lib/api";
import { useDocuments } from "../lib/documents";
import { usePolicyDetail } from "../lib/policy";

type Tab = "details" | "clauses" | "compare" | "ask";
const TABS: { key: Tab; label: StringKey; icon: IconName }[] = [
  { key: "details", label: "tab_details", icon: "info" },
  { key: "clauses", label: "tab_clauses", icon: "doc" },
  { key: "compare", label: "tab_compare", icon: "search" },
  { key: "ask", label: "tab_ask", icon: "user" },
];

const TIPS: { kind: StringKey; tip: StringKey }[] = [
  { kind: "kind_policy_wording", tip: "tip_wording" },
  { kind: "kind_policy_schedule", tip: "tip_schedule" },
  { kind: "kind_previous_policy", tip: "tip_previous" },
];

/** Upload area and the documents of the selected policy (or all documents when none is selected). */
function UploadPanel({ policyId, policies, onPolicyChosen, onDocsChanged }: {
  policyId: number | null;
  policies: Policy[];
  onPolicyChosen: (id: number | null) => void;
  onDocsChanged: (signature: string) => void;
}) {
  const { t } = useI18n();
  const selectId = useId();
  // Policy documents only: claim documents (letters, bills, receipts) live on the Rejection Check page.
  const { docs, failed, pending, upload, remove, changeKind, dismissPending, reload } = useDocuments(policyId, POLICY_DOCUMENT_KINDS);
  const [viewing, setViewing] = useState<DocumentInfo | null>(null);

  const signature = docs?.map((d) => `${d.id}:${d.status}:${d.policy_id}`).join(",") ?? "";
  useEffect(() => onDocsChanged(signature), [signature, onDocsChanged]);

  const picker = (
    <label className="field text-left" htmlFor={selectId}>
      {t("attach_to")}
      <select id={selectId} className="input py-2" value={policyId ?? ""} onChange={(e) => onPolicyChosen(e.target.value ? Number(e.target.value) : null)}>
        <option value="">{t("attach_none")}</option>
        {policies.map((p) => (
          <option key={p.id} value={p.id}>
            {p.name}
          </option>
        ))}
      </select>
    </label>
  );

  return (
    <div className="mb-6">
      <div className="grid items-start gap-4 lg:grid-cols-[1.4fr_1fr]">
        <DocumentUploader kinds={POLICY_DOCUMENT_KINDS} onFiles={upload} extra={picker} />
        <aside className="panel grid gap-3">
          <h3>{t("what_to_upload")}</h3>
          <ul className="m-0 grid list-none gap-2.5 p-0">
            {TIPS.map((x) => (
              <li key={x.kind} className="rounded-[10px] bg-surface-2 px-3 py-2.5 text-sm">
                <b className="font-semibold">{t(x.kind)}</b>
                <small className="block text-[12.5px] text-muted">{t(x.tip)}</small>
              </li>
            ))}
          </ul>
          <p className="flex gap-2.5 rounded-[10px] bg-surface-2 px-3 py-2.5 text-[13px] text-muted">
            <Icon name="lock" className="mt-0.5 h-4 w-4 flex-none text-accent" />
            {t("privacy_note")}
          </p>
        </aside>
      </div>

      <section className="mt-6" aria-labelledby="docs-title">
        <h2 id="docs-title" className="mb-3.5">
          {t("your_documents")}
        </h2>
        {failed ? (
          <div className="panel flex flex-wrap items-center gap-3">
            <Icon name="alert" className="h-5 w-5 text-bad" />
            <p className="flex-1">{t("err_network")}</p>
            <button type="button" className="btn" onClick={reload}>
              {t("retry")}
            </button>
          </div>
        ) : docs === null ? (
          <div className="grid gap-2.5" aria-busy="true">
            <div className="h-[72px] animate-pulse rounded-xl bg-surface-2" />
          </div>
        ) : (
          <DocumentList docs={docs} pending={pending} onView={setViewing} onDelete={remove} onChangeKind={changeKind} onDismissPending={dismissPending} />
        )}
      </section>
      <DocumentViewer doc={viewing} onClose={() => setViewing(null)} />
    </div>
  );
}

export function PolicyInsights() {
  const { t } = useI18n();
  const [params, setParams] = useSearchParams();
  const pickerId = useId();
  const [policies, setPolicies] = useState<Policy[] | null>(null);
  const [docsSignature, setDocsSignature] = useState("");

  const policyId = params.get("id") ? Number(params.get("id")) : null;
  const tab = (TABS.some((x) => x.key === params.get("tab")) ? params.get("tab") : "details") as Tab;
  const filter = (params.get("cat") ?? "all") as ClauseFilter;
  const focusRef = params.get("ref");
  const [uploadOpen, setUploadOpen] = useState(params.get("upload") === "1");

  const { policy, clauses, reload } = usePolicyDetail(policyId);

  // Reload policies when documents finish reading: an upload may have created or filled one.
  useEffect(() => {
    api.listPolicies().then(setPolicies).catch(() => setPolicies([]));
  }, [docsSignature]);
  useEffect(() => {
    if (docsSignature) reload();
  }, [docsSignature, reload]);

  // Open the first policy when none is chosen yet; show the uploader when there are none.
  useEffect(() => {
    if (!policies) return;
    if (policyId == null && policies.length && !params.has("none")) update({ id: String(policies[0]!.id) });
    if (!policies.length) setUploadOpen(true);
  }, [policies]); // runs when the list loads; `params` changes must not re-trigger it

  function update(changes: Record<string, string | null>) {
    const next = new URLSearchParams(params);
    for (const [k, v] of Object.entries(changes)) {
      if (v == null) next.delete(k);
      else next.set(k, v);
    }
    setParams(next, { replace: true });
  }

  const choosePolicy = (id: number | null) => update(id == null ? { id: null, none: "1", tab: null, ref: null } : { id: String(id), none: null, ref: null });
  const openClause = (ref: string) => update({ tab: "clauses", cat: "all", ref });
  const showCategory = (cat: Clause["category"]) => update({ tab: "clauses", cat, ref: null });

  return (
    <>
      <PageHead
        eyebrow={t("policy_eyebrow")}
        title={t("nav_policy")}
        lede={t("policy_sub")}
        actions={
          <div className="flex flex-wrap items-end gap-2.5">
            {!!policies?.length && (
              <label className="field" htmlFor={pickerId}>
                {t("choose_policy")}
                <select id={pickerId} className="input min-w-[220px] py-2" value={policyId ?? ""} onChange={(e) => choosePolicy(e.target.value ? Number(e.target.value) : null)}>
                  {policyId == null && <option value="">{t("attach_none")}</option>}
                  {policies.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name}
                    </option>
                  ))}
                </select>
              </label>
            )}
            {!!policies?.length && (
              <button type="button" className={`btn ${uploadOpen ? "" : "primary"}`} onClick={() => setUploadOpen((o) => !o)} aria-expanded={uploadOpen}>
                <Icon name={uploadOpen ? "close" : "upload"} />
                {uploadOpen ? t("hide_upload") : t("upload_documents")}
              </button>
            )}
          </div>
        }
      />

      {policies?.length === 0 && (
        <div className="panel mb-4 flex items-start gap-3" role="status">
          <span className="grid h-10 w-10 flex-none place-items-center rounded-xl bg-[var(--accent-soft)] text-accent">
            <Icon name="doc" className="h-5 w-5" />
          </span>
          <div>
            <p className="font-semibold">{t("insights_empty_title")}</p>
            <p className="muted mt-0.5 text-[14px]">{t("insights_empty_text")}</p>
          </div>
        </div>
      )}

      <AnimatePresence initial={false}>
        {uploadOpen && (
          <motion.div key="upload" initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} transition={{ duration: 0.25 }} className="overflow-hidden">
            <UploadPanel policyId={policyId} policies={policies ?? []} onPolicyChosen={choosePolicy} onDocsChanged={setDocsSignature} />
          </motion.div>
        )}
      </AnimatePresence>

      {policyId != null && (
        <>
          <PolicyStatusBanner policyId={policyId} refreshKey={docsSignature} />

          <div role="tablist" aria-label={t("policy_views")} className="mb-5 flex gap-0.5 overflow-x-auto border-b border-line [scrollbar-width:none]">
            {TABS.map((x) => (
              <button
                key={x.key}
                role="tab"
                type="button"
                aria-selected={tab === x.key}
                onClick={() => update({ tab: x.key, ref: null })}
                className={`-mb-px inline-flex items-center gap-2 border-b-2 px-3.5 py-2.5 text-[15px] font-medium whitespace-nowrap ${
                  tab === x.key ? "border-accent text-fg" : "border-transparent text-muted hover:text-fg"
                }`}
              >
                <Icon name={x.icon} className="h-4 w-4" />
                {t(x.label)}
              </button>
            ))}
          </div>

          <div role="tabpanel">
            {!policy || !clauses ? (
              <div className="grid gap-3" aria-busy="true">
                <div className="h-28 animate-pulse rounded-xl bg-surface-2" />
                <div className="h-40 animate-pulse rounded-xl bg-surface-2" />
              </div>
            ) : tab === "details" ? (
              <DetailsTab policy={policy} clauses={clauses} onOpenClause={openClause} onShowCategory={showCategory} />
            ) : tab === "clauses" ? (
              <ClausesTab policy={policy} clauses={clauses} filter={filter} onFilter={(f) => update({ cat: f, ref: null })} focusRef={focusRef} />
            ) : tab === "compare" ? (
              <CompareTab policy={policy} policies={policies ?? []} onOpenClause={openClause} />
            ) : (
              <AskTab policy={policy} onOpenClause={openClause} />
            )}
          </div>
        </>
      )}
    </>
  );
}
