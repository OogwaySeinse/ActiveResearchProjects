import { useMemo } from 'react';
import { CalendarClock, Award, Compass, Sparkles } from 'lucide-react';
import type { ResearchProject } from '../types';
import { formatUSD, daysUntil } from '../lib/format';

interface StatCardsProps {
  projects: ResearchProject[];
  filtered: ResearchProject[];
  now: number;
}

export function StatCards({ projects, filtered, now }: StatCardsProps) {
  const stats = useMemo(() => {
    const activeCount = filtered.length;

    const totalFunding = filtered.reduce((acc, c) => {
      if (c.funding_usd && c.funding_usd > 0) {
        return acc + c.funding_usd;
      }
      return acc;
    }, 0);

    const closingSoon = filtered.filter((c) => {
      const days = daysUntil(c.submission_deadline, now);
      return days !== null && days >= 0 && days <= 21;
    }).length;

    const conferencesCount = filtered.filter(
      (c) => c.project_type === 'conference' || c.project_type === 'thematic_program'
    ).length;
    const researchProjectsCount = filtered.length - conferencesCount;

    const disciplinesSet = new Set<string>();
    filtered.forEach((c) => disciplinesSet.add(c.discipline));

    return {
      activeCount,
      totalCount: projects.length,
      totalFunding,
      closingSoon,
      conferencesCount,
      researchProjectsCount,
      disciplineCount: disciplinesSet.size,
    };
  }, [projects, filtered, now]);

  const cards = [
    {
      idx: '01',
      label: 'LIVE & UPCOMING',
      value: stats.activeCount.toString(),
      sub: `${stats.conferencesCount} conferences/programs · ${stats.researchProjectsCount} projects/grants`,
      icon: Compass,
      accent: 'text-[#6b9e78]',
    },
    {
      idx: '02',
      label: 'RESEARCH FUNDING & PRIZES',
      value: formatUSD(stats.totalFunding, true),
      sub: 'Grants, fellowships & math/AI research awards',
      icon: Award,
      accent: 'text-[#c8a96e]',
    },
    {
      idx: '03',
      label: 'CFP DEADLINES ≤ 21 DAYS',
      value: stats.closingSoon.toString(),
      sub: 'Paper CFPs, abstract & grant deadlines approaching',
      icon: CalendarClock,
      accent: 'text-[#d4843e]',
    },
    {
      idx: '04',
      label: 'CORE DISCIPLINES',
      value: `${stats.disciplineCount} / 6`,
      sub: 'Math · Finance · Stats · Data Sci · AI · Economy',
      icon: Sparkles,
      accent: 'text-[#f4f0e0]',
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-3.5 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <div
            key={card.label}
            className="wunder-glass group relative overflow-hidden rounded-xl p-5 transition-all duration-300 hover:border-[rgba(244,240,224,0.28)]"
          >
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[10px] tracking-[0.2em] text-[#7a8275]">
                    /{card.idx}
                  </span>
                  <p className="font-mono text-[10px] font-medium uppercase tracking-[0.18em] text-[#c4c8b8]">
                    {card.label}
                  </p>
                </div>
                <p className="mt-3 font-serif text-3xl tracking-tight text-[#f4f0e0] sm:text-4xl">
                  {card.value}
                </p>
                <p className="mt-1.5 font-mono text-[11px] text-[#7a8275]">{card.sub}</p>
              </div>
              <div className="rounded-full border border-[rgba(244,240,224,0.12)] bg-[rgba(244,240,224,0.03)] p-2.5">
                <Icon className={`h-4 w-4 ${card.accent}`} />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
