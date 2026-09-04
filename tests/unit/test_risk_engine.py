import pytest
from agent.core.risk_engine import RevenueRiskEngine
from database.schema.enums import RiskLevel


def test_temporary_bank_failure_scoring():
    assessment = RevenueRiskEngine.calculate(
        amount=4999.0,
        failure_reason="temporary_bank_failure",
        attempt_count=1,
        customer_success_rate=0.95,
    )
    # Temporary bank failure has high recoverability and moderate/low risk
    assert assessment.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]
    assert assessment.recoverability_score >= 80.0
    assert assessment.expected_recovery > 4000.0
    assert assessment.recommended_baseline_delay_minutes == 120


def test_high_amount_increases_risk():
    small_case = RevenueRiskEngine.calculate(
        amount=1500.0,
        failure_reason="insufficient_funds",
        attempt_count=1,
    )
    large_case = RevenueRiskEngine.calculate(
        amount=65000.0,
        failure_reason="insufficient_funds",
        attempt_count=1,
    )
    assert large_case.risk_score > small_case.risk_score


def test_unrecoverable_case_scoring():
    assessment = RevenueRiskEngine.calculate(
        amount=5000.0,
        failure_reason="unrecoverable_case",
        attempt_count=1,
        customer_success_rate=0.4,
    )
    assert assessment.risk_level == RiskLevel.CRITICAL
    assert assessment.risk_score > 80.0
    assert assessment.recoverability_score < 15.0


def test_retry_count_degradation():
    attempt_1 = RevenueRiskEngine.calculate(
        amount=3000.0,
        failure_reason="insufficient_funds",
        attempt_count=1,
    )
    attempt_3 = RevenueRiskEngine.calculate(
        amount=3000.0,
        failure_reason="insufficient_funds",
        attempt_count=3,
    )
    assert attempt_3.risk_score > attempt_1.risk_score
    assert attempt_3.recoverability_score < attempt_1.recoverability_score
