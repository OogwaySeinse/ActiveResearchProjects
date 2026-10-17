import { useState, useRef, useEffect } from 'react';
import { ChevronDown, Check, X } from 'lucide-react';

interface MultiSelectProps {
  label: string;
  options: { value: string; label: string; count?: number }[];
  selected: string[];
  onChange: (next: string[]) => void;
}

export function MultiSelect({ label, options, selected, onChange }: MultiSelectProps) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener('mousedown', handleOutside);
    return () => document.removeEventListener('mousedown', handleOutside);
  }, []);

  const toggle = (val: string) => {
    if (selected.includes(val)) {
      onChange(selected.filter((v) => v !== val));
    } else {
      onChange([...selected, val]);
    }
  };

  return (
    <div className="relative" ref={containerRef}>
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className={`inline-flex items-center gap-2 rounded-full border px-3.5 py-1.5 font-mono text-[11px] uppercase tracking-[0.14em] transition ${
          selected.length > 0
            ? 'border-[#f4f0e0]/45 bg-[#f4f0e0]/10 text-[#f4f0e0]'
            : 'border-[rgba(244,240,224,0.14)] bg-[rgba(10,16,13,0.65)] text-[#c4c8b8] hover:border-[rgba(244,240,224,0.3)] hover:text-[#f4f0e0]'
        }`}
      >
        <span>{label}</span>
        {selected.length > 0 && (
          <span className="rounded-full bg-[#f4f0e0] px-1.5 py-0.2 text-[10px] font-semibold text-[#0a100d]">
            {selected.length}
          </span>
        )}
        <ChevronDown className="h-3.5 w-3.5 opacity-60" />
      </button>

      {open && (
        <div className="wunder-glass absolute left-0 z-50 mt-2 max-h-72 w-64 overflow-y-auto rounded-xl p-1.5 shadow-2xl">
          {selected.length > 0 && (
            <button
              type="button"
              onClick={() => onChange([])}
              className="mb-1 flex w-full items-center justify-between rounded-lg px-2.5 py-1.5 font-mono text-[10px] uppercase tracking-[0.14em] text-[#c4c8b8] hover:bg-[rgba(244,240,224,0.06)] hover:text-[#f4f0e0]"
            >
              <span>Clear selection</span>
              <X className="h-3 w-3" />
            </button>
          )}
          {options.map((opt) => {
            const isChecked = selected.includes(opt.value);
            return (
              <button
                key={opt.value}
                type="button"
                onClick={() => toggle(opt.value)}
                className="flex w-full items-center justify-between rounded-lg px-2.5 py-1.5 text-left font-mono text-xs text-[#c4c8b8] transition hover:bg-[rgba(244,240,224,0.06)] hover:text-[#f4f0e0]"
              >
                <div className="flex items-center gap-2 truncate">
                  <span
                    className={`flex h-3.5 w-3.5 shrink-0 items-center justify-center rounded border ${
                      isChecked
                        ? 'border-[#f4f0e0] bg-[#f4f0e0] text-[#0a100d]'
                        : 'border-[rgba(244,240,224,0.25)] bg-transparent'
                    }`}
                  >
                    {isChecked && <Check className="h-2.5 w-2.5 stroke-[3]" />}
                  </span>
                  <span className="truncate">{opt.label}</span>
                </div>
                {opt.count !== undefined && (
                  <span className="ml-2 font-mono text-[10px] text-[#7a8275]">{opt.count}</span>
                )}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

