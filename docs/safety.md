# RazorRecover AI — Safety & Governance Specification

## 1. Safety Architecture Overview

RazorRecover AI is designed around a zero-trust model towards generative AI outputs when executing financial workflows. No AI model (including Gemini) has write access to Razorpay credentials or payment authorization capabilities.

---

## 2. Hard Governance Rules & Thresholds

| Rule ID | Parameter | Threshold / Constraint | Action if Breached |
| :--- | :--- | :--- | :--- |
| **POL-01** | Max Recovery Attempts | `<= 2` attempts total | Case `BLOCKED` to prevent customer fatigue |
| **POL-02** | Autonomous Monetary Limit | `>= ₹10,000` | Mandatory `HUMAN_APPROVAL` required |
| **POL-03** | Risk Score Threshold | Risk `>= 80 / 100` | Mandatory `HUMAN_APPROVAL` required |
| **POL-04** | AI Confidence Floor | Confidence `< 0.70` | Mandatory `HUMAN_APPROVAL` required |
| **POL-05** | Double-Recovery Prevention | Payment already `CAPTURED` or `PAID` | Case `BLOCKED`; no action executed |
| **POL-06** | Duplicate Active Link | Active Razorpay link exists | Existing link reused; no new link created |
| **POL-07** | Attempt Cooldown | Minimum 4 hours between attempts | Case `BLOCKED` with `COOLDOWN_ACTIVE` |
| **POL-08** | Customer Opt-out | Customer flagged opted-out | Immediate termination; `BLOCKED` |
| **POL-09** | Action Whitelist | Only `PAYMENT_LINK` is executable | Any unsupported action blocked |
| **POL-10** | Webhook Verification | HMAC-SHA256 signature match | Unverified webhooks rejected (400 Bad Request) |
| **POL-11** | Webhook Idempotency | Unique `event_id` in database | Duplicate events acknowledged but skipped |
| **POL-12** | Settlement Verification | Amount paid == invoice amount | Mismatched amounts flagged for manual review |

---

## 3. Human-in-the-Loop (HITL) Workflow

When a recovery case requires human intervention:
1. The case transitions to `PENDING_HUMAN_APPROVAL`.
2. The AI recommendation and risk assessment are locked in an immutable state.
3. The merchant operator can inspect:
   - Invoice amount and customer lifetime value
   - Complete failure diagnosis and AI rationale
   - Policy trigger reason (e.g. "Amount ₹15,000 exceeds ₹10,000 autonomous threshold")
4. **Operator Decision**:
   - **Approve**: System generates the genuine Razorpay Payment Link and audits operator identity.
   - **Reject**: System cancels the recovery attempt, marks case `FAILED`, and records operator rejection reason.

---

## 4. Webhook Security & Idempotency Guarantee

All external status updates arrive via Razorpay webhooks (`POST /api/webhooks/razorpay`):
- **Signature Validation**: Backend computes `hmac_sha256(raw_body, RAZORPAY_WEBHOOK_SECRET)` and compares with `X-Razorpay-Signature` via constant-time comparison.
- **Idempotency Guard**:
  ```python
  if is_duplicate_event(event_id):
      return {"status": "ignored", "reason": "duplicate"}
  ```
- **Zero Double Counting**: Because updates are executed inside atomic transactions with event ID tracking, duplicate webhook deliveries will never increment recovered revenue metrics more than once.

---

## 5. Security Posture & Secrets Management
- **Zero Client-Side Secrets**: `RAZORPAY_KEY_SECRET`, `RAZORPAY_WEBHOOK_SECRET`, `GEMINI_API_KEY`, and Firebase private credentials are never bundled into frontend code.
- **Masked Credentials**: All UI components display only masked Key IDs (e.g. `rzp_test••••GaE7`).
- **Test Mode Boundary**: Live API keys (`rzp_live_`) are strictly disallowed. The application runs exclusively against Razorpay Test Mode (`rzp_test_`).
