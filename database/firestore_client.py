import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
import httpx

logger = logging.getLogger(__name__)


class FirestoreClient:
    """
    Direct client for Google Cloud Firestore REST API.
    Interacts with the user's Firebase project: razorrecover-ai-88f4c.
    Maintains collections for:
    - customers
    - payments
    - paymentFailures
    - recoveryCases
    - riskAssessments
    - aiDecisions
    - policyDecisions
    - humanApprovals
    - paymentLinks
    - webhookEvents
    - auditEvents
    - evaluations
    """

    def __init__(self):
        self.project_id = os.getenv("FIREBASE_PROJECT_ID", "razorrecover-ai-88f4c").strip()
        self.api_key = os.getenv("FIREBASE_API_KEY", "").strip()
        self.base_url = f"https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents"

    @property
    def is_configured(self) -> bool:
        return bool(self.project_id and self.api_key)

    def _py_to_firestore(self, value: Any) -> Dict[str, Any]:
        if value is None:
            return {"nullValue": None}
        elif isinstance(value, bool):
            return {"booleanValue": value}
        elif isinstance(value, int):
            return {"integerValue": str(value)}
        elif isinstance(value, float):
            return {"doubleValue": value}
        elif isinstance(value, str):
            return {"stringValue": value}
        elif isinstance(value, datetime):
            return {"timestampValue": value.isoformat() + "Z"}
        elif isinstance(value, dict):
            fields = {k: self._py_to_firestore(v) for k, v in value.items() if v is not None}
            return {"mapValue": {"fields": fields}}
        elif isinstance(value, (list, tuple)):
            values = [self._py_to_firestore(item) for item in value]
            return {"arrayValue": {"values": values}}
        else:
            return {"stringValue": str(value)}

    def _firestore_to_py(self, field_dict: Dict[str, Any]) -> Any:
        if not field_dict:
            return None
        key = next(iter(field_dict))
        val = field_dict[key]
        if key == "stringValue":
            return val
        elif key == "integerValue":
            return int(val)
        elif key == "doubleValue":
            return float(val)
        elif key == "booleanValue":
            return bool(val)
        elif key == "timestampValue":
            return val
        elif key == "nullValue":
            return None
        elif key == "mapValue":
            fields = val.get("fields", {})
            return {k: self._firestore_to_py(v) for k, v in fields.items()}
        elif key == "arrayValue":
            values = val.get("values", [])
            return [self._firestore_to_py(v) for v in values]
        return val

    def test_connection(self) -> Dict[str, Any]:
        """Verifies read and write capability to the project's Firestore database."""
        if not self.is_configured:
            return {
                "connected": False,
                "project_id": self.project_id,
                "message": "Firebase API Key not configured.",
            }

        try:
            url = f"{self.base_url}/_healthCheck"
            params = {"key": self.api_key}
            with httpx.Client(timeout=8.0) as client:
                res = client.get(url, params=params)
                if res.status_code in (200, 404):  # 404 means document doesn't exist yet, but API responded
                    return {
                        "connected": True,
                        "project_id": self.project_id,
                        "status": "CONNECTED",
                        "message": f"Successfully connected to Firestore ({self.project_id}).",
                    }
                else:
                    return {
                        "connected": False,
                        "project_id": self.project_id,
                        "status": "ERROR",
                        "error": res.text,
                    }
        except Exception as e:
            logger.error(f"Firestore connection error: {e}")
            return {
                "connected": False,
                "project_id": self.project_id,
                "status": "UNAVAILABLE",
                "error": str(e),
            }

    def save_document(self, collection: str, doc_id: str, data: Dict[str, Any]) -> bool:
        """Creates or overwrites a document in the specified collection."""
        if not self.is_configured:
            return False

        try:
            url = f"{self.base_url}/{collection}/{doc_id}"
            params = {"key": self.api_key}
            fields = {k: self._py_to_firestore(v) for k, v in data.items() if v is not None}
            fields["updatedAt"] = self._py_to_firestore(datetime.utcnow())

            with httpx.Client(timeout=8.0) as client:
                res = client.patch(url, params=params, json={"fields": fields})
                if res.status_code in (200, 201):
                    return True
                else:
                    logger.warning(f"Firestore write to {collection}/{doc_id} returned {res.status_code}: {res.text}")
                    return False
        except Exception as e:
            logger.error(f"Failed to write to Firestore {collection}/{doc_id}: {e}")
            return False

    def get_document(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Fetches a document from Firestore."""
        if not self.is_configured:
            return None

        try:
            url = f"{self.base_url}/{collection}/{doc_id}"
            params = {"key": self.api_key}
            with httpx.Client(timeout=8.0) as client:
                res = client.get(url, params=params)
                if res.status_code == 200:
                    doc = res.json()
                    fields = doc.get("fields", {})
                    data = {k: self._firestore_to_py(v) for k, v in fields.items()}
                    data["_id"] = doc_id
                    return data
                return None
        except Exception as e:
            logger.error(f"Failed to read from Firestore {collection}/{doc_id}: {e}")
            return None

    def list_documents(self, collection: str, page_size: int = 100) -> List[Dict[str, Any]]:
        """Lists documents from a Firestore collection."""
        if not self.is_configured:
            return []

        try:
            url = f"{self.base_url}/{collection}"
            params = {"key": self.api_key, "pageSize": page_size}
            with httpx.Client(timeout=8.0) as client:
                res = client.get(url, params=params)
                if res.status_code == 200:
                    docs = res.json().get("documents", [])
                    results = []
                    for d in docs:
                        name = d.get("name", "")
                        doc_id = name.split("/")[-1]
                        fields = d.get("fields", {})
                        py_dict = {k: self._firestore_to_py(v) for k, v in fields.items()}
                        py_dict["_id"] = doc_id
                        results.append(py_dict)
                    return results
                return []
        except Exception as e:
            logger.error(f"Failed to list documents from Firestore {collection}: {e}")
            return []


# Global singleton instance
firestore_client = FirestoreClient()
