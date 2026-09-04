from typing import Dict, Set
from database.schema.enums import RecoveryState


class InvalidStateTransitionError(ValueError):
    """Raised when an illegal state transition is attempted in the recovery workflow."""
    pass


class RecoveryStateMachine:
    """
    Finite State Machine governing the lifecycle of a Recovery Case.
    Guarantees that recovery cases cannot skip safety gates, approval gates,
    or verification steps.
    """

    ALLOWED_TRANSITIONS: Dict[RecoveryState, Set[RecoveryState]] = {
        RecoveryState.AT_RISK: {
            RecoveryState.ANALYZING,
            RecoveryState.STOPPED,
            RecoveryState.EXPIRED,
        },
        RecoveryState.ANALYZING: {
            RecoveryState.ANALYZING,
            RecoveryState.RECOMMENDED,
            RecoveryState.FAILED,
            RecoveryState.STOPPED,
        },
        RecoveryState.RECOMMENDED: {
            RecoveryState.SAFETY_CHECK,
            RecoveryState.STOPPED,
        },
        RecoveryState.SAFETY_CHECK: {
            RecoveryState.APPROVED,
            RecoveryState.PENDING_APPROVAL,
            RecoveryState.BLOCKED,
            RecoveryState.STOPPED,
        },
        RecoveryState.PENDING_APPROVAL: {
            RecoveryState.ANALYZING,
            RecoveryState.APPROVED,
            RecoveryState.BLOCKED,
            RecoveryState.STOPPED,
        },
        RecoveryState.APPROVED: {
            RecoveryState.ANALYZING,
            RecoveryState.EXECUTING,
            RecoveryState.STOPPED,
        },
        RecoveryState.EXECUTING: {
            RecoveryState.VERIFYING,
            RecoveryState.FAILED,
        },
        RecoveryState.VERIFYING: {
            RecoveryState.RECOVERED,
            RecoveryState.FAILED,
            RecoveryState.STOPPED,
        },
        RecoveryState.RECOVERED: set(),  # Terminal success state
        RecoveryState.BLOCKED: {
            RecoveryState.ANALYZING,
        },
        RecoveryState.FAILED: {
            RecoveryState.ANALYZING,      # Can re-analyze for another strategy if retries remaining
            RecoveryState.STOPPED,
        },
        RecoveryState.STOPPED: set(),    # Terminal stop
        RecoveryState.EXPIRED: set(),    # Terminal expiration
    }

    @classmethod
    def validate_transition(cls, current_state: RecoveryState, target_state: RecoveryState) -> bool:
        if current_state == target_state:
            return True
        allowed = cls.ALLOWED_TRANSITIONS.get(current_state, set())
        if target_state not in allowed:
            raise InvalidStateTransitionError(
                f"Invalid recovery state transition: Cannot transition from {current_state.value} to {target_state.value}. "
                f"Permitted next states: {[s.value for s in allowed]}"
            )
        return True

    @classmethod
    def can_transition(cls, current_state: RecoveryState, target_state: RecoveryState) -> bool:
        try:
            return cls.validate_transition(current_state, target_state)
        except InvalidStateTransitionError:
            return False
