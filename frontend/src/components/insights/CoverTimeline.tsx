import { motion } from "motion/react";
import { useI18n } from "../../i18n/I18nProvider";
import type { PolicyDetail } from "../../lib/api";
import { formatDate, formatMonth } from "../../lib/format";
import type { PolicyTerms } from "../../lib/policy";

const DAY = 86_400_000;
const ts = (iso: string) => new Date(`${iso}T00:00:00`).getTime();

type Mark = { at: number; label: string; sub: string; kind: "start" | "renewal" | "today" | "end" };

/** YYYY-MM-DD in the viewer's own time zone (toISOString would give yesterday before 5:30 am in India). */
function localIso(d: Date) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

/**
 * First policy → renewals → today → current policy end, with breaks in cover shaded red and
 * the date each waiting period ended. Built from the rules engine's timeline, not from AI.
 */
export function CoverTimeline({ terms, timeline }: { terms: PolicyTerms; timeline: NonNullable<PolicyDetail["timeline"]> }) {
  const { t, lang } = useI18n();
  const history = (terms.policy_history ?? []).filter((p) => p.start && p.end) as { start: string; end: string }[];
  const first = timeline.continuous_since ?? terms.first_policy_date ?? history[0]?.start ?? terms.policy_start;
  const end = terms.policy_end ?? history[history.length - 1]?.end;
  if (!first || !end) return null;

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const start = Math.min(ts(first), ...history.map((h) => ts(h.start)));
  const stop = Math.max(ts(end), today.getTime());
  const span = Math.max(stop - start, DAY);
  const pos = (at: number) => `${((at - start) / span) * 94 + 3}%`;

  const marks: Mark[] = [{ at: ts(first), label: t("timeline_first"), sub: formatDate(first, lang), kind: "start" }];
  for (const h of history.slice(1)) marks.push({ at: ts(h.start), label: t("timeline_renewal"), sub: formatMonth(h.start, lang), kind: "renewal" });
  marks.push({ at: ts(end), label: t("timeline_ends"), sub: formatDate(end, lang), kind: "end" });
  if (today.getTime() <= stop) marks.push({ at: today.getTime(), label: t("timeline_today"), sub: formatDate(localIso(today), lang), kind: "today" });

  // Waiting periods of a year or more, one label per end date ("4.3, 3.7 · 36 months ✓ Mar 2025").
  const waitGroups = new Map<string, { ends: string; months: number; refs: string[]; completed: boolean }>();
  for (const w of timeline.waiting_periods) {
    if (!w.ends || w.months < 12) continue;
    const g = waitGroups.get(w.ends) ?? { ends: w.ends, months: w.months, refs: [], completed: !!w.completed };
    if (w.clause_ref) g.refs.push(w.clause_ref);
    waitGroups.set(w.ends, g);
  }
  const waits = [...waitGroups.values()].sort((a, b) => a.ends.localeCompare(b.ends));

  return (
    <section className="panel mt-4" aria-labelledby="tl-title">
      <h3 id="tl-title" className="mb-2">
        {t("timeline_title")}
      </h3>
      <div className="overflow-x-auto pb-1">
        <div className="relative h-[204px] min-w-[640px]">
          {/* axis */}
          <div className="absolute top-[94px] right-0 left-0 h-[3px] rounded bg-line" />
          <motion.div
            className="absolute top-[94px] h-[3px] rounded bg-accent"
            style={{ left: pos(start) }}
            initial={{ width: 0 }}
            animate={{ width: `calc(${pos(Math.min(today.getTime(), ts(end)))} - ${pos(start)})` }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          />
          {/* breaks in cover */}
          {timeline.breaks.map((b) => (
            <div
              key={b.previous_end}
              className="absolute top-[86px] h-[19px] rounded bg-[var(--bad-bg)] outline outline-1 outline-bad"
              style={{ left: pos(ts(b.previous_end)), width: `calc(${pos(ts(b.next_start))} - ${pos(ts(b.previous_end))})` }}
              title={t("break_found", { date: formatDate(b.previous_end, lang) })}
            >
              <span className="absolute -top-5 left-0 text-[11px] whitespace-nowrap text-bad">{t("timeline_break")}</span>
            </div>
          ))}
          {/* waiting periods ending */}
          {waits.map((w, i) => (
            <div key={w.ends} className="absolute" style={{ left: pos(ts(w.ends)), top: 0 }}>
              <div className="absolute top-[52px] h-[42px] w-px -translate-x-1/2 border-l border-dashed border-sage" />
              <div
                className={`absolute -translate-x-1/2 rounded-md border border-sage bg-surface px-1.5 py-0.5 text-center text-[10.5px] leading-tight whitespace-nowrap ${w.completed ? "text-fg" : "text-warn"}`}
                style={{ top: 8 + (i % 2) * 22 }}
              >
                {w.refs.length ? `${w.refs.join(", ")} · ` : ""}
                {t("months_n", { n: w.months })} {w.completed ? "✓" : "→"} {formatMonth(w.ends, lang)}
              </div>
            </div>
          ))}
          {/* events */}
          {marks.map((m) => (
            <div key={`${m.kind}-${m.at}`} className="absolute top-0 h-full" style={{ left: pos(m.at) }}>
              <span
                className={`absolute top-[88px] h-[15px] w-[15px] -translate-x-1/2 rounded-full border-2 ${
                  m.kind === "today" ? "border-warn bg-warn" : m.kind === "end" ? "border-accent bg-surface" : "border-accent bg-accent"
                }`}
              />
              {m.kind !== "renewal" && (
                // "Today" gets its own row so it never collides with the policy end date
                <div className={`absolute ${m.kind === "today" ? "top-[162px] text-warn" : "top-[112px]"} w-[136px] -translate-x-1/2 text-center text-[11.5px] leading-snug`}>
                  <b className="block text-[12px]">{m.label}</b>
                  <span className="text-muted">{m.sub}</span>
                </div>
              )}
              {m.kind === "renewal" && (
                <span className="absolute top-[110px] -translate-x-1/2 text-[10.5px] whitespace-nowrap text-muted">{m.sub}</span>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
