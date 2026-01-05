// src/routes/screeningRoutesV2.ts
import { Router, Request, Response } from 'express';
import Papa from 'papaparse';
import { screeningServiceV2 } from '../services/screeningServiceV2';
import { ScreeningEntry, ScreeningListUploadResponse } from '../types';

const router = Router();

/**
 * POST /api/upload/screening-list
 * Upload screening list (3rd Excel) for comparison against KAMCO database
 */
router.post('/upload/screening-list', async (req: Request, res: Response) => {
  try {
    const { csvData } = req.body;

    if (!csvData) {
      return res.status(400).json({ error: 'CSV data is required' });
    }

    // Parse CSV
    const parseResult = Papa.parse<any>(csvData, {
      header: true,
      skipEmptyLines: true,
      transformHeader: (header) => header.trim().toLowerCase().replace(/\s+/g, '_'),
    });

    if (parseResult.errors.length > 0) {
      console.error('CSV parsing errors:', parseResult.errors);
    }

    const rows: ScreeningEntry[] = parseResult.data.map((row) => ({
      full_name: row.full_name || row.name || row.full_name_en || '',
      alias_alternate_names: row.alias_alternate_names || row.aliases || row.alternate_names || '',
      dob_or_reg_no: row.dob_or_reg_no || row.date_of_birth || row.reg_no || '',
      nationality_country: row.nationality_country || row.nationality || row.country || '',
      source: row.source || 'User Upload',
      effective_date: row.effective_date || new Date().toISOString().split('T')[0],
    }));

    // Filter valid rows
    const validRows = rows.filter((row) => row.full_name && row.full_name.length > 2);

    const response: ScreeningListUploadResponse = {
      rows: validRows,
      preview: validRows.slice(0, 5),
      errors: [],
      totalRows: parseResult.data.length,
      validRows: validRows.length,
    };

    console.log(`✅ Screening list uploaded: ${validRows.length} valid entries`);

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
