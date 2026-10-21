import { Table2 } from "lucide-react";
import { type ReactNode, useState } from "react";

import { BarList, type BarRow, CountUp, DataTable, Meter, Reveal } from "../components/charts";
import { Card, CardTitle, ErrorState, PageHeader, Skeleton } from "../components/ui";
import { REASONS, pct, titleCase } from "../lib/format";
import { useAnalytics } from "../lib/hooks";

const toRows = (obj: Record<string, number>, label: (k: string) => string = (k) => k): BarRow[] =>
  Object.entries(obj).map(([k, v]) => ({ label: label(k), value: v }));

function Kpi({ label, children, hint }: { label: string; children: ReactNode; hint?: string }) {
  return (
    <div className="rounded-xl border border-line bg-surface p-4 shadow-[0_1px_2px_rgb(0_0_0/0.04)]" title={hint}>
      <div className="text-[13px] font-medium text-ink-2">{label}</div>
      <div className="mt-1 font-display text-[30px] leading-tight font-semibold text-heading">{children}</div>
      {hint && <div className="mt-0.5 text-xs text-ink-3">{hint}</div>}
    </div>
  );
}

function ChartCard({ number, title, caption, rows, unit, asTable, total, keepOrder, delay = 0 }: {
  number: number; title: string; caption: string; rows: BarRow[]; unit: string; asTable: boolean; total?: number; keepOrder?: boolean; delay?: number;
}) {
  return (
    <Reveal delay={delay}>
      <Card className="h-full">
        <CardTitle number={number}>{title}</CardTitle>
        <p className="-mt-2 mb-4 text-[13px] text-ink-3">{caption}</p>
        {asTable ? <DataTable rows={rows} unit={unit} /> : <BarList rows={rows} unit={unit} total={total} keepOrder={keepOrder} />}
      </Card>
    </Reveal>
  );
}

export function AnalyticsPage() {
  const { data: a, isLoading, error } = useAnalytics();
  const [asTable, setAsTable] = useState(false);
  if (error) return <ErrorState error={error} />;

  const toggle = (
    <button onClick={() => setAsTable(!asTable)} aria-pressed={asTable}
      className="inline-flex min-h-10 cursor-pointer items-center gap-2 rounded-xl border border-line bg-surface px-3.5 text-sm font-medium text-ink-2 transition hover:text-ink">
      <Table2 className="size-4" aria-hidden />{asTable ? "Show charts" : "Show as tables"}
    </button>
  );

  if (isLoading || !a) {
    return (
      <div>
        <PageHeader title="Analytics" aside={toggle} />
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">{Array.from({ length: 5 }, (_, i) => <Skeleton key={i} className="h-28 rounded-2xl" />)}</div>
        <Skeleton className="mt-6 h-80 rounded-2xl" />
      </div>
    );
  }

  const started = a.totals.started ?? 0;
  return (
    <div>
      <PageHeader
        title="Analytics"
        subtitle="Is Sofía fixing the two problems? Candidates finishing the screening (the 60% who never answered calls) and recruiters only seeing qualified people (the 80% of wasted time)."
        aside={toggle}
      />

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
        <Kpi label="Completion rate" hint="Finished / (finished + abandoned)">
          {a.completion_rate === null ? "–" : <CountUp value={a.completion_rate * 100} format={(v) => `${Math.round(v)}%`} />}
        </Kpi>
        <Kpi label="Qualified" hint="Of finished screenings">
          {a.qualified_rate === null ? "–" : <CountUp value={a.qualified_rate * 100} format={(v) => `${Math.round(v)}%`} />}
        </Kpi>
        <Kpi label="Median time to finish" hint="From first message to outcome">
          {a.median_minutes_to_finish === null ? "–" : <CountUp value={a.median_minutes_to_finish} format={(v) => `${Math.round(v)} min`} />}
        </Kpi>
        <Kpi label="Median replies" hint="Candidate messages per screening">
          {a.median_candidate_messages === null ? "–" : <CountUp value={a.median_candidate_messages} />}
        </Kpi>
        <Kpi label="Human overrides" hint="Recruiter decisions against the bot">
          <CountUp value={a.human_overrides} />
        </Kpi>
      </div>

      <div className="mt-6">
        <ChartCard number={1} title="Funnel" unit="candidates" asTable={asTable} total={started} keepOrder
          caption="Candidates who got past each question. The drops at License and City are the knock-outs doing their job."
          rows={a.funnel.map((s) => ({ label: s.step, value: s.count }))} />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <ChartCard number={2} title="Why candidates are knocked out" unit="candidates" asTable={asTable}
          caption="Disqualification reasons. Each one is a rule set by the client." rows={toRows(a.knockout_reasons, (k) => REASONS[k] ?? k)} />
        <ChartCard number={3} title="Where abandoned candidates stopped" unit="candidates" asTable={asTable} delay={0.08}
          caption="The pending question when the last reminder went unanswered." rows={toRows(a.drop_off)} />
        <ChartCard number={4} title="Where candidates get frustrated" unit="messages" asTable={asTable}
          caption="Frustrated messages by the question being asked: candidates for rewording." rows={toRows(a.frustration_by_field)} />
        <ChartCard number={5} title="What candidates ask" unit="questions" asTable={asTable} delay={0.08}
          caption="Questions answered from the client's FAQ, by topic." rows={toRows(a.faq_usage, titleCase)} />
      </div>

      <Reveal className="mt-6">
        <Card>
          <CardTitle number={6}>Re-engagement</CardTitle>
          <p className="-mt-2 mb-6 max-w-3xl text-[13px] text-ink-3">
            Silent candidates get up to 3 reminders (+2 h, +24 h, +72 h), never at night in their timezone. Recovery rate = candidates who replied after a reminder: the direct measure of the 60% no-answer problem.
          </p>
          <div className="grid items-center gap-8 md:grid-cols-[auto_1fr]">
            <div className="flex flex-col items-center gap-3">
              <Meter value={a.recovery_rate} label="recovered" />
              <p className="num text-center text-sm text-ink-2">{a.candidates_recovered} of {a.candidates_nudged} nudged · {a.followups_sent} reminders sent</p>
            </div>
            <div>
              <div className="mb-3 text-sm font-medium text-ink">Which reminder brought them back</div>
              {asTable ? <DataTable rows={toRows(a.recovered_by_followup)} unit="candidates" />
                : <BarList rows={toRows(a.recovered_by_followup)} unit="candidates" keepOrder emptyText="Nobody recovered yet: reminders are sent as candidates go silent." />}
            </div>
          </div>
        </Card>
      </Reveal>

      <div className="mt-6 grid gap-6 lg:grid-cols-[1.2fr_1fr]">
        <Reveal>
          <Card className="h-full">
            <CardTitle number={7}>Questions Sofía couldn't answer</CardTitle>
            <p className="-mt-2 mb-3 text-[13px] text-ink-3">She never improvises: each one is a candidate for the FAQ.</p>
            {a.unanswered_questions.length ? (
              <ul className="divide-y divide-line">
                {a.unanswered_questions.map((q, i) => <li key={i} className="py-2.5 text-sm text-ink">“{q}”</li>)}
              </ul>
            ) : <p className="py-4 text-sm text-ink-3">None so far.</p>}
          </Card>
        </Reveal>
        <Reveal delay={0.08}>
          <Card className="h-full">
            <CardTitle number={8}>AI health</CardTitle>
            <dl className="grid grid-cols-2 gap-4">
              {[
                ["Template fallback rate", pct(a.template_fallback_rate), "Messages written by templates because the model failed or its draft was rejected"],
                ["LLM errors", String(a.llm_errors), "API errors, timeouts, refusals"],
                ["Guard rejections", String(a.guard_rejections), "Drafts rejected for length, markdown or leaked instructions"],
                ["Spain / Mexico", `${a.countries.ES ?? 0} / ${a.countries.MX ?? 0}`, "Candidates by country of their city"],
              ].map(([label, value, hint]) => (
                <div key={label} className="rounded-xl bg-surface-2 p-3" title={hint}>
                  <dt className="text-xs text-ink-3">{label}</dt>
                  <dd className="num mt-0.5 text-xl font-semibold text-ink">{value}</dd>
                </div>
              ))}
            </dl>
            <div className="mt-4 flex flex-wrap gap-2 text-xs text-ink-2">
              {Object.entries(a.languages).map(([k, v]) => <span key={k} className="rounded-md bg-surface-2 px-2 py-1">{k.toUpperCase()} · {v}</span>)}
            </div>
          </Card>
        </Reveal>
      </div>
    </div>
  );
}
