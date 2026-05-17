export type ReportTime = 'bmo' | 'amc' | 'dmh' | 'unknown';

export interface QuarterlyPeriod {
  fiscal_year: number;
  fiscal_quarter: number;
  period_end: string;
  report_date: string | null;
  report_time: ReportTime;
  eps_actual: string | number | null;
  eps_estimate: string | number | null;
  eps_surprise_pct: string | number | null;
  beat: boolean | null;
  revenue: string | number | null;
  revenue_estimate: string | number | null;
  revenue_surprise_pct: string | number | null;
  gross_margin_pct: string | number | null;
  operating_margin_pct: string | number | null;
  net_margin_pct: string | number | null;
  quarter_end_price: string | number | null;
  free_cash_flow: string | number | null;
  total_debt: string | number | null;
}

export interface UpcomingEarnings {
  report_date: string;
  report_time: ReportTime;
  fiscal_year: number;
  fiscal_quarter: number;
  eps_estimate: string | number | null;
  revenue_estimate: string | number | null;
  analyst_count: number | null;
  days_until: number | null;
}

export interface FundamentalsResponse {
  ticker: string;
  company_name: string | null;
  currency: string;
  periods: QuarterlyPeriod[];
  upcoming_earnings: UpcomingEarnings | null;
}
