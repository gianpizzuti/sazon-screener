import { useQuery } from "@tanstack/react-query";
import { createContext, useContext } from "react";

import { api } from "./api";

/** The server's clock (a simulated one in demo mode), so "2 h ago" matches the backend. */
export function useNow(): Date {
  const { data } = useQuery({ queryKey: ["health"], queryFn: api.health, refetchInterval: 30_000 });
  return data ? new Date(`${data.now}Z`) : new Date();
}

export function useCandidates() {
  return useQuery({ queryKey: ["candidates"], queryFn: api.candidates, refetchInterval: 20_000 });
}

export function useCandidate(id: string | undefined) {
  return useQuery({ queryKey: ["candidate", id], queryFn: () => api.candidate(id!), enabled: !!id, refetchInterval: 20_000 });
}

export function useAnalytics() {
  return useQuery({ queryKey: ["analytics"], queryFn: api.analytics, refetchInterval: 30_000 });
}

export type Toast = { id: number; text: string; tone?: "success" | "info" | "error" };
export const ToastContext = createContext<(text: string, tone?: Toast["tone"]) => void>(() => {});
export const useToast = () => useContext(ToastContext);
