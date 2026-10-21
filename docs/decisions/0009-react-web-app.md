# ADR 0009: Replace the Streamlit dashboard with a React web app

**Status:** accepted. Supersedes the UI choice of [ADR 0008](0008-api-first-recruiter-tool.md); its API-first architecture stands.

## Context
The Streamlit dashboard (ADR 0008) proved the recruiter workflow, but a product recruiters adopt needs more than that:
- interactions that feel immediate;
- motion that explains what changed (data that grows into view, a checklist that ticks as the agent collects answers);
- a polished light and dark theme.

Streamlit re-runs the whole script on every interaction and renders charts in iframes, so none of that is controllable.

## Decision
- **Stack:** React 19 + TypeScript + Vite + Tailwind CSS 4 + Motion, with TanStack Query for server state and React Router.
- **Served by FastAPI.** The built app (`web/dist`) is served at `/`, and the API moved under `/api`. Production is **one process**. During development Vite serves the app and proxies `/api`.
- **Design system as tokens.** Semantic colour tokens are defined for light and dark together, and every text/surface pair is checked for **WCAG AA contrast** (one muted text token was darkened, and the primary button uses a darker orange so white labels reach 5.2:1). Data colour is separate from brand colour. Fonts: Calistoga (display), Inter (text), JetBrains Mono (data).
- **Charts built in-house** instead of a chart library:
  - bars grow as they scroll into view by animating `transform: scaleX`, never `width`, so there are no layout shifts;
  - thin bars with a rounded data end and the value at the tip;
  - tooltips, keyboard focus, a text summary for screen readers, and a "show as tables" toggle.
- **Motion with meaning:**
  - counters count up, bars grow, lists stagger in;
  - the screening checklist ticks as values are captured;
  - the agent shows a typing indicator.

  Everything respects `prefers-reduced-motion`.
- **Route-level code splitting:** the pipeline loads first, the other pages load on demand.
- **The Streamlit dashboard is removed** (it remains in git history): two UIs would double the maintenance.

## Alternatives considered
| Option | Why not |
|---|---|
| Keep Streamlit + custom CSS/JS components | Iframe-isolated components and full-page reruns: the effects asked for would be hacks |
| A chart library (Recharts, ECharts) | Fast to start, but scroll-triggered growth, rounded data ends and accessibility details would fight the library's defaults |
| Next.js | Server rendering and routing conventions bring nothing for an internal tool behind an API; more to explain |
| No build step (vanilla JS + CDN) | No toolchain needed, but no components or types, and a weaker signal of production practice |

## Trade-offs accepted
- **Building the web app needs Node 18+.** `make install` builds it when `npm` is available; the API works without it. `web/dist` is not committed (build artefacts in git go stale).
- **More code to own and explain** than Streamlit: ~1,500 lines of TypeScript.
- **TypeScript 5, not 7:** 7 is the new native compiler. With a deadline, the established toolchain wins.

## Revisit when
Several recruiters and clients use it: then add authentication, roles, and real-time updates (WebSocket or SSE) instead of polling every 20 s.
