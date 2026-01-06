"""
Multi-sheet Excel parser for blacklist files
Reads 4 sheets: Clients, Vendors, Staff, Others
"""
import openpyxl
from typing import Dict, List
from fastapi import UploadFile, HTTPException

async def parse_blacklist_excel(file: UploadFile) -> Dict[str, List[Dict]]:
    """
    Parse uploaded Excel file and extract data from all 4 sheets
    
    Args:
        file: UploadFile - The uploaded Excel file
        
    Returns:
        Dict with sheet names as keys and list of rows as values
        {
            'clients': [{'Name': 'John Doe', 'Country': 'USA', ...}, ...],
            'vendors': [...],
            'staff': [...],
            'others': [...]
        }
    """
    try:
        # Read file contents
        contents = await file.read()
        
        # Load workbook from bytes
        workbook = openpyxl.load_workbook(filename=file.filename, data_contents=contents, read_only=True)
        
        result = {}
        expected_sheets = ['Clients', 'Vendors', 'Staff', 'Others']
        
        for sheet_name in expected_sheets:
            # Check if sheet exists (case-insensitive)
            actual_sheet_name = None
            for ws_name in workbook.sheetnames:
                if ws_name.lower() == sheet_name.lower():
                    actual_sheet_name = ws_name
                    break
            
            if not actual_sheet_name:
                print(f"Warning: Sheet '{sheet_name}' not found in Excel file")
                result[sheet_name.lower()] = []
                continue
            
            # Get worksheet
            worksheet = workbook[actual_sheet_name]
            
            # Get headers from first row
            headers = []
            for cell in worksheet[1]:
                headers.append(cell.value if cell.value else f"Column_{len(headers)}")
            
            # Parse rows
            rows = []
            for row_idx, row in enumerate(worksheet.iter_rows(min_row=2, values_only=True), start=2):
                # Skip empty rows
                if all(cell is None or str(cell).strip() == '' for cell in row):
                    continue
                
                # Create row dictionary
                row_dict = {}
                for col_idx, value in enumerate(row):
                    if col_idx < len(headers):
                        row_dict[headers[col_idx]] = value
                
                # Only add row if it has a name field
                if row_dict.get('Name') or row_dict.get('name'):
                    rows.append(row_dict)
            
            result[sheet_name.lower()] = rows
            print(f"Parsed {len(rows)} rows from sheet '{sheet_name}'")
        
        workbook.close()
        return result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing Excel file: {str(e)}")
