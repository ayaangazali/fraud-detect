"""
Database Initialization Script
Creates all tables and seeds initial data
"""
import sys
sys.path.insert(0, '.')

from database.connection import engine, Base, SessionLocal
from models.screening import KamcoEntity, BlacklistUpload, ScreeningMatch, DecisionLog
from models.auth import User, RefreshToken
from models.database import KamcoClient, KamcoVendor, KamcoStaff, KamcoOther, FlaggedItem
from data.kamco_entities import get_kamco_entities
from utils.auth import hash_password

def init_database():
    """Initialize all database tables and seed data"""
    print("=" * 60)
    print("DATABASE INITIALIZATION")
    print("=" * 60)
    
    # Create all tables
    print("\n1. Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("   ✅ All tables created")
    
    # List tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"   Tables: {len(tables)} total")
    
    db = SessionLocal()
    
    try:
        # Seed users if not exist
        print("\n2. Seeding users...")
        existing_users = db.query(User).count()
        if existing_users == 0:
            users = [
                User(
                    username="screener_test",
                    email="screener@kamco.com",
                    hashed_password=hash_password("ScreenerPass123!"),
                    role="screener",
                    is_active=True
                ),
                User(
                    username="checker_test",
                    email="checker@kamco.com",
                    hashed_password=hash_password("CheckerPass123!"),
                    role="checker",
                    is_active=True
                ),
                User(
                    username="finalizer_test",
                    email="finalizer@kamco.com",
                    hashed_password=hash_password("FinalizerPass123!"),
                    role="finalizer",
                    is_active=True
                ),
                User(
                    username="admin",
                    email="admin@kamco.com",
                    hashed_password=hash_password("AdminPass123!"),
                    role="finalizer",
                    is_active=True
                )
            ]
            for user in users:
                db.add(user)
            db.commit()
            print(f"   ✅ Created {len(users)} users")
        else:
            print(f"   ✅ Users already exist ({existing_users})")
        
        # Seed KAMCO entities if not exist
        print("\n3. Seeding KAMCO entities...")
        existing_entities = db.query(KamcoEntity).count()
        if existing_entities == 0:
            entities = get_kamco_entities()
            for e in entities:
                entity = KamcoEntity(
                    customer_id=e['id'],
                    entity_type=e['type'],
                    entity_category=e.get('category', 'Individual'),
                    name_english=e['name_english'],
                    name_arabic=e.get('name_arabic'),
                    civil_id=e.get('civil_id'),
                    nationality=e.get('nationality'),
                    risk_level=e.get('risk_level', 'Low')
                )
                db.add(entity)
            db.commit()
            print(f"   ✅ Seeded {len(entities)} KAMCO entities")
        else:
            print(f"   ✅ KAMCO entities already exist ({existing_entities})")
        
        print("\n" + "=" * 60)
        print("✅ DATABASE INITIALIZATION COMPLETE")
        print("=" * 60)
        
        # Summary
        print("\nSummary:")
        print(f"  - Users: {db.query(User).count()}")
        print(f"  - KAMCO Entities: {db.query(KamcoEntity).count()}")
        print(f"  - Blacklist Uploads: {db.query(BlacklistUpload).count()}")
        print(f"  - Screening Matches: {db.query(ScreeningMatch).count()}")
        print(f"  - Decision Logs: {db.query(DecisionLog).count()}")
        
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
