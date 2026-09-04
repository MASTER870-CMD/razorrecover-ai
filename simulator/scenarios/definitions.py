from dataclasses import dataclass
from typing import Optional
from database.schema.enums import RecoveryActionType


@dataclass
class ScenarioDefinition:
    key: str
    name: str
    description: str
    failure_reason: str
    failure_code: str
    typical_amount_range: tuple[float, float]
    payment_method: str
    ground_truth_optimal_action: str
    ground_truth_recoverable: bool
    ground_truth_policy_decision: str  # ALLOW, REQUIRE_HUMAN_APPROVAL, BLOCK
    simulation_success_rate: float  # probability of recovery if optimal action executed


SCENARIO_DEFINITIONS = {
    "insufficient_funds": ScenarioDefinition(
        key="insufficient_funds",
        name="Insufficient Funds on Debit/UPI",
        description="Customer account balance inadequate for scheduled charge. Resolvable via timed retry around pay cycle.",
        failure_reason="insufficient_funds",
        failure_code="BAD_REQUEST_PAYMENT_DECLINED_BY_BANK",
        typical_amount_range=(1499.0, 9999.0),
        payment_method="UPI",
        ground_truth_optimal_action=RecoveryActionType.DELAYED_RETRY.value,
        ground_truth_recoverable=True,
        ground_truth_policy_decision="ALLOW",
        simulation_success_rate=0.82,
    ),
    "temporary_bank_failure": ScenarioDefinition(
        key="temporary_bank_failure",
        name="Temporary Bank Gateway Outage",
        description="Issuer bank gateway (HDFC/SBI/ICICI) transiently down. Recovers quickly upon route restoration.",
        failure_reason="temporary_bank_failure",
        failure_code="GATEWAY_ERROR_ISSUER_DOWN",
        typical_amount_range=(999.0, 14999.0),
        payment_method="NETBANKING",
        ground_truth_optimal_action=RecoveryActionType.DELAYED_RETRY.value,
        ground_truth_recoverable=True,
        ground_truth_policy_decision="ALLOW",
        simulation_success_rate=0.92,
    ),
    "network_error": ScenarioDefinition(
        key="network_error",
        name="Network Communication Timeout",
        description="TCP socket timeout during capture handshake. Safely retryable immediately.",
        failure_reason="network_error",
        failure_code="GATEWAY_TIMEOUT",
        typical_amount_range=(499.0, 8999.0),
        payment_method="CARD",
        ground_truth_optimal_action=RecoveryActionType.IMMEDIATE_RETRY.value,
        ground_truth_recoverable=True,
        ground_truth_policy_decision="ALLOW",
        simulation_success_rate=0.95,
    ),
    "authentication_failure": ScenarioDefinition(
        key="authentication_failure",
        name="3DS OTP Authentication Failure",
        description="Customer aborted OTP screen or entered incorrect code. Re-prompting via Payment Link enables successful recovery.",
        failure_reason="authentication_failure",
        failure_code="BAD_REQUEST_PAYMENT_OTP_INCORRECT",
        typical_amount_range=(1999.0, 12999.0),
        payment_method="CARD",
        ground_truth_optimal_action=RecoveryActionType.PAYMENT_LINK.value,
        ground_truth_recoverable=True,
        ground_truth_policy_decision="ALLOW",
        simulation_success_rate=0.74,
    ),
    "expired_card": ScenarioDefinition(
        key="expired_card",
        name="Expired Card on File",
        description="Saved token validity expired. Retrying token is futile; payment link allows updated instrument entry.",
        failure_reason="expired_card",
        failure_code="CARD_EXPIRED",
        typical_amount_range=(999.0, 7999.0),
        payment_method="CARD",
        ground_truth_optimal_action=RecoveryActionType.PAYMENT_LINK.value,
        ground_truth_recoverable=True,
        ground_truth_policy_decision="ALLOW",
        simulation_success_rate=0.62,
    ),
    "checkout_abandoned": ScenarioDefinition(
        key="checkout_abandoned",
        name="Checkout Flow Abandonment",
        description="Customer initiated order checkout but dropped off at payment step. Targeted notification resumes intent.",
        failure_reason="checkout_abandoned",
        failure_code="ORDER_ABANDONED_AT_PAYMENT",
        typical_amount_range=(799.0, 4999.0),
        payment_method="UPI",
        ground_truth_optimal_action=RecoveryActionType.CUSTOMER_NOTIFICATION.value,
        ground_truth_recoverable=True,
        ground_truth_policy_decision="ALLOW",
        simulation_success_rate=0.55,
    ),
    "subscription_failure": ScenarioDefinition(
        key="subscription_failure",
        name="Recurring Subscription Mandate Failure",
        description="E-mandate auto-debit failed for monthly/annual SaaS tier. Coordinated smart retry protects ARR.",
        failure_reason="subscription_failure",
        failure_code="MANDATE_DEBIT_FAILED",
        typical_amount_range=(2499.0, 19999.0),
        payment_method="CARD",
        ground_truth_optimal_action=RecoveryActionType.DELAYED_RETRY.value,
        ground_truth_recoverable=True,
        ground_truth_policy_decision="ALLOW",
        simulation_success_rate=0.79,
    ),
    "overdue_invoice": ScenarioDefinition(
        key="overdue_invoice",
        name="Overdue B2B Enterprise Invoice",
        description="B2B Net-30 invoice unpaid beyond due date. Automated multi-channel notification and link recovery.",
        failure_reason="overdue_invoice",
        failure_code="INVOICE_PAST_DUE",
        typical_amount_range=(15000.0, 85000.0),
        payment_method="NETBANKING",
        ground_truth_optimal_action=RecoveryActionType.CUSTOMER_NOTIFICATION.value,
        ground_truth_recoverable=True,
        ground_truth_policy_decision="ALLOW",  # unless > 25000 which triggers human approval
        simulation_success_rate=0.68,
    ),
    "repeated_failure": ScenarioDefinition(
        key="repeated_failure",
        name="Chronic Repeated Payment Failure",
        description="Payment has already failed multiple prior retry attempts. Escalation or termination required to prevent penalties.",
        failure_reason="repeated_failure",
        failure_code="EXCESSIVE_RETRY_FAILURES",
        typical_amount_range=(1999.0, 15999.0),
        payment_method="CARD",
        ground_truth_optimal_action=RecoveryActionType.HUMAN_ESCALATION.value,
        ground_truth_recoverable=False,
        ground_truth_policy_decision="REQUIRE_HUMAN_APPROVAL",
        simulation_success_rate=0.25,
    ),
    "high_value_payment": ScenarioDefinition(
        key="high_value_payment",
        name="High-Value Enterprise Transaction (> ₹25,000)",
        description="Large payment transaction requiring mandatory human approval before automated retries.",
        failure_reason="high_value_payment",
        failure_code="HIGH_VALUE_THRESHOLD_EXCEEDED",
        typical_amount_range=(35000.0, 150000.0),
        payment_method="NETBANKING",
        ground_truth_optimal_action=RecoveryActionType.HUMAN_ESCALATION.value,
        ground_truth_recoverable=True,
        ground_truth_policy_decision="REQUIRE_HUMAN_APPROVAL",
        simulation_success_rate=0.75,
    ),
    "successful_retry": ScenarioDefinition(
        key="successful_retry",
        name="High-Confidence Delayed Retry",
        description="Payment with high recoverability that succeeds immediately upon scheduled retry.",
        failure_reason="temporary_bank_failure",
        failure_code="GATEWAY_RETRY_SCHEDULED",
        typical_amount_range=(1200.0, 8500.0),
        payment_method="UPI",
        ground_truth_optimal_action=RecoveryActionType.DELAYED_RETRY.value,
        ground_truth_recoverable=True,
        ground_truth_policy_decision="ALLOW",
        simulation_success_rate=0.98,
    ),
    "unrecoverable_case": ScenarioDefinition(
        key="unrecoverable_case",
        name="Stolen Instrument / Closed Account (Unrecoverable)",
        description="Hard decline due to suspected fraud, stolen card, or terminated account. Must be blocked.",
        failure_reason="unrecoverable_case",
        failure_code="ACCOUNT_CLOSED_OR_STOLEN",
        typical_amount_range=(2000.0, 25000.0),
        payment_method="CARD",
        ground_truth_optimal_action=RecoveryActionType.STOP_RECOVERY.value,
        ground_truth_recoverable=False,
        ground_truth_policy_decision="BLOCK",
        simulation_success_rate=0.01,
    ),
}
