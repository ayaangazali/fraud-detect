// src/routes/upload.ts
import { Router, Request, Response } from 'express';
import multer from 'multer';
import { parseFile, validateColumns } from '../utils/fileParser';
import { validateCustomers, validateBlacklist } from '../utils/validator';
import {
  CustomerUploadResponse,
  BlacklistUploadResponse,
} from '../types';

const router = Router();

// Configure multer for file uploads
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB limit
  },
  fileFilter: (req: any, file: any, cb: any) => {
    const ext = file.originalname.toLowerCase().split('.').pop();
    if (ext === 'csv' || ext === 'xlsx' || ext === 'xls') {
      cb(null, true);
    } else {
      cb(new Error('Only CSV and XLSX files are allowed'));
    }
  },
});

/**
 * POST /api/upload/customers
 * Upload and validate customer file
 */
router.post(
  '/customers',
  upload.single('file'),
  async (req: Request, res: Response) => {
    try {
      if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
      }

      // Parse file
      const data = parseFile(req.file.buffer, req.file.originalname);

      // Validate required columns
      const requiredColumns = [
        'customer_id',
        'type',
        'full_name_en',
        'nationality_country',
      ];
      validateColumns(data, requiredColumns);

      // Validate data
      const { rows, errors } = validateCustomers(data);

      // Prepare response
      const response: CustomerUploadResponse = {
        rows,
        preview: rows.slice(0, 20),
        errors,
        totalRows: rows.length,
        validRows: rows.length - new Set(errors.map(e => e.row)).size,
      };

      res.json(response);
    } catch (error: any) {
      console.error('Customer upload error:', error);
      res.status(400).json({ error: error.message });
    }
  }
);

/**
 * POST /api/upload/blacklist
 * Upload and validate blacklist file
 */
router.post(
  '/blacklist',
  upload.single('file'),
  async (req: Request, res: Response) => {
    try {
      if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
      }

      // Parse file
      const data = parseFile(req.file.buffer, req.file.originalname);

      // Validate required columns
      const requiredColumns = ['full_name', 'source', 'effective_date'];
      validateColumns(data, requiredColumns);

      // Validate data
      const { rows, errors } = validateBlacklist(data);

      // Prepare response
      const response: BlacklistUploadResponse = {
        rows,
        preview: rows.slice(0, 20),
        errors,
        totalRows: rows.length,
        validRows: rows.length - new Set(errors.map(e => e.row)).size,
      };

      res.json(response);
    } catch (error: any) {
      console.error('Blacklist upload error:', error);
      res.status(400).json({ error: error.message });
    }
  }
);

export default router;
