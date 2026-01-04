// src/types/index.ts
export interface CustomerRow {
  customer_id: string;
  type: 'individual' | 'corporate';
  full_name_en: string;
  date_of_birth?: string;
  company_reg_no?: string;
  nationality_country: string;
}

export interface CustomerValidationError {
  row: number;
  field: string;
  message: string;
}

export interface CustomerUploadResponse {
  rows: CustomerRow[];
  preview: CustomerRow[];
  errors: CustomerValidationError[];
  totalRows: number;
  validRows: number;
}

export interface BlacklistRow {
  full_name: string;
  alias_alternate_names?: string;
  source: 'government' | 'regulator' | 'other' | 'POLICE';
  effective_date: string;
  blacklist_type?: 'police' | 'user'; // Track if from hardcoded police list or user upload
}

export interface BlacklistValidationError {
  row: number;
  field: string;
  message: string;
}

export interface BlacklistUploadResponse {
  rows: BlacklistRow[];
  preview: BlacklistRow[];
  errors: BlacklistValidationError[];
  totalRows: number;
  validRows: number;
}

export interface ScreeningRequest {
  customers: CustomerRow[];
  blacklist: BlacklistRow[];
  threshold: number; // 0-100
  includeAliases: boolean;
}

export interface MatchResult {
  customer_id: string;
  customer_name: string;
  customer_type: 'individual' | 'corporate';
  dob_or_reg_no: string;
  nationality_country: string;
  matched_blacklist_name: string;
  matched_alias: string | null;
  source: string;
  effective_date: string;
  similarity_score: number;
  blacklist_type: 'police' | 'user'; // Distinguish between police and user blacklist
  match_type: 'direct' | 'alias' | 'fuzzy'; // How the match was found
  match_reason: string; // Human-readable explanation
  matched_field: string; // Which field matched (name, alias)
  score_breakdown: {
    name_similarity: number;
    alias_similarity: number;
    best_match: string;
  };
}

export interface ScreeningResponse {
  matches: MatchResult[];
  totalCustomers: number;
  totalBlacklist: number;
  matchesFound: number;
  processingTime: number;
}
