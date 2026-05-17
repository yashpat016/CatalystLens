'use client';

export interface BarChartItem {
  label: string;
  value: number;
  sublabel?: string;
  color?: string;
}

interface SimpleBarChartProps {
  items: BarChartItem[];
  valueFormatter?: (n: number) => string;
  height?: number;
}

export function SimpleBarChart({
  items,
  valueFormatter = (n) => n.toFixed(2),
  height = 200,
}: SimpleBarChartProps) {
  if (items.length === 0) {
    return (
      <div className="flex h-32 items-center justify-center text-sm text-text-muted">No data</div>
    );
  }

  const max = Math.max(...items.map((i) => Math.abs(i.value)), 0.001);

  return (
    <div className="w-full" style={{ height }} role="img" aria-label="Bar chart">
      <div className="flex h-full items-end justify-between gap-2 border-b border-border pb-1">
        {items.map((item) => {
          const pct = (Math.abs(item.value) / max) * 100;
          const barColor = item.color ?? (item.value >= 0 ? '#4f8cff' : '#ef4444');
          return (
            <div key={item.label} className="flex min-w-0 flex-1 flex-col items-center gap-1">
              <span className="font-mono text-[10px] text-text-muted">
                {valueFormatter(item.value)}
              </span>
              <div
                className="w-full max-w-[48px] rounded-t"
                style={{
                  height: `${Math.max(pct, 4)}%`,
                  backgroundColor: barColor,
                  minHeight: 4,
                }}
                title={`${item.label}: ${valueFormatter(item.value)}`}
              />
              <span className="truncate text-center text-[10px] text-text-subtle">{item.label}</span>
              {item.sublabel ? (
                <span className="text-[9px] text-text-muted">{item.sublabel}</span>
              ) : null}
            </div>
          );
        })}
      </div>
    </div>
  );
}
