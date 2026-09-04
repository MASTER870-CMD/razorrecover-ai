import hashlib
import hmac
import json
import logging
import os
from typing import Any, Dict, Optional, Tuple
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class NormalizedPaymentEvent(BaseModel):
    event_type: str
    payment_id: str
    order_id: Optional[str] = None
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    amount: float
    currency: str = "INR"
    failure_reason: Optional[str] = None
    failure_code: Optional[str] = None
    payment_method: str = "CARD"
    raw_payload: Dict[str, Any]


class RazorpayWebhookNormalizer:
    """
    Validates Razorpay HMAC-SHA256 webhook signatures and
    normalizes raw payloads into standard internal events.
    """

    @staticmethod
    def verify_signature(raw_body: bytes, signature: str, secret: Optional[str] = None) -> bool:
        webhook_secret = secret or os.getenv("RAZORPAY_WEBHOOK_SECRET")
        if not webhook_secret:
            # In simulator/dev mode without configured secret, allow
            return True

        if not signature:
            return False

        try:
            expected_signature = hmac.new(
                webhook_secret.encode("utf-8"),
                raw_body,
                hashlib.sha256,
            ).hexdigest()
            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            logger.error(f"Error validating webhook signature: {e}")
            return False

    @staticmethod
    def normalize(payload: Dict[str, Any]) -> NormalizedPaymentEvent:
        event = payload.get("event", "payment.failed")
        payload_entity = payload.get("payload", {})
        payment_entity = payload_entity.get("payment", {}).get("entity", {})

        amount_paisa = payment_entity.get("amount", 0)
        amount_inr = round(float(amount_paisa) / 100.0, 2) if amount_paisa else 4999.0

        payment_id = payment_entity.get("id", f"pay_norm_{os.urandom(4).hex()}")
        order_id = payment_entity.get("order_id")

        error_desc = payment_entity.get("error_description") or payment_entity.get("description") or "insufficient_funds"
        error_code = payment_entity.get("error_code") or "BAD_REQUEST_PAYMENT_FAILED"
        method = payment_entity.get("method", "UPI").upper()

        contact = payment_entity.get("contact")
        email = payment_entity.get("email") or "customer@example.in"

        return NormalizedPaymentEvent(
            event_type=event,
            payment_id=payment_id,
            order_id=order_id,
            customer_email=email,
            customer_phone=contact,
            amount=amount_inr,
            currency=payment_entity.get("currency", "INR"),
            failure_reason=error_desc,
            failure_code=error_code,
            payment_method=method,
            raw_payload=payload,
        )
