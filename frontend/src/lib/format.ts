import type { Lang } from "../i18n/strings";

const locale = (lang: Lang) => (lang === "hi" ? "hi-IN" : "en-IN");

/** ₹5,00,000 (Indian digit grouping). */
export function formatRupees(amount: number | null | undefined, lang: Lang): string {
  if (amount == null) return "—";
  return new Intl.NumberFormat(locale(lang), { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(amount);
}

/** 11 Mar 2026 */
export function formatDate(iso: string | null | undefined, lang: Lang): string {
  if (!iso) return "—";
  const d = new Date(`${iso}T00:00:00`);
  return new Intl.DateTimeFormat(locale(lang), { day: "2-digit", month: "short", year: "numeric" }).format(d);
}

/** Mar 2022 */
export function formatMonth(iso: string | null | undefined, lang: Lang): string {
  if (!iso) return "—";
  const d = new Date(`${iso}T00:00:00`);
  return new Intl.DateTimeFormat(locale(lang), { month: "short", year: "numeric" }).format(d);
}
