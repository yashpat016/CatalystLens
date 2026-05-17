'use client';

import { useEffect, useRef } from 'react';
import {
  createChart,
  ColorType,
  type IChartApi,
  type ISeriesApi,
  type HistogramData,
  type UTCTimestamp,
} from 'lightweight-charts';
import { toUnixSeconds } from '@/lib/time';
import { toNumber } from '@/lib/format';
import type { Bar } from '@/types/ticker';

interface VolumeBarsProps {
  bars: Bar[];
  height?: number;
}

function barsToVolume(bars: Bar[]): HistogramData[] {
  return bars.map((b) => {
    const open = toNumber(b.open) ?? 0;
    const close = toNumber(b.close) ?? 0;
    return {
      time: toUnixSeconds(b.timestamp) as UTCTimestamp,
      value: b.volume,
      color: close >= open ? '#22c55e88' : '#ef444488',
    };
  });
}

export function VolumeBars({ bars, height = 140 }: VolumeBarsProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<'Histogram'> | null>(null);

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
      rightPriceScale: { borderColor: '#1f2530' },
      timeScale: { borderColor: '#1f2530', timeVisible: true, secondsVisible: false },
    });
    chartRef.current = chart;

    seriesRef.current = chart.addHistogramSeries({
      priceFormat: { type: 'volume' },
      priceLineVisible: false,
      lastValueVisible: false,
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
      seriesRef.current = null;
    };
  }, [height]);

  useEffect(() => {
    if (!seriesRef.current) return;
    seriesRef.current.setData(barsToVolume(bars));
    chartRef.current?.timeScale().fitContent();
  }, [bars]);

  return (
    <div
      ref={containerRef}
      role="img"
      aria-label="Volume histogram"
      className="w-full overflow-hidden rounded-lg border border-border bg-bg-surface"
      style={{ height }}
    />
  );
}
