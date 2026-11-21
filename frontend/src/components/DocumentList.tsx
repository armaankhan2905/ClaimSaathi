import { AnimatePresence, motion } from "motion/react";
import { useState } from "react";
import { useI18n } from "../i18n/I18nProvider";
import type { StringKey } from "../i18n/strings";
import { api, CLAIM_DOCUMENT_KINDS, POLICY_DOCUMENT_KINDS, type DocumentInfo, type DocumentKind } from "../lib/api";
import { docErrorKey, formatBytes, type PendingUpload } from "../lib/documents";
import { Icon } from "./Icon";

function FileBadge({ contentType }: { contentType: string }) {
  const label = contentType === "application/pdf" ? "PDF" : contentType.split("/")[1]?.toUpperCase().replace("JPEG", "JPG");
  return (
    <span className="relative grid h-[46px] w-[38px] flex-none place-items-end justify-center rounded-md bg-paper pb-1.5 text-[9px] font-bold text-paper-ink shadow-[inset_0_0_0_1px_var(--line)]">
      {label}
    </span>
  );
}

function Spinner() {
  return <span className="inline-block h-3 w-3 animate-spin rounded-full border-2 border-current border-r-transparent" aria-hidden="true" />;
}

function StatusChip({ doc }: { doc: DocumentInfo }) {
  const { t } = useI18n();
  if (doc.status === "processing")
    return (
      <span className="chip sage">
        <Spinner />
        {t("reading")}
      </span>
    );
  if (doc.status === "failed")
    return (
      <span className="chip bad">
        <span className="dot" />
        {t("read_failed")}
      </span>
    );
  const pages = doc.page_count === 1 ? t("page_1") : t("pages_n", { n: doc.page_count ?? 0 });
  return (
    <span className="chip ok">
      <Icon name="check" className="h-3 w-3" />
      {pages}
      {doc.ocr_pages > 0 && ` · ${t("ocr_n", { n: doc.ocr_pages })}`}
    </span>
  );
}

/** Compact type picker shown in place of the type label, so a wrong choice can be fixed. */
function KindSelect({ doc, onChange }: { doc: DocumentInfo; onChange: (kind: DocumentKind) => Promise<void> }) {
  const { t } = useI18n();
  const [failed, setFailed] = useState(false);
  const groups: { label: StringKey; kinds: readonly DocumentKind[] }[] = [
    { label: "group_policy_docs", kinds: POLICY_DOCUMENT_KINDS },
    { label: "group_claim_docs", kinds: CLAIM_DOCUMENT_KINDS },
  ];
  return (
    <>
      <select
        value={doc.kind}
        aria-label={`${t("doc_type")}: ${doc.filename}`}
        title={t("change_type")}
        onChange={(e) => {
          setFailed(false);
          onChange(e.target.value as DocumentKind).catch(() => setFailed(true));
        }}
        className="max-w-full cursor-pointer rounded-md border border-transparent bg-transparent py-0.5 pr-1 pl-0 text-[12.5px] text-muted hover:border-line hover:bg-surface-2 focus:border-sage focus:outline-none"
      >
        {groups.map((g) => (
          <optgroup key={g.label} label={t(g.label)}>
            {g.kinds.map((k) => (
              <option key={k} value={k}>
                {t(`kind_${k}` as StringKey)}
              </option>
            ))}
          </optgroup>
        ))}
      </select>
      {failed && (
        <span role="alert" className="ml-1 text-[12px] text-bad">
          {t("err_generic")}
        </span>
      )}
    </>
  );
}

function DocumentRow({
  doc,
  onView,
  onDelete,
  onChangeKind,
}: {
  doc: DocumentInfo;
  onView: () => void;
  onDelete: () => Promise<void>;
  onChangeKind: (kind: DocumentKind) => Promise<void>;
}) {
  const { t } = useI18n();
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);

  return (
    <motion.li
      layout
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, height: 0, marginTop: 0 }}
      transition={{ duration: 0.2 }}
      className="list-none overflow-hidden rounded-xl border border-line bg-surface p-3"
    >
      <div className="flex flex-wrap items-center gap-3">
        <FileBadge contentType={doc.content_type} />
        <div className="min-w-0 flex-1 basis-48">
          <b className="block break-all text-sm font-semibold">{doc.filename}</b>
          <span className="flex flex-wrap items-center gap-x-1 text-[12.5px] text-muted">
            <KindSelect doc={doc} onChange={onChangeKind} />
            <span aria-hidden="true">·</span>
            {formatBytes(doc.size_bytes)}
          </span>
        </div>
        <StatusChip doc={doc} />
        <div className="flex gap-1.5">
          {doc.status === "ready" && (
            <button type="button" className="btn px-2.5 py-1.5 text-[13px]" onClick={onView}>
              <Icon name="eye" />
              {t("view_text")}
            </button>
          )}
          <button
            type="button"
            className="btn px-2.5 py-1.5"
            title={t("open_file")}
            aria-label={`${t("open_file")}: ${doc.filename}`}
            onClick={() => api.openDocumentFile(doc.id).catch(() => {})}
          >
            <Icon name="external" />
          </button>
          <button
            type="button"
            className="btn px-2.5 py-1.5 hover:text-bad"
            title={t("delete")}
            aria-label={`${t("delete")}: ${doc.filename}`}
            onClick={() => setConfirming(true)}
          >
            <Icon name="trash" />
          </button>
        </div>
      </div>

      {doc.status === "failed" && (
        <p className="mt-2.5 flex items-start gap-2 rounded-[10px] bg-[var(--bad-bg)] px-3 py-2 text-[13px] text-bad">
          <Icon name="alert" className="mt-0.5 h-4 w-4 flex-none" />
          {t(docErrorKey(doc.error))}
        </p>
      )}

      {confirming && (
        <div role="alertdialog" className="mt-2.5 flex flex-wrap items-center gap-2 rounded-[10px] bg-surface-2 px-3 py-2 text-[13.5px]">
          <span className="flex-1">{t("confirm_delete")}</span>
          <button type="button" className="btn px-3 py-1.5 text-[13px]" onClick={() => setConfirming(false)} disabled={busy}>
            {t("cancel")}
          </button>
          <button
            type="button"
            className="btn px-3 py-1.5 text-[13px] text-bad"
            disabled={busy}
            onClick={async () => {
              setBusy(true);
              try {
                await onDelete();
              } catch {
                setBusy(false);
              }
            }}
          >
            <Icon name="trash" />
            {t("yes_delete")}
          </button>
        </div>
      )}
    </motion.li>
  );
}

export function DocumentList({
  docs,
  pending,
  onView,
  onDelete,
  onChangeKind,
  onDismissPending,
}: {
  docs: DocumentInfo[];
  pending: PendingUpload[];
  onView: (doc: DocumentInfo) => void;
  onDelete: (id: number) => Promise<void>;
  onChangeKind: (id: number, kind: DocumentKind) => Promise<void>;
  onDismissPending: (key: string) => void;
}) {
  const { t } = useI18n();
  if (!docs.length && !pending.length) return <p className="muted py-6 text-center text-sm">{t("no_documents")}</p>;

  return (
    <ul className="m-0 grid gap-2.5 p-0">
      <AnimatePresence initial={false}>
        {pending.map((p) => (
          <motion.li
            key={p.key}
            layout
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="list-none rounded-xl border border-dashed border-line bg-surface p-3"
          >
            <div className="flex flex-wrap items-center gap-3">
              <span className="grid h-[46px] w-[38px] flex-none place-items-center rounded-md bg-surface-2 text-accent">
                <Icon name="doc" className="h-5 w-5" />
              </span>
              <div className="min-w-0 flex-1 basis-48">
                <b className="block break-all text-sm font-semibold">{p.name}</b>
                <span className="text-[12.5px] text-muted">{formatBytes(p.size)}</span>
              </div>
              {p.error ? (
                <button type="button" className="btn px-2.5 py-1.5" aria-label={t("close")} onClick={() => onDismissPending(p.key)}>
                  <Icon name="close" />
                </button>
              ) : (
                <span className="chip sage">
                  <Spinner />
                  {t("uploading")}
                </span>
              )}
            </div>
            {p.error && (
              <p className="mt-2.5 flex items-start gap-2 rounded-[10px] bg-[var(--bad-bg)] px-3 py-2 text-[13px] text-bad">
                <Icon name="alert" className="mt-0.5 h-4 w-4 flex-none" />
                {t(docErrorKey(p.error))}
              </p>
            )}
          </motion.li>
        ))}
        {docs.map((d) => (
          <DocumentRow
            key={d.id}
            doc={d}
            onView={() => onView(d)}
            onDelete={() => onDelete(d.id)}
            onChangeKind={(kind) => onChangeKind(d.id, kind)}
          />
        ))}
      </AnimatePresence>
    </ul>
  );
}
