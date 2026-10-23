import clsx from "clsx";
import { CalendarCheck, CalendarClock, Flag, Hourglass, Inbox, MapPin, MessageCircle, Search } from "lucide-react";
import { motion } from "motion/react";
import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { CountUp } from "../components/charts";
import { Chip, EmptyState, ErrorState, PageHeader, REVIEW_LABELS, ReviewBadge, Skeleton, StatusBadge, STATUS_ORDER, statusMeta } from "../components/ui";
import type { CandidateRow, ReviewStatus, Status } from "../lib/api";
import { AVAILABILITY, FLAG_LABELS, SCHEDULE, ago, experience, initials, interviewTime, shortDate, until, zoneText } from "../lib/format";
import { useCandidates, useNow } from "../lib/hooks";

type Filter = "action" | "all" | Status | `review:${ReviewStatus}`;
const REVIEWED: ReviewStatus[] = ["contacted", "interview", "hired", "rejected"];

/** Action needed: the bot qualified or flagged them, and no recruiter has decided yet. */
const needsAction = (r: CandidateRow) => (r.status === "qualified" || r.status === "needs_review") && r.review_status === "new";
const KPIS: Status[] = ["qualified", "needs_review", "in_progress", "awaiting_reply", "abandoned", "disqualified"];

function KpiTile({ status, count, index, onClick, active }: { status: Status; count: number; index: number; onClick: () => void; active: boolean }) {
  const { label, icon: Icon } = statusMeta(status);
  return (
    <motion.button
      onClick={onClick}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: index * 0.05, ease: [0.22, 1, 0.36, 1] }}
      whileHover={{ y: -2 }}
      className={clsx(
        "cursor-pointer rounded-xl border bg-surface p-4 text-left shadow-[0_1px_2px_rgb(0_0_0/0.04)] transition-colors",
        active ? "border-brand/50 ring-2 ring-brand/15" : "border-line hover:border-ink-3/40",
      )}
      aria-pressed={active}
    >
      <div className="flex items-center gap-1.5 text-[13px] font-medium text-ink-2"><Icon className="size-3.5" aria-hidden />{label}</div>
      <CountUp value={count} className="mt-1 block font-display text-[32px] leading-tight font-semibold text-heading" />
    </motion.button>
  );
}

/** The summary headline without the name it starts with (already shown above it). */
function subtitle(row: CandidateRow): string {
  if (!row.headline) return `${row.language.toUpperCase()} · via ${row.channel}`;
  const parts = row.headline.split(" · ");
  return (parts[0]?.trim() === row.name ? parts.slice(1) : parts).join(" · ");
}

function Row({ row, index, now, onOpen }: { row: CandidateRow; index: number; now: Date; onOpen: () => void }) {
  const waiting = row.status === "awaiting_reply" || row.status === "abandoned";
  return (
    <motion.tr
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: Math.min(index, 12) * 0.03 }}
      onClick={onOpen}
      onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), onOpen())}
      tabIndex={0}
      role="link"
      aria-label={`Open ${row.name ?? "candidate"}`}
      className="group cursor-pointer border-t border-line transition-colors hover:bg-surface-2/70 focus-visible:bg-surface-2"
    >
      <td className="py-3 pr-3 pl-5">
        <div className="flex items-center gap-3">
          <div className="grid size-9 shrink-0 place-items-center rounded-full bg-brand-soft text-[13px] font-semibold text-brand-ink ring-1 ring-brand/15">{initials(row.name)}</div>
          <div className="min-w-0">
            <div className="truncate font-medium text-ink group-hover:text-brand-ink">{row.name ?? "Unnamed candidate"}</div>
            <div className="max-w-[260px] truncate text-xs text-ink-3" title={row.headline ?? undefined}>{subtitle(row)}</div>
          </div>
        </div>
      </td>
      <td className="px-3 py-3">
        <div className="flex flex-col items-start gap-1">
          <StatusBadge status={row.status} size="sm" />
          <ReviewBadge status={row.review_status} overridden={row.overridden} size="sm" />
        </div>
      </td>
      <td className="px-3 py-3 text-sm">
        {row.city ? (
          <div className="flex items-start gap-1.5">
            <MapPin className="mt-0.5 size-3.5 shrink-0 text-ink-3" aria-hidden />
            <div className="leading-tight"><div className="whitespace-nowrap text-ink">{row.city}</div>{zoneText(row.zone, row.unlisted_zone) && <div className="text-xs text-ink-3">{zoneText(row.zone, row.unlisted_zone)}</div>}</div>
          </div>
        ) : <span className="text-ink-3">–</span>}
      </td>
      <td className="px-3 py-3 text-sm leading-tight">
        {row.availability.length || row.schedule.length ? (
          <>
            <div className="flex flex-wrap gap-1">{row.availability.map((a) => <Chip key={a}>{AVAILABILITY[a] ?? a}</Chip>)}</div>
            {row.schedule.length > 0 && <div className="mt-1 text-xs text-ink-3">{row.schedule.map((x) => SCHEDULE[x] ?? x).join(", ")}</div>}
          </>
        ) : <span className="text-ink-3">–</span>}
      </td>
      <td className="num px-3 py-3 text-sm whitespace-nowrap text-ink-2">{experience(row.experience_months)}</td>
      <td className="num px-3 py-3 text-sm whitespace-nowrap text-ink-2">{shortDate(row.start_date)}</td>
      <td className="px-3 py-3 text-sm">
        <div className="flex flex-col gap-1">
          {waiting && (
            <span className="inline-flex items-center gap-1 text-xs text-violet-700 dark:text-violet-300">
              <Hourglass className="size-3" aria-hidden />
              {row.status === "abandoned" ? "3/3 reminders, no reply" : `${row.followups_sent}/3 · next ${until(row.next_followup_at, now)}`}
            </span>
          )}
          {row.interview_status === "booked" && (
            <span className="inline-flex items-center gap-1 text-xs font-medium text-emerald-700 dark:text-emerald-300">
              <CalendarCheck className="size-3" aria-hidden />Interview {interviewTime(row.interview_at, row.interview_timezone)}
            </span>
          )}
          {row.interview_status === "offered" && (
            <span className="inline-flex items-center gap-1 text-xs text-ink-2"><CalendarClock className="size-3" aria-hidden />Choosing an interview time</span>
          )}
          {row.flags.map((f) => (
            <span key={f} className="inline-flex items-center gap-1 text-xs text-amber-800 dark:text-amber-300"><Flag className="size-3" aria-hidden />{FLAG_LABELS[f] ?? f}</span>
          ))}
          {row.open_questions > 0 && (
            <span className="inline-flex items-center gap-1 text-xs text-ink-2"><MessageCircle className="size-3" aria-hidden />{row.open_questions} open question{row.open_questions > 1 ? "s" : ""}</span>
          )}
          {!waiting && !row.flags.length && !row.open_questions && !row.interview_status && <span className="text-ink-3">–</span>}
        </div>
      </td>
      <td className="num py-3 pr-5 pl-3 text-right text-xs whitespace-nowrap text-ink-3">{ago(row.last_activity, now)}</td>
    </motion.tr>
  );
}

export function PipelinePage() {
  const { data: rows, isLoading, error } = useCandidates();
  const now = useNow();
  const navigate = useNavigate();
  const [filter, setFilter] = useState<Filter>("action");
  const [query, setQuery] = useState("");

  const counts = useMemo(() => {
    const c: Record<string, number> = {};
    rows?.forEach((r) => {
      c[r.status] = (c[r.status] ?? 0) + 1;
      c[`review:${r.review_status}`] = (c[`review:${r.review_status}`] ?? 0) + 1;
    });
    return c;
  }, [rows]);

  const shown = useMemo(() => (rows ?? []).filter((r) => {
    const byFilter = filter === "all" ? true
      : filter === "action" ? needsAction(r)
      : filter.startsWith("review:") ? r.review_status === filter.slice(7)
      : r.status === filter;
    return byFilter && (!query || (r.name ?? "").toLowerCase().includes(query.toLowerCase()) || (r.city ?? "").toLowerCase().includes(query.toLowerCase()));
  }), [rows, filter, query]);

  if (error) return <ErrorState error={error} />;

  const chips: { key: Filter; label: string; count: number; human?: boolean }[] = [
    { key: "action", label: "Action needed", count: rows?.filter(needsAction).length ?? 0 },
    { key: "all", label: "All", count: rows?.length ?? 0 },
    ...STATUS_ORDER.filter((s) => counts[s]).map((s) => ({ key: s as Filter, label: statusMeta(s).label, count: counts[s] })),
    // What recruiters decided, kept separate from what the bot decided
    ...REVIEWED.filter((r) => counts[`review:${r}`]).map((r) => ({ key: `review:${r}` as Filter, label: REVIEW_LABELS[r], count: counts[`review:${r}`], human: true })),
  ];

  const renderChip = (c: (typeof chips)[number]) => (
    <button key={c.key} role="tab" aria-selected={filter === c.key} onClick={() => setFilter(c.key)}
      className={clsx("inline-flex min-h-9 cursor-pointer items-center gap-1.5 rounded-full px-3.5 text-[13px] font-medium transition-colors",
        filter === c.key ? "bg-heading text-surface" : "bg-surface text-ink-2 ring-1 ring-line hover:text-ink")}>
      {c.label}<span className={clsx("num rounded-full px-1.5 text-[11px]", filter === c.key ? "bg-surface/20" : "bg-surface-2")}>{c.count}</span>
    </button>
  );

  return (
    <div>
      <PageHeader
        title="Candidate pipeline"
        subtitle="Every applicant is screened by Sofía within seconds. Action needed lists who is waiting for a person: qualified candidates (soonest start first), then the ones flagged for review."
      />

      <div className="mb-8 grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-6">
        {isLoading
          ? Array.from({ length: 6 }, (_, i) => <Skeleton key={i} className="h-[92px] rounded-2xl" />)
          : KPIS.map((s, i) => <KpiTile key={s} status={s} count={counts[s] ?? 0} index={i} active={filter === s} onClick={() => setFilter(filter === s ? "action" : s)} />)}
      </div>

      <div className="mb-4 space-y-2.5">
        <div role="tablist" aria-label="Filter by screening outcome" className="flex flex-wrap gap-1.5">
          {chips.filter((c) => !c.human).map(renderChip)}
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {chips.some((c) => c.human) && (
            // What recruiters decided: its own row, apart from what the bot decided
            <div role="tablist" aria-label="Filter by recruiter decision" className="flex flex-wrap items-center gap-1.5">
              <span className="mr-1 text-xs font-medium text-ink-3">Recruiter:</span>
              {chips.filter((c) => c.human).map(renderChip)}
            </div>
          )}
          <label className="relative ml-auto w-full sm:w-64">
            <span className="sr-only">Search by name or city</span>
            <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-ink-3" aria-hidden />
            <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search name or city"
              className="h-10 w-full rounded-lg border border-line bg-surface pr-3 pl-9 text-sm text-ink placeholder:text-ink-3 focus:border-focus focus:outline-none" />
          </label>
        </div>
      </div>

      <div className="overflow-hidden rounded-xl border border-line bg-surface shadow-[0_1px_2px_rgb(0_0_0/0.04)]">
        {isLoading ? (
          <div className="space-y-3 p-5">{Array.from({ length: 6 }, (_, i) => <Skeleton key={i} className="h-12" />)}</div>
        ) : !shown.length ? (
          <EmptyState icon={Inbox} title={rows?.length ? "No candidates match" : "No candidates yet"}>
            {rows?.length ? "Try another filter." : "Start a conversation from Try the agent, or run `make seed`."}
          </EmptyState>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[960px]">
              <thead>
                <tr className="text-left text-xs font-medium tracking-wide text-ink-3 uppercase">
                  <th className="py-3 pr-3 pl-5 font-medium">Candidate</th>
                  <th className="px-3 py-3 font-medium">Status</th>
                  <th className="px-3 py-3 font-medium">City</th>
                  <th className="px-3 py-3 font-medium">Availability · shift</th>
                  <th className="px-3 py-3 font-medium">Experience</th>
                  <th className="px-3 py-3 font-medium">Start</th>
                  <th className="px-3 py-3 font-medium">Attention</th>
                  <th className="py-3 pr-5 pl-3 text-right font-medium">Activity</th>
                </tr>
              </thead>
              <tbody>
                {shown.map((row, i) => <Row key={row.id} row={row} index={i} now={now} onOpen={() => navigate(`/candidates/${row.id}`)} />)}
              </tbody>
            </table>
          </div>
        )}
      </div>
      {!!shown.length && <p className="mt-3 text-xs text-ink-3">{shown.length} of {rows?.length} candidates · updates automatically</p>}
    </div>
  );
}
