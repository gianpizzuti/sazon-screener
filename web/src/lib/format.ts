/** Labels and formatting shared by every page. */

export const AVAILABILITY: Record<string, string> = { full_time: "Full-time", part_time: "Part-time", weekends: "Weekends" };
export const SCHEDULE: Record<string, string> = { morning: "Morning", afternoon: "Afternoon", evening: "Evening", flexible: "Flexible" };
export const REASONS: Record<string, string> = {
  no_license: "No driver's license",
  license_in_progress: "License in progress",
  out_of_area: "Outside service area",
};
export const FIELD_LABELS: Record<string, string> = {
  full_name: "Name",
  drivers_license: "Driver's license",
  location: "City",
  zone: "Zone",
  availability: "Availability",
  schedule: "Shift",
  experience_years: "Experience",
  experience_platforms: "Platforms",
  start_date: "Start date",
};
export const FLAG_LABELS: Record<string, string> = {
  human_requested: "Asked for a person",
  late_start: "Late start",
  abuse: "Abusive language",
  update_after_close: "New info after close",
  unclear_field: "Unclear answer",
  recap_not_confirmed: "Summary not confirmed",
};

export function initials(name: string | null): string {
  if (!name) return "?";
  return name.split(/\s+/).slice(0, 2).map((w) => w[0]?.toUpperCase() ?? "").join("");
}

export function experience(months: number | null): string {
  if (months === null) return "–";
  if (months === 0) return "None";
  if (months < 12) return `${months} mo`;
  const years = Math.round((months / 12) * 10) / 10;
  return `${years} yr`;
}

export function shortDate(value: string | null): string {
  if (!value) return "–";
  const d = new Date(`${value.slice(0, 10)}T12:00:00`);
  return d.toLocaleDateString("en-GB", { weekday: "short", day: "2-digit", month: "short" });
}

/** Server timestamps are naive UTC. */
export function parseUtc(value: string): Date {
  return new Date(value.endsWith("Z") ? value : `${value}Z`);
}

function span(minutes: number): string {
  if (minutes < 60) return `${Math.max(1, Math.round(minutes))} min`;
  if (minutes < 48 * 60) return `${Math.round(minutes / 60)} h`;
  return `${Math.round(minutes / 1440)} d`;
}

export function ago(value: string | null, now: Date): string {
  if (!value) return "–";
  const minutes = (now.getTime() - parseUtc(value).getTime()) / 60000;
  return minutes < 1 ? "just now" : `${span(minutes)} ago`;
}

export function until(value: string | null, now: Date): string {
  if (!value) return "–";
  const minutes = (parseUtc(value).getTime() - now.getTime()) / 60000;
  return minutes <= 0 ? "due now" : `in ${span(minutes)}`;
}

export function pct(value: number | null): string {
  return value === null ? "–" : `${Math.round(value * 100)}%`;
}

export function titleCase(text: string): string {
  return text.replace(/_/g, " ").replace(/^\w/, (c) => c.toUpperCase());
}
