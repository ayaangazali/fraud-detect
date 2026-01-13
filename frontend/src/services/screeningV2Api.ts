/**
 * Screening V2 API - Blacklist Upload Workflow
 * New workflow: Upload BLACKLIST CSV to screen against pre-loaded KAMCO entities
 */
import apiClient from './apiClient';

export interface BlacklistUploadResponse {
  success: boolean;
  upload_id: number;
  filename: string;
  entries_processed: number;
  matches_found: number;
  matches: ScreeningMatchDetail[];
  skipped_already_decided: number;
  re_reviews_flagged: number;
  threshold_used: number;
}

export interface ScreeningMatchDetail {
  match_id: number;
  kamco_entity: KamcoEntity;
  blacklist_entry: BlacklistEntry;
  overall_score: number;
  score_breakdown: ScoreBreakdown;
  risk_level: string;
  is_re_review: boolean;
  re_review_reason?: string;
}

export interface KamcoEntity {
  id: string;
  name_english: string;
  name_arabic?: string;
  civil_id?: string;
  nationality?: string;
  type: string;
  risk_rating?: string;
  status?: string;
}

export interface BlacklistEntry {
  reference_number: string;
  full_name_english: string;
  full_name_arabic?: string;
  civil_id?: string;
  nationality?: string;
  risk_level?: string;
  source?: string;
  raw_data?: Record<string, any>;
}

export interface ScoreBreakdown {
  name_english: number;
  name_arabic: number;
  id_number: number;
  nationality: number;
}

export interface DecisionRequest {
  match_id: number;
  status: 'FLAGGED' | 'CLEARED' | 'ESCALATED';
  notes?: string;
}

export interface DecisionResponse {
  success: boolean;
  decision_id: number;
  match_id: number;
  status: string;
  message: string;
}

export interface LogbookEntry {
  id: number;
  match_id: number;
  kamco_entity_id: string;
  match_score: number;
  decision_status: string;
  decision_date: string;
  decided_by: string;
  notes?: string;
  is_re_review: boolean;
  previous_status?: string;
}

export interface PendingMatch {
  match_id: number;
  upload_id: number;
  kamco_entity_id: string;
  match_score: number;
  score_breakdown: ScoreBreakdown;
  is_re_review: boolean;
  re_review_reason?: string;
  created_at: string;
}

export interface UploadHistory {
  id: number;
  filename: string;
  uploaded_by: string;
  uploaded_at: string;
  total_entries: number;
  matches_found: number;
  threshold_used: number;
  processed_at?: string;
}

/**
 * Upload blacklist CSV and screen against KAMCO entities
 */
export const uploadBlacklistCSV = async (
  file: File,
  threshold: number = 70
): Promise<BlacklistUploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('threshold', threshold.toString());

  const response = await apiClient.post<BlacklistUploadResponse>(
    '/screening/v2/upload-blacklist',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );

  return response.data;
};

/**
 * Make a decision on a screening match
 */
export const makeDecision = async (
  request: DecisionRequest
): Promise<DecisionResponse> => {
  const response = await apiClient.post<DecisionResponse>(
    '/screening/v2/decision',
    request
  );
  return response.data;
};

/**
 * Get decision logbook entries
 */
export const getLogbook = async (params?: {
  status_filter?: string;
  kamco_type?: string;
  start_date?: string;
  end_date?: string;
  limit?: number;
  offset?: number;
}): Promise<{
  success: boolean;
  entries: LogbookEntry[];
  total: number;
  limit: number;
  offset: number;
}> => {
  const response = await apiClient.get('/screening/v2/logbook', { params });
  return response.data;
};

/**
 * Get pending matches that need decisions
 */
export const getPendingMatches = async (params?: {
  upload_id?: number;
  min_score?: number;
  include_re_reviews?: boolean;
  limit?: number;
}): Promise<{
  success: boolean;
  matches: PendingMatch[];
  count: number;
}> => {
  const response = await apiClient.get('/screening/v2/pending-matches', {
    params,
  });
  return response.data;
};

/**
 * Get blacklist upload history
 */
export const getUploadHistory = async (
  limit: number = 20
): Promise<{
  success: boolean;
  uploads: UploadHistory[];
  count: number;
}> => {
  const response = await apiClient.get('/screening/v2/uploads', {
    params: { limit },
  });
  return response.data;
};

/**
 * Get pre-loaded KAMCO entities
 */
export const getKamcoEntities = async (params?: {
  entity_type?: string;
  search?: string;
  limit?: number;
}): Promise<{
  success: boolean;
  source: string;
  entities: KamcoEntity[];
  count: number;
}> => {
  const response = await apiClient.get('/screening/v2/kamco-entities', {
    params,
  });
  return response.data;
};

export default {
  uploadBlacklistCSV,
  makeDecision,
  getLogbook,
  getPendingMatches,
  getUploadHistory,
  getKamcoEntities,
};
