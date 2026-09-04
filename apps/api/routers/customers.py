from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from apps.api.schemas.api_models import CustomerResponse
from database.connection import get_db
from database.schema.models import Customer, Payment, RecoveryCase

router = APIRouter(prefix="/api/customers", tags=["Customers"])


@router.get("", response_model=List[CustomerResponse])
def list_customers(
    search: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Customer)
    if search:
        pattern = f"%{search}%"
        query = query.filter((Customer.name.ilike(pattern)) | (Customer.email.ilike(pattern)))

    customers = query.order_by(Customer.created_at.desc()).offset(offset).limit(limit).all()
    return customers


@router.get("/{customer_id}")
def get_customer_profile(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter((Customer.id == customer_id) | (Customer.external_id == customer_id)).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    payments = db.query(Payment).filter(Payment.customer_id == customer.id).order_by(Payment.created_at.desc()).limit(20).all()
    cases = db.query(RecoveryCase).filter(RecoveryCase.customer_id == customer.id).order_by(RecoveryCase.created_at.desc()).limit(10).all()

    return {
        "customer": customer,
        "recent_payments": [
            {
                "id": p.id,
                "amount": p.amount,
                "currency": p.currency,
                "status": p.status,
                "method": p.payment_method,
                "failure_reason": p.failure_reason,
                "created_at": p.created_at,
            }
            for p in payments
        ],
        "recovery_cases": [
            {
                "id": c.id,
                "amount": c.amount,
                "current_state": c.current_state,
                "risk_score": c.risk_score,
                "actual_recovery": c.actual_recovery,
                "created_at": c.created_at,
            }
            for c in cases
        ],
    }
