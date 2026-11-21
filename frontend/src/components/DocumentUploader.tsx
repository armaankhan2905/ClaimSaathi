import { motion } from "motion/react";
import { useId, useRef, useState, type DragEvent, type ReactNode } from "react";
import { useI18n } from "../i18n/I18nProvider";
import type { StringKey } from "../i18n/strings";
import type { DocumentKind } from "../lib/api";
import { Icon } from "./Icon";

const ACCEPT = "application/pdf,image/jpeg,image/png,image/webp,.pdf,.jpg,.jpeg,.png,.webp";

/** Big drop zone with a document-type picker. Calls onFiles; the parent does the uploading. */
export function DocumentUploader({
  kinds,
  onFiles,
  extra,
}: {
  kinds: readonly DocumentKind[];
  onFiles: (files: File[], kind: DocumentKind) => void;
  extra?: ReactNode;
}) {
  const { t } = useI18n();
  const inputRef = useRef<HTMLInputElement>(null);
  const kindId = useId();
  const [kind, setKind] = useState<DocumentKind>(kinds[0]!);
  const [dragging, setDragging] = useState(false);

  function take(list: FileList | null) {
    const files = list ? Array.from(list) : [];
    if (files.length) onFiles(files, kind);
  }

  function onDrop(e: DragEvent) {
    e.preventDefault();
    setDragging(false);
    take(e.dataTransfer.files);
  }

  return (
    <motion.div
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={(e) => {
        if (!e.currentTarget.contains(e.relatedTarget as Node)) setDragging(false);
      }}
      onDrop={onDrop}
      animate={{ scale: dragging ? 1.01 : 1 }}
      transition={{ duration: 0.15 }}
      className={`grid justify-items-center gap-3 rounded-[18px] border-2 border-dashed px-6 py-10 text-center transition-colors ${
        dragging ? "border-accent bg-[var(--accent-soft)]" : "border-[color-mix(in_srgb,var(--accent)_35%,transparent)] bg-surface"
      }`}
    >
      <span className="grid h-16 w-16 place-items-center rounded-[18px] bg-[var(--accent-soft)] text-accent">
        <Icon name="upload" className="h-[30px] w-[30px]" />
      </span>
      <h2 className="text-[21px]">{t("upload_title")}</h2>
      <p className="muted text-sm">{t("upload_hint")}</p>

      <div className="mt-1.5 flex flex-wrap items-end justify-center gap-2.5">
        <label className="field text-left" htmlFor={kindId}>
          {t("doc_type")}
          <select id={kindId} className="input py-2" value={kind} onChange={(e) => setKind(e.target.value as DocumentKind)}>
            {kinds.map((k) => (
              <option key={k} value={k}>
                {t(`kind_${k}` as StringKey)}
              </option>
            ))}
          </select>
        </label>
        {extra}
        <button type="button" className="btn primary" onClick={() => inputRef.current?.click()}>
          <Icon name="upload" />
          {t("choose_files")}
        </button>
      </div>
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPT}
        multiple
        hidden
        onChange={(e) => {
          take(e.target.files);
          e.target.value = ""; // allow choosing the same file again
        }}
      />
    </motion.div>
  );
}
