/** Standard Fibonacci retracement ratios (top = 0%, bottom = 100% of the swing). */

export interface FibLevel {
  label: string;
  ratio: number;
  price: number;
}

export interface FibRange {
  high: number;
  low: number;
}

export const FIB_RETRACEMENT_RATIOS: { label: string; ratio: number }[] = [
  { label: '0.0%', ratio: 0 },
  { label: '23.6%', ratio: 0.236 },
  { label: '38.2%', ratio: 0.382 },
  { label: '50.0%', ratio: 0.5 },
  { label: '61.8%', ratio: 0.618 },
  { label: '78.6%', ratio: 0.786 },
  { label: '100%', ratio: 1 },
];

/**
 * Retracement levels between ``low`` (100%) and ``high`` (0%) after an upswing.
 * Pullback support often clusters near 38.2–61.8%.
 */
function parsePrice(raw: string): number | null {
  const n = Number.parseFloat(raw.trim());
  return Number.isFinite(n) && n > 0 ? n : null;
}

export function resolveFibRange(highInput: string, lowInput: string): FibRange | null {
  const high = parsePrice(highInput);
  const low = parsePrice(lowInput);
  if (high === null || low === null || high <= low) return null;
  return { high, low };
}

export function fibRetracementLevels(high: number, low: number): FibLevel[] {
  if (!Number.isFinite(high) || !Number.isFinite(low) || high <= low) {
    return [];
  }
  const range = high - low;
  return FIB_RETRACEMENT_RATIOS.map(({ label, ratio }) => ({
    label,
    ratio,
    price: high - range * ratio,
  }));
}
