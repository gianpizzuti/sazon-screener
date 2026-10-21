import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import clsx from "clsx";
import { ChartNoAxesColumn, CircleCheck, Clock, FastForward, Info, MessagesSquare, Moon, Sun, Users } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { type ReactNode, useCallback, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";

import { api } from "../lib/api";
import { type Toast, ToastContext } from "../lib/hooks";

const NAV = [
  { to: "/", label: "Pipeline", icon: Users, end: true },
  { to: "/analytics", label: "Analytics", icon: ChartNoAxesColumn },
  { to: "/try", label: "Try the agent", icon: MessagesSquare },
];

/** The client's workspace: recruiters work "in Grupo Sazón" (each client is a config folder). */
function Workspace({ compact = false }: { compact?: boolean }) {
  return (
    <div className="flex items-center gap-2.5 px-2">
      <div className="grid size-9 shrink-0 place-items-center rounded-lg bg-brand-btn font-display text-[15px] font-semibold text-on-brand shadow-sm">GS</div>
      <div className={clsx("min-w-0 leading-tight", compact && "hidden sm:block")}>
        <div className="truncate font-display text-[17px] font-semibold text-heading">Grupo Sazón</div>
        <div className="text-[11px] font-medium tracking-wide text-ink-3 uppercase">Recruiting</div>
      </div>
    </div>
  );
}

function ThemeToggle() {
  const [dark, setDark] = useState(() => document.documentElement.classList.contains("dark"));
  const toggle = () => {
    const next = !dark;
    document.documentElement.classList.toggle("dark", next);
    try { localStorage.setItem("theme", next ? "dark" : "light"); } catch { /* storage may be blocked */ }
    setDark(next);
  };
  return (
    <button onClick={toggle} aria-label={dark ? "Switch to light theme" : "Switch to dark theme"}
      className="grid size-10 cursor-pointer place-items-center rounded-xl border border-line bg-surface text-ink-2 transition hover:text-ink">
      <motion.span key={String(dark)} initial={{ rotate: -45, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} transition={{ duration: 0.2 }}>
        {dark ? <Sun className="size-4" /> : <Moon className="size-4" />}
      </motion.span>
    </button>
  );
}

function DemoClock({ notify }: { notify: (text: string) => void }) {
  const client = useQueryClient();
  const { data: clock } = useQuery({ queryKey: ["demo-clock"], queryFn: api.demoClock, refetchInterval: 30_000 });
  const advance = useMutation({
    mutationFn: api.advance,
    onSuccess: (result) => {
      const sent = result.actions.filter((a) => a.action === "followup").length;
      const gaveUp = result.actions.filter((a) => a.action === "abandoned").length;
      notify(`Time moved forward: ${sent} follow-up${sent === 1 ? "" : "s"} sent, ${gaveUp} marked abandoned`);
      client.invalidateQueries();
    },
  });
  const [open, setOpen] = useState(false);
  if (!clock) return null;
  const now = new Date(`${clock.now}Z`);
  const steps: [string, number][] = [["+2 h", 2], ["+1 day", 24], ["+3 days", 72]];
  return (
    <>
      {/* Phones: a compact button with a menu, so the top bar never overflows. */}
      <div className="relative sm:hidden">
        <button onClick={() => setOpen(!open)} aria-expanded={open} aria-label="Demo clock"
          className="grid size-10 cursor-pointer place-items-center rounded-xl border border-line bg-surface text-brand-ink">
          <Clock className="size-4" />
        </button>
        <AnimatePresence>
          {open && (
            <motion.div initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              className="absolute right-0 z-30 mt-2 w-56 rounded-xl border border-line bg-surface p-2 shadow-xl">
              <div className="px-2 pb-2 text-xs text-ink-3">Demo clock{clock.offset_hours ? ` · +${Math.round(clock.offset_hours)} h` : ""}</div>
              {steps.map(([label, hours]) => (
                <button key={label} disabled={advance.isPending} onClick={() => { advance.mutate(hours); setOpen(false); }}
                  className="flex min-h-10 w-full cursor-pointer items-center gap-2 rounded-lg px-2 text-sm text-ink hover:bg-surface-2">
                  <FastForward className="size-4 text-ink-3" />{label}
                </button>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    <div className="hidden items-center gap-1 rounded-xl border border-line bg-surface p-1 pl-3 shadow-sm sm:flex">
      <Clock className="size-4 text-brand-ink" aria-hidden />
      <div className="mr-1 leading-tight">
        <div className="text-[11px] font-medium tracking-wide text-ink-3 uppercase">Demo clock{clock.offset_hours ? ` · +${Math.round(clock.offset_hours)} h` : ""}</div>
        <div className="num text-[13px] font-medium text-ink">
          {now.toLocaleString("en-GB", { weekday: "short", day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit", timeZone: "Europe/Madrid" })} <span className="text-ink-3">Madrid</span>
        </div>
      </div>
      {steps.map(([label, hours]) => (
        <button key={label} disabled={advance.isPending} onClick={() => advance.mutate(hours)}
          title="Move time forward for the whole system: follow-ups go out as they would in real life"
          className="inline-flex h-8 cursor-pointer items-center gap-1 rounded-lg px-2.5 text-[13px] font-medium text-ink-2 transition hover:bg-surface-2 hover:text-ink disabled:opacity-50">
          <FastForward className="size-3.5" aria-hidden />{label}
        </button>
      ))}
    </div>
    </>
  );
}

export function Layout({ children }: { children: ReactNode }) {
  const location = useLocation();
  const [toasts, setToasts] = useState<Toast[]>([]);
  const notify = useCallback((text: string, tone: Toast["tone"] = "success") => {
    const id = Date.now() + Math.random();
    setToasts((t) => [...t, { id, text, tone }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 4000);
  }, []);

  return (
    <ToastContext.Provider value={notify}>
      <a href="#main" className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-50 focus:rounded-lg focus:bg-surface focus:px-3 focus:py-2">Skip to content</a>
      <div className="min-h-dvh lg:grid lg:grid-cols-[232px_1fr]">
        <aside className="sticky top-0 hidden h-dvh flex-col gap-8 border-r border-line bg-surface/60 px-4 py-6 backdrop-blur lg:flex">
          <Workspace />
          <nav aria-label="Main" className="flex flex-col gap-1">
            {NAV.map(({ to, label, icon: Icon, end }) => (
              <NavLink key={to} to={to} end={end}
                className={({ isActive }) => clsx(
                  "relative flex min-h-10 items-center gap-3 rounded-xl px-3 text-sm font-medium transition-colors",
                  isActive ? "text-ink" : "text-ink-2 hover:bg-surface-2 hover:text-ink",
                )}>
                {({ isActive }) => (
                  <>
                    {isActive && <motion.span layoutId="nav-active" className="absolute inset-0 rounded-xl bg-brand-soft ring-1 ring-brand/20" transition={{ type: "spring", stiffness: 380, damping: 32 }} />}
                    <Icon className={clsx("relative size-[18px]", isActive && "text-brand-ink")} aria-hidden />
                    <span className="relative">{label}</span>
                  </>
                )}
              </NavLink>
            ))}
          </nav>
          <div className="mt-auto rounded-2xl bg-surface-2 p-3.5 text-[13px] leading-snug text-ink-2">
            <div className="mb-1 flex items-center gap-1.5 font-semibold text-ink"><Info className="size-3.5 text-brand-ink" />Human in the loop</div>
            Sofía (AI) screens; every outcome can be overridden by a recruiter, and every override is logged.
          </div>
        </aside>

        <div className="min-w-0">
          <header className="sticky top-0 z-20 border-b border-line bg-bg/80 backdrop-blur-md">
            <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-3 px-4 sm:px-6">
              <div className="flex items-center gap-2 lg:hidden"><Workspace compact /></div>
              <nav aria-label="Main mobile" className="flex gap-1 lg:hidden">
                {NAV.map(({ to, icon: Icon, label, end }) => (
                  <NavLink key={to} to={to} end={end} aria-label={label}
                    className={({ isActive }) => clsx("grid size-10 place-items-center rounded-xl", isActive ? "bg-brand-soft text-brand-ink" : "text-ink-2")}>
                    <Icon className="size-[18px]" />
                  </NavLink>
                ))}
              </nav>
              <div className="ml-auto flex items-center gap-2">
                <DemoClock notify={notify} />
                <ThemeToggle />
              </div>
            </div>
          </header>
          <main id="main" className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
            {/* Enter-only page transition: an exit animation with AnimatePresence + a router
                that renders the new route inside the exiting element left pages stuck invisible. */}
            <motion.div key={location.pathname} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.22, ease: [0.22, 1, 0.36, 1] }}>
              {children}
            </motion.div>
          </main>
        </div>
      </div>

      <div aria-live="polite" className="pointer-events-none fixed right-4 bottom-4 z-50 flex flex-col gap-2">
        <AnimatePresence>
          {toasts.map((t) => (
            <motion.div key={t.id} layout initial={{ opacity: 0, y: 12, scale: 0.98 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: 6 }}
              transition={{ duration: 0.2 }}
              className="pointer-events-auto flex max-w-sm items-center gap-2.5 rounded-xl border border-line bg-surface px-4 py-3 text-sm text-ink shadow-xl">
              <CircleCheck className={clsx("size-4 shrink-0", t.tone === "error" ? "text-rose-600" : "text-emerald-600")} aria-hidden />
              {t.text}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
}
