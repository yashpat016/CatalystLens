import { toNumber } from '@/lib/format';
import type { Bar } from '@/types/ticker';

export interface SwingRange {
  high: number;
  low: number;
  highTime: string;
  lowTime: string;
}

/** Highest high and lowest low across the provided bars (e.g. visible window). */
export function swingRangeFromBars(bars: Bar[]): SwingRange | null {
  if (bars.length === 0) return null;

  let high = -Infinity;
  let low = Infinity;
  let highTime = bars[0].timestamp;
  let lowTime = bars[0].timestamp;

  for (const b of bars) {
    const h = toNumber(b.high);
    const l = toNumber(b.low);
    if (h !== null && h > high) {
      high = h;
      highTime = b.timestamp;
    }
    if (l !== null && l < low) {
      low = l;
      lowTime = b.timestamp;
    }
  }

  if (!Number.isFinite(high) || !Number.isFinite(low) || high <= low) {
    return null;
  }

  return { high, low, highTime, lowTime };
}
