/**
 * Cloudflare Worker: Active Research & Conference Projects AI Advisor Proxy
 *
 * Holds GEMINI_API_KEY in Cloudflare secrets, enforces per-IP sliding-window
 * rate limiting, and calls Gemini 3.8 Flash via the Interactions API (`/v1beta/interactions`)
 * with structured JSON output for research & conference recommendations.
 */

export interface Env {
  GEMINI_API_KEY: string;
  ALLOWED_ORIGIN?: string;
  RATE_LIMIT_MAX_REQUESTS?: string;
  RATE_LIMIT_WINDOW_SECONDS?: string;
}

export interface ResearcherProfilePayload {
  prompt: string;
  academicStage: "phd_postdoc" | "faculty_pi" | "quant_industry";
  disciplines: string[];
  goal: "publish_paper" | "collaborate_project" | "secure_grant" | "win_benchmark";
  collaborationMode: "solo" | "co_authors" | "either";
  hoursPerWeek: number;
}

export interface CandidateProject {
  id: string;
  title: string;
  venue_code: string;
  discipline: string;
  category: string;
  project_type: string;
  tier: string;
  platform: string;
  submission_deadline: string | null;
  event_start_date: string | null;
  days_remaining: number | null;
  funding_usd: number;
  funding_raw: string;
  location: string;
  organizer: string;
  proceedings_publisher: string;
  tags: string[];
  description: string;
}

export interface RecommendRequestBody {
  profile: ResearcherProfilePayload;
  candidates: CandidateProject[];
}

const ipBuckets = new Map<string, number[]>();

function checkRateLimit(ip: string, maxRequests: number, windowSeconds: number) {
  const now = Date.now();
  const windowMs = windowSeconds * 1000;
  const timestamps = (ipBuckets.get(ip) ?? []).filter((t) => now - t < windowMs);
  if (timestamps.length >= maxRequests) {
    const oldest = timestamps[0] ?? now;
    const resetSeconds = Math.max(1, Math.ceil((oldest + windowMs - now) / 1000));
    ipBuckets.set(ip, timestamps);
    return { allowed: false, remaining: 0, resetSeconds };
  }
  timestamps.push(now);
  ipBuckets.set(ip, timestamps);
  return {
    allowed: true,
    remaining: Math.max(0, maxRequests - timestamps.length),
    resetSeconds: windowSeconds,
  };
}

function corsHeaders(origin: string | null, allowedOriginConfig = "*"): Record<string, string> {
  const allowed =
    allowedOriginConfig === "*"
      ? "*"
      : allowedOriginConfig
          .split(",")
          .map((s) => s.trim())
          .includes(origin ?? "")
        ? (origin ?? "*")
        : allowedOriginConfig.split(",")[0].trim();

  return {
    "Access-Control-Allow-Origin": allowed,
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
    "Access-Control-Max-Age": "86400",
  };
}

const RESPONSE_SCHEMA = {
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

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const origin = request.headers.get("Origin");
    const baseCors = corsHeaders(origin, env.ALLOWED_ORIGIN ?? "*");

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: baseCors });
    }

    const url = new URL(request.url);
    if (request.method === "GET" && (url.pathname === "/" || url.pathname === "/health")) {
      return Response.json(
        {
          ok: true,
          service: "active-research-conferences-recommender",
          model: "gemini-3.8-flash",
          api: "interactions-2026-05-20",
          configured: Boolean(env.GEMINI_API_KEY),
        },
        { headers: baseCors },
      );
    }

    if (request.method !== "POST" || (url.pathname !== "/recommend" && url.pathname !== "/")) {
      return Response.json(
        { error: "Not found. Send POST /recommend with { profile, candidates }." },
        { status: 404, headers: baseCors },
      );
    }

    if (!env.GEMINI_API_KEY) {
      return Response.json(
        { error: "GEMINI_API_KEY is not configured on the Cloudflare Worker." },
        { status: 503, headers: baseCors },
      );
    }

    const clientIp =
      request.headers.get("CF-Connecting-IP") ??
      request.headers.get("X-Forwarded-For")?.split(",")[0]?.trim() ??
      "anonymous";
    const maxReq = Number.parseInt(env.RATE_LIMIT_MAX_REQUESTS ?? "12", 10) || 12;
    const windowSec = Number.parseInt(env.RATE_LIMIT_WINDOW_SECONDS ?? "600", 10) || 600;
    const rate = checkRateLimit(clientIp, maxReq, windowSec);

    const rateHeaders = {
      ...baseCors,
      "X-RateLimit-Limit": String(maxReq),
      "X-RateLimit-Remaining": String(rate.remaining),
      "X-RateLimit-Reset": String(rate.resetSeconds),
    };

    if (!rate.allowed) {
      return Response.json(
        { error: `Rate limit exceeded. Try again in ${rate.resetSeconds}s.` },
        { status: 429, headers: rateHeaders },
      );
    }

    let body: RecommendRequestBody;
    try {
      body = (await request.json()) as RecommendRequestBody;
    } catch {
      return Response.json({ error: "Invalid JSON request body." }, { status: 400, headers: rateHeaders });
    }

    if (!body?.profile || !Array.isArray(body?.candidates) || body.candidates.length === 0) {
      return Response.json(
        { error: "Request must include `profile` and a non-empty `candidates` array." },
        { status: 400, headers: rateHeaders },
      );
    }

    const systemInstruction = [
      "You are an elite Academic Principal Investigator, Conference Program Chair, and Quantitative Research Strategist across Mathematics, Finance, Statistics, Data Science, Artificial Intelligence, and Economics.",
      "Select the 4 best active or upcoming research projects, conferences, thematic programs, or grants for the researcher from the provided `candidates` JSON list.",
      "1. ONLY recommend items whose `id` exists verbatim in `candidates`.",
      "2. Tailor `fit_reasons` directly to the researcher's prompt, academic stage, preferred disciplines, primary goal, and weekly research bandwidth.",
      "3. Build a rigorous 4-phase `weekly_plan` calibrated to their `hoursPerWeek` and the submission/project timeline.",
    ].join("\n");

    const geminiRes = await fetch("https://generativelanguage.googleapis.com/v1beta/interactions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-goog-api-key": env.GEMINI_API_KEY,
        "Api-Revision": "2026-05-20",
      },
      body: JSON.stringify({
        model: "gemini-3.8-flash",
        system_instruction: systemInstruction,
        input: JSON.stringify({
          researcher_profile: body.profile,
          candidates: body.candidates.slice(0, 36),
        }),
        store: false,
        generation_config: {
          temperature: 0.35,
          thinking_level: "low",
        },
        response_format: {
          type: "text",
          mime_type: "application/json",
          schema: RESPONSE_SCHEMA,
        },
      }),
    });

    if (!geminiRes.ok) {
      const errText = await geminiRes.text();
      return Response.json(
        { error: `Gemini Interactions API error (HTTP ${geminiRes.status})`, details: errText.slice(0, 500) },
        { status: 502, headers: rateHeaders },
      );
    }

    const interaction = (await geminiRes.json()) as {
      outputs?: { type: string; text?: string }[];
    };
    const textOutput = interaction.outputs?.find((o) => o.type === "text")?.text;
    if (!textOutput) {
      return Response.json({ error: "Gemini returned an empty output." }, { status: 502, headers: rateHeaders });
    }

    const parsed = JSON.parse(textOutput);
    return Response.json(
      {
        summary: parsed.summary,
        recommendations: parsed.recommendations,
        model: "gemini-3.8-flash",
        source: "gemini-worker",
      },
      { status: 200, headers: rateHeaders },
    );
  },
};

