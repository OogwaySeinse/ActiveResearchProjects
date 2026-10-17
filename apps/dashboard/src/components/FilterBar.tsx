import { Search, RotateCcw, Bookmark, Download, Sparkles, Clock } from 'lucide-react';
import type {
  Filters,
  ResearchProject,
  Discipline,
  ProjectType,
} from '../types';
import { ALL_DISCIPLINES } from '../types';
import { MultiSelect } from './MultiSelect';
import { DISCIPLINE_META, PROJECT_TYPE_LABELS } from '../lib/format';

interface FilterBarProps {
  filters: Filters;
  setFilters: React.Dispatch<React.SetStateAction<Filters>>;
  resetFilters: () => void;
  projects: ResearchProject[];
  filteredCount: number;
  bookmarksCount: number;
  onExportCsv: () => void;
  searchInputRef: React.RefObject<HTMLInputElement>;
}

const ALL_PROJECT_TYPES: ProjectType[] = [
  'conference',
  'research_project',
  'thematic_program',
  'grant_fellowship',
  'workshop_challenge',
];

const FUNDING_PRESETS = [
  { label: 'Any Track', value: 0 },
  { label: 'Funded ($5K+)', value: 5000 },
  { label: '$25K+', value: 25000 },
  { label: '$100K+', value: 100000 },
  { label: '$500K+', value: 500000 },
];

export function FilterBar({
  filters,
  setFilters,
  resetFilters,
  projects,
  filteredCount,
  bookmarksCount,
  onExportCsv,
  searchInputRef,
}: FilterBarProps) {
  const platformOptions = Array.from(
    projects.reduce((map, c) => {
      map.set(c.platform, (map.get(c.platform) ?? 0) + 1);
      return map;
    }, new Map<string, number>())
  )
    .sort((a, b) => b[1] - a[1])
    .map(([value, count]) => ({ value, label: value, count }));

  const categoryOptions = Array.from(
    projects.reduce((map, c) => {
      map.set(c.category, (map.get(c.category) ?? 0) + 1);
      return map;
    }, new Map<string, number>())
  )
    .sort((a, b) => b[1] - a[1])
    .map(([value, count]) => ({ value, label: value, count }));

  const tierOptions = Array.from(
    projects.reduce((map, c) => {
      map.set(c.tier, (map.get(c.tier) ?? 0) + 1);
      return map;
    }, new Map<string, number>())
  )
    .sort((a, b) => b[1] - a[1])
    .map(([value, count]) => ({ value, label: value, count }));

  const disciplineCounts = ALL_DISCIPLINES.reduce(
    (acc, d) => {
      acc[d] = projects.filter((p) => p.discipline === d).length;
      return acc;
    },
    {} as Record<Discipline, number>
  );

  const typeCounts = ALL_PROJECT_TYPES.reduce(
    (acc, k) => {
      acc[k] = projects.filter((p) => p.project_type === k).length;
      return acc;
    },
    {} as Record<ProjectType, number>
  );

  const toggleDiscipline = (d: Discipline) => {
    setFilters((f) => ({
      ...f,
      disciplines: f.disciplines.includes(d)
        ? f.disciplines.filter((x) => x !== d)
        : [...f.disciplines, d],
    }));
  };

  const toggleProjectType = (k: ProjectType) => {
    setFilters((f) => ({
      ...f,
      projectTypes: f.projectTypes.includes(k)
        ? f.projectTypes.filter((x) => x !== k)
        : [...f.projectTypes, k],
    }));
  };

  const hasActiveFilters =
    filters.search !== '' ||
    filters.disciplines.length > 0 ||
    filters.projectTypes.length > 0 ||
    filters.platforms.length > 0 ||
    filters.categories.length > 0 ||
    filters.tiers.length > 0 ||
    filters.minFundingUsd > 0 ||
    filters.cfpOpenOnly ||
    filters.savedOnly ||
    !filters.includeRolling;

  return (
    <div className="wunder-glass space-y-3.5 rounded-xl p-4">
      {/* Row 1: Quick Discipline Selector Pills (The 6 core user-requested disciplines) */}
      <div className="flex flex-wrap items-center gap-2 border-b border-[rgba(244,240,224,0.08)] pb-3">
        <span className="mr-1 inline-flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-[0.18em] text-[#7a8275]">
          <Sparkles className="h-3 w-3 text-[#c8a96e]" />
          Disciplines:
        </span>
        <button
          type="button"
          onClick={() => setFilters((f) => ({ ...f, disciplines: [] }))}
          className={`rounded-full border px-3 py-1 font-mono text-[11px] transition ${
            filters.disciplines.length === 0
              ? 'border-[#f4f0e0] bg-[#f4f0e0] font-semibold text-[#0a100d]'
              : 'border-[rgba(244,240,224,0.14)] bg-[rgba(10,16,13,0.5)] text-[#c4c8b8] hover:border-[rgba(244,240,224,0.3)] hover:text-[#f4f0e0]'
          }`}
        >
          All 6 Fields ({projects.length})
        </button>
        {ALL_DISCIPLINES.map((disc) => {
          const active = filters.disciplines.includes(disc);
          const meta = DISCIPLINE_META[disc];
          return (
            <button
              key={disc}
              type="button"
              onClick={() => toggleDiscipline(disc)}
              className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 font-mono text-[11px] transition ${
                active
                  ? 'border-[#f4f0e0] bg-[#f4f0e0] font-semibold text-[#0a100d]'
                  : `${meta.badgeCls} opacity-85 hover:opacity-100`
              }`}
            >
              <span>{meta.symbol}</span>
              <span>{disc}</span>
              <span className="text-[10px] opacity-75">({disciplineCounts[disc] ?? 0})</span>
            </button>
          );
        })}
      </div>

      {/* Row 2: Project vs Conference Track Selector Pills */}
      <div className="flex flex-wrap items-center gap-1.5 border-b border-[rgba(244,240,224,0.08)] pb-3">
        <span className="mr-1 font-mono text-[10px] uppercase tracking-[0.18em] text-[#7a8275]">
          Track:
        </span>
        <button
          type="button"
          onClick={() => setFilters((f) => ({ ...f, projectTypes: [] }))}
          className={`rounded-full border px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.14em] transition ${
            filters.projectTypes.length === 0
              ? 'border-[#c8a96e]/60 bg-[#c8a96e]/15 text-[#f4f0e0]'
              : 'border-[rgba(244,240,224,0.12)] text-[#7a8275] hover:text-[#c4c8b8]'
          }`}
        >
          All Formats
        </button>
        {ALL_PROJECT_TYPES.map((k) => {
          const active = filters.projectTypes.includes(k);
          const meta = PROJECT_TYPE_LABELS[k];
          return (
            <button
              key={k}
              type="button"
              onClick={() => toggleProjectType(k)}
              className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.14em] transition ${
                active
                  ? 'border-[#c8a96e] bg-[#c8a96e]/25 font-medium text-[#f4f0e0]'
                  : 'border-[rgba(244,240,224,0.12)] bg-[rgba(10,16,13,0.45)] text-[#c4c8b8] hover:border-[rgba(244,240,224,0.28)] hover:text-[#f4f0e0]'
              }`}
            >
              <span>{meta.icon}</span>
              <span>{meta.label}</span>
              <span className="opacity-70">({typeCounts[k] ?? 0})</span>
            </button>
          );
        })}
      </div>

      {/* Row 3: Search + Quick Toggles + Export */}
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[#7a8275]" />
          <input
            ref={searchInputRef}
            type="text"
            value={filters.search}
            onChange={(e) => setFilters((f) => ({ ...f, search: e.target.value }))}
            placeholder="Search conferences, CFPs, Lean 4 projects, grants, NBER, NeurIPS, JSM, AFA... (press /)"
            className="w-full rounded-full border border-[rgba(244,240,224,0.14)] bg-[rgba(10,16,13,0.75)] py-2 pl-10 pr-12 font-mono text-xs text-[#f4f0e0] placeholder-[#7a8275] focus:border-[#f4f0e0]/45 focus:outline-none"
          />
          <kbd className="pointer-events-none absolute right-3.5 top-1/2 hidden -translate-y-1/2 rounded border border-[rgba(244,240,224,0.15)] bg-[rgba(244,240,224,0.04)] px-1.5 py-0.5 font-mono text-[10px] text-[#7a8275] sm:inline-block">
            /
          </kbd>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => setFilters((f) => ({ ...f, cfpOpenOnly: !f.cfpOpenOnly }))}
            className={`inline-flex items-center gap-1.5 rounded-full border px-3.5 py-1.5 font-mono text-[11px] uppercase tracking-[0.14em] transition ${
              filters.cfpOpenOnly
                ? 'border-[#6b9e78]/60 bg-[#6b9e78]/20 text-[#a3d9b1]'
                : 'border-[rgba(244,240,224,0.14)] bg-[rgba(10,16,13,0.65)] text-[#c4c8b8] hover:border-[rgba(244,240,224,0.3)] hover:text-[#f4f0e0]'
            }`}
          >
            <Clock className="h-3.5 w-3.5" />
            <span>Open CFP Only</span>
          </button>

          <button
            type="button"
            onClick={() => setFilters((f) => ({ ...f, savedOnly: !f.savedOnly }))}
            className={`inline-flex items-center gap-1.5 rounded-full border px-3.5 py-1.5 font-mono text-[11px] uppercase tracking-[0.14em] transition ${
              filters.savedOnly
                ? 'border-[#c8a96e]/60 bg-[#c8a96e]/15 text-[#c8a96e]'
                : 'border-[rgba(244,240,224,0.14)] bg-[rgba(10,16,13,0.65)] text-[#c4c8b8] hover:border-[rgba(244,240,224,0.3)] hover:text-[#f4f0e0]'
            }`}
          >
            <Bookmark className="h-3.5 w-3.5" />
            <span>Saved</span>
            {bookmarksCount > 0 && (
              <span className="rounded-full bg-[#c8a96e]/25 px-1.5 py-0.2 text-[10px] text-[#f4f0e0]">
                {bookmarksCount}
              </span>
            )}
          </button>

          <button
            type="button"
            onClick={onExportCsv}
            className="inline-flex items-center gap-1.5 rounded-full border border-[rgba(244,240,224,0.14)] bg-[rgba(10,16,13,0.65)] px-3.5 py-1.5 font-mono text-[11px] uppercase tracking-[0.14em] text-[#c4c8b8] transition hover:border-[rgba(244,240,224,0.3)] hover:text-[#f4f0e0]"
            title="Export filtered rows to CSV"
          >
            <Download className="h-3.5 w-3.5" />
            <span>CSV</span>
          </button>
        </div>
      </div>

      {/* Row 4: Multi-select dropdowns + Funding presets + Counter */}
      <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
        <div className="flex flex-wrap items-center gap-2">
          <MultiSelect
            label="Society / Venue"
            options={platformOptions}
            selected={filters.platforms}
            onChange={(platforms) => setFilters((f) => ({ ...f, platforms }))}
          />
          <MultiSelect
            label="Subfield"
            options={categoryOptions}
            selected={filters.categories}
            onChange={(categories) => setFilters((f) => ({ ...f, categories }))}
          />
          <MultiSelect
            label="Tier"
            options={tierOptions}
            selected={filters.tiers}
            onChange={(tiers) => setFilters((f) => ({ ...f, tiers }))}
          />

          <div className="flex items-center rounded-full border border-[rgba(244,240,224,0.14)] bg-[rgba(10,16,13,0.65)] p-0.5">
            {FUNDING_PRESETS.map((preset) => (
              <button
                key={preset.value}
                type="button"
                onClick={() => setFilters((f) => ({ ...f, minFundingUsd: preset.value }))}
                className={`rounded-full px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.12em] transition ${
                  filters.minFundingUsd === preset.value
                    ? 'bg-[#f4f0e0] font-semibold text-[#0a100d]'
                    : 'text-[#7a8275] hover:text-[#f4f0e0]'
                }`}
              >
                {preset.label}
              </button>
            ))}
          </div>

          {hasActiveFilters && (
            <button
              type="button"
              onClick={resetFilters}
              className="inline-flex items-center gap-1 rounded-full px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.14em] text-[#c4c8b8] hover:bg-[rgba(244,240,224,0.06)] hover:text-[#f4f0e0]"
            >
              <RotateCcw className="h-3 w-3" />
              Reset
            </button>
          )}
        </div>

        <div className="font-mono text-[11px] uppercase tracking-[0.16em] text-[#7a8275]">
          Showing <span className="font-semibold text-[#f4f0e0]">{filteredCount}</span> of{' '}
          <span className="text-[#c4c8b8]">{projects.length}</span> tracked items
        </div>
      </div>
    </div>
  );
}
