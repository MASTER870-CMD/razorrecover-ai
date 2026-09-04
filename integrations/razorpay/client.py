import logging
import os
from typing import Any, Dict, Optional, Tuple
import httpx

logger = logging.getLogger(__name__)

RAZORPAY_API_BASE = "https://api.razorpay.com/v1"


class RazorpayClientWrapper:
    """
    Dedicated Razorpay API Client wrapper for RazorRecover AI.
    Strictly safeguards credentials on the server side and interfaces with
    Razorpay Test Mode APIs.
    """

    def __init__(self):
        self.key_id = os.getenv("RAZORPAY_KEY_ID", "").strip()
        self.key_secret = os.getenv("RAZORPAY_KEY_SECRET", "").strip()
        self.mode = os.getenv("PAYMENT_MODE", "simulator").lower()

    @property
    def has_credentials(self) -> bool:
        return bool(self.key_id and self.key_secret and not self.key_id.startswith("rzp_test_placeholder"))

    @property
    def masked_key_id(self) -> str:
        if not self.key_id:
            return "Not configured"
        if len(self.key_id) <= 8:
            return "rzp_test_••••"
        return f"{self.key_id[:8]}••••{self.key_id[-4:]}"

    def get_auth(self) -> Optional[Tuple[str, str]]:
        if self.has_credentials:
            return (self.key_id, self.key_secret)
        return None

    def test_connection(self) -> Dict[str, Any]:
        """
        Tests connection against Razorpay Test Mode API.
        Attempts authenticated request to /v1/payments?count=1.
        """
        if not self.has_credentials:
            return {
                "connected": False,
                "status": "LOCAL_SIMULATION",
                "message": "No valid Razorpay Test Mode credentials found. Operating in Local Simulation fallback mode.",
                "key_id_masked": self.masked_key_id,
            }

        try:
            with httpx.Client(timeout=8.0) as client:
                res = client.get(
                    f"{RAZORPAY_API_BASE}/payments",
                    params={"count": 1},
                    auth=(self.key_id, self.key_secret),
                )
                if res.status_code == 200:
                    return {
                        "connected": True,
                        "status": "RAZORPAY_TEST_MODE",
                        "message": "Successfully authenticated with Razorpay Test Mode API.",
                        "key_id_masked": self.masked_key_id,
                    }
                else:
                    error_msg = res.json().get("error", {}).get("description", res.text)
                    return {
                        "connected": False,
                        "status": "AUTHENTICATION_FAILED",
                        "message": f"Razorpay API error ({res.status_code}): {error_msg}",
                        "key_id_masked": self.masked_key_id,
                    }
        except Exception as e:
            logger.warning(f"Connection test to Razorpay failed: {e}")
            return {
                "connected": False,
                "status": "NETWORK_OR_TIMEOUT_ERROR",
                "message": f"Could not reach Razorpay API: {str(e)}",
                "key_id_masked": self.masked_key_id,
            }


razorpay_client = RazorpayClientWrapper()
