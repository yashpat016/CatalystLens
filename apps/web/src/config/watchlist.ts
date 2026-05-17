import watchlist from '@/data/watchlist.json';

export interface WatchlistEntry {
  ticker: string;
  exchange: string;
  company_name: string;
}

export const WATCHLIST = watchlist as WatchlistEntry[];

export const WATCHLIST_TICKERS = WATCHLIST.map((e) => e.ticker);
