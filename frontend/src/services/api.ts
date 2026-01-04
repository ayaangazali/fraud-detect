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
};
