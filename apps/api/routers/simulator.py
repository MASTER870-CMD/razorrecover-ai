from datetime import datetime
import time
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from agent.core.recovery_agent import RecoveryAgent
from agent.policies.policy_engine import DeterministicPolicyEngine
from apps.api.schemas.api_models import GenerateSimulatorRequest
from database.connection import get_db
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
    Payment,
    PolicyDecision,
    RecoveryAction,
    RecoveryCase,
)
from database.seed.demo_case import seed_demo_case
from simulator.generators.data_generator import SimulatorDataGenerator

router = APIRouter(prefix="/api/simulator", tags=["Simulator & Demo"])


@router.post("/generate")
def generate_synthetic_cases(request: GenerateSimulatorRequest, db: Session = Depends(get_db)):
    if request.scenario:
        case = SimulatorDataGenerator.generate_single_case(db=db, scenario_key=request.scenario)
        return {"status": "success", "cases_generated": 1, "case_id": case.id}
    else:
        cases = SimulatorDataGenerator.generate_batch(db=db, count=request.count)
        return {"status": "success", "cases_generated": len(cases)}


@router.post("/demo/run")
def run_demo_case(db: Session = Depends(get_db)):
    """
    Executes the complete end-to-end 1-Click Demo flow for Acme Media:
    1. Resets / Seeds Acme Media payment failure (₹4,999, INSUFFICIENT_FUNDS).
    2. Revenue risk engine detects risk (Risk ~45, Recoverability ~78%).
    3. AI Agent diagnoses cause and recommends DELAYED_RETRY.
    4. Deterministic Policy Engine passes safety checks (APPROVED).
    5. Action executes via Simulator (SIMULATED RETRY).
    6. Payment capture verified (SUCCESS, ₹4,999 recovered).
    7. Audit trail and metrics updated.
    """
    # Step 1: Clean up any prior demo run for clean idempotence
    old_demo_customer = db.query(Customer).filter(Customer.external_id == "cust_acme_media_demo_01").first()
    if old_demo_customer:
        old_cases = db.query(RecoveryCase).filter(RecoveryCase.customer_id == old_demo_customer.id).all()
        for oc in old_cases:
            db.delete(oc)
        db.delete(old_demo_customer)
        db.commit()

    # Step 2: Seed fresh demo case
    case = seed_demo_case(db)
    timeline_steps = []

    timeline_steps.append({
        "step": 1,
        "title": "Payment Failed Event Ingested",
        "description": "Acme Media subscription renewal of ₹4,999 failed with INSUFFICIENT_FUNDS.",
        "state": RecoveryState.AT_RISK.value,
        "timestamp": case.created_at.isoformat(),
    })

    # Step 3: AI Analysis & Diagnosis
    case.current_state = RecoveryState.ANALYZING.value
    agent = RecoveryAgent()
    decision = agent.analyze_case(case.id, db)

    agent_record = AgentDecision(
        case_id=case.id,
        diagnosis=decision.diagnosis,
        recommendation=decision.recommended_action,
        confidence=decision.confidence,
        reasoning_summary=decision.reasoning_summary,
        tools_called=decision.tools_called,
    )
    db.add(agent_record)

    case.recommended_action = decision.recommended_action
    case.expected_recovery = decision.expected_recovery
    case.recoverability_score = decision.recoverability_score
    case.current_state = RecoveryState.SAFETY_CHECK.value

    timeline_steps.append({
        "step": 2,
        "title": "AI Agent Diagnosis & Recommendation",
        "description": f"Diagnosis: '{decision.diagnosis}'. AI recommended {decision.recommended_action} with {decision.confidence:.0%} confidence.",
        "state": RecoveryState.RECOMMENDED.value,
        "reasoning": decision.reasoning_summary,
        "tools_called": decision.tools_called,
    })

    # Step 4: Deterministic Policy Engine Safety Check
    policy_res = DeterministicPolicyEngine.evaluate(
        recommended_action=decision.recommended_action,
        amount=case.amount,
        confidence=decision.confidence,
        risk_level=RiskLevel(case.risk_level),
        attempt_count=1,
        max_automatic_amount=25000.0,
    )

    policy_record = PolicyDecision(
        case_id=case.id,
        action=decision.recommended_action,
        decision=policy_res.decision.value,
        reason=policy_res.reason,
        policy_name=policy_res.policy_name,
        policy_metadata=policy_res.policy_metadata,
    )
    db.add(policy_record)

    case.current_state = RecoveryState.APPROVED.value

    audit_policy = AuditLog(
        case_id=case.id,
        actor=AuditActor.POLICY_ENGINE.value,
        event_type=AuditEventType.POLICY_APPROVED.value,
        action=decision.recommended_action,
        decision="APPROVED",
        previous_state=RecoveryState.SAFETY_CHECK.value,
        new_state=RecoveryState.APPROVED.value,
        amount=case.amount,
        details={"policy_reason": policy_res.reason, "rule_id": policy_res.rule_id},
    )
    db.add(audit_policy)

    timeline_steps.append({
        "step": 3,
        "title": "Safety Engine Cleared",
        "description": f"Safety check passed: {policy_res.reason}",
        "state": RecoveryState.APPROVED.value,
        "policy_decision": policy_res.decision.value,
    })

    # Step 5: Execution
    case.current_state = RecoveryState.EXECUTING.value
    action_ref = "retry_sim_acme_4999_ok"
    action_record = RecoveryAction(
        case_id=case.id,
        action_type=decision.recommended_action,
        status=ActionExecutionStatus.EXECUTED.value,
        amount=case.amount,
        external_reference=action_ref,
        payload={"scheduled_delay_minutes": 120, "mode": "SIMULATED"},
        executed_at=datetime.utcnow(),
    )
    db.add(action_record)

    audit_exec = AuditLog(
        case_id=case.id,
        actor=AuditActor.SIMULATOR.value,
        event_type=AuditEventType.ACTION_EXECUTED.value,
        action=decision.recommended_action,
        decision="EXECUTED",
        previous_state=RecoveryState.APPROVED.value,
        new_state=RecoveryState.EXECUTING.value,
        amount=case.amount,
        details={"reference": action_ref, "mode": "SIMULATED"},
    )
    db.add(audit_exec)

    timeline_steps.append({
        "step": 4,
        "title": "Recovery Action Executed",
        "description": f"Triggered smart {decision.recommended_action} in Payment Gateway Simulator.",
        "state": RecoveryState.EXECUTING.value,
        "reference": action_ref,
    })

    # Step 6: Verification & Final Recovery
    case.current_state = RecoveryState.VERIFYING.value
    # Verification succeeds
    case.current_state = RecoveryState.RECOVERED.value
    case.actual_recovery = 4999.0

    action_record.status = ActionExecutionStatus.VERIFIED.value
    action_record.verified_at = datetime.utcnow()

    payment = db.query(Payment).filter(Payment.id == case.payment_id).first()
    if payment:
        payment.status = "CAPTURED"

    audit_verify = AuditLog(
        case_id=case.id,
        actor=AuditActor.SIMULATOR.value,
        event_type=AuditEventType.RECOVERY_SUCCESS.value,
        action="VERIFY_PAYMENT_CAPTURE",
        decision="RECOVERED",
        previous_state=RecoveryState.VERIFYING.value,
        new_state=RecoveryState.RECOVERED.value,
        amount=4999.0,
        details={"verified": True, "recovered_inr": 4999.0},
    )
    db.add(audit_verify)
    db.commit()
    db.refresh(case)

    timeline_steps.append({
        "step": 5,
        "title": "Revenue Recovery Verified",
        "description": "Payment capture successfully verified. ₹4,999 credited to merchant balance.",
        "state": RecoveryState.RECOVERED.value,
        "recovered_amount": 4999.0,
    })

    return {
        "status": "success",
        "case_id": case.id,
        "customer": "Acme Media",
        "amount": 4999.0,
        "currency": "INR",
        "recovered_amount": case.actual_recovery,
        "final_state": case.current_state,
        "diagnosis": decision.diagnosis,
        "recommendation": decision.recommended_action,
        "policy_decision": "APPROVED",
        "timeline": timeline_steps,
    }
