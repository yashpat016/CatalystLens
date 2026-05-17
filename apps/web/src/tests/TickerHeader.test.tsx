import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { TickerHeader } from '@/components/ticker/TickerHeader';
import type { TickerSummary } from '@/types/ticker';

function makeSummary(overrides: Partial<TickerSummary> = {}): TickerSummary {
  return {
    ticker: 'AAPL',
    company_name: 'Apple Inc.',
    exchange: 'NASDAQ',
    price: '185.12',
    change_pct: '1.24',
    volume: 42_100_000,
    relative_volume: null,
    session: 'regular',
    last_bar_time: '2026-05-13T19:59:00Z',
    latest_event: null,
    ...overrides,
  };
}

describe('TickerHeader', () => {
  it('renders ticker, company, exchange', () => {
    render(<TickerHeader summary={makeSummary()} />);
    expect(screen.getByText('AAPL')).toBeInTheDocument();
    expect(screen.getByText('Apple Inc.')).toBeInTheDocument();
    expect(screen.getByText('NASDAQ')).toBeInTheDocument();
  });

  it('renders price formatted with dollar sign', () => {
    render(<TickerHeader summary={makeSummary({ price: '185.12' })} />);
    expect(screen.getByText('$185.12')).toBeInTheDocument();
  });

  it('renders positive change with leading +', () => {
    render(<TickerHeader summary={makeSummary({ change_pct: '1.24' })} />);
    expect(screen.getByText('+1.24%')).toBeInTheDocument();
  });

  it('renders negative change with leading -', () => {
    render(<TickerHeader summary={makeSummary({ change_pct: '-2.41' })} />);
    expect(screen.getByText('-2.41%')).toBeInTheDocument();
  });

  it('renders -- placeholder when price is null', () => {
    render(<TickerHeader summary={makeSummary({ price: null })} />);
    const stats = screen.getAllByText('--');
    expect(stats.length).toBeGreaterThan(0);
  });

  it('renders session badge for each session', () => {
    const { rerender } = render(<TickerHeader summary={makeSummary({ session: 'regular' })} />);
    expect(screen.getByText('Regular')).toBeInTheDocument();

    rerender(<TickerHeader summary={makeSummary({ session: 'premarket' })} />);
    expect(screen.getByText('Premarket')).toBeInTheDocument();

    rerender(<TickerHeader summary={makeSummary({ session: 'afterhours' })} />);
    expect(screen.getByText('After Hours')).toBeInTheDocument();

    rerender(<TickerHeader summary={makeSummary({ session: 'closed' })} />);
    expect(screen.getByText('Closed')).toBeInTheDocument();
  });

  it('formats large volumes with M/B suffix', () => {
    render(<TickerHeader summary={makeSummary({ volume: 42_100_000 })} />);
    expect(screen.getByText('42.10M')).toBeInTheDocument();
  });

  it('omits company name section when name is null', () => {
    render(<TickerHeader summary={makeSummary({ company_name: null, exchange: null })} />);
    expect(screen.queryByText('Apple Inc.')).toBeNull();
  });
});
