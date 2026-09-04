from dataclasses import dataclass
from typing import Optional
from database.schema.enums import RiskLevel


@dataclass
class RiskAssessment:
    risk_score: float
    risk_level: RiskLevel
    recoverability_score: float
    expected_recovery: float
    primary_risk_driver: str
    recommended_baseline_delay_minutes: int


class RevenueRiskEngine:
    """
    Deterministic Revenue Risk Engine for RazorRecover AI.
    Calculates exact mathematical risk scores, recoverability scores,
    and expected recovery amounts without LLM stochasticity.
    """

    FAILURE_BASE_RISK = {
        "temporary_bank_failure": 25.0,
        "network_error": 20.0,
        "insufficient_funds": 45.0,
        "subscription_failure": 48.0,
        "authentication_failure": 55.0,
        "checkout_abandoned": 58.0,
        "overdue_invoice": 65.0,
        "expired_card": 75.0,
        "repeated_failure": 85.0,
        "high_value_payment": 55.0,
        "unrecoverable_case": 96.0,
    }

    FAILURE_BASE_RECOVERABILITY = {
        "temporary_bank_failure": 90.0,
        "network_error": 88.0,
        "insufficient_funds": 76.0,
        "subscription_failure": 72.0,
        "authentication_failure": 62.0,
        "checkout_abandoned": 58.0,
        "high_value_payment": 68.0,
        "overdue_invoice": 52.0,
        "expired_card": 35.0,
        "repeated_failure": 24.0,
        "unrecoverable_case": 4.0,
    }

    OPTIMAL_DELAYS_MINUTES = {
        "network_error": 5,           # Immediate retry window
        "temporary_bank_failure": 120, # 2 hours for bank routing stabilization
        "insufficient_funds": 1440,    # 24 hours (optimal for balance top-up / salary timing)
        "subscription_failure": 720,   # 12 hours
        "authentication_failure": 30,  # 30 mins (prompt with link)
        "checkout_abandoned": 60,      # 1 hour cart recovery
        "expired_card": 0,             # Requires payment link / card update immediately
        "overdue_invoice": 0,          # Formal dunning communication
        "repeated_failure": 2880,      # 48 hours cooling period
        "high_value_payment": 0,       # Human approval needed before retry
        "unrecoverable_case": 0,       # Cease recovery
    }

    @classmethod
    def calculate(
        cls,
        amount: float,
        failure_reason: str,
        attempt_count: int = 1,
        customer_success_rate: float = 0.90,
        customer_ltv: float = 5000.0,
        hours_since_failure: float = 0.0,
        is_subscription: bool = False,
    ) -> RiskAssessment:
        normalized_reason = failure_reason.lower().replace(" ", "_")

        # 1. Base Risk from failure taxonomy
        base_risk = cls.FAILURE_BASE_RISK.get(normalized_reason, 50.0)

        # 2. Risk adjustments based on transaction parameters
        risk = base_risk
        primary_drivers = [f"Base taxonomy risk for {normalized_reason}"]

        # Amount impact
        if amount >= 50000.0:
            risk += 20.0
            primary_drivers.append("High transaction value (>= ₹50,000)")
        elif amount >= 20000.0:
            risk += 10.0
            primary_drivers.append("Elevated transaction value (>= ₹20,000)")
        elif amount <= 1000.0:
            risk -= 5.0

        # Attempt count impact
        if attempt_count > 1:
            penalty = (attempt_count - 1) * 14.0
            risk += penalty
            primary_drivers.append(f"{attempt_count} failed retry attempts")

        # Customer historical reliability
        if customer_success_rate >= 0.90:
            risk -= 15.0
            primary_drivers.append("Excellent customer payment track record (>= 90%)")
        elif customer_success_rate < 0.50:
            risk += 20.0
            primary_drivers.append("Poor historical payment success rate (< 50%)")

        # Subscription impact (churn risk)
        if is_subscription:
            risk += 8.0
            primary_drivers.append("Recurring subscription churn exposure")

        # Clamp risk score to [0.0, 100.0]
        final_risk = max(0.0, min(100.0, round(risk, 1)))

        # Categorize risk level
        if final_risk <= 30.0:
            risk_level = RiskLevel.LOW
        elif final_risk <= 60.0:
            risk_level = RiskLevel.MEDIUM
        elif final_risk <= 80.0:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.CRITICAL

        # 3. Base Recoverability calculation
        base_rec = cls.FAILURE_BASE_RECOVERABILITY.get(normalized_reason, 50.0)
        rec = base_rec

        # Customer track record boosts recoverability
        if customer_success_rate >= 0.90:
            rec += 12.0
        elif customer_success_rate < 0.50:
            rec -= 18.0

        # Severe degradation for multiple failed attempts
        if attempt_count > 1:
            rec -= (attempt_count - 1) * 16.0

        # Time decay: 1.5% decrease per 24 hours elapsed
        time_penalty = (hours_since_failure / 24.0) * 1.5
        rec -= time_penalty

        # Clamp recoverability score to [0.0, 100.0]
        final_rec = max(0.0, min(100.0, round(rec, 1)))

        # 4. Expected Recovery in INR
        expected_rec = round(amount * (final_rec / 100.0), 2)

        # 5. Optimal Baseline Delay
        optimal_delay = cls.OPTIMAL_DELAYS_MINUTES.get(normalized_reason, 60)

        return RiskAssessment(
            risk_score=final_risk,
            risk_level=risk_level,
            recoverability_score=final_rec,
            expected_recovery=expected_rec,
            primary_risk_driver=" | ".join(primary_drivers),
            recommended_baseline_delay_minutes=optimal_delay,
        )
