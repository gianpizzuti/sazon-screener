import { useMutation, useQueryClient } from "@tanstack/react-query";
import clsx from "clsx";
import { ArrowRight, Brain, Check, Hourglass, Languages, ListChecks, MessageCircle, Plus, Quote, Send } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";

import { Button, Card, CardTitle, Chip, PageHeader, StatusBadge } from "../components/ui";
import { type Analysis, api, type ScreeningData } from "../lib/api";
import { AVAILABILITY, SCHEDULE, experience, shortDate, titleCase } from "../lib/format";
import { useCandidate } from "../lib/hooks";

type Session = { id: string; quick: string[]; analysis: Analysis | null; silent: boolean };
const STORAGE_KEY = "try-agent-session";

const CHECKLIST: { label: string; value: (d: ScreeningData) => string | null }[] = [
  { label: "Name", value: (d) => d.full_name },
  { label: "Driver's license", value: (d) => (d.license_status ? { yes: "Yes", no: "No", in_progress: "In progress" }[d.license_status] : null) },
  { label: "City · zone", value: (d) => (d.in_service_area === false ? `${d.location_raw} (outside)` : d.city ? `${d.city}${d.zone ? ` · ${d.zone}` : ""}` : null) },
  { label: "Availability", value: (d) => d.availability.map((a) => AVAILABILITY[a]).join(", ") || null },
  { label: "Shift", value: (d) => d.preferred_schedule.map((s) => SCHEDULE[s]).join(", ") || null },
  { label: "Experience", value: (d) => (d.experience_months === null ? null : `${experience(d.experience_months)}${d.experience_platforms.length ? ` · ${d.experience_platforms.join(", ")}` : ""}`) },
  { label: "Start date", value: (d) => (d.start_date ? shortDate(d.start_date) : null) },
];

function loadSession(): Session | null {
  try { const raw = sessionStorage.getItem(STORAGE_KEY); return raw ? JSON.parse(raw) : null; } catch { return null; }
}

function TypingDots() {
  return (
    <div className="flex items-center gap-1 rounded-2xl rounded-tl-md bg-surface-2 px-4 py-3" aria-label="Sofía is typing">
      {[0, 1, 2].map((i) => (
        <motion.span key={i} className="size-1.5 rounded-full bg-ink-3" animate={{ y: [0, -4, 0], opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 0.9, repeat: Infinity, delay: i * 0.15 }} />
      ))}
    </div>
  );
}

export function TryAgentPage() {
  const client = useQueryClient();
  const [session, setSession] = useState<Session | null>(loadSession);
  const [language, setLanguage] = useState<"es" | "en">("es");
  const [text, setText] = useState("");
  const [pending, setPending] = useState<string | null>(null);
  const { data: detail } = useCandidate(session?.id);
  const scroller = useRef<HTMLDivElement>(null);

  useEffect(() => { try { session ? sessionStorage.setItem(STORAGE_KEY, JSON.stringify(session)) : sessionStorage.removeItem(STORAGE_KEY); } catch { /* ignore */ } }, [session]);
  useEffect(() => { scroller.current?.scrollTo({ top: scroller.current.scrollHeight, behavior: "smooth" }); }, [detail?.transcript.length, pending]);

  const start = useMutation({
    mutationFn: () => api.start(language),
    onSuccess: (r) => { setSession({ id: r.conversation_id, quick: r.messages.at(-1)?.quick_replies ?? [], analysis: null, silent: false }); client.invalidateQueries({ queryKey: ["candidates"] }); },
  });
  const send = useMutation({
    mutationFn: (message: string) => api.send(session!.id, message),
    onMutate: (message) => setPending(message),
    onSuccess: async (r) => {
      setSession((s) => s && { ...s, quick: r.messages.at(-1)?.quick_replies ?? [], analysis: r.analysis, silent: !r.messages.length });
      await client.invalidateQueries({ queryKey: ["candidate", session!.id] });
      client.invalidateQueries({ queryKey: ["candidates"] });
    },
    onSettled: () => setPending(null),
  });

  const submit = (message: string) => {
    if (!message.trim() || send.isPending) return;
    setText("");
    send.mutate(message.trim());
  };

  const transcript = detail?.transcript ?? [];
  const last = transcript.at(-1);
  const showQuick = !!session?.quick.length && last?.role === "agent" && last.meta.kind !== "followup" && !send.isPending;
  const finished = detail && !["in_progress", "awaiting_reply", "abandoned"].includes(detail.row.status);
  const a = session?.analysis;

  return (
    <div>
      <PageHeader
        title="Try the agent"
        subtitle="You are the candidate. This web chat calls the same API a WhatsApp webhook or a voice agent would. Go silent and use the demo clock to see the reminders."
        aside={
          <div className="flex items-center gap-2">
            <div role="radiogroup" aria-label="Opening language" className="flex rounded-xl bg-surface p-1 ring-1 ring-line">
              {(["es", "en"] as const).map((l) => (
                <button key={l} role="radio" aria-checked={language === l} onClick={() => setLanguage(l)}
                  className={clsx("min-h-8 cursor-pointer rounded-lg px-3 text-sm font-medium", language === l ? "bg-ink text-surface" : "text-ink-2 hover:text-ink")}>{l.toUpperCase()}</button>
              ))}
            </div>
            <Button variant={session ? "secondary" : "primary"} icon={Plus} loading={start.isPending} onClick={() => start.mutate()}>
              {session ? "New conversation" : "Start conversation"}
            </Button>
          </div>
        }
      />

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.25fr)_minmax(0,1fr)]">
        <div className="flex h-[640px] flex-col overflow-hidden rounded-[28px] border border-line bg-surface shadow-xl shadow-black/5">
          <div className="flex items-center gap-3 border-b border-line bg-surface-2/60 px-5 py-3.5">
            <div className="relative">
              <div className="grid size-10 place-items-center rounded-full bg-brand font-display text-white">S</div>
              <span className="absolute right-0 bottom-0 size-3 rounded-full bg-emerald-500 ring-2 ring-surface" aria-hidden />
            </div>
            <div className="leading-tight">
              <div className="font-semibold text-ink">Sofía · Grupo Sazón</div>
              <div className="text-xs text-ink-3">AI assistant · usually replies in a few seconds</div>
            </div>
            {detail && <div className="ml-auto"><StatusBadge status={detail.row.status} size="sm" /></div>}
          </div>

          <div ref={scroller} className="flex-1 space-y-3 overflow-y-auto px-5 py-5" aria-live="polite">
            {!session && (
              <div className="grid h-full place-items-center text-center">
                <div>
                  <div className="mx-auto mb-3 grid size-14 place-items-center rounded-2xl bg-brand-soft"><MessageCircle className="size-6 text-brand" /></div>
                  <p className="font-medium text-ink">Apply as a delivery driver</p>
                  <p className="mt-1 text-sm text-ink-3">Start a conversation to receive Sofía's first message.</p>
                </div>
              </div>
            )}
            <AnimatePresence initial={false}>
              {transcript.map((m, i) => {
                const agent = m.role === "agent";
                return (
                  <motion.div key={i} layout initial={{ opacity: 0, y: 10, scale: 0.98 }} animate={{ opacity: 1, y: 0, scale: 1 }} transition={{ duration: 0.25 }}
                    className={clsx("flex", agent ? "justify-start" : "justify-end")}>
                    <div className={clsx("max-w-[82%] rounded-2xl px-4 py-2.5 text-[15px] leading-relaxed whitespace-pre-line",
                      agent ? m.meta.kind === "followup" ? "rounded-tl-md bg-violet-50 text-ink ring-1 ring-violet-500/20 dark:bg-violet-400/10" : "rounded-tl-md bg-surface-2 text-ink"
                        : "rounded-tr-md bg-brand-btn text-white")}>
                      {m.text}
                      {m.meta.kind === "followup" && <div className="mt-1 flex items-center gap-1 text-xs text-violet-700 dark:text-violet-300"><Hourglass className="size-3" />Automatic reminder · you went silent</div>}
                    </div>
                  </motion.div>
                );
              })}
              {pending && (
                <motion.div key="pending" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex justify-end">
                  <div className="max-w-[82%] rounded-2xl rounded-tr-md bg-brand-btn px-4 py-2.5 text-[15px] text-white opacity-80">{pending}</div>
                </motion.div>
              )}
              {send.isPending && <motion.div key="typing" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex"><TypingDots /></motion.div>}
            </AnimatePresence>
            {session?.silent && <p className="text-center text-xs text-ink-3">Sofía doesn't reply: the conversation is closed and there was nothing to answer.</p>}
            {finished && (
              <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="flex justify-center pt-2">
                <Link to={`/candidates/${session!.id}`} className="inline-flex items-center gap-1.5 rounded-full bg-ink px-4 py-2 text-sm font-medium text-surface">
                  See it as a recruiter<ArrowRight className="size-4" />
                </Link>
              </motion.div>
            )}
          </div>

          {session && (
            <div className="border-t border-line p-3">
              <AnimatePresence>
                {showQuick && (
                  <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="mb-2 flex flex-wrap gap-1.5">
                    {session.quick.map((q) => (
                      <button key={q} onClick={() => submit(q)} className="min-h-9 cursor-pointer rounded-full border border-brand/40 bg-brand-soft px-3.5 text-[13px] font-medium text-brand-ink transition hover:bg-brand hover:text-white">{q}</button>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
              <form onSubmit={(e) => { e.preventDefault(); submit(text); }} className="flex items-center gap-2">
                <label htmlFor="msg" className="sr-only">Your message</label>
                <input id="msg" value={text} onChange={(e) => setText(e.target.value)} placeholder="Write as the candidate…" autoComplete="off"
                  className="h-11 flex-1 rounded-full border border-line bg-surface-2 px-4 text-[15px] text-ink placeholder:text-ink-3 focus:border-brand/60 focus:outline-none" />
                <button type="submit" disabled={!text.trim() || send.isPending} aria-label="Send"
                  className="grid size-11 cursor-pointer place-items-center rounded-full bg-brand-btn text-white transition active:scale-95 disabled:opacity-40">
                  <Send className="size-4" />
                </button>
              </form>
            </div>
          )}
        </div>

        <div className="space-y-6">
          <Card>
            <CardTitle icon={ListChecks} aside={detail && <span className="num text-sm text-ink-3">{CHECKLIST.filter((c) => c.value(detail.data)).length}/7</span>}>Screening progress</CardTitle>
            <ul className="space-y-1">
              {CHECKLIST.map((item) => {
                const value = detail ? item.value(detail.data) : null;
                return (
                  <li key={item.label} className="flex items-center gap-3 rounded-xl px-2 py-2">
                    <motion.span className={clsx("grid size-6 shrink-0 place-items-center rounded-full", value ? "bg-emerald-600 text-white" : "bg-surface-2 ring-1 ring-line")}
                      animate={value ? { scale: [0.6, 1.15, 1] } : { scale: 1 }} transition={{ duration: 0.35 }}>
                      {value && <Check className="size-3.5" strokeWidth={3} />}
                    </motion.span>
                    <span className="w-32 shrink-0 text-sm text-ink-3">{item.label}</span>
                    <AnimatePresence mode="wait">
                      <motion.span key={value ?? "empty"} initial={{ opacity: 0, x: -4 }} animate={{ opacity: 1, x: 0 }} className={clsx("truncate text-sm", value ? "font-medium text-ink" : "text-ink-3")}>
                        {value ?? "–"}
                      </motion.span>
                    </AnimatePresence>
                  </li>
                );
              })}
            </ul>
          </Card>

          <Card>
            <CardTitle icon={Brain}>What Sofía understood</CardTitle>
            {!a ? (
              <p className="text-sm text-ink-3">Send a message to see how it's interpreted: intents, language, sentiment and every value with the words it came from.</p>
            ) : (
              <motion.div key={JSON.stringify(a.evidence)} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="space-y-3">
                <div className="flex flex-wrap gap-1.5">
                  {a.intents.map((i) => <Chip key={i}>{titleCase(i)}</Chip>)}
                  <Chip><Languages className="size-3" />{a.language.toUpperCase()}{a.language_is_clear ? "" : " · no signal"}</Chip>
                  <Chip>Sentiment: {a.sentiment}</Chip>
                  {a.faq_id && <Chip>FAQ: {titleCase(a.faq_id)}</Chip>}
                </div>
                {a.evidence.length ? a.evidence.map((e, i) => (
                  <div key={i} className="flex gap-2 text-sm text-ink-2"><Quote className="mt-0.5 size-3.5 shrink-0 text-brand" /><span><span className="text-ink-3">{titleCase(e.field)}:</span> “{e.quote}”</span></div>
                )) : <p className="text-sm text-ink-3">No screening data in this message.</p>}
                <p className="text-xs text-ink-3">Every value must quote your words, or it is discarded. The model reads; the rules decide.</p>
              </motion.div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}
