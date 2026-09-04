import os
import sys

# Ensure workspace root is always on sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Set deterministic environment for testing
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("PAYMENT_MODE", "simulator")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_ci.db")
os.environ.setdefault("RAZORPAY_KEY_ID", "rzp_test_placeholder_key")
os.environ.setdefault("RAZORPAY_KEY_SECRET", "placeholder_secret_token")
os.environ.setdefault("RAZORPAY_WEBHOOK_SECRET", "placeholder_webhook_secret")
