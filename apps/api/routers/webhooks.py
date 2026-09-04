import json
import logging
import uuid
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from agent.core.risk_engine import RevenueRiskEngine
from database.connection import get_db
from database.schema.enums import (
    ActionExecutionStatus,
    AuditActor,
    AuditEventType,
    PaymentStatus,
    RecoveryState,
)
from database.schema.models import AuditLog, Customer, Payment, RecoveryAction, RecoveryCase
from database.firestore_sync import firestore_sync
from integrations.razorpay.service import razorpay_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])


@router.post("/razorpay")
async def handle_razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(None),
    db: Session = Depends(get_db),
):
    """
    Razorpay Webhook receiver with HMAC-SHA256 signature verification,
    strict event idempotency, and automated recovery state updates.
    """
    body_bytes = await request.body()

    # 1. Validate HMAC signature on raw body
    if x_razorpay_signature:
        is_valid = razorpay_service.webhooks.verify_signature(body_bytes, x_razorpay_signature)
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid webhook signature")

    try:
        payload = json.loads(body_bytes.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Malformed JSON webhook payload")

    # 2. Normalize payload
    normalized = razorpay_service.normalizer.normalize(payload)
    event_id = normalized.event_id
    logger.info(f"Received Razorpay webhook event {normalized.event_type} [EventID: {event_id}]")

    # 3. Check Idempotency
    if razorpay_service.webhooks.is_duplicate_event(event_id, db):
        logger.warning(f"Duplicate event {event_id} received. Rejecting duplicate execution.")
        return {"status": "ignored_duplicate", "event_id": event_id}

    case_id_associated = None

    # 4. Handle Payment Link Paid or Payment Captured Event (Recovery Succeeded)
    if normalized.event_type in ["payment_link.paid", "payment.captured"]:
        # Match case via payment_link_id or payment_id
        action = None
        if normalized.payment_link_id:
            action = db.query(RecoveryAction).filter(RecoveryAction.external_reference == normalized.payment_link_id).first()

        case = None
        if action:
            case = db.query(RecoveryCase).filter(RecoveryCase.id == action.case_id).first()
        elif normalized.payment_id:
            payment = db.query(Payment).filter(Payment.external_id == normalized.payment_id).first()
            if payment:
                case = db.query(RecoveryCase).filter(RecoveryCase.payment_id == payment.id).first()

        if case:
            case_id_associated = case.id
            previous_state = case.current_state
            case.current_state = RecoveryState.RECOVERED.value
            case.actual_recovery = case.amount

            if action:
                action.status = ActionExecutionStatus.VERIFIED.value

            payment_record = db.query(Payment).filter(Payment.id == case.payment_id).first()
            if payment_record:
                payment_record.status = PaymentStatus.CAPTURED.value

            audit = AuditLog(
                case_id=case.id,
                actor=AuditActor.WEBHOOK.value,
                event_type=AuditEventType.RECOVERY_SUCCESS.value,
                action="WEBHOOK_VERIFY_CAPTURE",
                decision="RECOVERED",
                previous_state=previous_state,
                new_state=RecoveryState.RECOVERED.value,
                amount=case.actual_recovery,
                details={
                    "event_id": event_id,
                    "event_type": normalized.event_type,
                    "payment_link_id": normalized.payment_link_id,
                    "payment_id": normalized.payment_id,
                },
            )
            db.add(audit)
            firestore_sync.sync_case({
                "id": case.id,
                "currentState": case.current_state,
                "actualRecovery": case.actual_recovery,
            })

    # 5. Handle Payment Failed Event (New Revenue at Risk)
    elif normalized.event_type == "payment.failed":
        email = normalized.customer_email or "guest@example.in"
        customer = db.query(Customer).filter(Customer.email == email).first()
        if not customer:
            customer = Customer(
                external_id=f"cust_{uuid.uuid4().hex[:10]}",
                name=normalized.customer_name or "Razorpay Customer",
                email=email,
                phone=normalized.customer_phone,
                customer_value=5000.0,
                payment_success_rate=0.90,
            )
            db.add(customer)
            db.flush()

        payment = db.query(Payment).filter(Payment.external_id == normalized.payment_id).first()
        if not payment:
            payment = Payment(
                external_id=normalized.payment_id,
                customer_id=customer.id,
                amount=normalized.amount,
                currency=normalized.currency,
                status=PaymentStatus.FAILED.value,
                payment_method=normalized.payment_method,
                failure_reason=normalized.failure_reason,
                failure_code=normalized.failure_code,
                attempt_count=1,
                metadata_json=payload,
            )
            db.add(payment)
            db.flush()

        existing_case = db.query(RecoveryCase).filter(RecoveryCase.payment_id == payment.id).first()
        if not existing_case:
            assessment = RevenueRiskEngine.calculate(
                amount=payment.amount,
                failure_reason=payment.failure_reason or "unknown",
                attempt_count=payment.attempt_count,
                customer_success_rate=customer.payment_success_rate,
                customer_ltv=customer.customer_value,
            )
            case = RecoveryCase(
                payment_id=payment.id,
                customer_id=customer.id,
                amount=payment.amount,
                currency=payment.currency,
                risk_score=assessment.risk_score,
                risk_level=assessment.risk_level.value,
                recoverability_score=assessment.recoverability_score,
                expected_recovery=assessment.expected_recovery,
                actual_recovery=0.0,
                current_state=RecoveryState.AT_RISK.value,
                recommended_action="PAYMENT_LINK",
                scenario_type=payment.failure_reason,
            )
            db.add(case)
            db.flush()
            case_id_associated = case.id

            audit = AuditLog(
                case_id=case.id,
                actor=AuditActor.WEBHOOK.value,
                event_type=AuditEventType.PAYMENT_FAILED.value,
                action="INGEST_RAZORPAY_WEBHOOK",
                decision="FLAGGED_AT_RISK",
                previous_state=None,
                new_state=RecoveryState.AT_RISK.value,
                amount=case.amount,
                details={
                    "event_id": event_id,
                    "failure_code": normalized.failure_code,
                    "risk_score": assessment.risk_score,
                },
            )
            db.add(audit)

    # 6. Record event for idempotency
    razorpay_service.webhooks.record_processed_event(
        event_id=event_id,
        event_type=normalized.event_type,
        payload=payload,
        case_id=case_id_associated,
        db=db,
    )
    firestore_sync.sync_webhook_event(event_id, {
        "eventId": event_id,
        "eventType": normalized.event_type,
        "caseId": case_id_associated,
        "paymentId": normalized.payment_id,
        "paymentLinkId": normalized.payment_link_id,
        "status": "PROCESSED",
    })
    db.commit()

    return {
        "status": "success",
        "event_id": event_id,
        "event_type": normalized.event_type,
        "case_id": case_id_associated,
    }
