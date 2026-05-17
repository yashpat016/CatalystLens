import { Card } from '@/components/ui/Card';
import type { AggregateFlow, InstitutionalResponse } from '@/types/institutional';

interface InstitutionalPanelProps {
  data: InstitutionalResponse;
}

const FLOW_LABEL: Record<AggregateFlow, string> = {
  net_buying: 'Net buying (QoQ)',
  net_selling: 'Net selling (QoQ)',
  mixed: 'Mixed (QoQ)',
  unchanged: 'Unchanged (QoQ)',
};

const FLOW_CLASS: Record<AggregateFlow, string> = {
  net_buying: 'text-accent-green',
  net_selling: 'text-accent-red',
  mixed: 'text-accent-amber',
  unchanged: 'text-text-muted',
};

function formatShares(n: number): string {
  const abs = Math.abs(n);
  if (abs >= 1_000_000_000) return `${(n / 1_000_000_000).toFixed(2)}B`;
  if (abs >= 1_000_000) return `${(n / 1_000_000).toFixed(2)}M`;
  if (abs >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

function formatUsd(raw: string | null): string {
  if (!raw) return '—';
  const n = Number(raw);
  if (Number.isNaN(n)) return raw;
  const abs = Math.abs(n);
  if (abs >= 1e12) return `$${(n / 1e12).toFixed(2)}T`;
  if (abs >= 1e9) return `$${(n / 1e9).toFixed(2)}B`;
  if (abs >= 1e6) return `$${(n / 1e6).toFixed(1)}M`;
  return `$${n.toLocaleString()}`;
}

function formatPrice(raw: string | null): string {
  if (!raw) return '—';
  const n = Number(raw);
  return Number.isNaN(n) ? raw : `$${n.toFixed(2)}`;
}

export function InstitutionalPanel({ data }: InstitutionalPanelProps) {
  const flow = data.aggregate_flow;

  return (
    <section className="flex flex-col gap-4" aria-label="Institutional holdings (13F)">
      <div className="flex flex-col gap-1">
        <h2 className="text-lg font-semibold text-text">Institutional holdings (13F)</h2>
        <p className="text-sm text-text-muted">
          Quarter end {data.data_as_of} · filed through {data.filed_through} ·{' '}
          <span className={FLOW_CLASS[flow]}>{FLOW_LABEL[flow]}</span>
          {data.net_shares_change_qoq != null ? (
            <>
              {' '}
              ({formatShares(data.net_shares_change_qoq)} shares QoQ,{' '}
              {formatUsd(data.net_value_change_usd)} value)
            </>
          ) : null}
        </p>
      </div>

      <div
        className="rounded-lg border border-accent-amber/30 bg-accent-amber/10 px-4 py-3 text-sm text-text-muted"
        role="note"
      >
        <strong className="text-accent-amber">SEC 13F limitations.</strong> Edgar reports
        quarter-end positions, not trade-level buys/sells. Data lags the quarter by ~45 days.
        Implied prices are derived (value ÷ shares), not reported average cost.
        <ul className="mt-2 list-inside list-disc space-y-1 text-xs">
          {data.data_notes.slice(0, 3).map((note) => (
            <li key={note}>{note}</li>
          ))}
        </ul>
      </div>

      <Card title="Top institutional holders (latest 13F snapshot)">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[720px] text-left text-sm">
            <thead>
              <tr className="border-b border-border text-xs text-text-muted">
                <th className="py-2 pr-4 font-medium">Manager</th>
                <th className="py-2 pr-4 font-medium">Shares</th>
                <th className="py-2 pr-4 font-medium">QoQ Δ</th>
                <th className="py-2 pr-4 font-medium">Value</th>
                <th className="py-2 pr-4 font-medium">Pos. price*</th>
                <th className="py-2 pr-4 font-medium">Flow price†</th>
                <th className="py-2 font-medium">Activity</th>
              </tr>
            </thead>
            <tbody>
              {data.holders.map((h) => (
                <tr key={h.cik ?? h.manager_name} className="border-b border-border/60">
                  <td className="py-2 pr-4 text-text">{h.manager_name}</td>
                  <td className="py-2 pr-4 tabular-nums text-text-muted">
                    {formatShares(h.shares)}
                  </td>
                  <td
                    className={`py-2 pr-4 tabular-nums ${
                      (h.shares_change_qoq ?? 0) > 0
                        ? 'text-accent-green'
                        : (h.shares_change_qoq ?? 0) < 0
                          ? 'text-accent-red'
                          : 'text-text-muted'
                    }`}
                  >
                    {h.shares_change_qoq != null ? formatShares(h.shares_change_qoq) : '—'}
                  </td>
                  <td className="py-2 pr-4 tabular-nums text-text-muted">
                    {formatUsd(h.market_value_usd)}
                  </td>
                  <td className="py-2 pr-4 tabular-nums text-text-muted">
                    {formatPrice(h.implied_position_price_usd)}
                  </td>
                  <td className="py-2 pr-4 tabular-nums text-text-muted">
                    {formatPrice(h.implied_flow_price_usd)}
                  </td>
                  <td className="py-2 capitalize text-text-muted">{h.activity}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-3 text-xs text-text-subtle">
          *Position price = market value ÷ shares at quarter end (mark, not cost basis). †Flow
          price = value change ÷ share change when the manager added or trimmed (rough QoQ proxy).
        </p>
      </Card>

      {data.quarter_history.length > 0 ? (
        <Card title="Institutional footprint (last 4 quarters)">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-border text-xs text-text-muted">
                  <th className="py-2 pr-4 font-medium">Quarter end</th>
                  <th className="py-2 pr-4 font-medium">Holders</th>
                  <th className="py-2 pr-4 font-medium">Total shares</th>
                  <th className="py-2 pr-4 font-medium">Net QoQ Δ</th>
                  <th className="py-2 font-medium">Flow</th>
                </tr>
              </thead>
              <tbody>
                {data.quarter_history.map((q) => (
                  <tr key={q.period_end} className="border-b border-border/60">
                    <td className="py-2 pr-4 text-text-muted">{q.period_end}</td>
                    <td className="py-2 pr-4 tabular-nums text-text-muted">{q.holder_count}</td>
                    <td className="py-2 pr-4 tabular-nums text-text-muted">
                      {formatShares(q.total_shares)}
                    </td>
                    <td className="py-2 pr-4 tabular-nums text-text-muted">
                      {q.net_shares_change_qoq != null
                        ? formatShares(q.net_shares_change_qoq)
                        : '—'}
                    </td>
                    <td className={`py-2 capitalize ${FLOW_CLASS[q.aggregate_flow]}`}>
                      {q.aggregate_flow.replace('_', ' ')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      ) : null}
    </section>
  );
}
