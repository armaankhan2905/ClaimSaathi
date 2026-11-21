import { AnimatePresence, motion } from "motion/react";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { useI18n } from "../../i18n/I18nProvider";
import type { StringKey } from "../../i18n/strings";
import { api, ApiError, type ChatMessage, type PolicyDetail } from "../../lib/api";
import { Icon } from "../Icon";

const SUGGESTIONS: Record<"health" | "motor", StringKey[]> = {
  health: ["sq_health_1", "sq_health_2", "sq_health_3", "sq_health_4", "sq_health_5", "sq_health_6"],
  motor: ["sq_motor_1", "sq_motor_2", "sq_motor_3", "sq_motor_4"],
};

const ANSWER_CHIP: Record<string, { key: StringKey; cls: string }> = {
  answered: { key: "at_answered", cls: "ok" },
  not_in_policy: { key: "at_not_in_policy", cls: "warn" },
  needs_more_info: { key: "at_needs_more_info", cls: "sage" },
  search_only: { key: "at_search_only", cls: "" },
};

function Typing() {
  const { t } = useI18n();
  return (
    <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="flex max-w-[82%] items-center gap-2.5 self-start rounded-[14px] rounded-bl-[4px] border border-line bg-surface-2 px-3.5 py-3 text-[13.5px] text-muted" role="status">
      <span className="flex gap-1" aria-hidden="true">
        {[0, 1, 2].map((i) => (
          <motion.span key={i} className="h-1.5 w-1.5 rounded-full bg-accent" animate={{ opacity: [0.3, 1, 0.3] }} transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }} />
        ))}
      </span>
      {t("thinking")}
    </motion.div>
  );
}

function Bubble({ msg, onOpenClause, onAsk }: { msg: ChatMessage; onOpenClause: (ref: string) => void; onAsk: (q: string) => void }) {
  const { t } = useI18n();
  if (msg.role === "user")
    return (
      <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="max-w-[82%] self-end rounded-[14px] rounded-br-[4px] bg-accent px-3.5 py-3 text-[14.5px] whitespace-pre-wrap text-accent-ink">
        <span className="sr-only">{t("you")}: </span>
        {msg.content}
      </motion.div>
    );

  const chip = ANSWER_CHIP[msg.answer_type ?? "answered"] ?? ANSWER_CHIP.answered!;
  const text = msg.answer_type === "search_only" ? t("search_only_intro") : msg.content || (msg.answer_type === "not_in_policy" ? t("not_in_policy_default") : "");
  return (
    <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="grid max-w-[88%] gap-2.5 self-start rounded-[14px] rounded-bl-[4px] border border-line bg-surface-2 px-3.5 py-3 text-[14.5px] max-sm:max-w-[96%]">
      <span className={`chip ${chip.cls} justify-self-start`}>
        <span className="dot" />
        {t(chip.key)}
      </span>
      {text && <p className="whitespace-pre-wrap">{text}</p>}
      {msg.citations.map((c) => (
        <blockquote key={c.ref} className="m-0 rounded-[10px] bg-paper px-3 py-2.5 font-[Georgia,'Times_New_Roman',serif] text-[13px] text-paper-ink">
          <button type="button" onClick={() => onOpenClause(c.ref)} className="mb-1 block font-mono text-[11px] text-accent hover:underline" aria-label={t("open_clause", { ref: c.ref })}>
            §{c.ref} · {c.title} →
          </button>
          “{c.quote}”
        </blockquote>
      ))}
      {msg.follow_ups.length > 0 && (
        <div className="flex flex-wrap gap-1.5 pt-0.5">
          {msg.follow_ups.map((f) => (
            <button key={f} type="button" onClick={() => onAsk(f)} className="rounded-full border border-line bg-surface px-2.5 py-1 text-left text-[12.5px] hover:border-sage">
              {f}
            </button>
          ))}
        </div>
      )}
    </motion.div>
  );
}

export function AskTab({ policy, onOpenClause }: { policy: PolicyDetail; onOpenClause: (ref: string) => void }) {
  const { t, lang } = useI18n();
  const [messages, setMessages] = useState<ChatMessage[] | null>(null);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<StringKey | null>(null);
  const scroller = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setMessages(null);
    api.getChat(policy.id).then(setMessages).catch(() => setMessages([]));
  }, [policy.id]);

  useEffect(() => {
    scroller.current?.scrollTo({ top: scroller.current.scrollHeight, behavior: "smooth" });
  }, [messages, sending]);

  async function ask(question: string) {
    const q = question.trim();
    if (!q || sending) return;
    setError(null);
    setSending(true);
    setInput("");
    const pending: ChatMessage = { id: -Date.now(), role: "user", content: q, lang, answer_type: null, citations: [], follow_ups: [], mode: null, created_at: "" };
    setMessages((m) => [...(m ?? []), pending]);
    try {
      const [question_, answer] = await api.ask(policy.id, q, lang);
      setMessages((m) => [...(m ?? []).filter((x) => x.id !== pending.id), question_!, answer!]);
    } catch (e) {
      setMessages((m) => (m ?? []).filter((x) => x.id !== pending.id));
      setInput(q); // give the question back so it can be sent again
      setError(e instanceof ApiError && e.message === "no_clauses" ? "ask_no_clauses" : e instanceof ApiError && e.status === 0 ? "err_network" : "ask_error");
    } finally {
      setSending(false);
      inputRef.current?.focus();
    }
  }

  async function clear() {
    await api.clearChat(policy.id).catch(() => {});
    setMessages([]);
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    ask(input);
  }

  const suggestions = SUGGESTIONS[policy.category === "motor" ? "motor" : "health"];

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.2 }} className="grid items-start gap-4 lg:grid-cols-[1fr_290px]">
      <section className="panel flex h-[min(72vh,760px)] min-h-[420px] flex-col gap-3.5 p-[18px] max-sm:p-3.5" aria-label={t("ask_title")}>
        <div ref={scroller} className="flex min-h-0 flex-1 flex-col gap-3.5 overflow-y-auto overscroll-contain pr-1 [scrollbar-gutter:stable]" aria-live="polite">
          {messages === null ? (
            <div className="h-16 w-2/3 animate-pulse rounded-xl bg-surface-2" />
          ) : messages.length === 0 && !sending ? (
            <div className="m-auto grid max-w-[46ch] justify-items-center gap-2 text-center">
              <span className="grid h-12 w-12 place-items-center rounded-2xl bg-[var(--accent-soft)] text-accent">
                <Icon name="search" className="h-6 w-6" />
              </span>
              <h3>{t("ask_title")}</h3>
              <p className="muted text-sm">{t("ask_empty")}</p>
            </div>
          ) : (
            <AnimatePresence initial={false}>
              {messages.map((m) => (
                <Bubble key={m.id} msg={m} onOpenClause={onOpenClause} onAsk={ask} />
              ))}
            </AnimatePresence>
          )}
          {sending && <Typing />}
        </div>

        {error && (
          <p role="alert" className="flex items-start gap-2 rounded-[10px] bg-[var(--bad-bg)] px-3 py-2 text-[13px] text-bad">
            <Icon name="alert" className="mt-0.5 h-4 w-4 flex-none" />
            {t(error)}
          </p>
        )}

        <form onSubmit={onSubmit} className="flex flex-none items-center gap-2 rounded-xl border border-line bg-bg py-1.5 pr-1.5 pl-3.5 focus-within:border-sage">
          <input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={t("ask_placeholder")}
            aria-label={t("ask_placeholder")}
            maxLength={1000}
            className="min-w-0 flex-1 border-0 bg-transparent py-2 text-fg outline-none"
          />
          <button type="submit" disabled={sending || !input.trim()} className="grid h-[38px] w-[38px] flex-none place-items-center rounded-[10px] bg-accent text-accent-ink disabled:opacity-40" aria-label={t("ask_send")} title={t("ask_send")}>
            <Icon name="arrow" className="h-[17px] w-[17px]" />
          </button>
        </form>
      </section>

      <aside className="grid gap-3">
        <div className="panel">
          <h3 className="mb-3">{t("try_asking")}</h3>
          <div className="grid gap-2">
            {suggestions.map((k) => (
              <button key={k} type="button" disabled={sending} onClick={() => ask(t(k))} className="rounded-[10px] border border-line bg-surface px-3 py-2.5 text-left text-[13.5px] hover:border-sage disabled:opacity-50">
                {t(k)}
              </button>
            ))}
          </div>
        </div>
        <p className="flex gap-2 rounded-[10px] bg-surface-2 px-3 py-2.5 text-[12.5px] text-muted">
          <Icon name="info" className="mt-0.5 h-4 w-4 flex-none text-accent" />
          {t("ask_note")}
        </p>
        {!!messages?.length && (
          <button type="button" className="btn justify-self-start px-3 py-1.5 text-[13px]" onClick={() => clear().catch(() => {})}>
            <Icon name="trash" />
            {t("clear_chat")}
          </button>
        )}
      </aside>
    </motion.div>
  );
}
