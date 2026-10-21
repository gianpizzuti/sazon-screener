/**
 * Data components. Rules (docs/decisions, D93): one validated data colour for single
 * series, thin bars with a rounded data end, the value at the tip, a tooltip, keyboard
 * focus, a text summary for screen readers, and animation that never hides the data:
 * with reduced motion everything renders in its final state immediately.
 */
import { animate, motion, useInView, useReducedMotion } from "motion/react";
import { type ReactNode, useEffect, useRef, useState } from "react";

const EASE = [0.22, 1, 0.36, 1] as const; // ease-out: things arriving

export function CountUp({ value, format = (v) => String(Math.round(v)), className }: {
  value: number;
  format?: (v: number) => string;
  className?: string;
}) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, amount: 0.6 });
  const reduce = useReducedMotion();
  const [shown, setShown] = useState(reduce ? value : 0);

  useEffect(() => {
    if (!inView) return;
    if (reduce) return setShown(value);
    const controls = animate(0, value, { duration: 0.9, ease: EASE, onUpdate: setShown });
    return () => controls.stop();
  }, [inView, value, reduce]);

  return (
    <span ref={ref} className={`num ${className ?? ""}`} aria-label={format(value)}>
      {format(shown)}
    </span>
  );
}

export function Reveal({ children, delay = 0, className }: { children: ReactNode; delay?: number; className?: string }) {
  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.25 }}
      transition={{ duration: 0.45, ease: EASE, delay }}
    >
      {children}
    </motion.div>
  );
}

export interface BarRow {
  label: string;
  value: number;
}

/** Horizontal single-series bars that grow as they scroll into view. */
export function BarList({ rows, unit, total, keepOrder = false, emptyText = "No data yet." }: {
  rows: BarRow[];
  unit: string;
  total?: number; // when set, the tooltip also shows the share of this total
  keepOrder?: boolean;
  emptyText?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, amount: 0.3 });
  const [hover, setHover] = useState<number | null>(null);
  const sorted = keepOrder ? rows : [...rows].sort((a, b) => b.value - a.value);
  const max = Math.max(1, ...sorted.map((r) => r.value));

  if (!rows.length) return <p className="py-6 text-sm text-ink-3">{emptyText}</p>;

  const summary = sorted.map((r) => `${r.label}: ${r.value} ${unit}`).join("; ");
  return (
    <div ref={ref} role="list" aria-label={summary} className="space-y-2.5">
      {sorted.map((row, i) => {
        const width = (row.value / max) * 100;
        const share = total ? Math.round((row.value / total) * 100) : null;
        return (
          <div
            key={row.label}
            role="listitem"
            tabIndex={0}
            aria-label={`${row.label}: ${row.value} ${unit}${share !== null ? `, ${share}%` : ""}`}
            onMouseEnter={() => setHover(i)}
            onMouseLeave={() => setHover(null)}
            onFocus={() => setHover(i)}
            onBlur={() => setHover(null)}
            className="group relative grid grid-cols-[minmax(84px,30%)_1fr] items-center gap-3 rounded-lg outline-offset-4"
          >
            <span className="truncate text-[13px] text-ink-2" title={row.label}>{row.label}</span>
            <div className="relative flex h-6 items-center">
              <div className="absolute inset-y-0 left-0 w-full rounded-r-[4px] bg-grid/60" aria-hidden />
              <motion.div
                className="relative h-[18px] origin-left rounded-r-[4px] bg-series transition-[filter] group-hover:brightness-110"
                style={{ width: `${Math.max(width, 1.5)}%` }}
                initial={{ scaleX: 0 }}
                animate={{ scaleX: inView ? 1 : 0 }}
                transition={{ duration: 0.7, ease: EASE, delay: 0.06 * i }}
              />
              <motion.span
                className="num relative ml-2 text-[13px] font-semibold text-ink"
                initial={{ opacity: 0 }}
                animate={{ opacity: inView ? 1 : 0 }}
                transition={{ duration: 0.3, delay: 0.06 * i + 0.45 }}
              >
                {row.value}
                {share !== null && <span className="ml-1.5 font-normal text-ink-3">{share}%</span>}
              </motion.span>
              {hover === i && (
                <div className="pointer-events-none absolute -top-9 left-0 z-10 rounded-lg bg-ink px-2.5 py-1 text-xs whitespace-nowrap text-surface shadow-lg">
                  {row.label} · {row.value} {unit}
                  {share !== null && ` · ${share}% of ${total}`}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

/** A single ratio against its limit: a ring that fills as it scrolls into view. */
export function Meter({ value, label, size = 148 }: { value: number | null; label: string; size?: number }) {
  const ref = useRef<SVGSVGElement>(null);
  const inView = useInView(ref, { once: true, amount: 0.6 });
  const stroke = 12;
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const ratio = value ?? 0;
  return (
    <div className="relative grid place-items-center" style={{ width: size, height: size }}>
      <svg ref={ref} width={size} height={size} className="-rotate-90" role="img" aria-label={`${label}: ${value === null ? "no data" : Math.round(ratio * 100) + "%"}`}>
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--series-soft)" strokeWidth={stroke} />
        <motion.circle
          cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--series)" strokeWidth={stroke} strokeLinecap="round"
          strokeDasharray={c}
          initial={{ strokeDashoffset: c }}
          animate={{ strokeDashoffset: inView ? c * (1 - ratio) : c }}
          transition={{ duration: 1.1, ease: EASE }}
        />
      </svg>
      <div className="absolute text-center">
        <div className="font-display text-3xl font-semibold text-heading">
          {value === null ? "–" : <CountUp value={ratio * 100} format={(v) => `${Math.round(v)}%`} />}
        </div>
        <div className="text-xs text-ink-3">{label}</div>
      </div>
    </div>
  );
}

/** A small data table, the accessible alternative to every chart. */
export function DataTable({ rows, unit }: { rows: BarRow[]; unit: string }) {
  if (!rows.length) return <p className="py-6 text-sm text-ink-3">No data yet.</p>;
  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="text-left text-ink-3"><th className="py-1 font-medium"> </th><th className="py-1 text-right font-medium">{unit}</th></tr>
      </thead>
      <tbody>
        {rows.map((r) => (
          <tr key={r.label} className="border-t border-line"><td className="py-1.5 text-ink-2">{r.label}</td><td className="num py-1.5 text-right font-medium">{r.value}</td></tr>
        ))}
      </tbody>
    </table>
  );
}
