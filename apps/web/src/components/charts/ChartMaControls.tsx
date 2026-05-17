'use client';

import type { MaType } from '@/lib/movingAverage';
import type { Timeframe } from '@/types/ticker';

export interface MaConfig {
  enabled: boolean;
  type: MaType;
  period: number;
  maValues?: (number | null)[];
}

interface ChartMaControlsProps {
  config: MaConfig;
  onChange: (config: MaConfig) => void;
  timeframe: Timeframe;
}

export function ChartMaControls({ config, onChange, timeframe }: ChartMaControlsProps) {
  return (
    <div className="mb-2 flex flex-wrap items-center gap-3 text-xs text-text-muted">
      <label className="flex cursor-pointer items-center gap-2">
        <input
          type="checkbox"
          checked={config.enabled}
          onChange={(e) => onChange({ ...config, enabled: e.target.checked })}
          className="rounded border-border"
        />
        Moving average
      </label>
      {config.enabled ? (
        <>
          <select
            value={config.type}
            onChange={(e) => onChange({ ...config, type: e.target.value as MaType })}
            className="rounded border border-border bg-bg-elevated px-2 py-1 text-xs text-text"
          >
            <option value="sma">Simple (SMA)</option>
            <option value="wma">Weighted (WMA)</option>
          </select>
          <label className="flex items-center gap-1.5">
            <span>Period</span>
            <input
              type="number"
              min={2}
              max={500}
              value={config.period}
              onChange={(e) =>
                onChange({
                  ...config,
                  period: Math.max(2, Number.parseInt(e.target.value, 10) || 2),
                })
              }
              className="w-16 rounded border border-border bg-bg-elevated px-2 py-1 font-mono text-xs text-text"
            />
            <span className="text-text-subtle">bars ({timeframe})</span>
          </label>
        </>
      ) : null}
    </div>
  );
}
