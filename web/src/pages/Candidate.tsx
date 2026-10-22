import { useMutation, useQueryClient } from "@tanstack/react-query";
import clsx from "clsx";
import {
  ArrowLeft, Bot, Briefcase, CalendarCheck, CalendarClock, Check, ChevronDown, CircleCheck, CircleDot, CircleX, Download, Flag, Gavel, Hourglass, Languages,
  MapPin, MessageCircle, MoonStar, Quote, RefreshCw, Sparkles, Trash2, TriangleAlert, User, X,
} from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { Reveal } from "../components/charts";
import { Button, Card, CardTitle, Chip, ErrorState, ReviewBadge, Skeleton, StatusBadge } from "../components/ui";
import { api, type CandidateDetail, type Message, type ReviewStatus } from "../lib/api";
import { AVAILABILITY, FIELD_LABELS, FLAG_LABELS, REASONS, SCHEDULE, ago, experience, initials, interviewTime, parseUtc, shortDate, titleCase, until } from "../lib/format";
import { useCandidate, useNow, useToast } from "../lib/hooks";

const REVIEW: { key: ReviewStatus; label: string }[] = [
  { key: "new", label: "New" },
  { key: "contacted", label: "Contacted" },
  { key: "interview", label: "Interview" },
  { key: "hired", label: "Hired" },
  { key: "rejected", label: "Rejected" },
];

function fieldValue(field: string, d: CandidateDetail["data"]): string {
  switch (field) {
    case "full_name": return d.full_name ?? "–";
    case "drivers_license": {
      const status = ({ yes: "Yes", no: "No", in_progress: "In progress" } as Record<string, string>)[d.license_status ?? ""] ?? "–";
      return d.license_status === "yes" && d.license_type ? `${status} (${{ car: "car", motorbike: "motorbike", both: "car and motorbike" }[d.license_type]})` : status;
    }
    case "location": return d.in_service_area === false ? `${d.location_raw} (outside area)` : d.city ?? "–";
    case "zone": return d.zone ?? "–";
    case "availability": return d.availability.map((a) => AVAILABILITY[a] ?? a).join(", ") || "–";
    case "schedule": return d.preferred_schedule.map((s) => SCHEDULE[s] ?? s).join(", ") || "–";
    case "experience_years": return experience(d.experience_months);
    case "experience_platforms": return d.experience_platforms.join(", ") || "–";
    case "start_date": return d.start_date ? shortDate(d.start_date) : "–";
  }
  return "–";
}

function FieldStatusIcon({ status }: { status: string }) {
  if (status === "valid") return <CircleCheck className="size-4 text-emerald-600 dark:text-emerald-400" aria-label="valid" />;
  if (status === "unclear") return <TriangleAlert className="size-4 text-amber-600 dark:text-amber-400" aria-label="unclear" />;
  if (status === "invalid") return <CircleX className="size-4 text-rose-600 dark:text-rose-400" aria-label="invalid" />;
  if (status === "skipped") return <CircleDot className="size-4 text-ink-3" aria-label="skipped" />;
  return <CircleDot className="size-4 text-line" aria-label="missing" />;
}

function SummaryCard({ detail }: { detail: CandidateDetail }) {
  const client = useQueryClient();
  const toast = useToast();
  const regenerate = useMutation({
    mutationFn: () => api.regenerateSummary(detail.row.id),
    onSuccess: () => { client.invalidateQueries({ queryKey: ["candidate", detail.row.id] }); toast("Summary regenerated"); },
  });
  const s = detail.summary;
  const active = detail.row.status === "in_progress" || detail.row.status === "awaiting_reply";
  return (
    <Card>
      <CardTitle icon={Sparkles} aside={!active && <Button variant="ghost" icon={RefreshCw} loading={regenerate.isPending} onClick={() => regenerate.mutate()} className="min-h-9 px-3">Regenerate</Button>}>
        AI summary
      </CardTitle>
      {regenerate.isPending ? (
        <div className="space-y-2"><Skeleton className="h-5 w-3/4" /><Skeleton className="h-4" /><Skeleton className="h-4 w-5/6" /></div>
      ) : !s ? (
        <p className="text-sm text-ink-3">{active ? "Written when the conversation ends, so the candidate never waits for it." : "No summary yet."}</p>
      ) : (
        <div>
          <p className="font-medium text-ink">{s.headline}</p>
          <p className="mt-2 text-[15px] leading-relaxed text-ink-2">{s.summary}</p>
          <div className="mt-4 grid gap-4 sm:grid-cols-2">
            <div>
              <div className="mb-2 text-xs font-semibold tracking-wide text-emerald-700 uppercase dark:text-emerald-400">Strengths</div>
              <ul className="space-y-1.5">{s.strengths.map((x, i) => <li key={i} className="flex gap-2 text-sm text-ink-2"><Check className="mt-0.5 size-4 shrink-0 text-emerald-600" aria-hidden />{x}</li>)}</ul>
            </div>
            <div>
              <div className="mb-2 text-xs font-semibold tracking-wide text-amber-700 uppercase dark:text-amber-400">To check</div>
              <ul className="space-y-1.5">{(s.concerns.length ? s.concerns : ["Nothing flagged"]).map((x, i) => <li key={i} className="flex gap-2 text-sm text-ink-2"><TriangleAlert className="mt-0.5 size-4 shrink-0 text-amber-600" aria-hidden />{x}</li>)}</ul>
            </div>
          </div>
          <div className="mt-4 flex gap-2.5 rounded-xl bg-brand-soft p-3.5 text-sm text-ink ring-1 ring-brand/15">
            <Gavel className="mt-0.5 size-4 shrink-0 text-brand-ink" aria-hidden /><span><span className="font-medium">Next step: </span>{s.recommended_action}</span>
          </div>
          {s.source === "template" && <p className="mt-2 text-xs text-ink-3">The AI summary was unavailable: fallback shown.</p>}
        </div>
      )}
    </Card>
  );
}

/** The interview the candidate booked in the chat (or why a person has to find a time). */
function InterviewCard({ detail }: { detail: CandidateDetail }) {
  const { interview_status: status, interview_at: at, interview_timezone: tz, interview_place: place } = detail.row;
  const booked = status === "booked";
  return (
    <Card className={clsx(booked && "ring-1 ring-emerald-600/25")}>
      <CardTitle icon={booked ? CalendarCheck : CalendarClock}>Interview</CardTitle>
      {booked ? (
        <>
          <div className="num font-display text-2xl font-semibold text-heading">{interviewTime(at, tz)}</div>
          <p className="mt-1 text-sm text-ink-2">{place}</p>
          <p className="mt-3 text-xs text-ink-3">Booked by the candidate in the chat. Times are shown in the restaurant's local time.</p>
        </>
      ) : status === "offered" ? (
        <p className="text-sm text-ink-2">Times offered in the chat; the candidate hasn't picked one yet.</p>
      ) : (
        <p className="text-sm text-ink-2">None of the offered times worked: <b className="text-ink">a recruiter needs to find a time</b> with the candidate.</p>
      )}
    </Card>
  );
}

function DecisionCard({ detail }: { detail: CandidateDetail }) {
  const client = useQueryClient();
  const toast = useToast();
  const [status, setStatus] = useState<ReviewStatus>(detail.review.status);
  const [note, setNote] = useState(detail.review.note);
  const [by, setBy] = useState(detail.review.updated_by || (() => { try { return localStorage.getItem("recruiter") ?? ""; } catch { return ""; } })());
  useEffect(() => { setStatus(detail.review.status); setNote(detail.review.note); }, [detail.review.status, detail.review.note]);

  const save = useMutation({
    mutationFn: () => api.review(detail.row.id, { status, note, by }),
    onSuccess: () => {
      try { localStorage.setItem("recruiter", by); } catch { /* storage may be blocked */ }
      client.invalidateQueries();
      toast("Decision saved");
    },
  });
  const bot = detail.row.status;
  const overriding = ((bot === "disqualified" || bot === "withdrawn") && ["contacted", "interview", "hired"].includes(status)) || (bot === "qualified" && status === "rejected");
  const dirty = status !== detail.review.status || note !== detail.review.note;

  return (
    <Card>
      <CardTitle icon={Gavel}>Recruiter decision</CardTitle>
      <div role="radiogroup" aria-label="Recruiter status" className="grid grid-cols-5 gap-1 rounded-xl bg-surface-2 p-1">
        {REVIEW.map((r) => (
          <button key={r.key} role="radio" aria-checked={status === r.key} onClick={() => setStatus(r.key)}
            className={clsx("relative min-h-9 cursor-pointer rounded-lg text-xs font-medium transition-colors", status === r.key ? "text-ink" : "text-ink-3 hover:text-ink")}>
            {status === r.key && <motion.span layoutId="review-pill" className="absolute inset-0 rounded-lg bg-surface shadow-sm ring-1 ring-line" transition={{ type: "spring", stiffness: 420, damping: 34 }} />}
            <span className="relative">{r.label}</span>
          </button>
        ))}
      </div>
      <AnimatePresence>
        {overriding && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} className="overflow-hidden">
            <div className="mt-3 flex gap-2.5 rounded-xl bg-amber-50 p-3 text-[13px] text-amber-900 ring-1 ring-amber-600/20 dark:bg-amber-400/10 dark:text-amber-200">
              <Gavel className="mt-0.5 size-4 shrink-0" aria-hidden />This overrides the automated outcome. It will be logged as a human override.
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      <label className="mt-4 block text-[13px] font-medium text-ink-2" htmlFor="note">Note</label>
      <textarea id="note" value={note} onChange={(e) => setNote(e.target.value)} rows={3} placeholder="e.g. Called, interview Thursday 11:00 at Chamberí"
        className="mt-1.5 w-full resize-none rounded-xl border border-line bg-surface p-3 text-sm text-ink placeholder:text-ink-3 focus:border-focus focus:outline-none" />
      <label className="mt-3 block text-[13px] font-medium text-ink-2" htmlFor="by">Your name</label>
      <input id="by" value={by} onChange={(e) => setBy(e.target.value)} placeholder="Recruiter name"
        className="mt-1.5 h-10 w-full rounded-xl border border-line bg-surface px-3 text-sm text-ink placeholder:text-ink-3 focus:border-focus focus:outline-none" />
      <div className="mt-4 flex items-center justify-between gap-3">
        <span className="text-xs text-ink-3">{detail.review.updated_at ? `Updated ${ago(detail.review.updated_at, new Date())}${detail.review.updated_by ? ` by ${detail.review.updated_by}` : ""}` : "No decision yet"}</span>
        <Button variant="primary" icon={Check} loading={save.isPending} disabled={!dirty} onClick={() => save.mutate()}>Save decision</Button>
      </div>
    </Card>
  );
}

function WhyPanel({ message }: { message: Message }) {
  const a = message.meta.analysis;
  const d = message.meta.directive as Record<string, unknown> | undefined;
  if (a) {
    const extracted = Object.entries(a.extracted).filter(([, v]) => v !== null && !(Array.isArray(v) && !v.length));
    return (
      <div className="space-y-3 text-[13px]">
        <div className="flex flex-wrap gap-1.5">
          {a.intents.map((i) => <Chip key={i}>{titleCase(i)}</Chip>)}
          <Chip><Languages className="size-3" />{a.language.toUpperCase()}{a.language_is_clear ? "" : " (no signal)"}</Chip>
          <Chip>Sentiment: {a.sentiment}</Chip>
          {a.faq_id && <Chip>FAQ: {titleCase(a.faq_id)}</Chip>}
        </div>
        {extracted.length > 0 && (
          <div className="rounded-lg bg-surface p-3 ring-1 ring-line">
            <div className="mb-1.5 text-xs font-semibold text-ink-3 uppercase">Extracted</div>
            {extracted.map(([k, v]) => (
              <div key={k} className="flex justify-between gap-4 py-0.5"><span className="text-ink-3">{titleCase(k)}</span><span className="font-mono text-ink">{typeof v === "object" ? JSON.stringify(v) : String(v)}</span></div>
            ))}
          </div>
        )}
        {a.evidence.map((e, i) => (
          <div key={i} className="flex gap-2 text-ink-2"><Quote className="mt-0.5 size-3.5 shrink-0 text-brand-ink" aria-hidden /><span><span className="text-ink-3">{titleCase(e.field)}:</span> “{e.quote}”</span></div>
        ))}
      </div>
    );
  }
  if (d) {
    const rows = [
      ["Decision", titleCase(String(d.kind ?? ""))],
      ["Asked for", d.ask_field ? FIELD_LABELS[String(d.ask_field)] ?? String(d.ask_field) : null],
      ["Because", d.ask_issue ? titleCase(String(d.ask_issue)) : null],
      ["Outcome", d.outcome ? titleCase(String(d.outcome)) : null],
      ["Tone", d.tone && d.tone !== "normal" ? String(d.tone) : null],
      ["Language", String(d.locale ?? "")],
    ].filter(([, v]) => v);
    return (
      <div className="text-[13px]">
        {rows.map(([k, v]) => <div key={k} className="flex justify-between gap-4 py-0.5"><span className="text-ink-3">{k}</span><span className="text-ink">{v}</span></div>)}
        {Array.isArray(d.acknowledge) && d.acknowledge.length > 0 && <p className="mt-2 text-ink-2">Acknowledged: {(d.acknowledge as string[]).join("; ")}</p>}
        <details className="mt-2"><summary className="cursor-pointer text-xs text-ink-3">Raw directive</summary>
          <pre className="mt-1 max-h-56 overflow-auto rounded-lg bg-surface p-2 font-mono text-[11px] text-ink-2 ring-1 ring-line">{JSON.stringify(d, null, 2)}</pre>
        </details>
      </div>
    );
  }
  return null;
}

function Bubble({ message, index }: { message: Message; index: number }) {
  const [open, setOpen] = useState(false);
  const agent = message.role === "agent";
  const followup = message.meta.kind === "followup";
  const canExplain = !!(message.meta.analysis || message.meta.directive);
  const label = agent
    ? followup ? `Reminder ${message.meta.attempt}${message.meta.whatsapp_template_required ? " · WhatsApp template" : ""}`
      : message.meta.source === "llm" ? "Written by the model" : "Fixed template"
    : message.meta.analysis ? `${message.meta.analysis.intents.map(titleCase).join(", ")} · ${message.meta.analysis.sentiment}` : "";
  return (
    <motion.div initial={{ opacity: 0, y: 8 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: 0.2 }}
      transition={{ duration: 0.3, delay: Math.min(index, 6) * 0.03 }}
      className={clsx("flex gap-2.5", agent ? "justify-start" : "justify-end")}>
      {agent && <div className="mt-1 grid size-8 shrink-0 place-items-center rounded-full bg-brand-btn font-display text-sm text-on-brand">S</div>}
      <div className={clsx("max-w-[78%]", !agent && "items-end text-right")}>
        <div className={clsx("rounded-2xl px-4 py-2.5 text-left text-[15px] leading-relaxed whitespace-pre-line",
          agent ? followup ? "rounded-tl-md bg-violet-50 text-ink ring-1 ring-violet-500/20 dark:bg-violet-400/10" : "rounded-tl-md bg-surface-2 text-ink"
            : "rounded-tr-md bg-brand-soft text-ink ring-1 ring-brand/15")}>
          {message.text}
        </div>
        <div className={clsx("mt-1 flex items-center gap-2 text-xs text-ink-3", !agent && "justify-end")}>
          {followup && <Hourglass className="size-3 text-violet-600" aria-hidden />}
          <span>{label}</span>
          {canExplain && (
            <button onClick={() => setOpen(!open)} aria-expanded={open} className="inline-flex cursor-pointer items-center gap-0.5 font-medium text-brand-ink hover:underline">
              {agent ? "Why?" : "Understood"}<ChevronDown className={clsx("size-3 transition-transform", open && "rotate-180")} />
            </button>
          )}
        </div>
        <AnimatePresence>
          {open && (
            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} transition={{ duration: 0.2 }} className="overflow-hidden text-left">
              <div className="mt-2 rounded-xl bg-surface-2 p-3"><WhyPanel message={message} /></div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
      {!agent && <div className="mt-1 grid size-8 shrink-0 place-items-center rounded-full bg-surface-2 text-ink-3"><User className="size-4" /></div>}
    </motion.div>
  );
}

const EVENT_LABELS: Record<string, string> = {
  conversation_started: "Conversation started", stage_changed: "Stage changed", field_valid: "Answer accepted", field_invalid: "Answer rejected",
  field_unclear: "Field marked unclear", field_corrected: "Answer corrected", field_refined: "Answer completed", field_reopened: "Field reopened", knockout: "Knock-out",
  completed: "Screening finished", question_answered: "Question answered (FAQ)", question_unanswered: "Question not in FAQ", language_switched: "Language switched",
  human_requested: "Asked for a person", followup_sent: "Reminder sent", resumed: "Candidate came back", abandoned: "Marked abandoned",
  review_status_changed: "Recruiter status changed", human_override: "Human override", sentiment: "Sentiment", talent_pool: "Talent pool answer",
  llm_error: "LLM error", guard_rejected: "Draft rejected by guard", ungrounded_value: "Ungrounded value discarded", abuse_strike: "Abusive message",
  update_after_close: "New info after close", ignored_after_close: "Ignored small talk after close", field_skipped: "Optional field skipped",
  recap_not_confirmed: "Summary not confirmed", interview_offered: "Interview times offered", interview_booked: "Interview booked",
  interview_cancelled: "Interview cancelled by the candidate", interview_handoff: "Interview: recruiter to find a time", interview_slot_taken: "Interview time taken meanwhile", knockout_deferred: "Knock-out deferred (not asked yet)", unsolicited_value_ignored: "Value mentioned in passing ignored",
};

function EraseButton({ id }: { id: string }) {
  const [confirming, setConfirming] = useState(false);
  const navigate = useNavigate();
  const client = useQueryClient();
  const toast = useToast();
  const erase = useMutation({ mutationFn: () => api.erase(id), onSuccess: () => { client.invalidateQueries(); toast("Candidate data erased"); navigate("/"); } });
  return (
    <>
      <Button variant="ghost" icon={Trash2} onClick={() => setConfirming(true)} className="text-rose-700 hover:text-rose-800 dark:text-rose-300">Erase data</Button>
      <AnimatePresence>
        {confirming && (
          <motion.div className="fixed inset-0 z-50 grid place-items-center bg-black/50 p-4" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setConfirming(false)}>
            <motion.div role="alertdialog" aria-modal="true" aria-labelledby="erase-title" initial={{ scale: 0.96, y: 8 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.98 }}
              onClick={(e) => e.stopPropagation()} className="w-full max-w-md rounded-2xl bg-surface p-6 shadow-2xl ring-1 ring-line">
              <div className="flex items-start justify-between gap-4">
                <h2 id="erase-title" className="font-display text-xl font-semibold text-heading">Erase this candidate?</h2>
                <button onClick={() => setConfirming(false)} aria-label="Cancel" className="cursor-pointer rounded-lg p-1 text-ink-3 hover:text-ink"><X className="size-5" /></button>
              </div>
              <p className="mt-2 text-sm text-ink-2">Right to erasure (GDPR): the transcript, data, summary and audit trail are deleted permanently. This cannot be undone.</p>
              <div className="mt-6 flex justify-end gap-2">
                <Button onClick={() => setConfirming(false)}>Cancel</Button>
                <Button variant="danger" icon={Trash2} loading={erase.isPending} onClick={() => erase.mutate()}>Erase permanently</Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

export function CandidatePage() {
  const { id } = useParams();
  const { data: detail, isLoading, error } = useCandidate(id);
  const now = useNow();

  if (error) return <ErrorState error={error} />;
  if (isLoading || !detail) {
    return <div className="space-y-4"><Skeleton className="h-24 rounded-2xl" /><div className="grid gap-6 lg:grid-cols-[1.6fr_1fr]"><Skeleton className="h-96 rounded-2xl" /><Skeleton className="h-96 rounded-2xl" /></div></div>;
  }
  const { row, data } = detail;
  const exportJson = () => {
    const blob = new Blob([JSON.stringify(detail, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = Object.assign(document.createElement("a"), { href: url, download: `candidate-${row.id.slice(0, 8)}.json` });
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      <Link to="/" className="mb-5 inline-flex items-center gap-1.5 text-sm font-medium text-ink-2 hover:text-ink"><ArrowLeft className="size-4" />Pipeline</Link>

      <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="mb-6 flex flex-wrap items-center gap-5">
        <div className="grid size-16 place-items-center rounded-2xl bg-brand-soft font-display text-2xl text-brand-ink ring-1 ring-brand/15">{initials(row.name)}</div>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="font-display text-3xl font-semibold text-heading">{row.name ?? "Unnamed candidate"}</h1>
            <StatusBadge status={row.status} />
            <ReviewBadge status={row.review_status} overridden={row.overridden} />
          </div>
          <div className="mt-1.5 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-ink-2">
            {row.applied_to && <span className="inline-flex items-center gap-1" title="The job ad applied to (from the application)"><Briefcase className="size-4 text-ink-3" />{row.applied_to}</span>}
            {row.city && <span className="inline-flex items-center gap-1"><MapPin className="size-4 text-ink-3" />{row.city}{row.zone && ` · ${row.zone}`}</span>}
            <span className="inline-flex items-center gap-1"><Languages className="size-4 text-ink-3" />{row.language.toUpperCase()}</span>
            <span className="inline-flex items-center gap-1"><MessageCircle className="size-4 text-ink-3" />via {row.channel} · started {ago(row.created_at, now)}</span>
            {row.disqualification_reason && <span className="inline-flex items-center gap-1 text-rose-700 dark:text-rose-300"><X className="size-4" />{REASONS[row.disqualification_reason]}{detail.talent_pool_opt_in !== null && ` · talent pool: ${detail.talent_pool_opt_in ? "yes" : "no"}`}</span>}
          </div>
        </div>
        <div className="flex gap-2">
          <Button icon={Download} onClick={exportJson}>Export JSON</Button>
          <EraseButton id={row.id} />
        </div>
      </motion.div>

      {(row.status === "awaiting_reply" || row.status === "abandoned") && (
        <motion.div initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }}
          className="mb-6 flex items-center gap-3 rounded-2xl bg-violet-50 p-4 text-sm text-violet-900 ring-1 ring-violet-500/20 dark:bg-violet-400/10 dark:text-violet-200">
          {row.status === "abandoned" ? <MoonStar className="size-5 shrink-0" /> : <Hourglass className="size-5 shrink-0" />}
          {row.status === "abandoned"
            ? "No reply after 3 reminders: marked abandoned. Any reply resumes the screening where it stopped."
            : <span>Waiting for the candidate · reminders sent <strong className="num">{row.followups_sent}/3</strong>{row.next_followup_at && <> · next <strong>{until(row.next_followup_at, now)}</strong> (never at night in their timezone)</>}</span>}
        </motion.div>
      )}

      <div className="grid gap-6 lg:grid-cols-[1.6fr_1fr]">
        <div className="space-y-6">
          <SummaryCard detail={detail} />
          <Reveal>
            <Card>
              <CardTitle icon={Check}>Screening data</CardTitle>
              <ul className="divide-y divide-line">
                {detail.fields.map((f) => (
                  <li key={f.field} className="grid grid-cols-[20px_120px_1fr] items-start gap-3 py-2.5">
                    <FieldStatusIcon status={f.status} />
                    <span className="text-sm text-ink-3">{FIELD_LABELS[f.field] ?? f.field}</span>
                    <div className="min-w-0">
                      <div className="text-sm font-medium text-ink">{fieldValue(f.field, data)}</div>
                      {f.evidence && <div className="mt-0.5 flex gap-1.5 text-xs text-ink-3"><Quote className="mt-0.5 size-3 shrink-0" />“{f.evidence}”</div>}
                    </div>
                  </li>
                ))}
              </ul>
            </Card>
          </Reveal>
        </div>
        <div className="space-y-6">
          {detail.row.interview_status && <InterviewCard detail={detail} />}
          <DecisionCard detail={detail} />
          {(detail.flags.length > 0 || detail.pending_questions.length > 0) && (
            <Reveal>
              <Card>
                <CardTitle icon={Flag}>Needs attention</CardTitle>
                <ul className="space-y-2 text-sm">
                  {detail.flags.map((f, i) => <li key={i} className="flex gap-2 text-ink-2"><Flag className="mt-0.5 size-4 shrink-0 text-amber-600" />{FLAG_LABELS[f.code] ?? f.code}{f.detail && <span className="text-ink-3">· {FIELD_LABELS[f.detail] ?? f.detail}</span>}</li>)}
                  {detail.pending_questions.map((q, i) => <li key={`q${i}`} className="flex gap-2 text-ink-2"><MessageCircle className="mt-0.5 size-4 shrink-0 text-ink-3" />Asked: “{q}”</li>)}
                </ul>
              </Card>
            </Reveal>
          )}
        </div>
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-[1.6fr_1fr]">
        <Card>
          <CardTitle icon={Bot}>Conversation</CardTitle>
          <div className="space-y-4">{detail.transcript.map((m, i) => <Bubble key={i} message={m} index={i} />)}</div>
        </Card>
        <Reveal>
          <Card>
            <CardTitle icon={CircleDot}>Audit trail</CardTitle>
            <ol className="relative space-y-3 border-l border-line pl-4">
              {detail.events.filter((e) => e.type !== "field_valid").map((e, i) => (
                <li key={i} className="relative">
                  <span className={clsx("absolute top-1.5 -left-[21px] size-2.5 rounded-full ring-4 ring-surface",
                    e.type === "human_override" || e.type === "knockout" ? "bg-rose-500" : e.type.includes("followup") || e.type === "resumed" ? "bg-violet-500" : "bg-ink-3")} />
                  <div className="text-sm text-ink">{EVENT_LABELS[e.type] ?? titleCase(e.type)}</div>
                  <div className="text-xs text-ink-3">{parseUtc(e.created_at).toLocaleString("en-GB", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })}
                    {Object.keys(e.payload).length > 0 && <span className="ml-1 font-mono">{Object.entries(e.payload).filter(([, v]) => v !== null && v !== "").map(([k, v]) => `${k}=${String(v)}`).join(" ").slice(0, 70)}</span>}
                  </div>
                </li>
              ))}
            </ol>
          </Card>
        </Reveal>
      </div>
    </div>
  );
}
