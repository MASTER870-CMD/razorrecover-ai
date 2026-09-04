import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from agent.evaluation.evaluator import EvaluationEngine
from database.schema.models import Base, EvaluationRun


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_evaluation_benchmark_500_cases(test_db):
    # Run the full 500-case evaluation benchmark
    run = EvaluationEngine.run_benchmark(test_db, dataset_size=500)

    assert run.dataset_size == 500
    assert run.revenue_at_risk > 0.0
    assert run.revenue_recovered > 0.0
    assert run.recovery_rate > 0.0
    assert run.baseline_recovery > 0.0
    assert run.recovery_rate > run.baseline_recovery_rate
    assert run.incremental_recovery > 0.0
    assert run.correct_decisions > 350
    assert run.unsafe_decisions_blocked > 0
    assert "accuracy_percentage" in run.metrics_breakdown
    assert len(run.evaluation_cases) == 500
