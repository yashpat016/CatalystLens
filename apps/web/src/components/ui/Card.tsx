import { type ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
  title?: string;
}

export function Card({ children, className = '', title }: CardProps) {
  return (
    <section
      className={`rounded-xl border border-border bg-bg-surface ${className}`.trim()}
    >
      {title ? (
        <header className="border-b border-border-subtle px-4 py-3">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-text-muted">
            {title}
          </h2>
        </header>
      ) : null}
      <div className="p-4">{children}</div>
    </section>
  );
}
