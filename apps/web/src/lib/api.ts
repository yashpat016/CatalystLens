import type { FundamentalsResponse } from '@/types/fundamentals';
import type { InsiderResponse } from '@/types/insider';
import type { InstitutionalResponse } from '@/types/institutional';
import type { BarsResponse, TickerSummary, Timeframe } from '@/types/ticker';

/**
 * Base URL for the CatalystLens API.
 *
 * For server components (running inside the Next.js Node process in Docker)
 * we want to reach the api container by its compose service name. For client
 * components we want the browser-reachable URL on the host.
 *
 * `NEXT_PUBLIC_API_BASE_URL` is exposed to the browser; the server side
 * defaults to the internal address if no override is provided.
 */
function resolveBaseUrl(): string {
  if (typeof window === 'undefined') {
    return (
      process.env.API_BASE_URL_INTERNAL ??
      process.env.NEXT_PUBLIC_API_BASE_URL ??
      'http://127.0.0.1:8000'
    );
  }
  // Same-origin proxy (next.config rewrites) — avoids CORS when using 127.0.0.1:3000.
  return '';
}

export class ApiClientError extends Error {
  readonly status: number;
  readonly detail: string;

  constructor(status: number, detail: string) {
    super(`API ${status}: ${detail}`);
    this.status = status;
    this.detail = detail;
    this.name = 'ApiClientError';
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const base = resolveBaseUrl();
  const url = `${base}${path}`;
  const res = await fetch(url, {
    ...init,
    headers: {
      Accept: 'application/json',
      ...(init?.headers ?? {}),
    },
    cache: 'no-store',
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      if (body && typeof body.detail === 'string') {
        detail = body.detail;
      }
    } catch {
      // body wasn't JSON, fall back to statusText
    }
    throw new ApiClientError(res.status, detail);
  }

  return (await res.json()) as T;
}

export function buildBarsPath(
  ticker: string,
  options: {
    timeframe?: Timeframe;
    start?: string;
    end?: string;
    limit?: number;
  } = {},
): string {
  const params = new URLSearchParams();
  if (options.timeframe) params.set('timeframe', options.timeframe);
  if (options.start) params.set('start', options.start);
  if (options.end) params.set('end', options.end);
  if (options.limit !== undefined) params.set('limit', String(options.limit));
  const query = params.toString();
  const safeTicker = encodeURIComponent(ticker.toUpperCase());
  return `/api/tickers/${safeTicker}/bars${query ? `?${query}` : ''}`;
}

export async function fetchTickerSummary(ticker: string): Promise<TickerSummary> {
  const safeTicker = encodeURIComponent(ticker.toUpperCase());
  return request<TickerSummary>(`/api/tickers/${safeTicker}/summary`);
}

export async function fetchTickerBars(
  ticker: string,
  options: {
    timeframe?: Timeframe;
    start?: string;
    end?: string;
    limit?: number;
  } = {},
): Promise<BarsResponse> {
  return request<BarsResponse>(buildBarsPath(ticker, options));
}

export async function fetchFundamentals(ticker: string): Promise<FundamentalsResponse> {
  const safeTicker = encodeURIComponent(ticker.toUpperCase());
  return request<FundamentalsResponse>(`/api/tickers/${safeTicker}/fundamentals`);
}

export async function fetchInstitutional(ticker: string): Promise<InstitutionalResponse> {
  const safeTicker = encodeURIComponent(ticker.toUpperCase());
  return request<InstitutionalResponse>(`/api/tickers/${safeTicker}/institutional`);
}

export async function fetchInsider(ticker: string): Promise<InsiderResponse> {
  const safeTicker = encodeURIComponent(ticker.toUpperCase());
  return request<InsiderResponse>(`/api/tickers/${safeTicker}/insider`);
}
