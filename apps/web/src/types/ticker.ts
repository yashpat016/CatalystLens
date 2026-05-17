export type SessionLabel = 'premarket' | 'regular' | 'afterhours' | 'closed';
export type Timeframe = '1m' | '5m' | '1h' | '1d' | '1mo';

export interface Bar {
  timestamp: string; // ISO-8601 UTC
  open: string | number;
  high: string | number;
  low: string | number;
  close: string | number;
  volume: number;
  vwap?: string | number | null;
  trade_count?: number | null;
  session: SessionLabel;
}

export interface BarsResponse {
  ticker: string;
  timeframe: Timeframe;
  bars: Bar[];
}

export interface TickerSummary {
  ticker: string;
  company_name: string | null;
  exchange: string | null;
  price: string | number | null;
  change_pct: string | number | null;
  volume: number | null;
  relative_volume: string | number | null;
  session: SessionLabel;
  last_bar_time: string | null;
  latest_event: Record<string, unknown> | null;
}

export interface ApiError {
  detail: string;
}
