#!/usr/bin/env python3
"""
Database Backup Script
Creates timestamped backups of the SQLite database
"""
import os
import shutil
from datetime import datetime
import gzip

# Configuration
DB_PATH = "database/kamco.db"
BACKUP_DIR = "database/backups"
KEEP_BACKUPS = 10  # Keep last 10 backups

def create_backup():
    """Create a compressed backup of the database"""
    
    # Create backup directory if it doesn't exist
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        return False
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"kamco_backup_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    compressed_path = f"{backup_path}.gz"
    
    try:
        # Copy database file
        print(f"📦 Creating backup: {backup_filename}")
        shutil.copy2(DB_PATH, backup_path)
        
        # Get file size
        size_bytes = os.path.getsize(backup_path)
        size_mb = size_bytes / (1024 * 1024)
        print(f"   Original size: {size_mb:.2f} MB")
        
        # Compress backup
        print(f"   Compressing...")
        with open(backup_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Remove uncompressed version
        os.remove(backup_path)
        
        # Get compressed size
        compressed_size = os.path.getsize(compressed_path)
        compressed_mb = compressed_size / (1024 * 1024)
        compression_ratio = (1 - compressed_size / size_bytes) * 100
        
        print(f"   Compressed size: {compressed_mb:.2f} MB")
        print(f"   Compression: {compression_ratio:.1f}% savings")
        print(f"✅ Backup created: {compressed_path}")
        
        # Cleanup old backups
        cleanup_old_backups()
        
        return True
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

def cleanup_old_backups():
    """Remove old backups keeping only the most recent ones"""
    try:
        # Get all backup files
        backups = []
        for filename in os.listdir(BACKUP_DIR):
            if filename.startswith("kamco_backup_") and filename.endswith(".db.gz"):
                filepath = os.path.join(BACKUP_DIR, filename)
                backups.append((filepath, os.path.getctime(filepath)))
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x[1], reverse=True)
        
        # Remove old backups
        if len(backups) > KEEP_BACKUPS:
            print(f"\n🧹 Cleaning up old backups (keeping {KEEP_BACKUPS} most recent)...")
            for filepath, _ in backups[KEEP_BACKUPS:]:
                print(f"   Removing: {os.path.basename(filepath)}")
                os.remove(filepath)
            print(f"✅ Removed {len(backups) - KEEP_BACKUPS} old backup(s)")
        
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")

def list_backups():
    """List all available backups"""
    if not os.path.exists(BACKUP_DIR):
        print("No backups found.")
        return
    
    backups = []
    for filename in os.listdir(BACKUP_DIR):
        if filename.startswith("kamco_backup_") and filename.endswith(".db.gz"):
            filepath = os.path.join(BACKUP_DIR, filename)
            size = os.path.getsize(filepath) / (1024 * 1024)
            ctime = os.path.getctime(filepath)
            date_str = datetime.fromtimestamp(ctime).strftime("%Y-%m-%d %H:%M:%S")
            backups.append((filename, date_str, size))
    
    if not backups:
        print("No backups found.")
        return
    
    print(f"\n📋 Available Backups ({len(backups)}):")
    print(f"{'Filename':<40} {'Date':<20} {'Size':>10}")
    print("-" * 75)
    for filename, date, size in sorted(backups, key=lambda x: x[1], reverse=True):
        print(f"{filename:<40} {date:<20} {size:>8.2f} MB")

def restore_backup(backup_filename):
    """Restore database from backup"""
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    if not os.path.exists(backup_path):
        print(f"❌ Backup not found: {backup_filename}")
        return False
    
    try:
        # Create backup of current database
        if os.path.exists(DB_PATH):
            print("📦 Backing up current database before restore...")
            create_backup()
        
        # Extract compressed backup
        print(f"📂 Restoring from: {backup_filename}")
        temp_path = DB_PATH + ".restore_temp"
        
        with gzip.open(backup_path, 'rb') as f_in:
            with open(temp_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Replace current database
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        shutil.move(temp_path, DB_PATH)
        
        print(f"✅ Database restored successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Restore failed: {e}")
        # Cleanup temp file if exists
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Kamco Database Backup Utility")
        print("\nUsage:")
        print("  python3 backup_database.py backup          - Create new backup")
        print("  python3 backup_database.py list            - List all backups")
        print("  python3 backup_database.py restore <file>  - Restore from backup")
        print("\nExamples:")
        print("  python3 backup_database.py backup")
        print("  python3 backup_database.py list")
        print("  python3 backup_database.py restore kamco_backup_20260106_120000.db.gz")
        return
    
    command = sys.argv[1].lower()
    
    if command == "backup":
        create_backup()
    elif command == "list":
        list_backups()
    elif command == "restore":
        if len(sys.argv) < 3:
            print("❌ Please specify backup filename to restore")
            print("   Use 'list' command to see available backups")
        else:
            restore_backup(sys.argv[2])
    else:
        print(f"❌ Unknown command: {command}")
        print("   Use: backup, list, or restore")

if __name__ == "__main__":
    main()
