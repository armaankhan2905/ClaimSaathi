import { useEffect, useId, useRef, useState, type ReactNode } from "react";
import { useI18n } from "../../i18n/I18nProvider";
import type { StringKey } from "../../i18n/strings";
import { api, type Complaint, type ComplaintFields, type Stage } from "../../lib/api";
import { Icon } from "../Icon";
import { STAGE_LINK, STAGES } from "./StartComplaint";

const GRIEVANCE_TYPES: ComplaintFields["grievance_type"][] = ["claim_rejected", "claim_partly_paid", "claim_delay", "policy_service", "other"];
const localIso = () => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
};

function Field({ label, children, full, hint }: { label: string; children: (id: string) => ReactNode; full?: boolean; hint?: string }) {
  const id = useId();
  return (
    <label className={`field ${full ? "sm:col-span-2" : ""}`} htmlFor={id}>
      {label}
      {children(id)}
      {hint && <small className="text-[12px] font-normal">{hint}</small>}
    </label>
  );
}

/** The letter as it will be sent, rebuilt by the server after every edit. */
export function LetterPreview({ letter }: { letter: Complaint["letter"] }) {
  return (
    <article className="rounded-2xl border border-line bg-paper px-5 py-5 font-[Georgia,'Times_New_Roman',serif] text-[14px] leading-relaxed text-paper-ink sm:px-7" aria-live="polite">
      <div className="mb-3 flex flex-wrap justify-between gap-2 font-sans text-[12px] opacity-75">
        <span>To: {letter.to}</span>
        <span>{letter.date}</span>
      </div>
      <p className="mb-3">
        <b>Subject:</b> {letter.subject}
      </p>
      {letter.paragraphs.map((p, i) => (
        <p key={i} className="mb-3">
          {p}
        </p>
      ))}
      {letter.grounds.length > 0 && (
        <>
          <p className="mb-1.5">{letter.grounds_intro}</p>
          <ol className="mb-3 grid gap-1.5 pl-5">
            {letter.grounds.map((g, i) => (
              <li key={i}>
                {g.text} {g.ref && <span className="cite">§{g.ref}</span>}
              </li>
            ))}
          </ol>
        </>
      )}
      {letter.ask && (
        <p className="mb-3">
          <b>{letter.ask_label}:</b> {letter.ask}
        </p>
      )}
      <p className="mb-3">{letter.closing_note}</p>
      {letter.attachments.length > 0 && (
        <p className="mb-3 text-[13px]">
          <b>Enclosures:</b>
          {letter.attachments.map((a, i) => (
            <span key={i} className="block">
              {i + 1}. {a}
            </span>
          ))}
        </p>
      )}
      {letter.sign_off && <p className="mb-1">{letter.sign_off}</p>}
      <p>
        {letter.contact.map((c, i) => (
          <span key={i} className="block">
            {c}
          </span>
        ))}
      </p>
    </article>
  );
}

export function ComplaintDraft({ complaint, onChange }: { complaint: Complaint; onChange: (c: Complaint) => void }) {
  const { t } = useI18n();
  const [fields, setFields] = useState<ComplaintFields>(complaint.fields);
  const [saveState, setSaveState] = useState<"idle" | "saving" | "saved" | "error">("idle");
  const [copied, setCopied] = useState(false);
  const [sending, setSending] = useState(false);
  const [sentOn, setSentOn] = useState(localIso());
  const [reference, setReference] = useState("");
  const [busy, setBusy] = useState<string | null>(null);
  const pending = useRef<Partial<ComplaintFields>>({});
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  // A different complaint (or a new stage) starts from the server's copy.
  useEffect(() => setFields(complaint.fields), [complaint.id, complaint.stage]); // eslint-disable-line react-hooks/exhaustive-deps

  async function flush() {
    clearTimeout(timer.current);
    const changes = pending.current;
    if (!Object.keys(changes).length) return complaint;
    pending.current = {};
    setSaveState("saving");
    try {
      const c = await api.updateComplaint(complaint.id, { fields: changes });
      onChange(c);
      setSaveState("saved");
      return c;
    } catch {
      pending.current = { ...changes, ...pending.current };
      setSaveState("error");
      return null;
    }
  }

  function set<K extends keyof ComplaintFields>(key: K, value: ComplaintFields[K]) {
    setFields((f) => ({ ...f, [key]: value }));
    pending.current = { ...pending.current, [key]: value };
    clearTimeout(timer.current);
    timer.current = setTimeout(flush, 700);
  }
  useEffect(() => () => clearTimeout(timer.current), []);

  async function setStage(stage: Stage) {
    await flush();
    onChange(await api.updateComplaint(complaint.id, { stage }));
  }

  async function copy() {
    const c = (await flush()) ?? complaint;
    await navigator.clipboard.writeText(c.letter_text).catch(() => {});
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  }

  async function download(what: "letter" | "package") {
    setBusy(what);
    await flush();
    await api.downloadComplaint(complaint.id, what, `ClaimSaathi-complaint-${what}.pdf`).catch(() => {});
    setBusy(null);
  }

  async function markSent() {
    setBusy("sent");
    await flush();
    try {
      onChange(await api.markSent(complaint.id, { sent_on: sentOn, reference }));
    } finally {
      setBusy(null);
    }
  }

  const stage = complaint.stage;
  const tookInsurerStepHere = complaint.history.some((e) => e.kind === "sent" && e.stage === "insurer");
  const mailto = `mailto:${encodeURIComponent(fields.to_email.trim())}?subject=${encodeURIComponent(complaint.letter.subject)}&body=${encodeURIComponent(complaint.letter_text)}`;
  const grounds = fields.grounds;

  return (
    <div className="grid gap-5">
      {/* Where it goes */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="muted text-[13px]">{t("comp_filing_to")}</span>
        <div className="seg flex-wrap" role="radiogroup" aria-label={t("comp_filing_to")}>
          {STAGES.map((s) => (
            <button
              key={s}
              type="button"
              role="radio"
              aria-checked={stage === s}
              className={`rounded-lg px-3 py-1.5 text-[13px] ${stage === s ? "bg-accent font-semibold text-accent-ink" : "text-muted hover:text-fg"}`}
              onClick={() => stage !== s && setStage(s)}
            >
              {t(`stage_${s}` as StringKey)}
            </button>
          ))}
        </div>
        {complaint.recommended_stage === stage && <span className="chip sage text-[11.5px]">{t("comp_recommended")}</span>}
      </div>

      <div className="grid items-start gap-5 lg:grid-cols-[1fr_1.05fr]">
        <form className="panel grid gap-4" onSubmit={(e) => e.preventDefault()} noValidate>
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h3>{t("comp_details")}</h3>
            <span className="muted text-[12.5px]" role="status">
              {saveState === "saving" ? t("saving") : saveState === "saved" ? t("saved") : saveState === "error" ? <span className="text-bad">{t("comp_err")}</span> : t("comp_prefilled")}
            </span>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <Field label={t("f_name")}>{(id) => <input id={id} className="input" value={fields.name} onChange={(e) => set("name", e.target.value)} autoComplete="name" />}</Field>
            <Field label={t("f_phone")}>{(id) => <input id={id} className="input" value={fields.phone} onChange={(e) => set("phone", e.target.value)} inputMode="tel" autoComplete="tel" />}</Field>
            <Field label={t("f_email")}>{(id) => <input id={id} className="input" value={fields.email} onChange={(e) => set("email", e.target.value)} type="email" autoComplete="email" />}</Field>
            <Field label={t("f_insurer")}>{(id) => <input id={id} className="input" value={fields.insurer} onChange={(e) => set("insurer", e.target.value)} />}</Field>
            <Field label={t("f_address")} full>{(id) => <input id={id} className="input" value={fields.address} onChange={(e) => set("address", e.target.value)} autoComplete="street-address" />}</Field>
            <Field label={t("f_policy")}>{(id) => <input id={id} className="input" value={fields.policy_number} onChange={(e) => set("policy_number", e.target.value)} />}</Field>
            <Field label={t("f_claim")}>{(id) => <input id={id} className="input" value={fields.claim_number} onChange={(e) => set("claim_number", e.target.value)} />}</Field>
            <Field label={t("f_amount")}>
              {(id) => <input id={id} className="input num" value={fields.amount ?? ""} inputMode="numeric" onChange={(e) => set("amount", e.target.value.replace(/\D/g, "") ? Number(e.target.value.replace(/\D/g, "")) : null)} />}
            </Field>
            <Field label={t("f_type")}>
              {(id) => (
                <select id={id} className="input py-2" value={fields.grievance_type} onChange={(e) => set("grievance_type", e.target.value as ComplaintFields["grievance_type"])}>
                  {GRIEVANCE_TYPES.map((g) => (
                    <option key={g} value={g}>
                      {t(`gt_${g}` as StringKey)}
                    </option>
                  ))}
                </select>
              )}
            </Field>
            {stage === "insurer" && (
              <Field label={t("f_to_email")} full hint={t("f_to_email_hint")}>
                {(id) => <input id={id} className="input" value={fields.to_email} onChange={(e) => set("to_email", e.target.value)} type="email" placeholder="grievance@…" />}
              </Field>
            )}
          </div>

          {stage !== "insurer" && !tookInsurerStepHere && (
            <fieldset className="m-0 grid gap-3 rounded-xl border border-line p-3.5 sm:grid-cols-2">
              <legend className="px-1 text-[13px] font-semibold">{t("comp_earlier_title")}</legend>
              <Field label={t("f_earlier_date")}>
                {(id) => <input id={id} type="date" className="input" max={localIso()} value={fields.earlier_complaint_date ?? ""} onChange={(e) => set("earlier_complaint_date", e.target.value || null)} />}
              </Field>
              <Field label={t("f_earlier_ref")}>{(id) => <input id={id} className="input" value={fields.earlier_reference} onChange={(e) => set("earlier_reference", e.target.value)} />}</Field>
              {fields.situation !== "no_reply" && (
                <Field label={t("f_reply_date")}>
                  {(id) => <input id={id} type="date" className="input" max={localIso()} value={fields.insurer_reply_date ?? ""} onChange={(e) => set("insurer_reply_date", e.target.value || null)} />}
                </Field>
              )}
            </fieldset>
          )}

          <div className="grid gap-2">
            <h4 className="text-[14.5px] font-semibold">{t("grounds_title")}</h4>
            <p className="muted text-[12.5px]">{t("grounds_hint")}</p>
            <ol className="m-0 grid list-none gap-2.5 p-0">
              {grounds.map((g, i) => (
                <li key={i} className="grid grid-cols-[auto_1fr_auto] items-start gap-2">
                  <span className="num mt-2.5 w-5 text-right text-[13px] text-muted">{i + 1}.</span>
                  <div className="grid gap-1.5">
                    <textarea
                      className="input min-h-[84px] resize-y text-[14px] leading-snug"
                      value={g.text}
                      aria-label={`${t("grounds_title")} ${i + 1}`}
                      onChange={(e) => set("grounds", grounds.map((x, j) => (j === i ? { ...x, text: e.target.value } : x)))}
                    />
                    <label className="flex items-center gap-2 text-[12.5px] text-muted">
                      {t("ground_ref")}
                      <input
                        className="input w-24 px-2 py-1 font-mono text-[12.5px]"
                        value={g.ref ?? ""}
                        onChange={(e) => set("grounds", grounds.map((x, j) => (j === i ? { ...x, ref: e.target.value || null } : x)))}
                      />
                    </label>
                  </div>
                  <button type="button" className="btn mt-1 px-2 py-1.5 hover:text-bad" aria-label={t("ground_remove", { n: i + 1 })} onClick={() => set("grounds", grounds.filter((_, j) => j !== i))}>
                    <Icon name="close" className="h-4 w-4" />
                  </button>
                </li>
              ))}
            </ol>
            <button type="button" className="btn justify-self-start px-3 py-1.5 text-[13px]" onClick={() => set("grounds", [...grounds, { text: "", ref: null }])}>
              <Icon name="plus" className="h-4 w-4" />
              {t("ground_add")}
            </button>
          </div>

          <Field label={t("f_ask")} full>
            {(id) => <textarea id={id} className="input min-h-[84px] resize-y text-[14px] leading-snug" value={fields.ask} onChange={(e) => set("ask", e.target.value)} />}
          </Field>

          <div className="grid gap-2">
            <h4 className="text-[14.5px] font-semibold">{t("attach_title")}</h4>
            {complaint.has_report && (
              <label className="flex items-center gap-2.5 rounded-[10px] bg-surface-2 px-3 py-2 text-[14px]">
                <input type="checkbox" checked={fields.include_report} onChange={(e) => set("include_report", e.target.checked)} className="accent-[var(--accent)]" />
                <Icon name="shield" className="h-4 w-4 text-accent" />
                {t("attach_report")}
              </label>
            )}
            {complaint.attachment_options.map((d) => (
              <label key={d.id} className="flex items-center gap-2.5 rounded-[10px] bg-surface-2 px-3 py-2 text-[14px]">
                <input
                  type="checkbox"
                  checked={fields.attachments.includes(d.id)}
                  onChange={(e) => set("attachments", e.target.checked ? [...fields.attachments, d.id] : fields.attachments.filter((x) => x !== d.id))}
                  className="accent-[var(--accent)]"
                />
                <Icon name="doc" className="h-4 w-4 flex-none text-accent" />
                <span className="min-w-0 flex-1 truncate" title={d.filename}>
                  {d.filename}
                </span>
                <small className="text-[12px] text-muted">{t(`kind_${d.kind}` as StringKey)}</small>
              </label>
            ))}
            {!complaint.has_report && !complaint.attachment_options.length && <p className="muted text-[13px]">{t("attach_empty")}</p>}
          </div>
        </form>

        <div className="grid gap-3 lg:sticky lg:top-20">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h3>{t("preview_title")}</h3>
            <button type="button" className="btn px-3 py-1.5 text-[13px]" onClick={() => copy()}>
              <Icon name={copied ? "check" : "copy"} className="h-4 w-4" />
              {copied ? t("copied") : t("copy_text")}
            </button>
          </div>
          <LetterPreview letter={complaint.letter} />
          <p className="muted text-[12.5px]">{t("letter_english_note")}</p>

          <section className="panel grid gap-3" aria-labelledby="send-title">
            <h3 id="send-title">{t("how_to_send")}</h3>
            <p className="muted text-[13.5px]">{t(stage === "insurer" ? "email_hint" : stage === "bima_bharosa" ? "bb_steps" : "om_steps")}</p>
            <div className="flex flex-wrap gap-2">
              {stage === "insurer" ? (
                <a href={mailto} className="btn primary" onClick={() => flush()}>
                  <Icon name="mail" />
                  {t("email_insurer")}
                </a>
              ) : (
                <a href={STAGE_LINK[stage]} target="_blank" rel="noopener noreferrer" className="btn primary">
                  <Icon name="external" />
                  {t(stage === "bima_bharosa" ? "bb_open" : "om_open")}
                </a>
              )}
              <button type="button" className="btn" disabled={busy === "package"} onClick={() => download("package")}>
                <Icon name="download" />
                {t("dl_package")}
              </button>
              <button type="button" className="btn" disabled={busy === "letter"} onClick={() => download("letter")}>
                <Icon name="doc" />
                {t("dl_letter")}
              </button>
            </div>
            <p className="muted text-[12px]">{t("dl_package_hint")}</p>

            <div className="border-t border-line pt-3">
              {sending ? (
                <div className="grid gap-3 sm:grid-cols-2">
                  <Field label={t("sent_on")}>{(id) => <input id={id} type="date" className="input" max={localIso()} value={sentOn} onChange={(e) => setSentOn(e.target.value)} />}</Field>
                  <Field label={t("sent_ref")}>{(id) => <input id={id} className="input" value={reference} onChange={(e) => setReference(e.target.value)} maxLength={80} />}</Field>
                  <div className="flex flex-wrap gap-2 sm:col-span-2">
                    <button type="button" className="btn primary" disabled={busy === "sent" || !sentOn} onClick={() => markSent()}>
                      <Icon name="check" />
                      {t("confirm_sent")}
                    </button>
                    <button type="button" className="btn" onClick={() => setSending(false)}>
                      {t("cancel")}
                    </button>
                  </div>
                </div>
              ) : (
                <button type="button" className="btn" onClick={() => setSending(true)}>
                  <Icon name="check" />
                  {t("mark_sent")}
                </button>
              )}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
