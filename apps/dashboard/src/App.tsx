import { useEffect, useMemo, useRef, useState } from 'react';
import {
  ArrowUpRight,
  Github,
  Sparkles,
  RefreshCw,
  Table2,
  BarChart3,
  Radio,
  Compass,
  MapPin,
  Calendar,
} from 'lucide-react';
import type { Discipline, Filters } from './types';
import { ALL_DISCIPLINES, DEFAULT_FILTERS } from './types';
import { useBookmarks, useDataset, useNow } from './lib/hooks';
import {
  DISCIPLINE_META,
  PROJECT_TYPE_LABELS,
  applyProjectFilters,
  exportProjectsToCsv,
  formatCountdown,
  formatDate,
  formatUSD,
} from './lib/format';
import { AsciiBackdrop } from './components/AsciiBackdrop';
import { StatCards } from './components/StatCards';
import { FilterBar } from './components/FilterBar';
import { AiRecommender } from './components/AiRecommender';
import { ResearchTable } from './components/ResearchTable';
import { Charts } from './components/Charts';
import { SourceStatus } from './components/SourceStatus';

export function App() {
  const { state, reload } = useDataset();
  const now = useNow();
  const { bookmarks, toggleBookmark } = useBookmarks();

  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS);
  const [activeTab, setActiveTab] = useState<'table' | 'analytics'>('table');
  const searchInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (
        e.key === '/' &&
        document.activeElement?.tagName !== 'INPUT' &&
        document.activeElement?.tagName !== 'TEXTAREA'
      ) {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, []);

  const projects = useMemo(
    () => (state.status === 'ready' ? state.data.projects : []),
    [state]
  );

  const filtered = useMemo(
    () => applyProjectFilters(projects, filters, bookmarks, now),
    [projects, filters, bookmarks, now]
  );

  // Select 4 flagship highlights across diverse disciplines for the hero showcase
  const flagshipHighlights = useMemo(() => {
    const picked = [];
    const seenDisciplines = new Set<string>();
    for (const p of projects) {
      if (!seenDisciplines.has(p.discipline)) {
        picked.push(p);
        seenDisciplines.add(p.discipline);
      }
      if (picked.length === 4) break;
    }
    return picked;
  }, [projects]);

  const jumpToDiscipline = (disc: Discipline) => {
    setFilters((f) => ({
      ...f,
      disciplines: f.disciplines.includes(disc) ? [] : [disc],
    }));
    const el = document.getElementById('live-arena');
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  const resetFilters = () => setFilters(DEFAULT_FILTERS);

  return (
    <div className="relative min-h-screen text-[#f4f0e0]">
      <AsciiBackdrop />

      {/* Top Navigation Bar (wundernn.io / ActiveMLCompetitions style) */}
      <header className="sticky top-3 z-40 mx-auto flex max-w-7xl items-center justify-between px-4 pt-4 sm:px-8">
        <a
          href="#"
          className="wunder-pill inline-flex items-center gap-2.5 rounded-full px-4 py-2 font-mono text-xs font-medium tracking-[0.18em] text-[#f4f0e0]"
        >
          <span className="h-2 w-2 rounded-full bg-[#6b9e78] shadow-[0_0_8px_#6b9e78]" />
          <span>RESEARCH.ARENA</span>
          <span className="hidden text-[#7a8275] sm:inline">// LIVE INDEX</span>
        </a>

        <nav className="hidden items-center gap-2 md:flex">
          <a
            href="#ai-matchmaker"
            className="wunder-pill rounded-full px-3.5 py-1.5 font-mono text-[11px] uppercase tracking-[0.16em] text-[#c4c8b8] hover:text-[#f4f0e0]"
          >
            /02 AI Matchmaker
          </a>
          <a
            href="#live-arena"
            className="wunder-pill rounded-full px-3.5 py-1.5 font-mono text-[11px] uppercase tracking-[0.16em] text-[#c4c8b8] hover:text-[#f4f0e0]"
          >
            /03 Live Arena ({projects.length})
          </a>
          <a
            href="#telemetry"
            className="wunder-pill rounded-full px-3.5 py-1.5 font-mono text-[11px] uppercase tracking-[0.16em] text-[#c4c8b8] hover:text-[#f4f0e0]"
          >
            /04 Telemetry
          </a>
        </nav>

        <div className="flex items-center gap-2">
          <a
            href="https://oogwayseinse.github.io/ActiveQuantCompetitions/"
            target="_blank"
            rel="noreferrer"
            className="wunder-pill hidden items-center gap-1 rounded-full px-3 py-1.5 font-mono text-[10px] uppercase tracking-[0.14em] text-[#c8a96e] sm:inline-flex"
            title="Sibling Index: Active Quant Competitions"
          >
            <span>Quant Index</span>
            <ArrowUpRight className="h-3 w-3" />
          </a>
          <a
            href="https://oogwayseinse.github.io/ActiveMLCompetitions/#live-arena"
            target="_blank"
            rel="noreferrer"
            className="wunder-pill hidden items-center gap-1 rounded-full px-3 py-1.5 font-mono text-[10px] uppercase tracking-[0.14em] text-[#9fd4ac] sm:inline-flex"
            title="Sibling Index: Active ML Competitions"
          >
            <span>ML Index</span>
            <ArrowUpRight className="h-3 w-3" />
          </a>
          <a
            href="data/projects.json"
            target="_blank"
            rel="noreferrer"
            className="wunder-pill inline-flex items-center gap-1.5 rounded-full px-3.5 py-1.5 font-mono text-[10px] uppercase tracking-[0.14em] text-[#f4f0e0]"
          >
            <Radio className="h-3 w-3 text-[#6b9e78]" />
            <span>JSON API</span>
          </a>
        </div>
      </header>

      {/* Main Content Container */}
      <main className="relative z-10 mx-auto max-w-7xl space-y-12 px-4 pb-24 pt-8 sm:px-8">
        {/* Hero Section */}
        <section className="relative pt-4">
          <div className="flex flex-wrap items-center gap-2.5">
            <span className="font-mono text-[11px] tracking-[0.22em] text-[#7a8275]">/01</span>
            <span className="inline-flex items-center gap-1.5 rounded-full border border-[#6b9e78]/40 bg-[#6b9e78]/15 px-3 py-0.5 font-mono text-[10px] uppercase tracking-[0.18em] text-[#a3d9b1]">
              <span className="h-1.5 w-1.5 rounded-full bg-[#6b9e78]" />
              Updated Daily · 06:00 UTC
            </span>
            <span className="rounded-full border border-[rgba(244,240,224,0.14)] bg-[rgba(244,240,224,0.03)] px-3 py-0.5 font-mono text-[10px] uppercase tracking-[0.16em] text-[#c8a96e]">
              Conferences · Calls for Papers · Polymath Projects · Grants
            </span>
          </div>

          <h1 className="mt-4 max-w-4xl font-serif text-4xl leading-[1.08] tracking-tight text-[#f4f0e0] sm:text-6xl">
            Live &amp; Upcoming Research Projects and Conferences{' '}
            <span className="italic text-[#c8a96e]">Across 6 Quantitative Fields.</span>
          </h1>

          <p className="mt-4 max-w-3xl text-sm leading-relaxed text-[#c4c8b8] sm:text-base">
            Continuously monitoring active Calls for Papers (CFPs), flagship academic conferences, formal mathematics collaborations, research institute programs, and competitive research grants across{' '}
            <span className="text-[#f4f0e0]">
              Mathematics, Finance, Statistics, Data Science, Artificial Intelligence, and Economy
            </span>
            .
          </p>

          {/* Interactive 6-Discipline Jump Bar */}
          <div className="mt-6 flex flex-wrap items-center gap-2">
            {ALL_DISCIPLINES.map((disc) => {
              const count = projects.filter((p) => p.discipline === disc).length;
              const isSelected = filters.disciplines.includes(disc);
              const meta = DISCIPLINE_META[disc];
              return (
                <button
                  key={disc}
                  type="button"
                  onClick={() => jumpToDiscipline(disc)}
                  className={`inline-flex items-center gap-2 rounded-full border px-3.5 py-1.5 font-mono text-xs transition ${
                    isSelected
                      ? 'border-[#f4f0e0] bg-[#f4f0e0] font-semibold text-[#0a100d]'
                      : `${meta.badgeCls} hover:scale-[1.02]`
                  }`}
                >
                  <span>{meta.symbol}</span>
                  <span>{disc}</span>
                  <span className="rounded-full bg-black/25 px-1.5 py-0.2 text-[10px]">
                    {count}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Hero Flagship Highlights Strip */}
          {flagshipHighlights.length > 0 && (
            <div className="mt-8 grid grid-cols-1 gap-3.5 sm:grid-cols-2 lg:grid-cols-4">
              {flagshipHighlights.map((item) => {
                const discMeta = DISCIPLINE_META[item.discipline];
                const typeMeta = PROJECT_TYPE_LABELS[item.project_type];
                return (
                  <a
                    key={item.id}
                    href={item.url}
                    target="_blank"
                    rel="noreferrer"
                    className="wunder-glass group flex flex-col justify-between rounded-xl p-4 transition-all duration-300 hover:-translate-y-0.5 hover:border-[#c8a96e]/50"
                  >
                    <div>
                      <div className="flex items-center justify-between gap-2">
                        <span
                          className={`rounded-full border px-2 py-0.5 font-mono text-[9px] uppercase tracking-[0.12em] ${typeMeta.badgeCls}`}
                        >
                          {typeMeta.icon} {typeMeta.label}
                        </span>
                        <ArrowUpRight className="h-3.5 w-3.5 text-[#7a8275] transition group-hover:text-[#f4f0e0]" />
                      </div>
                      <h3 className="mt-2.5 font-serif text-base leading-snug text-[#f4f0e0] group-hover:text-[#c8a96e]">
                        {item.title}
                      </h3>
                      <div className="mt-1.5 flex flex-wrap gap-1">
                        <span
                          className={`rounded-full border px-2 py-0.2 font-mono text-[9px] uppercase tracking-[0.1em] ${discMeta.badgeCls}`}
                        >
                          {discMeta.symbol} {item.discipline}
                        </span>
                      </div>
                    </div>

                    <div className="mt-3.5 border-t border-[rgba(244,240,224,0.08)] pt-2.5 font-mono text-[10px]">
                      <div className="flex items-center justify-between text-[#c4c8b8]">
                        <span className="truncate text-[#c8a96e]">
                          {item.funding_usd > 0
                            ? formatUSD(item.funding_usd, false)
                            : item.venue_code || item.platform}
                        </span>
                        <span className="shrink-0 text-[#7a8275]">
                          {formatCountdown(item, now)}
                        </span>
                      </div>
                      {(item.location || item.event_start_date) && (
                        <div className="mt-1 flex items-center gap-2 truncate text-[9px] text-[#7a8275]">
                          {item.location && (
                            <span className="inline-flex items-center gap-0.5 truncate">
                              <MapPin className="h-2.5 w-2.5 shrink-0" />
                              {item.location}
                            </span>
                          )}
                          {item.event_start_date && (
                            <span className="inline-flex items-center gap-0.5 truncate">
                              <Calendar className="h-2.5 w-2.5 shrink-0" />
                              {formatDate(item.event_start_date)}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </a>
                );
              })}
            </div>
          )}
        </section>

        {/* Stat Cards */}
        <StatCards projects={projects} filtered={filtered} now={now} />

        {/* Gemini 3.8 Flash AI Research & Conference Matchmaker */}
        <AiRecommender
          projects={projects}
          bookmarks={bookmarks}
          onToggleBookmark={toggleBookmark}
          now={now}
        />

        {/* Live Arena Section (#live-arena) */}
        <section id="live-arena" className="space-y-4 scroll-mt-20">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-[11px] tracking-[0.22em] text-[#7a8275]">
                  /03
                </span>
                <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-[#c8a96e]">
                  LIVE RESEARCH &amp; CONFERENCE ARENA
                </span>
              </div>
              <h2 className="mt-1 font-serif text-3xl tracking-tight text-[#f4f0e0]">
                Active Calls for Papers, Conferences, Grants &amp; Open Projects
              </h2>
            </div>

            <div className="flex items-center gap-1.5 self-start rounded-full border border-[rgba(244,240,224,0.14)] bg-[rgba(10,16,13,0.7)] p-1">
              <button
                type="button"
                onClick={() => setActiveTab('table')}
                className={`inline-flex items-center gap-1.5 rounded-full px-3.5 py-1.5 font-mono text-[11px] uppercase tracking-[0.14em] transition ${
                  activeTab === 'table'
                    ? 'bg-[#f4f0e0] font-semibold text-[#0a100d]'
                    : 'text-[#c4c8b8] hover:text-[#f4f0e0]'
                }`}
              >
                <Table2 className="h-3.5 w-3.5" />
                <span>Index Table</span>
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('analytics')}
                className={`inline-flex items-center gap-1.5 rounded-full px-3.5 py-1.5 font-mono text-[11px] uppercase tracking-[0.14em] transition ${
                  activeTab === 'analytics'
                    ? 'bg-[#f4f0e0] font-semibold text-[#0a100d]'
                    : 'text-[#c4c8b8] hover:text-[#f4f0e0]'
                }`}
              >
                <BarChart3 className="h-3.5 w-3.5" />
                <span>Telemetry</span>
              </button>
            </div>
          </div>

          <FilterBar
            filters={filters}
            setFilters={setFilters}
            resetFilters={resetFilters}
            projects={projects}
            filteredCount={filtered.length}
            bookmarksCount={bookmarks.size}
            onExportCsv={() => exportProjectsToCsv(filtered)}
            searchInputRef={searchInputRef}
          />

          {state.status === 'loading' ? (
            <div className="wunder-glass flex items-center justify-center gap-3 rounded-2xl p-16 font-mono text-xs text-[#c4c8b8]">
              <RefreshCw className="h-4 w-4 animate-spin text-[#c8a96e]" />
              <span>Loading active research projects &amp; conferences...</span>
            </div>
          ) : state.status === 'error' ? (
            <div className="wunder-glass rounded-2xl border border-[#c75c5c]/40 p-8 text-center text-sm text-[#e8a8a8]">
              <p>Failed to load dataset: {state.error}</p>
              <button
                type="button"
                onClick={reload}
                className="mt-3 rounded-full bg-[#f4f0e0] px-4 py-1.5 font-mono text-xs text-[#0a100d]"
              >
                Retry
              </button>
            </div>
          ) : activeTab === 'table' ? (
            <ResearchTable
              data={filtered}
              bookmarks={bookmarks}
              onToggleBookmark={toggleBookmark}
              now={now}
            />
          ) : (
            <Charts projects={filtered} />
          )}
        </section>

        {/* Always-on Telemetry & Feed Status Footer Section */}
        <section id="telemetry" className="space-y-4 scroll-mt-20">
          <Charts projects={filtered} />
          {state.status === 'ready' && (
            <SourceStatus
              sources={state.data.metadata.sources}
              generatedAt={state.data.metadata.generated_at}
              now={now}
            />
          )}
        </section>

        {/* Footer */}
        <footer className="border-t border-[rgba(244,240,224,0.1)] pt-8 pb-6 font-mono text-xs text-[#7a8275]">
          <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
            <div className="flex items-center gap-2">
              <Compass className="h-4 w-4 text-[#c8a96e]" />
              <span className="text-[#f4f0e0]">Active Research &amp; Conference Arena</span>
              <span>
                · Mathematics · Finance · Statistics · Data Science · AI · Economy
              </span>
            </div>
            <div className="flex flex-wrap items-center gap-4">
              <a
                href="https://oogwayseinse.github.io/ActiveQuantCompetitions/"
                target="_blank"
                rel="noreferrer"
                className="hover:text-[#f4f0e0]"
              >
                ActiveQuantCompetitions
              </a>
              <a
                href="https://oogwayseinse.github.io/ActiveMLCompetitions/#live-arena"
                target="_blank"
                rel="noreferrer"
                className="hover:text-[#f4f0e0]"
              >
                ActiveMLCompetitions
              </a>
              <a
                href="data/projects.csv"
                target="_blank"
                rel="noreferrer"
                className="hover:text-[#f4f0e0]"
              >
                Download CSV
              </a>
              <a
                href="https://github.com/OogwaySeinse/ActiveResearchProjects"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 hover:text-[#f4f0e0]"
              >
                <Github className="h-3.5 w-3.5" />
                <span>GitHub</span>
              </a>
            </div>
          </div>
        </footer>
      </main>

      {/* Floating Bottom CTA Pill (wundernn.io signature) */}
      <div className="pointer-events-none fixed bottom-6 left-1/2 z-40 -translate-x-1/2">
        <a
          href="#ai-matchmaker"
          className="wunder-cta-glow pointer-events-auto inline-flex items-center gap-2 rounded-full border border-[rgba(244,240,224,0.25)] bg-[#f4f0e0] px-5 py-2.5 font-mono text-[11px] font-semibold uppercase tracking-[0.16em] text-[#0a100d] shadow-2xl transition hover:scale-[1.03]"
        >
          <Sparkles className="h-3.5 w-3.5 text-[#0a100d]" />
          <span>AI Research &amp; CFP Matchmaker</span>
        </a>
      </div>
    </div>
  );
}

export default App;
