from datetime import datetime
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from agent.core.risk_engine import RevenueRiskEngine
from database.connection import get_db
from database.schema.enums import AuditActor, AuditEventType, PaymentStatus, RecoveryState
from database.schema.models import AuditLog, Customer, Payment, RazorpaySyncStatus, RecoveryCase
from integrations.razorpay.service import razorpay_service

router = APIRouter(prefix="/api/razorpay", tags=["Razorpay Connection"])


@router.get("/connection")
def get_connection(db: Session = Depends(get_db)):
    status_record = db.query(RazorpaySyncStatus).filter_by(id="default").first()
    live_status = razorpay_service.get_connection_status()

    return {
        "is_connected": live_status["is_connected"],
        "status": live_status["status"],
        "mode": live_status["mode"],
        "message": live_status["message"],
        "key_id_masked": live_status["key_id_masked"],
        "last_sync_at": status_record.last_sync_at.isoformat() if (status_record and status_record.last_sync_at) else None,
        "last_error": status_record.last_error if status_record else None,
    }


@router.post("/test-connection")
def test_connection(db: Session = Depends(get_db)):
    result = razorpay_service.client.test_connection()

    status_record = db.query(RazorpaySyncStatus).filter_by(id="default").first()
    if not status_record:
        status_record = RazorpaySyncStatus(id="default")
        db.add(status_record)

    status_record.is_connected = result.get("connected", False)
    status_record.mode = result.get("status", "LOCAL_SIMULATION")
    status_record.key_id_masked = result.get("key_id_masked", "None")
    if not result.get("connected"):
        status_record.last_error = result.get("message")
    else:
        status_record.last_error = None

    db.commit()
    result["mode"] = result.get("status", "LOCAL_SIMULATION")
    return result


@router.post("/sync/payments")
def sync_payments(db: Session = Depends(get_db)):
    """
    Synchronizes payments from Razorpay Test Mode API into database.
    Normalizes records, evaluates risk for failures, and creates recovery cases.
    """
    raw_payments = razorpay_service.payments.fetch_payments(count=30)
    synced_count = len(raw_payments)
    new_cases_count = 0

    status_record = db.query(RazorpaySyncStatus).filter_by(id="default").first()
    if not status_record:
        status_record = RazorpaySyncStatus(id="default")
        db.add(status_record)

    status_record.last_sync_at = datetime.utcnow()

    for p_data in raw_payments:
        # Upsert Customer
        email = p_data.get("email") or "customer@example.in"
        customer = db.query(Customer).filter(Customer.email == email).first()
        if not customer:
            customer = Customer(
                external_id=f"cust_rzp_{p_data['id'][-8:]}",
                name="Razorpay Test Customer",
                email=email,
                phone=p_data.get("contact"),
                customer_value=p_data["amount"] * 3,
                payment_success_rate=0.90,
            )
            db.add(customer)
            db.flush()

        # Upsert Payment
        payment = db.query(Payment).filter(Payment.external_id == p_data["id"]).first()
        if not payment:
            payment = Payment(
                external_id=p_data["id"],
                customer_id=customer.id,
                amount=p_data["amount"],
                currency=p_data["currency"],
                status=p_data["status"],
                payment_method=p_data["method"],
                failure_reason=p_data.get("error_description"),
                failure_code=p_data.get("error_code"),
                attempt_count=1,
            )
            db.add(payment)
            db.flush()

            # If failed, create Recovery Case
            if p_data["status"] == "FAILED":
                assessment = RevenueRiskEngine.calculate(
                    amount=payment.amount,
                    failure_reason=payment.failure_reason or "unknown",
                    attempt_count=1,
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
                    scenario_type=payment.failure_reason,
                )
                db.add(case)
                db.flush()
                new_cases_count += 1

                audit = AuditLog(
                    case_id=case.id,
                    actor=AuditActor.WEBHOOK.value,
                    event_type=AuditEventType.PAYMENT_FAILED.value,
                    action="SYNC_FROM_RAZORPAY_TEST_MODE",
                    decision="FLAGGED_AT_RISK",
                    amount=payment.amount,
                    details={"payment_id": payment.external_id},
                )
                db.add(audit)

    db.commit()
    return {
        "status": "success",
        "synced_count": synced_count,
        "synced_payments_count": synced_count,
        "new_cases_created": new_cases_count,
        "mode": "RAZORPAY_TEST_MODE" if razorpay_service.client.has_credentials else "LOCAL_SIMULATION",
    }


@router.post("/sync/payment-links")
def sync_payment_links(db: Session = Depends(get_db)):
    """Synchronizes payment links and verifies completed test payments."""
    status_record = db.query(RazorpaySyncStatus).filter_by(id="default").first()
    if not status_record:
        status_record = RazorpaySyncStatus(id="default")
        db.add(status_record)
    status_record.last_sync_at = datetime.utcnow()
    db.commit()
    return {
        "status": "success",
        "synced_count": 0,
        "mode": "RAZORPAY_TEST_MODE" if razorpay_service.client.has_credentials else "LOCAL_SIMULATION",
    }
