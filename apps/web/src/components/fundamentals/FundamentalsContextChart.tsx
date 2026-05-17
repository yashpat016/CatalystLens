'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  createChart,
  ColorType,
  type IChartApi,
  type ISeriesApi,
  type LineData,
  type UTCTimestamp,
} from 'lightweight-charts';
import { toNumber } from '@/lib/format';
import type { QuarterlyPeriod } from '@/types/fundamentals';

interface FundamentalsContextChartProps {
  periods: QuarterlyPeriod[];
  height?: number;
}

type SeriesKey = 'stock' | 'revenue' | 'fcf' | 'debt' | 'margin';

const SERIES_META: Record<
  SeriesKey,
  { label: string; color: string; scale: 'left' | 'debtFcf' | 'right'; dashed?: boolean }
> = {
  stock: { label: 'Stock price (indexed)', color: '#4f8cff', scale: 'left' },
  revenue: { label: 'Net revenue (indexed)', color: '#22c55e', scale: 'left' },
  fcf: { label: 'Free cash flow (indexed)', color: '#a78bfa', scale: 'debtFcf' },
  debt: { label: 'Total debt (indexed)', color: '#f59e0b', scale: 'debtFcf', dashed: true },
  margin: { label: 'Net margin %', color: '#e6e8ec', scale: 'right' },
};

const DEFAULT_VISIBLE: SeriesKey[] = ['stock', 'revenue', 'fcf', 'debt', 'margin'];

function periodToTime(period_end: string): UTCTimestamp {
  return Math.floor(new Date(`${period_end}T12:00:00Z`).getTime() / 1000) as UTCTimestamp;
}

function indexTo100(values: number[]): number[] {
  const base = values.find((v) => v > 0) ?? values[0] ?? 1;
  return values.map((v) => (v / base) * 100);
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

export function FundamentalsContextChart({
  periods,
  height = 360,
}: FundamentalsContextChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesMapRef = useRef<Partial<Record<SeriesKey, ISeriesApi<'Line'>>>>({});
  const [visible, setVisible] = useState<Set<SeriesKey>>(() => new Set(DEFAULT_VISIBLE));

  const seriesData = useMemo(() => {
    const stock = periods.map((p) => toNumber(p.quarter_end_price) ?? 0);
    const revenue = periods.map((p) => toNumber(p.revenue) ?? 0);
    const fcf = periods.map((p) => toNumber(p.free_cash_flow) ?? 0);
    const debt = periods.map((p) => toNumber(p.total_debt) ?? 0);
    const margin = periods.map((p) => toNumber(p.net_margin_pct) ?? 0);

    return {
      stock: buildLineData(periods, indexTo100(stock)),
      revenue: buildLineData(periods, indexTo100(revenue)),
      fcf: buildLineData(periods, indexTo100(fcf)),
      debt: buildLineData(periods, indexTo100(debt)),
      margin: buildLineData(periods, margin),
    };
  }, [periods]);

  const resetZoom = useCallback(() => {
    const chart = chartRef.current;
    if (!chart) return;
    chart.timeScale().fitContent();
    chart.priceScale('left').applyOptions({ autoScale: true });
    chart.priceScale('right').applyOptions({ autoScale: true });
    try {
      chart.priceScale('debtFcf').applyOptions({ autoScale: true });
    } catch {
      // Overlay scale absent if chart not fully initialized yet.
    }
  }, []);

  const toggleSeries = (key: SeriesKey) => {
    setVisible((prev) => {
      const next = new Set(prev);
      if (next.has(key)) {
        if (next.size === 1) return prev;
        next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });
  };

  useEffect(() => {
    if (!containerRef.current) return;

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
      rightPriceScale: {
        borderColor: '#1f2530',
        scaleMargins: { top: 0.12, bottom: 0.12 },
      },
      leftPriceScale: {
        visible: true,
        borderColor: '#1f2530',
        scaleMargins: { top: 0.12, bottom: 0.12 },
      },
      timeScale: {
        borderColor: '#1f2530',
        timeVisible: true,
        fixLeftEdge: false,
        fixRightEdge: false,
        minBarSpacing: 8,
        barSpacing: 28,
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

    const map: Partial<Record<SeriesKey, ISeriesApi<'Line'>>> = {};
    (Object.keys(SERIES_META) as SeriesKey[]).forEach((key) => {
      const meta = SERIES_META[key];
      map[key] = chart.addLineSeries({
        color: meta.color,
        lineWidth: 2,
        priceScaleId: meta.scale,
        lineStyle: meta.dashed ? 2 : 0,
        title: meta.label,
        visible: true,
        lastValueVisible: false,
        priceLineVisible: false,
      });
    });
    seriesMapRef.current = map;

    // FCF/debt series above register the overlay scale `debtFcf`.
    chart.priceScale('debtFcf').applyOptions({
      scaleMargins: { top: 0.15, bottom: 0.15 },
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
      seriesMapRef.current = {};
    };
  }, [height]);

  useEffect(() => {
    const map = seriesMapRef.current;
    (Object.keys(SERIES_META) as SeriesKey[]).forEach((key) => {
      const s = map[key];
      if (!s) return;
      s.setData(seriesData[key]);
      s.applyOptions({ visible: visible.has(key) });
    });
    resetZoom();
  }, [periods, seriesData, visible, resetZoom]);

  if (periods.length < 2) {
    return (
      <p className="text-sm text-text-muted">
        Need at least two quarters of fundamentals to show the context chart.
      </p>
    );
  }

  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <p className="text-xs text-text-muted">
          Drag to pan · scroll to zoom time · scroll on axis or pinch to zoom value scales
        </p>
        <button
          type="button"
          onClick={resetZoom}
          className="rounded-md border border-border bg-bg-elevated px-3 py-1 text-xs font-medium text-text hover:border-accent hover:text-accent"
        >
          Reset zoom
        </button>
      </div>

      <div
        ref={containerRef}
        role="img"
        aria-label="Indexed stock, revenue, free cash flow, and debt with net margin percent"
        className="w-full overflow-hidden rounded-lg border border-border bg-bg-surface"
        style={{ height }}
      />

      <div className="mt-3 flex flex-wrap gap-2">
        {(Object.keys(SERIES_META) as SeriesKey[]).map((key) => {
          const meta = SERIES_META[key];
          const on = visible.has(key);
          return (
            <button
              key={key}
              type="button"
              onClick={() => toggleSeries(key)}
              className={`inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1 text-xs transition ${
                on
                  ? 'border-border bg-bg-elevated text-text'
                  : 'border-transparent bg-transparent text-text-subtle line-through opacity-60'
              }`}
              aria-pressed={on}
            >
              <span
                className="inline-block h-0.5 w-4 rounded"
                style={{
                  backgroundColor: meta.color,
                  opacity: on ? 1 : 0.35,
                }}
              />
              {meta.label}
            </button>
          );
        })}
      </div>

      <p className="mt-2 text-xs text-text-subtle">
        Dollar metrics are indexed to 100 at the oldest quarter. FCF and debt use a separate
        left scale so they are not flattened against revenue. Click legend items to focus one or
        more series; double-click a price axis to reset that scale. Demo fixture data.
      </p>
    </div>
  );
}
