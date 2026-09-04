from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class NormalizedEvent:
    event_id: str
    event_type: str
    payment_id: Optional[str]
    payment_link_id: Optional[str]
    amount: float
    currency: str
    status: str
    failure_reason: Optional[str]
    failure_code: Optional[str]
    customer_email: Optional[str]
    customer_name: Optional[str]
    customer_phone: Optional[str]
    payment_method: str
    raw_payload: Dict[str, Any]


class RazorpayEventNormalizer:
    """
    Normalizes diverse Razorpay webhook and API payloads into
    standard internal data contracts.
    """

    @staticmethod
    def normalize(payload: Dict[str, Any]) -> NormalizedEvent:
        event_id = payload.get("event_id") or payload.get("id") or f"evt_norm_{os_random()}"
        event_type = payload.get("event", "payment.failed")

        payload_obj = payload.get("payload", {})
        payment_entity = payload_obj.get("payment", {}).get("entity", {})
        link_entity = payload_obj.get("payment_link", {}).get("entity", {})

        # Amount resolution
        amount_paisa = payment_entity.get("amount") or link_entity.get("amount") or 0
        amount_inr = round(float(amount_paisa) / 100.0, 2) if amount_paisa else 4999.0

        # IDs
        payment_id = payment_entity.get("id")
        payment_link_id = link_entity.get("id")

        # Contact details
        email = payment_entity.get("email") or link_entity.get("customer", {}).get("email") or "customer@example.in"
        contact = payment_entity.get("contact") or link_entity.get("customer", {}).get("contact")
        name = link_entity.get("customer", {}).get("name") or "Razorpay Customer"

        # Failure details
        failure_desc = (
            payment_entity.get("error_description")
            or payment_entity.get("description")
            or "insufficient_funds"
        )
        failure_code = payment_entity.get("error_code") or "GATEWAY_ERROR"
        method = (payment_entity.get("method") or "CARD").upper()
        status = (payment_entity.get("status") or link_entity.get("status") or "failed").upper()

        return NormalizedEvent(
            event_id=event_id,
            event_type=event_type,
            payment_id=payment_id,
            payment_link_id=payment_link_id,
            amount=amount_inr,
            currency=payment_entity.get("currency", "INR"),
            status=status,
            failure_reason=failure_desc,
            failure_code=failure_code,
            customer_email=email,
            customer_name=name,
            customer_phone=contact,
            payment_method=method,
            raw_payload=payload,
        )


def os_random() -> str:
    import uuid
    return uuid.uuid4().hex[:10]
