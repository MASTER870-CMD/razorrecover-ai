import pytest
from database.connection import get_db_session, init_db
from database.schema.models import Customer, Payment, RecoveryCase, WebhookEvent
from database.schema.enums import PolicyDecisionType, RecoveryActionType, RecoveryState, RiskLevel
from agent.policies.policy_engine import DeterministicPolicyEngine
from agent.core.state_machine import RecoveryStateMachine, InvalidStateTransitionError
from integrations.razorpay.webhooks import RazorpayWebhookSecurity


@pytest.fixture(autouse=True)
def setup_database():
    init_db()


def test_ai_cannot_bypass_policy_amount_ceiling():
    """Policy engine must flag human review or block if amount exceeds threshold, regardless of AI recommendation."""
    # AI recommends payment link for high amount
    eval_result = DeterministicPolicyEngine.evaluate(
        recommended_action=RecoveryActionType.PAYMENT_LINK.value,
        amount=50000.0,  # Exceeds default limit 25,000
        confidence=0.95,
        risk_level=RiskLevel.MEDIUM,
        attempt_count=1,
    )
    
    assert eval_result.decision == PolicyDecisionType.REQUIRE_HUMAN_APPROVAL
    assert "amount" in eval_result.reason.lower() or "exceeds" in eval_result.reason.lower()


def test_ai_cannot_bypass_policy_max_attempts():
    """Policy engine blocks further recovery if attempts exceed threshold."""
    eval_result = DeterministicPolicyEngine.evaluate(
        recommended_action=RecoveryActionType.DELAYED_RETRY.value,
        amount=1000.0,
        confidence=0.99,
        risk_level=RiskLevel.CRITICAL,
        attempt_count=5,  # Exceeds max retry attempts (3)
    )
    
    assert eval_result.decision == PolicyDecisionType.BLOCK


def test_blocked_action_cannot_execute():
    """A case in BLOCKED state cannot directly transition to EXECUTING or RECOVERED."""
    with pytest.raises(InvalidStateTransitionError):
        RecoveryStateMachine.validate_transition(RecoveryState.BLOCKED, RecoveryState.EXECUTING)

    with pytest.raises(InvalidStateTransitionError):
        RecoveryStateMachine.validate_transition(RecoveryState.BLOCKED, RecoveryState.RECOVERED)


def test_recovery_cannot_be_marked_successful_before_verification():
    """Case cannot jump directly from AT_RISK or APPROVED to RECOVERED without execution and verification."""
    with pytest.raises(InvalidStateTransitionError):
        RecoveryStateMachine.validate_transition(RecoveryState.AT_RISK, RecoveryState.RECOVERED)

    with pytest.raises(InvalidStateTransitionError):
        RecoveryStateMachine.validate_transition(RecoveryState.APPROVED, RecoveryState.RECOVERED)


def test_duplicate_webhook_cannot_create_duplicate_recovery():
    """If the same webhook arrives twice, idempotency check ensures it is discarded."""
    import uuid
    with get_db_session() as db:
        duplicate_event_id = f"evt_dup_{uuid.uuid4().hex[:12]}"
        
        # First arrival
        is_dup_1 = RazorpayWebhookSecurity.is_duplicate_event(duplicate_event_id, db)
        assert is_dup_1 is False
        
        RazorpayWebhookSecurity.record_processed_event(
            event_id=duplicate_event_id,
            event_type="payment.captured",
            payload={"id": duplicate_event_id, "amount": 1000},
            case_id=None,
            db=db,
        )
        
        # Second arrival
        is_dup_2 = RazorpayWebhookSecurity.is_duplicate_event(duplicate_event_id, db)
        assert is_dup_2 is True  # Detected as duplicate, discarded!
