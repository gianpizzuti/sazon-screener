import clsx from "clsx";
import {
  Ban,
  CircleCheck,
  Hourglass,
  type LucideIcon,
  MessageCircle,
  MoonStar,
  ShieldOff,
  TriangleAlert,
  Undo2,
} from "lucide-react";
import type { ButtonHTMLAttributes, ReactNode } from "react";

import type { Status } from "../lib/api";

export function Card({ className, children }: { className?: string; children: ReactNode }) {
  return (
    <section className={clsx("rounded-2xl border border-line bg-surface p-5 shadow-[0_1px_2px_rgb(0_0_0/0.04)]", className)}>
      {children}
    </section>
  );
}

export function CardTitle({ icon: Icon, children, aside }: { icon?: LucideIcon; children: ReactNode; aside?: ReactNode }) {
  return (
    <div className="mb-4 flex items-center justify-between gap-3">
      <h2 className="flex items-center gap-2 text-[15px] font-semibold text-ink">
        {Icon && <Icon className="size-4 text-brand" aria-hidden />}
        {children}
      </h2>
      {aside}
    </div>
  );
}

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  icon?: LucideIcon;
  loading?: boolean;
};

export function Button({ variant = "secondary", icon: Icon, loading, className, children, disabled, ...rest }: ButtonProps) {
  return (
    <button
      {...rest}
      disabled={disabled || loading}
      className={clsx(
        "inline-flex min-h-10 cursor-pointer items-center justify-center gap-2 rounded-xl px-4 text-sm font-medium",
        "transition-[background-color,transform,box-shadow] duration-150 active:scale-[0.97] disabled:cursor-not-allowed disabled:opacity-50",
        variant === "primary" && "bg-brand-btn text-white shadow-sm hover:brightness-110",
        variant === "secondary" && "border border-line bg-surface text-ink hover:bg-surface-2",
        variant === "ghost" && "text-ink-2 hover:bg-surface-2 hover:text-ink",
        variant === "danger" && "bg-rose-700 text-white hover:bg-rose-800",
        className,
      )}
    >
      {loading ? <span className="size-4 animate-spin rounded-full border-2 border-current border-t-transparent" /> : Icon && <Icon className="size-4" aria-hidden />}
      {children}
    </button>
  );
}

const STATUS: Record<Status, { label: string; icon: LucideIcon; tone: string }> = {
  qualified: { label: "Qualified", icon: CircleCheck, tone: "bg-emerald-50 text-emerald-800 ring-emerald-600/20 dark:bg-emerald-400/10 dark:text-emerald-300 dark:ring-emerald-400/25" },
  needs_review: { label: "Needs review", icon: TriangleAlert, tone: "bg-amber-50 text-amber-900 ring-amber-600/25 dark:bg-amber-400/10 dark:text-amber-300 dark:ring-amber-400/25" },
  in_progress: { label: "In progress", icon: MessageCircle, tone: "bg-sky-50 text-sky-800 ring-sky-600/20 dark:bg-sky-400/10 dark:text-sky-300 dark:ring-sky-400/25" },
  awaiting_reply: { label: "Awaiting reply", icon: Hourglass, tone: "bg-violet-50 text-violet-800 ring-violet-600/20 dark:bg-violet-400/10 dark:text-violet-300 dark:ring-violet-400/25" },
  abandoned: { label: "Abandoned", icon: MoonStar, tone: "bg-stone-100 text-stone-700 ring-stone-500/20 dark:bg-stone-400/10 dark:text-stone-300 dark:ring-stone-400/20" },
  disqualified: { label: "Disqualified", icon: Ban, tone: "bg-rose-50 text-rose-800 ring-rose-600/20 dark:bg-rose-400/10 dark:text-rose-300 dark:ring-rose-400/25" },
  withdrawn: { label: "Withdrawn", icon: Undo2, tone: "bg-stone-100 text-stone-700 ring-stone-500/20 dark:bg-stone-400/10 dark:text-stone-300 dark:ring-stone-400/20" },
  terminated: { label: "Closed", icon: ShieldOff, tone: "bg-stone-100 text-stone-700 ring-stone-500/20 dark:bg-stone-400/10 dark:text-stone-300 dark:ring-stone-400/20" },
};

export const STATUS_ORDER: Status[] = ["qualified", "needs_review", "in_progress", "awaiting_reply", "abandoned", "disqualified", "withdrawn", "terminated"];

export function statusMeta(status: Status) {
  return STATUS[status] ?? STATUS.in_progress;
}

/** Status is always icon + label: colour never carries meaning alone. */
export function StatusBadge({ status, size = "md" }: { status: Status; size?: "sm" | "md" }) {
  const { label, icon: Icon, tone } = statusMeta(status);
  return (
    <span className={clsx("inline-flex shrink-0 items-center gap-1.5 rounded-full font-medium ring-1 ring-inset", tone,
      size === "sm" ? "px-2 py-0.5 text-xs" : "px-2.5 py-1 text-[13px]")}>
      <Icon className={size === "sm" ? "size-3" : "size-3.5"} aria-hidden />
      {label}
    </span>
  );
}

export function Chip({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <span className={clsx("inline-flex items-center gap-1 rounded-md bg-surface-2 px-2 py-0.5 text-xs font-medium text-ink-2", className)}>
      {children}
    </span>
  );
}

export function Skeleton({ className }: { className?: string }) {
  return <div className={clsx("animate-pulse rounded-lg bg-surface-2", className)} aria-hidden />;
}

export function EmptyState({ icon: Icon, title, children }: { icon: LucideIcon; title: string; children?: ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center gap-2 py-12 text-center">
      <div className="mb-1 grid size-12 place-items-center rounded-2xl bg-surface-2">
        <Icon className="size-5 text-ink-3" aria-hidden />
      </div>
      <p className="font-medium text-ink">{title}</p>
      {children && <div className="max-w-sm text-sm text-ink-3">{children}</div>}
    </div>
  );
}

export function ErrorState({ error }: { error: unknown }) {
  return (
    <Card className="border-rose-300/60">
      <p className="font-medium text-rose-700 dark:text-rose-300">Something went wrong</p>
      <p className="mt-1 text-sm text-ink-2">{error instanceof Error ? error.message : String(error)}</p>
    </Card>
  );
}

export function PageHeader({ title, subtitle, aside }: { title: string; subtitle?: ReactNode; aside?: ReactNode }) {
  return (
    <header className="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 className="font-display text-3xl tracking-tight text-ink sm:text-[34px]">{title}</h1>
        {subtitle && <p className="mt-1.5 max-w-2xl text-[15px] text-ink-2">{subtitle}</p>}
      </div>
      {aside}
    </header>
  );
}
