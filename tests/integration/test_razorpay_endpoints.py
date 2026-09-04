import pytest
from fastapi.testclient import TestClient
from apps.api.main import app
from database.connection import init_db


@pytest.fixture(autouse=True)
def setup_db():
    init_db()


client = TestClient(app)


def test_get_razorpay_connection():
    response = client.get("/api/razorpay/connection")
    assert response.status_code == 200
    data = response.json()
    assert "is_connected" in data
    assert "mode" in data
    assert "key_id_masked" in data
    assert "secret" not in data  # Never expose secret!


def test_test_razorpay_connection():
    response = client.post("/api/razorpay/test-connection")
    assert response.status_code == 200
    data = response.json()
    assert "connected" in data
    assert "mode" in data


def test_sync_razorpay_payments():
    response = client.post("/api/razorpay/sync/payments")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "synced_count" in data


def test_sync_razorpay_payment_links():
    response = client.post("/api/razorpay/sync/payment-links")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "synced_count" in data
