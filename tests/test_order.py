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

def test_create_order_success():
    client.post("/products", json={"name": "Test Product", "description": "Test Desc", "price": 10.0, "quantity": 100})
    response = client.post("/orders", json={"id": 1, "quantity": 1})
    assert response.status_code == 200
    assert response.json()["message"] == "Заказ успешно создан"
    assert "id" in response.json()

def test_create_order_insufficient_quantity():
    client.post("/products", json={"name": "Test Product", "description": "Test Desc", "price": 10.0, "quantity": 1})
    response = client.post("/orders", json={"id": 1, "quantity": 2})
    assert response.status_code == 400

def test_change_order_status_success():
    client.post("/products", json={"name": "Test Product", "description": "Test Desc", "price": 10.0, "quantity": 100})

    response = client.post("/orders", json={"id": 1, "quantity": 1})
    order_id = response.json().get("id")

    response = client.patch(f"/orders/{order_id}/status", json={"status": "отправлен"})
    assert response.status_code == 200
    assert response.json()["message"] == "Статус обновлен"

    response = client.get(f"/orders/{order_id}")
    order_data = response.json()

    order = order_data[0]
    status = order_data[1]

    assert order["id"] == order_id
    assert status == "отправлен"
