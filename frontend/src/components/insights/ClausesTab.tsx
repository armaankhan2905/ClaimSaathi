import { AnimatePresence, motion } from "motion/react";
import { useEffect, useMemo, useRef, useState } from "react";
import { useI18n } from "../../i18n/I18nProvider";
import type { StringKey } from "../../i18n/strings";
import { api, type Clause, type PolicyDetail } from "../../lib/api";
import { CATEGORY_CHIP, CATEGORY_LABEL, waitingFor } from "../../lib/policy";
import { Icon } from "../Icon";
import { WaitingChip } from "./WaitingChip";

export type ClauseFilter = "all" | "coverage" | "exclusion" | "limit" | "waiting_period" | "definition" | "rules";

const FILTERS: { key: ClauseFilter; label: StringKey; match: (c: Clause) => boolean }[] = [
  { key: "all", label: "filter_all", match: () => true },
  { key: "coverage", label: "ccat_coverage", match: (c) => c.category === "coverage" },
  { key: "exclusion", label: "ccat_exclusion", match: (c) => c.category === "exclusion" },
  { key: "limit", label: "ccat_limit", match: (c) => c.category === "limit" },
  { key: "waiting_period", label: "ccat_waiting_period", match: (c) => c.category === "waiting_period" },
  { key: "definition", label: "ccat_definition", match: (c) => c.category === "definition" },
  { key: "rules", label: "ccat_rules", match: (c) => ["condition", "claim_process", "grievance", "other"].includes(c.category) },
];

/** Rejoin lines the PDF wrapped mid-sentence; keep bullets, numbered items and blank lines. */
export function reflow(text: string): string {
  const out: string[] = [];
  for (const line of text.split("\n")) {
    const prev = out[out.length - 1];
    const startsItem = /^\s*(•|-|\d+[.)]|\([a-z0-9]+\))\s/i.test(line);
    if (prev && line.trim() && prev.trim() && !/[.:;!?]$/.test(prev.trim()) && !startsItem) out[out.length - 1] = `${prev.trimEnd()} ${line.trim()}`;
    else out.push(line);
  }
  return out.join("\n");
}

function ClauseCard({ clause, timeline, best, focused }: { clause: Clause; timeline: PolicyDetail["timeline"]; best?: boolean; focused?: boolean }) {
  const { t, lang } = useI18n();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLElement>(null);
  const long = clause.text.length > 520;
  const wait = waitingFor(clause, timeline);
  const pages = clause.page_start === clause.page_end ? t("page_short", { n: clause.page_start }) : t("pages_short", { a: clause.page_start, b: clause.page_end });

  useEffect(() => {
    if (focused) ref.current?.scrollIntoView({ behavior: "smooth", block: "center" });
  }, [focused]);

  return (
    <motion.article
      ref={ref}
      layout="position"
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.18 }}
      id={`clause-${clause.ref}`}
      className={`grid overflow-hidden rounded-[14px] border md:grid-cols-2 ${focused ? "border-accent shadow-[0_0_0_3px_var(--accent-soft)]" : "border-line"}`}
    >
      <div className="min-w-0 bg-paper px-[18px] py-4 text-paper-ink">
        <span className="font-mono text-[11.5px] opacity-70">{t("clause_ref_line", { ref: clause.ref, section: clause.section_title, pages })}</span>
        <h3 className="mt-1 mb-2 text-[15px]">{clause.title}</h3>
        <p className={`font-[Georgia,'Times_New_Roman',serif] text-[13.5px] leading-[1.6] whitespace-pre-wrap ${long && !open ? "line-clamp-[9]" : ""}`}>
          {reflow(clause.text)}
        </p>
        {long && (
          <button type="button" className="mt-1.5 text-[12.5px] font-semibold text-accent" onClick={() => setOpen((o) => !o)}>
            {open ? t("show_less") : t("show_full")}
          </button>
        )}
      </div>
      <div className="flex min-w-0 flex-col gap-2 bg-surface px-[18px] py-4">
        <span className="eyebrow">{t("what_it_means")}</span>
        {clause.plain ? <p className="text-[14.5px]">{clause.plain[lang]}</p> : <p className="muted text-[13.5px]">{t("no_plain")}</p>}
        <div className="mt-auto flex flex-wrap gap-2 pt-1">
          {best && (
            <span className="chip sage">
              <Icon name="search" className="h-3 w-3" />
              {t("best_match")}
            </span>
          )}
          <span className={`chip ${CATEGORY_CHIP[clause.category]}`}>{t(CATEGORY_LABEL[clause.category])}</span>
          {wait && <WaitingChip status={wait} />}
        </div>
      </div>
    </motion.article>
  );
}

export function ClausesTab({
  policy,
  clauses,
  filter,
  onFilter,
  focusRef,
}: {
  policy: PolicyDetail;
  clauses: Clause[];
  filter: ClauseFilter;
  onFilter: (f: ClauseFilter) => void;
  focusRef: string | null;
}) {
  const { t } = useI18n();
  const [query, setQuery] = useState("");
  const [hits, setHits] = useState<Clause[] | null>(null);
  const [searching, setSearching] = useState(false);

  // Meaning-based search on the server once the user has typed a few letters (debounced).
  useEffect(() => {
    const q = query.trim();
    if (q.length < 2) {
      setHits(null);
      return;
    }
    setSearching(true);
    let current = true; // a slower reply to an older query must not replace newer results
    const timer = setTimeout(() => {
      api
        .searchClauses(policy.id, q, 8)
        .then((r) => current && setHits(r.filter((h) => h.score >= 0.12).map((h) => h.clause)))
        .catch(() => current && setHits([]))
        .finally(() => current && setSearching(false));
    }, 300);
    return () => {
      current = false;
      clearTimeout(timer);
    };
  }, [query, policy.id]);

  const counts = useMemo(() => Object.fromEntries(FILTERS.map((f) => [f.key, clauses.filter(f.match).length])), [clauses]);
  const active = FILTERS.find((f) => f.key === filter) ?? FILTERS[0]!;
  const shown = hits ?? clauses.filter(active.match);

  if (!clauses.length) return <p className="panel muted">{t("no_clauses")}</p>;

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.2 }}>
      <div className="mb-4 flex flex-wrap items-center gap-2.5">
        <label className="flex min-w-[220px] flex-1 items-center gap-2 rounded-[10px] border border-line bg-surface px-3 focus-within:border-sage">
          <Icon name="search" className="h-4 w-4 flex-none text-muted" />
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t("search_clauses")}
            aria-label={t("search_clauses")}
            title={t("search_hint")}
            className="min-w-0 flex-1 border-0 bg-transparent py-2.5 text-fg outline-none"
          />
          {searching && <span className="text-[12px] text-muted">{t("searching")}</span>}
        </label>
        {!hits && (
          <div className="flex flex-wrap gap-1.5" role="group" aria-label={t("policy_views")}>
            {FILTERS.filter((f) => f.key === "all" || counts[f.key]).map((f) => (
              <button
                key={f.key}
                type="button"
                aria-pressed={filter === f.key}
                onClick={() => onFilter(f.key)}
                className={`rounded-full border px-3 py-1.5 text-[13px] ${filter === f.key ? "border-sage bg-surface-2 text-fg" : "border-line text-muted hover:text-fg"}`}
              >
                {t(f.label)} <span className="num opacity-70">{counts[f.key]}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {shown.length === 0 ? (
        <p className="panel muted text-center">{t("no_results")}</p>
      ) : (
        <div className="grid gap-3">
          <AnimatePresence initial={false} mode="popLayout">
            {shown.map((c, i) => (
              <ClauseCard key={c.id} clause={c} timeline={policy.timeline} best={!!hits && i === 0} focused={focusRef === c.ref} />
            ))}
          </AnimatePresence>
        </div>
      )}
    </motion.div>
  );
}
