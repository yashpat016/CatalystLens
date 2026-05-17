import { Stat } from '@/components/ui/Stat';
import { changeColor, formatPercent, formatPrice, formatVolume } from '@/lib/format';
import { formatEtDateTime } from '@/lib/time';
import { yahooFinanceUrl } from '@/lib/yahooFinance';
import type { SessionLabel, TickerSummary } from '@/types/ticker';

interface TickerHeaderProps {
  summary: TickerSummary;
}

const SESSION_BADGE: Record<SessionLabel, { label: string; className: string }> = {
  regular: { label: 'Regular', className: 'border-accent-green/40 text-accent-green' },
  premarket: { label: 'Premarket', className: 'border-accent/40 text-accent' },
  afterhours: { label: 'After Hours', className: 'border-accent-amber/40 text-accent-amber' },
  closed: { label: 'Closed', className: 'border-border text-text-muted' },
};

export function TickerHeader({ summary }: TickerHeaderProps) {
  const badge = SESSION_BADGE[summary.session];
  const changeClass = changeColor(summary.change_pct);

  return (
    <header className="rounded-xl border border-border bg-bg-surface px-6 py-5">
      <div className="flex flex-wrap items-start justify-between gap-6">
        <div className="min-w-0">
          <div className="flex items-baseline gap-3">
            <h1 className="font-mono text-3xl font-bold tracking-wide text-text">
              {summary.ticker}
            </h1>
            <span
              className={`rounded border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider ${badge.className}`}
              aria-label={`Session: ${badge.label}`}
            >
              {badge.label}
            </span>
            <a
              href={yahooFinanceUrl(summary.ticker)}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded border border-border-subtle px-2 py-0.5 text-[10px] font-medium text-accent hover:border-accent hover:bg-accent/10"
            >
              Yahoo Finance ↗
            </a>
          </div>
          {summary.company_name ? (
            <p className="mt-1 text-sm text-text-muted">
              {summary.company_name}
              {summary.exchange ? <span className="ml-2 text-text-subtle">{summary.exchange}</span> : null}
            </p>
          ) : null}
        </div>
        <div className="flex flex-wrap items-end gap-6">
          <Stat
            label="Price"
            value={summary.price !== null ? `$${formatPrice(summary.price)}` : '--'}
          />
          <Stat
            label="Change"
            value={
              <span className={changeClass}>{formatPercent(summary.change_pct)}</span>
            }
          />
          <Stat label="Volume" value={formatVolume(summary.volume)} />
          <Stat
            label="Last Bar"
            value={
              <span className="text-sm text-text-muted">
                {summary.last_bar_time ? formatEtDateTime(summary.last_bar_time) : '--'}
              </span>
            }
          />
        </div>
      </div>
    </header>
  );
}
