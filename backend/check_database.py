#!/usr/bin/env python3
"""
Database Inspector - View all data stored in the Kamco Fraud Detection system
"""

from database.connection import SessionLocal
from models.database import FlaggedItem, InReviewQueue
from models.auth import User
from models.case import Case, CaseNote, CaseStatus
from models.notification import EmailNotification
from sqlalchemy import inspect
import json
from datetime import datetime

def format_datetime(dt):
    """Format datetime for display"""
    if dt is None:
        return "NULL"
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_table(headers, rows):
    """Print data in table format"""
    if not rows:
        print("  (No data)")
        return
    
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Print header
    header_row = "  " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    print(header_row)
    print("  " + "-" * (len(header_row) - 2))
    
    # Print rows
    for row in rows:
        print("  " + " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)))

def main():
    db = SessionLocal()
    
    try:
        print_section("📊 KAMCO FRAUD DETECTION - DATABASE CONTENTS")
        
        # ========== USERS ==========
        print_section("👥 USERS")
        users = db.query(User).all()
        if users:
            headers = ["ID", "Username", "Email", "Role", "Active", "Last Login", "Created"]
            rows = []
            for user in users:
                rows.append([
                    user.id,
                    user.username,
                    user.email,
                    user.role.value,
                    "Yes" if user.is_active else "No",
                    format_datetime(user.last_login),
                    format_datetime(user.created_at)
                ])
            print_table(headers, rows)
            print(f"\n  Total Users: {len(users)}")
        else:
            print("  (No users registered yet)")
        
        # ========== FLAGGED ITEMS ==========
        print_section("📄 FLAGGED ITEMS (Documents)")
        items = db.query(FlaggedItem).all()
        if items:
            headers = ["ID", "File Name", "Type", "Customer", "Amount", "Risk", "Status", "Case ID"]
            rows = []
            for item in items:
                rows.append([
                    item.id,
                    item.file_name[:30] if item.file_name else "N/A",
                    item.document_type or "N/A",
                    item.customer_name[:20] if item.customer_name else "N/A",
                    f"${item.transaction_amount:,.2f}" if item.transaction_amount else "N/A",
                    f"{item.risk_score:.1f}" if item.risk_score else "0.0",
                    item.status.value if hasattr(item.status, 'value') else item.status,
                    item.case_id or "None"
                ])
            print_table(headers, rows)
            print(f"\n  Total Documents: {len(items)}")
            
            # Show detailed info for first item
            if items:
                item = items[0]
                print("\n  📋 Sample Document Details (ID: 1):")
                print(f"     File Path: {item.file_path}")
                print(f"     Flagged At: {format_datetime(item.flagged_at)}")
                print(f"     Flag Reason: {item.flag_reason[:100] if item.flag_reason else 'None'}...")
                if item.extracted_text:
                    print(f"     Extracted Text: {item.extracted_text[:100]}...")
                print(f"     Screener ID: {item.screener_id or 'Not assigned'}")
                print(f"     Checker ID: {item.checker_id or 'Not assigned'}")
                print(f"     Finalizer ID: {item.finalizer_id or 'Not assigned'}")
        else:
            print("  (No documents uploaded yet)")
        
        # ========== CASES ==========
        print_section("📁 CASES")
        cases = db.query(Case).all()
        if cases:
            headers = ["ID", "Case Number", "Status", "Priority", "Created", "Updated"]
            rows = []
            for case in cases:
                rows.append([
                    case.id,
                    case.case_number,
                    case.status.value if hasattr(case.status, 'value') else case.status,
                    case.priority.value if hasattr(case.priority, 'value') else str(case.priority),
                    format_datetime(case.created_at),
                    format_datetime(case.updated_at)
                ])
            print_table(headers, rows)
            print(f"\n  Total Cases: {len(cases)}")
            
            # Show case details
            for case in cases:
                print(f"\n  📋 Case {case.case_number} Details:")
                print(f"     Title: {case.title or 'N/A'}")
                print(f"     Description: {case.description[:100] if case.description else 'N/A'}...")
                print(f"     Created By: User #{case.created_by_id}" if case.created_by_id else "Unknown")
                print(f"     Assigned To: User #{case.assigned_to_id}" if case.assigned_to_id else "Unassigned")
                print(f"     Closed At: {format_datetime(case.closed_at)}")
        else:
            print("  (No cases created yet)")
        
        # ========== CASE NOTES ==========
        print_section("📝 CASE NOTES")
        notes = db.query(CaseNote).all()
        if notes:
            headers = ["ID", "Case", "User", "Type", "Note Preview", "Created"]
            rows = []
            for note in notes:
                case = db.query(Case).filter(Case.id == note.case_id).first()
                user = db.query(User).filter(User.id == note.user_id).first() if note.user_id else None
                
                rows.append([
                    note.id,
                    case.case_number if case else f"#{note.case_id}",
                    user.username if user else "System",
                    note.note_type.value if hasattr(note.note_type, 'value') else note.note_type,
                    note.note[:40] + "..." if len(note.note) > 40 else note.note,
                    format_datetime(note.created_at)
                ])
            print_table(headers, rows)
            print(f"\n  Total Notes: {len(notes)}")
        else:
            print("  (No case notes yet)")
        
        # ========== REVIEW QUEUE ==========
        print_section("🔄 IN REVIEW QUEUE")
        queue_items = db.query(InReviewQueue).all()
        if queue_items:
            headers = ["ID", "Case#", "Status", "Risk", "Kamco Name", "Match Score", "Created"]
            rows = []
            for q in queue_items:
                case = db.query(Case).filter(Case.id == q.case_id).first() if q.case_id else None
                
                rows.append([
                    q.id,
                    case.case_number if case else "None",
                    q.status or "pending",
                    q.risk_score,
                    q.kamco_name[:30] if q.kamco_name else "N/A",
                    f"{q.match_score:.1f}%" if q.match_score else "0.0%",
                    format_datetime(q.created_at)
                ])
            print_table(headers, rows)
            print(f"\n  Total Queue Items: {len(queue_items)}")
        else:
            print("  (No items in review queue)")
        
        # ========== EMAIL NOTIFICATIONS ==========
        print_section("📧 EMAIL NOTIFICATIONS")
        emails = db.query(EmailNotification).all()
        if emails:
            headers = ["ID", "Case", "Recipient", "Subject", "Status", "Created"]
            rows = []
            for email in emails:
                case = db.query(Case).filter(Case.id == email.case_id).first()
                rows.append([
                    email.id,
                    case.case_number if case else f"#{email.case_id}",
                    email.recipient_email,
                    email.subject[:40] + "..." if len(email.subject) > 40 else email.subject,
                    email.status,
                    format_datetime(email.created_at)
                ])
            print_table(headers, rows)
            print(f"\n  Total Notifications: {len(emails)}")
        else:
            print("  (No email notifications yet)")
        
        # ========== STATISTICS ==========
        print_section("📊 STATISTICS")
        
        # Count by status
        print("\n  Document Status Breakdown:")
        status_counts = {}
        for item in items:
            status = item.status.value if hasattr(item.status, 'value') else item.status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if status_counts:
            for status, count in sorted(status_counts.items()):
                print(f"     {status}: {count}")
        else:
            print("     (No data)")
        
        # Count by role
        print("\n  Users by Role:")
        role_counts = {}
        for user in users:
            role = user.role.value if hasattr(user.role, 'value') else user.role
            role_counts[role] = role_counts.get(role, 0) + 1
        
        if role_counts:
            for role, count in sorted(role_counts.items()):
                print(f"     {role}: {count}")
        else:
            print("     (No data)")
        
        # Case statistics
        print("\n  Case Status Breakdown:")
        case_status_counts = {}
        for case in cases:
            status = case.status.value if hasattr(case.status, 'value') else case.status
            case_status_counts[status] = case_status_counts.get(status, 0) + 1
        
        if case_status_counts:
            for status, count in sorted(case_status_counts.items()):
                print(f"     {status}: {count}")
        else:
            print("     (No data)")
        
        print("\n" + "=" * 80)
        print("  💡 TIP: Use this script anytime to see what's stored in your database!")
        print("  Run: python3 backend/check_database.py")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
