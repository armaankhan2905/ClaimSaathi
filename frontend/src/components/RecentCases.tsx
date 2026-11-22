import { useEffect, useState } from "react";
import { Link } from "react-router";
import { useI18n } from "../i18n/I18nProvider";
import type { StringKey } from "../i18n/strings";
import { api, type Claim, type Complaint } from "../lib/api";
import { useAuth } from "../lib/auth";
import { formatDate } from "../lib/format";
import { Icon } from "./Icon";

type Item = { key: string; to: string; when: string; kind: "check" | "complaint"; title: string; detail: string; chip: { label: string; cls: string } | null };

/** Rejection checks and complaints in progress, newest first (hidden when there are none). */
export function RecentCases() {
  const { t, lang } = useI18n();
  const { user } = useAuth();
  const [items, setItems] = useState<Item[]>([]);

  useEffect(() => {
    if (!user) {
      setItems([]);
      return;
    }
    let live = true;
    Promise.all([api.listClaims(), api.listComplaints()])
      .then(([claims, complaints]: [Claim[], Complaint[]]) => {
        if (!live) return;
        const fromClaims: Item[] = claims.map((c) => ({
          key: `c${c.id}`,
          to: `/rejection?claim=${c.id}`,
          when: c.checked_at ?? c.created_at,
          kind: "check",
          title: c.facts?.claim_number ?? t("case_new_check"),
          detail: c.facts?.treatment ?? "",
          chip: c.findings
            ? { label: t(`assess_${c.findings.assessment}` as StringKey), cls: c.findings.assessment === "inconsistency" ? "warn" : "" }
            : { label: t("case_not_checked"), cls: "" },
        }));
        const fromComplaints: Item[] = complaints.map((c) => ({
          key: `p${c.id}`,
          to: `/complaint?id=${c.id}`,
          when: c.updated_at,
          kind: "complaint",
          title: c.fields.claim_number || `#${c.id}`,
          detail:
            t(`stage_${c.stage}` as StringKey) +
            (c.status === "sent" && c.tracker.reply_due && !c.tracker.replied ? ` · ${t("case_reply_due", { date: formatDate(c.tracker.reply_due, lang) })}` : ""),
          chip: { label: t(`comp_status_${c.status}` as StringKey), cls: c.status === "resolved" ? "ok" : c.status === "sent" ? "sage" : "" },
        }));
        setItems([...fromClaims, ...fromComplaints].sort((a, b) => b.when.localeCompare(a.when)).slice(0, 4));
      })
      .catch(() => {});
    return () => {
      live = false;
    };
  }, [t, lang, user]);

  if (!user || !items.length) return null;
  return (
    <section className="mt-[34px]" aria-labelledby="h-cases">
      <h2 id="h-cases" className="mb-3.5">
        {t("your_cases")}
      </h2>
      <ul className="m-0 grid list-none gap-2.5 p-0 md:grid-cols-2">
        {items.map((it) => (
          <li key={it.key}>
            <Link to={it.to} className="flex items-center gap-3 rounded-2xl border border-line bg-surface px-4 py-3 text-fg no-underline shadow-[var(--shadow)] transition-colors hover:border-sage">
              <span className="grid h-10 w-10 flex-none place-items-center rounded-xl bg-[var(--accent-soft)] text-accent">
                <Icon name={it.kind === "check" ? "search" : "flag"} className="h-5 w-5" />
              </span>
              <span className="min-w-0 flex-1">
                <span className="block text-[12px] text-muted">{t(it.kind === "check" ? "case_check" : "case_complaint")}</span>
                <b className="block truncate font-semibold">{it.title}</b>
                {it.detail && <span className="block truncate text-[13px] text-muted">{it.detail}</span>}
              </span>
              {it.chip && <span className={`chip ${it.chip.cls} text-[11.5px]`}>{it.chip.label}</span>}
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
