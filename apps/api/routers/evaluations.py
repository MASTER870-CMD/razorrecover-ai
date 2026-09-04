from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from agent.evaluation.evaluator import EvaluationEngine
from apps.api.schemas.api_models import EvaluationRunResponse
from database.connection import get_db
from database.schema.models import EvaluationCase, EvaluationRun

router = APIRouter(prefix="/api/evaluations", tags=["Evaluations"])


@router.get("", response_model=List[EvaluationRunResponse])
def list_evaluations(db: Session = Depends(get_db)):
    runs = db.query(EvaluationRun).order_by(EvaluationRun.created_at.desc()).limit(20).all()
    return runs


@router.get("/{run_id}")
def get_evaluation_detail(run_id: str, db: Session = Depends(get_db)):
    run = db.query(EvaluationRun).filter(EvaluationRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Evaluation run not found")

    cases = (
        db.query(EvaluationCase)
        .filter(EvaluationCase.evaluation_run_id == run.id)
        .order_by(EvaluationCase.passed.asc())  # Show failed cases first for inspection
        .limit(100)
        .all()
    )

    return {
        "run": run,
        "sample_cases": [
            {
                "id": c.id,
                "scenario": c.scenario,
                "amount": c.amount,
                "expected_action": c.expected_action,
                "actual_action": c.actual_action,
                "expected_outcome": c.expected_outcome,
                "actual_outcome": c.actual_outcome,
                "passed": c.passed,
                "reasoning": c.reasoning,
            }
            for c in cases
        ],
    }


@router.post("/run", response_model=EvaluationRunResponse)
def run_evaluation(dataset_size: int = Query(500, ge=50, le=1000), db: Session = Depends(get_db)):
    run = EvaluationEngine.run_benchmark(db=db, dataset_size=dataset_size)
    return run
