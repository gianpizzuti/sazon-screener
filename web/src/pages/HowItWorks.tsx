/**
 * "How it works": the screening flow as an interactive flowchart, plus the live rules of
 * this workspace (read from /api/config, so the page changes when the client's YAML does).
 */
import { useQuery } from "@tanstack/react-query";
import clsx from "clsx";
import {
  BellRing, Bot, ChevronDown, Cpu, Hand, MapPinned, MessageCircleQuestion, MousePointerClick, Play, RotateCcw, Scale, ShieldAlert, Undo2, UserCheck, X,
} from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { type KeyboardEvent, useEffect, useMemo, useState } from "react";

import { Reveal } from "../components/charts";
import { Card, CardTitle, Chip, ErrorState, PageHeader, Skeleton } from "../components/ui";
import { api, type WorkspaceConfig } from "../lib/api";

// ------------------------------------------------------------------ flowchart model
type Kind = "start" | "step" | "decision" | "out" | "branch" | "review" | "end";
interface Node { id: string; kind: Kind; x: number; y: number; title: string; sub?: string }
interface Edge { from: string; to: string; d: string; label?: string; lx?: number; ly?: number; anchor?: "start" | "middle" | "end" }

const SPINE = 300;
const SIDE = 690;
const NODES: Node[] = [
  { id: "start", kind: "start", x: SPINE, y: 40, title: "Candidate applies" },
  { id: "greet", kind: "step", x: SPINE, y: 125, title: "Greeting", sub: "AI disclosed · privacy note" },
  { id: "name", kind: "step", x: SPINE, y: 210, title: "Full name" },
  { id: "license", kind: "decision", x: SPINE, y: 305, title: "Valid driver's license?" },
  { id: "ko_license", kind: "out", x: SIDE, y: 305, title: "Disqualified · no license", sub: "told why · talent-pool opt-in" },
  { id: "city", kind: "decision", x: SPINE, y: 420, title: "City in a service area?" },
  { id: "ko_city", kind: "out", x: SIDE, y: 420, title: "Disqualified · out of area", sub: "told why · talent-pool opt-in" },
  { id: "zone", kind: "step", x: SPINE, y: 525, title: "Zone", sub: "optional · asked once" },
  { id: "avail", kind: "step", x: SPINE, y: 610, title: "Availability" },
  { id: "shift", kind: "step", x: SPINE, y: 695, title: "Preferred shift" },
  { id: "exp", kind: "decision", x: SPINE, y: 800, title: "Delivery experience?" },
  { id: "platforms", kind: "branch", x: SIDE, y: 800, title: "Which platforms", sub: "Glovo, Rappi, Uber Eats…" },
  { id: "start_date", kind: "step", x: SPINE, y: 905, title: "Start date" },
  { id: "recap", kind: "decision", x: SPINE, y: 1010, title: "Recap confirmed?" },
  { id: "qualified", kind: "step", x: SPINE, y: 1115, title: "Qualified", sub: "interview times offered" },
  { id: "interview", kind: "end", x: SPINE, y: 1215, title: "Interview booked", sub: "picked in the chat" },
  { id: "handoff", kind: "review", x: SIDE, y: 1215, title: "Recruiter finds a time", sub: "no time fitted, 2 rounds" },
  { id: "review", kind: "review", x: SIDE, y: 1115, title: "Needs review", sub: "a knock-out stayed unclear" },
];
const EDGES: Edge[] = [
  { from: "start", to: "greet", d: "M300,60 V97" },
  { from: "greet", to: "name", d: "M300,151 V182" },
  { from: "name", to: "license", d: "M300,236 V259" },
  { from: "license", to: "ko_license", d: "M440,305 H538", label: "no / in progress", lx: 489, ly: 296 },
  { from: "license", to: "city", d: "M300,351 V374", label: "yes", lx: 312, ly: 366, anchor: "start" },
  { from: "city", to: "ko_city", d: "M440,420 H538", label: "no", lx: 489, ly: 411 },
  { from: "city", to: "zone", d: "M300,466 V497", label: "yes", lx: 312, ly: 485, anchor: "start" },
  { from: "zone", to: "avail", d: "M300,551 V582" },
  { from: "avail", to: "shift", d: "M300,636 V667" },
  { from: "shift", to: "exp", d: "M300,721 V754" },
  { from: "exp", to: "platforms", d: "M440,800 H538", label: "yes", lx: 489, ly: 791 },
  { from: "exp", to: "start_date", d: "M300,846 V877", label: "none", lx: 312, ly: 866, anchor: "start" },
  { from: "platforms", to: "start_date", d: "M690,830 V905 H432" },
  { from: "start_date", to: "recap", d: "M300,931 V964" },
  { from: "recap", to: "qualified", d: "M300,1056 V1087", label: "yes", lx: 312, ly: 1075, anchor: "start" },
  { from: "qualified", to: "interview", d: "M300,1141 V1187", label: "picks one", lx: 312, ly: 1170, anchor: "start" },
  { from: "qualified", to: "handoff", d: "M430,1125 H470 V1215 H538", label: "none fits", lx: 504, ly: 1206 },
  { from: "recap", to: "review", d: "M440,1010 H690 V1083", label: "yes, but a knock-out was unclear", lx: 565, ly: 1001 },
  { from: "recap", to: "name", d: "M160,1010 H96 V210 H168", label: "correction → that question again", lx: 84, ly: 610 },
];

const DETAILS: Record<string, { asks?: string; rules: string[] }> = {
  start: { rules: ["Sofía writes within seconds of the application: no recruiter call, no waiting.", "Recruiters only step in where the flow sends a candidate to them."] },
  greet: { asks: "¡Hola! 👋 Soy Sofía, la asistente virtual (IA) de Grupo Sazón… ¿Empezamos?", rules: ["A fixed template: on WhatsApp, business-initiated messages must be pre-approved.", "Says it is an AI and what the data is used for.", "\"No\" here = withdrawn; \"not now\" = paused and reminded later."] },
  name: { asks: "¿Cómo te llamas? Nombre y apellido, por favor.", rules: ["First name and surname. A first name alone is kept and the surname asked once.", "Answers can come in any order: several in one message are all captured."] },
  license: { asks: "¿Tienes carnet de conducir en vigor (coche o moto)?", rules: ["Knock-out, decided by a rule, never by the AI.", "\"Lo estoy sacando\" = in progress: disqualified for now, offered the talent pool.", "\"Sí\" alone gets one follow-up: car, motorbike or both. Which types count is the client's setting (Grupo Sazón: both).", "Unclear after 2 attempts: the screening continues and ends in Needs review."] },
  ko_license: { rules: ["The candidate is told why, kindly, and offered to be contacted later.", "A recruiter can always override this outcome; overrides are logged."] },
  city: { asks: "¿En qué ciudad y zona te gustaría repartir?", rules: ["Knock-out: the city must be one of the service areas below.", "Known places are matched by code (accents, typos, ambiguity like \"Centro\").", "Unknown places use the model's knowledge, but only to a configured city."] },
  ko_city: { rules: ["\"We don't deliver in Toledo yet\" + talent-pool opt-in.", "Re-checked if the candidate corrects the city at the recap."] },
  zone: { asks: "¿Y en qué zona o barrio de Madrid?", rules: ["Only asked if the candidate gave just the city.", "Optional and asked once: it only helps match the nearest restaurant."] },
  avail: { asks: "¿Qué disponibilidad tienes: jornada completa, media jornada o fines de semana?", rules: ["Full-time or part-time, plus weekends if they want.", "\"Full time y part time\" is a contradiction: Sofía asks which one."] },
  shift: { asks: "¿Qué turno prefieres: mañana, tarde, noche o flexible?", rules: ["Morning, afternoon, evening or flexible. All three = flexible."] },
  exp: { asks: "¿Tienes experiencia como repartidor/a? ¿Cuánto tiempo y en qué plataformas?", rules: ["The model reports months exactly (\"8 meses\" = 8); years are computed by code.", "No experience is fine: it is not a knock-out."] },
  platforms: { rules: ["Normalised (\"uber\" → Uber Eats); unknown employers kept as written.", "Only asked when experience is above zero."] },
  start_date: { asks: "¿Cuándo podrías empezar?", rules: ["The model reads the expression (\"el lunes que viene\"); code computes the date in the candidate's timezone.", "A past date is asked again; more than 90 days away is accepted and flagged."] },
  recap: { asks: "Antes de terminar, revisa tus datos: … ¿Está todo correcto?", rules: ["Rendered from the data by a template: the candidate's details are never paraphrased.", "A correction re-asks that field and re-runs the knock-outs."] },
  qualified: { asks: "Elige día y hora para tu entrevista (unos 20 minutos) en Grupo Sazón Malasaña (Madrid): 1) miércoles 21/10 a las 16:00 …", rules: ["Three free times, from the client's calendar settings, in the restaurant's local time, the candidate's preferred shift first.", "A fixed template with buttons: dates and times are never written by the AI.", "An AI summary is written for the recruiter after the conversation ends."] },
  interview: { rules: ["Read by rules first (button, number, weekday, time); the AI only when the rules can't tell.", "A unique index in the database: two candidates can never get the same time.", "Confirmation reminds them to bring their licence; they can move it by writing again."] },
  handoff: { rules: ["Nothing fitted after two rounds of options (no loops).", "Flagged for a recruiter, who finds a time with the candidate."] },
  review: { rules: ["A knock-out answer stayed unclear after two attempts.", "The bot does not guess: a recruiter decides."] },
};

const SCENARIOS: { key: string; label: string; path: string[] }[] = [
  { key: "qualified", label: "Qualified", path: ["start", "greet", "name", "license", "city", "zone", "avail", "shift", "exp", "platforms", "start_date", "recap", "qualified", "interview"] },
  { key: "no_license", label: "No license", path: ["start", "greet", "name", "license", "ko_license"] },
  { key: "out_of_area", label: "Out of area", path: ["start", "greet", "name", "license", "city", "ko_city"] },
  { key: "no_experience", label: "No experience", path: ["start", "greet", "name", "license", "city", "zone", "avail", "shift", "exp", "start_date", "recap", "qualified", "interview"] },
];

function nodeBox(n: Node) {
  if (n.kind === "start") return { w: 200, h: 40 };
  if (n.kind === "decision") return { w: 280, h: 92 };
  if (n.kind === "out" || n.kind === "branch" || n.kind === "review") return { w: 300, h: 60 };
  return { w: 260, h: 52 };
}

// ------------------------------------------------------------------ flowchart view
function Flowchart({ selected, onSelect, trail }: { selected: string; onSelect: (id: string) => void; trail: string[] }) {
  const lit = new Set(trail);
  const litEdges = new Set(trail.slice(1).map((id, i) => `${trail[i]}>${id}`));
  const keyHandler = (id: string) => (e: KeyboardEvent) => {
    if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onSelect(id); }
  };
  return (
    // One trigger for the whole chart (as soon as any of it is visible): with a trigger per node,
    // nodes below the fold stayed invisible until scrolled to, and the chart looked broken.
    <motion.svg viewBox="60 0 800 1260" className="mx-auto h-auto w-full max-w-[860px]" role="img"
      initial="hidden" whileInView="shown" viewport={{ once: true, amount: 0.01 }}
      aria-label="Screening flow: greeting, name, driver's license (knock-out), city in a service area (knock-out), zone, availability, shift, experience and platforms, start date, recap, then qualified or needs review. A correction at the recap asks that question again. A qualified candidate picks an interview time in the chat, or a recruiter finds one.">
      <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
          <path d="M0,0 L10,5 L0,10 z" fill="var(--ink-3)" />
        </marker>
        <marker id="arrow-lit" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
          <path d="M0,0 L10,5 L0,10 z" fill="var(--series)" />
        </marker>
      </defs>

      {EDGES.map((e, i) => {
        const on = litEdges.has(`${e.from}>${e.to}`);
        return (
          <g key={`${e.from}-${e.to}`}>
            <motion.path d={e.d} fill="none" strokeWidth={on ? 2.5 : 1.5} strokeLinejoin="round"
              stroke={on ? "var(--series)" : "var(--ink-3)"} strokeOpacity={on ? 1 : 0.55}
              strokeDasharray={e.to === "name" && e.from === "recap" ? "5 5" : undefined}
              markerEnd={`url(#${on ? "arrow-lit" : "arrow"})`}
              variants={{ hidden: { pathLength: 0 }, shown: { pathLength: 1, transition: { duration: 0.4, delay: 0.25 + 0.03 * i, ease: "easeOut" } } }} />
            {e.label && (
              e.from === "recap" && e.to === "name" ? (
                <text x={e.lx} y={e.ly} transform={`rotate(-90 ${e.lx} ${e.ly})`} textAnchor="middle" className="fill-ink-3 text-[13px]">{e.label}</text>
              ) : (
                <text x={e.lx} y={e.ly} textAnchor={e.anchor ?? "middle"} className={clsx("text-[13px] font-medium", on ? "fill-brand-ink" : "fill-ink-3")}>{e.label}</text>
              )
            )}
          </g>
        );
      })}

      {NODES.map((n, i) => {
        const { w, h } = nodeBox(n);
        const isSel = selected === n.id;
        const isLit = lit.has(n.id);
        const fill = n.kind === "end" ? "var(--brand-btn)" : n.kind === "out" ? "var(--surface)" : isLit ? "var(--brand-soft)" : "var(--surface)";
        const titleClass = n.kind === "end" ? "fill-on-brand" : n.kind === "out" ? "fill-rose-700 dark:fill-rose-300" : n.kind === "review" ? "fill-amber-800 dark:fill-amber-300" : "fill-heading";
        const stroke = isSel ? "var(--focus)" : isLit ? "var(--series)" : n.kind === "out" ? "#e11d48" : n.kind === "review" ? "#d97706" : "var(--line)";
        return (
          <motion.g key={n.id} role="button" tabIndex={0} aria-pressed={isSel} aria-label={`${n.title}${n.sub ? `, ${n.sub}` : ""}`}
            onClick={() => onSelect(n.id)} onKeyDown={keyHandler(n.id)} className="cursor-pointer outline-none"
            variants={{ hidden: { opacity: 0, y: 6 }, shown: { opacity: 1, y: 0, transition: { duration: 0.3, delay: 0.02 * i } } }}>
            {n.kind === "decision" ? (
              <polygon points={`${n.x},${n.y - h / 2} ${n.x + w / 2},${n.y} ${n.x},${n.y + h / 2} ${n.x - w / 2},${n.y}`}
                fill={isLit ? "var(--brand-soft)" : "var(--surface-2)"} stroke={stroke} strokeWidth={isSel || isLit ? 2.5 : 1.5}
                strokeOpacity={n.kind === "decision" && !isSel && !isLit ? 0.9 : 1} />
            ) : (
              <rect x={n.x - w / 2} y={n.y - h / 2} width={w} height={h} rx={n.kind === "start" ? h / 2 : 12}
                fill={fill} stroke={stroke} strokeWidth={isSel || isLit ? 2.5 : 1.5} strokeOpacity={n.kind === "out" || n.kind === "review" ? 0.6 : 1} />
            )}
            <text x={n.x} y={n.sub ? n.y - 3 : n.y + 5} textAnchor="middle" className={clsx("text-[16px] font-semibold", titleClass)}>{n.title}</text>
            {n.sub && <text x={n.x} y={n.y + 15} textAnchor="middle" className={clsx("text-[13px]", n.kind === "end" ? "fill-on-brand" : "fill-ink-3")}>{n.sub}</text>}
          </motion.g>
        );
      })}
    </motion.svg>
  );
}

const KIND_LABEL: Record<Kind, string> = {
  start: "Start", step: "Step", decision: "Decision · rule-based", out: "Outcome", branch: "Step", review: "Outcome", end: "Outcome",
};

function NodeDetails({ id, cfg, compact = false }: { id: string; cfg?: WorkspaceConfig; compact?: boolean }) {
  const node = NODES.find((n) => n.id === id)!;
  const detail = DETAILS[id];
  return (
    <div>
      {!compact && (
        <>
          <div className="mb-1 text-xs font-medium tracking-wide text-ink-3 uppercase">{KIND_LABEL[node.kind]}</div>
          <h3 className="font-display text-xl font-semibold text-heading">{node.title}</h3>
        </>
      )}
      {detail?.asks && (
        <div className={clsx("rounded-lg bg-surface p-3 text-sm text-ink ring-1 ring-line", !compact && "mt-3")}>
          <div className="mb-1 text-xs font-medium text-ink-3">Sofía asks (es-ES)</div>“{detail.asks}”
        </div>
      )}
      <ul className="mt-3 space-y-2">
        {detail?.rules.map((r) => <li key={r} className="flex gap-2 text-sm text-ink-2"><span className="mt-2 size-1.5 shrink-0 rounded-full bg-brand-ink" />{r}</li>)}
      </ul>
      {id === "city" && cfg && <p className="mt-3 text-xs text-ink-3">Service areas: {cfg.service_areas.map((a) => a.name).join(", ")}.</p>}
    </div>
  );
}

// ------------------------------------------------------------------ page
export function HowItWorksPage() {
  const { data: cfg, isLoading, error } = useQuery({ queryKey: ["config"], queryFn: api.config });
  const [selected, setSelected] = useState("start");
  const [scenario, setScenario] = useState<string | null>(null);
  const [step, setStep] = useState(0);
  const [drawer, setDrawer] = useState(false);
  const path = useMemo(() => SCENARIOS.find((s) => s.key === scenario)?.path ?? [], [scenario]);

  useEffect(() => {
    if (!scenario || step >= path.length - 1) return;
    const timer = setTimeout(() => setStep((s) => s + 1), 650);
    return () => clearTimeout(timer);
  }, [scenario, step, path.length]);
  useEffect(() => { if (scenario) setSelected(path[step]); }, [scenario, step, path]);
  useEffect(() => {
    if (!drawer) return;
    const onKey = (e: globalThis.KeyboardEvent) => { if (e.key === "Escape") setDrawer(false); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [drawer]);

  const run = (key: string) => { setScenario(key); setStep(0); setDrawer(false); };
  const pick = (id: string) => { setScenario(null); setSelected(id); setDrawer(true); };
  const f = cfg?.followups;

  return (
    <div>
      <PageHeader title="How Sofía works"
        subtitle="The screening flow and the rules this workspace runs on. The AI reads and writes the messages; every decision on this chart is made by these rules, and a recruiter can override any outcome." />

      <Card>
        <CardTitle number={1}>The screening flow</CardTitle>
        <div className="mb-5 hidden flex-wrap items-center gap-1.5 md:flex">
          <span className="mr-1 text-xs font-medium text-ink-3">Trace a candidate:</span>
          {SCENARIOS.map((sc) => (
            <button key={sc.key} onClick={() => run(sc.key)} aria-pressed={scenario === sc.key}
              className={clsx("inline-flex min-h-8 cursor-pointer items-center gap-1 rounded-full px-3 text-[13px] font-medium transition-colors",
                scenario === sc.key ? "bg-heading text-surface" : "bg-surface text-ink-2 ring-1 ring-line hover:text-ink")}>
              <Play className="size-3" aria-hidden />{sc.label}
            </button>
          ))}
          {scenario && (
            <button onClick={() => { setScenario(null); setSelected("start"); }} aria-label="Clear trace"
              className="grid size-8 cursor-pointer place-items-center rounded-full text-ink-3 hover:text-ink"><RotateCcw className="size-4" /></button>
          )}
          <span className="ml-auto flex items-center gap-1.5 text-xs text-ink-3"><MousePointerClick className="size-3.5" aria-hidden />Click any step for its rules</span>
        </div>

        <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_300px]">
          <div className="hidden md:block"><Flowchart selected={selected} onSelect={pick} trail={path.slice(0, step + 1)} /></div>

          {/* Phones: the same flow as an accordion (a scaled-down chart would be unreadable) */}
          <ol className="space-y-2 md:hidden">
            {NODES.filter((n) => n.kind !== "start").map((n) => {
              const open = selected === n.id;
              const sideBranch = n.kind === "out" || n.kind === "branch" || n.kind === "review";
              return (
                <li key={n.id} className={clsx(sideBranch && "ml-5")}>
                  <button onClick={() => setSelected(open ? "start" : n.id)} aria-expanded={open}
                    className={clsx("flex w-full items-center gap-3 rounded-lg border px-3 py-2.5 text-left",
                      open ? "border-focus bg-brand-soft" : n.kind === "out" ? "border-rose-300 dark:border-rose-900" : n.kind === "end" ? "border-brand-ink" : "border-line")}>
                    <span className="min-w-0 flex-1">
                      <span className={clsx("block text-sm font-semibold", n.kind === "out" ? "text-rose-700 dark:text-rose-300" : "text-heading")}>{n.title}</span>
                      {n.sub && <span className="block text-xs text-ink-3">{n.sub}</span>}
                    </span>
                    {n.kind === "decision" && <span className="rounded bg-surface-2 px-1.5 py-0.5 text-[11px] font-medium text-ink-2">rule</span>}
                    <ChevronDown className={clsx("size-4 shrink-0 text-ink-3 transition-transform", open && "rotate-180")} aria-hidden />
                  </button>
                  {open && <div className="px-1 pt-2 pb-1"><NodeDetails id={n.id} cfg={cfg} compact /></div>}
                </li>
              );
            })}
          </ol>

          {/* Wide screens: a side panel next to the chart */}
          <aside className="hidden xl:sticky xl:top-24 xl:block xl:self-start">
            <motion.div key={selected} initial={{ opacity: 0, x: 8 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.2 }}
              className="rounded-xl bg-surface-2 p-5">
              <NodeDetails id={selected} cfg={cfg} />
            </motion.div>
          </aside>
        </div>
      </Card>

      {/* Tablets and small laptops: the chart needs the full width, so details float above it */}
      <AnimatePresence>
        {drawer && (
          <motion.aside initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 16 }} transition={{ duration: 0.2 }}
            className="fixed right-4 bottom-4 z-40 hidden max-h-[70dvh] w-[340px] overflow-auto rounded-xl border border-line bg-surface-2 p-5 shadow-2xl md:block xl:hidden">
            <button onClick={() => setDrawer(false)} aria-label="Close details"
              className="absolute top-3 right-3 grid size-8 cursor-pointer place-items-center rounded-full text-ink-3 hover:bg-surface hover:text-ink"><X className="size-4" /></button>
            <NodeDetails id={selected} cfg={cfg} />
          </motion.aside>
        )}
      </AnimatePresence>

      <Reveal className="mt-6">
        <Card>
          <CardTitle number={2}>Who decides what</CardTitle>
          <div className="grid gap-4 md:grid-cols-3">
            {[
              { icon: Bot, title: "The AI reads and writes", items: ["Understands each message: values, intent, language, sentiment", "Must quote the candidate's words for every value, or it is discarded", "Writes the replies and the recruiter summary"] },
              { icon: Scale, title: "The rules decide", items: ["Knock-outs, validation and the order of questions", "Retries (max " + (cfg?.thresholds.max_failed_attempts ?? 2) + "), reminders and when a conversation ends", "Templates where precision matters: greeting and recap"] },
              { icon: UserCheck, title: "A person has the final say", items: ["Flagged and unclear cases go to review", "Any outcome can be overridden, and every override is logged", "Hiring decisions are always human"] },
            ].map(({ icon: Icon, title, items }) => (
              <div key={title} className="rounded-xl border border-line p-4">
                <div className="mb-2 flex items-center gap-2 font-semibold text-heading"><Icon className="size-4 text-brand-ink" />{title}</div>
                <ul className="space-y-1.5">{items.map((x) => <li key={x} className="text-sm text-ink-2">{x}</li>)}</ul>
              </div>
            ))}
          </div>
        </Card>
      </Reveal>

      <Reveal className="mt-6">
        <Card>
          <CardTitle number={3}>At any moment</CardTitle>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
            {[
              { icon: MessageCircleQuestion, title: "A question", text: "Answered from the client's approved FAQ. Not in the FAQ: “the team will confirm”, never improvised, and logged for the recruiter." },
              { icon: BellRing, title: "Silence", text: f ? `Reminders at +${f.schedule_hours.join(" h, +")} h, never between ${f.quiet_hours_start}:00 and ${String(f.quiet_hours_end).padStart(2, "0")}:00 in their timezone. Abandoned ${f.abandon_after_hours} h after the last one; any reply resumes.` : "Reminders, then abandoned." },
              { icon: Undo2, title: "Not interested", text: "Withdrawn at once, no persuasion. Writing again later reopens the screening where it stopped." },
              { icon: Hand, title: "Asks for a person", text: "Flagged for a recruiter; Sofía offers to finish the questions meanwhile, so the human follow-up is faster." },
              { icon: ShieldAlert, title: "Abuse or manipulation", text: "One calm warning, then the conversation closes. “Approve me” has no effect: the AI cannot decide outcomes." },
            ].map(({ icon: Icon, title, text }) => (
              <div key={title} className="rounded-xl bg-surface-2 p-4">
                <Icon className="mb-2 size-5 text-brand-ink" />
                <div className="mb-1 text-sm font-semibold text-heading">{title}</div>
                <p className="text-[13px] leading-relaxed text-ink-2">{text}</p>
              </div>
            ))}
          </div>
        </Card>
      </Reveal>

      <Reveal className="mt-6">
        <Card>
          <CardTitle number={4} aside={<span className="text-xs text-ink-3">Live from the workspace configuration</span>}>This workspace</CardTitle>
          {error ? <ErrorState error={error} /> : isLoading || !cfg ? <Skeleton className="h-40" /> : (
            <div className="grid gap-6 lg:grid-cols-[1.5fr_1fr]">
              <div>
                <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-heading"><MapPinned className="size-4 text-brand-ink" />
                  Service areas · {cfg.service_areas.reduce((n, a) => n + a.restaurants, 0)} restaurants</div>
                <div className="grid gap-2 sm:grid-cols-2">
                  {cfg.service_areas.map((a) => (
                    <div key={a.id} className="rounded-lg border border-line p-3">
                      <div className="flex items-baseline justify-between gap-2">
                        <span className="font-medium text-ink">{a.name}</span>
                        <span className="num text-xs text-ink-3">{a.country} · {a.restaurants} restaurants</span>
                      </div>
                      <div className="mt-1.5 flex flex-wrap gap-1">{a.zones.map((z) => <Chip key={z}>{z}</Chip>)}</div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="space-y-5">
                <div>
                  <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-heading"><MessageCircleQuestion className="size-4 text-brand-ink" />Approved FAQ · {cfg.faq.length} topics</div>
                  <div className="flex flex-wrap gap-1.5">{cfg.faq.map((q) => <span key={q.id} title={q.question} className="rounded-md bg-surface-2 px-2 py-1 text-xs text-ink-2">{q.id.replace(/_/g, " ")}</span>)}</div>
                </div>
                <div>
                  <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-heading"><Cpu className="size-4 text-brand-ink" />Models, one per task</div>
                  <dl className="space-y-1.5 text-sm">
                    {[["Understanding", cfg.models.understand, "fast: the candidate is waiting"], ["Replies", cfg.models.speak, "tone matters"], ["Recruiter summary", cfg.models.summary, "after the chat: quality first"]].map(([k, v, why]) => (
                      <div key={k} className="flex flex-wrap items-baseline justify-between gap-x-3">
                        <dt className="text-ink-2">{k} <span className="text-xs text-ink-3">· {why}</span></dt>
                        <dd className="font-mono text-xs text-ink">{v}</dd>
                      </div>
                    ))}
                  </dl>
                </div>
                <div>
                  <div className="mb-2 text-sm font-semibold text-heading">Limits</div>
                  <p className="text-sm text-ink-2">Messages up to {cfg.thresholds.max_message_chars} characters · {cfg.thresholds.max_failed_attempts} attempts per question · start dates beyond {cfg.thresholds.late_start_days} days are flagged.</p>
                </div>
              </div>
            </div>
          )}
        </Card>
      </Reveal>
    </div>
  );
}
