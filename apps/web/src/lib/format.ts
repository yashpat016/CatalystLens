/**
 * Display helpers for numbers, prices, and volumes.
 *
 * All numeric API values arrive as strings (because we use Pydantic Decimal) or
 * numbers. These helpers coerce safely and produce trader-friendly output.
 */

export function toNumber(value: string | number | null | undefined): number | null {
  if (value === null || value === undefined) return null;
  const n = typeof value === 'string' ? Number(value) : value;
  return Number.isFinite(n) ? n : null;
}

export function formatPrice(value: string | number | null | undefined, digits = 2): string {
  const n = toNumber(value);
  if (n === null) return '--';
  return n.toLocaleString('en-US', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

export function formatPercent(value: string | number | null | undefined, digits = 2): string {
  const n = toNumber(value);
  if (n === null) return '--';
  const sign = n > 0 ? '+' : '';
  return `${sign}${n.toFixed(digits)}%`;
}

export function formatVolume(value: number | null | undefined): string {
  if (value === null || value === undefined) return '--';
  if (value >= 1_000_000_000) return `${(value / 1_000_000_000).toFixed(2)}B`;
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(2)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
  return value.toLocaleString('en-US');
}

export function changeColor(value: string | number | null | undefined): string {
  const n = toNumber(value);
  if (n === null || n === 0) return 'text-text-muted';
  return n > 0 ? 'text-accent-green' : 'text-accent-red';
}
