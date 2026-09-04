import hashlib
import hmac
import pytest
from database.connection import get_db_session, init_db
from database.schema.models import WebhookEvent
from integrations.razorpay.client import RazorpayClientWrapper
from integrations.razorpay.payment_links import RazorpayPaymentLinksService
from integrations.razorpay.webhooks import RazorpayWebhookSecurity


@pytest.fixture(autouse=True)
def setup_db():
    init_db()


def test_razorpay_client_masking():
    wrapper = RazorpayClientWrapper()
    masked = wrapper.masked_key_id
    assert isinstance(masked, str)
    if wrapper.has_credentials:
        assert "••••" in masked
    else:
        assert masked == "Not configured" or "rzp_test_" in masked


def test_payment_link_generation():
    service = RazorpayPaymentLinksService()
    link = service.create_payment_link(
        amount_inr=1500.0,
        customer_name="Rohan Verma",
        customer_email="rohan@example.com",
        customer_phone="+919876543210",
        description="Invoice recovery for March SaaS",
    )
    assert link["short_url"].startswith("https://rzp.io/") or link["short_url"].startswith("https://api.razorpay.com/")
    assert link["amount"] == 1500.0
    assert link["reference_id"].startswith("rc_link_")
    assert link["payment_link_id"].startswith("plink_")


def test_webhook_signature_verification():
    secret = "rzp_webhook_secret_test_xyz"
    raw_payload = b'{"event":"payment_link.paid","id":"evt_12345"}'
    valid_sig = hmac.new(secret.encode("utf-8"), raw_payload, hashlib.sha256).hexdigest()

    # Valid signature
    assert RazorpayWebhookSecurity.verify_signature(raw_payload, valid_sig, secret) is True

    # Tampered body
    tampered_body = b'{"event":"payment_link.paid","id":"evt_99999"}'
    assert RazorpayWebhookSecurity.verify_signature(tampered_body, valid_sig, secret) is False

    # Invalid signature
    assert RazorpayWebhookSecurity.verify_signature(raw_payload, "invalid_sig_abc", secret) is False


def test_webhook_idempotency_enforcement():
    import uuid
    with get_db_session() as db:
        event_id = f"evt_test_{uuid.uuid4().hex[:12]}"
        # First check: not processed
        assert RazorpayWebhookSecurity.is_duplicate_event(event_id, db) is False

        # Record event
        RazorpayWebhookSecurity.record_processed_event(
            event_id=event_id,
            event_type="payment.captured",
            payload={"id": event_id},
            case_id=None,
            db=db,
        )

        # Second check: now it IS processed
        assert RazorpayWebhookSecurity.is_duplicate_event(event_id, db) is True
