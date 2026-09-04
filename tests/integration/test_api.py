import pytest
from fastapi.testclient import TestClient
from apps.api.main import app
from database.connection import init_db


@pytest.fixture(autouse=True)
def setup_database():
    init_db()


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "RazorRecover AI" in data["service"]


def test_dashboard_endpoint():
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "revenue_at_risk" in data
    assert "revenue_recovered" in data
    assert "recovery_rate" in data
    assert "active_cases" in data


def test_recovery_cases_list():
    response = client.get("/api/recovery-cases")
    assert response.status_code == 200
    cases = response.json()
    assert isinstance(cases, list)


def test_demo_run_full_lifecycle():
    # Trigger 1-Click Demo flow
    response = client.post("/api/simulator/demo/run")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["customer"] == "Acme Media"
    assert data["amount"] == 4999.0
    assert data["recovered_amount"] == 4999.0
    assert data["final_state"] == "RECOVERED"
    assert data["policy_decision"] == "APPROVED"
    assert len(data["timeline"]) == 5


def test_audit_logs_recorded():
    response = client.get("/api/audit")
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) > 0
    actors = {log["actor"] for log in logs}
    assert any(a in actors for a in ["SIMULATOR", "POLICY_ENGINE", "AGENT", "WEBHOOK"])


def test_webhook_ingestion():
    import uuid
    hook_id = f"pay_test_hook_{uuid.uuid4().hex[:8]}"
    payload = {
        "event": "payment.failed",
        "payload": {
            "payment": {
                "entity": {
                    "id": hook_id,
                    "amount": 750000,  # ₹7,500.00
                    "currency": "INR",
                    "method": "card",
                    "description": "insufficient_funds",
                    "error_code": "BAD_REQUEST_PAYMENT_DECLINED",
                    "email": "test.merchant@example.in",
                    "contact": "+919811122233",
                }
            }
        },
    }
    response = client.post("/api/webhooks/razorpay", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "case_id" in data
