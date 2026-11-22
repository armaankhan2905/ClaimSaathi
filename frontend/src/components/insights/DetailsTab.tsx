import { motion } from "motion/react";
import type { ReactNode } from "react";
import { useI18n } from "../../i18n/I18nProvider";
import type { StringKey } from "../../i18n/strings";
import type { Clause, PolicyDetail } from "../../lib/api";
import { formatDate, formatRupees } from "../../lib/format";
import type { PolicyTerms } from "../../lib/policy";
import { Icon } from "../Icon";
import { CoverTimeline } from "./CoverTimeline";
import { WaitingChip, waitingBasisKey } from "./WaitingChip";

const MAX_ITEMS = 6;

function Cite({ refId, onOpen }: { refId: string; onOpen: (ref: string) => void }) {
  const { t } = useI18n();
  return (
    <button type="button" className="cite cursor-pointer hover:underline" onClick={() => onOpen(refId)} aria-label={t("open_clause", { ref: refId })}>
      §{refId}
    </button>
  );
}

function Fact({ label, value, sub }: { label: string; value: ReactNode; sub?: ReactNode }) {
  return (
    <div className="min-w-0 bg-surface px-4 py-3.5 shadow-[1px_1px_0_0_var(--line)]">
      <dt className="text-[12px] text-muted">{label}</dt>
      <dd className="m-0 mt-1 text-[15.5px] font-semibold">
        {value}
        {sub && <small className="mt-0.5 block text-[12px] font-normal text-muted">{sub}</small>}
      </dd>
    </div>
  );
}

function Column({ icon, cls, title, items, empty, onMore }: { icon: string; cls: string; title: string; items: ReactNode[]; empty: string; onMore?: () => void }) {
  const { t } = useI18n();
  return (
    <div className="panel min-w-0">
      <h3 className="mb-2.5 flex items-center gap-2 text-[14.5px]">
        <span className={`chip ${cls} px-[7px]`}>{icon}</span>
        {title}
      </h3>
      {items.length === 0 ? (
        <p className="muted text-[13.5px]">{empty}</p>
      ) : (
        <ul className="m-0 grid list-none gap-2 p-0 text-[13.5px]">
          {items.slice(0, MAX_ITEMS).map((item, i) => (
            <li key={i} className="flex items-baseline justify-between gap-2 border-b border-line pb-2 last:border-0 last:pb-0">
              {item}
            </li>
          ))}
        </ul>
      )}
      {items.length > MAX_ITEMS && onMore && (
        <button type="button" className="mt-2 text-[13px] font-semibold text-accent" onClick={onMore}>
          {t("more_n", { n: items.length - MAX_ITEMS })}
        </button>
      )}
    </div>
  );
}

export function DetailsTab({
  policy,
  clauses,
  onOpenClause,
  onShowCategory,
}: {
  policy: PolicyDetail;
  clauses: Clause[];
  onOpenClause: (ref: string) => void;
  onShowCategory: (category: Clause["category"]) => void;
}) {
  const { t, lang } = useI18n();
  const terms = (policy.terms ?? {}) as PolicyTerms;
  const timeline = policy.timeline;
  if (!policy.terms) return <p className="panel muted">{t("no_terms")}</p>;

  const isMotor = policy.category === "motor";
  const missing = <span className="font-normal text-muted">{t("not_found")}</span>;
  // When the documents don't state a value, use what the policy card already has.
  const sumInsured = terms.sum_insured ?? policy.sum_insured;
  const end = terms.policy_end ?? policy.renews_on;
  const coverSince = timeline?.continuous_since ?? policy.cover_since;
  const daysToEnd = end ? Math.round((new Date(`${end}T00:00:00`).getTime() - Date.now()) / 86_400_000) : null;
  const brk = timeline?.breaks[timeline.breaks.length - 1];

  const byCat = (c: Clause["category"]) => clauses.filter((x) => x.category === c);
  const clauseItem = (c: Clause) => (
    <>
      <span className="min-w-0">{c.title}</span>
      <Cite refId={c.ref} onOpen={onOpenClause} />
    </>
  );
  const exclusionClause = byCat("exclusion")[0];
  const notCovered = terms.key_exclusions?.length
    ? terms.key_exclusions.map((x) => (
        <>
          <span className="min-w-0">{x}</span>
          {exclusionClause && <Cite refId={exclusionClause.ref} onOpen={onOpenClause} />}
        </>
      ))
    : byCat("exclusion").map(clauseItem);

  const waiting = (timeline?.waiting_periods ?? []).map((w) => (
    <div className="grid w-full gap-1">
      <div className="flex items-baseline justify-between gap-2">
        <span className="min-w-0">
          {w.name} · <span className="num">{w.months === 1 ? t("month_1") : t("months_n", { n: w.months })}</span>
        </span>
        {w.clause_ref && <Cite refId={w.clause_ref} onOpen={onOpenClause} />}
      </div>
      <div className="flex flex-wrap items-center gap-1.5">
        <WaitingChip status={w} />
        <span className={`text-[12px] ${w.note ? "text-warn" : "text-muted"}`}>{t(waitingBasisKey(w) as StringKey)}</span>
      </div>
    </div>
  ));

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.2 }}>
      {/* Lines are drawn by each cell (not by gaps over a grey background), so a short last row
          leaves plain card colour instead of a grey block. */}
      <dl className="num m-0 grid grid-cols-[repeat(auto-fit,minmax(180px,1fr))] overflow-hidden rounded-xl border border-line bg-surface">
        <Fact
          label={isMotor ? t("idv") : t("sum_insured")}
          value={sumInsured ? formatRupees(sumInsured, lang) : missing}
          sub={terms.policyholder ? `${t("policyholder")}: ${terms.policyholder}` : undefined}
        />
        <Fact
          label={t("policy_period")}
          value={end ? (terms.policy_start ? `${formatDate(terms.policy_start, lang)} – ${formatDate(end, lang)}` : formatDate(end, lang)) : missing}
          sub={daysToEnd == null ? undefined : daysToEnd >= 0 ? t("renews_in", { n: daysToEnd }) : t("expired_on", { date: formatDate(end, lang) })}
        />
        <Fact
          label={t("continuous_cover")}
          value={coverSince ? formatDate(coverSince, lang) : missing}
          sub={brk ? <span className="text-bad">{t("break_found", { date: formatDate(brk.previous_end, lang) })}</span> : timeline?.continuous_since ? t("no_break") : undefined}
        />
        {!isMotor && (
          <Fact
            label={t("room_rent")}
            value={terms.room_rent_limit || missing}
            sub={terms.icu_limit ? t("icu", { v: terms.icu_limit }) : undefined}
          />
        )}
        <Fact label={t("copay")} value={terms.copayment || <span className="font-normal">{t("none_stated")}</span>} />
        <Fact label={t("premium")} value={terms.premium ? formatRupees(terms.premium, lang) : missing} sub={terms.premium ? t("per_year") : undefined} />
      </dl>

      <div className="mt-4 grid gap-3.5 sm:grid-cols-2 xl:grid-cols-4">
        <Column icon="✓" cls="ok" title={t("col_covered")} items={byCat("coverage").map(clauseItem)} empty={t("nothing_listed")} onMore={() => onShowCategory("coverage")} />
        <Column icon="✕" cls="bad" title={t("col_not_covered")} items={notCovered} empty={t("nothing_listed")} onMore={() => onShowCategory("exclusion")} />
        <Column icon="!" cls="warn" title={t("col_limits")} items={byCat("limit").map(clauseItem)} empty={t("nothing_listed")} onMore={() => onShowCategory("limit")} />
        <Column icon="⏱" cls="sage" title={t("col_waiting")} items={waiting} empty={t("nothing_listed")} onMore={() => onShowCategory("waiting_period")} />
      </div>

      {timeline && <CoverTimeline terms={terms} timeline={timeline} />}

      <p className="disclaimer flex gap-2">
        <Icon name="info" className="mt-0.5 h-4 w-4 flex-none" />
        {t("disclaimer")}
      </p>
    </motion.div>
  );
}
