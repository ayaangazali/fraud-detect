"""
Multi-Format Parser for Blacklist Files
Supports: Excel (.xlsx, .xls), CSV, XML, JSON
"""
import pandas as pd
import xml.etree.ElementTree as ET
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from io import BytesIO


class MultiFormatParserError(Exception):
    """Custom exception for parsing errors"""
    pass


class MultiFormatParser:
    """
    Universal parser for blacklist data in multiple formats
    Supports: Excel, CSV, XML, JSON
    """
    
    # Column name mappings (English, Arabic, and variations)
    FIELD_MAPPINGS = {
        'name_english': [
            'name (english)', 'name english', 'english name', 'name_english',
            'name', 'full name', 'person name', 'entity name',
            'english_name', 'name_en', 'name en'
        ],
        'name_arabic': [
            'name (arabic)', 'name arabic', 'arabic name', 'name_arabic',
            'الاسم', 'اسم', 'الاسم الكامل', 'اسم الشخص',
            'arabic_name', 'name_ar', 'name ar', 'الإسم'
        ],
        'civil_id': [
            'civil id', 'civil_id', 'civilid', 'civil id number',
            'رقم مدني', 'رقم_مدني', 'الرقم المدني', 'رقم المدني',
            'civil', 'id number', 'national id', 'رقم هوية'
        ],
        'passport_number': [
            'passport number', 'passport_number', 'passport', 'passport no',
            'رقم جواز السفر', 'جواز السفر', 'جواز_سفر', 'رقم_جواز',
            'passport_no', 'passport num'
        ],
        'nationality': [
            'nationality', 'country', 'nation', 'الجنسية', 'جنسية',
            'national', 'citizen of', 'الجنسيه'
        ],
        'source': [
            'source', 'data source', 'list source', 'المصدر', 'مصدر',
            'origin', 'from'
        ],
        'list_date': [
            'date added', 'date_added', 'add date', 'added date',
            'تاريخ الإضافة', 'تاريخ اضافة', 'التاريخ',
            'date', 'created date', 'entry date', 'list date', 'list_date'
        ],
        'notes': [
            'notes', 'remarks', 'comments', 'description',
            'ملاحظات', 'ملاحظة', 'تعليقات', 'وصف',
            'note', 'remark', 'comment'
        ]
    }
    
    def __init__(self, file_bytes: bytes, filename: str):
        """
        Initialize parser with file data
        
        Args:
            file_bytes: File content as bytes
            filename: Original filename (used to detect format)
        """
        self.file_bytes = file_bytes
        self.filename = filename.lower()
        self.format = self._detect_format()
        
    def _detect_format(self) -> str:
        """Detect file format from extension"""
        if self.filename.endswith(('.xlsx', '.xls')):
            return 'excel'
        elif self.filename.endswith('.csv'):
            return 'csv'
        elif self.filename.endswith('.xml'):
            return 'xml'
        elif self.filename.endswith('.json'):
            return 'json'
        else:
            raise MultiFormatParserError(f"Unsupported file format: {self.filename}")
    
    def _normalize_column_name(self, col: str) -> Optional[str]:
        """
        Normalize column name to standard field name
        
        Args:
            col: Column name from file
            
        Returns:
            Normalized field name or None if not recognized
        """
        col_lower = str(col).lower().strip()
        
        for field, variations in self.FIELD_MAPPINGS.items():
            if col_lower in variations:
                return field
        
        return None
    
    def _map_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Map DataFrame columns to standard field names
        
        Args:
            df: Raw DataFrame
            
        Returns:
            DataFrame with normalized column names
        """
        # Create mapping
        column_mapping = {}
        for col in df.columns:
            normalized = self._normalize_column_name(col)
            if normalized:
                column_mapping[col] = normalized
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        return df
    
    def _parse_excel(self) -> pd.DataFrame:
        """Parse Excel file"""
        try:
            df = pd.read_excel(BytesIO(self.file_bytes), engine='openpyxl')
            
            # Skip rows until we find headers (handle title rows)
            for i in range(min(20, len(df))):
                if self._looks_like_header_row(df.iloc[i]):
                    if i > 0:
                        # Use this row as headers
                        df.columns = df.iloc[i]
                        df = df[i+1:].reset_index(drop=True)
                    break
            
            return df
        except Exception as e:
            raise MultiFormatParserError(f"Failed to parse Excel: {str(e)}")
    
    def _parse_csv(self) -> pd.DataFrame:
        """Parse CSV file"""
        try:
            # Try different encodings
            for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1256']:
                try:
                    df = pd.read_csv(BytesIO(self.file_bytes), encoding=encoding)
                    return df
                except UnicodeDecodeError:
                    continue
            
            raise MultiFormatParserError("Unable to decode CSV file")
        except Exception as e:
            raise MultiFormatParserError(f"Failed to parse CSV: {str(e)}")
    
    def _parse_xml(self) -> pd.DataFrame:
        """
        Parse XML file
        
        Supports two XML structures:
        1. List format:
           <blacklist>
             <entry>
               <name_english>John Doe</name_english>
               <civil_id>123456789012</civil_id>
               ...
             </entry>
           </blacklist>
        
        2. Attribute format:
           <blacklist>
             <entry name_english="John Doe" civil_id="123456789012" ... />
           </blacklist>
        """
        try:
            tree = ET.parse(BytesIO(self.file_bytes))
            root = tree.getroot()
            
            data = []
            
            # Find all entry elements (try common names)
            entries = []
            for tag in ['entry', 'item', 'record', 'person', 'entity']:
                entries = root.findall(f'.//{tag}')
                if entries:
                    break
            
            if not entries:
                raise MultiFormatParserError("No entries found in XML (expected <entry>, <item>, or <record> tags)")
            
            for entry in entries:
                row = {}
                
                # Try to get data from child elements
                for child in entry:
                    tag_name = child.tag.lower().strip()
                    row[tag_name] = child.text
                
                # Try to get data from attributes
                for attr, value in entry.attrib.items():
                    attr_name = attr.lower().strip()
                    if attr_name not in row:  # Don't override child elements
                        row[attr_name] = value
                
                if row:  # Only add if we found some data
                    data.append(row)
            
            if not data:
                raise MultiFormatParserError("No data extracted from XML entries")
            
            df = pd.DataFrame(data)
            return df
            
        except ET.ParseError as e:
            raise MultiFormatParserError(f"Invalid XML format: {str(e)}")
        except Exception as e:
            raise MultiFormatParserError(f"Failed to parse XML: {str(e)}")
    
    def _parse_json(self) -> pd.DataFrame:
        """
        Parse JSON file
        
        Supports two JSON structures:
        1. Array of objects:
           [
             {"name_english": "John Doe", "civil_id": "123456789012", ...},
             {"name_english": "Jane Smith", "civil_id": "234567890123", ...}
           ]
        
        2. Object with array:
           {
             "blacklist": [
               {"name_english": "John Doe", "civil_id": "123456789012", ...},
               ...
             ]
           }
        """
        try:
            data = json.loads(self.file_bytes.decode('utf-8'))
            
            # Handle array format
            if isinstance(data, list):
                df = pd.DataFrame(data)
            
            # Handle object with array format
            elif isinstance(data, dict):
                # Try common array keys
                for key in ['blacklist', 'entries', 'items', 'records', 'data']:
                    if key in data and isinstance(data[key], list):
                        df = pd.DataFrame(data[key])
                        break
                else:
                    # If no array found, try to use the first list value
                    for value in data.values():
                        if isinstance(value, list):
                            df = pd.DataFrame(value)
                            break
                    else:
                        raise MultiFormatParserError("No array found in JSON object")
            else:
                raise MultiFormatParserError("JSON must be an array or object containing an array")
            
            return df
            
        except json.JSONDecodeError as e:
            raise MultiFormatParserError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            raise MultiFormatParserError(f"Failed to parse JSON: {str(e)}")
    
    def _looks_like_header_row(self, row: pd.Series) -> bool:
        """Check if a row looks like a header row"""
        if row.isna().all():
            return False
        
        # Check if row contains common header keywords
        row_str = ' '.join([str(x).lower() for x in row if pd.notna(x)])
        header_keywords = ['name', 'civil', 'passport', 'nationality', 'id', 'الاسم', 'رقم']
        
        return any(keyword in row_str for keyword in header_keywords)
    
    def parse(self) -> Dict[str, Any]:
        """
        Parse file and return structured data
        
        Returns:
            Dictionary with:
            - data: List of parsed records
            - summary: Parsing statistics
            - errors: List of errors encountered
        """
        try:
            # Parse based on format
            if self.format == 'excel':
                df = self._parse_excel()
            elif self.format == 'csv':
                df = self._parse_csv()
            elif self.format == 'xml':
                df = self._parse_xml()
            elif self.format == 'json':
                df = self._parse_json()
            else:
                raise MultiFormatParserError(f"Unsupported format: {self.format}")
            
            # Map columns to standard names
            df = self._map_columns(df)
            
            # Remove empty rows
            df = df.dropna(how='all')
            
            # Parse records
            data = []
            errors = []
            
            for idx, row in df.iterrows():
                try:
                    record = self._parse_row(row, idx)
                    if record:
                        data.append(record)
                except Exception as e:
                    errors.append({
                        'row': idx + 1,
                        'error': str(e)
                    })
            
            # Generate batch ID
            batch_id = f"BATCH_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            return {
                'data': data,
                'summary': {
                    'batch_id': batch_id,
                    'total_rows': len(df),
                    'valid_records': len(data),
                    'errors': len(errors),
                    'format': self.format
                },
                'errors': errors
            }
            
        except Exception as e:
            raise MultiFormatParserError(f"Failed to parse file: {str(e)}")
    
    def _parse_row(self, row: pd.Series, row_num: int) -> Optional[Dict[str, Any]]:
        """Parse a single row into a record"""
        # Skip if all values are empty
        if row.isna().all():
            return None
        
        record = {}
        
        # Extract fields
        for field in ['name_english', 'name_arabic', 'civil_id', 'passport_number', 
                      'nationality', 'source', 'date_added', 'notes']:
            value = row.get(field)
            if pd.notna(value):
                # Clean string values
                if isinstance(value, str):
                    value = value.strip()
                record[field] = value
        
        # Validate: must have at least name_english or name_arabic
        if not record.get('name_english') and not record.get('name_arabic'):
            raise ValueError("Missing both name_english and name_arabic")
        
        # Parse date if provided
        if 'date_added' in record and record['date_added']:
            try:
                if isinstance(record['date_added'], str):
                    record['date_added'] = datetime.strptime(record['date_added'], '%Y-%m-%d').date()
                elif isinstance(record['date_added'], datetime):
                    record['date_added'] = record['date_added'].date()
            except:
                # Keep as string if parsing fails
                pass
        
        # Set default status
        record['status'] = 'active'
        
        return record


def parse_blacklist_file(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Convenience function to parse a blacklist file
    
    Args:
        file_bytes: File content as bytes
        filename: Original filename
        
    Returns:
        Parsed data with summary and errors
    """
    parser = MultiFormatParser(file_bytes, filename)
    return parser.parse()
