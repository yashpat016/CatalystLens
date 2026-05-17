'use client';

import { useEffect, useRef } from 'react';
import {
  ColorType,
  createChart,
  type IChartApi,
  type ISeriesApi,
  type LogicalRange,
} from 'lightweight-charts';
import {
  barsToCandles,
  barsToVolume,
  buildMaSeries,
  buildVwapSeries,
  CHART_GRID,
  CHART_LAYOUT,
} from '@/lib/chartSeries';
import type { MaConfig } from '@/components/charts/ChartMaControls';
import { fibRetracementLevels, type FibRange } from '@/lib/fibonacci';
import { DEFAULT_VISIBLE_BARS } from '@/lib/chartLimits';
import type { Bar, Timeframe } from '@/types/ticker';
import type { IPriceLine } from 'lightweight-charts';

interface LinkedPriceVolumeChartsProps {
  bars: Bar[];
  timeframe: Timeframe;
  vwap?: (number | null)[];
  fibRange?: FibRange | null;
  maConfig?: MaConfig;
  priceHeight?: number;
  volumeHeight?: number;
}

function syncVisibleRange(source: IChartApi, target: IChartApi, guard: { active: boolean }) {
  source.timeScale().subscribeVisibleLogicalRangeChange((range: LogicalRange | null) => {
    if (guard.active || range === null) return;
    guard.active = true;
    target.timeScale().setVisibleLogicalRange(range);
    guard.active = false;
  });
}

function applyDefaultVisibleRange(chart: IChartApi, barCount: number, visibleBars: number) {
  if (barCount === 0) return;
  const vis = Math.min(barCount, visibleBars);
  if (barCount > vis) {
    chart.timeScale().setVisibleLogicalRange({ from: barCount - vis, to: barCount - 1 });
  } else {
    chart.timeScale().fitContent();
  }
}

const FIB_COLORS = ['#f59e0b', '#eab308', '#84cc16', '#22c55e', '#14b8a6', '#38bdf8', '#a78bfa'];

export function LinkedPriceVolumeCharts({
  bars,
  timeframe,
  vwap,
  fibRange = null,
  maConfig,
  priceHeight = 420,
  volumeHeight = 140,
}: LinkedPriceVolumeChartsProps) {
  const priceContainerRef = useRef<HTMLDivElement | null>(null);
  const volumeContainerRef = useRef<HTMLDivElement | null>(null);
  const priceChartRef = useRef<IChartApi | null>(null);
  const volumeChartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const vwapSeriesRef = useRef<ISeriesApi<'Line'> | null>(null);
  const maSeriesRef = useRef<ISeriesApi<'Line'> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null);
  const fibLinesRef = useRef<IPriceLine[]>([]);
  const barsLenRef = useRef(0);

  useEffect(() => {
    if (!priceContainerRef.current || !volumeContainerRef.current) return;

    const guard = { active: false };
    const showSeconds = timeframe === '1m' || timeframe === '5m';

    const priceChart = createChart(priceContainerRef.current, {
      width: priceContainerRef.current.clientWidth,
      height: priceHeight,
      layout: {
        background: { type: ColorType.Solid, color: CHART_LAYOUT.background.color },
        textColor: CHART_LAYOUT.textColor,
        fontSize: CHART_LAYOUT.fontSize,
      },
      grid: CHART_GRID,
      rightPriceScale: { borderColor: '#1f2530', autoScale: true },
      timeScale: {
        borderColor: '#1f2530',
        visible: false,
        timeVisible: false,
        secondsVisible: showSeconds,
      },
      crosshair: { mode: 1 },
    });

    const volumeChart = createChart(volumeContainerRef.current, {
      width: volumeContainerRef.current.clientWidth,
      height: volumeHeight,
      layout: {
        background: { type: ColorType.Solid, color: CHART_LAYOUT.background.color },
        textColor: CHART_LAYOUT.textColor,
        fontSize: CHART_LAYOUT.fontSize,
      },
      grid: CHART_GRID,
      rightPriceScale: { borderColor: '#1f2530', autoScale: true },
      timeScale: {
        borderColor: '#1f2530',
        timeVisible: true,
        secondsVisible: showSeconds,
      },
      crosshair: { mode: 1 },
    });

    priceChartRef.current = priceChart;
    volumeChartRef.current = volumeChart;

    candleSeriesRef.current = priceChart.addCandlestickSeries({
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderUpColor: '#22c55e',
      borderDownColor: '#ef4444',
      wickUpColor: '#22c55e',
      wickDownColor: '#ef4444',
    });

    vwapSeriesRef.current = priceChart.addLineSeries({
      color: '#4f8cff',
      lineWidth: 2,
      priceLineVisible: false,
      lastValueVisible: false,
    });

    maSeriesRef.current = priceChart.addLineSeries({
      color: '#f59e0b',
      lineWidth: 2,
      priceLineVisible: false,
      lastValueVisible: true,
      title: 'MA',
    });

    volumeSeriesRef.current = volumeChart.addHistogramSeries({
      priceFormat: { type: 'volume' },
      priceLineVisible: false,
      lastValueVisible: false,
    });

    syncVisibleRange(priceChart, volumeChart, guard);
    syncVisibleRange(volumeChart, priceChart, guard);

    const onResize = () => {
      const w = priceContainerRef.current?.clientWidth ?? 0;
      if (w > 0) {
        priceChart.applyOptions({ width: w });
        volumeChart.applyOptions({ width: w });
      }
    };
    window.addEventListener('resize', onResize);

    return () => {
      window.removeEventListener('resize', onResize);
      priceChart.remove();
      volumeChart.remove();
      priceChartRef.current = null;
      volumeChartRef.current = null;
      candleSeriesRef.current = null;
      vwapSeriesRef.current = null;
      maSeriesRef.current = null;
      volumeSeriesRef.current = null;
      fibLinesRef.current = [];
    };
  }, [priceHeight, volumeHeight, timeframe]);

  useEffect(() => {
    if (!candleSeriesRef.current || !volumeSeriesRef.current) return;

    candleSeriesRef.current.setData(barsToCandles(bars));
    if (vwapSeriesRef.current) {
      vwapSeriesRef.current.setData(buildVwapSeries(bars, vwap));
    }
    volumeSeriesRef.current.setData(barsToVolume(bars));

    const visible = DEFAULT_VISIBLE_BARS[timeframe];
    if (bars.length !== barsLenRef.current) {
      barsLenRef.current = bars.length;
      if (priceChartRef.current && volumeChartRef.current) {
        applyDefaultVisibleRange(priceChartRef.current, bars.length, visible);
        applyDefaultVisibleRange(volumeChartRef.current, bars.length, visible);
      }
    }
  }, [bars, vwap, timeframe]);

  useEffect(() => {
    if (!maSeriesRef.current) return;
    if (!maConfig?.enabled || !maConfig.maValues?.length) {
      maSeriesRef.current.setData([]);
      return;
    }
    maSeriesRef.current.applyOptions({
      title: `${maConfig.type.toUpperCase()}(${maConfig.period})`,
    });
    maSeriesRef.current.setData(buildMaSeries(bars, maConfig.maValues));
  }, [bars, maConfig]);

  useEffect(() => {
    if (!candleSeriesRef.current) return;

    for (const line of fibLinesRef.current) {
      candleSeriesRef.current.removePriceLine(line);
    }
    fibLinesRef.current = [];

    if (fibRange) {
      const levels = fibRetracementLevels(fibRange.high, fibRange.low);
      levels.forEach((level, i) => {
        const pl = candleSeriesRef.current!.createPriceLine({
          price: level.price,
          color: FIB_COLORS[i % FIB_COLORS.length],
          lineWidth: 1,
          lineStyle: 2,
          axisLabelVisible: true,
          title: level.label,
        });
        fibLinesRef.current.push(pl);
      });
    }
  }, [fibRange]);

  return (
    <div className="flex w-full flex-col gap-1" aria-label="Linked price and volume charts">
      <div
        ref={priceContainerRef}
        className="w-full overflow-hidden rounded-t-lg border border-b-0 border-border bg-bg-surface"
        style={{ height: priceHeight }}
      />
      <div
        ref={volumeContainerRef}
        className="w-full overflow-hidden rounded-b-lg border border-border bg-bg-surface"
        style={{ height: volumeHeight }}
      />
    </div>
  );
}
