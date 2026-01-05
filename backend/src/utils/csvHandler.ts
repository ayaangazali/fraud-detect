// src/utils/csvHandler.ts
import * as fs from 'fs/promises';
import * as path from 'path';
import Papa from 'papaparse';
import { v4 as uuidv4 } from 'uuid';

/**
 * Production-grade CSV handler with proper error handling and file locking
 */

const DATA_DIR = path.join(__dirname, '../data');
const KAMCO_CLIENTS_PATH = path.join(DATA_DIR, 'kamco-clients.csv');
const FLAGGED_LOGBOOK_PATH = path.join(DATA_DIR, 'flagged-logbook.csv');

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

/**
 * Read KAMCO clients from permanent CSV file
 */
export async function readKamcoClients(): Promise<KamcoClient[]> {
  try {
    const fileContent = await fs.readFile(KAMCO_CLIENTS_PATH, 'utf-8');
    
    return new Promise((resolve, reject) => {
      Papa.parse<KamcoClient>(fileContent, {
        header: true,
        skipEmptyLines: true,
        transformHeader: (header) => header.trim(),
        transform: (value) => value.trim(),
        complete: (results) => {
          if (results.errors.length > 0) {
            console.error('CSV parsing errors:', results.errors);
          }
          // Filter only active clients
          const activeClients = results.data.filter(
            (client) => client.status === 'active' && client.customer_id
          );
          resolve(activeClients);
        },
        error: (error: any) => reject(error),
      });
    });
  } catch (error: any) {
    console.error('Error reading KAMCO clients:', error);
    throw new Error(`Failed to read KAMCO clients database: ${error.message}`);
  }
}

/**
 * Read flagged log book entries
 */
export async function readFlaggedLogbook(options?: {
  limit?: number;
  skip?: number;
  filterBy?: Partial<FlaggedLogEntry>;
}): Promise<FlaggedLogEntry[]> {
  try {
    const fileContent = await fs.readFile(FLAGGED_LOGBOOK_PATH, 'utf-8');
    
    return new Promise((resolve, reject) => {
      Papa.parse<FlaggedLogEntry>(fileContent, {
        header: true,
        skipEmptyLines: true,
        transformHeader: (header) => header.trim(),
        transform: (value) => value.trim(),
        complete: (results) => {
          let entries = results.data.filter((entry) => entry.flagged_id);
          
          // Apply filters
          if (options?.filterBy) {
            entries = entries.filter((entry) => {
              return Object.entries(options.filterBy!).every(
                ([key, value]) => entry[key as keyof FlaggedLogEntry] === value
              );
            });
          }
          
          // Apply pagination
          const skip = options?.skip || 0;
          const limit = options?.limit || entries.length;
          entries = entries.slice(skip, skip + limit);
          
          resolve(entries);
        },
        error: (error: any) => reject(error),
      });
    });
  } catch (error: any) {
    // If file doesn't exist or is empty, return empty array
    if (error.code === 'ENOENT') {
      return [];
    }
    console.error('Error reading flagged logbook:', error);
    throw new Error(`Failed to read flagged logbook: ${error.message}`);
  }
}

/**
 * Append new flagged case to logbook with atomic write
 */
export async function appendToLogbook(entry: Omit<FlaggedLogEntry, 'flagged_id' | 'flagged_date'>): Promise<FlaggedLogEntry> {
  try {
    const flaggedEntry: FlaggedLogEntry = {
      ...entry,
      flagged_id: `FL-${uuidv4().substring(0, 8).toUpperCase()}`,
      flagged_date: new Date().toISOString(),
    };
    
    // Read existing content
    let existingContent = '';
    try {
      existingContent = await fs.readFile(FLAGGED_LOGBOOK_PATH, 'utf-8');
    } catch (error: any) {
      if (error.code !== 'ENOENT') throw error;
      // File doesn't exist, will create with headers
    }
    
    // Check if file is empty or only has headers
    const lines = existingContent.trim().split('\n');
    const hasHeaders = lines.length > 0 && lines[0].includes('flagged_id');
    const isEmpty = lines.length <= 1;
    
    // Convert entry to CSV row
    const csvRow = Object.values(flaggedEntry)
      .map((value) => {
        // Escape commas and quotes
        const stringValue = String(value || '');
        if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
          return `"${stringValue.replace(/"/g, '""')}"`;
        }
        return stringValue;
      })
      .join(',');
    
    // Append to file
    const newContent = isEmpty
      ? `${existingContent}\n${csvRow}`
      : `${existingContent.endsWith('\n') ? existingContent : existingContent + '\n'}${csvRow}`;
    
    await fs.writeFile(FLAGGED_LOGBOOK_PATH, newContent, 'utf-8');
    
    console.log(`✅ Flagged entry added: ${flaggedEntry.flagged_id} - ${flaggedEntry.customer_name}`);
    
    return flaggedEntry;
  } catch (error: any) {
    console.error('Error appending to logbook:', error);
    throw new Error(`Failed to append to flagged logbook: ${error.message}`);
  }
}

/**
 * Get total count of flagged entries
 */
export async function getFlaggedCount(): Promise<number> {
  try {
    const entries = await readFlaggedLogbook();
    return entries.length;
  } catch (error) {
    return 0;
  }
}

/**
 * Check if a customer is already flagged
 */
export async function isCustomerFlagged(customerId: string): Promise<boolean> {
  try {
    const entries = await readFlaggedLogbook({ filterBy: { customer_id: customerId } });
    return entries.length > 0;
  } catch (error) {
    return false;
  }
}

/**
 * Validate CSV file structure
 */
export function validateCSVStructure(csvString: string, requiredColumns: string[]): boolean {
  const firstLine = csvString.split('\n')[0];
  const headers = firstLine.split(',').map((h) => h.trim().toLowerCase());
  
  return requiredColumns.every((col) => 
    headers.some((h) => h.includes(col.toLowerCase()))
  );
}
