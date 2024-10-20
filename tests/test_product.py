import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base, engine

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_create_product_success():
    response = client.post("/products", json={"name": "Test Product", "description": "Test Desc", "price": 10.0, "quantity": 100})
    assert response.status_code == 200
    assert response.json()["message"] == "Продукт успешно создан"

def test_create_duplicate_product():
    client.post("/products", json={"name": "Test Product", "description": "Test Desc", "price": 10.0, "quantity": 100})
    response = client.post("/products", json={"name": "Test Product", "description": "Test Desc", "price": 10.0, "quantity": 100})
    assert response.status_code == 400

def test_edit_product_success():
    response = client.post("/products", json={"name": "Test Product", "description": "Test Desc", "price": 10.0, "quantity": 100})
    product_id = response.json().get("id")

    response = client.put(f"/product/{product_id}", json={"name": "Updated Product", "description": "Updated Desc", "price": 15.0, "quantity": 50})
    assert response.status_code == 200

    response = client.get(f"/products/{product_id}")
    assert response.json()["name"] == "Updated Product"

def test_delete_product_success():
    response = client.post("/products", json={"name": "Test Product", "description": "Test Desc", "price": 10.0, "quantity": 100})
    product_id = response.json().get("id")

    response = client.delete(f"/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Продукт успешно удален"

    response = client.get(f"/products/{product_id}")
    assert response.status_code == 404
