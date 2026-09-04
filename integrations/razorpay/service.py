import logging
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from integrations.razorpay.client import razorpay_client
from integrations.razorpay.normalizer import NormalizedEvent, RazorpayEventNormalizer
from integrations.razorpay.payment_links import RazorpayPaymentLinksService
from integrations.razorpay.payments import RazorpayPaymentsService
from integrations.razorpay.webhooks import RazorpayWebhookSecurity

logger = logging.getLogger(__name__)


class RazorpayService:
    """
    Unified Razorpay Service Facade for RazorRecover AI.
    Handles Test Mode API interactions and graceful Local Simulation fallback.
    """

    client = razorpay_client
    payment_links = RazorpayPaymentLinksService
    payments = RazorpayPaymentsService
    webhooks = RazorpayWebhookSecurity
    normalizer = RazorpayEventNormalizer

    @classmethod
    def get_connection_status(cls) -> Dict[str, Any]:
        test_res = cls.client.test_connection()
        return {
            "is_connected": test_res.get("connected", False),
            "status": test_res.get("status"),
            "mode": "RAZORPAY_TEST_MODE" if test_res.get("connected") else "LOCAL_SIMULATION",
            "message": test_res.get("message"),
            "key_id_masked": cls.client.masked_key_id,
        }

    @classmethod
    def create_recovery_payment_link(
        cls,
        amount_inr: float,
        customer_name: str,
        customer_email: str,
        customer_phone: Optional[str] = None,
        description: str = "RazorRecover AI Recovery Link",
        case_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes the supported recovery action: creates a Payment Link
        via Razorpay Test Mode API or local simulator.
        """
        ref = f"case_{case_id[:8]}" if case_id else None
        return cls.payment_links.create_payment_link(
            amount_inr=amount_inr,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            description=description,
            reference_id=ref,
        )

    @classmethod
    def verify_payment_link_completion(cls, payment_link_id: str) -> Dict[str, Any]:
        """
        Verifies whether customer payment on the link was captured.
        """
        return cls.payment_links.fetch_payment_link(payment_link_id)


razorpay_service = RazorpayService()
