import pytest
from agent.core.state_machine import InvalidStateTransitionError, RecoveryStateMachine
from database.schema.enums import RecoveryState


def test_valid_state_progression():
    # AT_RISK -> ANALYZING -> RECOMMENDED -> SAFETY_CHECK -> APPROVED -> EXECUTING -> VERIFYING -> RECOVERED
    assert RecoveryStateMachine.validate_transition(RecoveryState.AT_RISK, RecoveryState.ANALYZING)
    assert RecoveryStateMachine.validate_transition(RecoveryState.ANALYZING, RecoveryState.RECOMMENDED)
    assert RecoveryStateMachine.validate_transition(RecoveryState.RECOMMENDED, RecoveryState.SAFETY_CHECK)
    assert RecoveryStateMachine.validate_transition(RecoveryState.SAFETY_CHECK, RecoveryState.APPROVED)
    assert RecoveryStateMachine.validate_transition(RecoveryState.APPROVED, RecoveryState.EXECUTING)
    assert RecoveryStateMachine.validate_transition(RecoveryState.EXECUTING, RecoveryState.VERIFYING)
    assert RecoveryStateMachine.validate_transition(RecoveryState.VERIFYING, RecoveryState.RECOVERED)


def test_invalid_skip_to_recovered_fails():
    with pytest.raises(InvalidStateTransitionError):
        RecoveryStateMachine.validate_transition(RecoveryState.AT_RISK, RecoveryState.RECOVERED)


def test_invalid_skip_to_executing_fails():
    with pytest.raises(InvalidStateTransitionError):
        RecoveryStateMachine.validate_transition(RecoveryState.AT_RISK, RecoveryState.EXECUTING)


def test_human_approval_state_transitions():
    assert RecoveryStateMachine.validate_transition(RecoveryState.SAFETY_CHECK, RecoveryState.PENDING_APPROVAL)
    assert RecoveryStateMachine.validate_transition(RecoveryState.PENDING_APPROVAL, RecoveryState.APPROVED)
    assert RecoveryStateMachine.validate_transition(RecoveryState.PENDING_APPROVAL, RecoveryState.BLOCKED)

    # Cannot skip directly from PENDING_APPROVAL to RECOVERED without execution
    with pytest.raises(InvalidStateTransitionError):
        RecoveryStateMachine.validate_transition(RecoveryState.PENDING_APPROVAL, RecoveryState.RECOVERED)
