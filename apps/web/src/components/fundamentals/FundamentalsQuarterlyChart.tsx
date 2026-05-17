'use client';

import { useCallback, useEffect, useMemo, useRef } from 'react';
import {
  ColorType,
  createChart,
  type IChartApi,
  type ISeriesApi,
  type LineData,
  type UTCTimestamp,
} from 'lightweight-charts';
import type { QuarterlyPeriod } from '@/types/fundamentals';

export interface QuarterlySeries {
  id: string;
  label: string;
  color: string;
  values: number[];
  /** e.g. '$' or '%' */
  valueSuffix?: string;
}

interface FundamentalsQuarterlyChartProps {
  periods: QuarterlyPeriod[];
  series: QuarterlySeries[];
  height?: number;
  yAxisHint?: string;
}

function periodToTime(period_end: string): UTCTimestamp {
  return Math.floor(new Date(`${period_end}T12:00:00Z`).getTime() / 1000) as UTCTimestamp;
}

function buildLineData(periods: QuarterlyPeriod[], values: number[]): LineData[] {
  const out: LineData[] = [];
  for (let i = 0; i < periods.length; i++) {
    const v = values[i];
    if (!Number.isFinite(v)) continue;
    out.push({ time: periodToTime(periods[i].period_end), value: v });
  }
  return out;
}

export function FundamentalsQuarterlyChart({
  periods,
  series,
  height = 280,
  yAxisHint,
}: FundamentalsQuarterlyChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRefs = useRef<ISeriesApi<'Line'>[]>([]);

  const resetZoom = useCallback(() => {
    chartRef.current?.timeScale().fitContent();
  }, []);

  const legend = useMemo(() => series.map((s) => s.label).join(' · '), [series]);

  useEffect(() => {
    if (!containerRef.current || periods.length < 2) return;

    const chart = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height,
      layout: {
        background: { type: ColorType.Solid, color: '#11151c' },
        textColor: '#8b94a3',
        fontSize: 11,
      },
      grid: {
        vertLines: { color: '#1f2530' },
        horzLines: { color: '#1f2530' },
      },
      rightPriceScale: { borderColor: '#1f2530' },
      timeScale: {
        borderColor: '#1f2530',
        timeVisible: true,
        fixLeftEdge: false,
        fixRightEdge: false,
        minBarSpacing: 8,
      },
      handleScroll: { mouseWheel: true, pressedMouseMove: true, horzTouchDrag: true },
      handleScale: {
        axisPressedMouseMove: { time: true, price: true },
        mouseWheel: true,
        pinch: true,
      },
    });

    chartRef.current = chart;
    seriesRefs.current = series.map((s) =>
      chart.addLineSeries({
        color: s.color,
        lineWidth: 2,
        title: s.label,
        lastValueVisible: true,
        priceLineVisible: false,
      }),
    );

    const onResize = () => {
      if (chartRef.current && containerRef.current) {
        chartRef.current.applyOptions({ width: containerRef.current.clientWidth });
      }
    };
    window.addEventListener('resize', onResize);

    return () => {
      window.removeEventListener('resize', onResize);
      chart.remove();
      chartRef.current = null;
      seriesRefs.current = [];
    };
  }, [height, periods.length, series]);

  useEffect(() => {
    seriesRefs.current.forEach((line, idx) => {
      line.setData(buildLineData(periods, series[idx].values));
    });
    resetZoom();
  }, [periods, series, resetZoom]);

  if (periods.length < 2) {
    return <p className="text-sm text-text-muted">Not enough quarters to chart.</p>;
  }

  return (
    <div>
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <p className="text-xs text-text-muted">
          {legend}
          {yAxisHint ? ` · ${yAxisHint}` : ''}
        </p>
        <button
          type="button"
          onClick={resetZoom}
          className="rounded border border-border px-2 py-0.5 text-[10px] text-text-muted hover:text-accent"
        >
          Reset zoom
        </button>
      </div>
      <div
        ref={containerRef}
        className="w-full overflow-hidden rounded-lg border border-border bg-bg-surface"
        style={{ height }}
        role="img"
        aria-label={`Quarterly chart: ${legend}`}
      />
    </div>
  );
}
