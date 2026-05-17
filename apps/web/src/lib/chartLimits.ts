import type { Timeframe } from '@/types/ticker';

/** Max bars requested per timeframe (API cap is 10_000). */
export const BAR_LIMIT_BY_TIMEFRAME: Record<Timeframe, number> = {
  '1m': 2500,
  '5m': 5000,
  '1h': 3000,
  '1d': 1500,
  '1mo': 120,
};

/** Default visible window after load (logical bar count). */
export const DEFAULT_VISIBLE_BARS: Record<Timeframe, number> = {
  '1m': 390,
  '5m': 390,
  '1h': 130,
  '1d': 252,
  '1mo': 60,
};

export const TIMEFRAME_OPTIONS: { value: Timeframe; label: string; hint: string }[] = [
  { value: '1m', label: '1m', hint: 'Intraday ~2 weeks' },
  { value: '5m', label: '5m', hint: 'Intraday ~months' },
  { value: '1h', label: '1h', hint: 'Hourly ~months' },
  { value: '1d', label: '1D', hint: 'Daily ~5+ years' },
  { value: '1mo', label: '1M', hint: 'Monthly ~10 years' },
];
