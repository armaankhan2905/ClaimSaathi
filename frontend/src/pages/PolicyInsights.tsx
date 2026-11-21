import { useEffect, useId, useState } from "react";
import { useSearchParams } from "react-router";
import { DocumentList } from "../components/DocumentList";
import { DocumentUploader } from "../components/DocumentUploader";
import { DocumentViewer } from "../components/DocumentViewer";
import { Icon } from "../components/Icon";
import { PageHead } from "../components/PageHead";
import { PolicyStatusBanner } from "../components/PolicyStatusBanner";
import { useI18n } from "../i18n/I18nProvider";
import type { StringKey } from "../i18n/strings";
import { api, POLICY_DOCUMENT_KINDS, type DocumentInfo, type Policy } from "../lib/api";
import { useDocuments } from "../lib/documents";

const TIPS: { kind: StringKey; tip: StringKey }[] = [
  { kind: "kind_policy_wording", tip: "tip_wording" },
  { kind: "kind_policy_schedule", tip: "tip_schedule" },
  { kind: "kind_previous_policy", tip: "tip_previous" },
];

export function PolicyInsights() {
  const { t } = useI18n();
  const [params, setParams] = useSearchParams();
  const policySelectId = useId();
  const [policies, setPolicies] = useState<Policy[]>([]);
  const policyId = params.get("id") ? Number(params.get("id")) : null;
  // Every document type is listed for now, so a file retyped as a claim document doesn't vanish.
  // Once Rejection Check has its own list (Stage 6), pass POLICY_DOCUMENT_KINDS here.
  const { docs, failed, pending, upload, remove, changeKind, dismissPending, reload } = useDocuments(policyId);
  const [viewing, setViewing] = useState<DocumentInfo | null>(null);

  // Reload the policy list when documents finish reading: an upload may have created a policy.
  const docsSignature = docs?.map((d) => `${d.id}:${d.status}:${d.policy_id}`).join(",") ?? "";
  useEffect(() => {
    api.listPolicies().then(setPolicies).catch(() => {});
  }, [docsSignature]);

  function choosePolicy(value: string) {
    setParams(value ? { id: value } : {}, { replace: true });
  }

  const policyPicker = (
    <label className="field text-left" htmlFor={policySelectId}>
      {t("attach_to")}
      <select id={policySelectId} className="input py-2" value={policyId ?? ""} onChange={(e) => choosePolicy(e.target.value)}>
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
    <>
      <PageHead eyebrow={t("policy_eyebrow")} title={t("nav_policy")} lede={t("policy_sub")} />
      {policyId != null && <PolicyStatusBanner policyId={policyId} refreshKey={docsSignature} />}

      <div className="grid items-start gap-4 lg:grid-cols-[1.4fr_1fr]">
        <DocumentUploader kinds={POLICY_DOCUMENT_KINDS} onFiles={upload} extra={policyPicker} />

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

      <section className="mt-8" aria-labelledby="docs-title">
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
            <div className="h-[72px] animate-pulse rounded-xl bg-surface-2" />
          </div>
        ) : (
          <DocumentList
            docs={docs}
            pending={pending}
            onView={setViewing}
            onDelete={remove}
            onChangeKind={changeKind}
            onDismissPending={dismissPending}
          />
        )}
      </section>

      <p className="disclaimer">{t("disclaimer")}</p>
      <DocumentViewer doc={viewing} onClose={() => setViewing(null)} />
    </>
  );
}
