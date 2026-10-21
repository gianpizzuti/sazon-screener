/** Typed client for the FastAPI backend (/api). Types mirror the Pydantic models. */

export type Status =
  | "qualified"
  | "needs_review"
  | "in_progress"
  | "awaiting_reply"
  | "abandoned"
  | "disqualified"
  | "withdrawn"
  | "terminated";

export type ReviewStatus = "new" | "contacted" | "interview" | "hired" | "rejected";

export interface CandidateRow {
  id: string;
  status: Status;
  needs_review: boolean;
  review_status: ReviewStatus;
  name: string | null;
  city: string | null;
  zone: string | null;
  country: string | null;
  availability: string[];
  schedule: string[];
  experience_months: number | null;
  platforms: string[];
  start_date: string | null;
  language: string;
  channel: string;
  disqualification_reason: string | null;
  flags: string[];
  open_questions: number;
  headline: string | null;
  followups_sent: number;
  next_followup_at: string | null;
  created_at: string;
  last_activity: string;
  priority: number;
}

export interface ScreeningData {
  full_name: string | null;
  has_drivers_license: boolean | null;
  license_status: "yes" | "no" | "in_progress" | null;
  location_raw: string | null;
  city: string | null;
  country: string | null;
  zone: string | null;
  in_service_area: boolean | null;
  availability: string[];
  preferred_schedule: string[];
  experience_years: number | null;
  experience_months: number | null;
  experience_platforms: string[];
  start_date: string | null;
  start_date_raw: string | null;
}

export interface Analysis {
  language: "es" | "en";
  language_is_clear: boolean;
  spanish_variant: string;
  intents: string[];
  sentiment: string;
  question: string | null;
  faq_id: string | null;
  correction_target: string | null;
  extracted: Record<string, unknown>;
  evidence: { field: string; quote: string }[];
}

export interface Message {
  role: "agent" | "candidate";
  text: string;
  created_at: string;
  meta: {
    kind?: string;
    source?: "llm" | "template";
    attempt?: number;
    whatsapp_template_required?: boolean;
    analysis?: Analysis;
    directive?: Record<string, unknown>;
    error?: string;
  };
}

export interface Summary {
  headline: string;
  summary: string;
  strengths: string[];
  concerns: string[];
  candidate_questions: string[];
  recommended_action: string;
  source: "llm" | "template";
}

export interface Review {
  status: ReviewStatus;
  note: string;
  updated_by: string;
  updated_at: string | null;
}

export interface CandidateDetail {
  row: CandidateRow;
  data: ScreeningData;
  fields: { field: string; status: string; evidence: string | null; failed_attempts: number }[];
  flags: { code: string; detail: string; at: string }[];
  pending_questions: string[];
  talent_pool_opt_in: boolean | null;
  summary: Summary | null;
  review: Review;
  transcript: Message[];
  events: { type: string; payload: Record<string, unknown>; created_at: string }[];
}

export interface Analytics {
  totals: Record<string, number>;
  completion_rate: number | null;
  qualified_rate: number | null;
  funnel: { step: string; count: number }[];
  drop_off: Record<string, number>;
  knockout_reasons: Record<string, number>;
  median_minutes_to_finish: number | null;
  median_candidate_messages: number | null;
  languages: Record<string, number>;
  countries: Record<string, number>;
  frustration_by_field: Record<string, number>;
  faq_usage: Record<string, number>;
  unanswered_questions: string[];
  template_fallback_rate: number | null;
  llm_errors: number;
  guard_rejections: number;
  human_overrides: number;
  followups_sent: number;
  candidates_nudged: number;
  candidates_recovered: number;
  recovery_rate: number | null;
  recovered_by_followup: Record<string, number>;
}

export interface TurnResult {
  conversation_id: string;
  stage: string;
  messages: { text: string; quick_replies: string[] }[];
  completed: boolean;
  data: ScreeningData;
  analysis: Analysis | null;
  event_types: string[];
}

export interface DemoClock {
  now: string;
  offset_hours: number;
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`/api${path}`, {
      method,
      headers: body === undefined ? undefined : { "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError(0, "The API is not reachable. Start it with `make run`.");
  }
  if (!response.ok) {
    const text = await response.text();
    throw new ApiError(response.status, text || response.statusText);
  }
  return response.status === 204 ? (undefined as T) : ((await response.json()) as T);
}

export const api = {
  health: () => request<{ status: string; now: string }>("GET", "/health"),
  candidates: () => request<CandidateRow[]>("GET", "/candidates"),
  candidate: (id: string) => request<CandidateDetail>("GET", `/candidates/${id}`),
  review: (id: string, body: { status: ReviewStatus; note: string; by: string }) =>
    request<Review>("PUT", `/candidates/${id}/review`, body),
  erase: (id: string) => request<void>("DELETE", `/candidates/${id}`),
  regenerateSummary: (id: string) => request<Summary>("POST", `/candidates/${id}/summary`),
  analytics: () => request<Analytics>("GET", "/analytics"),
  start: (language: "es" | "en") => request<TurnResult>("POST", "/conversations", { channel: "web", language }),
  send: (id: string, text: string) =>
    request<TurnResult>("POST", `/conversations/${id}/messages?debug=true`, { text }),
  demoClock: async (): Promise<DemoClock | null> => {
    try {
      return await request<DemoClock>("GET", "/demo/clock");
    } catch (error) {
      if (error instanceof ApiError && error.status === 404) return null; // demo tools disabled
      throw error;
    }
  },
  advance: (hours: number) =>
    request<DemoClock & { actions: { action: string; attempt?: number }[] }>("POST", "/demo/advance", { hours }),
};
