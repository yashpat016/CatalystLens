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
import {
  axisCaption,
  METRICS,
  metricSeries,
  pairTitle,
  type MetricId,
  type MetricPair,
} from '@/lib/fundamentalsMetrics';
import type { QuarterlyPeriod } from '@/types/fundamentals';

interface FundamentalsPairChartProps {
  periods: QuarterlyPeriod[];
  pair: MetricPair;
  height?: number;
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

export function FundamentalsPairChart({
  periods,
  pair,
  height = 260,
}: FundamentalsPairChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const leftSeriesRef = useRef<ISeriesApi<'Line'> | null>(null);
  const rightSeriesRef = useRef<ISeriesApi<'Line'> | null>(null);

  const { leftValues, rightValues } = useMemo(
    () => ({
      leftValues: metricSeries(periods, pair.left),
      rightValues: metricSeries(periods, pair.right),
    }),
    [periods, pair.left, pair.right],
  );

  const resetZoom = useCallback(() => {
    const chart = chartRef.current;
    if (!chart) return;
    chart.timeScale().fitContent();
    chart.priceScale('left').applyOptions({ autoScale: true });
    chart.priceScale('right').applyOptions({ autoScale: true });
  }, []);

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
      leftPriceScale: {
        visible: true,
        borderColor: '#1f2530',
        scaleMargins: { top: 0.12, bottom: 0.12 },
      },
      rightPriceScale: {
        visible: true,
        borderColor: '#1f2530',
        scaleMargins: { top: 0.12, bottom: 0.12 },
      },
      timeScale: {
        borderColor: '#1f2530',
        timeVisible: true,
        fixLeftEdge: false,
        fixRightEdge: false,
        minBarSpacing: 6,
        barSpacing: 18,
      },
      handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
        horzTouchDrag: true,
        vertTouchDrag: true,
      },
      handleScale: {
        axisPressedMouseMove: { time: true, price: true },
        axisDoubleClickReset: { time: true, price: true },
        mouseWheel: true,
        pinch: true,
      },
      crosshair: { mode: 1 },
    });

    chartRef.current = chart;

    leftSeriesRef.current = chart.addLineSeries({
      color: METRICS[pair.left].color,
      lineWidth: 2,
      priceScaleId: 'left',
      lastValueVisible: false,
      priceLineVisible: false,
    });

    rightSeriesRef.current = chart.addLineSeries({
      color: METRICS[pair.right].color,
      lineWidth: 2,
      priceScaleId: 'right',
      lineStyle: pair.right === 'debt' ? 2 : 0,
      lastValueVisible: false,
      priceLineVisible: false,
    });

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
      leftSeriesRef.current = null;
      rightSeriesRef.current = null;
    };
  }, [height, pair.left, pair.right, periods.length]);

  useEffect(() => {
    if (!leftSeriesRef.current || !rightSeriesRef.current) return;
    leftSeriesRef.current.setData(buildLineData(periods, leftValues));
    rightSeriesRef.current.setData(buildLineData(periods, rightValues));
    resetZoom();
  }, [periods, leftValues, rightValues, resetZoom]);

  if (periods.length < 2) {
    return (
      <p className="text-sm text-text-muted">Need at least two quarters to compare metrics.</p>
    );
  }

  const oldest = periods[0]?.period_end ?? '';
  const newest = periods[periods.length - 1]?.period_end ?? '';

  return (
    <div className="rounded-lg border border-border bg-bg-surface p-3">
      <div className="mb-2 flex flex-wrap items-start justify-between gap-2">
        <div>
          <h4 className="text-sm font-semibold text-text">{pairTitle(pair)}</h4>
          <p className="text-[10px] text-text-subtle">
            {periods.length} quarters · {oldest} → {newest}
          </p>
        </div>
        <button
          type="button"
          onClick={resetZoom}
          className="rounded border border-border bg-bg-elevated px-2 py-0.5 text-[10px] text-text-muted hover:border-accent hover:text-accent"
        >
          Reset zoom
        </button>
      </div>

      <div ref={containerRef} className="w-full overflow-hidden rounded-md" style={{ height }} />

      <div className="mt-2 flex flex-wrap justify-between gap-2 text-[10px] text-text-muted">
        <span className="inline-flex items-center gap-1.5">
          <span
            className="inline-block h-0.5 w-3 rounded"
            style={{ backgroundColor: METRICS[pair.left].color }}
          />
          Left: {axisCaption(pair.left)}
        </span>
        <span className="inline-flex items-center gap-1.5">
          <span
            className="inline-block h-0.5 w-3 rounded"
            style={{ backgroundColor: METRICS[pair.right].color }}
          />
          Right: {axisCaption(pair.right)}
        </span>
      </div>
    </div>
  );
}
