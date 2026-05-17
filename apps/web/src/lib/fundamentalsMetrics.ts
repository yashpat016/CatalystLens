import { toNumber } from '@/lib/format';
import type { QuarterlyPeriod } from '@/types/fundamentals';

export type MetricId = 'stock' | 'revenue' | 'fcf' | 'debt' | 'margin';

export interface MetricDef {
  id: MetricId;
  label: string;
  /** How values are plotted on the assigned axis. */
  mode: 'indexed' | 'percent';
  color: string;
}

export const METRICS: Record<MetricId, MetricDef> = {
  stock: { id: 'stock', label: 'Stock price', mode: 'indexed', color: '#4f8cff' },
  revenue: { id: 'revenue', label: 'Net revenue', mode: 'indexed', color: '#22c55e' },
  fcf: { id: 'fcf', label: 'Free cash flow', mode: 'indexed', color: '#a78bfa' },
  debt: { id: 'debt', label: 'Total debt', mode: 'indexed', color: '#f59e0b' },
  margin: { id: 'margin', label: 'Net margin', mode: 'percent', color: '#e6e8ec' },
};

export const METRIC_IDS = Object.keys(METRICS) as MetricId[];

export interface MetricPair {
  left: MetricId;
  right: MetricId;
}

export function pairKey(pair: MetricPair): string {
  return `${pair.left}__${pair.right}`;
}

export function pairTitle(pair: MetricPair): string {
  return `${METRICS[pair.left].label} vs ${METRICS[pair.right].label}`;
}

/** Curated dual-axis views that read clearly on two scales. */
export const RECOMMENDED_PAIRS: MetricPair[] = [
  { left: 'stock', right: 'margin' },
  { left: 'stock', right: 'revenue' },
  { left: 'revenue', right: 'margin' },
  { left: 'debt', right: 'revenue' },
  { left: 'debt', right: 'stock' },
  { left: 'debt', right: 'margin' },
  { left: 'revenue', right: 'fcf' },
  { left: 'stock', right: 'fcf' },
  { left: 'debt', right: 'fcf' },
];

function rawValue(period: QuarterlyPeriod, id: MetricId): number {
  switch (id) {
    case 'stock':
      return toNumber(period.quarter_end_price) ?? 0;
    case 'revenue':
      return toNumber(period.revenue) ?? 0;
    case 'fcf':
      return toNumber(period.free_cash_flow) ?? 0;
    case 'debt':
      return toNumber(period.total_debt) ?? 0;
    case 'margin':
      return toNumber(period.net_margin_pct) ?? 0;
    default:
      return 0;
  }
}

function indexTo100(values: number[]): number[] {
  const base = values.find((v) => v > 0) ?? values[0] ?? 1;
  return values.map((v) => (v / base) * 100);
}

/** Series values aligned to ``periods`` for charting. */
export function metricSeries(periods: QuarterlyPeriod[], id: MetricId): number[] {
  const raw = periods.map((p) => rawValue(p, id));
  if (METRICS[id].mode === 'percent') return raw;
  return indexTo100(raw);
}

export function axisCaption(id: MetricId): string {
  const m = METRICS[id];
  return m.mode === 'indexed' ? `${m.label} (indexed, 100 = oldest quarter)` : `${m.label} (%)`;
}
