from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from apps.api.schemas.api_models import AuditLogResponse
from database.connection import get_db
from database.schema.models import AuditLog

router = APIRouter(prefix="/api/audit", tags=["Audit Trail"])


@router.get("", response_model=List[AuditLogResponse])
def list_audit_logs(
    case_id: Optional[str] = Query(None),
    actor: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(AuditLog)

    if case_id:
        query = query.filter(AuditLog.case_id == case_id)
    if actor:
        query = query.filter(AuditLog.actor == actor.upper())
    if event_type:
        query = query.filter(AuditLog.event_type == event_type.upper())

    logs = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()
    return logs
