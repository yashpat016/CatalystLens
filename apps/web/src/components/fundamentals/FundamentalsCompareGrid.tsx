'use client';

import { useMemo, useState } from 'react';
import { FundamentalsPairChart } from '@/components/fundamentals/FundamentalsPairChart';
import {
  METRIC_IDS,
  METRICS,
  pairKey,
  RECOMMENDED_PAIRS,
  type MetricId,
  type MetricPair,
} from '@/lib/fundamentalsMetrics';
import type { QuarterlyPeriod } from '@/types/fundamentals';

interface FundamentalsCompareGridProps {
  periods: QuarterlyPeriod[];
}

function pairsEqual(a: MetricPair, b: MetricPair): boolean {
  return a.left === b.left && a.right === b.right;
}

export function FundamentalsCompareGrid({ periods }: FundamentalsCompareGridProps) {
  const [activePairs, setActivePairs] = useState<MetricPair[]>(() => [...RECOMMENDED_PAIRS]);
  const [pickLeft, setPickLeft] = useState<MetricId>('stock');
  const [pickRight, setPickRight] = useState<MetricId>('revenue');

  const activeKeys = useMemo(() => new Set(activePairs.map(pairKey)), [activePairs]);

  const addPair = (pair: MetricPair) => {
    if (pair.left === pair.right) return;
    setActivePairs((prev) => {
      if (prev.some((p) => pairsEqual(p, pair))) return prev;
      return [...prev, pair];
    });
  };

  const removePair = (pair: MetricPair) => {
    setActivePairs((prev) => prev.filter((p) => !pairsEqual(p, pair)));
  };

  const handleAddCustom = () => {
    addPair({ left: pickLeft, right: pickRight });
  };

  return (
    <div className="flex flex-col gap-4">
      <p className="text-xs text-text-muted">
        Each panel compares <strong className="text-text">two</strong> metrics on separate Y-axes
        (quarterly, ~5 years). Dollar amounts are indexed to 100 at the oldest quarter so trends
        are comparable; margin stays in percent on the right axis. Drag or scroll on a panel to
        zoom; use legend chips to add or remove views.
      </p>

      <div className="flex flex-wrap items-end gap-3 rounded-lg border border-border bg-bg-elevated p-3">
        <label className="flex flex-col gap-1 text-xs text-text-muted">
          Left axis
          <select
            value={pickLeft}
            onChange={(e) => setPickLeft(e.target.value as MetricId)}
            className="rounded border border-border bg-bg-surface px-2 py-1.5 font-mono text-sm text-text"
          >
            {METRIC_IDS.map((id) => (
              <option key={id} value={id}>
                {METRICS[id].label}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-xs text-text-muted">
          Right axis
          <select
            value={pickRight}
            onChange={(e) => setPickRight(e.target.value as MetricId)}
            className="rounded border border-border bg-bg-surface px-2 py-1.5 font-mono text-sm text-text"
          >
            {METRIC_IDS.map((id) => (
              <option key={id} value={id}>
                {METRICS[id].label}
              </option>
            ))}
          </select>
        </label>
        <button
          type="button"
          onClick={handleAddCustom}
          disabled={pickLeft === pickRight}
          className="rounded-md border border-border bg-bg-surface px-3 py-1.5 text-xs font-medium text-text hover:border-accent disabled:opacity-40"
        >
          Add chart
        </button>
        <button
          type="button"
          onClick={() => setActivePairs([...RECOMMENDED_PAIRS])}
          className="rounded-md border border-border bg-bg-surface px-3 py-1.5 text-xs text-text-muted hover:text-text"
        >
          Show all recommended
        </button>
        <button
          type="button"
          onClick={() => setActivePairs([])}
          className="rounded-md border border-border bg-bg-surface px-3 py-1.5 text-xs text-text-muted hover:text-text"
        >
          Clear all
        </button>
      </div>

      <div className="flex flex-wrap gap-2">
        {RECOMMENDED_PAIRS.map((pair) => {
          const key = pairKey(pair);
          const on = activeKeys.has(key);
          return (
            <button
              key={key}
              type="button"
              onClick={() => (on ? removePair(pair) : addPair(pair))}
              className={`rounded-full border px-3 py-1 text-xs transition ${
                on
                  ? 'border-accent bg-accent/15 text-accent'
                  : 'border-border text-text-muted hover:border-accent/50'
              }`}
            >
              {METRICS[pair.left].label} / {METRICS[pair.right].label}
            </button>
          );
        })}
      </div>

      {activePairs.length === 0 ? (
        <p className="text-sm text-text-muted">Select a preset above or build a custom pair.</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {activePairs.map((pair) => (
            <div key={pairKey(pair)} className="relative">
              <button
                type="button"
                onClick={() => removePair(pair)}
                className="absolute right-5 top-5 z-10 rounded border border-border bg-bg px-1.5 py-0.5 text-[10px] text-text-muted hover:text-accent-red"
                aria-label="Remove chart"
              >
                ×
              </button>
              <FundamentalsPairChart periods={periods} pair={pair} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
