import { motion } from "motion/react";
import { useId, useRef, useState, type DragEvent, type ReactNode } from "react";
import { useI18n } from "../i18n/I18nProvider";
import type { StringKey } from "../i18n/strings";
import type { DocumentKind } from "../lib/api";
import { CameraScannerModal } from "./CameraScannerModal";
import { Icon } from "./Icon";

const ACCEPT = "application/pdf,image/jpeg,image/png,image/webp,.pdf,.jpg,.jpeg,.png,.webp";

/** Dual-box uploader: Box 1 for file upload/dropzone, Box 2 for live camera scan integrated with Dart/Flutter. */
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
  const [cameraOpen, setCameraOpen] = useState(false);

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
    <div className="grid gap-3">
      {/* Top Document Metadata Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-line bg-surface px-5 py-3.5 shadow-sm">
        <div className="flex flex-wrap items-center gap-3">
          <label className="field mb-0 text-left" htmlFor={kindId}>
            <span className="text-[12px] font-semibold text-muted uppercase tracking-wider">{t("doc_type")}</span>
            <select
              id={kindId}
              className="input py-1.5 text-sm"
              value={kind}
              onChange={(e) => setKind(e.target.value as DocumentKind)}
            >
              {kinds.map((k) => (
                <option key={k} value={k}>
                  {t(`kind_${k}` as StringKey)}
                </option>
              ))}
            </select>
          </label>
          {extra}
        </div>

        <div className="hidden items-center gap-2 text-xs text-muted sm:flex">
          <span className="inline-block h-2 w-2 rounded-full bg-emerald-500" />
          <span>Upload files or scan physical documents</span>
        </div>
      </div>

      {/* Two Boxes Grid: 1 for Upload, 1 for Scan using Camera */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* Box 1: File Upload Box */}
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
          className={`group flex min-h-[220px] flex-col items-center justify-center rounded-[20px] border-2 border-dashed p-6 text-center transition-all ${
            dragging
              ? "border-accent bg-[var(--accent-soft)]"
              : "border-[color-mix(in_srgb,var(--accent)_35%,transparent)] bg-surface hover:border-accent"
          }`}
        >
          <span className="mb-3 grid h-14 w-14 place-items-center rounded-2xl bg-[var(--accent-soft)] text-accent transition-transform group-hover:scale-105">
            <Icon name="upload" className="h-7 w-7" />
          </span>

          <h3 className="text-lg font-bold">{t("box_upload_title")}</h3>
          <p className="muted mt-1 max-w-[34ch] text-xs leading-relaxed">{t("box_upload_desc")}</p>

          <button
            type="button"
            className="btn primary mt-4 px-4 py-2 text-sm font-semibold shadow-sm"
            onClick={() => inputRef.current?.click()}
          >
            <Icon name="upload" />
            {t("choose_files")}
          </button>
        </motion.div>

        {/* Box 2: Scan using Camera Box (with Dart / Flutter Integration) */}
        <motion.div
          whileHover={{ scale: 1.01 }}
          transition={{ duration: 0.15 }}
          className="group flex min-h-[220px] flex-col items-center justify-center rounded-[20px] border-2 border-dashed border-[color-mix(in_srgb,var(--accent)_35%,transparent)] bg-surface p-6 text-center transition-all hover:border-accent"
        >
          <span className="relative mb-3 grid h-14 w-14 place-items-center rounded-2xl bg-[var(--accent-soft)] text-accent transition-transform group-hover:scale-105">
            <Icon name="camera" className="h-7 w-7" />
            <span className="absolute -top-1 -right-1 flex h-3.5 w-3.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex h-3.5 w-3.5 rounded-full bg-emerald-500" />
            </span>
          </span>

          <div className="flex items-center justify-center gap-1.5">
            <h3 className="text-lg font-bold">{t("box_scan_title")}</h3>
            <span className="rounded bg-accent/15 px-1.5 py-0.5 text-[10px] font-semibold text-accent uppercase tracking-wide">
              Flutter / Dart
            </span>
          </div>

          <p className="muted mt-1 max-w-[34ch] text-xs leading-relaxed">{t("box_scan_desc")}</p>

          <div className="mt-4 flex flex-wrap items-center justify-center gap-2">
            <button
              type="button"
              className="btn primary px-4 py-2 text-sm font-semibold shadow-sm"
              onClick={() => setCameraOpen(true)}
            >
              <Icon name="camera" />
              {t("btn_open_camera")}
            </button>
            <a
              href="http://localhost:5174"
              target="_blank"
              rel="noopener noreferrer"
              className="btn px-2.5 py-2 text-xs"
              title={t("flutter_open_app")}
            >
              <Icon name="external" className="h-3.5 w-3.5" />
              <span>Flutter (:5174)</span>
            </a>
          </div>
        </motion.div>
      </div>

      {/* Hidden file input for file picker */}
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

      {/* Camera Scanner Modal (Live Camera + Flutter Integration) */}
      <CameraScannerModal
        isOpen={cameraOpen}
        onClose={() => setCameraOpen(false)}
        onCapture={(file) => onFiles([file], kind)}
        documentKindLabel={t(`kind_${kind}` as StringKey)}
      />
    </div>
  );
}
