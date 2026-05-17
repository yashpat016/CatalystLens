export type InsiderTransactionType = 'buy' | 'sell' | 'award' | 'gift';

export interface InsiderTransaction {
  transaction_date: string;
  filing_date: string;
  insider_name: string;
  role: string;
  transaction_type: InsiderTransactionType;
  shares: number;
  price_usd: string | number | null;
  value_usd: string | number | null;
  shares_owned_after: number | null;
}

export interface InsiderResponse {
  ticker: string;
  company_name: string | null;
  source: string;
  data_as_of: string;
  data_notes: string[];
  transactions: InsiderTransaction[];
}
