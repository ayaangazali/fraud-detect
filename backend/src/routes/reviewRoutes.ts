// src/routes/reviewRoutes.ts
import { Router, Request, Response } from 'express';
import ExcelJS from 'exceljs';
import PDFDocument from 'pdfkit';
import { appendToLogbook, readFlaggedLogbook } from '../utils/csvHandler';
import { FlagRequest, SafeRequest, FlaggedLogEntry } from '../types';

const router = Router();

/**
 * POST /api/review/flag
 * Flag a match and add to logbook
 */
router.post('/flag', async (req: Request, res: Response) => {
  try {
    const { match, comments, flagged_by }: FlagRequest = req.body;

    // Validation
    if (!match || !comments) {
      return res.status(400).json({ error: 'Match data and comments are required' });
    }

    if (comments.trim().length < 10) {
      return res.status(400).json({ error: 'Comments must be at least 10 characters long' });
    }

    // Prepare log entry
    const logEntry: Omit<FlaggedLogEntry, 'flagged_id' | 'flagged_date'> = {
      customer_id: match.customer_id,
      customer_name: match.customer_name,
      customer_type: match.customer_type,
      customer_dob: match.dob_or_reg_no,
      customer_nationality: match.nationality_country,
      customer_department: match.kamco_client?.department || 'N/A',
      customer_position: match.kamco_client?.position || 'N/A',
      screening_name: match.matched_blacklist_name,
      screening_aliases: match.matched_alias || 'N/A',
      screening_source: match.source,
      similarity_score: match.similarity_score,
      match_type: match.match_type,
      match_reason: match.match_reason,
      user_comments: comments.trim(),
      flagged_by: flagged_by || 'System',
      screening_file_source: 'User Upload',
    };

    // Append to logbook
    const flaggedEntry = await appendToLogbook(logEntry);

    res.json({
      success: true,
      message: 'Case flagged successfully and added to log book',
      flagged_id: flaggedEntry.flagged_id,
      flagged_date: flaggedEntry.flagged_date,
    });
  } catch (error: any) {
    console.error('Error flagging case:', error);
    res.status(500).json({ error: error.message || 'Failed to flag case' });
  }
});

/**
 * POST /api/review/safe
 * Mark a match as safe (cleared)
 */
router.post('/safe', async (req: Request, res: Response) => {
  try {
    const { match_id, screening_name }: SafeRequest = req.body;

    // Validation
    if (!match_id || !screening_name) {
      return res.status(400).json({ error: 'Match ID and screening name are required' });
    }

    // For now, we just log it. In production, you might want to store safe cases for audit
    console.log(`✅ Case marked as SAFE: ${match_id} - ${screening_name}`);

    // Optional: Store in safe-cases log for audit trail
    // await appendToSafeCasesLog({ match_id, screening_name, cleared_date: new Date().toISOString() });

    res.json({
      success: true,
      message: 'Case marked as safe',
      match_id,
    });
  } catch (error: any) {
    console.error('Error marking case as safe:', error);
    res.status(500).json({ error: error.message || 'Failed to mark case as safe' });
  }
});

/**
 * GET /api/review/flagged-logbook
 * Get all flagged cases with pagination and filtering
 */
router.get('/flagged-logbook', async (req: Request, res: Response) => {
  try {
    const limit = parseInt(req.query.limit as string) || 100;
    const skip = parseInt(req.query.skip as string) || 0;
    const customer_id = req.query.customer_id as string;
    const flagged_by = req.query.flagged_by as string;

    const filterBy: any = {};
    if (customer_id) filterBy.customer_id = customer_id;
    if (flagged_by) filterBy.flagged_by = flagged_by;

    const entries = await readFlaggedLogbook({ limit, skip, filterBy });

    res.json({
      success: true,
      entries,
      count: entries.length,
      skip,
      limit,
    });
  } catch (error: any) {
    console.error('Error reading flagged logbook:', error);
    res.status(500).json({ error: error.message || 'Failed to read flagged logbook' });
  }
});

/**
 * GET /api/review/export-flagged
 * Export all flagged cases to Excel with formatting
 */
router.get('/export-flagged', async (req: Request, res: Response) => {
  try {
    // Read all flagged entries
    const entries = await readFlaggedLogbook({ limit: 10000, skip: 0 });

    if (entries.length === 0) {
      return res.status(404).json({ error: 'No flagged cases found' });
    }

    // Create workbook
    const workbook = new ExcelJS.Workbook();
    const worksheet = workbook.addWorksheet('Flagged Cases');

    // Define columns
    worksheet.columns = [
      { header: 'Flagged ID', key: 'flagged_id', width: 15 },
      { header: 'Customer ID', key: 'customer_id', width: 12 },
      { header: 'Customer Name', key: 'customer_name', width: 25 },
      { header: 'Type', key: 'customer_type', width: 12 },
      { header: 'DOB/Reg No', key: 'customer_dob', width: 15 },
      { header: 'Nationality', key: 'customer_nationality', width: 15 },
      { header: 'Department', key: 'customer_department', width: 20 },
      { header: 'Position', key: 'customer_position', width: 20 },
      { header: 'Screening Name', key: 'screening_name', width: 25 },
      { header: 'Aliases', key: 'screening_aliases', width: 30 },
      { header: 'Source', key: 'screening_source', width: 20 },
      { header: 'Similarity %', key: 'similarity_score', width: 12 },
      { header: 'Match Type', key: 'match_type', width: 12 },
      { header: 'Match Reason', key: 'match_reason', width: 30 },
      { header: 'Comments', key: 'user_comments', width: 40 },
      { header: 'Flagged Date', key: 'flagged_date', width: 20 },
      { header: 'Flagged By', key: 'flagged_by', width: 15 },
      { header: 'File Source', key: 'screening_file_source', width: 15 },
    ];

    // Style header row
    worksheet.getRow(1).font = { bold: true, size: 12, color: { argb: 'FFFFFFFF' } };
    worksheet.getRow(1).fill = {
      type: 'pattern',
      pattern: 'solid',
      fgColor: { argb: 'FF1864AB' }, // Customer blue
    };
    worksheet.getRow(1).alignment = { vertical: 'middle', horizontal: 'center' };
    worksheet.getRow(1).height = 25;

    // Add data rows
    entries.forEach((entry) => {
      const row = worksheet.addRow({
        flagged_id: entry.flagged_id,
        customer_id: entry.customer_id,
        customer_name: entry.customer_name,
        customer_type: entry.customer_type,
        customer_dob: entry.customer_dob,
        customer_nationality: entry.customer_nationality,
        customer_department: entry.customer_department,
        customer_position: entry.customer_position,
        screening_name: entry.screening_name,
        screening_aliases: entry.screening_aliases,
        screening_source: entry.screening_source,
        similarity_score: entry.similarity_score,
        match_type: entry.match_type,
        match_reason: entry.match_reason,
        user_comments: entry.user_comments,
        flagged_date: entry.flagged_date,
        flagged_by: entry.flagged_by,
        screening_file_source: entry.screening_file_source,
      });

      // Color-code by risk level
      const score = entry.similarity_score;
      if (score >= 95) {
        row.fill = {
          type: 'pattern',
          pattern: 'solid',
          fgColor: { argb: 'FFFFE6E6' }, // Light red
        };
      } else if (score >= 85) {
        row.fill = {
          type: 'pattern',
          pattern: 'solid',
          fgColor: { argb: 'FFFFF4E6' }, // Light orange
        };
      } else if (score >= 75) {
        row.fill = {
          type: 'pattern',
          pattern: 'solid',
          fgColor: { argb: 'FFFFFBE6' }, // Light yellow
        };
      }

      // Make similarity score bold
      row.getCell('similarity_score').font = { bold: true };
    });

    // Add filters
    worksheet.autoFilter = {
      from: 'A1',
      to: `R1`,
    };

    // Freeze header row
    worksheet.views = [{ state: 'frozen', ySplit: 1 }];

    // Generate filename with date
    const date = new Date().toISOString().split('T')[0];
    const filename = `KAMCO_Flagged_Cases_${date}.xlsx`;

    // Set response headers
    res.setHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);

    // Write to response
    await workbook.xlsx.write(res);
    res.end();
  } catch (error: any) {
    console.error('Error exporting flagged cases:', error);
    res.status(500).json({ error: error.message || 'Failed to export flagged cases' });
  }
});

/**
 * POST /api/review/generate-pdf
 * Generate comprehensive PDF screening report
 */
router.post('/generate-pdf', async (req: Request, res: Response) => {
  try {
    const { summary, matches, flaggedMatches } = req.body;

    // Create PDF document
    const doc = new PDFDocument({
      size: 'A4',
      margins: { top: 50, bottom: 50, left: 50, right: 50 },
    });

    // Set response headers
    const date = new Date().toISOString().split('T')[0];
    const filename = `KAMCO_Screening_Report_${date}.pdf`;
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);

    // Pipe PDF to response
    doc.pipe(res);

    // Header
    doc.fontSize(24).font('Helvetica-Bold').text('KAMCO Investment Company', { align: 'center' });
    doc.fontSize(18).text('AML/KYC Screening Report', { align: 'center' });
    doc.moveDown(0.5);
    doc.fontSize(10).font('Helvetica').fillColor('#666666')
      .text(`Generated: ${new Date().toLocaleString()}`, { align: 'center' });
    doc.moveDown(2);

    // Executive Summary
    doc.fontSize(16).font('Helvetica-Bold').fillColor('#000000').text('Executive Summary');
    doc.moveDown(0.5);
    doc.fontSize(11).font('Helvetica');
    
    const summaryData = [
      `Total Matches Screened: ${summary?.total || matches?.length || 0}`,
      `Cases Flagged for Review: ${summary?.flagged || 0}`,
      `Cases Marked Safe: ${summary?.safe || 0}`,
      `Cases Skipped: ${summary?.skipped || 0}`,
    ];

    summaryData.forEach(line => {
      doc.text(`• ${line}`);
    });
    doc.moveDown(2);

    // Risk Overview
    if (matches && matches.length > 0) {
      doc.fontSize(16).font('Helvetica-Bold').text('Risk Distribution');
      doc.moveDown(0.5);
      doc.fontSize(11).font('Helvetica');

      const critical = matches.filter((m: any) => m.similarity_score >= 95).length;
      const high = matches.filter((m: any) => m.similarity_score >= 85 && m.similarity_score < 95).length;
      const medium = matches.filter((m: any) => m.similarity_score >= 75 && m.similarity_score < 85).length;
      const low = matches.filter((m: any) => m.similarity_score < 75).length;

      doc.fillColor('#D32F2F').text(`⚠️  Critical Risk (95%+): ${critical} cases`);
      doc.fillColor('#F57C00').text(`⚠️  High Risk (85-94%): ${high} cases`);
      doc.fillColor('#FBC02D').text(`⚠️  Medium Risk (75-84%): ${medium} cases`);
      doc.fillColor('#388E3C').text(`✓  Low Risk (<75%): ${low} cases`);
      doc.moveDown(2);
    }

    // Flagged Cases Detail
    if (flaggedMatches && flaggedMatches.length > 0) {
      doc.fillColor('#000000');
      doc.fontSize(16).font('Helvetica-Bold').text('Flagged Cases - Detailed Review');
      doc.moveDown(0.5);

      flaggedMatches.forEach((match: any, index: number) => {
        if (doc.y > 700) doc.addPage();

        doc.fontSize(12).font('Helvetica-Bold')
          .fillColor('#1864AB')
          .text(`Case ${index + 1}: ${match.customer_name}`);
        
        doc.fontSize(10).font('Helvetica').fillColor('#000000');
        doc.text(`Customer ID: ${match.customer_id}`);
        doc.text(`Screening Match: ${match.screening_name}`);
        doc.text(`Similarity Score: ${match.similarity_score}%`);
        doc.text(`Match Type: ${match.match_type.toUpperCase()}`);
        doc.text(`Source: ${match.screening_source}`);
        
        if (match.user_comments) {
          doc.fillColor('#7950F2').text(`Investigator Notes: ${match.user_comments}`);
        }
        
        doc.moveDown(1);
        doc.strokeColor('#CCCCCC').lineWidth(0.5)
          .moveTo(50, doc.y).lineTo(545, doc.y).stroke();
        doc.moveDown(1);
      });
    }

    // Compliance Statement
    doc.addPage();
    doc.fontSize(14).font('Helvetica-Bold').fillColor('#000000')
      .text('Compliance Officer Review', { align: 'center' });
    doc.moveDown(2);

    doc.fontSize(11).font('Helvetica');
    doc.text('This screening report has been generated by KAMCO\'s automated AML/KYC system.');
    doc.text('All flagged cases require manual review by a qualified compliance officer.');
    doc.moveDown(2);

    doc.text('Compliance Officer Signature: _________________________________');
    doc.moveDown(1);
    doc.text('Date: _________________________________');
    doc.moveDown(1);
    doc.text('Approval Status: _________________________________');

    // Footer
    doc.fontSize(8).fillColor('#999999')
      .text('CONFIDENTIAL - KAMCO Investment Company', 50, 770, { align: 'center' });

    // Finalize PDF
    doc.end();
  } catch (error: any) {
    console.error('Error generating PDF:', error);
    res.status(500).json({ error: error.message || 'Failed to generate PDF report' });
  }
});

export default router;
