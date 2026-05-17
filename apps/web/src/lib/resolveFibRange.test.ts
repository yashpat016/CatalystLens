import { describe, expect, it } from 'vitest';
import { resolveFibRange } from '@/lib/fibonacci';

describe('resolveFibRange', () => {
  it('parses valid high and low', () => {
    expect(resolveFibRange('150.5', '120')).toEqual({ high: 150.5, low: 120 });
  });

  it('rejects when high <= low', () => {
    expect(resolveFibRange('100', '100')).toBeNull();
    expect(resolveFibRange('90', '100')).toBeNull();
  });

  it('rejects invalid numbers', () => {
    expect(resolveFibRange('', '10')).toBeNull();
    expect(resolveFibRange('abc', '10')).toBeNull();
  });
});
