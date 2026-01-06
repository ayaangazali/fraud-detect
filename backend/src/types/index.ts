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
  source: 'government' | 'regulator' | 'other' | 'REGULATOR';
  effective_date: string;
  blacklist_type?: 'regulator' | 'user'; // Track if from hardcoded regulator list or user upload
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
  blacklist_type: 'regulator' | 'user'; // Distinguish between regulator and user blacklist
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

// NEW TYPES FOR UPDATED WORKFLOW

export interface KamcoClient {
  customer_id: string;
  name: string;
  type: 'individual' | 'company';
  dob_or_reg_no: string;
  nationality_country: string;
  department: string;
  position: string;
  hire_date: string;
  status: 'active' | 'inactive';
}

export interface ScreeningEntry {
  crm_reference: string; // Customer reference from CRM
  wc1_ref: string; // World-Check reference
  crm_name: string; // Name in CRM
  primary_name: string; // Primary name (can be same as crm_name)
  match_score: string; // Match score as string (will be converted to number)
  match_strength: 'WEAK' | 'MEDIUM' | 'STRONG' | 'VERY_STRONG'; // Match strength
  change_type: 'new' | 'update' | 'delete'; // Type of change
  change_field: string; // Field that changed
  from_val: string; // Previous value (date or 'N/A')
  to_val: string; // New value (date)
  record_date: string; // Date of record
}

export interface ScreeningListUploadResponse {
  rows: ScreeningEntry[];
  preview: ScreeningEntry[];
  errors: any[];
  totalRows: number;
  validRows: number;
}

export interface FlaggedLogEntry {
  flagged_id: string;
  customer_id: string;
  customer_name: string;
  customer_type: string;
  customer_dob: string;
  customer_nationality: string;
  customer_department: string;
  customer_position: string;
  screening_name: string;
  screening_aliases: string;
  screening_source: string;
  similarity_score: number;
  match_type: string;
  match_reason: string;
  user_comments: string;
  flagged_date: string;
  flagged_by: string;
  screening_file_source: string;
}

export interface ReviewAction {
  type: 'flag' | 'safe' | 'skip';
  match: MatchResult;
  comments?: string;
}

export interface ReviewState {
  currentIndex: number;
  totalMatches: number;
  flaggedCount: number;
  safeCount: number;
  skippedCount: number;
  reviewedMatches: string[]; // Array of match IDs
}

export interface ExtendedMatchResult extends MatchResult {
  review_status: 'pending' | 'flagged' | 'safe' | 'skipped';
  kamco_client?: KamcoClient; // Embedded KAMCO client data
  screening_entry?: ScreeningEntry; // Embedded screening entry data
}

export interface FlagRequest {
  match: ExtendedMatchResult;
  comments: string;
  flagged_by?: string;
}

export interface SafeRequest {
  match_id: string;
  screening_name: string;
}

