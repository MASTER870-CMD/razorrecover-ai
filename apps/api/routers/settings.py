from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from apps.api.schemas.api_models import SettingsUpdateRequest
from database.connection import get_db
from database.schema.enums import AuditActor, AuditEventType
from database.schema.models import AuditLog, SystemSettings

router = APIRouter(prefix="/api/settings", tags=["Settings"])


@router.get("")
def get_settings(db: Session = Depends(get_db)):
    settings = db.query(SystemSettings).filter_by(id="default").first()
    if not settings:
        settings = SystemSettings(id="default")
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.post("")
def update_settings(payload: SettingsUpdateRequest, db: Session = Depends(get_db)):
    settings = db.query(SystemSettings).filter_by(id="default").first()
    if not settings:
        settings = SystemSettings(id="default")
        db.add(settings)

    changes = {}
    if payload.automatic_recovery_enabled is not None:
        changes["automatic_recovery_enabled"] = payload.automatic_recovery_enabled
        settings.automatic_recovery_enabled = payload.automatic_recovery_enabled
    if payload.max_retry_attempts is not None:
        changes["max_retry_attempts"] = payload.max_retry_attempts
        settings.max_retry_attempts = payload.max_retry_attempts
    if payload.max_automatic_amount is not None:
        changes["max_automatic_amount"] = payload.max_automatic_amount
        settings.max_automatic_amount = payload.max_automatic_amount
    if payload.human_approval_threshold is not None:
        changes["human_approval_threshold"] = payload.human_approval_threshold
        settings.human_approval_threshold = payload.human_approval_threshold
    if payload.recovery_window_days is not None:
        changes["recovery_window_days"] = payload.recovery_window_days
        settings.recovery_window_days = payload.recovery_window_days
    if payload.max_contact_attempts is not None:
        changes["max_contact_attempts"] = payload.max_contact_attempts
        settings.max_contact_attempts = payload.max_contact_attempts
    if payload.retry_cooldown_minutes is not None:
        changes["retry_cooldown_minutes"] = payload.retry_cooldown_minutes
        settings.retry_cooldown_minutes = payload.retry_cooldown_minutes

    audit = AuditLog(
        actor=AuditActor.HUMAN_OPERATOR.value,
        event_type=AuditEventType.SETTINGS_UPDATED.value,
        action="UPDATE_SAFETY_POLICY_THRESHOLDS",
        decision="APPLIED",
        details={"changes": changes},
    )
    db.add(audit)
    db.commit()
    db.refresh(settings)

    return {"status": "updated", "settings": settings}
