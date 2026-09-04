from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from apps.api.schemas.api_models import PaymentResponse
from database.connection import get_db
from database.schema.models import Customer, Payment

router = APIRouter(prefix="/api/payments", tags=["Payments"])


@router.get("", response_model=List[PaymentResponse])
def list_payments(
    status: Optional[str] = Query(None),
    method: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Payment).join(Customer)

    if status:
        query = query.filter(Payment.status == status.upper())
    if method:
        query = query.filter(Payment.payment_method == method.upper())

    payments = query.order_by(Payment.created_at.desc()).offset(offset).limit(limit).all()

    return [
        PaymentResponse(
            id=p.id,
            external_id=p.external_id,
            customer_id=p.customer_id,
            customer_name=p.customer.name if p.customer else "Unknown",
            amount=p.amount,
            currency=p.currency,
            status=p.status,
            payment_method=p.payment_method,
            failure_reason=p.failure_reason,
            failure_code=p.failure_code,
            attempt_count=p.attempt_count,
            created_at=p.created_at,
        )
        for p in payments
    ]
