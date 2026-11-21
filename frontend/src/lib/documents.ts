import { useCallback, useEffect, useRef, useState } from "react";
import type { StringKey } from "../i18n/strings";
import { api, ApiError, type DocumentInfo, type DocumentKind } from "./api";

const KNOWN_ERRORS = new Set([
  "file_too_large",
  "unsupported_type",
  "empty_file",
  "password_protected",
  "unreadable_file",
  "too_many_pages",
  "no_text_found",
  "internal_error",
]);

/** Translation key for an upload or reading error code. */
export function docErrorKey(code: string | null | undefined): StringKey {
  if (code === "network") return "err_network";
  return code && KNOWN_ERRORS.has(code) ? (`docerr_${code}` as StringKey) : "err_generic";
}

export function formatBytes(n: number): string {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${Math.round(n / 1024)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
}

/** Files still on their way up, shown above the list until the server has them. */
export type PendingUpload = { key: string; name: string; size: number; error: string | null };

/**
 * Documents for one policy (or all, when policyId is null), kept fresh while any are
 * still being read, plus upload and delete actions.
 */
export function useDocuments(policyId: number | null, kinds: readonly DocumentKind[]) {
  const [docs, setDocs] = useState<DocumentInfo[] | null>(null);
  const [failed, setFailed] = useState(false);
  const [pending, setPending] = useState<PendingUpload[]>([]);
  const kindSet = useRef(new Set<string>(kinds));

  const load = useCallback(async () => {
    try {
      const all = await api.listDocuments(policyId);
      setDocs(all.filter((d) => kindSet.current.has(d.kind)));
      setFailed(false);
    } catch {
      setFailed(true);
    }
  }, [policyId]);

  useEffect(() => {
    setDocs(null);
    load();
  }, [load]);

  // Poll while anything is still being read.
  const processing = docs?.some((d) => d.status === "processing") ?? false;
  useEffect(() => {
    if (!processing) return;
    const id = setInterval(load, 1500);
    return () => clearInterval(id);
  }, [processing, load]);

  const upload = useCallback(
    async (files: File[], kind: DocumentKind) => {
      await Promise.all(
        files.map(async (file) => {
          const key = `${file.name}-${file.size}-${Math.random()}`;
          setPending((p) => [...p, { key, name: file.name, size: file.size, error: null }]);
          try {
            const doc = await api.uploadDocument(file, kind, policyId);
            setPending((p) => p.filter((x) => x.key !== key));
            setDocs((d) => [doc, ...(d ?? [])]);
          } catch (e) {
            const code = e instanceof ApiError ? (e.status === 0 ? "network" : e.message) : "internal_error";
            setPending((p) => p.map((x) => (x.key === key ? { ...x, error: code } : x)));
          }
        }),
      );
    },
    [policyId],
  );

  const dismissPending = useCallback((key: string) => setPending((p) => p.filter((x) => x.key !== key)), []);

  const remove = useCallback(async (id: number) => {
    await api.deleteDocument(id);
    setDocs((d) => d?.filter((x) => x.id !== id) ?? null);
  }, []);

  return { docs, failed, pending, upload, remove, dismissPending, reload: load };
}
