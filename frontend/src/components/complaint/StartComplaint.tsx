import { useId, useState } from "react";
import { Link } from "react-router";
import { useI18n } from "../../i18n/I18nProvider";
import type { StringKey } from "../../i18n/strings";
import type { Claim, Situation, Stage } from "../../lib/api";
import { formatDate, formatRupees } from "../../lib/format";
import { Icon } from "../Icon";

export const SITUATIONS: Situation[] = ["not_yet", "unsatisfied", "no_reply", "bb_unresolved"];
export const STAGE_OF: Record<Situation, Stage> = { not_yet: "insurer", unsatisfied: "bima_bharosa", no_reply: "bima_bharosa", bb_unresolved: "ombudsman" };
export const STAGES: Stage[] = ["insurer", "bima_bharosa", "ombudsman"];
export const STAGE_LINK: Partial<Record<Stage, string>> = {
  bima_bharosa: "https://bimabharosa.irdai.gov.in/",
  ombudsman: "https://www.cioins.co.in/",
};

/** The three levels of a complaint, the recommended one highlighted. */
export function RouteCards({ current }: { current: Stage }) {
  const { t } = useI18n();
  return (
    <ol className="m-0 grid list-none gap-3 p-0 md:grid-cols-3">
      {STAGES.map((s, i) => {
        const now = s === current;
        return (
          <li key={s} className={`rounded-2xl border p-4 ${now ? "border-accent bg-surface shadow-[var(--shadow)]" : "border-line bg-surface-2"}`} aria-current={now ? "step" : undefined}>
            <span className={`chip ${now ? "sage" : ""} text-[11.5px]`}>{t(`stage_step_${i + 1}` as StringKey)}</span>
            <h3 className="mt-2">{t(`stage_${s}` as StringKey)}</h3>
            <p className="muted mt-1 text-[13.5px]">{t(`stage_${s}_text` as StringKey)}</p>
            {STAGE_LINK[s] && (
              <a href={STAGE_LINK[s]} target="_blank" rel="noopener noreferrer" className="mt-2 inline-flex items-center gap-1 text-[13px]">
                {new URL(STAGE_LINK[s]!).hostname.replace("www.", "")}
                <Icon name="external" className="h-3.5 w-3.5" />
              </a>
            )}
          </li>
        );
      })}
    </ol>
  );
}

export function StartComplaint({ claims, initialClaim, onStart, busy }: {
  claims: Claim[];
  initialClaim: number | null;
  onStart: (claimId: number | null, situation: Situation) => void;
  busy: boolean;
}) {
  const { t, lang } = useI18n();
  const checked = claims.filter((c) => c.status === "ready" && c.findings);
  const [situation, setSituation] = useState<Situation>("not_yet");
  const [claimId, setClaimId] = useState<number | null>(initialClaim ?? checked[0]?.id ?? null);
  const pickId = useId();
  const claim = checked.find((c) => c.id === claimId) ?? null;
  const fd = claim?.findings;
  // Same grounds the draft will list (see backend complaints.grounds_from_findings).
  let grounds = 0;
  let continuity = false;
  for (const r of fd?.rows ?? []) {
    if (r.status === "contradicted") {
      grounds += 1 + (r.code === "waiting_over_counted_wrongly" && r.data.insurer_counted_from ? 1 : 0);
      if (r.data.periods_checked && !r.data.breaks?.length && !continuity) {
        grounds += 1;
        continuity = true;
      }
    } else if (r.status === "unclear" && r.question_en) grounds += 1;
  }
  const refs = new Set(fd?.rows.map((r) => r.policy_quote?.ref ?? r.clause_ref).filter(Boolean)).size;
  const docs = fd?.checklist.filter((c) => c.have).length ?? 0;

  return (
    <div className="grid gap-5">
      <div className="grid items-start gap-4 lg:grid-cols-2">
        <fieldset className="panel m-0 grid gap-2.5">
          <legend className="float-left mb-1 w-full font-display text-[17px] font-semibold">{t("comp_where")}</legend>
          {SITUATIONS.map((s) => (
            <label
              key={s}
              className={`flex cursor-pointer items-start gap-3 rounded-xl border px-3.5 py-3 text-[14.5px] transition-colors ${
                situation === s ? "border-accent bg-[var(--accent-soft)]" : "border-line hover:border-accent"
              }`}
            >
              <input type="radio" name="situation" value={s} checked={situation === s} onChange={() => setSituation(s)} className="mt-1 accent-[var(--accent)]" />
              <span>
                <b className="block font-semibold">{t(`sit_${s}` as StringKey)}</b>
                <small className="text-[12.5px] text-muted">{t(`sit_${s}_hint` as StringKey)}</small>
              </span>
            </label>
          ))}
        </fieldset>

        <div className="panel grid gap-3.5">
          <h3>{t("comp_from_check")}</h3>
          {checked.length ? (
            <>
              <label className="field" htmlFor={pickId}>
                {t("comp_which_check")}
                <select id={pickId} className="input py-2" value={claimId ?? ""} onChange={(e) => setClaimId(e.target.value ? Number(e.target.value) : null)}>
                  {checked.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.facts?.claim_number ?? `#${c.id}`}
                      {c.facts?.treatment ? ` · ${c.facts.treatment}` : ""}
                    </option>
                  ))}
                  <option value="">{t("comp_no_check")}</option>
                </select>
              </label>
              {claim && (
                <>
                  <div className="num grid grid-cols-3 gap-2 text-center">
                    {[
                      [grounds, "comp_count_grounds"],
                      [docs, "comp_count_docs"],
                      [refs, "comp_count_refs"],
                    ].map(([n, k]) => (
                      <div key={k as string} className="rounded-xl bg-surface-2 px-2 py-3">
                        <b className="block font-display text-2xl text-accent">{n as number}</b>
                        <span className="text-[12px] text-muted">{t(k as StringKey)}</span>
                      </div>
                    ))}
                  </div>
                  <p className="rounded-[10px] bg-surface-2 px-3 py-2 text-[13px] text-muted">
                    {t("comp_check_summary", {
                      claim: claim.facts?.claim_number ?? "—",
                      amount: claim.facts?.claimed_amount ? formatRupees(claim.facts.claimed_amount, lang) : "—",
                      date: formatDate(claim.facts?.letter_date, lang),
                    })}
                  </p>
                </>
              )}
            </>
          ) : (
            <div className="grid gap-3">
              <p className="muted text-[14px]">{t("comp_no_checks_hint")}</p>
              <Link to="/rejection" className="btn justify-self-start">
                <Icon name="search" />
                {t("comp_go_check")}
              </Link>
            </div>
          )}
          <button type="button" className="btn primary justify-self-start" disabled={busy} onClick={() => onStart(claim ? claim.id : null, situation)}>
            {t("comp_start")}
            <Icon name="arrow" />
          </button>
        </div>
      </div>
      <RouteCards current={STAGE_OF[situation]} />
    </div>
  );
}
