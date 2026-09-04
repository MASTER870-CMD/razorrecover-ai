import hashlib
import hmac
import json
import logging
import os
from typing import Any, Dict, Optional, Tuple
from sqlalchemy.orm import Session

from database.schema.models import WebhookEvent

logger = logging.getLogger(__name__)


class RazorpayWebhookSecurity:
    """
    Handles Razorpay HMAC-SHA256 signature verification and
    strict database-backed event idempotency.
    """

    @staticmethod
    def verify_signature(raw_body: bytes, signature: str, secret: Optional[str] = None) -> bool:
        webhook_secret = secret or os.getenv("RAZORPAY_WEBHOOK_SECRET", "")

        # If secret is not configured in local development, permit simulation
        if not webhook_secret:
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
            logger.error(f"Error computing HMAC-SHA256 signature: {e}")
            return False

    @staticmethod
    def is_duplicate_event(event_id: str, db: Session) -> bool:
        """Checks if a Razorpay event ID was previously processed."""
        if not event_id:
            return False
        existing = db.query(WebhookEvent).filter(WebhookEvent.event_id == event_id).first()
        return existing is not None

    @staticmethod
    def record_processed_event(event_id: str, event_type: str, payload: Dict[str, Any], case_id: Optional[str], db: Session) -> WebhookEvent:
        """Stores event ID to enforce idempotency."""
        event_record = WebhookEvent(
            event_id=event_id,
            event_type=event_type,
            payload=payload,
            case_id=case_id,
        )
        db.add(event_record)
        db.commit()
        return event_record
