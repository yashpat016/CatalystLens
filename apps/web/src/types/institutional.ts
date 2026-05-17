export type HolderActivity = 'new' | 'increased' | 'decreased' | 'closed' | 'unchanged';
export type AggregateFlow = 'net_buying' | 'net_selling' | 'mixed' | 'unchanged';

export interface InstitutionalHolder {
  manager_name: string;
  cik: string | null;
  shares: number;
  market_value_usd: string;
  shares_change_qoq: number | null;
  value_change_usd: string | null;
  activity: HolderActivity;
  implied_position_price_usd: string | null;
  implied_flow_price_usd: string | null;
  pct_of_outstanding: string | null;
  filing_date: string | null;
}

export interface InstitutionalQuarterSummary {
  period_end: string;
  filed_through: string;
  holder_count: number;
  total_shares: number;
  total_market_value_usd: string;
  net_shares_change_qoq: number | null;
  net_value_change_usd: string | null;
  aggregate_flow: AggregateFlow;
}

export interface InstitutionalResponse {
  ticker: string;
  company_name: string | null;
  source: string;
  data_as_of: string;
  filed_through: string;
  data_notes: string[];
  aggregate_flow: AggregateFlow;
  net_shares_change_qoq: number | null;
  net_value_change_usd: string | null;
  holders: InstitutionalHolder[];
  quarter_history: InstitutionalQuarterSummary[];
}
