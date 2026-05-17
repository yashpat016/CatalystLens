'use client';

import { Card } from '@/components/ui/Card';
import { formatPrice, toNumber } from '@/lib/format';
import type { InsiderResponse, InsiderTransaction } from '@/types/insider';

interface InsiderPanelProps {
  data: InsiderResponse;
}

export function InsiderPanel({ data }: InsiderPanelProps) {
  const ceoTx = data.transactions.filter(
    (t) => t.role.toUpperCase().includes('CEO') || t.role.toUpperCase() === 'CHIEF EXECUTIVE OFFICER',
  );
  const rest = data.transactions.filter((t) => !ceoTx.includes(t));

  return (
    <section aria-label="Insider transactions">
      <Card title="Insider activity (Form 4 style)">
        <p className="mb-3 text-xs text-text-muted">
          CEO and executive open-market transactions from demo fixtures — not live SEC filings.
        </p>
        {data.data_notes.length > 0 ? (
          <ul className="mb-4 list-inside list-disc text-xs text-text-subtle">
            {data.data_notes.map((n) => (
              <li key={n}>{n}</li>
            ))}
          </ul>
        ) : null}

        {ceoTx.length > 0 ? (
          <TxTable title="CEO" rows={ceoTx} />
        ) : null}
        {rest.length > 0 ? (
          <TxTable title="Other insiders" rows={rest} />
        ) : null}
      </Card>
    </section>
  );
}

function TxTable({ title, rows }: { title: string; rows: InsiderTransaction[] }) {
  return (
    <div className="mb-6 last:mb-0">
      <h3 className="mb-2 text-sm font-medium text-text">{title}</h3>
      <div className="max-h-72 overflow-auto rounded-lg border border-border-subtle">
        <table className="w-full text-left text-xs">
          <thead className="sticky top-0 bg-bg-elevated">
            <tr className="border-b border-border text-text-subtle">
              <th className="py-2 pl-3 pr-3">Date</th>
              <th className="py-2 pr-3">Insider</th>
              <th className="py-2 pr-3">Role</th>
              <th className="py-2 pr-3">Type</th>
              <th className="py-2 pr-3">Shares</th>
              <th className="py-2 pr-3">Price</th>
              <th className="py-2 pr-3">Value</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((t, i) => (
              <tr key={`${t.transaction_date}-${t.insider_name}-${i}`} className="border-b border-border-subtle">
                <td className="py-2 pl-3 pr-3 font-mono">{t.transaction_date}</td>
                <td className="py-2 pr-3">{t.insider_name}</td>
                <td className="py-2 pr-3 text-text-muted">{t.role}</td>
                <td className="py-2 pr-3">
                  <TxBadge type={t.transaction_type} />
                </td>
                <td className="py-2 pr-3 font-mono">{t.shares.toLocaleString()}</td>
                <td className="py-2 pr-3 font-mono">
                  {t.price_usd !== null ? `$${formatPrice(t.price_usd)}` : '—'}
                </td>
                <td className="py-2 pr-3 font-mono">
                  {t.value_usd !== null ? `$${formatValue(t.value_usd)}` : '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function TxBadge({ type }: { type: InsiderTransaction['transaction_type'] }) {
  if (type === 'buy') {
    return <span className="font-semibold text-accent-green">Buy</span>;
  }
  if (type === 'sell') {
    return <span className="font-semibold text-accent-red">Sell</span>;
  }
  return <span className="text-text-muted">{type}</span>;
}

function formatValue(v: string | number): string {
  const n = toNumber(v);
  if (n === null) return '—';
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(2)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toFixed(0);
}
