import Link from 'next/link';
import { WATCHLIST } from '@/config/watchlist';

export default function LandingPage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-4xl flex-col items-center justify-center px-6 py-16">
      <div className="w-full">
        <header className="mb-12 text-center">
          <p className="mb-3 text-xs uppercase tracking-[0.3em] text-text-muted">CatalystLens</p>
          <h1 className="mb-4 text-4xl font-semibold tracking-tight text-text sm:text-5xl">
            See what moved your watchlist and how the market reacted.
          </h1>
          <p className="mx-auto max-w-2xl text-text-muted">
            A source-backed market event and liquidity intelligence dashboard. Not a trading bot,
            not a buy/sell signal generator &mdash; a research terminal.
          </p>
        </header>

        <section className="rounded-xl border border-border bg-bg-surface p-6">
          <p className="mb-4 text-sm font-medium text-text-muted">
            Watchlist ({WATCHLIST.length} tickers) — or open{' '}
            <code className="rounded bg-bg-elevated px-1 text-xs">/ticker/SYMBOL</code>
          </p>
          <div className="flex max-h-64 flex-wrap gap-2 overflow-y-auto">
            {WATCHLIST.map(({ ticker, company_name }) => (
              <Link
                key={ticker}
                href={`/ticker/${ticker}`}
                title={company_name}
                className="rounded-md border border-border bg-bg-elevated px-3 py-1.5 font-mono text-sm font-semibold tracking-wide text-text transition hover:border-accent hover:text-accent"
              >
                {ticker}
              </Link>
            ))}
          </div>
        </section>

        <footer className="mt-12 text-center text-xs text-text-subtle">
          Price charts use Alpaca when configured &middot; fundamentals and 13F are demo fixtures
          (synthetic, not live SEC filings)
        </footer>
      </div>
    </main>
  );
}
