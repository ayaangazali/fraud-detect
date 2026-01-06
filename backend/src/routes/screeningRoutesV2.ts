// src/routes/screeningRoutesV2.ts
import { Router, Request, Response } from 'express';
import * as ExcelJS from 'exceljs';
import { screeningServiceV2 } from '../services/screeningServiceV2';
import { ScreeningEntry, ScreeningListUploadResponse } from '../types';

const router = Router();

/**
 * POST /api/upload/screening-list
 * Upload screening list (Excel file with Change Log sheet) for comparison against KAMCO database
 */
router.post('/upload/screening-list', async (req: Request, res: Response) => {
  try {
    const { excelData } = req.body;

    if (!excelData) {
      return res.status(400).json({ error: 'Excel data is required' });
    }

    // Parse Excel data (base64)
    const buffer = Buffer.from(excelData, 'base64');
    const workbook = new ExcelJS.Workbook();
    await workbook.xlsx.load(buffer.buffer.slice(buffer.byteOffset, buffer.byteOffset + buffer.byteLength));

    // Get the "Change Log" sheet (2nd sheet)
    const changeLogSheet = workbook.getWorksheet('Change Log') || workbook.getWorksheet(2);
    
    if (!changeLogSheet) {
      return res.status(400).json({ error: 'Change Log sheet not found in Excel file' });
    }

    const rows: ScreeningEntry[] = [];
    const errors: any[] = [];

    // Read rows from Change Log sheet (skip header)
    changeLogSheet.eachRow((row, rowNumber) => {
      if (rowNumber === 1) return; // Skip header

      try {
        const entry: ScreeningEntry = {
          crm_reference: String(row.getCell(1).value || ''),
          wc1_ref: String(row.getCell(2).value || ''),
          crm_name: String(row.getCell(3).value || ''),
          primary_name: String(row.getCell(4).value || ''),
          match_score: String(row.getCell(5).value || '0'),
          match_strength: String(row.getCell(6).value || 'WEAK') as any,
          change_type: String(row.getCell(7).value || 'update') as any,
          change_field: String(row.getCell(8).value || ''),
          from_val: String(row.getCell(9).value || 'N/A'),
          to_val: String(row.getCell(10).value || ''),
          record_date: String(row.getCell(11).value || ''),
        };

        // Validate required fields
        if (entry.crm_name && entry.crm_name.length > 2) {
          rows.push(entry);
        }
      } catch (error: any) {
        errors.push({
          row: rowNumber,
          error: error.message,
        });
      }
    });

    const response: ScreeningListUploadResponse = {
      rows: rows,
      preview: rows.slice(0, 5),
      errors: errors,
      totalRows: changeLogSheet.rowCount - 1, // Exclude header
      validRows: rows.length,
    };

    console.log(`✅ Screening list uploaded: ${rows.length} valid entries from Change Log sheet`);

    res.json(response);
  } catch (error: any) {
    console.error('Error uploading screening list:', error);
    res.status(500).json({ error: error.message || 'Failed to upload screening list' });
  }
});

/**
 * POST /api/screen-list
 * Screen uploaded list against KAMCO database (3rd Excel vs 1st Excel)
 */
router.post('/screen-list', async (req: Request, res: Response) => {
  try {
    const { screeningList, threshold, includeAliases } = req.body;

    // Validation
    if (!screeningList || !Array.isArray(screeningList)) {
      return res.status(400).json({ error: 'Screening list array is required' });
    }

    if (screeningList.length === 0) {
      return res.status(400).json({ error: 'Screening list is empty' });
    }

    const thresholdValue = threshold || 70;
    const includeAliasesValue = includeAliases !== false;

    console.log(
      `🔍 Screening ${screeningList.length} entries against KAMCO database (threshold: ${thresholdValue}%)`
    );

    // Initialize service and screen
    await screeningServiceV2.initialize();
    const matches = await screeningServiceV2.screenAgainstKamco(screeningList, {
      threshold: thresholdValue,
      includeAliases: includeAliasesValue,
    });

    res.json({
      success: true,
      matches,
      totalScreeningEntries: screeningList.length,
      totalKamcoClients: screeningServiceV2.getKamcoClientsCount(),
      matchesFound: matches.length,
    });
  } catch (error: any) {
    console.error('Error screening list:', error);
    res.status(500).json({ error: error.message || 'Failed to screen list' });
  }
});

/**
 * GET /api/kamco-clients
 * Get KAMCO clients (optional - for admin viewing)
 */
router.get('/kamco-clients', async (req: Request, res: Response) => {
  try {
    await screeningServiceV2.initialize();
    
    const count = screeningServiceV2.getKamcoClientsCount();

    res.json({
      success: true,
      message: 'KAMCO clients database loaded',
      count,
    });
  } catch (error: any) {
    console.error('Error getting KAMCO clients:', error);
    res.status(500).json({ error: error.message || 'Failed to get KAMCO clients' });
  }
});

export default router;
