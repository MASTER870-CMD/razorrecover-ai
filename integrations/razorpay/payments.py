import logging
from typing import Any, Dict, List, Optional
import httpx

from integrations.razorpay.client import RAZORPAY_API_BASE, razorpay_client

logger = logging.getLogger(__name__)


class RazorpayPaymentsService:
    """
    Dedicated Razorpay Payments sync service.
    Pulls real payment records from Razorpay Test Mode API.
    """

    @staticmethod
    def fetch_payments(count: int = 25) -> List[Dict[str, Any]]:
        if not razorpay_client.has_credentials:
            return []

        try:
            auth = razorpay_client.get_auth()
            with httpx.Client(timeout=10.0) as client:
                res = client.get(
                    f"{RAZORPAY_API_BASE}/payments",
                    params={"count": count},
                    auth=auth,
                )
                if res.status_code == 200:
                    items = res.json().get("items", [])
                    normalized = []
                    for item in items:
                        normalized.append({
                            "id": item.get("id"),
                            "amount": float(item.get("amount", 0)) / 100.0,
                            "currency": item.get("currency", "INR"),
                            "status": item.get("status", "failed").upper(),
                            "method": item.get("method", "card").upper(),
                            "email": item.get("email"),
                            "contact": item.get("contact"),
                            "error_code": item.get("error_code"),
                            "error_description": item.get("error_description"),
                            "created_at": item.get("created_at"),
                        })
                    return normalized
                else:
                    logger.warning(f"Failed to fetch payments from Razorpay: {res.text}")
                    return []
        except Exception as e:
            logger.error(f"Error connecting to Razorpay payments API: {e}")
            return []

    @staticmethod
    def fetch_payment(payment_id: str) -> Optional[Dict[str, Any]]:
        if not razorpay_client.has_credentials:
            return None

        try:
            auth = razorpay_client.get_auth()
            with httpx.Client(timeout=8.0) as client:
                res = client.get(f"{RAZORPAY_API_BASE}/payments/{payment_id}", auth=auth)
                if res.status_code == 200:
                    item = res.json()
                    return {
                        "id": item.get("id"),
                        "amount": float(item.get("amount", 0)) / 100.0,
                        "currency": item.get("currency", "INR"),
                        "status": item.get("status", "").upper(),
                        "captured": item.get("status") == "captured",
                        "method": item.get("method", "card").upper(),
                        "email": item.get("email"),
                        "error_description": item.get("error_description"),
                    }
        except Exception as e:
            logger.error(f"Error fetching payment {payment_id} from Razorpay: {e}")
        return None
