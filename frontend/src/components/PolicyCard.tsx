import { motion } from "motion/react";
import { Link } from "react-router";
import { useI18n } from "../i18n/I18nProvider";
import type { StringKey } from "../i18n/strings";
import type { Policy } from "../lib/api";
import { formatDate, formatMonth, formatRupees } from "../lib/format";

const STATUS: Record<Policy["status"], { key: StringKey; cls: string }> = {
  active: { key: "status_active", cls: "ok" },
  lapsed: { key: "status_lapsed", cls: "bad" },
  processing: { key: "status_processing", cls: "sage" },
};

export function PolicyCard({ policy, index = 0 }: { policy: Policy; index?: number }) {
  const { t, lang } = useI18n();
  const status = STATUS[policy.status] ?? STATUS.active;
  const reading = policy.status === "processing" || policy.analysis_status === "running";
  const isMotor = policy.category === "motor";
  const addons = policy.highlights.addons ?? [];
  const warnings = policy.highlights.warnings ?? [];

  const stats: { label: string; value: string }[] = [
    { label: isMotor ? t("idv") : t("sum_insured"), value: formatRupees(policy.sum_insured, lang) },
    { label: t("renews"), value: formatDate(policy.renews_on, lang) },
    isMotor
      ? { label: t("addons"), value: addons.length ? addons.join(", ") : t("none") }
      : { label: t("cover_since"), value: formatMonth(policy.cover_since, lang) },
  ];

  return (
    <motion.article
      className="panel grid gap-3"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: index * 0.06, ease: "easeOut" }}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <span className="eyebrow">{t(`cat_${policy.category}` as StringKey)}</span>
          <h3 className="mt-1 text-lg">{policy.name}</h3>
          <p className="muted text-[13px]">
            {policy.insurer || (reading ? "…" : "")}
            {policy.insurer && policy.policy_number && (
              <>
                {" · "}
                <span className="mono">{policy.policy_number}</span>
              </>
            )}
          </p>
        </div>
        {reading ? (
          <span className="chip sage">
            <span className="inline-block h-3 w-3 animate-spin rounded-full border-2 border-current border-r-transparent" aria-hidden="true" />
            {t("reading_details")}
          </span>
        ) : (
          <span className={`chip ${status.cls}`}>
            <span className="dot" />
            {t(status.key)}
          </span>
        )}
      </div>
      {policy.analysis_status === "failed" && (
        <span className="chip warn justify-self-start">
          <span className="dot" />
          {t("details_failed")}
        </span>
      )}
      <dl className="num m-0 grid grid-cols-2 gap-2.5 sm:grid-cols-3">
        {stats.map((s) => (
          <div key={s.label} className="min-w-0 rounded-[10px] bg-surface-2 px-3 py-2.5">
            <dt className="text-[11.5px] text-muted">{s.label}</dt>
            <dd className="m-0 mt-0.5 truncate font-semibold" title={s.value}>
              {s.value}
            </dd>
          </div>
        ))}
      </dl>
      <div className="flex flex-wrap items-center gap-2">
        <Link to={`/policy?id=${policy.id}`} className="btn">
          {t("view_insights")}
        </Link>
        {warnings.map((w) => (
          <span key={w} className="chip warn">
            <span className="dot" />
            {w}
          </span>
        ))}
      </div>
    </motion.article>
  );
}
