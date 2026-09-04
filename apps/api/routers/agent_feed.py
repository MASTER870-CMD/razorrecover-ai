from typing import Any, Dict, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.connection import get_db
from database.schema.models import AuditLog, Customer, RecoveryCase

router = APIRouter(prefix="/api/agent", tags=["AI Agent Activity"])


@router.get("/activity")
def get_agent_live_activity(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Returns actual recorded system and agent activity from the immutable audit logs.
    Shows the step-by-step diagnostic and execution events across all cases.
    """
    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .all()
    )

    activity_stream = []
    for log in logs:
        customer_name = "Merchant Customer"
        amount = log.amount or 0.0
        if log.case_id:
            case = db.query(RecoveryCase).filter(RecoveryCase.id == log.case_id).first()
            if case and case.customer:
                customer_name = case.customer.name
                amount = case.amount

        activity_stream.append({
            "id": log.id,
            "case_id": log.case_id,
            "timestamp": log.created_at.isoformat() if log.created_at else None,
            "actor": log.actor,
            "event_type": log.event_type,
            "action": log.action,
            "decision": log.decision,
            "previous_state": log.previous_state,
            "new_state": log.new_state,
            "amount": amount,
            "customer_name": customer_name,
            "correlation_id": log.correlation_id,
            "details": log.details,
        })

    return activity_stream
