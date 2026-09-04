import logging
from datetime import datetime
from typing import Any, Dict, Optional
from database.firestore_client import firestore_client

logger = logging.getLogger(__name__)


class FirestoreSyncService:
    """
    Synchronizes recovery domain events and entities into Firebase Firestore collections:
    - recoveryCases/{caseId}
    - aiDecisions/{decisionId}
    - policyDecisions/{decisionId}
    - humanApprovals/{approvalId}
    - paymentLinks/{paymentLinkId}
    - webhookEvents/{eventId}
    - auditEvents/{eventId}
    - payments/{paymentId}
    - customers/{customerId}
    """

    @staticmethod
    def sync_case(case_dict: Dict[str, Any]) -> bool:
        case_id = case_dict.get("id")
        if not case_id:
            return False
        return firestore_client.save_document("recoveryCases", case_id, case_dict)

    @staticmethod
    def sync_ai_decision(decision_id: str, data: Dict[str, Any]) -> bool:
        return firestore_client.save_document("aiDecisions", decision_id, data)

    @staticmethod
    def sync_policy_decision(decision_id: str, data: Dict[str, Any]) -> bool:
        return firestore_client.save_document("policyDecisions", decision_id, data)

    @staticmethod
    def sync_human_approval(approval_id: str, data: Dict[str, Any]) -> bool:
        return firestore_client.save_document("humanApprovals", approval_id, data)

    @staticmethod
    def sync_payment_link(link_id: str, data: Dict[str, Any]) -> bool:
        return firestore_client.save_document("paymentLinks", link_id, data)

    @staticmethod
    def sync_webhook_event(event_id: str, data: Dict[str, Any]) -> bool:
        return firestore_client.save_document("webhookEvents", event_id, data)

    @staticmethod
    def sync_audit_event(event_id: str, data: Dict[str, Any]) -> bool:
        return firestore_client.save_document("auditEvents", event_id, data)

    @staticmethod
    def sync_payment(payment_id: str, data: Dict[str, Any]) -> bool:
        return firestore_client.save_document("payments", payment_id, data)

    @staticmethod
    def sync_customer(customer_id: str, data: Dict[str, Any]) -> bool:
        return firestore_client.save_document("customers", customer_id, data)


firestore_sync = FirestoreSyncService()
