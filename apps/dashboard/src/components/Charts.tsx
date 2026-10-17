import { useMemo } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
} from 'recharts';
import type { ResearchProject, ProjectType } from '../types';
import { ALL_DISCIPLINES } from '../types';
import { DISCIPLINE_META, PROJECT_TYPE_LABELS, formatUSD } from '../lib/format';

interface ChartsProps {
  projects: ResearchProject[];
}

const BAR_COLORS = [
  '#c8a96e',
  '#6b9e78',
  '#7ba3cc',
  '#d4843e',
  '#a992fa',
  '#8fc1a9',
];

export function Charts({ projects }: ChartsProps) {
  const byDiscipline = useMemo(() => {
    return ALL_DISCIPLINES.map((disc) => {
      const matching = projects.filter((p) => p.discipline === disc);
      const funding = matching.reduce((acc, p) => acc + (p.funding_usd ?? 0), 0);
      return {
        discipline: `${DISCIPLINE_META[disc].symbol} ${disc}`,
        count: matching.length,
        funding,
      };
    });
  }, [projects]);

  const byKind = useMemo(() => {
    const map = new Map<ProjectType, number>();
    for (const c of projects) {
      map.set(c.project_type, (map.get(c.project_type) ?? 0) + 1);
    }
    return Array.from(map.entries())
      .map(([pt, count]) => ({
        kind: PROJECT_TYPE_LABELS[pt]?.label ?? pt,
        count,
      }))
      .sort((a, b) => b.count - a.count);
  }, [projects]);

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
      {/* Chart 1: Coverage across the 6 Core Disciplines */}
      <div className="wunder-glass rounded-2xl p-5">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#7a8275]">
              /TELEMETRY 01
            </span>
            <h3 className="mt-0.5 font-serif text-xl text-[#f4f0e0]">
              Active Projects &amp; Conferences by Discipline
            </h3>
          </div>
          <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-[#c8a96e]">
            6 Core Fields
          </span>
        </div>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={byDiscipline}
              layout="vertical"
              margin={{ top: 4, right: 18, left: 16, bottom: 4 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="rgba(244,240,224,0.07)"
                horizontal={false}
              />
              <XAxis
                type="number"
                stroke="#7a8275"
                fontSize={11}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                type="category"
                dataKey="discipline"
                stroke="#c4c8b8"
                fontSize={11}
                width={160}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip
                cursor={{ fill: 'rgba(244,240,224,0.04)' }}
                contentStyle={{
                  backgroundColor: '#0a100d',
                  border: '1px solid rgba(244,240,224,0.2)',
                  borderRadius: '10px',
                  fontFamily: 'JetBrains Mono, monospace',
                  fontSize: '11px',
                  color: '#f4f0e0',
                }}
                formatter={(val: number, name: string) => [
                  name === 'funding' ? formatUSD(val, true) : `${val} active items`,
                  name === 'funding' ? 'Tracked Funding' : 'Count',
                ]}
              />
              <Bar dataKey="count" radius={[0, 6, 6, 0]}>
                {byDiscipline.map((_, i) => (
                  <Cell key={i} fill={BAR_COLORS[i % BAR_COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Chart 2: Breakdown by Project / Conference Format */}
      <div className="wunder-glass rounded-2xl p-5">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-[#7a8275]">
              /TELEMETRY 02
            </span>
            <h3 className="mt-0.5 font-serif text-xl text-[#f4f0e0]">
              Breakdown by Opportunity Track
            </h3>
          </div>
          <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-[#6b9e78]">
            Conferences · Grants · Projects
          </span>
        </div>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={byKind}
              layout="vertical"
              margin={{ top: 4, right: 18, left: 16, bottom: 4 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="rgba(244,240,224,0.07)"
                horizontal={false}
              />
              <XAxis
                type="number"
                stroke="#7a8275"
                fontSize={11}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                type="category"
                dataKey="kind"
                stroke="#c4c8b8"
                fontSize={11}
                width={165}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip
                cursor={{ fill: 'rgba(244,240,224,0.04)' }}
                contentStyle={{
                  backgroundColor: '#0a100d',
                  border: '1px solid rgba(244,240,224,0.2)',
                  borderRadius: '10px',
                  fontFamily: 'JetBrains Mono, monospace',
                  fontSize: '11px',
                  color: '#f4f0e0',
                }}
              />
              <Bar dataKey="count" radius={[0, 6, 6, 0]}>
                {byKind.map((_, i) => (
                  <Cell key={i} fill={BAR_COLORS[(i + 2) % BAR_COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
