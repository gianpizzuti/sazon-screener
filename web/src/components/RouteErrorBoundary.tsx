import { Component, type ReactNode } from "react";

import { Button, Card } from "./ui";

const RELOADED_AT = "chunk-reload-at";

/** A page's code failed to load: after a new build (old file names are gone) or with the server down. */
function isChunkLoadError(error: unknown): boolean {
  const text = error instanceof Error ? `${error.name} ${error.message}` : String(error);
  return /dynamically imported module|module script failed|Loading chunk|Failed to fetch/i.test(text);
}

/**
 * Keeps one failing page from blanking the whole app (React unmounts everything on an uncaught
 * render error). A page whose code can't load is reloaded once, which picks up the new build;
 * if that doesn't help (e.g. the server is down), the error is shown with a Reload button.
 */
export class RouteErrorBoundary extends Component<{ children: ReactNode }, { error: unknown }> {
  state = { error: null as unknown };

  static getDerivedStateFromError(error: unknown) {
    return { error };
  }

  componentDidCatch(error: unknown) {
    if (!isChunkLoadError(error)) return;
    // Reload only if the server answers (a new build is there to pick up): with the server down,
    // a reload would replace this message with the browser's own error page.
    fetch("/", { method: "HEAD", cache: "no-store" })
      .then((response) => {
        let last = 0;
        try { last = Number(sessionStorage.getItem(RELOADED_AT) ?? 0); } catch { /* storage may be blocked */ }
        if (!response.ok || Date.now() - last < 30_000) return;  // at most one automatic reload
        try { sessionStorage.setItem(RELOADED_AT, String(Date.now())); } catch { /* storage may be blocked */ }
        window.location.reload();
      })
      .catch(() => { /* server unreachable: keep the message */ });
  }

  render() {
    if (!this.state.error) return this.props.children;
    const chunk = isChunkLoadError(this.state.error);
    return (
      <Card className="border-rose-300/60">
        <p className="font-medium text-rose-700 dark:text-rose-300">{chunk ? "This page couldn't load" : "Something went wrong on this page"}</p>
        <p className="mt-1 text-sm text-ink-2">
          {chunk ? "The server may not be running: start it with make run, then reload." : String(this.state.error)}
        </p>
        <Button className="mt-4" onClick={() => window.location.reload()}>Reload</Button>
      </Card>
    );
  }
}
