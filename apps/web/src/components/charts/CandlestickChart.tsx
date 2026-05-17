'use client';

import { useEffect, useRef } from 'react';
import {
  createChart,
  ColorType,
  type IChartApi,
  type ISeriesApi,
  type CandlestickData,
  type LineData,
  type UTCTimestamp,
} from 'lightweight-charts';
import { toUnixSeconds } from '@/lib/time';
import { toNumber } from '@/lib/format';
import type { Bar } from '@/types/ticker';

interface CandlestickChartProps {
  bars: Bar[];
  vwap?: (number | null)[];
  height?: number;
}

function barsToCandles(bars: Bar[]): CandlestickData<UTCTimestamp>[] {
  const candles: CandlestickData<UTCTimestamp>[] = [];
  for (const b of bars) {
    const open = toNumber(b.open);
    const high = toNumber(b.high);
    const low = toNumber(b.low);
    const close = toNumber(b.close);
    if (open === null || high === null || low === null || close === null) continue;
    candles.push({
      time: toUnixSeconds(b.timestamp) as UTCTimestamp,
      open,
      high,
      low,
      close,
    });
  }
  return candles;
}

function buildVwapSeries(bars: Bar[], vwap?: (number | null)[]): LineData[] {
  if (!vwap || vwap.length === 0) return [];
  const out: LineData[] = [];
  const n = Math.min(bars.length, vwap.length);
  for (let i = 0; i < n; i++) {
    const v = vwap[i];
    if (v === null || v === undefined || !Number.isFinite(v)) continue;
    out.push({
      time: toUnixSeconds(bars[i].timestamp) as UTCTimestamp,
      value: v,
    });
  }
  return out;
}

export function CandlestickChart({ bars, vwap, height = 420 }: CandlestickChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const vwapSeriesRef = useRef<ISeriesApi<'Line'> | null>(null);

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
      crosshair: { mode: 1 },
    });
    chartRef.current = chart;

    candleSeriesRef.current = chart.addCandlestickSeries({
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderUpColor: '#22c55e',
      borderDownColor: '#ef4444',
      wickUpColor: '#22c55e',
      wickDownColor: '#ef4444',
    });

    vwapSeriesRef.current = chart.addLineSeries({
      color: '#4f8cff',
      lineWidth: 2,
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
      candleSeriesRef.current = null;
      vwapSeriesRef.current = null;
    };
  }, [height]);

  useEffect(() => {
    if (!candleSeriesRef.current) return;
    candleSeriesRef.current.setData(barsToCandles(bars));
    if (vwapSeriesRef.current) {
      vwapSeriesRef.current.setData(buildVwapSeries(bars, vwap));
    }
    chartRef.current?.timeScale().fitContent();
  }, [bars, vwap]);

  return (
    <div
      ref={containerRef}
      role="img"
      aria-label="Price candlestick chart with VWAP overlay"
      className="w-full overflow-hidden rounded-lg border border-border bg-bg-surface"
      style={{ height }}
    />
  );
}
