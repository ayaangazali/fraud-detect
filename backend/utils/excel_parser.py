"""
Excel Parser Utility for Phase 4
Handles multi-sheet Excel parsing with Arabic text support
"""
import pandas as pd
import openpyxl
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import uuid
from fastapi import UploadFile, HTTPException


class ExcelParserError(Exception):
    """Custom exception for Excel parsing errors"""
    pass


class ExcelParser:
    """
    Excel file parser for blacklist and Kamco entity files
    Supports:
    - Multi-sheet workbooks
    - Arabic text (UTF-8 encoding)
    - Civil ID validation (12-digit)
    - Missing data handling
    - Data validation
    """
    
    def __init__(self, file_path: str = None, file_bytes: bytes = None):
        """
        Initialize parser with either file path or bytes
        
        Args:
            file_path: Path to Excel file
            file_bytes: File content as bytes
        """
        self.file_path = file_path
        self.file_bytes = file_bytes
        self.workbook = None
        self.sheets = {}
        
    def load_workbook(self) -> openpyxl.Workbook:
        """Load Excel workbook"""
        try:
            if self.file_bytes:
                from io import BytesIO
                self.workbook = openpyxl.load_workbook(BytesIO(self.file_bytes), data_only=True)
            elif self.file_path:
                self.workbook = openpyxl.load_workbook(self.file_path, data_only=True)
            else:
                raise ExcelParserError("No file path or bytes provided")
            return self.workbook
        except Exception as e:
            raise ExcelParserError(f"Failed to load workbook: {str(e)}")
    
    def get_sheet_names(self) -> List[str]:
        """Get all sheet names from workbook"""
        if not self.workbook:
            self.load_workbook()
        return self.workbook.sheetnames
    
    def parse_sheet(self, sheet_name: str, expected_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Parse a specific sheet into DataFrame
        
        Args:
            sheet_name: Name of the sheet to parse
            expected_columns: Optional list of expected column names
            
        Returns:
            DataFrame with parsed data
        """
        try:
            if self.file_bytes:
                from io import BytesIO
                df = pd.read_excel(BytesIO(self.file_bytes), sheet_name=sheet_name, engine='openpyxl')
            elif self.file_path:
                df = pd.read_excel(self.file_path, sheet_name=sheet_name, engine='openpyxl')
            else:
                raise ExcelParserError("No file path or bytes provided")
            
            # Clean column names (strip whitespace)
            df.columns = df.columns.str.strip()
            
            # Check expected columns if provided
            if expected_columns:
                missing_cols = set(expected_columns) - set(df.columns)
                if missing_cols:
                    raise ExcelParserError(
                        f"Missing required columns in sheet '{sheet_name}': {', '.join(missing_cols)}"
                    )
            
            return df
        except Exception as e:
            raise ExcelParserError(f"Failed to parse sheet '{sheet_name}': {str(e)}")
    
    def parse_all_sheets(self) -> Dict[str, pd.DataFrame]:
        """Parse all sheets in workbook"""
        if not self.workbook:
            self.load_workbook()
        
        sheets = {}
        for sheet_name in self.get_sheet_names():
            try:
                sheets[sheet_name] = self.parse_sheet(sheet_name)
            except Exception as e:
                print(f"Warning: Could not parse sheet '{sheet_name}': {str(e)}")
        
        return sheets
    
    def parse_blacklist(self, sheet_name: str = None) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Parse blacklist/sanctions list Excel file
        
        Args:
            sheet_name: Specific sheet name (optional, uses first sheet if not provided)
            
        Returns:
            Tuple of (records_list, summary_dict)
        """
        if not self.workbook:
            self.load_workbook()
        
        # Use first sheet if no sheet name provided
        if not sheet_name:
            sheet_name = self.get_sheet_names()[0]
        
        # Required columns for blacklist
        required_columns = ['name_arabic']  # Minimum required
        
        df = self.parse_sheet(sheet_name, required_columns)
        
        # Generate batch ID for this upload
        batch_id = f"BATCH-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{str(uuid.uuid4())[:8]}"
        
        records = []
        errors = []
        
        for idx, row in df.iterrows():
            try:
                record = self._parse_blacklist_row(row, batch_id)
                records.append(record)
            except Exception as e:
                errors.append(f"Row {idx + 2}: {str(e)}")  # +2 for header and 0-based index
        
        summary = {
            "total_rows": len(df),
            "valid_records": len(records),
            "errors": errors,
            "error_count": len(errors),
            "batch_id": batch_id,
            "sheet_name": sheet_name
        }
        
        return records, summary
    
    def _parse_blacklist_row(self, row: pd.Series, batch_id: str) -> Dict[str, Any]:
        """Parse a single blacklist row"""
        # Helper to safely get value
        def get_value(key: str, default: str = None) -> str:
            val = row.get(key, default)
            if pd.isna(val):
                return default
            return str(val).strip() if val else default
        
        # Validate Arabic name (required)
        name_arabic = get_value('name_arabic')
        if not name_arabic:
            raise ValueError("name_arabic is required")
        
        # Parse Civil ID and validate format
        civil_id = get_value('civil_id')
        if civil_id:
            # Remove any non-numeric characters
            civil_id = ''.join(filter(str.isdigit, civil_id))
            if len(civil_id) != 12:
                print(f"Warning: Invalid Civil ID format '{civil_id}' (expected 12 digits)")
        
        return {
            "name_arabic": name_arabic,
            "name_english": get_value('name_english'),
            "civil_id": civil_id,
            "passport_number": get_value('passport_number'),
            "entity_type": get_value('entity_type', 'Individual'),
            "nationality": get_value('nationality'),
            "country": get_value('country'),
            "decree_number": get_value('decree_number'),
            "list_date": get_value('list_date'),
            "source": get_value('source', 'Unknown'),
            "category": get_value('category'),
            "risk_level": get_value('risk_level', 'High'),
            "reason": get_value('reason'),
            "status": get_value('status', 'Active'),
            "notes": get_value('notes'),
            "upload_batch_id": batch_id
        }
    
    def validate_blacklist_file(self) -> Dict[str, Any]:
        """
        Validate blacklist Excel file structure
        
        Returns:
            Validation result dictionary
        """
        try:
            if not self.workbook:
                self.load_workbook()
            
            sheet_names = self.get_sheet_names()
            if not sheet_names:
                return {
                    "valid": False,
                    "error": "Workbook has no sheets"
                }
            
            # Check first sheet for required columns
            first_sheet = sheet_names[0]
            df = self.parse_sheet(first_sheet)
            
            if 'name_arabic' not in df.columns:
                return {
                    "valid": False,
                    "error": "Missing required column: name_arabic"
                }
            
            # Check if there's any data
            if len(df) == 0:
                return {
                    "valid": False,
                    "error": "No data rows found in Excel file"
                }
            
            return {
                "valid": True,
                "sheets": sheet_names,
                "primary_sheet": first_sheet,
                "row_count": len(df),
                "columns": list(df.columns)
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    def parse_kamco_entities(self, entity_type: str = "Clients") -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Parse Kamco entity data (Clients, Vendors, Staff, Others)
        
        Args:
            entity_type: Type of entity sheet to parse
            
        Returns:
            Tuple of (records_list, summary_dict)
        """
        if not self.workbook:
            self.load_workbook()
        
        # Try to find matching sheet
        sheet_name = None
        for name in self.get_sheet_names():
            if entity_type.lower() in name.lower():
                sheet_name = name
                break
        
        if not sheet_name:
            raise ExcelParserError(f"Could not find sheet for entity type: {entity_type}")
        
        df = self.parse_sheet(sheet_name)
        
        records = []
        for idx, row in df.iterrows():
            record = row.to_dict()
            # Clean None values
            record = {k: (v if pd.notna(v) else None) for k, v in record.items()}
            records.append(record)
        
        summary = {
            "entity_type": entity_type,
            "sheet_name": sheet_name,
            "total_records": len(records),
            "columns": list(df.columns)
        }
        
        return records, summary


# Convenience functions

def parse_blacklist_excel(file_path: str = None, file_bytes: bytes = None) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Convenience function to parse blacklist Excel file
    
    Args:
        file_path: Path to Excel file
        file_bytes: File content as bytes
        
    Returns:
        Tuple of (records_list, summary_dict)
    """
    parser = ExcelParser(file_path=file_path, file_bytes=file_bytes)
    return parser.parse_blacklist()


def validate_blacklist_excel(file_path: str = None, file_bytes: bytes = None) -> Dict[str, Any]:
    """
    Convenience function to validate blacklist Excel file
    
    Args:
        file_path: Path to Excel file
        file_bytes: File content as bytes
        
    Returns:
        Validation result dictionary
    """
    parser = ExcelParser(file_path=file_path, file_bytes=file_bytes)
    return parser.validate_blacklist_file()


# Legacy compatibility function
async def parse_blacklist_excel_legacy(file: UploadFile) -> Dict[str, List[Dict]]:
    """
    Legacy function for backward compatibility
    Parse uploaded Excel file and extract data from all 4 sheets
    """
    try:
        contents = await file.read()
        workbook = openpyxl.load_workbook(filename=file.filename, data_only=True)
        
        result = {}
        expected_sheets = ['Clients', 'Vendors', 'Staff', 'Others']
        
        for sheet_name in expected_sheets:
            actual_sheet_name = None
            for ws_name in workbook.sheetnames:
                if ws_name.lower() == sheet_name.lower():
                    actual_sheet_name = ws_name
                    break
            
            if not actual_sheet_name:
                result[sheet_name.lower()] = []
                continue
            
            worksheet = workbook[actual_sheet_name]
            headers = [cell.value if cell.value else f"Column_{i}" for i, cell in enumerate(worksheet[1])]
            
            rows = []
            for row in worksheet.iter_rows(min_row=2, values_only=True):
                if all(cell is None or str(cell).strip() == '' for cell in row):
                    continue
                
                row_dict = {headers[i]: value for i, value in enumerate(row) if i < len(headers)}
                if row_dict.get('Name') or row_dict.get('name'):
                    rows.append(row_dict)
            
            result[sheet_name.lower()] = rows
        
        workbook.close()
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing Excel file: {str(e)}")

