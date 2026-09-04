from datetime import datetime
from sqlalchemy.orm import Session

from agent.core.risk_engine import RevenueRiskEngine
from database.schema.enums import (
    AuditActor,
    AuditEventType,
    PaymentMethod,
    PaymentStatus,
    RecoveryActionType,
    RecoveryState,
    RiskLevel,
)
from database.schema.models import (
    AuditLog,
    Customer,
    Payment,
    RecoveryAction,
    RecoveryCase,
)


def seed_demo_case(db: Session) -> RecoveryCase:
    """
    Seeds the exact Acme Media demo case as specified:
    - Customer: Acme Media
    - Payment: ₹4,999
    - Status: FAILED
    - Failure: INSUFFICIENT_FUNDS
    - History: Strong payment history (96%)
    - Initial State: AT_RISK
    """
    # Check if existing Acme Media demo case exists
    existing = (
        db.query(RecoveryCase)
        .join(Customer)
        .filter(Customer.name == "Acme Media", RecoveryCase.amount == 4999.0)
        .first()
    )
    if existing:
        return existing

    customer = Customer(
        external_id="cust_acme_media_demo_01",
        name="Acme Media",
        email="billing@acmemedia.in",
        phone="+91 9820012345",
        customer_value=48500.0,
        payment_success_rate=0.96,
    )
    db.add(customer)
    db.flush()

    payment = Payment(
        external_id="pay_demo_acme_4999",
        customer_id=customer.id,
        amount=4999.0,
        currency="INR",
        status=PaymentStatus.FAILED.value,
        payment_method=PaymentMethod.UPI.value,
        failure_reason="insufficient_funds",
        failure_code="BAD_REQUEST_PAYMENT_DECLINED_BY_BANK",
        attempt_count=1,
        metadata_json={"product": "SaaS Annual Subscription", "channel": "Web Checkout"},
    )
    db.add(payment)
    db.flush()

    assessment = RevenueRiskEngine.calculate(
        amount=4999.0,
        failure_reason="insufficient_funds",
        attempt_count=1,
        customer_success_rate=customer.payment_success_rate,
        customer_ltv=customer.customer_value,
        is_subscription=True,
    )

    case = RecoveryCase(
        payment_id=payment.id,
        customer_id=customer.id,
        amount=4999.0,
        currency="INR",
        risk_score=assessment.risk_score,
        risk_level=assessment.risk_level.value,
        recoverability_score=assessment.recoverability_score,
        expected_recovery=assessment.expected_recovery,
        actual_recovery=0.0,
        recommended_action=RecoveryActionType.DELAYED_RETRY.value,
        current_state=RecoveryState.AT_RISK.value,
        scenario_type="insufficient_funds",
    )
    db.add(case)
    db.flush()

    # Initial Audit Entry
    audit = AuditLog(
        case_id=case.id,
        actor=AuditActor.WEBHOOK.value,
        event_type=AuditEventType.PAYMENT_FAILED.value,
        action="RECEIVE_PAYMENT_FAILED_EVENT",
        decision="FLAG_REVENUE_AT_RISK",
        previous_state=None,
        new_state=RecoveryState.AT_RISK.value,
        amount=4999.0,
        details={
            "customer": "Acme Media",
            "failure_reason": "insufficient_funds",
            "risk_score": assessment.risk_score,
            "recoverability_score": assessment.recoverability_score,
        },
    )
    db.add(audit)
    db.commit()

    return case
