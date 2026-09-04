import json
import logging
import os
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from agent.core.risk_engine import RevenueRiskEngine
from agent.prompts.recovery_prompts import (
    RECOVERY_AGENT_SYSTEM_PROMPT,
    RECOVERY_CASE_USER_PROMPT,
)
from agent.tools.registry import AgentToolRegistry
from database.schema.enums import RecoveryActionType, RiskLevel
from database.schema.models import Customer, Payment, RecoveryCase

logger = logging.getLogger(__name__)


class AgentDecisionResult(BaseModel):
    case_id: str
    diagnosis: str
    risk_level: str
    recoverability_score: float = Field(ge=0.0, le=100.0)
    recommended_action: str
    expected_recovery: float
    confidence: float = Field(ge=0.0, le=1.0)
    requires_human_approval: bool
    reasoning_summary: str
    tools_called: List[str] = Field(default_factory=list)


class RecoveryAgent:
    """
    RazorRecover Autonomous AI Agent.
    Orchestrates tool calling, failure diagnosis, and recovery recommendation
    using Google Gemini API with deterministic fallback.
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self._client = None

        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
                logger.info("Initialized Gemini AI client successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize Gemini client: {e}. Running in deterministic AI mode.")

    def analyze_case(self, case_id: str, db: Session) -> AgentDecisionResult:
        """
        Analyze a recovery case using controlled tool interfaces and generate
        a structured decision.
        """
        tools = AgentToolRegistry(db)
        tools_called: List[str] = []

        # Tool 1: Fetch case and payment details
        case = db.query(RecoveryCase).filter(RecoveryCase.id == case_id).first()
        if not case:
            raise ValueError(f"Recovery case {case_id} not found")

        tools_called.append("get_payment_details")
        payment_info = tools.get_payment_details(case.payment_id)

        # Tool 2: Fetch customer profile
        tools_called.append("get_customer_history")
        customer_info = tools.get_customer_history(case.customer_id)

        # Tool 3 & 4: Calculate deterministic risk and recoverability
        tools_called.append("calculate_risk")
        risk_info = tools.calculate_risk(case.payment_id)

        tools_called.append("calculate_recoverability")
        rec_info = tools.calculate_recoverability(case.payment_id)

        # Tool 5: Classify failure taxonomy
        tools_called.append("classify_failure")
        classification = tools.classify_failure(
            failure_reason=payment_info.get("failure_reason", ""),
            failure_code=payment_info.get("failure_code", ""),
        )

        # Attempt Gemini LLM analysis if API key is active
        if self._client:
            try:
                user_prompt = RECOVERY_CASE_USER_PROMPT.format(
                    case_id=case.id,
                    payment_id=payment_info.get("external_id", case.payment_id),
                    customer_name=customer_info.get("name", "Unknown"),
                    customer_email=customer_info.get("email", "unknown@example.com"),
                    amount=case.amount,
                    payment_method=payment_info.get("payment_method", "CARD"),
                    failure_reason=payment_info.get("failure_reason", "unknown"),
                    failure_code=payment_info.get("failure_code", "none"),
                    attempt_count=payment_info.get("attempt_count", 1),
                    success_rate=customer_info.get("payment_success_rate", 0.9),
                    customer_ltv=customer_info.get("customer_value", 5000.0),
                    risk_score=risk_info.get("risk_score", 50.0),
                    risk_level=risk_info.get("risk_level", "MEDIUM"),
                    recoverability_score=rec_info.get("recoverability_score", 70.0),
                    expected_recovery=rec_info.get("expected_recovery", case.amount * 0.7),
                )

                response = self._client.models.generate_content(
                    model=self.model_name,
                    contents=user_prompt,
                    config={
                        "system_instruction": RECOVERY_AGENT_SYSTEM_PROMPT,
                        "response_mime_type": "application/json",
                        "temperature": 0.1,
                    },
                )

                if response.text:
                    parsed = json.loads(response.text)
                    tools_called.append("recommend_recovery_action")
                    return AgentDecisionResult(
                        case_id=case.id,
                        diagnosis=parsed.get("diagnosis", classification.get("classified_category")),
                        risk_level=parsed.get("risk_level", risk_info.get("risk_level")),
                        recoverability_score=float(parsed.get("recoverability_score", rec_info.get("recoverability_score"))),
                        recommended_action=parsed.get("recommended_action", classification.get("recommended_action")),
                        expected_recovery=float(parsed.get("expected_recovery", rec_info.get("expected_recovery"))),
                        confidence=float(parsed.get("confidence", 0.92)),
                        requires_human_approval=bool(parsed.get("requires_human_approval", case.amount > 25000.0)),
                        reasoning_summary=parsed.get("reasoning_summary", "Deterministic recovery analysis completed."),
                        tools_called=tools_called,
                    )
            except Exception as ex:
                logger.warning(f"Gemini API call encountered an error ({ex}). Falling back to deterministic AI model.")

        # Deterministic Expert AI Engine Fallback (guaranteed 100% uptime)
        return self._analyze_with_deterministic_model(
            case=case,
            payment_info=payment_info,
            customer_info=customer_info,
            risk_info=risk_info,
            rec_info=rec_info,
            classification=classification,
            tools_called=tools_called,
        )

    def _analyze_with_deterministic_model(
        self,
        case: RecoveryCase,
        payment_info: Dict[str, Any],
        customer_info: Dict[str, Any],
        risk_info: Dict[str, Any],
        rec_info: Dict[str, Any],
        classification: Dict[str, Any],
        tools_called: List[str],
    ) -> AgentDecisionResult:
        tools_called.append("recommend_recovery_action")
        amount = case.amount
        attempt_count = payment_info.get("attempt_count", 1)
        reason = (payment_info.get("failure_reason") or "").lower()
        success_rate = customer_info.get("payment_success_rate", 0.9)
        risk_level = risk_info.get("risk_level", "MEDIUM")
        rec_score = float(rec_info.get("recoverability_score", 70.0))
        expected_rec = float(rec_info.get("expected_recovery", amount * 0.7))

        requires_human = (amount > 25000.0) or (risk_level == "CRITICAL") or (attempt_count >= 3)

        if "insufficient" in reason or "balance" in reason:
            diagnosis = "Customer balance shortfall on account debit"
            recommended_action = RecoveryActionType.DELAYED_RETRY.value
            confidence = 0.93
            reasoning = (
                f"Payment of ₹{amount:,.2f} failed due to insufficient funds. Customer has a strong {success_rate:.0%} "
                f"payment history with lifetime value of ₹{customer_info.get('customer_value', 0):,.2f}. Recommending a smart "
                f"delayed retry scheduled for balance replenishment window."
            )
        elif "bank" in reason or "issuer" in reason or "downtime" in reason:
            diagnosis = "Transient issuer bank processing degradation"
            recommended_action = RecoveryActionType.DELAYED_RETRY.value
            confidence = 0.95
            reasoning = (
                f"Issuer gateway failure detected. Bank routing issues are typically resolved within 2 hours. "
                f"A delayed retry carries a high {rec_score:.0f}% probability of successful recovery."
            )
        elif "network" in reason or "timeout" in reason:
            diagnosis = "Transient gateway network communication timeout"
            recommended_action = RecoveryActionType.IMMEDIATE_RETRY.value
            confidence = 0.96
            reasoning = (
                "Transient network timeout during capture request. Immediate retry is optimal before customer session terminates."
            )
        elif "expired" in reason or "validity" in reason:
            diagnosis = "Saved payment instrument expired"
            recommended_action = RecoveryActionType.PAYMENT_LINK.value
            confidence = 0.90
            reasoning = (
                "Card validity period has lapsed. Retrying the existing token will repeatedly fail. "
                "Dispatching a secure Razorpay Payment Link to allow modern UPI/Card renewal."
            )
        elif "auth" in reason or "otp" in reason or "3ds" in reason:
            diagnosis = "Customer 3DS authentication challenge expired or aborted"
            recommended_action = RecoveryActionType.PAYMENT_LINK.value
            confidence = 0.88
            reasoning = (
                "Customer abandoned the two-factor authentication challenge. Sending a dynamic Razorpay payment link "
                "with 24-hour expiry to facilitate seamless checkout."
            )
        elif "abandon" in reason:
            diagnosis = "Checkout session dropped before payment completion"
            recommended_action = RecoveryActionType.CUSTOMER_NOTIFICATION.value
            confidence = 0.85
            reasoning = (
                "Cart abandonment detected. Sending targeted notification with one-click payment resumption."
            )
        elif "repeated" in reason or attempt_count >= 3:
            diagnosis = "Exhausted standard retry attempts without successful capture"
            recommended_action = RecoveryActionType.HUMAN_ESCALATION.value if amount > 5000 else RecoveryActionType.STOP_RECOVERY.value
            confidence = 0.91
            requires_human = True
            reasoning = (
                f"Payment has failed {attempt_count} times. Additional automated retries risk merchant account debit penalties. "
                f"Escalating to human account manager for direct merchant outreach."
            )
        elif "unrecoverable" in reason or "stolen" in reason or "lost" in reason:
            diagnosis = "Hard unrecoverable decline (stolen/fraudulent card or closed account)"
            recommended_action = RecoveryActionType.STOP_RECOVERY.value
            confidence = 0.98
            rec_score = 4.0
            expected_rec = 0.0
            reasoning = (
                "Hard decline reported by issuing bank. To prevent fraud penalties, all recovery actions are permanently stopped."
            )
        else:
            diagnosis = "Unspecified payment authorization decline"
            recommended_action = RecoveryActionType.CUSTOMER_NOTIFICATION.value
            confidence = 0.82
            reasoning = (
                f"Generic decline encountered. Recommending customer notification with support contact options."
            )

        return AgentDecisionResult(
            case_id=case.id,
            diagnosis=diagnosis,
            risk_level=risk_level,
            recoverability_score=rec_score,
            recommended_action=recommended_action,
            expected_recovery=expected_rec,
            confidence=confidence,
            requires_human_approval=requires_human,
            reasoning_summary=reasoning,
            tools_called=tools_called,
        )
