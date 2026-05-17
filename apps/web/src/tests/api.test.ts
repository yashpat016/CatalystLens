import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { ApiClientError, buildBarsPath, fetchTickerBars, fetchTickerSummary } from '@/lib/api';

describe('buildBarsPath', () => {
  it('uppercases the ticker and encodes it', () => {
    expect(buildBarsPath('aapl')).toBe('/api/tickers/AAPL/bars');
  });

  it('includes timeframe param when provided', () => {
    expect(buildBarsPath('AAPL', { timeframe: '1m' })).toBe('/api/tickers/AAPL/bars?timeframe=1m');
  });

  it('combines multiple params', () => {
    const path = buildBarsPath('AAPL', {
      timeframe: '1d',
      start: '2026-05-13T00:00:00Z',
      end: '2026-05-13T20:00:00Z',
    });
    expect(path).toContain('timeframe=1d');
    expect(path).toContain('start=');
    expect(path).toContain('end=');
  });
});

describe('fetchTickerSummary', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn());
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('returns parsed JSON on 200', async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      new Response(JSON.stringify({ ticker: 'AAPL', session: 'regular' }), { status: 200 }),
    );
    const result = await fetchTickerSummary('aapl');
    expect(result.ticker).toBe('AAPL');
  });

  it('throws ApiClientError on non-2xx with detail', async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      new Response(JSON.stringify({ detail: 'ticker not found' }), { status: 404 }),
    );
    await expect(fetchTickerSummary('ZZZZ')).rejects.toBeInstanceOf(ApiClientError);
  });

  it('preserves status and detail on the thrown error', async () => {
    (globalThis.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce(
      new Response(JSON.stringify({ detail: 'bad timeframe' }), { status: 422 }),
    );
    try {
      await fetchTickerSummary('AAPL');
      throw new Error('should have thrown');
    } catch (err) {
      expect(err).toBeInstanceOf(ApiClientError);
      const e = err as ApiClientError;
      expect(e.status).toBe(422);
      expect(e.detail).toBe('bad timeframe');
    }
  });
});

describe('fetchTickerBars', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn());
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('calls the bars endpoint with the right URL', async () => {
    const fetchMock = globalThis.fetch as ReturnType<typeof vi.fn>;
    fetchMock.mockResolvedValueOnce(
      new Response(JSON.stringify({ ticker: 'AAPL', timeframe: '1m', bars: [] }), { status: 200 }),
    );
    await fetchTickerBars('AAPL', { timeframe: '1m' });
    expect(fetchMock).toHaveBeenCalledTimes(1);
    const url = fetchMock.mock.calls[0][0] as string;
    expect(url).toContain('/api/tickers/AAPL/bars');
    expect(url).toContain('timeframe=1m');
  });
});
