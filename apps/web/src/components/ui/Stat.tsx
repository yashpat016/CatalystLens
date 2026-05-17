import { type ReactNode } from 'react';

interface StatProps {
  label: string;
  value: ReactNode;
  hint?: ReactNode;
  className?: string;
}

export function Stat({ label, value, hint, className = '' }: StatProps) {
  return (
    <div className={`flex flex-col gap-0.5 ${className}`.trim()}>
      <div className="text-[10px] uppercase tracking-[0.2em] text-text-subtle">{label}</div>
      <div className="font-mono text-lg font-semibold text-text">{value}</div>
      {hint !== undefined && hint !== null ? (
        <div className="text-xs text-text-muted">{hint}</div>
      ) : null}
    </div>
  );
}
