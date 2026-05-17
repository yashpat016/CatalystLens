/** Simple / weighted moving averages aligned to bar series (period = bar count). */

export type MaType = 'sma' | 'wma';

export function movingAverage(
  closes: number[],
  period: number,
  type: MaType,
): (number | null)[] {
  if (period < 1 || closes.length === 0) return closes.map(() => null);
  if (type === 'sma') return sma(closes, period);
  return wma(closes, period);
}

export function sma(values: number[], period: number): (number | null)[] {
  const out: (number | null)[] = [];
  for (let i = 0; i < values.length; i++) {
    if (i + 1 < period) {
      out.push(null);
      continue;
    }
    let sum = 0;
    for (let j = i - period + 1; j <= i; j++) sum += values[j];
    out.push(sum / period);
  }
  return out;
}

export function wma(values: number[], period: number): (number | null)[] {
  const out: (number | null)[] = [];
  const denom = (period * (period + 1)) / 2;
  for (let i = 0; i < values.length; i++) {
    if (i + 1 < period) {
      out.push(null);
      continue;
    }
    let weighted = 0;
    for (let j = 0; j < period; j++) {
      weighted += values[i - period + 1 + j] * (j + 1);
    }
    out.push(weighted / denom);
  }
  return out;
}
