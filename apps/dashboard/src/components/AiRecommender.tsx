import { useState } from 'react';
import {
  Sparkles,
  Send,
  KeyRound,
  ExternalLink,
  AlertCircle,
  Loader2,
  Bookmark,
  CheckCircle2,
  Cpu,
  RotateCcw,
  ChevronDown,
  ChevronUp,
  MapPin,
  Calendar,
} from 'lucide-react';
import type { ResearchProject, Discipline } from '../types';
import { ALL_DISCIPLINES } from '../types';
import {
  ARCHETYPE_PRESETS,
  generateResearchRecommendations,
  loadSavedProfile,
  loadCustomGeminiKey,
  saveCustomGeminiKey,
  loadWorkerUrl,
  type ResearcherProfile,
  type RecommenderResult,
  type EnrichedRecommendation,
} from '../lib/recommender';
import {
  DISCIPLINE_META,
  PROJECT_TYPE_LABELS,
  formatUSD,
  formatCountdown,
} from '../lib/format';

interface AiRecommenderProps {
  projects: ResearchProject[];
  bookmarks: Set<string>;
  onToggleBookmark: (id: string) => void;
  now: number;
}

export function AiRecommender({
  projects,
  bookmarks,
  onToggleBookmark,
  now,
}: AiRecommenderProps) {
  const [profile, setProfile] = useState<ResearcherProfile>(() => loadSavedProfile());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<RecommenderResult | null>(null);

  const [showKeyModal, setShowKeyModal] = useState(false);
  const [apiKeyInput, setApiKeyInput] = useState(() => loadCustomGeminiKey());
  const [savedKeyFlag, setSavedKeyFlag] = useState(() => Boolean(loadCustomGeminiKey()));

  const sharedAvailable = Boolean(loadWorkerUrl());

  const handleRun = async (overrideProfile?: ResearcherProfile) => {
    const activeProfile = overrideProfile ?? profile;
    if (!activeProfile.prompt.trim()) return;
    if (overrideProfile) setProfile(overrideProfile);

    setLoading(true);
    setError(null);
    try {
      const res = await generateResearchRecommendations(
        projects,
        activeProfile,
        now,
        undefined,
        apiKeyInput.trim() || undefined
      );
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Recommendation engine failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleApplyPreset = (presetProfile: Partial<ResearcherProfile>) => {
    const merged: ResearcherProfile = {
      ...profile,
      ...presetProfile,
    };
    handleRun(merged);
  };

  const toggleProfileDiscipline = (d: Discipline) => {
    setProfile((prev) => {
      const exists = prev.disciplines.includes(d);
      const next = exists
        ? prev.disciplines.filter((x) => x !== d)
        : [...prev.disciplines, d];
      return {
        ...prev,
        disciplines: next.length > 0 ? next : [d],
      };
    });
  };

  const handleSaveKey = () => {
    const trimmed = apiKeyInput.trim();
    saveCustomGeminiKey(trimmed);
    setSavedKeyFlag(Boolean(trimmed));
    setShowKeyModal(false);
  };

  return (
    <section
      id="ai-matchmaker"
      className="wunder-glass relative overflow-hidden rounded-2xl p-6 sm:p-8"
    >
      <div className="pointer-events-none absolute -right-24 -top-24 h-64 w-64 rounded-full bg-[#c8a96e]/10 blur-3xl" />

      {/* Header */}
      <div className="relative flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-2.5">
            <span className="font-mono text-[11px] tracking-[0.22em] text-[#7a8275]">/02</span>
            <span className="inline-flex items-center gap-1.5 rounded-full border border-[#c8a96e]/35 bg-[#c8a96e]/10 px-3 py-0.5 font-mono text-[10px] uppercase tracking-[0.16em] text-[#c8a96e]">
              <Sparkles className="h-3 w-3" />
              Gemini 3.8 Flash · Research &amp; CFP Matchmaker
            </span>
            <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-[#7a8275]">
              {sharedAvailable
                ? 'Shared Endpoint Active'
                : savedKeyFlag
                  ? 'Custom Gemini Key Active'
                  : 'Instant Neural Scholar Ranker + Optional BYOK'}
            </span>
          </div>
          <h2 className="mt-2 font-serif text-2xl tracking-tight text-[#f4f0e0] sm:text-3xl">
            Match Your Research Agenda to Live Conferences, Grants &amp; Projects
          </h2>
          <p className="mt-1 max-w-2xl text-xs text-[#c4c8b8] sm:text-sm">
            Describe your research paper, theorem-proving background, econometric methodology, or target discipline—our recommender ranks the highest-fit open Calls for Papers, polymath collaborations, and research grants with a 4-phase execution plan.
          </p>
        </div>

        <button
          type="button"
          onClick={() => setShowKeyModal((s) => !s)}
          className="inline-flex items-center gap-1.5 self-start rounded-full border border-[rgba(244,240,224,0.16)] bg-[rgba(244,240,224,0.03)] px-3.5 py-1.5 font-mono text-[10px] uppercase tracking-[0.14em] text-[#c4c8b8] transition hover:border-[rgba(244,240,224,0.32)] hover:text-[#f4f0e0]"
        >
          <KeyRound className="h-3 w-3 text-[#c8a96e]" />
          <span>{savedKeyFlag ? 'API Key Saved' : 'Gemini API Key'}</span>
          {showKeyModal ? (
            <ChevronUp className="h-3 w-3" />
          ) : (
            <ChevronDown className="h-3 w-3" />
          )}
        </button>
      </div>

      {/* Optional BYOK Drawer */}
      {showKeyModal && (
        <div className="mt-4 rounded-xl border border-[rgba(244,240,224,0.14)] bg-[rgba(10,16,13,0.85)] p-4">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="space-y-1">
              <p className="font-mono text-xs font-medium text-[#f4f0e0]">
                Optional: Bring Your Own Google AI Studio Key (`gemini-3.8-flash`)
              </p>
              <p className="text-xs text-[#7a8275]">
                Stored strictly in your browser&apos;s `localStorage`. Never transmitted anywhere except directly to `generativelanguage.googleapis.com`.
              </p>
            </div>
            <a
              href="https://aistudio.google.com/apikey"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 font-mono text-[11px] uppercase tracking-[0.14em] text-[#c8a96e] hover:underline"
            >
              Get Free API Key <ExternalLink className="h-3 w-3" />
            </a>
          </div>
          <div className="mt-3 flex flex-col gap-2 sm:flex-row">
            <input
              type="password"
              value={apiKeyInput}
              onChange={(e) => setApiKeyInput(e.target.value)}
              placeholder="AIzaSy..."
              className="flex-1 rounded-full border border-[rgba(244,240,224,0.16)] bg-[rgba(10,16,13,0.9)] px-4 py-2 font-mono text-xs text-[#f4f0e0] placeholder-[#7a8275] focus:border-[#f4f0e0]/45 focus:outline-none"
            />
            <button
              type="button"
              onClick={handleSaveKey}
              className="rounded-full bg-[#f4f0e0] px-5 py-2 font-mono text-xs font-semibold uppercase tracking-[0.14em] text-[#0a100d] transition hover:bg-[#e5dec9]"
            >
              Save Key
            </button>
            {savedKeyFlag && (
              <button
                type="button"
                onClick={() => {
                  setApiKeyInput('');
                  saveCustomGeminiKey('');
                  setSavedKeyFlag(false);
                }}
                className="rounded-full border border-[rgba(244,240,224,0.16)] px-4 py-2 font-mono text-xs uppercase tracking-[0.14em] text-[#c4c8b8] hover:text-[#f4f0e0]"
              >
                Clear
              </button>
            )}
          </div>
        </div>
      )}

      {/* Discipline Focus & Prompt Input */}
      <div className="mt-5 space-y-3">
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="mr-1 font-mono text-[10px] uppercase tracking-[0.16em] text-[#7a8275]">
            Focus Fields:
          </span>
          {ALL_DISCIPLINES.map((d) => {
            const active = profile.disciplines.includes(d);
            const meta = DISCIPLINE_META[d];
            return (
              <button
                key={d}
                type="button"
                onClick={() => toggleProfileDiscipline(d)}
                className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 font-mono text-[10px] transition ${
                  active
                    ? 'border-[#f4f0e0] bg-[#f4f0e0] font-semibold text-[#0a100d]'
                    : 'border-[rgba(244,240,224,0.14)] text-[#c4c8b8] hover:border-[rgba(244,240,224,0.3)]'
                }`}
              >
                <span>{meta.symbol}</span>
                <span>{d}</span>
              </button>
            );
          })}
        </div>

        <div className="flex flex-col gap-2.5 sm:flex-row">
          <input
            type="text"
            value={profile.prompt}
            onChange={(e) => setProfile((p) => ({ ...p, prompt: e.target.value }))}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !loading) handleRun();
            }}
            placeholder="e.g., Working on stochastic analysis, high-dimensional statistics, and machine learning for financial time series..."
            className="flex-1 rounded-full border border-[rgba(244,240,224,0.16)] bg-[rgba(10,16,13,0.78)] px-5 py-3 font-mono text-xs text-[#f4f0e0] placeholder-[#7a8275] focus:border-[#f4f0e0]/50 focus:outline-none"
          />
          <button
            type="button"
            disabled={loading || !profile.prompt.trim()}
            onClick={() => handleRun()}
            className="wunder-cta-glow inline-flex items-center justify-center gap-2 rounded-full bg-[#f4f0e0] px-6 py-3 font-mono text-xs font-semibold uppercase tracking-[0.16em] text-[#0a100d] transition hover:bg-[#e6dfc8] disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <Send className="h-3.5 w-3.5" />
                <span>Match Research</span>
              </>
            )}
          </button>
        </div>

        {/* Archetype Starter Pills */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-[#7a8275]">
            Scholar Archetypes:
          </span>
          {ARCHETYPE_PRESETS.map((preset, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleApplyPreset(preset.profile)}
              className="rounded-full border border-[rgba(244,240,224,0.12)] bg-[rgba(244,240,224,0.03)] px-3 py-1 text-left font-mono text-[11px] text-[#c4c8b8] transition hover:border-[rgba(244,240,224,0.3)] hover:text-[#f4f0e0]"
              title={preset.tagline}
            >
              {preset.label}
            </button>
          ))}
        </div>
      </div>

      {/* Error Notice */}
      {error && (
        <div className="mt-4 flex items-center gap-2 rounded-xl border border-[#c75c5c]/40 bg-[#c75c5c]/10 p-3 text-xs text-[#e8a8a8]">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="mt-6 space-y-4 border-t border-[rgba(244,240,224,0.1)] pt-5">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="flex flex-wrap items-center gap-2">
              {result.source !== 'local-neural-ranker' ? (
                <span className="inline-flex items-center gap-1.5 rounded-full border border-[#6b9e78]/40 bg-[#6b9e78]/15 px-3 py-1 font-mono text-[10px] uppercase tracking-[0.14em] text-[#a3d9b1]">
                  <CheckCircle2 className="h-3 w-3" />
                  Ranked by {result.model}
                </span>
              ) : (
                <span className="inline-flex items-center gap-1.5 rounded-full border border-[#c8a96e]/40 bg-[#c8a96e]/15 px-3 py-1 font-mono text-[10px] uppercase tracking-[0.14em] text-[#e6c88c]">
                  <Cpu className="h-3 w-3" />
                  {result.model}
                </span>
              )}
              <p className="text-xs text-[#c4c8b8]">{result.summary}</p>
            </div>

            <button
              type="button"
              onClick={() => setResult(null)}
              className="inline-flex items-center gap-1 font-mono text-[10px] uppercase tracking-[0.14em] text-[#7a8275] hover:text-[#f4f0e0]"
            >
              <RotateCcw className="h-3 w-3" />
              Clear
            </button>
          </div>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            {result.recommendations.map((rec: EnrichedRecommendation, index: number) => {
              const c = rec.project;
              const isBookmarked = bookmarks.has(c.id);
              const discMeta = DISCIPLINE_META[c.discipline];
              const typeMeta = PROJECT_TYPE_LABELS[c.project_type];

              return (
                <div
                  key={c.id}
                  className="flex flex-col justify-between rounded-xl border border-[rgba(244,240,224,0.14)] bg-[rgba(10,16,13,0.75)] p-5 transition hover:border-[rgba(244,240,224,0.32)]"
                >
                  <div>
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex flex-wrap items-center gap-1.5">
                        <span className="rounded-full bg-[#f4f0e0] px-2.5 py-0.5 font-mono text-[10px] font-bold text-[#0a100d]">
                          #{index + 1} · {rec.match_score}% MATCH
                        </span>
                        <span
                          className={`rounded-full border px-2 py-0.5 font-mono text-[10px] ${discMeta.badgeCls}`}
                        >
                          {discMeta.symbol} {c.discipline}
                        </span>
                        <span
                          className={`rounded-full border px-2 py-0.5 font-mono text-[10px] ${typeMeta.badgeCls}`}
                        >
                          {typeMeta.icon} {typeMeta.label}
                        </span>
                      </div>

                      <button
                        type="button"
                        onClick={() => onToggleBookmark(c.id)}
                        className={`rounded-full p-1 transition ${
                          isBookmarked
                            ? 'text-[#c8a96e]'
                            : 'text-[#7a8275] hover:text-[#f4f0e0]'
                        }`}
                        title="Save project or conference"
                      >
                        <Bookmark
                          className={`h-3.5 w-3.5 ${isBookmarked ? 'fill-current' : ''}`}
                        />
                      </button>
                    </div>

                    <a
                      href={c.url}
                      target="_blank"
                      rel="noreferrer"
                      className="mt-2.5 block font-serif text-lg leading-snug text-[#f4f0e0] hover:text-[#c8a96e]"
                    >
                      {c.title}
                    </a>
                    <p className="mt-0.5 font-mono text-[10px] uppercase tracking-[0.14em] text-[#c8a96e]">
                      {rec.headline}
                    </p>

                    <ul className="mt-2.5 space-y-1 text-xs leading-relaxed text-[#c4c8b8]">
                      {rec.fit_reasons.map((r, i) => (
                        <li key={i} className="flex items-start gap-1.5">
                          <span className="mt-1 h-1 w-1 shrink-0 rounded-full bg-[#c8a96e]" />
                          <span>{r}</span>
                        </li>
                      ))}
                    </ul>

                    {rec.weekly_plan && rec.weekly_plan.length > 0 && (
                      <div className="mt-3 rounded-lg border border-[rgba(244,240,224,0.08)] bg-[rgba(244,240,224,0.02)] p-2.5">
                        <div className="font-mono text-[10px] uppercase tracking-[0.14em] text-[#7a8275]">
                          4-Phase Execution Roadmap
                        </div>
                        <div className="mt-1.5 grid grid-cols-1 gap-1.5 sm:grid-cols-2">
                          {rec.weekly_plan.slice(0, 4).map((step, idx2) => (
                            <div
                              key={idx2}
                              className="rounded border border-[rgba(244,240,224,0.06)] bg-[rgba(10,16,13,0.6)] p-2"
                            >
                              <div className="font-mono text-[9px] uppercase text-[#c8a96e]">
                                {step.week} · {step.focus}
                              </div>
                              <div className="mt-0.5 text-[11px] leading-snug text-[#c4c8b8]">
                                {step.deliverable}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="mt-4 border-t border-[rgba(244,240,224,0.08)] pt-3">
                    <div className="flex flex-wrap items-center justify-between gap-2 font-mono text-[11px]">
                      <span className="text-[#c8a96e]">
                        {c.funding_usd > 0 ? formatUSD(c.funding_usd, false) : c.funding_raw}
                      </span>
                      <span className="text-[#7a8275]">{formatCountdown(c, now)}</span>
                    </div>

                    <div className="mt-1.5 flex flex-wrap items-center justify-between gap-2 font-mono text-[10px] text-[#7a8275]">
                      <div className="flex flex-wrap items-center gap-3">
                        {c.location && (
                          <span className="inline-flex items-center gap-1">
                            <MapPin className="h-2.5 w-2.5" />
                            {c.location}
                          </span>
                        )}
                        {c.event_start_date && (
                          <span className="inline-flex items-center gap-1">
                            <Calendar className="h-2.5 w-2.5" />
                            {c.event_start_date}
                          </span>
                        )}
                      </div>
                      <a
                        href={c.url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 font-mono text-[10px] uppercase tracking-[0.16em] text-[#f4f0e0] hover:text-[#c8a96e]"
                      >
                        Open Portal <ExternalLink className="h-2.5 w-2.5" />
                      </a>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </section>
  );
}
