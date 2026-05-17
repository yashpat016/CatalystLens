import type {
  CandlestickData,
  HistogramData,
  LineData,
  UTCTimestamp,
} from 'lightweight-charts';
import { toNumber } from '@/lib/format';
import { toUnixSeconds } from '@/lib/time';
import type { Bar } from '@/types/ticker';

export function barsToCandles(bars: Bar[]): CandlestickData<UTCTimestamp>[] {
  const candles: CandlestickData<UTCTimestamp>[] = [];
  for (const b of bars) {
    const open = toNumber(b.open);
    const high = toNumber(b.high);
    const low = toNumber(b.low);
    const close = toNumber(b.close);
    if (open === null || high === null || low === null || close === null) continue;
    candles.push({
      time: toUnixSeconds(b.timestamp) as UTCTimestamp,
      open,
      high,
      low,
      close,
    });
  }
  return candles;
}

export function buildMaSeries(bars: Bar[], maValues: (number | null)[]): LineData[] {
  const out: LineData[] = [];
  const n = Math.min(bars.length, maValues.length);
  for (let i = 0; i < n; i++) {
    const v = maValues[i];
    if (v === null || !Number.isFinite(v)) continue;
    out.push({
      time: toUnixSeconds(bars[i].timestamp) as UTCTimestamp,
      value: v,
    });
  }
  return out;
}

export function buildVwapSeries(bars: Bar[], vwap?: (number | null)[]): LineData[] {
  if (!vwap || vwap.length === 0) return [];
  const out: LineData[] = [];
  const n = Math.min(bars.length, vwap.length);
  for (let i = 0; i < n; i++) {
    const v = vwap[i];
    if (v === null || v === undefined || !Number.isFinite(v)) continue;
    out.push({
      time: toUnixSeconds(bars[i].timestamp) as UTCTimestamp,
      value: v,
    });
  }
  return out;
}

export function barsToVolume(bars: Bar[]): HistogramData[] {
  return bars.map((b) => {
    const open = toNumber(b.open) ?? 0;
    const close = toNumber(b.close) ?? 0;
    return {
      time: toUnixSeconds(b.timestamp) as UTCTimestamp,
      value: b.volume,
      color: close >= open ? '#22c55e88' : '#ef444488',
    };
  });
}

/** Shared layout options for stacked, linked charts. */
export const CHART_LAYOUT = {
  background: { type: 'solid' as const, color: '#11151c' },
  textColor: '#8b94a3',
  fontSize: 11,
};

export const CHART_GRID = {
  vertLines: { color: '#1f2530' },
  horzLines: { color: '#1f2530' },
};
