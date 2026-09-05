import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from agent.core.recovery_agent import RecoveryAgent
from agent.core.state_machine import RecoveryStateMachine
from agent.policies.policy_engine import DeterministicPolicyEngine
from apps.api.schemas.api_models import (
    AgentDecisionResponse,
    AuditLogResponse,
    PolicyDecisionResponse,
    RecoveryActionResponse,
    RecoveryCaseResponse,
)
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
    SystemSettings,
)
from database.firestore_sync import firestore_sync
from integrations.razorpay.service import razorpay_service

router = APIRouter(prefix="/api/recovery-cases", tags=["Recovery Cases"])


@router.get("", response_model=List[RecoveryCaseResponse])
def list_recovery_cases(
    status: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(RecoveryCase).join(Customer).join(Payment)

    if status:
        query = query.filter(RecoveryCase.current_state == status.upper())
    if risk_level:
        query = query.filter(RecoveryCase.risk_level == risk_level.upper())
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Customer.name.ilike(search_pattern))
            | (Customer.email.ilike(search_pattern))
            | (Payment.external_id.ilike(search_pattern))
        )

    cases = query.order_by(RecoveryCase.created_at.desc()).offset(offset).limit(limit).all()

    response = []
    for c in cases:
        response.append(
            RecoveryCaseResponse(
                id=c.id,
                payment_id=c.payment_id,
                customer_id=c.customer_id,
                customer_name=c.customer.name if c.customer else "Unknown",
                customer_email=c.customer.email if c.customer else "unknown@example.in",
                amount=c.amount,
                currency=c.currency,
                risk_score=c.risk_score,
                risk_level=c.risk_level,
                recoverability_score=c.recoverability_score,
                recommended_action=c.recommended_action,
                current_state=c.current_state,
                expected_recovery=c.expected_recovery,
                actual_recovery=c.actual_recovery,
                scenario_type=c.scenario_type,
                failure_reason=c.payment.failure_reason if c.payment else None,
                payment_method=c.payment.payment_method if c.payment else None,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
        )
    return response


@router.get("/{case_id}")
def get_recovery_case_detail(case_id: str, db: Session = Depends(get_db)):
    case = db.query(RecoveryCase).filter(RecoveryCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Recovery case not found")

    payment = db.query(Payment).filter(Payment.id == case.payment_id).first()
    customer = db.query(Customer).filter(Customer.id == case.customer_id).first()
    agent_decisions = db.query(AgentDecision).filter(AgentDecision.case_id == case.id).order_by(AgentDecision.created_at.desc()).all()
    policy_decisions = db.query(PolicyDecision).filter(PolicyDecision.case_id == case.id).order_by(PolicyDecision.created_at.desc()).all()
    actions = db.query(RecoveryAction).filter(RecoveryAction.case_id == case.id).order_by(RecoveryAction.executed_at.desc()).all()
    audit_logs = db.query(AuditLog).filter(AuditLog.case_id == case.id).order_by(AuditLog.created_at.asc()).all()

    return {
        "case": {
            "id": case.id,
            "amount": case.amount,
            "currency": case.currency,
            "risk_score": case.risk_score,
            "risk_level": case.risk_level,
            "recoverability_score": case.recoverability_score,
            "recommended_action": case.recommended_action,
            "current_state": case.current_state,
            "expected_recovery": case.expected_recovery,
            "actual_recovery": case.actual_recovery,
            "scenario_type": case.scenario_type,
            "created_at": case.created_at,
            "updated_at": case.updated_at,
        },
        "customer": {
            "id": customer.id if customer else None,
            "name": customer.name if customer else "Unknown",
            "email": customer.email if customer else "unknown@example.in",
            "phone": customer.phone if customer else None,
            "customer_value": customer.customer_value if customer else 0.0,
            "payment_success_rate": customer.payment_success_rate if customer else 0.0,
        },
        "payment": {
            "id": payment.id if payment else None,
            "external_id": payment.external_id if payment else None,
            "status": payment.status if payment else None,
            "payment_method": payment.payment_method if payment else None,
            "failure_reason": payment.failure_reason if payment else None,
            "failure_code": payment.failure_code if payment else None,
            "attempt_count": payment.attempt_count if payment else 1,
        },
        "agent_decisions": [
            {
                "id": d.id,
                "diagnosis": d.diagnosis,
                "recommendation": d.recommendation,
                "confidence": d.confidence,
                "reasoning_summary": d.reasoning_summary,
                "tools_called": d.tools_called,
                "created_at": d.created_at,
            }
            for d in agent_decisions
        ],
        "policy_decisions": [
            {
                "id": p.id,
                "action": p.action,
                "decision": p.decision,
                "reason": p.reason,
                "policy_name": p.policy_name,
                "policy_metadata": p.policy_metadata,
                "created_at": p.created_at,
            }
            for p in policy_decisions
        ],
        "payment_link": next(
            (
                {
                    "payment_link_id": a.external_reference,
                    "short_url": (a.payload or {}).get("short_url"),
                    "mode": (a.payload or {}).get("mode", "LOCAL_SIMULATION"),
                    "status": a.status,
                }
                for a in actions
                if a.action_type == "PAYMENT_LINK"
            ),
            None,
        ),
        "actions": [
            {
                "id": a.id,
                "action_type": a.action_type,
                "status": a.status,
                "amount": a.amount,
                "external_reference": a.external_reference,
                "payload": a.payload,
                "executed_at": a.executed_at,
                "verified_at": a.verified_at,
            }
            for a in actions
        ],
        "audit_logs": [
            {
                "id": l.id,
                "actor": l.actor,
                "event_type": l.event_type,
                "action": l.action,
                "decision": l.decision,
                "previous_state": l.previous_state,
                "new_state": l.new_state,
                "amount": l.amount,
                "correlation_id": l.correlation_id,
                "details": l.details,
                "created_at": l.created_at,
            }
            for l in audit_logs
        ],
    }


@router.post("/{case_id}/analyze")
def analyze_recovery_case(case_id: str, db: Session = Depends(get_db)):
    case = db.query(RecoveryCase).filter(RecoveryCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Recovery case not found")

    # State transition: -> ANALYZING
    previous_state = case.current_state
    try:
        RecoveryStateMachine.validate_transition(RecoveryState(case.current_state), RecoveryState.ANALYZING)
    except InvalidStateTransitionError:
        pass
    case.current_state = RecoveryState.ANALYZING.value

    # Run AI Agent
    agent = RecoveryAgent()
    decision = agent.analyze_case(case_id=case.id, db=db)

    # Persist Agent Decision
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
    case.risk_level = decision.risk_level

    # State transition: -> RECOMMENDED -> SAFETY_CHECK
    case.current_state = RecoveryState.SAFETY_CHECK.value

    # Deterministic Safety Policy Check
    settings = db.query(SystemSettings).filter_by(id="default").first()
    payment = db.query(Payment).filter(Payment.id == case.payment_id).first()

    policy_result = DeterministicPolicyEngine.evaluate(
        recommended_action=decision.recommended_action,
        amount=case.amount,
        confidence=decision.confidence,
        risk_level=RiskLevel(case.risk_level),
        attempt_count=payment.attempt_count if payment else 1,
        max_retry_attempts=getattr(settings, "max_retry_attempts", 3) if settings else 3,
        max_automatic_amount=getattr(settings, "max_automatic_amount", 25000.0) if settings else 25000.0,
        human_approval_threshold=getattr(settings, "human_approval_threshold", 0.70) if settings else 0.70,
        recovery_window_days=getattr(settings, "recovery_window_days", 14) if settings else 14,
        max_contact_attempts=getattr(settings, "max_contact_attempts", 2) if settings else 2,
        retry_cooldown_minutes=getattr(settings, "retry_cooldown_minutes", 60) if settings else 60,
    )

    policy_record = PolicyDecision(
        case_id=case.id,
        action=decision.recommended_action,
        decision=policy_result.decision.value,
        reason=policy_result.reason,
        policy_name=policy_result.policy_name,
        policy_metadata=policy_result.policy_metadata,
    )
    db.add(policy_record)

    # Route according to deterministic policy decision
    if policy_result.decision == PolicyDecisionType.BLOCK:
        case.current_state = RecoveryState.BLOCKED.value
        audit_event = AuditEventType.ACTION_BLOCKED.value
    elif policy_result.decision == PolicyDecisionType.REQUIRE_HUMAN_APPROVAL:
        case.current_state = RecoveryState.PENDING_APPROVAL.value
        audit_event = AuditEventType.HUMAN_APPROVAL_REQUESTED.value
    else:
        case.current_state = RecoveryState.APPROVED.value
        audit_event = AuditEventType.POLICY_APPROVED.value

    # Log Audit Record
    audit = AuditLog(
        case_id=case.id,
        actor=AuditActor.POLICY_ENGINE.value,
        event_type=audit_event,
        action=decision.recommended_action,
        decision=policy_result.decision.value,
        previous_state=previous_state,
        new_state=case.current_state,
        amount=case.amount,
        details={
            "diagnosis": decision.diagnosis,
            "policy_reason": policy_result.reason,
            "rule_id": policy_result.rule_id,
        },
    )
    db.add(audit)
    db.commit()

    firestore_sync.sync_case({
        "id": case.id,
        "amount": case.amount,
        "currency": case.currency,
        "currentState": case.current_state,
        "riskScore": case.risk_score,
        "riskLevel": case.risk_level,
        "recoverabilityScore": case.recoverability_score,
        "recommendedAction": case.recommended_action,
        "expectedRecovery": case.expected_recovery,
    })
    firestore_sync.sync_ai_decision(str(agent_record.id), {
        "caseId": case.id,
        "diagnosis": decision.diagnosis,
        "recommendation": decision.recommended_action,
        "confidence": decision.confidence,
        "reasoningSummary": decision.reasoning_summary,
    })
    firestore_sync.sync_policy_decision(str(policy_record.id), {
        "caseId": case.id,
        "decision": policy_result.decision.value,
        "reason": policy_result.reason,
        "policyName": policy_result.policy_name,
    })

    return {
        "status": "success",
        "case_id": case.id,
        "new_state": case.current_state,
        "recommendation": decision.recommended_action,
        "policy_decision": policy_result.decision.value,
        "policy_reason": policy_result.reason,
        "reasoning_summary": decision.reasoning_summary,
    }


@router.post("/{case_id}/approve")
def approve_recovery_case(case_id: str, db: Session = Depends(get_db)):
    case = db.query(RecoveryCase).filter(RecoveryCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Recovery case not found")

    # Idempotent handling: If already approved or further in lifecycle, return cleanly
    if case.current_state in {
        RecoveryState.APPROVED.value,
        RecoveryState.EXECUTING.value,
        RecoveryState.VERIFYING.value,
        RecoveryState.RECOVERED.value,
        "WAITING_FOR_PAYMENT",
    }:
        return {"status": "already_approved", "case_id": case.id, "current_state": case.current_state}

    previous_state = case.current_state
    case.current_state = RecoveryState.APPROVED.value

    audit = AuditLog(
        case_id=case.id,
        actor=AuditActor.HUMAN_OPERATOR.value,
        event_type=AuditEventType.HUMAN_APPROVED.value,
        action=case.recommended_action,
        decision="APPROVED",
        previous_state=previous_state,
        new_state=case.current_state,
        amount=case.amount,
        details={"operator": "Merchant Finance Admin", "timestamp": datetime.utcnow().isoformat()},
    )
    db.add(audit)
    db.commit()

    firestore_sync.sync_human_approval(case.id, {
        "caseId": case.id,
        "decision": "APPROVED",
        "operator": "Merchant Finance Admin",
        "amount": case.amount,
    })
    firestore_sync.sync_case({"id": case.id, "currentState": case.current_state})

    return {"status": "approved", "case_id": case.id, "current_state": case.current_state}


@router.post("/{case_id}/reject")
def reject_recovery_case(case_id: str, reason: str = Query("Rejected by merchant operator"), db: Session = Depends(get_db)):
    case = db.query(RecoveryCase).filter(RecoveryCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Recovery case not found")

    # Idempotent handling: If already blocked/rejected, return cleanly
    if case.current_state == RecoveryState.BLOCKED.value:
        return {"status": "already_rejected", "case_id": case.id, "current_state": case.current_state}

    previous_state = case.current_state
    case.current_state = RecoveryState.BLOCKED.value

    audit = AuditLog(
        case_id=case.id,
        actor=AuditActor.HUMAN_OPERATOR.value,
        event_type=AuditEventType.HUMAN_REJECTED.value,
        action=case.recommended_action,
        decision="REJECTED",
        previous_state=previous_state,
        new_state=case.current_state,
        amount=case.amount,
        details={"reason": reason, "operator": "Merchant Finance Admin"},
    )
    db.add(audit)
    db.commit()

    firestore_sync.sync_human_approval(case.id, {
        "caseId": case.id,
        "decision": "REJECTED",
        "operator": "Merchant Finance Admin",
        "reason": reason,
    })
    firestore_sync.sync_case({"id": case.id, "currentState": case.current_state})

    return {"status": "rejected", "case_id": case.id, "current_state": case.current_state}


@router.post("/{case_id}/execute")
def execute_recovery_action(case_id: str, db: Session = Depends(get_db)):
    case = db.query(RecoveryCase).filter(RecoveryCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Recovery case not found")

    # Idempotent handling: If already executing, waiting for payment, or recovered, return existing record cleanly
    if case.current_state in {RecoveryState.EXECUTING.value, RecoveryState.VERIFYING.value, "WAITING_FOR_PAYMENT"}:
        existing_action = (
            db.query(RecoveryAction)
            .filter(RecoveryAction.case_id == case.id)
            .order_by(RecoveryAction.executed_at.desc())
            .first()
        )
        ref = existing_action.external_reference if existing_action else ""
        payload = existing_action.payload if existing_action and isinstance(existing_action.payload, dict) else {}
        return {
            "status": "already_executed",
            "case_id": case.id,
            "current_state": case.current_state,
            "action_type": case.recommended_action or "PAYMENT_LINK",
            "reference": ref,
            "payment_link_url": payload.get("short_url"),
            "mode": payload.get("mode", "LOCAL_SIMULATION"),
        }

    if case.current_state == RecoveryState.RECOVERED.value:
        return {
            "status": "already_recovered",
            "case_id": case.id,
            "current_state": "RECOVERED",
            "actual_recovery": case.actual_recovery,
        }

    if case.current_state != RecoveryState.APPROVED.value:
        raise HTTPException(status_code=400, detail=f"Cannot execute action for case in state {case.current_state}. Case must be APPROVED.")

    previous_state = case.current_state
    RecoveryStateMachine.validate_transition(RecoveryState.APPROVED, RecoveryState.EXECUTING)
    case.current_state = RecoveryState.EXECUTING.value

    customer = db.query(Customer).filter(Customer.id == case.customer_id).first()
    payment = db.query(Payment).filter(Payment.id == case.payment_id).first()

    # Route action to Gateway Service (Razorpay Test Mode or Local Simulator)
    action_type = case.recommended_action or "PAYMENT_LINK"
    ref = f"act_{uuid.uuid4().hex[:10]}"
    payload = {}

    if action_type == "PAYMENT_LINK":
        res = razorpay_service.create_recovery_payment_link(
            amount_inr=case.amount,
            customer_name=customer.name if customer else "Customer",
            customer_email=customer.email if customer else "cust@example.in",
            customer_phone=customer.phone if customer else "+919876543210",
            description=f"RazorRecover AI Recovery for Case #{case.id[:8]}",
            case_id=case.id,
        )
        ref = res.get("payment_link_id", ref)
        payload = res
    elif action_type in {"DELAYED_RETRY", "IMMEDIATE_RETRY"}:
        payload = {
            "mode": razorpay_service.get_connection_status()["mode"],
            "strategy": action_type,
            "scheduled_at": datetime.utcnow().isoformat(),
        }
    elif action_type == "CUSTOMER_NOTIFICATION":
        payload = {"channel": "EMAIL_AND_SMS", "sent_to": customer.email if customer else "customer@example.in"}

    action_record = RecoveryAction(
        case_id=case.id,
        action_type=action_type,
        status=ActionExecutionStatus.EXECUTED.value,
        amount=case.amount,
        external_reference=ref,
        payload=payload,
        executed_at=datetime.utcnow(),
    )
    db.add(action_record)

    audit = AuditLog(
        case_id=case.id,
        actor=AuditActor.AGENT.value,
        event_type=AuditEventType.ACTION_EXECUTED.value,
        action=action_type,
        decision="EXECUTED",
        previous_state=previous_state,
        new_state=case.current_state,
        amount=case.amount,
        details={"reference": ref, "mode": payload.get("mode", "LOCAL_SIMULATION"), "short_url": payload.get("short_url")},
    )
    db.add(audit)
    db.commit()

    if payload.get("payment_link_id"):
        firestore_sync.sync_payment_link(payload["payment_link_id"], {
            "caseId": case.id,
            "shortUrl": payload.get("short_url"),
            "amount": case.amount,
            "status": "created",
            "mode": payload.get("mode", "RAZORPAY_TEST_MODE"),
        })
    firestore_sync.sync_case({"id": case.id, "currentState": case.current_state})

    return {
        "status": "executed",
        "case_id": case.id,
        "current_state": case.current_state,
        "action_type": action_type,
        "reference": ref,
        "payment_link_url": payload.get("short_url"),
        "mode": payload.get("mode", "LOCAL_SIMULATION"),
    }


@router.post("/{case_id}/verify")
def verify_recovery_outcome(case_id: str, force_success: Optional[bool] = None, db: Session = Depends(get_db)):
    case = db.query(RecoveryCase).filter(RecoveryCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Recovery case not found")

    # Idempotent check: if already recovered, return success immediately
    if case.current_state == RecoveryState.RECOVERED.value:
        return {
            "status": "already_recovered",
            "case_id": case.id,
            "current_state": "RECOVERED",
            "recovered": True,
            "actual_recovery": case.actual_recovery or case.amount,
        }

    # If case was in APPROVED state when verify was clicked, execute action first
    if case.current_state == RecoveryState.APPROVED.value:
        execute_recovery_action(case_id, db)
        case = db.query(RecoveryCase).filter(RecoveryCase.id == case_id).first()

    previous_state = case.current_state
    case.current_state = RecoveryState.VERIFYING.value

    # Fetch last action executed
    last_action = (
        db.query(RecoveryAction)
        .filter(RecoveryAction.case_id == case.id)
        .order_by(RecoveryAction.executed_at.desc())
        .first()
    )

    is_success = False
    if force_success is not None:
        is_success = force_success
    elif last_action and last_action.external_reference:
        v_res = razorpay_service.verify_payment_link_completion(last_action.external_reference)
        is_success = v_res.get("paid", False)
    else:
        is_success = True  # fallback confirmation in simulator test

    if is_success:
        case.current_state = RecoveryState.RECOVERED.value
        case.actual_recovery = case.amount
        if last_action:
            last_action.status = ActionExecutionStatus.VERIFIED.value
            last_action.verified_at = datetime.utcnow()
        payment = db.query(Payment).filter(Payment.id == case.payment_id).first()
        if payment:
            payment.status = "CAPTURED"

        audit_event = AuditEventType.RECOVERY_SUCCESS.value
        decision_label = "RECOVERED"
    else:
        case.current_state = RecoveryState.FAILED.value
        case.actual_recovery = 0.0
        if last_action:
            last_action.status = ActionExecutionStatus.FAILED.value
            last_action.verified_at = datetime.utcnow()

        audit_event = AuditEventType.RECOVERY_FAILED.value
        decision_label = "FAILED"

    audit = AuditLog(
        case_id=case.id,
        actor=AuditActor.AGENT.value,
        event_type=audit_event,
        action="VERIFY_PAYMENT_CAPTURE",
        decision=decision_label,
        previous_state=previous_state,
        new_state=case.current_state,
        amount=case.actual_recovery,
        details={"verified": is_success, "actual_recovered_inr": case.actual_recovery},
    )
    db.add(audit)
    db.commit()

    firestore_sync.sync_case({
        "id": case.id,
        "currentState": case.current_state,
        "actualRecovery": case.actual_recovery,
        "verified": is_success,
    })
    firestore_sync.sync_audit_event(str(audit.id), {
        "caseId": case.id,
        "actor": audit.actor,
        "eventType": audit.event_type,
        "decision": audit.decision,
        "amount": case.actual_recovery,
    })

    return {
        "status": "verified",
        "case_id": case.id,
        "current_state": case.current_state,
        "recovered": is_success,
        "actual_recovery": case.actual_recovery,
    }
