import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MotionConfig } from "motion/react";
import { lazy, StrictMode, Suspense } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import { Layout } from "./components/Layout";
import "./index.css";
import { PipelinePage } from "./pages/Pipeline";

// Route-level code splitting: the landing page loads first, the rest on demand.
const CandidatePage = lazy(() => import("./pages/Candidate").then((m) => ({ default: m.CandidatePage })));
const AnalyticsPage = lazy(() => import("./pages/Analytics").then((m) => ({ default: m.AnalyticsPage })));
const TryAgentPage = lazy(() => import("./pages/TryAgent").then((m) => ({ default: m.TryAgentPage })));

const queryClient = new QueryClient({ defaultOptions: { queries: { staleTime: 5_000, retry: 1 } } });

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      {/* reducedMotion="user": animations collapse to their end state when the OS asks for less motion */}
      <MotionConfig reducedMotion="user">
        <BrowserRouter>
          <Layout>
            <Suspense fallback={<div className="h-64 animate-pulse rounded-2xl bg-surface-2" />}>
              <Routes>
                <Route path="/" element={<PipelinePage />} />
                <Route path="/candidates/:id" element={<CandidatePage />} />
                <Route path="/analytics" element={<AnalyticsPage />} />
                <Route path="/try" element={<TryAgentPage />} />
              </Routes>
            </Suspense>
          </Layout>
        </BrowserRouter>
      </MotionConfig>
    </QueryClientProvider>
  </StrictMode>,
);
