import { useI18n } from "../../i18n/I18nProvider";
import type { WaitingStatus } from "../../lib/api";
import { formatDate } from "../../lib/format";

/** "Over since 12 Mar 2024" (green) or "Ends 12 Mar 2028 · 480 days left" (amber). */
export function WaitingChip({ status }: { status: WaitingStatus }) {
  const { t, lang } = useI18n();
  if (status.completed == null || !status.ends) return null;
  if (status.completed)
    return (
      <span className="chip ok">
        <span className="dot" />
        {t("wp_over", { date: formatDate(status.ends, lang) })}
      </span>
    );
  return (
    <span className="chip warn">
      <span className="dot" />
      {t("wp_ends", { date: formatDate(status.ends, lang) })} · {t("wp_days_left", { n: status.days_left ?? 0 })}
    </span>
  );
}

export function waitingBasisKey(status: WaitingStatus) {
  if (status.note === "break_in_cover") return "wp_break_note" as const;
  if (status.counted_from === "first_policy_date") return "wp_from_first" as const;
  if (status.counted_from === "policy_start") return "wp_from_start" as const;
  return "wp_unclear" as const;
}
