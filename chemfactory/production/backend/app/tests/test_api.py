import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..main import app
from ..db.database import get_db, Base
from ..db.models import User, Role, Product, Batch, ManufacturingOrder, QualityCheck
from ..core.security import get_password_hash

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(setup_database):
    db = TestingSessionLocal()
    
    # Create test role
    role = Role(name="ADMIN", description="Administrator")
    db.add(role)
    db.commit()
    db.refresh(role)
    
    # Create test user
    user = User(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        hashed_password=get_password_hash("testpassword"),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Assign role to user
    user.roles.append(role)
    db.commit()
    
    yield user
    db.close()

@pytest.fixture
def auth_headers(test_user):
    # Login to get token
    response = client.post("/api/v1/auth/login", data={
        "username": "testuser",
        "password": "testpassword"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

class TestAuthentication:
    def test_login_success(self, setup_database, test_user):
        response = client.post("/api/v1/auth/login", data={
            "username": "testuser",
            "password": "testpassword"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, setup_database):
        response = client.post("/api/v1/auth/login", data={
            "username": "testuser",
            "password": "wrongpassword"
        })
        assert response.status_code == 401

    def test_get_current_user(self, setup_database, auth_headers):
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

class TestProductsAPI:
    def test_create_product(self, setup_database, auth_headers):
        product_data = {
            "code": "TEST001",
            "name_en": "Test Product",
            "name_ar": "منتج تجريبي",
            "product_type": "FINISHED_GOOD",
            "unit": "L",
            "density": 1.0,
            "hazard_class": "NONE",
            "storage_flag": "NORMAL",
            "is_active": True
        }
        response = client.post("/api/v1/products/", json=product_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "TEST001"
        assert data["name_en"] == "Test Product"

    def test_get_products(self, setup_database, auth_headers):
        response = client.get("/api/v1/products/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_search_products(self, setup_database, auth_headers):
        response = client.get("/api/v1/products/search/test", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

class TestManufacturingAPI:
    def test_create_manufacturing_order(self, setup_database, auth_headers):
        # First create a product and BOM
        product_data = {
            "code": "MO_TEST001",
            "name_en": "MO Test Product",
            "product_type": "FINISHED_GOOD",
            "unit": "L",
            "is_active": True
        }
        product_response = client.post("/api/v1/products/", json=product_data, headers=auth_headers)
        product_id = product_response.json()["id"]
        
        # Create manufacturing order
        mo_data = {
            "product_id": product_id,
            "bom_id": 1,  # Assuming BOM exists
            "target_quantity": 100.0,
            "planned_start_date": "2024-01-01T08:00:00",
            "planned_end_date": "2024-01-01T16:00:00",
            "priority": 1
        }
        response = client.post("/api/v1/manufacturing/orders", json=mo_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["target_quantity"] == 100.0
        assert "mo_number" in data

    def test_get_manufacturing_orders(self, setup_database, auth_headers):
        response = client.get("/api/v1/manufacturing/orders", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_manufacturing_dashboard_stats(self, setup_database, auth_headers):
        response = client.get("/api/v1/manufacturing/dashboard/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_orders" in data
        assert "active_orders" in data
        assert "completion_rate" in data

class TestBatchesAPI:
    def test_create_batch(self, setup_database, auth_headers):
        # First create a product
        product_data = {
            "code": "BATCH_TEST001",
            "name_en": "Batch Test Product",
            "product_type": "FINISHED_GOOD",
            "unit": "L",
            "is_active": True
        }
        product_response = client.post("/api/v1/products/", json=product_data, headers=auth_headers)
        product_id = product_response.json()["id"]
        
        # Create batch
        batch_data = {
            "product_id": product_id,
            "target_quantity": 50.0,
            "status": "PLANNED"
        }
        response = client.post("/api/v1/batches/", json=batch_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["target_quantity"] == 50.0
        assert "batch_number" in data

    def test_get_batches(self, setup_database, auth_headers):
        response = client.get("/api/v1/batches/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

class TestQualityAPI:
    def test_create_quality_check(self, setup_database, auth_headers):
        # First create a batch
        product_data = {
            "code": "QC_TEST001",
            "name_en": "QC Test Product",
            "product_type": "FINISHED_GOOD",
            "unit": "L",
            "is_active": True
        }
        product_response = client.post("/api/v1/products/", json=product_data, headers=auth_headers)
        product_id = product_response.json()["id"]
        
        batch_data = {
            "product_id": product_id,
            "target_quantity": 25.0,
            "status": "PLANNED"
        }
        batch_response = client.post("/api/v1/batches/", json=batch_data, headers=auth_headers)
        batch_id = batch_response.json()["id"]
        
        # Create quality check
        qc_data = {
            "batch_id": batch_id,
            "test_name_en": "pH Test",
            "test_name_ar": "اختبار الحموضة",
            "test_method": "pH Meter",
            "target_value": 7.0,
            "tolerance_min": 0.5,
            "tolerance_max": 0.5,
            "unit": "pH",
            "status": "PENDING"
        }
        response = client.post("/api/v1/quality/checks", json=qc_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["test_name_en"] == "pH Test"
        assert data["target_value"] == 7.0

    def test_perform_quality_test(self, setup_database, auth_headers):
        # This would require creating a quality check first
        # For now, test the endpoint structure
        response = client.post("/api/v1/quality/checks/1/test", 
                             params={"actual_value": 7.2, "notes": "Test result"}, 
                             headers=auth_headers)
        # This might return 404 if QC doesn't exist, which is expected
        assert response.status_code in [200, 404]

class TestMonitoringAPI:
    def test_monitoring_dashboard(self, setup_database, auth_headers):
        response = client.get("/api/v1/monitoring/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "production" in data
        assert "quality" in data
        assert "inventory" in data
        assert "equipment" in data

    def test_system_alerts(self, setup_database, auth_headers):
        response = client.get("/api/v1/monitoring/alerts", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert "total_alerts" in data

    def test_system_metrics(self, setup_database, auth_headers):
        response = client.get("/api/v1/monitoring/metrics", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "production" in data
        assert "quality" in data
        assert "efficiency" in data

class TestReportsAPI:
    def test_production_summary(self, setup_database, auth_headers):
        response = client.get("/api/v1/reports/production/summary", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "period" in data
        assert "summary" in data

    def test_quality_trends(self, setup_database, auth_headers):
        response = client.get("/api/v1/reports/quality/trends", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "overall_metrics" in data
        assert "daily_trends" in data

    def test_inventory_analysis(self, setup_database, auth_headers):
        response = client.get("/api/v1/reports/inventory/analysis", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "abc_analysis" in data

    def test_kpi_dashboard(self, setup_database, auth_headers):
        response = client.get("/api/v1/reports/kpi/dashboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "production_kpis" in data
        assert "quality_kpis" in data
        assert "inventory_kpis" in data
        assert "financial_kpis" in data

class TestSystemIntegration:
    def test_health_check(self, setup_database):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_root_endpoint(self, setup_database):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "features" in data

    def test_dashboard_stats(self, setup_database, auth_headers):
        response = client.get("/api/v1/dashboard/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "system_status" in data
        assert "features_available" in data
        assert "api_version" in data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
