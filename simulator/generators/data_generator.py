import random
import uuid
from datetime import datetime, timedelta
from typing import List, Tuple
from sqlalchemy.orm import Session

from database.schema.enums import (
    AuditActor,
    AuditEventType,
    PaymentMethod,
    PaymentStatus,
    RecoveryState,
    RiskLevel,
)
from database.schema.models import (
    AuditLog,
    Customer,
    Invoice,
    Payment,
    RecoveryCase,
    Subscription,
)
from simulator.scenarios.definitions import SCENARIO_DEFINITIONS, ScenarioDefinition

FIRST_NAMES = [
    "Aarav", "Pooja", "Vikram", "Neha", "Rohan", "Ananya", "Rahul", "Priya",
    "Siddharth", "Kavita", "Aditya", "Meera", "Karan", "Sneha", "Arjun",
    "Divya", "Gaurav", "Sunita", "Rajesh", "Swati", "Nikhil", "Deepika"
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Reddy", "Mehta", "Iyer", "Nair", "Chopra",
    "Gupta", "Malhotra", "Joshi", "Bose", "Kulkarni", "Deshmukh", "Singh"
]

COMPANY_PREFIXES = [
    "Acme", "Bharat", "Indus", "Apex", "Zenith", "Novus", "Vedic",
    "Bengaluru", "Mumbai", "Deccan", "Urban", "NextGen", "CloudScale"
]

COMPANY_SUFFIXES = [
    "Media", "Tech", "Analytics", "SaaS", "Labs", "Digital", "Solutions",
    "Ventures", "Studio", "Pay", "Commerce", "Networks", "Enterprise"
]


class SimulatorDataGenerator:
    """
    Generates realistic Indian merchant financial entities and failure scenarios
    for RazorRecover AI simulation and evaluation.
    """

    @classmethod
    def generate_customer_name(cls) -> Tuple[str, bool]:
        is_b2b = random.random() < 0.35
        if is_b2b:
            return f"{random.choice(COMPANY_PREFIXES)} {random.choice(COMPANY_SUFFIXES)}", True
        return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}", False

    @classmethod
    def generate_single_case(
        cls,
        db: Session,
        scenario_key: str,
        custom_amount: float = None,
        is_demo: bool = False,
    ) -> RecoveryCase:
        scenario = SCENARIO_DEFINITIONS.get(scenario_key, SCENARIO_DEFINITIONS["insufficient_funds"])

        # 1. Customer profile
        name, is_b2b = cls.generate_customer_name()
        slug = name.lower().replace(" ", ".")
        email = f"{slug}@example.in"
        phone = f"+91 98{random.randint(10000000, 99999999)}"

        # Set realistic customer stats based on scenario
        if scenario_key == "unrecoverable_case":
            success_rate = 0.35
            customer_ltv = 1500.0
        elif scenario_key == "repeated_failure":
            success_rate = 0.55
            customer_ltv = 4000.0
        else:
            success_rate = round(random.uniform(0.85, 0.98), 2)
            customer_ltv = round(random.uniform(8000.0, 75000.0), 2)

        customer = Customer(
            external_id=f"cust_{uuid.uuid4().hex[:12]}",
            name=name,
            email=email,
            phone=phone,
            customer_value=customer_ltv,
            payment_success_rate=success_rate,
        )
        db.add(customer)
        db.flush()

        # 2. Amount calculation
        if custom_amount is not None:
            amount = custom_amount
        else:
            min_amt, max_amt = scenario.typical_amount_range
            amount = round(random.uniform(min_amt, max_amt), 2)

        # 3. Payment creation
        attempt_count = 3 if scenario_key == "repeated_failure" else 1
        payment = Payment(
            external_id=f"pay_{uuid.uuid4().hex[:14]}",
            customer_id=customer.id,
            amount=amount,
            currency="INR",
            status=PaymentStatus.FAILED.value,
            payment_method=scenario.payment_method,
            failure_reason=scenario.failure_reason,
            failure_code=scenario.failure_code,
            attempt_count=attempt_count,
            metadata_json={"scenario": scenario_key, "is_b2b": is_b2b},
        )
        db.add(payment)
        db.flush()

        # 4. Associated Subscription or Invoice if applicable
        if scenario_key == "subscription_failure":
            sub = Subscription(
                customer_id=customer.id,
                plan_name="Enterprise Growth Monthly",
                amount=amount,
                status="HALTED",
                failure_count=1,
            )
            db.add(sub)
        elif scenario_key == "overdue_invoice":
            inv = Invoice(
                customer_id=customer.id,
                invoice_number=f"INV-2026-{random.randint(1000, 9999)}",
                amount=amount,
                status="OVERDUE",
                due_date=datetime.utcnow() - timedelta(days=random.randint(3, 15)),
            )
            db.add(inv)
        db.flush()

        # 5. Recovery Case calculation via deterministic risk engine
        from agent.core.risk_engine import RevenueRiskEngine
        assessment = RevenueRiskEngine.calculate(
            amount=amount,
            failure_reason=scenario.failure_reason,
            attempt_count=attempt_count,
            customer_success_rate=customer.payment_success_rate,
            customer_ltv=customer.customer_value,
            is_subscription=(scenario_key == "subscription_failure"),
        )

        recovery_case = RecoveryCase(
            payment_id=payment.id,
            customer_id=customer.id,
            amount=amount,
            currency="INR",
            risk_score=assessment.risk_score,
            risk_level=assessment.risk_level.value,
            recoverability_score=assessment.recoverability_score,
            expected_recovery=assessment.expected_recovery,
            actual_recovery=0.0,
            recommended_action=None,
            current_state=RecoveryState.AT_RISK.value,
            scenario_type=scenario_key,
        )
        db.add(recovery_case)
        db.flush()

        # 6. Initial Audit Log
        audit = AuditLog(
            case_id=recovery_case.id,
            actor=AuditActor.SIMULATOR.value,
            event_type=AuditEventType.PAYMENT_FAILED.value,
            action="INGEST_PAYMENT_FAILURE",
            decision="FLAGGED_AT_RISK",
            previous_state=None,
            new_state=RecoveryState.AT_RISK.value,
            amount=amount,
            details={
                "scenario": scenario_key,
                "failure_code": scenario.failure_code,
                "risk_score": assessment.risk_score,
                "recoverability_score": assessment.recoverability_score,
            },
        )
        db.add(audit)
        db.commit()

        return recovery_case

    @classmethod
    def generate_batch(cls, db: Session, count: int = 100) -> List[RecoveryCase]:
        scenarios = list(SCENARIO_DEFINITIONS.keys())
        cases = []
        for _ in range(count):
            scenario = random.choice(scenarios)
            case = cls.generate_single_case(db, scenario)
            cases.append(case)
        return cases
