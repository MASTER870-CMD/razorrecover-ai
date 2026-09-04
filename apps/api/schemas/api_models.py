from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CustomerResponse(BaseModel):
    id: str
    external_id: str
    name: str
    email: str
    phone: Optional[str] = None
    customer_value: float
    payment_success_rate: float
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PaymentResponse(BaseModel):
    id: str
    external_id: str
    customer_id: str
    customer_name: Optional[str] = None
    amount: float
    currency: str
    status: str
    payment_method: str
    failure_reason: Optional[str] = None
    failure_code: Optional[str] = None
    attempt_count: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RecoveryCaseResponse(BaseModel):
    id: str
    payment_id: str
    customer_id: str
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    amount: float
    currency: str
    risk_score: float
    risk_level: str
    recoverability_score: float
    recommended_action: Optional[str] = None
    current_state: str
    expected_recovery: float
    actual_recovery: float
    scenario_type: Optional[str] = None
    failure_reason: Optional[str] = None
    payment_method: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AgentDecisionResponse(BaseModel):
    id: str
    case_id: str
    diagnosis: str
    recommendation: str
    confidence: float
    reasoning_summary: str
    tools_called: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PolicyDecisionResponse(BaseModel):
    id: str
    case_id: str
    action: str
    decision: str
    reason: str
    policy_name: str
    policy_metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class RecoveryActionResponse(BaseModel):
    id: str
    case_id: str
    action_type: str
    status: str
    amount: float
    external_reference: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    executed_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AuditLogResponse(BaseModel):
    id: str
    case_id: Optional[str] = None
    actor: str
    event_type: str
    action: Optional[str] = None
    decision: Optional[str] = None
    previous_state: Optional[str] = None
    new_state: Optional[str] = None
    amount: Optional[float] = None
    correlation_id: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DashboardSummaryResponse(BaseModel):
    revenue_at_risk: float
    revenue_recovered: float
    recovery_rate: float
    active_cases: int
    human_review_cases: int
    blocked_actions: int
    total_cases: int
    revenue_at_risk_over_time: List[Dict[str, Any]]
    revenue_recovered_over_time: List[Dict[str, Any]]
    failure_reason_breakdown: List[Dict[str, Any]]
    recovery_action_breakdown: List[Dict[str, Any]]
    risk_level_breakdown: List[Dict[str, Any]]
    data_source: str = "LOCAL_SIMULATION"
    last_sync_at: Optional[str] = None


class EvaluationRunResponse(BaseModel):
    id: str
    dataset_size: int
    revenue_at_risk: float
    revenue_recovered: float
    recovery_rate: float
    baseline_recovery: float
    baseline_recovery_rate: float
    incremental_recovery: float
    correct_decisions: int
    unsafe_decisions_blocked: int
    human_escalations: int
    metrics_breakdown: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SettingsUpdateRequest(BaseModel):
    automatic_recovery_enabled: Optional[bool] = None
    max_retry_attempts: Optional[int] = None
    max_automatic_amount: Optional[float] = None
    human_approval_threshold: Optional[float] = None
    recovery_window_days: Optional[int] = None
    max_contact_attempts: Optional[int] = None
    retry_cooldown_minutes: Optional[int] = None


class GenerateSimulatorRequest(BaseModel):
    count: int = Field(default=100, ge=1, le=1000)
    scenario: Optional[str] = None
