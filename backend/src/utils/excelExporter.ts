// src/utils/excelExporter.ts
import ExcelJS from 'exceljs';
import { MatchResult } from '../types';

/**
 * Generate Excel file from match results
 */
export async function generateExcelReport(matches: MatchResult[]): Promise<Buffer> {
  const workbook = new ExcelJS.Workbook();
  const worksheet = workbook.addWorksheet('Screening Results');

  // Define columns
  worksheet.columns = [
    { header: 'Customer ID', key: 'customer_id', width: 15 },
    { header: 'Customer Name', key: 'customer_name', width: 30 },
    { header: 'Customer Type', key: 'customer_type', width: 15 },
    { header: 'DOB/Reg No', key: 'dob_or_reg_no', width: 15 },
    { header: 'Nationality/Country', key: 'nationality_country', width: 20 },
    { header: 'Matched Blacklist Name', key: 'matched_blacklist_name', width: 30 },
    { header: 'Matched Alias', key: 'matched_alias', width: 30 },
    { header: 'Source', key: 'source', width: 15 },
    { header: 'Blacklist Type', key: 'blacklist_type', width: 15 },
    { header: 'Effective Date', key: 'effective_date', width: 15 },
    { header: 'Similarity Score', key: 'similarity_score', width: 15 },
  ];

  // Style header row
  worksheet.getRow(1).font = { bold: true };
  worksheet.getRow(1).fill = {
    type: 'pattern',
    pattern: 'solid',
    fgColor: { argb: 'FFD3D3D3' },
  };

  // Add data rows
  matches.forEach(match => {
    worksheet.addRow({
      customer_id: match.customer_id,
      customer_name: match.customer_name,
      customer_type: match.customer_type,
      dob_or_reg_no: match.dob_or_reg_no,
      nationality_country: match.nationality_country,
      matched_blacklist_name: match.matched_blacklist_name,
      matched_alias: match.matched_alias || '',
      source: match.source,
      blacklist_type: match.blacklist_type,
      effective_date: match.effective_date,
      similarity_score: match.similarity_score,
    });
  });

  // Generate buffer
  const buffer = await workbook.xlsx.writeBuffer();
  return Buffer.from(buffer);
}
