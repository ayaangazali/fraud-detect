#!/usr/bin/env python3
"""
Run Database Migration - Add Phase 3 fields to flagged_items table
"""

import sqlite3
import os
from datetime import datetime

def run_migration():
    db_path = os.path.join(os.path.dirname(__file__), "database/kamco.db")
    
    print("=" * 70)
    print("  DATABASE MIGRATION: Phase 3 Fields")
    print("=" * 70)
    print(f"\nDatabase: {db_path}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    if not os.path.exists(db_path):
        print("❌ Error: Database file not found!")
        print(f"   Expected at: {db_path}")
        return False
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check current schema
        print("📋 Step 1: Checking current schema...")
        cursor.execute("PRAGMA table_info(flagged_items)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"   Current columns: {len(columns)}")
        
        # Fields to add
        new_fields = {
            'checker_assigned_at': 'TIMESTAMP',
            'checker_reviewed_at': 'TIMESTAMP',
            'finalizer_reviewed_at': 'TIMESTAMP',
            'resolution_date': 'TIMESTAMP',
            'checker_notes': 'TEXT',
            'finalizer_notes': 'TEXT',
            'escalation_level': 'VARCHAR(50)'
        }
        
        # Check which fields need to be added
        fields_to_add = {}
        for field, field_type in new_fields.items():
            if field not in columns:
                fields_to_add[field] = field_type
        
        if not fields_to_add:
            print("\n✅ All Phase 3 fields already exist!")
            print("   No migration needed.")
            return True
        
        print(f"\n📝 Step 2: Adding {len(fields_to_add)} new fields...")
        
        # Add each field
        for field, field_type in fields_to_add.items():
            print(f"   Adding: {field} ({field_type})...")
            cursor.execute(f"ALTER TABLE flagged_items ADD COLUMN {field} {field_type}")
        
        # Commit changes
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
        # Verify
        print("\n📋 Step 3: Verifying changes...")
        cursor.execute("PRAGMA table_info(flagged_items)")
        new_columns = [row[1] for row in cursor.fetchall()]
        print(f"   New total columns: {len(new_columns)}")
        
        print("\n✅ Phase 3 fields added:")
        for field in fields_to_add.keys():
            if field in new_columns:
                print(f"   ✓ {field}")
            else:
                print(f"   ✗ {field} (FAILED)")
        
        print("\n" + "=" * 70)
        print("  Migration Complete! You can now use Phase 3 endpoints.")
        print("=" * 70)
        
        return True
        
    except sqlite3.Error as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    success = run_migration()
    exit(0 if success else 1)
