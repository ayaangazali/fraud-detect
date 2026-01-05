// src/utils/excelExporter.ts
import ExcelJS from 'exceljs';
import { MatchResult } from '../types';

/**
 * Generate Excel file from match results with enhanced styling and summary
 */
export async function generateExcelReport(matches: MatchResult[]): Promise<Buffer> {
  const workbook = new ExcelJS.Workbook();
  workbook.creator = 'AML/KYC Screening System';
  workbook.created = new Date();
  
  // ========================================
  // MAIN RESULTS SHEET
  // ========================================
  const worksheet = workbook.addWorksheet('Screening Results', {
    properties: { defaultRowHeight: 22 }
  });

  // Define columns
  worksheet.columns = [
    { header: 'Customer ID', key: 'customer_id', width: 15 },
    { header: 'Customer Name', key: 'customer_name', width: 30 },
    { header: 'Customer Type', key: 'customer_type', width: 15 },
    { header: 'DOB/Reg No', key: 'dob_or_reg_no', width: 20 },
    { header: 'Nationality', key: 'nationality_country', width: 20 },
    { header: 'Blacklist Match', key: 'matched_blacklist_name', width: 30 },
    { header: 'Matched Alias', key: 'matched_alias', width: 30 },
    { header: 'Source', key: 'source', width: 15 },
    { header: 'Blacklist Type', key: 'blacklist_type', width: 15 },
    { header: 'Effective Date', key: 'effective_date', width: 15 },
    { header: 'Similarity Score', key: 'similarity_score', width: 15 },
    { header: 'Match Type', key: 'match_type', width: 15 },
    { header: 'Match Reason', key: 'match_reason', width: 60 },
  ];

  // Style header row
  const headerRow = worksheet.getRow(1);
  headerRow.font = { bold: true, size: 12, color: { argb: 'FFFFFFFF' } };
  headerRow.fill = {
    type: 'pattern',
    pattern: 'solid',
    fgColor: { argb: 'FF228BE6' } // Blue header
  };
  headerRow.alignment = { vertical: 'middle', horizontal: 'center' };
  headerRow.height = 28;

  // Add data rows with styling
  matches.forEach((match, index) => {
    const row = worksheet.addRow({
      customer_id: match.customer_id,
      customer_name: match.customer_name,
      customer_type: match.customer_type,
      dob_or_reg_no: match.dob_or_reg_no,
      nationality_country: match.nationality_country,
      matched_blacklist_name: match.matched_blacklist_name,
      matched_alias: match.matched_alias || 'N/A',
      source: match.source,
      blacklist_type: match.blacklist_type === 'regulator' ? 'Regulator' : 'User',
      effective_date: match.effective_date,
      similarity_score: `${match.similarity_score}%`,
      match_type: match.match_type.charAt(0).toUpperCase() + match.match_type.slice(1),
      match_reason: match.match_reason,
    });

    // Color code customer data columns (blue theme)
    for (let i = 1; i <= 5; i++) {
      const cell = row.getCell(i);
      cell.fill = {
        type: 'pattern',
        pattern: 'solid',
        fgColor: { argb: 'FFE7F5FF' } // Light blue for customer data
      };
      cell.font = { color: { argb: 'FF1864AB' } }; // Dark blue text
    }

    // Color code regulator/match data columns (purple theme)
    for (let i = 6; i <= 13; i++) {
      const cell = row.getCell(i);
      cell.fill = {
        type: 'pattern',
        pattern: 'solid',
        fgColor: { argb: 'FFF3F0FF' } // Light purple for regulator data
      };
      cell.font = { color: { argb: 'FF5F3DC4' } }; // Dark purple text
    }

    // Highlight based on risk level (similarity score)
    const scoreCell = row.getCell(11);
    if (match.similarity_score >= 90) {
      // High risk - Red
      scoreCell.fill = {
        type: 'pattern',
        pattern: 'solid',
        fgColor: { argb: 'FFFFE5E5' }
      };
      scoreCell.font = { color: { argb: 'FFC92A2A' }, bold: true };
    } else if (match.similarity_score >= 75) {
      // Medium risk - Orange
      scoreCell.fill = {
        type: 'pattern',
        pattern: 'solid',
        fgColor: { argb: 'FFFFE8CC' }
      };
      scoreCell.font = { color: { argb: 'FFE8590C' }, bold: true };
    }

    // Highlight blacklist type
    const typeCell = row.getCell(9);
    typeCell.font = { bold: true };

    row.alignment = { vertical: 'middle', wrapText: false };
  });

  // Add borders to all cells
  worksheet.eachRow((row) => {
    row.eachCell((cell) => {
      cell.border = {
        top: { style: 'thin', color: { argb: 'FFCCCCCC' } },
        left: { style: 'thin', color: { argb: 'FFCCCCCC' } },
        bottom: { style: 'thin', color: { argb: 'FFCCCCCC' } },
        right: { style: 'thin', color: { argb: 'FFCCCCCC' } }
      };
    });
  });

  // Add auto-filter
  worksheet.autoFilter = {
    from: { row: 1, column: 1 },
    to: { row: 1, column: 13 }
  };

  // Freeze header row
  worksheet.views = [
    { state: 'frozen', ySplit: 1 }
  ];

  // ========================================
  // SUMMARY SHEET
  // ========================================
  const summarySheet = workbook.addWorksheet('Summary');
  
  const totalMatches = matches.length;
  const highRisk = matches.filter(m => m.similarity_score >= 90).length;
  const mediumRisk = matches.filter(m => m.similarity_score >= 75 && m.similarity_score < 90).length;
  const lowRisk = matches.filter(m => m.similarity_score < 75).length;
  const regulatorMatches = matches.filter(m => m.blacklist_type === 'regulator').length;
  const userMatches = matches.filter(m => m.blacklist_type === 'user').length;
  const directMatches = matches.filter(m => m.match_type === 'direct').length;
  const aliasMatches = matches.filter(m => m.match_type === 'alias').length;
  const fuzzyMatches = matches.filter(m => m.match_type === 'fuzzy').length;

  summarySheet.columns = [
    { header: 'Metric', key: 'metric', width: 35 },
    { header: 'Value', key: 'value', width: 20 }
  ];

  const summaryHeaderRow = summarySheet.getRow(1);
  summaryHeaderRow.font = { bold: true, size: 14, color: { argb: 'FFFFFFFF' } };
  summaryHeaderRow.fill = {
    type: 'pattern',
    pattern: 'solid',
    fgColor: { argb: 'FF2E7D32' }
  };
  summaryHeaderRow.height = 28;
  summaryHeaderRow.alignment = { vertical: 'middle', horizontal: 'center' };

  // Add summary rows
  summarySheet.addRow({ metric: 'Total Matches', value: totalMatches });
  summarySheet.addRow({ metric: '' }); // Empty row
  
  summarySheet.addRow({ metric: 'Risk Breakdown' });
  summarySheet.addRow({ metric: '  High Risk (≥90%)', value: highRisk });
  summarySheet.addRow({ metric: '  Medium Risk (75-89%)', value: mediumRisk });
  summarySheet.addRow({ metric: '  Low Risk (<75%)', value: lowRisk });
  summarySheet.addRow({ metric: '' }); // Empty row
  
  summarySheet.addRow({ metric: 'Blacklist Source' });
  summarySheet.addRow({ metric: '  Regulator Blacklist', value: regulatorMatches });
  summarySheet.addRow({ metric: '  User Blacklist', value: userMatches });
  summarySheet.addRow({ metric: '' }); // Empty row
  
  summarySheet.addRow({ metric: 'Match Type' });
  summarySheet.addRow({ metric: '  Direct Match', value: directMatches });
  summarySheet.addRow({ metric: '  Alias Match', value: aliasMatches });
  summarySheet.addRow({ metric: '  Fuzzy Match', value: fuzzyMatches });
  summarySheet.addRow({ metric: '' }); // Empty row
  
  summarySheet.addRow({ metric: 'Report Generated', value: new Date().toLocaleString() });

  // Style summary rows
  summarySheet.eachRow((row, rowNumber) => {
    if (rowNumber > 1) {
      row.font = { size: 12 };
      row.alignment = { vertical: 'middle' };
      
      // Bold section headers
      if (row.getCell(1).value && !row.getCell(2).value && row.getCell(1).value !== '') {
        row.getCell(1).font = { bold: true, size: 13, color: { argb: 'FF228BE6' } };
      }
      
      // Bold metrics
      if (row.getCell(1).value && row.getCell(2).value) {
        row.getCell(1).font = { bold: true };
      }
    }
    
    row.eachCell((cell) => {
      if (cell.value) {
        cell.border = {
          top: { style: 'thin', color: { argb: 'FFCCCCCC' } },
          left: { style: 'thin', color: { argb: 'FFCCCCCC' } },
          bottom: { style: 'thin', color: { argb: 'FFCCCCCC' } },
          right: { style: 'thin', color: { argb: 'FFCCCCCC' } }
        };
      }
    });
  });

  // Generate buffer
  const buffer = await workbook.xlsx.writeBuffer();
  return Buffer.from(buffer);
}
