'use client';

export type QuarterWindow = 8 | 12 | 20 | 'all';

interface QuarterRangeControlProps {
  total: number;
  value: QuarterWindow;
  onChange: (w: QuarterWindow) => void;
}

const OPTIONS: { value: QuarterWindow; label: string }[] = [
  { value: 8, label: '8Q (~2y)' },
  { value: 12, label: '12Q (~3y)' },
  { value: 20, label: '20Q (~5y)' },
  { value: 'all', label: 'All' },
];

export function QuarterRangeControl({ total, value, onChange }: QuarterRangeControlProps) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="text-xs text-text-muted">History window:</span>
      {OPTIONS.filter((o) => o.value === 'all' || (typeof o.value === 'number' && o.value <= total)).map(
        (o) => (
          <button
            key={String(o.value)}
            type="button"
            onClick={() => onChange(o.value)}
            className={`rounded-full border px-3 py-1 text-xs ${
              value === o.value
                ? 'border-accent bg-accent/15 text-accent'
                : 'border-border text-text-muted hover:border-accent/40'
            }`}
          >
            {o.label}
          </button>
        ),
      )}
      <span className="text-[10px] text-text-subtle">({total} quarters available)</span>
    </div>
  );
}

export function slicePeriods<T>(periods: T[], window: QuarterWindow): T[] {
  if (window === 'all') return periods;
  return periods.slice(-window);
}
