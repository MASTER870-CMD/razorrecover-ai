# AI Agent Architecture — RazorRecover AI

## 1. Overview
RazorRecover AI implements a **Tool-Using Autonomous AI Agent** powered by Google Gemini (with structured output schema enforcement) and a deterministic fallback engine.

The agent reasons over multi-dimensional financial context:
- **Payment event**: Amount, currency, instrument type (UPI, Card, Netbanking), bank failure code.
- **Customer history**: Lifetime value (LTV), historical success rate, tenure.
- **Risk scores**: Pre-computed mathematical risk and recoverability indices.
- **Dunning lifecycle**: Previous retry count, time elapsed since failure.

---

## 2. Controlled Tool Catalog

The AI agent does NOT have direct SQL or unrestricted execution capabilities. It interacts strictly through 15 sandboxed tools:

1. `get_payment_details(payment_id)`: Fetches sanitized payment details.
2. `get_customer_history(customer_id)`: Returns LTV, lifetime transactions, and track record.
3. `get_subscription_details(subscription_id)`: Inspects recurring mandate schedules.
4. `get_invoice_details(invoice_id)`: Retrieves overdue Net-30 invoice details.
5. `calculate_risk(payment_id)`: Invokes deterministic risk calculation.
6. `calculate_recoverability(payment_id)`: Computes statistical recoverability score.
7. `classify_failure(failure_reason, failure_code)`: Normalizes bank errors into standard taxonomy.
8. `recommend_recovery_action(case_id, diagnosis, risk_level, recoverability_score)`: Generates action proposal.
9. `create_retry_request(case_id, retry_type, delay_minutes)`: Stages scheduled retry.
10. `create_payment_link(case_id, amount, expiry_hours)`: Stages Razorpay payment link.
11. `send_recovery_notification(case_id, channel, message)`: Dispatches customer dunning communication.
12. `create_human_review(case_id, reason, priority)`: Escalates high-risk cases for merchant review.
13. `verify_payment_status(case_id, external_ref)`: Checks outcome status.
14. `record_audit_event(case_id, event, decision, reason)`: Logs immutable audit entry.
15. `get_recovery_metrics()`: Aggregates real-time pipeline performance.

---

## 3. Structured Output Contract

The agent guarantees valid JSON outputs adhering to this schema:
```json
{
  "case_id": "case_123",
  "diagnosis": "Customer balance shortfall on account debit",
  "risk_level": "MEDIUM",
  "recoverability_score": 76.0,
  "recommended_action": "DELAYED_RETRY",
  "expected_recovery": 4999.0,
  "confidence": 0.93,
  "requires_human_approval": false,
  "reasoning_summary": "Payment failed due to insufficient funds. Customer has a 96% track record. Recommending a smart delayed retry."
}
```
Chain-of-thought is never exposed externally; only business-facing reasoning summaries are stored.
