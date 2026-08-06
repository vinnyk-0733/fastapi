import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import database_models
from main import app, get_db

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

database_models.Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    # Recreate tables and seed default products before each test
    database_models.Base.metadata.drop_all(bind=engine)
    database_models.Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    initial_products = [
        database_models.Product(id=1, name="phone", description="budget phone", price=99.0, quantity=10),
        database_models.Product(id=2, name="laptop", description="gaming laptop", price=999.0, quantity=6),
        database_models.Product(id=3, name="Pen", description="Blue ink pen", price=10.0, quantity=100),
        database_models.Product(id=4, name="table", description="Marble table", price=4000.0, quantity=4),
    ]
    db.add_all(initial_products)
    db.commit()
    db.close()
    yield


def test_greet():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "welcome to fastapi"


def test_get_all_products():
    response = client.get("/products")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 4
    assert data[0]["name"] == "phone"


def test_get_product_by_id_success():
    response = client.get("/products/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "phone"
    assert data["price"] == 99.0


def test_get_product_by_id_not_found():
    response = client.get("/products/999")
    assert response.status_code == 200
    assert response.json() == "Product not found"


def test_add_product():
    new_product = {
        "id": 5,
        "name": "Monitor",
        "description": "4K Ultra HD Display",
        "price": 350.0,
        "quantity": 15,
    }
    response = client.post("/products", json=new_product)
    assert response.status_code == 200
    assert response.json() == new_product

    # Verify it was added
    get_res = client.get("/products/5")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Monitor"


def test_update_product_success():
    updated_payload = {
        "id": 1,
        "name": "phone Pro",
        "description": "Upgraded budget phone",
        "price": 149.99,
        "quantity": 20,
    }
    response = client.put("/products/1", json=updated_payload)
    assert response.status_code == 200
    assert response.json() == "Product updated"

    # Verify update in DB
    get_res = client.get("/products/1")
    assert get_res.json()["name"] == "phone Pro"
    assert get_res.json()["price"] == 149.99


def test_update_product_not_found():
    updated_payload = {
        "id": 999,
        "name": "Nonexistent",
        "description": "Does not exist",
        "price": 0.0,
        "quantity": 0,
    }
    response = client.put("/products/999", json=updated_payload)
    assert response.status_code == 200
    assert response.json() == "Product not found"


def test_delete_product_success():
    response = client.delete("/products/1")
    assert response.status_code == 200
    assert response.json() == "Product deleted"

    # Verify deleted
    get_res = client.get("/products/1")
    assert get_res.json() == "Product not found"


def test_delete_product_not_found():
    response = client.delete("/products/999")
    assert response.status_code == 200
    assert response.json() == "Product not found"
