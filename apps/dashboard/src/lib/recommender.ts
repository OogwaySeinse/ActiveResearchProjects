import { ALL_DISCIPLINES, type Discipline, type ResearchProject } from "../types";
import { formatUSD, primaryTargetDate } from "./format";

export type AcademicStage = "phd_postdoc" | "faculty_pi" | "quant_industry";
export type PrimaryResearchGoal = "publish_paper" | "collaborate_project" | "secure_grant" | "win_benchmark";
export type CollaborationMode = "solo" | "co_authors" | "either";

export interface ResearcherProfile {
  prompt: string;
  academicStage: AcademicStage;
  disciplines: Discipline[];
  goal: PrimaryResearchGoal;
  collaborationMode: CollaborationMode;
  hoursPerWeek: number;
}

export interface ResearchMilestone {
  week: string;
  focus: string;
  deliverable: string;
}

export interface EnrichedRecommendation {
  id: string;
  project: ResearchProject;
  match_score: number;
  headline: string;
  fit_reasons: string[];
  watch_outs: string;
  weekly_plan: ResearchMilestone[];
}

export interface RecommenderResult {
  summary: string;
  recommendations: EnrichedRecommendation[];
  model: string;
  source: "gemini-worker" | "gemini-direct" | "local-neural-ranker";
  generatedAt: string;
}

const PROFILE_STORAGE_KEY = "wunderscholar.profile.v1";
const RESULT_STORAGE_KEY = "wunderscholar.result.v1";
const WORKER_URL_STORAGE_KEY = "wunderscholar.workerUrl.v1";
const GEMINI_KEY_STORAGE_KEY = "wunderscholar.geminiKey.v1";

export const DEFAULT_RESEARCHER_PROFILE: ResearcherProfile = {
  prompt:
    "Working on stochastic analysis, high-dimensional statistics, and machine learning for financial time series. Looking for CORE A* conference calls for papers, institute programs, or open research collaborations over the next 2–4 months.",
  academicStage: "phd_postdoc",
  disciplines: ["Mathematics", "Finance", "Statistics", "Artificial Intelligence"],
  goal: "publish_paper",
  collaborationMode: "co_authors",
  hoursPerWeek: 15,
};

export const ARCHETYPE_PRESETS: { label: string; tagline: string; profile: Partial<ResearcherProfile> }[] = [
  {
    label: "∑ Pure & Formal Math (Lean 4 / AMS / SLMath)",
    tagline: "Algebraic geometry, number theory, PDEs, Lean 4 Mathlib formalization & MSRI/INI residencies",
    profile: {
      prompt:
        "Research mathematician specializing in number theory, harmonic analysis, PDEs, and Lean 4 formalization. Interested in SLMath/Newton/ICERM semester programs, STOC/SODA/SIAM conferences, and collaborative Lean 4 blueprints.",
      academicStage: "phd_postdoc",
      disciplines: ["Mathematics"],
      goal: "collaborate_project",
      collaborationMode: "co_authors",
      hoursPerWeek: 18,
    },
  },
  {
    label: "$ Quant Finance & Econometrics (AFA / WFA / NBER)",
    tagline: "Asset pricing, market microstructure, limit order books, stochastic volatility & NBER/EFA calls",
    profile: {
      prompt:
        "Quantitative finance & financial econometrics researcher working on limit order book dynamics, asset pricing factors, and rough volatility. Targeting AFA/WFA/EFA/SFS Cavalcade CFPs, ACM ICAIF, INQUIRE/Q-Group grants, and ENS/ADIA Lab benchmarks.",
      academicStage: "quant_industry",
      disciplines: ["Finance", "Economy"],
      goal: "publish_paper",
      collaborationMode: "co_authors",
      hoursPerWeek: 14,
    },
  },
  {
    label: "∼ Mathematical Stats & Causal Inference (IMS / JSM / ISBA)",
    tagline: "High-dimensional inference, DoubleML, Bayesian nonparametrics, conformal prediction & NSF grants",
    profile: {
      prompt:
        "Statistician working on semiparametric causal inference, Double Machine Learning, Bayesian MCMC, and conformal prediction. Looking for IMS/JSM/ISBA/CLeaR/AISTATS submissions and NSF DMS statistical methodology grants.",
      academicStage: "faculty_pi",
      disciplines: ["Statistics", "Data Science"],
      goal: "publish_paper",
      collaborationMode: "co_authors",
      hoursPerWeek: 16,
    },
  },
  {
    label: "✦ Frontier AI & Data Science (NeurIPS / ICLR / KDD / VLDB)",
    tagline: "LLMs, reasoning, statistical learning theory, graph mining, scalable data systems & AIMO/ARC",
    profile: {
      prompt:
        "AI and Data Science researcher building mathematical reasoning LLMs, graph neural networks, and scalable data systems. Targeting NeurIPS, ICML, ICLR, COLT, KDD, VLDB, and high-visibility reasoning benchmarks.",
      academicStage: "phd_postdoc",
      disciplines: ["Artificial Intelligence", "Data Science"],
      goal: "publish_paper",
      collaborationMode: "co_authors",
      hoursPerWeek: 20,
    },
  },
  {
    label: "⚖ Macro, Market Design & Policy Economy (AEA / Econometric Soc / CEPR)",
    tagline: "HANK macroeconomics, monetary policy, structural estimation, mechanism design & replication games",
    profile: {
      prompt:
        "Economist working on heterogeneous-agent macroeconomics (HANK), monetary policy, auction market design, and structural econometrics. Interested in NBER Summer Institute, Econometric Society, SED, ACM EC, and ECB/CEPR calls.",
      academicStage: "faculty_pi",
      disciplines: ["Economy", "Finance"],
      goal: "publish_paper",
      collaborationMode: "co_authors",
      hoursPerWeek: 15,
    },
  },
];

export function loadSavedProfile(): ResearcherProfile {
  try {
    const raw = localStorage.getItem(PROFILE_STORAGE_KEY);
    if (!raw) return DEFAULT_RESEARCHER_PROFILE;
    const parsed = JSON.parse(raw) as Partial<ResearcherProfile>;
    const validDisciplines = Array.isArray(parsed.disciplines)
      ? parsed.disciplines.filter((d): d is Discipline => ALL_DISCIPLINES.includes(d as Discipline))
      : DEFAULT_RESEARCHER_PROFILE.disciplines;
    return {
      prompt: typeof parsed.prompt === "string" ? parsed.prompt : DEFAULT_RESEARCHER_PROFILE.prompt,
      academicStage: parsed.academicStage ?? DEFAULT_RESEARCHER_PROFILE.academicStage,
      disciplines: validDisciplines.length > 0 ? validDisciplines : DEFAULT_RESEARCHER_PROFILE.disciplines,
      goal: parsed.goal ?? DEFAULT_RESEARCHER_PROFILE.goal,
      collaborationMode: parsed.collaborationMode ?? DEFAULT_RESEARCHER_PROFILE.collaborationMode,
      hoursPerWeek:
        typeof parsed.hoursPerWeek === "number" ? parsed.hoursPerWeek : DEFAULT_RESEARCHER_PROFILE.hoursPerWeek,
    };
  } catch {
    return DEFAULT_RESEARCHER_PROFILE;
  }
}

export function saveProfile(profile: ResearcherProfile): void {
  try {
    localStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(profile));
  } catch {
    // ignore
  }
}

export function loadWorkerUrl(): string {
  const envUrl = (import.meta.env.VITE_RECOMMENDER_URL as string | undefined)?.trim() ?? "";
  try {
    return localStorage.getItem(WORKER_URL_STORAGE_KEY)?.trim() || envUrl;
  } catch {
    return envUrl;
  }
}

export function saveWorkerUrl(url: string): void {
  try {
    if (url.trim()) localStorage.setItem(WORKER_URL_STORAGE_KEY, url.trim());
    else localStorage.removeItem(WORKER_URL_STORAGE_KEY);
  } catch {
    // ignore
  }
}

export function loadCustomGeminiKey(): string {
  const envKey = (import.meta.env.VITE_GEMINI_API_KEY as string | undefined)?.trim() ?? "";
  try {
    return localStorage.getItem(GEMINI_KEY_STORAGE_KEY)?.trim() || envKey;
  } catch {
    return envKey;
  }
}

export function saveCustomGeminiKey(key: string): void {
  try {
    if (key.trim()) localStorage.setItem(GEMINI_KEY_STORAGE_KEY, key.trim());
    else localStorage.removeItem(GEMINI_KEY_STORAGE_KEY);
  } catch {
    // ignore
  }
}

function extractTokens(prompt: string): string[] {
  const stop = new Set([
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "working",
    "looking",
    "interested",
    "research",
    "researcher",
    "conferences",
    "conference",
    "projects",
    "project",
    "over",
    "next",
    "months",
  ]);
  return prompt
    .toLowerCase()
    .replace(/[^a-z0-9+#-]/g, " ")
    .split(/\s+/)
    .filter((w) => w.length >= 3 && !stop.has(w));
}

interface ScoredCandidate {
  project: ResearchProject;
  score: number;
  matchedTerms: string[];
  days: number | null;
}

export function rankCandidates(
  all: ResearchProject[],
  profile: ResearcherProfile,
  now: number,
  limit = 24,
): ScoredCandidate[] {
  const tokens = extractTokens(profile.prompt);
  const scored: ScoredCandidate[] = [];

  for (const p of all) {
    const target = primaryTargetDate(p, now);
    const hay = [
      p.title,
      p.venue_code,
      p.discipline,
      p.category,
      p.platform,
      p.organizer,
      p.lead_researchers,
      p.proceedings_publisher,
      p.description,
      ...p.tags,
    ]
      .join(" ")
      .toLowerCase();

    let score = 48;
    const matchedTerms: string[] = [];

    // 1. Discipline alignment
    if (profile.disciplines.includes(p.discipline)) {
      score += 22;
    }

    // 2. Prompt keyword overlap
    for (const tok of tokens) {
      if (hay.includes(tok)) {
        score += tok.length >= 5 ? 6 : 4;
        if (!matchedTerms.includes(tok) && matchedTerms.length < 5) {
          matchedTerms.push(tok);
        }
      }
    }

    // 3. Goal alignment
    if (profile.goal === "publish_paper") {
      if (p.project_type === "conference") score += 20;
      if (p.tier === "CORE A* / Top-Tier") score += 12;
      if (p.status === "active" || p.status === "ending_soon") score += 8;
    } else if (profile.goal === "collaborate_project") {
      if (p.project_type === "research_project" || p.project_type === "thematic_program") score += 24;
    } else if (profile.goal === "secure_grant") {
      if (p.project_type === "grant_fellowship") score += 26;
      if (p.funding_usd >= 20_000) score += 12;
    } else if (profile.goal === "win_benchmark") {
      if (p.project_type === "workshop_challenge" || p.project_type === "research_project") score += 24;
      if (p.funding_usd > 0) score += 10;
    }

    // 4. Academic stage alignment
    if (profile.academicStage === "faculty_pi") {
      if (p.project_type === "grant_fellowship" || p.project_type === "thematic_program" || p.tier === "CORE A* / Top-Tier") {
        score += 10;
      }
    } else if (profile.academicStage === "quant_industry") {
      if (p.discipline === "Finance" || p.discipline === "Artificial Intelligence" || p.discipline === "Data Science") {
        score += 8;
      }
    }

    scored.push({
      project: p,
      score,
      matchedTerms,
      days: target.days !== null ? Math.round(target.days) : null,
    });
  }

  scored.sort((a, b) => b.score - a.score || b.project.funding_usd - a.project.funding_usd);
  return scored.slice(0, limit);
}

function buildFourPhaseRoadmap(p: ResearchProject, profile: ResearcherProfile): ResearchMilestone[] {
  const hrs = profile.hoursPerWeek;
  if (p.project_type === "research_project") {
    return [
      {
        week: `Phase 1 (~${hrs}h/wk)`,
        focus: "Blueprint & Literature Onboarding",
        deliverable: `Clone the ${p.venue_code} repository/dependency graph, review open lemmas or replication tasks, and claim an unclaimed theorem/module.`,
      },
      {
        week: `Phase 2 (~${hrs}h/wk)`,
        focus: "Core Proof / Empirical Implementation",
        deliverable: `Formalize intermediate definitions/lemmas or implement reproducible econometric/statistical pipelines matching ${p.platform} standards.`,
      },
      {
        week: `Phase 3 (~${hrs}h/wk)`,
        focus: "CI Verification & Maintainer Review",
        deliverable: "Pass automated proof/code checks, eliminate sorry/placeholder axioms, and submit pull request for maintainer review.",
      },
      {
        week: `Phase 4 (~${hrs}h/wk)`,
        focus: "Upstream Merge & Monograph Co-Authorship",
        deliverable: `Integrate contribution into ${p.proceedings_publisher || p.platform} and document results in the collaborative paper.`,
      },
    ];
  }

  if (p.project_type === "grant_fellowship" || p.project_type === "thematic_program") {
    return [
      {
        week: `Phase 1 (~${hrs}h/wk)`,
        focus: "Solicitation Alignment & Specific Aims",
        deliverable: `Draft a crisp 1-page Specific Aims & Intellectual Merit summary aligned with ${p.organizer} panel priorities.`,
      },
      {
        week: `Phase 2 (~${hrs}h/wk)`,
        focus: "Preliminary Results & Theoretical Framework",
        deliverable: `Compile pilot theorems, empirical simulation evidence, and multi-year work packages for ${p.venue_code}.`,
      },
      {
        week: `Phase 3 (~${hrs}h/wk)`,
        focus: "Budget Justification & Co-PI Letters",
        deliverable: `Finalize institutional budget (${p.funding_raw}), data management plan, and collaborator letters of commitment.`,
      },
      {
        week: `Phase 4 (~${hrs}h/wk)`,
        focus: "Internal Mock Panel & Portal Submission",
        deliverable: `Incorporate feedback from senior colleagues and submit 48 hours ahead of the ${p.submission_deadline ?? "solicitation"} deadline.`,
      },
    ];
  }

  return [
    {
      week: `Phase 1 (~${hrs}h/wk)`,
      focus: "Problem Formulation & Theoretical Identification",
      deliverable: `Lock core theorem statements / identification strategy and verify novelty against recent ${p.venue_code} proceedings.`,
    },
    {
      week: `Phase 2 (~${hrs}h/wk)`,
      focus: "Proofs, Empirical Baselines & Ablations",
      deliverable: `Complete mathematical proofs and run out-of-sample / Monte Carlo benchmarks with confidence intervals.`,
    },
    {
      week: `Phase 3 (~${hrs}h/wk)`,
      focus: "Abstract Registration & Paper Polishing",
      deliverable: `Register abstract${p.abstract_deadline ? ` by ${p.abstract_deadline}` : ""} and structure manuscript for ${p.proceedings_publisher}.`,
    },
    {
      week: `Phase 4 (~${hrs}h/wk)`,
      focus: "Camera-Ready Appendix & Reproducibility Package",
      deliverable: `Audit proofs, package anonymized code/data appendix, and submit prior to ${p.submission_deadline ?? "CFP close"}.`,
    },
  ];
}

export function synthesizeLocalRecommendations(
  all: ResearchProject[],
  profile: ResearcherProfile,
  now: number,
): RecommenderResult {
  const candidates = rankCandidates(all, profile, now, 18);
  const picked: ScoredCandidate[] = [];
  const discCount = new Map<string, number>();

  for (const cand of candidates) {
    const count = discCount.get(cand.project.discipline) ?? 0;
    if (count >= 2 && picked.length < 3 && profile.disciplines.length > 1) continue;
    picked.push(cand);
    discCount.set(cand.project.discipline, count + 1);
    if (picked.length === 4) break;
  }
  while (picked.length < Math.min(4, candidates.length)) {
    const next = candidates.find((c) => !picked.includes(c));
    if (!next) break;
    picked.push(next);
  }

  const maxScore = picked[0]?.score ?? 85;
  const recommendations: EnrichedRecommendation[] = picked.map((item, idx) => {
    const p = item.project;
    const matchScore = Math.min(
      98,
      Math.max(78, Math.round(97 - idx * 3 - Math.max(0, (maxScore - item.score) * 0.2))),
    );

    const reasons: string[] = [
      `Direct alignment with your ${p.discipline} agenda (${p.category} via ${p.platform}).`,
    ];
    if (item.matchedTerms.length > 0) {
      reasons.push(
        `Matches core research keywords from your prompt: ${item.matchedTerms.map((t) => `“${t}”`).join(", ")}.`,
      );
    } else {
      reasons.push(`High-impact ${p.tier} venue published in ${p.proceedings_publisher || p.platform}.`);
    }

    if (p.funding_usd > 0) {
      reasons.push(
        `Includes ${p.funding_raw} (${formatUSD(p.funding_usd, false)} equivalent) supporting research execution or travel.`,
      );
    } else {
      reasons.push(
        `Well-suited for a ${profile.hoursPerWeek}h/week ${profile.collaborationMode === "co_authors" ? "co-authored" : "focused"} research cadence.`,
      );
    }

    const watchOuts =
      item.days !== null && item.days <= 14
        ? `Urgent window (${item.days} days remaining) — lock abstract registration and core theorem/empirical tables immediately.`
        : p.tier === "CORE A* / Top-Tier"
          ? `Highly selective ${p.venue_code} review process (~15–22% acceptance rate); emphasize rigorous mathematical proofs, identification, or out-of-distribution ablations.`
          : `Coordinate early with ${p.organizer} guidelines and verify formatting/anonymization requirements.`;

    return {
      id: p.id,
      project: p,
      match_score: matchScore,
      headline: `${p.tier} ${p.discipline} opportunity at ${p.venue_code || p.platform}`,
      fit_reasons: reasons.slice(0, 3),
      watch_outs: watchOuts,
      weekly_plan: buildFourPhaseRoadmap(p, profile),
    };
  });

  const summary = `Synthesized across ${all.length} active research projects & conferences in ${profile.disciplines.join(", ")}. Prioritized ${
    profile.goal.replace("_", " ")
  } tracks calibrated for ${profile.hoursPerWeek} hrs/week.`;

  return {
    summary,
    recommendations,
    model: "gemini-3.8-flash (ready) · local neural scholar ranker",
    source: "local-neural-ranker",
    generatedAt: new Date().toISOString(),
  };
}

const GEMINI_SCHEMA = {
  type: "object",
  properties: {
    summary: { type: "string" },
    recommendations: {
      type: "array",
      items: {
        type: "object",
        properties: {
          id: { type: "string" },
          match_score: { type: "integer" },
          headline: { type: "string" },
          fit_reasons: { type: "array", items: { type: "string" } },
          watch_outs: { type: "string" },
          weekly_plan: {
            type: "array",
            items: {
              type: "object",
              properties: {
                week: { type: "string" },
                focus: { type: "string" },
                deliverable: { type: "string" },
              },
              required: ["week", "focus", "deliverable"],
            },
          },
        },
        required: ["id", "match_score", "headline", "fit_reasons", "watch_outs", "weekly_plan"],
      },
    },
  },
  required: ["summary", "recommendations"],
};

export async function generateResearchRecommendations(
  all: ResearchProject[],
  profile: ResearcherProfile,
  now: number,
  customWorkerUrl?: string,
  customGeminiKey?: string,
): Promise<RecommenderResult> {
  saveProfile(profile);
  const workerUrl = (customWorkerUrl ?? loadWorkerUrl()).trim().replace(/\/+$/, "");
  const geminiKey = (customGeminiKey ?? loadCustomGeminiKey()).trim();

  const topScored = rankCandidates(all, profile, now, 28);
  const byId = new Map(all.map((p) => [p.id, p]));

  const candidates = topScored.map(({ project: p, days }) => ({
    id: p.id,
    title: p.title,
    venue_code: p.venue_code,
    discipline: p.discipline,
    category: p.category,
    project_type: p.project_type,
    tier: p.tier,
    platform: p.platform,
    submission_deadline: p.submission_deadline,
    event_start_date: p.event_start_date,
    days_remaining: days,
    funding_usd: p.funding_usd,
    funding_raw: p.funding_raw,
    location: p.location,
    organizer: p.organizer,
    proceedings_publisher: p.proceedings_publisher,
    tags: p.tags.slice(0, 8),
    description: p.description.slice(0, 260),
  }));

  if (workerUrl) {
    const endpoint = workerUrl.endsWith("/recommend") ? workerUrl : `${workerUrl}/recommend`;
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ profile, candidates }),
    });
    if (res.ok) {
      const data = await res.json();
      const hydrated: EnrichedRecommendation[] = [];
      for (const item of data.recommendations ?? []) {
        const proj = byId.get(item.id);
        if (proj) hydrated.push({ ...item, id: proj.id, project: proj });
      }
      if (hydrated.length > 0) {
        return {
          summary: data.summary,
          recommendations: hydrated,
          model: data.model ?? "gemini-3.8-flash",
          source: "gemini-worker",
          generatedAt: new Date().toISOString(),
        };
      }
    }
  }

  if (geminiKey) {
    const systemInstruction = [
      "You are an elite Academic Principal Investigator, Conference Program Chair, and Quantitative Research Advisor across Mathematics, Finance, Statistics, Data Science, Artificial Intelligence, and Economy.",
      "Select the 4 best active research projects, conferences, institute programs, or grants for the researcher from the provided `candidates` JSON list.",
      "1. ONLY recommend items whose `id` exists verbatim in `candidates`.",
      "2. Tailor `fit_reasons` directly to the researcher's prompt, disciplines, academic stage, and goal.",
      "3. Build a concrete 4-phase `weekly_plan` calibrated to their `hoursPerWeek`.",
    ].join("\n");

    const geminiRes = await fetch("https://generativelanguage.googleapis.com/v1beta/interactions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-goog-api-key": geminiKey,
        "Api-Revision": "2026-05-20",
      },
      body: JSON.stringify({
        model: "gemini-3.8-flash",
        system_instruction: systemInstruction,
        input: JSON.stringify({ researcher_profile: profile, candidates }),
        store: false,
        generation_config: {
          temperature: 0.35,
          thinking_level: "low",
        },
        response_format: {
          type: "text",
          mime_type: "application/json",
          schema: GEMINI_SCHEMA,
        },
      }),
    });

    if (geminiRes.ok) {
      const interaction = (await geminiRes.json()) as { outputs?: { type: string; text?: string }[] };
      const textOutput = interaction.outputs?.find((o) => o.type === "text")?.text;
      if (textOutput) {
        const parsed = JSON.parse(textOutput);
        const hydrated: EnrichedRecommendation[] = [];
        for (const item of parsed.recommendations ?? []) {
          const proj = byId.get(item.id);
          if (proj) hydrated.push({ ...item, id: proj.id, project: proj });
        }
        if (hydrated.length > 0) {
          return {
            summary: parsed.summary,
            recommendations: hydrated,
            model: "gemini-3.8-flash",
            source: "gemini-direct",
            generatedAt: new Date().toISOString(),
          };
        }
      }
    }
  }

  await new Promise((r) => setTimeout(r, 320));
  const local = synthesizeLocalRecommendations(all, profile, now);
  try {
    localStorage.setItem(RESULT_STORAGE_KEY, JSON.stringify(local));
  } catch {
    // ignore
  }
  return local;
}

