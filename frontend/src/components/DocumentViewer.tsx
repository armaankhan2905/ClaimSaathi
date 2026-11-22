import { AnimatePresence, motion } from "motion/react";
import { useEffect, useRef, useState } from "react";
import { useI18n } from "../i18n/I18nProvider";
import { api, type DocumentInfo, type DocumentPage } from "../lib/api";
import { Icon } from "./Icon";

/** Side sheet showing the clean text of each page, with how it was read. */
export function DocumentViewer({ doc, onClose }: { doc: DocumentInfo | null; onClose: () => void }) {
  const { t } = useI18n();
  const [pages, setPages] = useState<DocumentPage[] | null>(null);
  const [failed, setFailed] = useState(false);
  const [current, setCurrent] = useState(1);
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!doc) return;
    setPages(null);
    setFailed(false);
    setCurrent(1);
    api.getPages(doc.id).then(setPages).catch(() => setFailed(true));
  }, [doc]);

  useEffect(() => {
    if (!doc) return;
    closeRef.current?.focus();
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [doc, onClose]);

  const page = pages?.find((p) => p.page_number === current);

  return (
    <AnimatePresence>
      {doc && (
        <motion.div className="fixed inset-0 z-40 flex justify-end" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
          <div className="absolute inset-0 bg-black/40" onClick={onClose} aria-hidden="true" />
          <motion.aside
            role="dialog"
            aria-modal="true"
            aria-labelledby="viewer-title"
            className="relative flex h-full w-full max-w-[760px] flex-col border-l border-line bg-bg shadow-2xl"
            initial={{ x: 60 }}
            animate={{ x: 0 }}
            exit={{ x: 60 }}
            transition={{ duration: 0.22, ease: "easeOut" }}
          >
            <header className="flex items-start gap-3 border-b border-line px-5 py-4">
              <div className="min-w-0 flex-1">
                <span className="eyebrow">{t("extracted_text")}</span>
                <h2 id="viewer-title" className="mt-1 break-all text-lg">
                  {doc.filename}
                </h2>
              </div>
              <button ref={closeRef} type="button" className="btn px-2.5 py-1.5" onClick={onClose} aria-label={t("close")}>
                <Icon name="close" />
              </button>
            </header>

            {pages && pages.length > 1 && (
              <nav className="flex gap-1 overflow-x-auto border-b border-line px-5 py-2.5 [scrollbar-width:thin]" aria-label={t("pages_n", { n: pages.length })}>
                {pages.map((p) => (
                  <button
                    key={p.page_number}
                    type="button"
                    onClick={() => setCurrent(p.page_number)}
                    aria-pressed={p.page_number === current}
                    className={`whitespace-nowrap rounded-lg px-3 py-1.5 text-[13px] ${
                      p.page_number === current ? "bg-accent text-accent-ink" : "text-muted hover:bg-surface-2"
                    }`}
                  >
                    {t("page_n", { n: p.page_number })}
                  </button>
                ))}
              </nav>
            )}

            <div className="flex-1 overflow-y-auto px-5 py-4">
              {failed && <p className="text-bad">{t("err_generic")}</p>}
              {!pages && !failed && <div className="h-40 animate-pulse rounded-xl bg-surface-2" />}
              {page && (
                <>
                  <div className="mb-3 flex flex-wrap items-center gap-2 text-[12.5px] text-muted">
                    <span className="font-semibold text-fg">{t("page_n", { n: page.page_number })}</span>
                    <span className={`chip ${page.method === "ocr" ? "warn" : "sage"}`}>
                      {page.method === "ocr"
                        ? t("read_ocr", { n: Math.round((page.ocr_confidence ?? 0) * 100) })
                        : t("read_text_layer")}
                    </span>
                  </div>
                  {page.method === "ocr" && (
                    <p className="mb-3 flex gap-2 rounded-[10px] bg-surface-2 px-3 py-2 text-[12.5px] text-muted">
                      <Icon name="info" className="mt-0.5 h-4 w-4 flex-none text-accent" />
                      {t("ocr_note")}
                    </p>
                  )}
                  <article className="whitespace-pre-wrap rounded-[14px] border border-line bg-paper px-6 py-5 font-mono text-[14px] leading-[1.65] text-paper-ink">
                    {page.text}
                  </article>
                </>
              )}
            </div>
          </motion.aside>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
