/** Yahoo Finance quote URL for a CatalystLens ticker. */

export function yahooFinanceUrl(ticker: string): string {
  const t = ticker.toUpperCase();
  if (t === 'BTC') return 'https://finance.yahoo.com/quote/BTC-USD';
  if (t === 'ETH') return 'https://finance.yahoo.com/quote/ETH-USD';
  return `https://finance.yahoo.com/quote/${encodeURIComponent(t)}`;
}
