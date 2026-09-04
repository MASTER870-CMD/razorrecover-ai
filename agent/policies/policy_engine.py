from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from database.schema.enums import PolicyDecisionType, RecoveryActionType, RiskLevel


@dataclass
class PolicyResult:
    decision: PolicyDecisionType
    reason: str
    policy_name: str
    rule_id: str
    policy_metadata: Dict[str, Any] = field(default_factory=dict)


class DeterministicPolicyEngine:
    """
    Core Safety & Policy Engine for RazorRecover AI.
    Guarantees that money movement and customer communication follow
    deterministic merchant rules and risk ceilings.
    """

    ALLOWED_ACTIONS = {action.value for action in RecoveryActionType}

    @classmethod
    def evaluate(
        cls,
        recommended_action: str,
        amount: float,
        confidence: float,
        risk_level: RiskLevel,
        attempt_count: int,
        hours_since_failure: float = 0.0,
        minutes_since_last_attempt: float = 120.0,
        contact_attempts_count: int = 0,
        customer_opted_out: bool = False,
        # Configurable policy thresholds
        max_retry_attempts: int = 3,
        max_automatic_amount: float = 25000.0,
        human_approval_threshold: float = 0.70,
        recovery_window_days: int = 14,
        max_contact_attempts: int = 2,
        retry_cooldown_minutes: int = 60,
    ) -> PolicyResult:
        # Rule 1: Action Whitelist Check
        if recommended_action not in cls.ALLOWED_ACTIONS:
            return PolicyResult(
                decision=PolicyDecisionType.BLOCK,
                reason=f"Action '{recommended_action}' is not in the merchant-approved action catalog.",
                policy_name="ALLOWED_ACTIONS_WHITELIST",
                rule_id="RULE_01_WHITELIST",
                policy_metadata={"recommended_action": recommended_action},
            )

        # Rule 2: Explicit Stop Recovery
        if recommended_action == RecoveryActionType.STOP_RECOVERY.value:
            return PolicyResult(
                decision=PolicyDecisionType.ALLOW,
                reason="Recovery termination confirmed safely.",
                policy_name="STOP_RECOVERY_CONFIRMATION",
                rule_id="RULE_02_STOP",
            )

        # Rule 3: Customer Opt-Out Protection
        if customer_opted_out and recommended_action in {
            RecoveryActionType.CUSTOMER_NOTIFICATION.value,
            RecoveryActionType.PAYMENT_LINK.value,
        }:
            return PolicyResult(
                decision=PolicyDecisionType.BLOCK,
                reason="Customer has opted out of automated notifications. Dunning contact blocked.",
                policy_name="CUSTOMER_OPT_OUT_GUARD",
                rule_id="RULE_03_OPT_OUT",
            )

        # Rule 4: Recovery Window Expiration
        if hours_since_failure > (recovery_window_days * 24):
            return PolicyResult(
                decision=PolicyDecisionType.BLOCK,
                reason=f"Payment failure occurred {hours_since_failure:.1f}h ago, exceeding maximum {recovery_window_days}-day recovery window.",
                policy_name="RECOVERY_WINDOW_LIMIT",
                rule_id="RULE_04_WINDOW_EXPIRED",
                policy_metadata={"hours_elapsed": hours_since_failure, "max_days": recovery_window_days},
            )

        # Rule 5: Maximum Retry Attempts Exceeded
        is_retry_action = recommended_action in {
            RecoveryActionType.IMMEDIATE_RETRY.value,
            RecoveryActionType.DELAYED_RETRY.value,
        }
        if is_retry_action and attempt_count >= max_retry_attempts:
            return PolicyResult(
                decision=PolicyDecisionType.BLOCK,
                reason=f"Attempt count ({attempt_count}) has reached the maximum permitted limit ({max_retry_attempts}). Direct debit retries blocked.",
                policy_name="MAX_RETRY_ATTEMPTS",
                rule_id="RULE_05_MAX_RETRIES",
                policy_metadata={"attempt_count": attempt_count, "max_retries": max_retry_attempts},
            )

        # Rule 6: Retry Cooldown Violation (Prevent Hammering)
        if recommended_action == RecoveryActionType.IMMEDIATE_RETRY.value and minutes_since_last_attempt < retry_cooldown_minutes:
            return PolicyResult(
                decision=PolicyDecisionType.BLOCK,
                reason=f"Last retry attempt was {minutes_since_last_attempt:.0f} mins ago. Minimum cooldown of {retry_cooldown_minutes} mins is enforced to prevent issuer blocking.",
                policy_name="RETRY_COOLDOWN_PROTECTION",
                rule_id="RULE_06_COOLDOWN",
                policy_metadata={"minutes_since_last": minutes_since_last_attempt, "cooldown_mins": retry_cooldown_minutes},
            )

        # Rule 7: Maximum Customer Contact Attempts
        if recommended_action in {RecoveryActionType.CUSTOMER_NOTIFICATION.value, RecoveryActionType.PAYMENT_LINK.value}:
            if contact_attempts_count >= max_contact_attempts:
                return PolicyResult(
                    decision=PolicyDecisionType.BLOCK,
                    reason=f"Customer has already received {contact_attempts_count} notifications (max {max_contact_attempts}). Further outreach blocked to protect brand reputation.",
                    policy_name="MAX_CONTACT_ATTEMPTS",
                    rule_id="RULE_07_CONTACT_LIMIT",
                    policy_metadata={"contact_count": contact_attempts_count, "max_contact": max_contact_attempts},
                )

        # Rule 8: High Value Human Approval Threshold
        if amount > max_automatic_amount:
            return PolicyResult(
                decision=PolicyDecisionType.REQUIRE_HUMAN_APPROVAL,
                reason=f"Amount ₹{amount:,.2f} exceeds automatic execution limit of ₹{max_automatic_amount:,.2f}. Mandatory human review required.",
                policy_name="MAX_AUTOMATIC_AMOUNT",
                rule_id="RULE_08_AMOUNT_THRESHOLD",
                policy_metadata={"amount": amount, "threshold": max_automatic_amount},
            )

        # Rule 9: Agent Low Confidence Human Review
        if confidence < human_approval_threshold:
            return PolicyResult(
                decision=PolicyDecisionType.REQUIRE_HUMAN_APPROVAL,
                reason=f"AI agent confidence ({confidence:.2f}) is below the deterministic safety threshold ({human_approval_threshold:.2f}).",
                policy_name="HUMAN_APPROVAL_CONFIDENCE_THRESHOLD",
                rule_id="RULE_09_CONFIDENCE_THRESHOLD",
                policy_metadata={"confidence": confidence, "threshold": human_approval_threshold},
            )

        # Rule 10: Critical Risk Human Escalation
        if risk_level == RiskLevel.CRITICAL:
            return PolicyResult(
                decision=PolicyDecisionType.REQUIRE_HUMAN_APPROVAL,
                reason="Risk assessment is CRITICAL. System policy requires merchant finance team confirmation prior to execution.",
                policy_name="CRITICAL_RISK_MANDATORY_REVIEW",
                rule_id="RULE_10_CRITICAL_RISK",
                policy_metadata={"risk_level": risk_level.value},
            )

        # Rule 11: Explicit Human Escalation Request
        if recommended_action == RecoveryActionType.HUMAN_ESCALATION.value:
            return PolicyResult(
                decision=PolicyDecisionType.REQUIRE_HUMAN_APPROVAL,
                reason="AI agent explicitly routed case for human specialist review.",
                policy_name="EXPLICIT_HUMAN_ESCALATION",
                rule_id="RULE_11_AGENT_ESCALATION",
            )

        # Rule 12: All Safety Checks Passed -> ALLOW
        return PolicyResult(
            decision=PolicyDecisionType.ALLOW,
            reason=f"Action '{recommended_action}' passed all 11 safety rules within risk ceiling ₹{max_automatic_amount:,.2f}.",
            policy_name="STANDARD_SAFETY_CLEARANCE",
            rule_id="RULE_12_CLEARANCE",
            policy_metadata={
                "amount": amount,
                "confidence": confidence,
                "risk_level": risk_level.value,
                "attempt_count": attempt_count,
            },
        )
