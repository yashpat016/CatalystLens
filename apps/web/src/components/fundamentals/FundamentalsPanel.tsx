'use client';

import { useMemo, useState } from 'react';
import { Card } from '@/components/ui/Card';
import { FundamentalsCompareGrid } from '@/components/fundamentals/FundamentalsCompareGrid';
import { FundamentalsQuarterlyChart } from '@/components/fundamentals/FundamentalsQuarterlyChart';
import {
  QuarterRangeControl,
  slicePeriods,
  type QuarterWindow,
} from '@/components/fundamentals/QuarterRangeControl';
import { formatPercent, formatPrice, toNumber } from '@/lib/format';
import type { FundamentalsResponse, QuarterlyPeriod } from '@/types/fundamentals';

interface FundamentalsPanelProps {
  data: FundamentalsResponse;
}

function periodLabel(p: QuarterlyPeriod): string {
  return `Q${p.fiscal_quarter} '${String(p.fiscal_year).slice(-2)}`;
}

function formatRevenueB(value: string | number | null): string {
  const n = toNumber(value);
  if (n === null) return '--';
  return `$${(n / 1_000_000_000).toFixed(2)}B`;
}

export function FundamentalsPanel({ data }: FundamentalsPanelProps) {
  const allPeriods = data.periods;
  const [window, setWindow] = useState<QuarterWindow>(12);
  const periods = useMemo(() => slicePeriods(allPeriods, window), [allPeriods, window]);

  const ue = data.upcoming_earnings;

  const epsActual = periods.map((p) => toNumber(p.eps_actual) ?? 0);
  const epsEst = periods.map((p) => toNumber(p.eps_estimate) ?? 0);
  const revenueB = periods.map((p) => (toNumber(p.revenue) ?? 0) / 1_000_000_000);
  const grossM = periods.map((p) => toNumber(p.gross_margin_pct) ?? 0);
  const operM = periods.map((p) => toNumber(p.operating_margin_pct) ?? 0);
  const netM = periods.map((p) => toNumber(p.net_margin_pct) ?? 0);

  return (
    <section className="flex flex-col gap-6" aria-label="Fundamentals and earnings">
      {ue ? (
        <Card title="Upcoming earnings">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <MetricBlock
              label="Report date"
              value={formatReportDate(ue.report_date)}
              hint={reportTimeLabel(ue.report_time)}
            />
            <MetricBlock
              label="Days until release"
              value={ue.days_until !== null ? String(ue.days_until) : '--'}
              hint={`FY${ue.fiscal_year} Q${ue.fiscal_quarter}`}
            />
            <MetricBlock
              label="Projected EPS"
              value={ue.eps_estimate !== null ? `$${formatPrice(ue.eps_estimate)}` : '--'}
              hint={
                allPeriods.length > 0
                  ? `Prior Q actual: $${formatPrice(allPeriods[allPeriods.length - 1].eps_actual)}`
                  : undefined
              }
            />
            <MetricBlock
              label="Projected revenue"
              value={formatRevenueB(ue.revenue_estimate)}
              hint={ue.analyst_count !== null ? `${ue.analyst_count} analysts` : undefined}
            />
          </div>
        </Card>
      ) : null}

      <Card title="Fundamentals comparisons (~5 years, dual-axis panels)">
        <FundamentalsCompareGrid periods={allPeriods} />
      </Card>

      <Card title="Quarterly trends">
        <QuarterRangeControl total={allPeriods.length} value={window} onChange={setWindow} />
        <p className="mb-4 mt-3 text-xs text-text-muted">
          Line charts scale to the selected window — drag to zoom a date range, scroll to
          compress/expand. Tables below list the same quarters for exact values.
        </p>

        <div className="flex flex-col gap-8">
          <div>
            <h3 className="mb-2 text-sm font-medium text-text">EPS — actual vs estimate</h3>
            <FundamentalsQuarterlyChart
              periods={periods}
              yAxisHint="USD per share"
              series={[
                { id: 'eps', label: 'EPS actual', color: '#4f8cff', values: epsActual },
                { id: 'est', label: 'EPS estimate', color: '#5a6271', values: epsEst },
              ]}
            />
            <BeatMissTable periods={periods} />
          </div>

          <div>
            <h3 className="mb-2 text-sm font-medium text-text">Revenue</h3>
            <FundamentalsQuarterlyChart
              periods={periods}
              yAxisHint="USD billions"
              series={[{ id: 'rev', label: 'Net revenue', color: '#22c55e', values: revenueB }]}
            />
            <RevenueSurpriseTable periods={periods} />
          </div>

          <div>
            <h3 className="mb-2 text-sm font-medium text-text">Margins (% of revenue)</h3>
            <FundamentalsQuarterlyChart
              periods={periods}
              yAxisHint="percent"
              series={[
                { id: 'gross', label: 'Gross', color: '#4f8cff', values: grossM },
                { id: 'oper', label: 'Operating', color: '#a78bfa', values: operM },
                { id: 'net', label: 'Net', color: '#22c55e', values: netM },
              ]}
            />
            <MarginsTimeline periods={periods.slice(-4)} />
          </div>
        </div>
      </Card>
    </section>
  );
}

function MetricBlock({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
  hint?: string;
}) {
  return (
    <div className="rounded-lg border border-border-subtle bg-bg-elevated px-4 py-3">
      <p className="text-[10px] uppercase tracking-wider text-text-subtle">{label}</p>
      <p className="mt-1 font-mono text-xl font-semibold text-text">{value}</p>
      {hint ? <p className="mt-1 text-xs text-text-muted">{hint}</p> : null}
    </div>
  );
}

function BeatMissTable({ periods }: { periods: QuarterlyPeriod[] }) {
  return (
    <div className="mt-4 max-h-64 overflow-auto rounded-lg border border-border-subtle">
      <table className="w-full text-left text-xs">
        <thead className="sticky top-0 bg-bg-elevated">
          <tr className="border-b border-border text-text-subtle">
            <th className="py-2 pl-3 pr-4">Quarter</th>
            <th className="py-2 pr-4">Reported</th>
            <th className="py-2 pr-4">Estimate</th>
            <th className="py-2 pr-4">Surprise</th>
            <th className="py-2 pr-3">Result</th>
          </tr>
        </thead>
        <tbody>
          {[...periods].reverse().map((p) => (
            <tr key={`${p.fiscal_year}-Q${p.fiscal_quarter}`} className="border-b border-border-subtle">
              <td className="py-2 pl-3 pr-4 font-mono text-text">{periodLabel(p)}</td>
              <td className="py-2 pr-4 font-mono">${formatPrice(p.eps_actual)}</td>
              <td className="py-2 pr-4 font-mono text-text-muted">${formatPrice(p.eps_estimate)}</td>
              <td className="py-2 pr-4 font-mono">{formatPercent(p.eps_surprise_pct)}</td>
              <td className="py-2 pr-3">
                {p.beat === true ? (
                  <span className="text-accent-green">Beat</span>
                ) : p.beat === false ? (
                  <span className="text-accent-red">Miss</span>
                ) : (
                  <span className="text-text-muted">—</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function RevenueSurpriseTable({ periods }: { periods: QuarterlyPeriod[] }) {
  return (
    <div className="mt-4 max-h-64 overflow-auto rounded-lg border border-border-subtle">
      <table className="w-full text-left text-xs">
        <thead className="sticky top-0 bg-bg-elevated">
          <tr className="border-b border-border text-text-subtle">
            <th className="py-2 pl-3 pr-4">Quarter</th>
            <th className="py-2 pr-4">Revenue</th>
            <th className="py-2 pr-4">Estimate</th>
            <th className="py-2 pr-3">Surprise</th>
          </tr>
        </thead>
        <tbody>
          {[...periods].reverse().map((p) => (
            <tr key={`rev-${p.fiscal_year}-Q${p.fiscal_quarter}`} className="border-b border-border-subtle">
              <td className="py-2 pl-3 pr-4 font-mono">{periodLabel(p)}</td>
              <td className="py-2 pr-4 font-mono">{formatRevenueB(p.revenue)}</td>
              <td className="py-2 pr-4 font-mono text-text-muted">{formatRevenueB(p.revenue_estimate)}</td>
              <td className="py-2 pr-3 font-mono">{formatPercent(p.revenue_surprise_pct)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function MarginsTimeline({ periods }: { periods: QuarterlyPeriod[] }) {
  const recent = periods.slice(-4);
  return (
    <div className="mt-6 grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
      {recent.map((p) => (
        <div
          key={`m-${p.fiscal_year}-Q${p.fiscal_quarter}`}
          className="rounded-lg border border-border-subtle bg-bg-elevated p-3"
        >
          <p className="font-mono text-xs font-semibold text-text">{periodLabel(p)}</p>
          <dl className="mt-2 space-y-1 text-xs">
            <div className="flex justify-between">
              <dt className="text-text-muted">Gross</dt>
              <dd className="font-mono text-accent">{formatPercent(p.gross_margin_pct)}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-text-muted">Operating</dt>
              <dd className="font-mono">{formatPercent(p.operating_margin_pct)}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-text-muted">Net</dt>
              <dd className="font-mono text-accent-green">{formatPercent(p.net_margin_pct)}</dd>
            </div>
          </dl>
        </div>
      ))}
    </div>
  );
}

function formatReportDate(iso: string): string {
  const d = new Date(iso + 'T12:00:00');
  return d.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

function reportTimeLabel(t: string): string {
  if (t === 'bmo') return 'Before market open';
  if (t === 'amc') return 'After market close';
  if (t === 'dmh') return 'During market hours';
  return '';
}
