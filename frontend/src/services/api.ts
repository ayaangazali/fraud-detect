// src/services/api.ts
import axios from 'axios';
import {
  CustomerUploadResponse,
  BlacklistUploadResponse,
  ScreeningResponse,
  CustomerRow,
  BlacklistRow,
  MatchResult,
} from '../types';

const API_BASE_URL = '/api';

export const api = {
  // Upload customer file
  uploadCustomers: async (file: File): Promise<CustomerUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post<CustomerUploadResponse>(
      `${API_BASE_URL}/upload/customers`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    );
    return response.data;
  },

  // Upload blacklist file
  uploadBlacklist: async (file: File): Promise<BlacklistUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await axios.post<BlacklistUploadResponse>(
      `${API_BASE_URL}/upload/blacklist`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    );
    return response.data;
  },

  // Run screening
  runScreening: async (
    customers: CustomerRow[],
    blacklist: BlacklistRow[],
    threshold: number,
    includeAliases: boolean
  ): Promise<ScreeningResponse> => {
    const response = await axios.post<ScreeningResponse>(`${API_BASE_URL}/screen`, {
      customers,
      blacklist,
      threshold,
      includeAliases,
    });
    return response.data;
  },

  // Export to Excel
  exportToExcel: async (matches: MatchResult[]): Promise<Blob> => {
    const response = await axios.post(`${API_BASE_URL}/export`, 
      { matches },
      {
        responseType: 'blob',
      }
    );
    return response.data;
  },

  // NEW WORKFLOW APIS
  
  // Upload screening list (3rd Excel)
  uploadScreeningList: async (file: File): Promise<any> => {
    const text = await file.text();
    const response = await axios.post(`${API_BASE_URL}/upload/screening-list`, {
      csvData: text,
    });
    return response.data;
  },

  // Screen list against KAMCO database
  screenList: async (
    screeningList: any[],
    threshold: number,
    includeAliases: boolean
  ): Promise<any> => {
    const response = await axios.post(`${API_BASE_URL}/screen-list`, {
      screeningList,
      threshold,
      includeAliases,
    });
    return response.data;
  },

  // Flag a match
  flagCase: async (match: any, comments: string, flaggedBy?: string): Promise<any> => {
    const response = await axios.post(`${API_BASE_URL}/review/flag`, {
      match,
      comments,
      flagged_by: flaggedBy,
    });
    return response.data;
  },

  // Mark as safe
  markSafe: async (matchId: string, screeningName: string): Promise<any> => {
    const response = await axios.post(`${API_BASE_URL}/review/safe`, {
      match_id: matchId,
      screening_name: screeningName,
    });
    return response.data;
  },

  // Get flagged logbook
  getFlaggedLogbook: async (limit?: number, skip?: number): Promise<any> => {
    const response = await axios.get(`${API_BASE_URL}/review/flagged-logbook`, {
      params: { limit, skip },
    });
    return response.data;
  },

  // Get KAMCO clients count
  getKamcoClientsCount: async (): Promise<any> => {
    const response = await axios.get(`${API_BASE_URL}/kamco-clients`);
    return response.data;
  },

  // Export flagged cases to Excel
  exportFlaggedCases: async (): Promise<Blob> => {
    const response = await axios.get(`${API_BASE_URL}/review/export-flagged`, {
      responseType: 'blob',
    });
    return response.data;
  },

  // Generate PDF report
  generatePDF: async (reviewData: any): Promise<Blob> => {
    const response = await axios.post(`${API_BASE_URL}/review/generate-pdf`, reviewData, {
      responseType: 'blob',
    });
    return response.data;
  },
};
