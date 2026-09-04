import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Customer(Base):
    __tablename__ = "customers"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    external_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    email = Column(String(200), index=True, nullable=False)
    phone = Column(String(50), nullable=True)
    customer_value = Column(Float, default=0.0)  # LTV in INR
    payment_success_rate = Column(Float, default=1.0)  # 0.0 to 1.0
    created_at = Column(DateTime, default=datetime.utcnow)

    payments = relationship("Payment", back_populates="customer", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="customer", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="customer", cascade="all, delete-orphan")
    recovery_cases = relationship("RecoveryCase", back_populates="customer")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    external_id = Column(String(100), unique=True, index=True, nullable=False)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    amount = Column(Float, nullable=False)  # in INR
    currency = Column(String(10), default="INR")
    status = Column(String(50), index=True, nullable=False)  # PENDING, FAILED, CAPTURED
    payment_method = Column(String(50), default="CARD")  # UPI, CARD, NETBANKING
    failure_reason = Column(String(200), nullable=True)
    failure_code = Column(String(100), nullable=True)
    attempt_count = Column(Integer, default=1)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Customer", back_populates="payments")
    recovery_cases = relationship("RecoveryCase", back_populates="payment")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    plan_name = Column(String(100), default="Professional Plan")
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    status = Column(String(50), default="ACTIVE")
    next_payment_at = Column(DateTime, nullable=True)
    failure_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="subscriptions")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    invoice_number = Column(String(100), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    status = Column(String(50), default="ISSUED")
    due_date = Column(DateTime, nullable=False)
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="invoices")


class RecoveryCase(Base):
    __tablename__ = "recovery_cases"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    payment_id = Column(String(36), ForeignKey("payments.id"), nullable=False)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    risk_score = Column(Float, default=0.0)  # 0 to 100
    risk_level = Column(String(20), default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    recoverability_score = Column(Float, default=0.0)  # 0 to 100
    recommended_action = Column(String(50), nullable=True)
    current_state = Column(String(50), index=True, default="AT_RISK")
    expected_recovery = Column(Float, default=0.0)
    actual_recovery = Column(Float, default=0.0)
    scenario_type = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    payment = relationship("Payment", back_populates="recovery_cases")
    customer = relationship("Customer", back_populates="recovery_cases")
    agent_decisions = relationship("AgentDecision", back_populates="recovery_case", cascade="all, delete-orphan")
    policy_decisions = relationship("PolicyDecision", back_populates="recovery_case", cascade="all, delete-orphan")
    recovery_actions = relationship("RecoveryAction", back_populates="recovery_case", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="recovery_case", cascade="all, delete-orphan")


class AgentDecision(Base):
    __tablename__ = "agent_decisions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("recovery_cases.id"), nullable=False)
    diagnosis = Column(String(500), nullable=False)
    recommendation = Column(String(100), nullable=False)
    confidence = Column(Float, default=1.0)
    reasoning_summary = Column(Text, nullable=False)
    tools_called = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    recovery_case = relationship("RecoveryCase", back_populates="agent_decisions")


class PolicyDecision(Base):
    __tablename__ = "policy_decisions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("recovery_cases.id"), nullable=False)
    action = Column(String(100), nullable=False)
    decision = Column(String(50), nullable=False)  # ALLOW, REQUIRE_HUMAN_APPROVAL, BLOCK
    reason = Column(Text, nullable=False)
    policy_name = Column(String(100), default="STANDARD_FINTECH_GUARDRAIL")
    policy_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    recovery_case = relationship("RecoveryCase", back_populates="policy_decisions")


class RecoveryAction(Base):
    __tablename__ = "recovery_actions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("recovery_cases.id"), nullable=False)
    action_type = Column(String(100), nullable=False)
    status = Column(String(50), default="PENDING")
    amount = Column(Float, nullable=False)
    external_reference = Column(String(200), nullable=True)
    payload = Column(JSON, default=dict)
    executed_at = Column(DateTime, nullable=True)
    verified_at = Column(DateTime, nullable=True)

    recovery_case = relationship("RecoveryCase", back_populates="recovery_actions")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("recovery_cases.id"), nullable=True)
    actor = Column(String(50), nullable=False)  # AGENT, POLICY_ENGINE, HUMAN_OPERATOR, etc.
    event_type = Column(String(100), nullable=False)
    action = Column(String(100), nullable=True)
    decision = Column(String(100), nullable=True)
    previous_state = Column(String(50), nullable=True)
    new_state = Column(String(50), nullable=True)
    amount = Column(Float, nullable=True)
    correlation_id = Column(String(100), default=generate_uuid)
    details = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    recovery_case = relationship("RecoveryCase", back_populates="audit_logs")


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    dataset_size = Column(Integer, default=500)
    revenue_at_risk = Column(Float, default=0.0)
    revenue_recovered = Column(Float, default=0.0)
    recovery_rate = Column(Float, default=0.0)
    baseline_recovery = Column(Float, default=0.0)
    baseline_recovery_rate = Column(Float, default=0.0)
    incremental_recovery = Column(Float, default=0.0)
    correct_decisions = Column(Integer, default=0)
    unsafe_decisions_blocked = Column(Integer, default=0)
    human_escalations = Column(Integer, default=0)
    metrics_breakdown = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    evaluation_cases = relationship("EvaluationCase", back_populates="evaluation_run", cascade="all, delete-orphan")


class EvaluationCase(Base):
    __tablename__ = "evaluation_cases"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    evaluation_run_id = Column(String(36), ForeignKey("evaluation_runs.id"), nullable=False)
    scenario = Column(String(100), nullable=False)
    amount = Column(Float, default=0.0)
    expected_action = Column(String(100), nullable=False)
    actual_action = Column(String(100), nullable=False)
    expected_outcome = Column(String(100), nullable=False)
    actual_outcome = Column(String(100), nullable=False)
    passed = Column(Boolean, default=True)
    reasoning = Column(Text, nullable=True)

    evaluation_run = relationship("EvaluationRun", back_populates="evaluation_cases")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("recovery_cases.id"), nullable=True)
    recipient = Column(String(200), nullable=False)
    channel = Column(String(50), default="EMAIL")  # EMAIL, SMS, WHATSAPP
    status = Column(String(50), default="SENT")
    message = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    strategy_a = Column(String(100), nullable=False)
    strategy_b = Column(String(100), nullable=False)
    attempts_a = Column(Integer, default=0)
    attempts_b = Column(Integer, default=0)
    recovered_a = Column(Float, default=0.0)
    recovered_b = Column(Float, default=0.0)
    recovery_rate_a = Column(Float, default=0.0)
    recovery_rate_b = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(String(36), primary_key=True, default="default")
    automatic_recovery_enabled = Column(Boolean, default=True)
    max_retry_attempts = Column(Integer, default=3)
    max_automatic_amount = Column(Float, default=25000.0)  # INR
    human_approval_threshold = Column(Float, default=0.70)  # Confidence threshold
    recovery_window_days = Column(Integer, default=14)
    max_contact_attempts = Column(Integer, default=2)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    event_id = Column(String(100), unique=True, index=True, nullable=False)
    event_type = Column(String(100), nullable=False)
    payload = Column(JSON, default=dict)
    case_id = Column(String(36), nullable=True)
    processed_at = Column(DateTime, default=datetime.utcnow)


class RazorpaySyncStatus(Base):
    __tablename__ = "razorpay_sync_status"

    id = Column(String(36), primary_key=True, default="default")
    is_connected = Column(Boolean, default=False)
    key_id_masked = Column(String(100), default="None configured")
    mode = Column(String(50), default="LOCAL_SIMULATION")
    last_sync_at = Column(DateTime, nullable=True)
    last_error = Column(String(500), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

