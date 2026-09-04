import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from agent.core.risk_engine import RevenueRiskEngine
from database.schema.enums import (
    ActionExecutionStatus,
    AuditActor,
    AuditEventType,
    PolicyDecisionType,
    RecoveryActionType,
    RecoveryState,
    RiskLevel,
)
from database.schema.models import (
    AgentDecision,
    AuditLog,
    Customer,
    Invoice,
    Notification,
    Payment,
    PolicyDecision,
    RecoveryAction,
    RecoveryCase,
    Subscription,
)


class AgentToolRegistry:
    """
    Controlled Tool Interfaces for the RazorRecover AI Agent.
    Strictly encapsulates database access and ensures controlled execution.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_payment_details(self, payment_id: str) -> Dict[str, Any]:
        """Fetch sanitized payment details for a specific payment ID."""
        payment = self.db.query(Payment).filter((Payment.id == payment_id) | (Payment.external_id == payment_id)).first()
        if not payment:
            return {"error": f"Payment {payment_id} not found"}
        return {
            "payment_id": payment.id,
            "external_id": payment.external_id,
            "customer_id": payment.customer_id,
            "amount": payment.amount,
            "currency": payment.currency,
            "status": payment.status,
            "payment_method": payment.payment_method,
            "failure_reason": payment.failure_reason,
            "failure_code": payment.failure_code,
            "attempt_count": payment.attempt_count,
            "created_at": payment.created_at.isoformat() if payment.created_at else None,
        }

    def get_customer_history(self, customer_id: str) -> Dict[str, Any]:
        """Retrieve aggregated historical payment performance and LTV for a customer."""
        customer = self.db.query(Customer).filter((Customer.id == customer_id) | (Customer.external_id == customer_id)).first()
        if not customer:
            return {"error": f"Customer {customer_id} not found"}

        total_payments = self.db.query(Payment).filter(Payment.customer_id == customer.id).count()
        failed_payments = self.db.query(Payment).filter(Payment.customer_id == customer.id, Payment.status == "FAILED").count()

        return {
            "customer_id": customer.id,
            "external_id": customer.external_id,
            "name": customer.name,
            "email": customer.email,
            "customer_value": customer.customer_value,
            "payment_success_rate": round(customer.payment_success_rate, 2),
            "total_lifetime_payments": total_payments,
            "total_failed_payments": failed_payments,
            "created_at": customer.created_at.isoformat() if customer.created_at else None,
        }

    def get_subscription_details(self, subscription_id: str) -> Dict[str, Any]:
        """Fetch subscription details if recovery involves recurring revenue."""
        sub = self.db.query(Subscription).filter(Subscription.id == subscription_id).first()
        if not sub:
            return {"error": f"Subscription {subscription_id} not found"}
        return {
            "subscription_id": sub.id,
            "customer_id": sub.customer_id,
            "plan_name": sub.plan_name,
            "amount": sub.amount,
            "status": sub.status,
            "failure_count": sub.failure_count,
            "next_payment_at": sub.next_payment_at.isoformat() if sub.next_payment_at else None,
        }

    def get_invoice_details(self, invoice_id: str) -> Dict[str, Any]:
        """Retrieve invoice details for overdue B2B receivables."""
        inv = self.db.query(Invoice).filter((Invoice.id == invoice_id) | (Invoice.invoice_number == invoice_id)).first()
        if not inv:
            return {"error": f"Invoice {invoice_id} not found"}
        return {
            "invoice_id": inv.id,
            "customer_id": inv.customer_id,
            "invoice_number": inv.invoice_number,
            "amount": inv.amount,
            "status": inv.status,
            "due_date": inv.due_date.isoformat() if inv.due_date else None,
            "paid_at": inv.paid_at.isoformat() if inv.paid_at else None,
        }

    def calculate_risk(self, payment_id: str) -> Dict[str, Any]:
        """Invoke deterministic risk scoring engine for a payment."""
        payment = self.db.query(Payment).filter((Payment.id == payment_id) | (Payment.external_id == payment_id)).first()
        if not payment:
            return {"error": f"Payment {payment_id} not found"}
        customer = self.db.query(Customer).filter(Customer.id == payment.customer_id).first()

        assessment = RevenueRiskEngine.calculate(
            amount=payment.amount,
            failure_reason=payment.failure_reason or "unknown",
            attempt_count=payment.attempt_count,
            customer_success_rate=customer.payment_success_rate if customer else 0.85,
            customer_ltv=customer.customer_value if customer else 5000.0,
        )

        return {
            "risk_score": assessment.risk_score,
            "risk_level": assessment.risk_level.value,
            "primary_driver": assessment.primary_risk_driver,
        }

    def calculate_recoverability(self, payment_id: str) -> Dict[str, Any]:
        """Invoke deterministic recoverability scoring engine for a payment."""
        payment = self.db.query(Payment).filter((Payment.id == payment_id) | (Payment.external_id == payment_id)).first()
        if not payment:
            return {"error": f"Payment {payment_id} not found"}
        customer = self.db.query(Customer).filter(Customer.id == payment.customer_id).first()

        assessment = RevenueRiskEngine.calculate(
            amount=payment.amount,
            failure_reason=payment.failure_reason or "unknown",
            attempt_count=payment.attempt_count,
            customer_success_rate=customer.payment_success_rate if customer else 0.85,
            customer_ltv=customer.customer_value if customer else 5000.0,
        )

        return {
            "recoverability_score": assessment.recoverability_score,
            "expected_recovery": assessment.expected_recovery,
            "recommended_baseline_delay_minutes": assessment.recommended_baseline_delay_minutes,
        }

    def classify_failure(self, failure_reason: str, failure_code: Optional[str] = None) -> Dict[str, Any]:
        """Taxonomize payment failure into deterministic categories."""
        reason = (failure_reason or "").lower()
        code = (failure_code or "").lower()

        if "insufficient" in reason or "balance" in reason or "funds" in reason or "bad_request" in code:
            category = "INSUFFICIENT_FUNDS"
            transient = True
            recommended_action = "DELAYED_RETRY"
        elif "bank" in reason or "issuer" in reason or "gateway" in reason or "downtime" in reason:
            category = "TEMPORARY_BANK_FAILURE"
            transient = True
            recommended_action = "DELAYED_RETRY"
        elif "network" in reason or "timeout" in reason:
            category = "NETWORK_ERROR"
            transient = True
            recommended_action = "IMMEDIATE_RETRY"
        elif "auth" in reason or "otp" in reason or "3ds" in reason or "declined_by_user" in reason:
            category = "AUTHENTICATION_FAILURE"
            transient = False
            recommended_action = "PAYMENT_LINK"
        elif "expired" in reason or "validity" in reason:
            category = "EXPIRED_CARD"
            transient = False
            recommended_action = "PAYMENT_LINK"
        elif "abandon" in reason:
            category = "CHECKOUT_ABANDONED"
            transient = False
            recommended_action = "CUSTOMER_NOTIFICATION"
        elif "unrecoverable" in reason or "stolen" in reason or "lost" in reason or "closed" in reason:
            category = "UNRECOVERABLE"
            transient = False
            recommended_action = "STOP_RECOVERY"
        else:
            category = "GENERAL_FAILURE"
            transient = False
            recommended_action = "CUSTOMER_NOTIFICATION"

        return {
            "classified_category": category,
            "is_transient": transient,
            "recommended_action": recommended_action,
        }

    def recommend_recovery_action(
        self,
        case_id: str,
        diagnosis: str,
        risk_level: str,
        recoverability_score: float,
    ) -> Dict[str, Any]:
        """Propose recovery action based on structured factors."""
        rec_score = float(recoverability_score)
        if rec_score < 10.0:
            action = "STOP_RECOVERY"
        elif risk_level == "CRITICAL":
            action = "HUMAN_ESCALATION"
        elif "bank" in diagnosis.lower() or "insufficient" in diagnosis.lower():
            action = "DELAYED_RETRY"
        elif "network" in diagnosis.lower():
            action = "IMMEDIATE_RETRY"
        elif "expired" in diagnosis.lower() or "auth" in diagnosis.lower():
            action = "PAYMENT_LINK"
        else:
            action = "CUSTOMER_NOTIFICATION"

        return {
            "case_id": case_id,
            "recommended_action": action,
            "confidence": 0.92,
        }

    def create_retry_request(self, case_id: str, retry_type: str, delay_minutes: int = 0) -> Dict[str, Any]:
        """Stage a retry execution in the database."""
        case = self.db.query(RecoveryCase).filter(RecoveryCase.id == case_id).first()
        if not case:
            return {"error": f"Case {case_id} not found"}

        action = RecoveryAction(
            case_id=case.id,
            action_type=retry_type,
            status="PENDING",
            amount=case.amount,
            external_reference=f"retry_{uuid.uuid4().hex[:12]}",
            payload={"delay_minutes": delay_minutes, "scheduled_at": (datetime.utcnow() + timedelta(minutes=delay_minutes)).isoformat()},
        )
        self.db.add(action)
        self.db.commit()
        return {
            "action_id": action.id,
            "action_type": retry_type,
            "status": action.status,
            "delay_minutes": delay_minutes,
        }

    def create_payment_link(self, case_id: str, amount: float, expiry_hours: int = 48) -> Dict[str, Any]:
        """Generate a simulated or live Razorpay payment link for customer dunning."""
        case = self.db.query(RecoveryCase).filter(RecoveryCase.id == case_id).first()
        if not case:
            return {"error": f"Case {case_id} not found"}

        link_id = f"plink_{uuid.uuid4().hex[:12]}"
        short_url = f"https://rzp.io/i/{link_id}"
        action = RecoveryAction(
            case_id=case.id,
            action_type="PAYMENT_LINK",
            status="PENDING",
            amount=amount,
            external_reference=link_id,
            payload={"short_url": short_url, "expiry_hours": expiry_hours},
        )
        self.db.add(action)
        self.db.commit()
        return {
            "action_id": action.id,
            "payment_link_id": link_id,
            "short_url": short_url,
            "amount": amount,
        }

    def send_recovery_notification(self, case_id: str, channel: str, message: str) -> Dict[str, Any]:
        """Dispatch customer notification (email / SMS / WhatsApp)."""
        case = self.db.query(RecoveryCase).filter(RecoveryCase.id == case_id).first()
        if not case:
            return {"error": f"Case {case_id} not found"}
        customer = self.db.query(Customer).filter(Customer.id == case.customer_id).first()

        notification = Notification(
            case_id=case.id,
            recipient=customer.email if customer else "customer@example.com",
            channel=channel.upper(),
            status="SENT",
            message=message,
        )
        self.db.add(notification)
        self.db.commit()
        return {
            "notification_id": notification.id,
            "recipient": notification.recipient,
            "channel": notification.channel,
            "status": "SENT",
        }

    def create_human_review(self, case_id: str, reason: str, priority: str = "HIGH") -> Dict[str, Any]:
        """Create a human review record requiring merchant approval."""
        case = self.db.query(RecoveryCase).filter(RecoveryCase.id == case_id).first()
        if not case:
            return {"error": f"Case {case_id} not found"}

        action = RecoveryAction(
            case_id=case.id,
            action_type="HUMAN_ESCALATION",
            status="PENDING",
            amount=case.amount,
            payload={"reason": reason, "priority": priority},
        )
        self.db.add(action)
        self.db.commit()
        return {
            "action_id": action.id,
            "status": "PENDING_APPROVAL",
            "priority": priority,
            "reason": reason,
        }

    def verify_payment_status(self, case_id: str, external_reference: Optional[str] = None) -> Dict[str, Any]:
        """Verify the execution status of a recovery action."""
        case = self.db.query(RecoveryCase).filter(RecoveryCase.id == case_id).first()
        if not case:
            return {"error": f"Case {case_id} not found"}

        # Check last executed action
        action = self.db.query(RecoveryAction).filter(RecoveryAction.case_id == case.id).order_by(RecoveryAction.executed_at.desc()).first()
        status = action.status if action else "UNKNOWN"
        recovered = status == "VERIFIED"
        return {
            "case_id": case_id,
            "verified": recovered,
            "action_status": status,
            "amount_recovered": case.amount if recovered else 0.0,
        }

    def record_audit_event(
        self,
        case_id: str,
        actor: str,
        event_type: str,
        action: Optional[str] = None,
        decision: Optional[str] = None,
        previous_state: Optional[str] = None,
        new_state: Optional[str] = None,
        amount: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Persist an immutable audit log entry."""
        log = AuditLog(
            case_id=case_id,
            actor=actor,
            event_type=event_type,
            action=action,
            decision=decision,
            previous_state=previous_state,
            new_state=new_state,
            amount=amount,
            details=details or {},
        )
        self.db.add(log)
        self.db.commit()
        return {"audit_id": log.id, "created_at": log.created_at.isoformat()}

    def get_recovery_metrics(self) -> Dict[str, Any]:
        """Aggregate high-level recovery metrics from active database."""
        from sqlalchemy import func
        total_risk = self.db.query(func.sum(RecoveryCase.amount)).scalar() or 0.0
        total_recovered = self.db.query(func.sum(RecoveryCase.actual_recovery)).scalar() or 0.0
        total_cases = self.db.query(RecoveryCase).count()
        recovered_cases = self.db.query(RecoveryCase).filter(RecoveryCase.current_state == "RECOVERED").count()
        rate = (recovered_cases / total_cases * 100.0) if total_cases > 0 else 0.0

        return {
            "total_revenue_at_risk": round(total_risk, 2),
            "total_revenue_recovered": round(total_recovered, 2),
            "total_cases": total_cases,
            "recovered_cases": recovered_cases,
            "recovery_rate_percent": round(rate, 2),
        }
