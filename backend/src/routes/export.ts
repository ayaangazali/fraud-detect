// src/routes/export.ts
import { Router, Request, Response } from 'express';
import { generateExcelReport } from '../utils/excelExporter';
import { MatchResult } from '../types';

const router = Router();

/**
 * POST /api/export
 * Generate Excel file from screening results
 */
router.post('/export', async (req: Request, res: Response) => {
  try {
    const { matches }: { matches: MatchResult[] } = req.body;

    if (!matches || !Array.isArray(matches)) {
      return res.status(400).json({ error: 'matches array is required' });
    }

    // Generate Excel file
    const buffer = await generateExcelReport(matches);

    // Set headers for file download
    const filename = `screening_results_${new Date().toISOString().split('T')[0]}.xlsx`;
    res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
    res.setHeader('Content-Length', buffer.length);

    res.send(buffer);
  } catch (error: any) {
    console.error('Export error:', error);
    res.status(500).json({ error: error.message });
  }
});

export default router;
