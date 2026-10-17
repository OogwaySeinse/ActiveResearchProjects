import { CheckCircle2, AlertTriangle, Radio } from 'lucide-react';
import type { SourceStatusItem } from '../types';
import { relativeTime } from '../lib/format';

interface SourceStatusProps {
  sources: SourceStatusItem[];
  generatedAt: string;
  now: number;
}

export function SourceStatus({ sources, generatedAt, now }: SourceStatusProps) {
  return (
    <div className="wunder-glass rounded-2xl p-5">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-[rgba(244,240,224,0.1)] pb-3.5">
        <div className="flex items-center gap-2">
          <Radio className="h-4 w-4 text-[#6b9e78]" />
          <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-[#f4f0e0]">
            Scraper Feed Telemetry ({sources.length} modular adapters)
          </span>
        </div>
        <span className="font-mono text-[11px] text-[#7a8275]">
          Snapshot updated {relativeTime(generatedAt, now)} ({new Date(generatedAt).toUTCString()})
        </span>
      </div>

      <div className="mt-3.5 grid grid-cols-1 gap-2.5 sm:grid-cols-2 lg:grid-cols-3">
        {sources.map((src) => {
          const isOk = src.status === 'ok' || src.status === 'cached';
          return (
            <div
              key={src.name}
              className="flex items-center justify-between rounded-xl border border-[rgba(244,240,224,0.1)] bg-[rgba(10,16,13,0.6)] px-3.5 py-2.5"
            >
              <div className="flex items-center gap-2.5 truncate">
                {isOk ? (
                  <CheckCircle2 className="h-4 w-4 shrink-0 text-[#6b9e78]" />
                ) : (
                  <AlertTriangle className="h-4 w-4 shrink-0 text-[#d4843e]" />
                )}
                <div className="truncate">
                  <div className="truncate font-mono text-xs text-[#f4f0e0]">
                    {src.name}
                  </div>
                  <div className="truncate font-mono text-[10px] text-[#7a8275]">
                    {src.label}
                  </div>
                </div>
              </div>
              <div className="ml-3 shrink-0 text-right">
                <span className="rounded-full bg-[rgba(244,240,224,0.08)] px-2 py-0.5 font-mono text-xs font-semibold text-[#c8a96e]">
                  {src.count}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
