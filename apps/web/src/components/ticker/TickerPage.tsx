'use client';

import Link from 'next/link';
import { TickerHeader } from '@/components/ticker/TickerHeader';
import { PriceChartSection } from '@/components/ticker/PriceChartSection';
import { Card } from '@/components/ui/Card';
import { FundamentalsPanel } from '@/components/fundamentals/FundamentalsPanel';
import { InsiderPanel } from '@/components/insider/InsiderPanel';
import { InstitutionalPanel } from '@/components/institutional/InstitutionalPanel';
import type { FundamentalsResponse } from '@/types/fundamentals';
import type { InsiderResponse } from '@/types/insider';
import type { InstitutionalResponse } from '@/types/institutional';
import type { TickerSummary } from '@/types/ticker';

interface TickerPageProps {
  summary: TickerSummary;
  fundamentals?: FundamentalsResponse | null;
  fundamentalsError?: string | null;
  institutional?: InstitutionalResponse | null;
  institutionalError?: string | null;
  insider?: InsiderResponse | null;
  insiderError?: string | null;
  errorMessage?: string | null;
}

export function TickerPage({
  summary,
  fundamentals,
  fundamentalsError,
  institutional,
  institutionalError,
  insider,
  insiderError,
  errorMessage,
}: TickerPageProps) {
  return (
    <main className="mx-auto flex max-w-7xl flex-col gap-6 px-6 py-8">
      <nav className="text-xs text-text-muted">
        <Link href="/" className="hover:text-text">
          &larr; Back
        </Link>
      </nav>

      <TickerHeader summary={summary} />

      <div
        className="rounded-lg border border-accent-amber/30 bg-accent-amber/10 px-4 py-3 text-sm text-text-muted"
        role="status"
      >
        <strong className="text-accent-amber">Demo panels.</strong> Fundamentals and institutional
        (13F) sections use synthetic fixtures for research UI development — not live SEC or
        earnings data. Price charts use Alpaca when{' '}
        <code className="rounded bg-bg-elevated px-1 text-xs">MARKET_DATA_PROVIDER=alpaca</code>{' '}
        is configured.
      </div>

      {errorMessage ? (
        <Card>
          <p className="text-sm text-accent-red">{errorMessage}</p>
        </Card>
      ) : null}

      <PriceChartSection ticker={summary.ticker} />

      {fundamentalsError ? (
        <Card>
          <p className="text-sm text-accent-amber">Fundamentals: {fundamentalsError}</p>
        </Card>
      ) : fundamentals ? (
        <FundamentalsPanel data={fundamentals} />
      ) : null}

      {institutionalError ? (
        <Card>
          <p className="text-sm text-accent-amber">Institutional: {institutionalError}</p>
        </Card>
      ) : institutional ? (
        <InstitutionalPanel data={institutional} />
      ) : null}

      {insiderError ? (
        <Card>
          <p className="text-sm text-accent-amber">Insider: {insiderError}</p>
        </Card>
      ) : insider ? (
        <InsiderPanel data={insider} />
      ) : null}

      <footer className="text-xs text-text-subtle">
        VWAP is the typical-price approximation from bar data and resets on each session boundary.
        Sprint 1 omits events, alerts, and the ask panel &mdash; those arrive in later sprints.
      </footer>
    </main>
  );
}
