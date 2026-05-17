import { notFound } from 'next/navigation';
import {
  ApiClientError,
  fetchFundamentals,
  fetchInsider,
  fetchInstitutional,
  fetchTickerSummary,
} from '@/lib/api';
import { TickerPage } from '@/components/ticker/TickerPage';
import type { Metadata } from 'next';
import type { FundamentalsResponse } from '@/types/fundamentals';
import type { InsiderResponse } from '@/types/insider';
import type { InstitutionalResponse } from '@/types/institutional';
import type { TickerSummary } from '@/types/ticker';

interface PageProps {
  params: { ticker: string };
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const ticker = params.ticker.toUpperCase();
  return {
    title: `${ticker} · CatalystLens`,
  };
}

export default async function Page({ params }: PageProps) {
  const ticker = params.ticker.toUpperCase();

  let summary: TickerSummary | null = null;
  let fundamentals: FundamentalsResponse | null = null;
  let errorMessage: string | null = null;
  let fundamentalsError: string | null = null;
  let institutional: InstitutionalResponse | null = null;
  let institutionalError: string | null = null;
  let insider: InsiderResponse | null = null;
  let insiderError: string | null = null;

  try {
    summary = await fetchTickerSummary(ticker);
  } catch (err) {
    if (err instanceof ApiClientError && err.status === 404) {
      notFound();
    }
    errorMessage = err instanceof Error ? err.message : 'Failed to load summary.';
  }

  try {
    insider = await fetchInsider(ticker);
  } catch (err) {
    if (err instanceof ApiClientError && err.status === 404) {
      insiderError = 'No insider transaction fixture for this ticker yet.';
    } else {
      insiderError = err instanceof Error ? err.message : 'Failed to load insider data.';
    }
  }

  try {
    fundamentals = await fetchFundamentals(ticker);
  } catch (err) {
    if (err instanceof ApiClientError && err.status === 404) {
      fundamentalsError = 'No fundamentals fixture for this ticker yet.';
    } else {
      fundamentalsError =
        err instanceof Error ? err.message : 'Failed to load fundamentals.';
    }
  }

  try {
    institutional = await fetchInstitutional(ticker);
  } catch (err) {
    if (err instanceof ApiClientError && err.status === 404) {
      institutionalError = 'No institutional (13F) fixture for this ticker yet.';
    } else {
      institutionalError =
        err instanceof Error ? err.message : 'Failed to load institutional holdings.';
    }
  }

  // If the summary call failed for a non-404 reason, render an explicit error
  // state with a placeholder summary so the page still mounts.
  if (!summary) {
    summary = {
      ticker,
      company_name: null,
      exchange: null,
      price: null,
      change_pct: null,
      volume: null,
      relative_volume: null,
      session: 'closed',
      last_bar_time: null,
      latest_event: null,
    };
  }

  return (
    <TickerPage
      summary={summary}
      fundamentals={fundamentals}
      fundamentalsError={fundamentalsError}
      institutional={institutional}
      institutionalError={institutionalError}
      insider={insider}
      insiderError={insiderError}
      errorMessage={errorMessage}
    />
  );
}
