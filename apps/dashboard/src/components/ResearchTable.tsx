import { useMemo, useState } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getPaginationRowModel,
  flexRender,
  createColumnHelper,
  type SortingState,
} from '@tanstack/react-table';
import {
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  ExternalLink,
  Bookmark,
  CalendarPlus,
  ChevronLeft,
  ChevronRight,
  MapPin,
  Calendar,
} from 'lucide-react';
import type { ResearchProject } from '../types';
import {
  DISCIPLINE_META,
  PROJECT_TYPE_LABELS,
  formatUSD,
  formatDate,
  formatCountdown,
  getUrgency,
  primaryTargetDate,
  downloadIcsForProject,
} from '../lib/format';

interface ResearchTableProps {
  data: ResearchProject[];
  bookmarks: Set<string>;
  onToggleBookmark: (id: string) => void;
  now: number;
}

const columnHelper = createColumnHelper<ResearchProject>();

const STATUS_BADGE: Record<string, string> = {
  ending_soon: 'border-[#d4843e]/55 bg-[#d4843e]/18 text-[#f4b178]',
  active: 'border-[#6b9e78]/45 bg-[#6b9e78]/15 text-[#9fd4ac]',
  upcoming: 'border-[#c8a96e]/45 bg-[#c8a96e]/15 text-[#e6c88c]',
  rolling: 'border-[#7ba3cc]/45 bg-[#7ba3cc]/15 text-[#b3d1f0]',
};

export function ResearchTable({
  data,
  bookmarks,
  onToggleBookmark,
  now,
}: ResearchTableProps) {
  const [sorting, setSorting] = useState<SortingState>([]);

  const columns = useMemo(
    () => [
      columnHelper.display({
        id: 'bookmark',
        header: () => <span className="sr-only">Save</span>,
        cell: ({ row }) => {
          const id = row.original.id;
          const isSaved = bookmarks.has(id);
          return (
            <button
              type="button"
              onClick={() => onToggleBookmark(id)}
              className={`rounded-full p-1 transition ${
                isSaved ? 'text-[#c8a96e]' : 'text-[#7a8275] hover:text-[#f4f0e0]'
              }`}
              title={isSaved ? 'Remove from saved' : 'Save project / conference'}
            >
              <Bookmark className={`h-3.5 w-3.5 ${isSaved ? 'fill-current' : ''}`} />
            </button>
          );
        },
        size: 36,
      }),
      columnHelper.accessor('title', {
        header: 'Project / Conference / Call',
        cell: (info) => {
          const c = info.row.original;
          return (
            <div className="max-w-xl py-1">
              <div className="flex flex-wrap items-center gap-1.5">
                {c.venue_code && (
                  <span className="rounded border border-[rgba(244,240,224,0.16)] bg-[rgba(244,240,224,0.05)] px-1.5 py-0.2 font-mono text-[10px] font-semibold text-[#c8a96e]">
                    {c.venue_code}
                  </span>
                )}
                <a
                  href={c.url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1.5 font-serif text-base font-normal leading-snug text-[#f4f0e0] transition hover:text-[#c8a96e]"
                >
                  <span>{c.title}</span>
                  <ExternalLink className="h-3 w-3 shrink-0 opacity-60" />
                </a>
                {c.tier && (
                  <span className="rounded-full border border-[#c8a96e]/35 bg-[#c8a96e]/10 px-2 py-0.2 font-mono text-[9px] uppercase tracking-[0.12em] text-[#e6c88c]">
                    {c.tier}
                  </span>
                )}
              </div>
              <p className="mt-1 line-clamp-2 text-xs leading-relaxed text-[#7a8275]">
                {c.description}
              </p>
              <div className="mt-1.5 flex flex-wrap items-center gap-2.5">
                {c.location && (
                  <span className="inline-flex items-center gap-1 font-mono text-[10px] text-[#c4c8b8]">
                    <MapPin className="h-2.5 w-2.5 text-[#c8a96e]" />
                    {c.location} ({c.format})
                  </span>
                )}
                {c.event_start_date && (
                  <span className="inline-flex items-center gap-1 font-mono text-[10px] text-[#c4c8b8]">
                    <Calendar className="h-2.5 w-2.5 text-[#6b9e78]" />
                    {formatDate(c.event_start_date)}
                    {c.event_end_date && c.event_end_date !== c.event_start_date
                      ? ` – ${formatDate(c.event_end_date)}`
                      : ''}
                  </span>
                )}
                {c.tags && c.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {c.tags.slice(0, 4).map((tag) => (
                      <span
                        key={tag}
                        className="rounded border border-[rgba(244,240,224,0.1)] bg-[rgba(244,240,224,0.03)] px-1.5 py-0.2 font-mono text-[10px] text-[#7a8275]"
                      >
                        #{tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        },
      }),
      columnHelper.accessor('discipline', {
        header: 'Discipline & Subfield',
        cell: (info) => {
          const disc = info.getValue();
          const meta = DISCIPLINE_META[disc];
          const c = info.row.original;
          return (
            <div className="max-w-[220px] space-y-1">
              <span
                className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 font-mono text-[10px] uppercase tracking-[0.1em] ${meta?.badgeCls ?? ''}`}
              >
                <span>{meta?.symbol}</span>
                <span>{disc}</span>
              </span>
              <div className="font-mono text-[10px] leading-snug text-[#7a8275]">
                {c.category}
              </div>
            </div>
          );
        },
      }),
      columnHelper.accessor('project_type', {
        header: 'Track / Host',
        cell: (info) => {
          const pt = info.getValue();
          const meta = PROJECT_TYPE_LABELS[pt];
          const c = info.row.original;
          return (
            <div className="space-y-1">
              <span
                className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 font-mono text-[10px] uppercase tracking-[0.1em] ${meta?.badgeCls ?? ''}`}
              >
                <span>{meta?.icon}</span>
                <span>{meta?.label ?? pt}</span>
              </span>
              <div className="font-mono text-[10px] text-[#c4c8b8]">{c.platform}</div>
              {c.proceedings_publisher && (
                <div className="font-mono text-[9px] text-[#7a8275]">
                  {c.proceedings_publisher}
                </div>
              )}
            </div>
          );
        },
      }),
      columnHelper.accessor('funding_usd', {
        header: 'Grant / Award / Track',
        cell: (info) => {
          const usd = info.getValue();
          const raw = info.row.original.funding_raw;
          return (
            <div className="max-w-[190px]">
              <div className="font-mono text-xs font-semibold text-[#c8a96e]">
                {usd > 0 ? formatUSD(usd, false) : raw || 'Peer-Reviewed'}
              </div>
              {usd > 0 && raw && (
                <div className="mt-0.5 font-mono text-[10px] leading-snug text-[#7a8275]">
                  {raw}
                </div>
              )}
            </div>
          );
        },
      }),
      columnHelper.accessor('submission_deadline', {
        header: 'CFP / Next Milestone',
        cell: (info) => {
          const c = info.row.original;
          const urgency = getUrgency(c, now);
          const target = primaryTargetDate(c, now);
          return (
            <div className="flex items-center justify-between gap-2">
              <div>
                <div
                  className={`font-mono text-xs font-medium ${
                    urgency === 'critical'
                      ? 'text-[#d4843e]'
                      : urgency === 'soon'
                        ? 'text-[#c8a96e]'
                        : 'text-[#f4f0e0]'
                  }`}
                >
                  {formatCountdown(c, now)}
                </div>
                <div className="font-mono text-[10px] text-[#7a8275]">
                  {target.iso ? `${target.kind}: ${formatDate(target.iso)}` : 'Continuous / Open'}
                </div>
              </div>
              {(c.submission_deadline || c.event_start_date) && (
                <button
                  type="button"
                  onClick={() => downloadIcsForProject(c)}
                  className="rounded-full border border-[rgba(244,240,224,0.12)] p-1.5 text-[#7a8275] transition hover:border-[rgba(244,240,224,0.3)] hover:text-[#f4f0e0]"
                  title="Add deadline to Calendar (.ics)"
                >
                  <CalendarPlus className="h-3 w-3" />
                </button>
              )}
            </div>
          );
        },
        sortingFn: (rowA, rowB) => {
          const a = primaryTargetDate(rowA.original, now).days ?? 999999;
          const b = primaryTargetDate(rowB.original, now).days ?? 999999;
          return a - b;
        },
      }),
      columnHelper.accessor('status', {
        header: 'Status',
        cell: (info) => {
          const status = info.getValue();
          const cls = STATUS_BADGE[status] ?? STATUS_BADGE.active;
          const label = status === 'ending_soon' ? 'closing soon' : status;
          return (
            <span
              className={`inline-flex items-center rounded-full border px-2.5 py-0.5 font-mono text-[10px] uppercase tracking-[0.14em] ${cls}`}
            >
              {label}
            </span>
          );
        },
      }),
    ],
    [bookmarks, onToggleBookmark, now]
  );

  const table = useReactTable({
    data,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: {
      pagination: {
        pageSize: 25,
      },
    },
  });

  if (data.length === 0) {
    return (
      <div className="wunder-glass rounded-2xl p-12 text-center">
        <p className="font-serif text-2xl text-[#f4f0e0]">
          No matching research projects or conferences
        </p>
        <p className="mt-2 font-mono text-xs text-[#7a8275]">
          Try clearing a discipline or format filter to see all live items.
        </p>
      </div>
    );
  }

  return (
    <div className="wunder-glass overflow-hidden rounded-2xl">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-left">
          <thead>
            {table.getHeaderGroups().map((headerGroup) => (
              <tr
                key={headerGroup.id}
                className="border-b border-[rgba(244,240,224,0.12)] bg-[rgba(10,16,13,0.6)]"
              >
                {headerGroup.headers.map((header) => {
                  const canSort = header.column.getCanSort();
                  const sorted = header.column.getIsSorted();
                  return (
                    <th
                      key={header.id}
                      className="px-4 py-3.5 font-mono text-[10px] font-medium uppercase tracking-[0.18em] text-[#7a8275]"
                    >
                      {header.isPlaceholder ? null : (
                        <button
                          type="button"
                          onClick={header.column.getToggleSortingHandler()}
                          disabled={!canSort}
                          className={`inline-flex items-center gap-1.5 ${
                            canSort ? 'cursor-pointer hover:text-[#f4f0e0]' : 'cursor-default'
                          }`}
                        >
                          <span>
                            {flexRender(
                              header.column.columnDef.header,
                              header.getContext()
                            )}
                          </span>
                          {canSort && (
                            <span>
                              {sorted === 'asc' ? (
                                <ArrowUp className="h-3 w-3 text-[#c8a96e]" />
                              ) : sorted === 'desc' ? (
                                <ArrowDown className="h-3 w-3 text-[#c8a96e]" />
                              ) : (
                                <ArrowUpDown className="h-3 w-3 opacity-40" />
                              )}
                            </span>
                          )}
                        </button>
                      )}
                    </th>
                  );
                })}
              </tr>
            ))}
          </thead>
          <tbody className="divide-y divide-[rgba(244,240,224,0.08)]">
            {table.getRowModel().rows.map((row) => (
              <tr
                key={row.id}
                className="transition-colors hover:bg-[rgba(244,240,224,0.03)]"
              >
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="px-4 py-3.5 align-top">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      {table.getPageCount() > 1 && (
        <div className="flex flex-wrap items-center justify-between gap-3 border-t border-[rgba(244,240,224,0.1)] px-5 py-3.5 font-mono text-xs text-[#c4c8b8]">
          <div>
            Page{' '}
            <span className="font-semibold text-[#f4f0e0]">
              {table.getState().pagination.pageIndex + 1}
            </span>{' '}
            of <span className="text-[#f4f0e0]">{table.getPageCount()}</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
              className="inline-flex items-center gap-1 rounded-full border border-[rgba(244,240,224,0.14)] px-3 py-1 text-[11px] uppercase tracking-[0.14em] transition hover:border-[rgba(244,240,224,0.3)] disabled:opacity-40"
            >
              <ChevronLeft className="h-3.5 w-3.5" />
              Prev
            </button>
            <button
              type="button"
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
              className="inline-flex items-center gap-1 rounded-full border border-[rgba(244,240,224,0.14)] px-3 py-1 text-[11px] uppercase tracking-[0.14em] transition hover:border-[rgba(244,240,224,0.3)] disabled:opacity-40"
            >
              Next
              <ChevronRight className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
