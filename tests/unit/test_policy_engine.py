import pytest
from agent.policies.policy_engine import DeterministicPolicyEngine
from database.schema.enums import PolicyDecisionType, RecoveryActionType, RiskLevel


def test_allowed_standard_recovery():
    result = DeterministicPolicyEngine.evaluate(
        recommended_action=RecoveryActionType.DELAYED_RETRY.value,
        amount=4999.0,
        confidence=0.92,
        risk_level=RiskLevel.MEDIUM,
        attempt_count=1,
    )
    assert result.decision == PolicyDecisionType.ALLOW
    assert result.rule_id == "RULE_12_CLEARANCE"


def test_max_retries_exceeded_blocks_retry():
    # If attempt count >= 3, policy must BLOCK further direct retries
    result = DeterministicPolicyEngine.evaluate(
        recommended_action=RecoveryActionType.DELAYED_RETRY.value,
        amount=4999.0,
        confidence=0.95,
        risk_level=RiskLevel.MEDIUM,
        attempt_count=3,
        max_retry_attempts=3,
    )
    assert result.decision == PolicyDecisionType.BLOCK
    assert "maximum permitted limit" in result.reason.lower()


def test_high_amount_requires_human_approval():
    # High value transaction (> ₹25,000) cannot be executed automatically
    result = DeterministicPolicyEngine.evaluate(
        recommended_action=RecoveryActionType.DELAYED_RETRY.value,
        amount=45000.0,
        confidence=0.95,
        risk_level=RiskLevel.MEDIUM,
        attempt_count=1,
        max_automatic_amount=25000.0,
    )
    assert result.decision == PolicyDecisionType.REQUIRE_HUMAN_APPROVAL
    assert "exceeds automatic execution limit" in result.reason.lower()


def test_low_confidence_requires_human_approval():
    # AI confidence < 0.70 cannot bypass policy
    result = DeterministicPolicyEngine.evaluate(
        recommended_action=RecoveryActionType.DELAYED_RETRY.value,
        amount=2500.0,
        confidence=0.55,
        risk_level=RiskLevel.LOW,
        attempt_count=1,
        human_approval_threshold=0.70,
    )
    assert result.decision == PolicyDecisionType.REQUIRE_HUMAN_APPROVAL
    assert "below the deterministic safety threshold" in result.reason.lower()


def test_critical_risk_requires_human_approval():
    result = DeterministicPolicyEngine.evaluate(
        recommended_action=RecoveryActionType.DELAYED_RETRY.value,
        amount=5000.0,
        confidence=0.92,
        risk_level=RiskLevel.CRITICAL,
        attempt_count=1,
    )
    assert result.decision == PolicyDecisionType.REQUIRE_HUMAN_APPROVAL
    assert "CRITICAL" in result.reason


def test_unsupported_action_blocked():
    # Model hallucinations of non-existent actions are strictly blocked
    result = DeterministicPolicyEngine.evaluate(
        recommended_action="UNRESTRICTED_AUTO_DEBIT",
        amount=1000.0,
        confidence=0.99,
        risk_level=RiskLevel.LOW,
        attempt_count=1,
    )
    assert result.decision == PolicyDecisionType.BLOCK
    assert "not in the merchant-approved action catalog" in result.reason


def test_retry_cooldown_blocks_immediate_hammering():
    result = DeterministicPolicyEngine.evaluate(
        recommended_action=RecoveryActionType.IMMEDIATE_RETRY.value,
        amount=1000.0,
        confidence=0.95,
        risk_level=RiskLevel.LOW,
        attempt_count=1,
        minutes_since_last_attempt=15.0,
        retry_cooldown_minutes=60,
    )
    assert result.decision == PolicyDecisionType.BLOCK
    assert "cooldown" in result.reason.lower()
