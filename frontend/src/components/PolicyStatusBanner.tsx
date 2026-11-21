import { useEffect, useState } from "react";
import { useI18n } from "../i18n/I18nProvider";
import { api, type Policy } from "../lib/api";
import { Icon } from "./Icon";

/** What ClaimSaathi has understood about one policy, refreshed while it is being read. */
export function PolicyStatusBanner({ policyId, refreshKey }: { policyId: number; refreshKey: unknown }) {
  const { t } = useI18n();
  const [policy, setPolicy] = useState<Policy | null>(null);

  useEffect(() => {
    api.getPolicy(policyId).then(setPolicy).catch(() => setPolicy(null));
  }, [policyId, refreshKey]);

  const running = policy?.analysis_status === "running" || policy?.status === "processing";
  useEffect(() => {
    if (!running) return;
    const id = setInterval(() => api.getPolicy(policyId).then(setPolicy).catch(() => {}), 2000);
    return () => clearInterval(id);
  }, [running, policyId]);

  if (!policy || policy.analysis_status === "none") return null;

  async function readAgain() {
    setPolicy(await api.analyzePolicy(policyId));
  }

  if (running)
    return (
      <div className="panel mb-4 flex items-center gap-3 py-3.5" role="status">
        <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-accent border-r-transparent" aria-hidden="true" />
        <p className="text-sm">{t("understanding_policy")}</p>
      </div>
    );

  const failed = policy.analysis_status === "failed";
  return (
    <div className={`panel mb-4 flex flex-wrap items-start gap-3 py-3.5 ${failed ? "border-[color-mix(in_srgb,var(--bad)_40%,transparent)]" : ""}`}>
      <span className={`grid h-9 w-9 flex-none place-items-center rounded-[10px] ${failed ? "bg-[var(--bad-bg)] text-bad" : "bg-[var(--ok-bg)] text-ok"}`}>
        <Icon name={failed ? "alert" : "check"} className="h-[18px] w-[18px]" />
      </span>
      <div className="min-w-[220px] flex-1">
        <p className="font-semibold">
          {policy.name} · {failed ? t("understanding_failed") : policy.clause_count ? t("understood_n", { n: policy.clause_count }) : t("understood_none")}
        </p>
        {!failed && (
          <p className="muted mt-0.5 text-[13px]">{policy.analysis_mode === "ai" ? t("ai_mode_note") : t("basic_mode_note")}</p>
        )}
      </div>
      <button type="button" className="btn px-3 py-1.5 text-[13px]" onClick={() => readAgain().catch(() => {})}>
        {t("read_again")}
      </button>
    </div>
  );
}
