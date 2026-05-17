'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { LinkedPriceVolumeCharts } from '@/components/charts/LinkedPriceVolumeCharts';
import { ChartMaControls, type MaConfig } from '@/components/charts/ChartMaControls';
import { FibRetracementControl } from '@/components/charts/FibRetracementControl';
import type { FibRange } from '@/lib/fibonacci';
import { Card } from '@/components/ui/Card';
import { fetchTickerBars } from '@/lib/api';
import { BAR_LIMIT_BY_TIMEFRAME, TIMEFRAME_OPTIONS } from '@/lib/chartLimits';
import { toNumber } from '@/lib/format';
import { movingAverage } from '@/lib/movingAverage';
import { rollingVwap } from '@/lib/metrics';
import type { Bar, Timeframe } from '@/types/ticker';

interface PriceChartSectionProps {
  ticker: string;
}

export function PriceChartSection({ ticker }: PriceChartSectionProps) {
  const [timeframe, setTimeframe] = useState<Timeframe>('1d');
  const [bars, setBars] = useState<Bar[]>([]);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);

  const [fibEnabled, setFibEnabled] = useState(false);
  const [fibHigh, setFibHigh] = useState('');
  const [fibLow, setFibLow] = useState('');
  const [fibRange, setFibRange] = useState<FibRange | null>(null);

  const [maConfig, setMaConfig] = useState<MaConfig>({
    enabled: false,
    type: 'sma',
    period: 20,
  });

  const vwap = useMemo(() => rollingVwap(bars, { resetOn: 'session' }), [bars]);

  const closes = useMemo(
    () => bars.map((b) => toNumber(b.close) ?? 0),
    [bars],
  );

  const maConfigWithValues = useMemo((): MaConfig => {
    if (!maConfig.enabled || closes.length === 0) {
      return { ...maConfig, maValues: [] };
    }
    const maValues = movingAverage(closes, maConfig.period, maConfig.type);
    return { ...maConfig, maValues };
  }, [maConfig, closes]);

  const loadBars = useCallback(
    async (tf: Timeframe) => {
      setLoading(true);
      setFetchError(null);
      try {
        const resp = await fetchTickerBars(ticker, {
          timeframe: tf,
          limit: BAR_LIMIT_BY_TIMEFRAME[tf],
        });
        setBars(resp.bars);
      } catch (err) {
        setFetchError(err instanceof Error ? err.message : 'Failed to load bars.');
        setBars([]);
      } finally {
        setLoading(false);
      }
    },
    [ticker],
  );

  useEffect(() => {
    void loadBars(timeframe);
  }, [timeframe, loadBars]);

  const chartTitle = useMemo(() => {
    const tfLabel = TIMEFRAME_OPTIONS.find((o) => o.value === timeframe)?.label ?? timeframe;
    return `Price & volume (${tfLabel}) · linked scroll · VWAP (session-reset)`;
  }, [timeframe]);

  return (
    <Card title={chartTitle}>
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <span className="text-xs text-text-muted">Timeframe</span>
        {TIMEFRAME_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            type="button"
            title={opt.hint}
            disabled={loading}
            onClick={() => setTimeframe(opt.value)}
            className={`rounded-md border px-2.5 py-1 text-xs font-medium transition-colors ${
              timeframe === opt.value
                ? 'border-accent bg-accent/15 text-accent'
                : 'border-border-subtle text-text-muted hover:border-border hover:text-text'
            } disabled:opacity-50`}
          >
            {opt.label}
          </button>
        ))}
        {loading ? <span className="text-xs text-text-subtle">Loading…</span> : null}
      </div>

      {fetchError ? (
        <div className="mb-3 rounded-lg border border-accent-red/40 bg-accent-red/10 px-3 py-2 text-sm text-accent-red">
          <p className="font-medium">Could not load price bars</p>
          <p className="mt-1 font-mono text-xs">{fetchError}</p>
        </div>
      ) : null}

      {bars.length === 0 && !loading && !fetchError ? (
        <EmptyState message="No bars returned for this symbol and timeframe." />
      ) : bars.length > 0 || loading ? (
        <>
          <ChartMaControls config={maConfig} onChange={setMaConfig} timeframe={timeframe} />
          <FibRetracementControl
            enabled={fibEnabled}
            onEnabledChange={setFibEnabled}
            highInput={fibHigh}
            lowInput={fibLow}
            onHighChange={setFibHigh}
            onLowChange={setFibLow}
            bars={bars}
            onRangeResolved={setFibRange}
          />
          <LinkedPriceVolumeCharts
            bars={bars}
            timeframe={timeframe}
            vwap={vwap}
            fibRange={fibRange}
            maConfig={maConfigWithValues}
          />
          <p className="mt-2 text-xs text-text-subtle">
            Pan or zoom on either panel — both stay aligned. Default view shows a sensible window
            for each timeframe; scroll left for older bars.
            {bars.length > 0 ? (
              <>
                {' '}
                {bars.length} bars · {formatBarTime(bars[0].timestamp, timeframe)} →{' '}
                {formatBarTime(bars[bars.length - 1].timestamp, timeframe)}.
              </>
            ) : null}
          </p>
        </>
      ) : null}
    </Card>
  );
}

function formatBarTime(iso: string, timeframe: Timeframe): string {
  const d = new Date(iso);
  if (timeframe === '1d' || timeframe === '1mo') {
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  }
  return d.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex h-32 items-center justify-center text-sm text-text-muted">{message}</div>
  );
}
