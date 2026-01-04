// src/utils/validator.ts
import {
  CustomerRow,
  CustomerValidationError,
  BlacklistRow,
  BlacklistValidationError,
} from '../types';

/**
 * Validate customer data rows
 */
export function validateCustomers(data: any[]): {
  rows: CustomerRow[];
  errors: CustomerValidationError[];
} {
  const rows: CustomerRow[] = [];
  const errors: CustomerValidationError[] = [];

  data.forEach((item, index) => {
    const rowNumber = index + 2; // +2 because: 0-indexed + header row
    const rowErrors: CustomerValidationError[] = [];

    // Validate customer_id
    if (!item.customer_id || String(item.customer_id).trim() === '') {
      rowErrors.push({
        row: rowNumber,
        field: 'customer_id',
        message: 'customer_id is required',
      });
    }

    // Validate type
    if (!item.type || !['individual', 'corporate'].includes(item.type)) {
      rowErrors.push({
        row: rowNumber,
        field: 'type',
        message: 'type must be "individual" or "corporate"',
      });
    }

    // Validate full_name_en
    if (!item.full_name_en || String(item.full_name_en).trim() === '') {
      rowErrors.push({
        row: rowNumber,
        field: 'full_name_en',
        message: 'full_name_en is required',
      });
    }

    // Validate type-specific fields
    if (item.type === 'individual') {
      if (!item.date_of_birth || String(item.date_of_birth).trim() === '') {
        rowErrors.push({
          row: rowNumber,
          field: 'date_of_birth',
          message: 'date_of_birth is required for individuals',
        });
      }
    } else if (item.type === 'corporate') {
      if (!item.company_reg_no || String(item.company_reg_no).trim() === '') {
        rowErrors.push({
          row: rowNumber,
          field: 'company_reg_no',
          message: 'company_reg_no is required for corporates',
        });
      }
    }

    // Validate nationality_country
    if (!item.nationality_country || String(item.nationality_country).trim() === '') {
      rowErrors.push({
        row: rowNumber,
        field: 'nationality_country',
        message: 'nationality_country is required',
      });
    }

    // Add row if no critical errors (can still add to rows for preview)
    const row: CustomerRow = {
      customer_id: String(item.customer_id || '').trim(),
      type: item.type,
      full_name_en: String(item.full_name_en || '').trim(),
      date_of_birth: item.date_of_birth ? String(item.date_of_birth).trim() : undefined,
      company_reg_no: item.company_reg_no ? String(item.company_reg_no).trim() : undefined,
      nationality_country: String(item.nationality_country || '').trim(),
    };

    rows.push(row);
    errors.push(...rowErrors);
  });

  return { rows, errors };
}

/**
 * Validate blacklist data rows
 */
export function validateBlacklist(data: any[]): {
  rows: BlacklistRow[];
  errors: BlacklistValidationError[];
} {
  const rows: BlacklistRow[] = [];
  const errors: BlacklistValidationError[] = [];

  data.forEach((item, index) => {
    const rowNumber = index + 2;
    const rowErrors: BlacklistValidationError[] = [];

    // Validate full_name
    if (!item.full_name || String(item.full_name).trim() === '') {
      rowErrors.push({
        row: rowNumber,
        field: 'full_name',
        message: 'full_name is required',
      });
    }

    // Validate source
    if (!item.source || !['government', 'regulator', 'other'].includes(item.source)) {
      rowErrors.push({
        row: rowNumber,
        field: 'source',
        message: 'source must be "government", "regulator", or "other"',
      });
    }

    // Validate effective_date
    if (!item.effective_date || String(item.effective_date).trim() === '') {
      rowErrors.push({
        row: rowNumber,
        field: 'effective_date',
        message: 'effective_date is required',
      });
    }

    const row: BlacklistRow = {
      full_name: String(item.full_name || '').trim(),
      alias_alternate_names: item.alias_alternate_names
        ? String(item.alias_alternate_names).trim()
        : undefined,
      source: item.source,
      effective_date: String(item.effective_date || '').trim(),
    };

    rows.push(row);
    errors.push(...rowErrors);
  });

  return { rows, errors };
}
