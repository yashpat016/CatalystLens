/**
 * Client-side metric helpers.
 *
 * Mirrors the backend `app/metrics/vwap.py` logic so the chart can display a
 * VWAP line whether or not the API supplied one. The backend version is the
 * source of truth; this implementation exists purely for rendering.
 */

import type { Bar } from '@/types/ticker';
import { toNumber } from '@/lib/format';

function typicalPrice(bar: Bar): number | null {
  const h = toNumber(bar.high);
  const l = toNumber(bar.low);
  const c = toNumber(bar.close);
  if (h === null || l === null || c === null) return null;
  return (h + l + c) / 3;
}

export function rollingVwap(bars: Bar[], opts: { resetOn?: 'session' | 'day' | null } = {}): (number | null)[] {
  const resetOn = opts.resetOn ?? 'session';
  const out: (number | null)[] = [];
  let pv = 0;
  let v = 0;
  let lastKey: string | null = null;

  for (const bar of bars) {
    let key: string | null = null;
    if (resetOn === 'session') key = bar.session;
    else if (resetOn === 'day') key = bar.timestamp.slice(0, 10);

    if (resetOn !== null && key !== lastKey) {
      pv = 0;
      v = 0;
      lastKey = key;
    }

    const tp = typicalPrice(bar);
    if (tp !== null && bar.volume > 0) {
      pv += tp * bar.volume;
      v += bar.volume;
    }

    out.push(v > 0 ? pv / v : null);
  }

  return out;
}
