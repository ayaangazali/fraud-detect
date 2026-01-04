// src/utils/fileParser.ts
import XLSX from 'xlsx';
import Papa from 'papaparse';
import { CustomerRow, BlacklistRow } from '../types';

/**
 * Parse uploaded file (CSV or XLSX) to JSON
 */
export function parseFile(buffer: Buffer, filename: string): any[] {
  const ext = filename.toLowerCase().split('.').pop();

  if (ext === 'csv') {
    return parseCSV(buffer);
  } else if (ext === 'xlsx' || ext === 'xls') {
    return parseXLSX(buffer);
  } else {
    throw new Error('Unsupported file format. Please upload CSV or XLSX files.');
  }
}

function parseCSV(buffer: Buffer): any[] {
  const text = buffer.toString('utf-8');
  const result = Papa.parse(text, {
    header: true,
    skipEmptyLines: true,
    transformHeader: (header: string) => header.trim(),
  });

  if (result.errors.length > 0) {
    throw new Error(`CSV parsing error: ${result.errors[0].message}`);
  }

  return result.data;
}

function parseXLSX(buffer: Buffer): any[] {
  const workbook = XLSX.read(buffer, { type: 'buffer' });
  const sheetName = workbook.SheetNames[0];
  const sheet = workbook.Sheets[sheetName];
  const data = XLSX.utils.sheet_to_json(sheet, { defval: '' });
  
  return data;
}

/**
 * Validate required columns exist
 */
export function validateColumns(data: any[], requiredColumns: string[]): void {
  if (data.length === 0) {
    throw new Error('File is empty');
  }

  const firstRow = data[0];
  const columns = Object.keys(firstRow);
  const missing = requiredColumns.filter(col => !columns.includes(col));

  if (missing.length > 0) {
    throw new Error(`Missing required columns: ${missing.join(', ')}`);
  }
}
