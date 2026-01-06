"""
Seed script to populate Kamco database with sample data
Run this once to initialize the database with test data
"""
from database.connection import engine, SessionLocal, init_db
from models.database import KamcoClient, KamcoVendor, KamcoStaff, KamcoOther

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
        db.commit()
        print("✅ Existing data cleared")
        
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
        
        print("\n" + "="*50)
        print("✅ DATABASE SEEDED SUCCESSFULLY!")
        print("="*50)
        print("\nDatabase Summary:")
        print(f"  • Clients: {len(clients)}")
        print(f"  • Vendors: {len(vendors)}")
        print(f"  • Staff: {len(staff)}")
        print(f"  • Others: {len(others)}")
        print(f"  • Total: {len(clients) + len(vendors) + len(staff) + len(others)}")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
