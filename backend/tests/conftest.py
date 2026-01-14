"""
Pytest Configuration and Shared Fixtures
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import sys
import os
import httpx
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from database.connection import Base, get_db
from models.auth import User, RefreshToken, UserRole
from utils.auth import hash_password

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


class TestClient:
    """Synchronous test client wrapper using httpx ASGITransport"""
    def __init__(self, app):
        self.app = app
        self.base_url = "http://testserver"
    
    def _run_async(self, coro):
        """Run async coroutine synchronously"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    
    async def _async_request(self, method, url, **kwargs):
        transport = httpx.ASGITransport(app=self.app)
        async with httpx.AsyncClient(transport=transport, base_url=self.base_url) as client:
            if method == "GET":
                return await client.get(url, **kwargs)
            elif method == "POST":
                return await client.post(url, **kwargs)
            elif method == "PUT":
                return await client.put(url, **kwargs)
            elif method == "DELETE":
                return await client.delete(url, **kwargs)
    
    def get(self, url, **kwargs):
        return self._run_async(self._async_request("GET", url, **kwargs))
    
    def post(self, url, **kwargs):
        return self._run_async(self._async_request("POST", url, **kwargs))
    
    def put(self, url, **kwargs):
        return self._run_async(self._async_request("PUT", url, **kwargs))
    
    def delete(self, url, **kwargs):
        return self._run_async(self._async_request("DELETE", url, **kwargs))


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with overridden database dependency"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_users(db_session):
    """Create test users in the database"""
    users_data = [
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
        },
        {
            "username": "admin_test",
            "email": "admin@kamco.com",
            "password": "Admin123",
            "role": UserRole.ADMIN
        },
        {
            "username": "inactive_user",
            "email": "inactive@kamco.com",
            "password": "Inactive123",
            "role": UserRole.SCREENER,
            "is_active": False
        }
    ]
    
    users = {}
    for user_data in users_data:
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=hash_password(user_data["password"]),
            role=user_data["role"],
            is_active=user_data.get("is_active", True)
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Store both user object and plain password for testing
        users[user_data["username"]] = {
            "user": user,
            "password": user_data["password"],
            "username": user_data["username"],
            "email": user_data["email"],
            "role": user_data["role"]
        }
    
    return users


@pytest.fixture(scope="function")
def authenticated_screener(client, test_users):
    """Get authenticated screener with access token"""
    screener = test_users["screener_test"]
    response = client.post(
        "/api/auth/login",
        json={
            "username": screener["username"],
            "password": screener["password"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    return {
        "user": screener["user"],
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "headers": {"Authorization": f"Bearer {data['access_token']}"}
    }


@pytest.fixture(scope="function")
def authenticated_checker(client, test_users):
    """Get authenticated checker with access token"""
    checker = test_users["checker_test"]
    response = client.post(
        "/api/auth/login",
        json={
            "username": checker["username"],
            "password": checker["password"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    return {
        "user": checker["user"],
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "headers": {"Authorization": f"Bearer {data['access_token']}"}
    }


@pytest.fixture(scope="function")
def authenticated_finalizer(client, test_users):
    """Get authenticated finalizer with access token"""
    finalizer = test_users["finalizer_test"]
    response = client.post(
        "/api/auth/login",
        json={
            "username": finalizer["username"],
            "password": finalizer["password"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    return {
        "user": finalizer["user"],
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "headers": {"Authorization": f"Bearer {data['access_token']}"}
    }


@pytest.fixture(scope="function")
def authenticated_admin(client, test_users):
    """Get authenticated admin with access token"""
    admin = test_users["admin_test"]
    response = client.post(
        "/api/auth/login",
        json={
            "username": admin["username"],
            "password": admin["password"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    return {
        "user": admin["user"],
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "headers": {"Authorization": f"Bearer {data['access_token']}"}
    }


@pytest.fixture(scope="function")
def seed_kamco_entities(db_session):
    """Create sample Kamco entities for screening tests"""
    try:
        from models.screening import KamcoEntity
        
        entities_data = [
            {
                "customer_id": "KM001",
                "name_english": "Ahmad Muhammad Al-Hassan",
                "name_arabic": "أحمد محمد الحسن",
                "civil_id": "123456789012",
                "nationality": "Kuwait",
                "entity_type": "CLIENT",
                "entity_category": "Individual"
            },
            {
                "customer_id": "KM002",
                "name_english": "Global Trading Corporation Ltd",
                "name_arabic": "شركة التجارة العالمية",
                "civil_id": "987654321098",
                "nationality": "UAE",
                "entity_type": "VENDOR",
                "entity_category": "Corporate"
            },
            {
                "customer_id": "KM003",
                "name_english": "Mohamed Ali Ibrahim",
                "name_arabic": "محمد علي إبراهيم",
                "civil_id": "456789012345",
                "nationality": "Egypt",
                "entity_type": "STAFF",
                "entity_category": "Individual"
            },
            {
                "customer_id": "KM004",
                "name_english": "Fatima Al-Sabah",
                "name_arabic": "فاطمة الصباح",
                "civil_id": "321654987012",
                "nationality": "Kuwait",
                "entity_type": "CLIENT",
                "entity_category": "Individual"
            },
            {
                "customer_id": "KM005",
                "name_english": "International Finance Partners",
                "name_arabic": "شركاء التمويل الدولي",
                "civil_id": "",
                "nationality": "Saudi Arabia",
                "entity_type": "VENDOR",
                "entity_category": "Corporate"
            }
        ]
        
        entities = []
        for data in entities_data:
            entity = KamcoEntity(**data)
            db_session.add(entity)
            entities.append(entity)
        
        db_session.commit()
        
        # Refresh all entities
        for entity in entities:
            db_session.refresh(entity)
        
        return entities
    except ImportError:
        return []
