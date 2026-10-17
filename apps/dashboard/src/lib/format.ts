import type { Discipline, Filters, ProjectType, ResearchProject } from "../types";

const DAY_MS = 86_400_000;

export const DISCIPLINE_META: Record<
  Discipline,
  { symbol: string; shortLabel: string; color: string; badgeCls: string; glowCls: string }
> = {
  Mathematics: {
    symbol: "∑",
    shortLabel: "Mathematics",
    color: "#fde047",
    badgeCls: "border-amber-300/40 bg-amber-400/15 text-amber-200",
    glowCls: "shadow-[0_0_16px_rgba(253,224,71,0.2)]",
  },
  Finance: {
    symbol: "$",
    shortLabel: "Finance",
    color: "#34d399",
    badgeCls: "border-emerald-400/40 bg-emerald-400/15 text-emerald-200",
    glowCls: "shadow-[0_0_16px_rgba(52,211,153,0.2)]",
  },
  Statistics: {
    symbol: "∼",
    shortLabel: "Statistics",
    color: "#38bdf8",
    badgeCls: "border-sky-400/40 bg-sky-400/15 text-sky-200",
    glowCls: "shadow-[0_0_16px_rgba(56,189,248,0.2)]",
  },
  "Data Science": {
    symbol: "◈",
    shortLabel: "Data Science",
    color: "#c084fc",
    badgeCls: "border-purple-400/40 bg-purple-400/15 text-purple-200",
    glowCls: "shadow-[0_0_16px_rgba(192,132,252,0.2)]",
  },
  "Artificial Intelligence": {
    symbol: "✦",
    shortLabel: "Artificial Intelligence",
    color: "#6ee7b7",
    badgeCls: "border-teal-300/45 bg-teal-400/15 text-teal-200",
    glowCls: "shadow-[0_0_16px_rgba(110,231,183,0.22)]",
  },
  Economy: {
    symbol: "⚖",
    shortLabel: "Economy",
    color: "#fb923c",
    badgeCls: "border-orange-400/40 bg-orange-400/15 text-orange-200",
    glowCls: "shadow-[0_0_16px_rgba(251,146,60,0.2)]",
  },
};

export const PROJECT_TYPE_LABELS: Record<ProjectType, { label: string; icon: string; badgeCls: string }> = {
  conference: {
    label: "Conference / CFP",
    icon: "🏛️",
    badgeCls: "border-emerald-300/35 bg-emerald-400/12 text-emerald-200",
  },
  research_project: {
    label: "Open Research Project",
    icon: "🔬",
    badgeCls: "border-amber-300/35 bg-amber-400/12 text-amber-200",
  },
  thematic_program: {
    label: "Institute Program",
    icon: "🎓",
    badgeCls: "border-sky-300/35 bg-sky-400/12 text-sky-200",
  },
  grant_fellowship: {
    label: "Grant / Fellowship",
    icon: "💎",
    badgeCls: "border-purple-300/35 bg-purple-400/12 text-purple-200",
  },
  workshop_challenge: {
    label: "Workshop / Benchmark",
    icon: "⚡",
    badgeCls: "border-rose-300/35 bg-rose-400/12 text-rose-200",
  },
};

export function deadlineMs(iso: string | null): number | null {
  if (!iso) return null;
  return Date.parse(`${iso}T23:59:59Z`);
}

export function daysUntil(iso: string | null, now: number): number | null {
  const ms = deadlineMs(iso);
  return ms === null ? null : (ms - now) / DAY_MS;
}

export function primaryTargetDate(p: ResearchProject, now: number): {
  iso: string | null;
  kind: "CFP Deadline" | "Event Start" | "Rolling / Open";
  days: number | null;
} {
  const subDays = daysUntil(p.submission_deadline, now);
  if (p.submission_deadline && subDays !== null && subDays >= -0.5) {
    return { iso: p.submission_deadline, kind: "CFP Deadline", days: subDays };
  }
  const startDays = daysUntil(p.event_start_date, now);
  if (p.event_start_date && startDays !== null && startDays >= -0.5) {
    return { iso: p.event_start_date, kind: "Event Start", days: startDays };
  }
  return { iso: p.submission_deadline ?? p.event_start_date, kind: "Rolling / Open", days: null };
}

export type Urgency = "critical" | "soon" | "normal" | "upcoming_event" | "rolling";

export function getUrgency(p: ResearchProject, now: number): Urgency {
  const subDays = daysUntil(p.submission_deadline, now);
  if (subDays !== null && subDays >= 0) {
    if (subDays <= 14) return "critical";
    if (subDays <= 35) return "soon";
    return "normal";
  }
  const startDays = daysUntil(p.event_start_date, now);
  if (startDays !== null && startDays >= 0) {
    return "upcoming_event";
  }
  return "rolling";
}

export function formatCountdown(p: ResearchProject, now: number): string {
  const target = primaryTargetDate(p, now);
  if (target.days === null) return "Rolling / Open";
  const d = Math.max(0, Math.floor(target.days));
  const hrs = Math.max(0, Math.floor((target.days - d) * 24));
  const prefix = target.kind === "CFP Deadline" ? "CFP:" : "Conf:";
  if (d === 0) return `${prefix} ${hrs}h left`;
  if (d <= 21) return `${prefix} ${d}d ${hrs}h`;
  if (d <= 75) return `${prefix} ${d} days`;
  return `${prefix} ~${Math.round(d / 30)} mo (${d}d)`;
}

const usdCompact = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  notation: "compact",
  maximumFractionDigits: 1,
});
const usdFull = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

export function formatUSD(v: number | null | undefined, compact = true): string {
  if (!v || v <= 0) return "Peer-Reviewed";
  return compact ? usdCompact.format(v) : usdFull.format(v);
}

export function formatDate(iso: string | null | undefined): string {
  if (!iso) return "Rolling / TBA";
  const d = new Date(`${iso}T00:00:00Z`);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" });
}

export function relativeTime(iso: string, now: number): string {
  const parsed = Date.parse(iso);
  if (Number.isNaN(parsed)) return "recently";
  const diff = Math.max(0, now - parsed);
  const mins = Math.round(diff / 60_000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.round(mins / 60);
  if (hours < 48) return `${hours}h ago`;
  return `${Math.round(hours / 24)}d ago`;
}

export function applyProjectFilters(
  rows: ResearchProject[],
  f: Filters,
  bookmarks: Set<string>,
  now: number,
): ResearchProject[] {
  const q = f.search.trim().toLowerCase();
  const terms = q ? q.split(/\s+/) : [];

  return rows.filter((p) => {
    if (f.savedOnly && !bookmarks.has(p.id)) return false;
    if (!f.includeRolling && p.status === "rolling") return false;
    if (f.cfpOpenOnly) {
      const subDays = daysUntil(p.submission_deadline, now);
      if (subDays === null || subDays < 0) return false;
    }
    if (f.disciplines.length > 0 && !f.disciplines.includes(p.discipline)) return false;
    if (f.categories.length > 0 && !f.categories.includes(p.category)) return false;
    if (f.projectTypes.length > 0 && !f.projectTypes.includes(p.project_type)) return false;
    if (f.platforms.length > 0 && !f.platforms.includes(p.platform)) return false;
    if (f.tiers.length > 0 && !f.tiers.includes(p.tier)) return false;
    if (f.formats.length > 0 && !f.formats.includes(p.format)) return false;
    if (f.minFundingUsd > 0 && (p.funding_usd || 0) < f.minFundingUsd) return false;

    if (f.deadlineWithinDays !== null) {
      const target = primaryTargetDate(p, now);
      if (target.days === null || target.days < 0 || target.days > f.deadlineWithinDays) {
        return false;
      }
    }

    if (terms.length > 0) {
      const hay = [
        p.title,
        p.venue_code,
        p.discipline,
        p.category,
        p.platform,
        p.organizer,
        p.lead_researchers,
        p.proceedings_publisher,
        p.location,
        p.description,
        ...p.tags,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      if (!terms.every((t) => hay.includes(t))) return false;
    }

    return true;
  });
}

export function downloadIcsForProject(p: ResearchProject): void {
  const dateStr = (p.submission_deadline ?? p.event_start_date ?? "2027-01-15").replace(/-/g, "");
  const summary = `${p.venue_code || p.title} — ${p.submission_deadline ? "CFP / Submission Deadline" : "Conference Start"}`;
  const desc = `${p.title}\\nDiscipline: ${p.discipline} (${p.category})\\nOrganizer: ${p.organizer}\\nURL: ${p.url}`;
  const ics = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//WunderScholar//Active Research & Conferences//EN",
    "BEGIN:VEVENT",
    `UID:${p.id}@wunderscholar.io`,
    `DTSTART;VALUE=DATE:${dateStr}`,
    `DTEND;VALUE=DATE:${dateStr}`,
    `SUMMARY:${summary}`,
    `DESCRIPTION:${desc}`,
    `LOCATION:${p.location}`,
    `URL:${p.url}`,
    "END:VEVENT",
    "END:VCALENDAR",
  ].join("\r\n");

  const blob = new Blob([ics], { type: "text/calendar;charset=utf-8" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `${(p.venue_code || p.id).toLowerCase().replace(/[^a-z0-9-]+/g, "-")}.ics`;
  link.click();
  URL.revokeObjectURL(link.href);
}

export function exportProjectsToCsv(projects: ResearchProject[], filename = "active-research-conferences.csv"): void {
  const headers = [
    "Title",
    "Venue Code",
    "Discipline",
    "Category",
    "Track Type",
    "Tier",
    "Status",
    "Host / Society",
    "Abstract Deadline",
    "Submission Deadline",
    "Notification Date",
    "Event Start Date",
    "Event End Date",
    "Location",
    "Format",
    "Funding / Grant",
    "Funding USD",
    "Proceedings / Publisher",
    "URL",
  ];

  const rows = projects.map((p) => [
    p.title,
    p.venue_code,
    p.discipline,
    p.category,
    p.project_type,
    p.tier,
    p.status,
    p.platform,
    p.abstract_deadline ?? "",
    p.submission_deadline ?? "Rolling",
    p.notification_date ?? "",
    p.event_start_date ?? "",
    p.event_end_date ?? "",
    p.location,
    p.format,
    p.funding_raw,
    String(p.funding_usd || 0),
    p.proceedings_publisher,
    p.url,
  ]);

  const esc = (v: string) => `"${String(v ?? "").replace(/"/g, '""')}"`;
  const csv = [headers.map(esc).join(","), ...rows.map((r) => r.map(esc).join(","))].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}

