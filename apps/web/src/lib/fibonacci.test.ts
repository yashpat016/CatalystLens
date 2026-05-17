import { describe, expect, it } from 'vitest';
import { fibRetracementLevels } from './fibonacci';

describe('fibRetracementLevels', () => {
  it('returns empty when high <= low', () => {
    expect(fibRetracementLevels(100, 100)).toEqual([]);
    expect(fibRetracementLevels(90, 100)).toEqual([]);
  });

  it('places 0% at high and 100% at low', () => {
    const levels = fibRetracementLevels(110, 100);
    expect(levels[0].price).toBe(110);
    expect(levels[levels.length - 1].price).toBe(100);
  });

  it('computes 50% midpoint', () => {
    const levels = fibRetracementLevels(120, 100);
    const mid = levels.find((l) => l.label === '50.0%');
    expect(mid?.price).toBe(110);
  });
});
