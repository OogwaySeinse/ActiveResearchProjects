export type Discipline =
  | "Mathematics"
  | "Finance"
  | "Statistics"
  | "Data Science"
  | "Artificial Intelligence"
  | "Economy";

export type ProjectType =
  | "conference"
  | "research_project"
  | "workshop_challenge"
  | "grant_fellowship"
  | "thematic_program";

export type ProjectStatus = "active" | "ending_soon" | "upcoming" | "rolling";

export interface ResearchProject {
  id: string;
  title: string;
  name?: string;
  platform: string;
  source: string;
  url: string;
  discipline: Discipline;
  category: string;
  project_type: ProjectType;
  tier: string;
  status: ProjectStatus;
  abstract_deadline: string | null;
  submission_deadline: string | null;
  notification_date: string | null;
  event_start_date: string | null;
  event_end_date: string | null;
  days_remaining: number | null;
  location: string;
  format: string;
  funding_raw: string;
  funding_usd: number;
  funding_currency: string;
  venue_code: string;
  organizer: string;
  lead_researchers: string;
  proceedings_publisher: string;
  paper_url: string | null;
  tags: string[];
  description: string;
  participants_count: number | null;
  sources: string[];
  first_seen_at: string | null;
  is_new: boolean;
  scraped_at: string;
}

export interface SourceStatusItem {
  name: string;
  label: string;
  status: "ok" | "cached" | "degraded" | "error";
  count: number;
  duration_ms: number;
  error: string | null;
  updated_at: string;
}

export interface DatasetMetadata {
  generated_at: string;
  run_date: string;
  total_active: number;
  raw_records: number;
  duplicates_merged: number;
  new_today: number;
  ending_soon_count: number;
  total_funding_usd: number;
  disciplines_count: number;
  platforms_count: number;
  by_discipline: Record<string, number>;
  by_type: Record<string, number>;
  by_platform: Record<string, number>;
  fx_source: string;
  sources: SourceStatusItem[];
}

export interface DatasetPayload {
  metadata: DatasetMetadata;
  projects: ResearchProject[];
}

export interface Filters {
  search: string;
  disciplines: Discipline[];
  categories: string[];
  projectTypes: ProjectType[];
  platforms: string[];
  tiers: string[];
  formats: string[];
  minFundingUsd: number;
  deadlineWithinDays: number | null;
  cfpOpenOnly: boolean;
  savedOnly: boolean;
  includeRolling: boolean;
}

export const ALL_DISCIPLINES: Discipline[] = [
  "Mathematics",
  "Finance",
  "Statistics",
  "Data Science",
  "Artificial Intelligence",
  "Economy",
];

export const DEFAULT_FILTERS: Filters = {
  search: "",
  disciplines: [],
  categories: [],
  projectTypes: [],
  platforms: [],
  tiers: [],
  formats: [],
  minFundingUsd: 0,
  deadlineWithinDays: null,
  cfpOpenOnly: false,
  savedOnly: false,
  includeRolling: true,
};

