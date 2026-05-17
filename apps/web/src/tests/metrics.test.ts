import { describe, it, expect } from 'vitest';
import { rollingVwap } from '@/lib/metrics';
import type { Bar } from '@/types/ticker';

function bar(overrides: Partial<Bar> = {}): Bar {
  return {
    timestamp: '2026-05-13T13:30:00Z',
    open: 100,
    high: 101,
    low: 99,
    close: 100.5,
    volume: 1000,
    session: 'regular',
    ...overrides,
  };
}

describe('rollingVwap', () => {
  it('returns empty array for empty input', () => {
    expect(rollingVwap([])).toEqual([]);
  });

  it('matches running mean for constant-price bars', () => {
    const bars = [
      bar({ high: 100, low: 100, close: 100, volume: 1000 }),
      bar({ high: 100, low: 100, close: 100, volume: 1000 }),
      bar({ high: 100, low: 100, close: 100, volume: 1000 }),
    ];
    expect(rollingVwap(bars, { resetOn: null })).toEqual([100, 100, 100]);
  });

  it('weights by volume', () => {
    const bars = [
      bar({ high: 10, low: 10, close: 10, volume: 100 }),
      bar({ high: 20, low: 20, close: 20, volume: 300 }),
    ];
    const out = rollingVwap(bars, { resetOn: null });
    // (10*100 + 20*300) / 400 = 17.5
    expect(out[1]).toBeCloseTo(17.5, 4);
  });

  it('resets at session boundary', () => {
    const bars = [
      bar({ session: 'premarket', high: 100, low: 100, close: 100, volume: 100 }),
      bar({ session: 'premarket', high: 100, low: 100, close: 100, volume: 100 }),
      bar({ session: 'regular', high: 200, low: 200, close: 200, volume: 100 }),
    ];
    const out = rollingVwap(bars, { resetOn: 'session' });
    expect(out[2]).toBe(200);
  });

  it('emits null until first positive-volume bar', () => {
    const bars = [bar({ volume: 0 }), bar({ volume: 1000 })];
    const out = rollingVwap(bars, { resetOn: null });
    expect(out[0]).toBeNull();
    expect(out[1]).not.toBeNull();
  });
});
