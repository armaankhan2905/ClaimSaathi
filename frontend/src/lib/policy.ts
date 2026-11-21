import { useCallback, useEffect, useState } from "react";
import type { StringKey } from "../i18n/strings";
import { api, type Clause, type PolicyDetail, type WaitingStatus } from "./api";

export type PolicyTerms = {
  policy_name?: string | null;
  insurer?: string | null;
  policy_number?: string | null;
  policyholder?: string | null;
  policy_start?: string | null;
  policy_end?: string | null;
  first_policy_date?: string | null;
  sum_insured?: number | null;
  premium?: number | null;
  room_rent_limit?: string | null;
  icu_limit?: string | null;
  copayment?: string | null;
  policy_history?: { policy_number: string | null; start: string | null; end: string | null }[];
  addons?: string[];
  key_exclusions?: string[];
};

/** One policy with its terms, timeline and clauses; refreshes itself while it is being read. */
export function usePolicyDetail(policyId: number | null) {
  const [policy, setPolicy] = useState<PolicyDetail | null>(null);
  const [clauses, setClauses] = useState<Clause[] | null>(null);
  const [failed, setFailed] = useState(false);

  const load = useCallback(async () => {
    if (policyId == null) return;
    try {
      const [p, c] = await Promise.all([api.getPolicy(policyId), api.listClauses(policyId)]);
      setPolicy(p);
      setClauses(c);
      setFailed(false);
    } catch {
      setFailed(true);
    }
  }, [policyId]);

  useEffect(() => {
    setPolicy(null);
    setClauses(null);
    load();
  }, [load]);

  const running = policy?.analysis_status === "running" || policy?.status === "processing";
  useEffect(() => {
    if (!running) return;
    const id = setInterval(load, 2500);
    return () => clearInterval(id);
  }, [running, load]);

  return { policy, clauses, failed, reload: load };
}

export const CATEGORY_LABEL: Record<Clause["category"], StringKey> = {
  coverage: "cat1_coverage",
  exclusion: "cat1_exclusion",
  limit: "cat1_limit",
  waiting_period: "cat1_waiting_period",
  definition: "cat1_definition",
  condition: "cat1_condition",
  claim_process: "cat1_claim_process",
  grievance: "cat1_grievance",
  other: "cat1_other",
};

export const CATEGORY_CHIP: Record<Clause["category"], string> = {
  coverage: "ok",
  exclusion: "bad",
  limit: "warn",
  waiting_period: "sage",
  definition: "",
  condition: "",
  claim_process: "",
  grievance: "",
  other: "",
};

/** The waiting-period status for a clause, if that clause defines one. */
export function waitingFor(clause: Clause, timeline: PolicyDetail["timeline"]): WaitingStatus | undefined {
  return timeline?.waiting_periods.find((w) => w.clause_ref === clause.ref);
}
