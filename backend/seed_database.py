"""
Seed script to populate Kamco database with sample data
Run this once to initialize the database with test data
"""
from database.connection import engine, SessionLocal, init_db
from models.database import KamcoClient, KamcoVendor, KamcoStaff, KamcoOther
from models.auth import User, UserRole
from models.case import Case, CaseNote, CaseStatus, CasePriority, NoteType
from utils.auth import hash_password
from datetime import datetime

def seed_database():
    # Create tables
    print("Creating database tables...")
    init_db()
    print("✅ Tables created")
    
    # Create session
    db = SessionLocal()
    
    try:
        # Clear existing data
        print("\nClearing existing data...")
        db.query(KamcoClient).delete()
        db.query(KamcoVendor).delete()
        db.query(KamcoStaff).delete()
        db.query(KamcoOther).delete()
        # Clear auth tables
        db.query(User).delete()
        db.query(Case).delete()
        db.commit()
        print("✅ Existing data cleared")
        
        # ============================================================
        # SEED AUTHENTICATION USERS
        # ============================================================
        print("\n" + "="*60)
        print("SEEDING AUTHENTICATION USERS")
        print("="*60)
        
        users_data = [
            {
                "username": "admin",
                "email": "admin@kamco.com",
                "password": "Admin123",
                "role": UserRole.ADMIN
            },
            {
                "username": "screener_test",
                "email": "screener@kamco.com",
                "password": "Screener123",
                "role": UserRole.SCREENER
            },
            {
                "username": "checker_test",
                "email": "checker@kamco.com",
                "password": "Checker123",
                "role": UserRole.CHECKER
            },
            {
                "username": "finalizer_test",
                "email": "finalizer@kamco.com",
                "password": "Finalizer123",
                "role": UserRole.FINALIZER
            }
        ]
        
        users = []
        for user_data in users_data:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=hash_password(user_data["password"]),
                role=user_data["role"],
                is_active=True
            )
            db.add(user)
            users.append(user)
        
        db.commit()
        
        for i, user in enumerate(users):
            db.refresh(user)
            print(f"✅ User {i+1}: {user.email} ({user.role.value}) - ID: {user.id}")
        
        print(f"\n📧 Login Credentials:")
        print(f"   Admin:     admin@kamco.com / Admin123 (FULL ACCESS)")
        print(f"   Screener:  screener@kamco.com / Screener123")
        print(f"   Checker:   checker@kamco.com / Checker123")
        print(f"   Finalizer: finalizer@kamco.com / Finalizer123")
        
        # ============================================================
        # SEED TEST CASES
        # ============================================================
        print("\n" + "="*60)
        print("SEEDING TEST CASES")
        print("="*60)
        
        cases_data = [
            {
                "case_number": "CASE-2026-0001",
                "status": CaseStatus.IN_REVIEW,
                "priority": CasePriority.HIGH,
                "title": "High-Risk Client Match - ABC Trading Corp",
                "description": "Potential match found between client and sanctioned entity. Requires immediate review.",
                "created_by": users[0],  # screener
                "assigned_to": users[1]  # checker
            },
            {
                "case_number": "CASE-2026-0002",
                "status": CaseStatus.FLAGGED,
                "priority": CasePriority.MEDIUM,
                "title": "Vendor Screening - XYZ Supplies Ltd",
                "description": "Vendor name partially matches blacklist entry. Actor field requires verification.",
                "created_by": users[0],  # screener
                "assigned_to": users[1]  # checker
            }
        ]
        
        cases = []
        for case_data in cases_data:
            case = Case(
                case_number=case_data["case_number"],
                status=case_data["status"],
                priority=case_data["priority"],
                title=case_data["title"],
                description=case_data["description"],
                created_by_id=case_data["created_by"].id,
                assigned_to_id=case_data["assigned_to"].id if case_data.get("assigned_to") else None
            )
            db.add(case)
            cases.append(case)
        
        db.commit()
        
        for case in cases:
            db.refresh(case)
            print(f"✅ Case: {case.case_number} - {case.title[:50]}...")
        
        # ============================================================
        # SEED CASE NOTES
        # ============================================================
        print("\nSeeding Case Notes...")
        
        notes_data = [
            {
                "case": cases[0],
                "user": users[0],  # screener
                "note": "Initial scan detected 85% name match with sanctioned entity. Actor field shows 'John Smith' which requires verification.",
                "note_type": NoteType.COMMENT
            },
            {
                "case": cases[0],
                "user": users[0],  # screener
                "note": "Status changed from 'open' to 'in_review'",
                "note_type": NoteType.STATUS_CHANGE
            },
            {
                "case": cases[1],
                "user": users[0],  # screener
                "note": "Vendor match score 78%. Source shows 'OFAC Sanctions List'. Flagged for checker review.",
                "note_type": NoteType.COMMENT
            },
            {
                "case": cases[1],
                "user": users[0],  # screener
                "note": "Item flagged and assigned to checker for verification",
                "note_type": NoteType.STATUS_CHANGE
            }
        ]
        
        for note_data in notes_data:
            note = CaseNote(
                case_id=note_data["case"].id,
                user_id=note_data["user"].id,
                note=note_data["note"],
                note_type=note_data["note_type"]
            )
            db.add(note)
        
        db.commit()
        print(f"✅ Added {len(notes_data)} case notes")
        
        # ============================================================
        # SEED KAMCO DATA (existing code continues below)
        # ============================================================
        
        print("\n" + "="*60)
        print("SEEDING KAMCO DATABASE")
        print("="*60)
        
        # Seed Clients
        print("\nSeeding Clients...")
        clients = [
            KamcoClient(
                name="Mohammed Al-Rashid",
                account_number="ACC-2024-001",
                date_opened="2024-01-15",
                actor_name="Ahmed Hassan",
                country="Kuwait",
                notes="VIP Client"
            ),
            KamcoClient(
                name="Sarah Investment Corp",
                account_number="ACC-2024-002",
                date_opened="2024-02-20",
                actor_name="Sarah Johnson",
                country="USA",
                notes="Corporate account"
            ),
            KamcoClient(
                name="Global Trading LLC",
                account_number="ACC-2023-089",
                date_opened="2023-11-05",
                actor_name="David Chen",
                country="Singapore",
                notes="Trading account"
            ),
            KamcoClient(
                name="Abdullah Enterprises",
                account_number="ACC-2024-003",
                date_opened="2024-03-10",
                actor_name="Abdullah Al-Mutairi",
                country="Kuwait",
                notes="Local business"
            ),
            KamcoClient(
                name="European Ventures SA",
                account_number="ACC-2023-055",
                date_opened="2023-08-22",
                actor_name="Maria Garcia",
                country="Spain",
                notes="Investment firm"
            )
        ]
        
        for client in clients:
            db.add(client)
        
        db.commit()
        print(f"✅ Added {len(clients)} clients")
        
        # Seed Vendors
        print("\nSeeding Vendors...")
        vendors = [
            KamcoVendor(
                name="Tech Solutions International",
                vendor_id="VEN-2024-001",
                date_registered="2024-01-10",
                actor_name="John Smith",
                category="IT Services",
                notes="Software provider"
            ),
            KamcoVendor(
                name="Office Supplies Kuwait",
                vendor_id="VEN-2023-045",
                date_registered="2023-05-15",
                actor_name="Fatima Al-Ali",
                category="Office Supplies",
                notes="Regular supplier"
            ),
            KamcoVendor(
                name="Cleaning Services Co",
                vendor_id="VEN-2023-067",
                date_registered="2023-09-01",
                actor_name="Ahmad Mohammed",
                category="Cleaning",
                notes="Facilities management"
            ),
            KamcoVendor(
                name="Security Systems Ltd",
                vendor_id="VEN-2024-005",
                date_registered="2024-02-28",
                actor_name="Robert Brown",
                category="Security",
                notes="Security equipment"
            )
        ]
        
        for vendor in vendors:
            db.add(vendor)
        
        db.commit()
        print(f"✅ Added {len(vendors)} vendors")
        
        # Seed Staff
        print("\nSeeding Staff...")
        staff = [
            KamcoStaff(
                name="Khalid Al-Mansour",
                employee_id="EMP-001",
                department="Finance",
                position="CFO",
                hire_date="2020-01-15",
                notes="Executive team"
            ),
            KamcoStaff(
                name="Lisa Anderson",
                employee_id="EMP-045",
                department="Compliance",
                position="Compliance Officer",
                hire_date="2021-06-10",
                notes="Key compliance role"
            ),
            KamcoStaff(
                name="Omar Khalil",
                employee_id="EMP-089",
                department="IT",
                position="Senior Developer",
                hire_date="2022-03-20",
                notes="Tech team lead"
            ),
            KamcoStaff(
                name="Jennifer Lee",
                employee_id="EMP-102",
                department="HR",
                position="HR Manager",
                hire_date="2021-09-05",
                notes="Human resources"
            ),
            KamcoStaff(
                name="Hassan Ibrahim",
                employee_id="EMP-078",
                department="Operations",
                position="Operations Manager",
                hire_date="2020-11-12",
                notes="Operations lead"
            )
        ]
        
        for staff_member in staff:
            db.add(staff_member)
        
        db.commit()
        print(f"✅ Added {len(staff)} staff members")
        
        # Seed Others
        print("\nSeeding Others...")
        others = [
            KamcoOther(
                name="Annual Audit Firm 2024",
                category="Auditor",
                reference_id="AUD-2024",
                description="External audit services",
                notes="Annual contract"
            ),
            KamcoOther(
                name="Legal Advisors Group",
                category="Legal",
                reference_id="LEG-001",
                description="Legal consultation services",
                notes="Retainer agreement"
            ),
            KamcoOther(
                name="Marketing Agency Kuwait",
                category="Marketing",
                reference_id="MKT-2023",
                description="Brand and marketing services",
                notes="Project-based"
            )
        ]
        
        for other in others:
            db.add(other)
        
        db.commit()
        print(f"✅ Added {len(others)} others")
        
        print("\n" + "="*60)
        print("✅ DATABASE SEEDED SUCCESSFULLY!")
        print("="*60)
        print("\nDatabase Summary:")
        print("  Authentication:")
        print(f"    • Users: {len(users)} (Screener, Checker, Finalizer)")
        print(f"    • Cases: {len(cases)}")
        print(f"    • Case Notes: {len(notes_data)}")
        print("  Kamco Data:")
        print(f"    • Clients: {len(clients)}")
        print(f"    • Vendors: {len(vendors)}")
        print(f"    • Staff: {len(staff)}")
        print(f"    • Others: {len(others)}")
        print(f"    • Total Records: {len(clients) + len(vendors) + len(staff) + len(others)}")
        print("\n📧 Test User Credentials:")
        print("    screener@kamco.com  / Screener123")
        print("    checker@kamco.com   / Checker123")
        print("    finalizer@kamco.com / Finalizer123")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
