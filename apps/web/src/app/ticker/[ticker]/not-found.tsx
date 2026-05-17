import Link from 'next/link';
import { WATCHLIST_TICKERS } from '@/config/watchlist';

export default function NotFound() {
  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col items-center justify-center px-6 py-16 text-center">
      <p className="mb-3 text-xs uppercase tracking-[0.3em] text-text-muted">CatalystLens</p>
      <h1 className="mb-3 text-3xl font-semibold tracking-tight text-text">
        Unknown ticker
      </h1>
      <p className="mb-6 max-w-md text-text-muted">
        That ticker is not in the watchlist. Pick one below or add it to{' '}
        <code className="text-xs">config/watchlist.json</code> and re-run seed.
      </p>
      <div className="flex max-w-lg flex-wrap justify-center gap-2">
        {WATCHLIST_TICKERS.map((t) => (
          <Link
            key={t}
            href={`/ticker/${t}`}
            className="rounded-md border border-border bg-bg-elevated px-4 py-2 font-mono text-sm font-semibold tracking-wide text-text hover:border-accent hover:text-accent"
          >
            {t}
          </Link>
        ))}
      </div>
    </main>
  );
}
