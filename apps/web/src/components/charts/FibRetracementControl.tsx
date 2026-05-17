'use client';

import { useEffect, useMemo } from 'react';
import {
  fibRetracementLevels,
  resolveFibRange,
  type FibRange,
} from '@/lib/fibonacci';
import { swingRangeFromBars } from '@/lib/swingRange';
import type { Bar } from '@/types/ticker';

interface FibRetracementControlProps {
  enabled: boolean;
  onEnabledChange: (v: boolean) => void;
  highInput: string;
  lowInput: string;
  onHighChange: (v: string) => void;
  onLowChange: (v: string) => void;
  bars: Bar[];
  onRangeResolved: (range: FibRange | null) => void;
}

export function FibRetracementControl({
  enabled,
  onEnabledChange,
  highInput,
  lowInput,
  onHighChange,
  onLowChange,
  bars,
  onRangeResolved,
}: FibRetracementControlProps) {
  const range = useMemo(() => resolveFibRange(highInput, lowInput), [highInput, lowInput]);
  const levels = useMemo(
    () => (range ? fibRetracementLevels(range.high, range.low) : []),
    [range],
  );

  useEffect(() => {
    onRangeResolved(enabled && range ? range : null);
  }, [enabled, range, onRangeResolved]);

  const fillFromChart = () => {
    const swing = swingRangeFromBars(bars);
    if (!swing) return;
    onHighChange(swing.high.toFixed(2));
    onLowChange(swing.low.toFixed(2));
  };

  const invalid =
    enabled &&
    highInput.trim() !== '' &&
    lowInput.trim() !== '' &&
    range === null;

  return (
    <div className="mb-3 space-y-2">
      <div className="flex flex-wrap items-center gap-3">
        <label className="flex cursor-pointer items-center gap-2 text-xs text-text-muted">
          <input
            type="checkbox"
            checked={enabled}
            onChange={(e) => onEnabledChange(e.target.checked)}
            className="rounded border-border"
          />
          Fib retracement
        </label>
        {enabled ? (
          <>
            <label className="flex items-center gap-1.5 text-xs text-text-muted">
              <span className="whitespace-nowrap">High $</span>
              <input
                type="text"
                inputMode="decimal"
                value={highInput}
                onChange={(e) => onHighChange(e.target.value)}
                placeholder="0.00"
                className="w-24 rounded border border-border bg-bg-elevated px-2 py-1 font-mono text-xs text-text"
              />
            </label>
            <label className="flex items-center gap-1.5 text-xs text-text-muted">
              <span className="whitespace-nowrap">Low $</span>
              <input
                type="text"
                inputMode="decimal"
                value={lowInput}
                onChange={(e) => onLowChange(e.target.value)}
                placeholder="0.00"
                className="w-24 rounded border border-border bg-bg-elevated px-2 py-1 font-mono text-xs text-text"
              />
            </label>
            <button
              type="button"
              onClick={fillFromChart}
              disabled={bars.length === 0}
              className="rounded border border-border-subtle px-2 py-1 text-xs text-text-muted hover:border-border hover:text-text disabled:opacity-40"
            >
              Fill from chart range
            </button>
          </>
        ) : null}
      </div>
      {enabled ? (
        invalid ? (
          <p className="text-xs text-accent-red">High must be greater than low.</p>
        ) : levels.length > 0 ? (
          <div className="rounded-lg border border-border-subtle bg-bg-elevated px-3 py-2 text-xs text-text-muted">
            <p className="mb-1 font-medium text-text">
              Pullback levels (0% = high ${range!.high.toFixed(2)}, 100% = low $
              {range!.low.toFixed(2)})
            </p>
            <ul className="flex flex-wrap gap-x-3 gap-y-0.5 font-mono text-[10px]">
              {levels.map((l) => (
                <li key={l.label}>
                  {l.label}: ${l.price.toFixed(2)}
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <p className="text-xs text-text-subtle">Enter swing high and low to draw levels on the chart.</p>
        )
      ) : null}
    </div>
  );
}
