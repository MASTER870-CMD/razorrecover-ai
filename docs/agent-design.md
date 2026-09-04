# RazorRecover AI — Agent Design & Decision Loop

## 1. Core Philosophy: The Separation of Intelligence and Execution

In mission-critical financial software, **an AI model must never possess autonomous authority to move funds, initiate arbitrary charges, or bypass safety guardrails.**

RazorRecover AI enforces a strict architectural boundary:
- **AI Recommends**: Gemini analyzes failure context and recommends optimal recovery strategies.
- **Deterministic Policy Controls**: Hard-coded mathematical rules validate every proposed action before execution.
- **Backend Executes**: Bounded handlers execute only supported Razorpay API calls (e.g., Payment Link creation).
- **Razorpay Verifies**: Payment success is confirmed only by authentic Razorpay cryptographic webhook signatures or direct API verification.

```
       [ AI Agent ]             [ Policy Engine ]          [ Recovery Worker ]
   Generates Hypothesis   ==>    Enforces Constraints  ==>  Executes Razorpay Link
   (Strategy, Confidence)        (Allowed / Blocked /        (Only if Approved)
                                  Human Review)
```

---

## 2. The 8-Stage Agent Loop

```
    1. OBSERVE   ───>  2. DIAGNOSE  ───>  3. SCORE  ───>  4. DECIDE
        │                                                     │
        v                                                     v
    8. AUDIT    <───   7. VERIFY   <───   6. ACT   <───  5. GUARD
```

### Stage 1: OBSERVE
- **Trigger**: Razorpay payment failure event or batch sync ingestion.
- **Data Ingestion**: Captures payment ID, currency, amount, error code, error description, customer identifier, and timestamp.
- **Context Gathering**: Queries historical customer transactions, previous recovery attempts, and customer lifetime value (LTV).

### Stage 2: DIAGNOSE
- **Failure Classification**: Distinguishes between temporary infrastructure issues (`INSUFFICIENT_FUNDS`, `NETWORK_FAILURE`, `OTP_EXPIRED`), terminal failures (`EXPIRED_CARD`, `DO_NOT_HONOR`, `ACCOUNT_CLOSED`), and fraud/security blocks.
- **Gemini Reasoning**: Sends qualitative context to Gemini (`gemini-3.6-flash`). The model outputs structured diagnosis and candidate strategies (`PAYMENT_LINK`, `SMART_RETRY_SCHEDULE`, `CUSTOMER_OUTREACH`).

### Stage 3: SCORE
- **Deterministic Risk Engine**: Computes a reproducible risk score (0–100) and recoverability score (0–100).
- **Input Weights**:
  - Failure Category Severity: +10 to +40 points
  - Amount Factor: Logarithmic scaling based on invoice size
  - Customer Past Success Rate: Inversely correlated to risk
  - Prior Failed Recovery Attempts: Significant risk penalty (+20 points per prior failure)

### Stage 4: DECIDE
- AI proposes an actionable plan with confidence rating (0.0 to 1.0) and supporting reasoning.
- Fallback Engine: If Gemini is unreachable or returns invalid JSON, the deterministic fallback engine generates a rule-based recommendation immediately.

### Stage 5: GUARD (The Safety Gate)
- Every proposal is processed by the **Deterministic Policy Engine**.
- The proposal is evaluated against 13 strict rules:
  1. No recovery on already paid/settled payments.
  2. Maximum 2 attempts per invoice.
  3. No duplicate active payment links.
  4. Amounts >= ₹10,000 require **Human Approval**.
  5. Critical risk scores (>= 80) require **Human Approval**.
  6. AI confidence (< 0.70) requires **Human Approval**.
  7. Customer opt-outs block recovery immediately.
  8. Minimum 4-hour cooldown between attempts.
  9. Unsupported actions are blocked unconditionally.
- **Outputs**: `ALLOWED`, `REQUIRES_HUMAN_APPROVAL`, or `BLOCKED`.

### Stage 6: ACT
- If `ALLOWED` (or `APPROVED` by human operator):
  - Calls official Razorpay Test Mode API to generate a verifiable Payment Link (`https://rzp.io/...`).
  - Records the link ID and reference ID in the database and Firebase Firestore.
- If `BLOCKED` or `REJECTED`:
  - Enters terminal state `BLOCKED` or `FAILED`. No payment link is ever generated.

### Stage 7: VERIFY
- The agent **never assumes recovery has succeeded** based on link creation or customer clicks.
- Recovery is marked `RECOVERED` **only when**:
  1. Razorpay webhook event `payment.captured` or `payment_link.paid` is received.
  2. HMAC-SHA256 signature is cryptographically validated using the webhook secret.
  3. Event idempotency check verifies this event was not previously counted.
  4. Amount paid matches the expected recovery amount.

### Stage 8: AUDIT
- Every state transition emits an immutable, append-only audit event:
  - `PAYMENT_FAILED`
  - `AI_DIAGNOSIS_CREATED`
  - `POLICY_EVALUATED`
  - `HUMAN_APPROVAL_REQUESTED`
  - `RECOVERY_ACTION_EXECUTED`
  - `WEBHOOK_RECEIVED`
  - `PAYMENT_VERIFIED`
  - `RECOVERY_CONFIRMED`
- All audit events are synchronized to Firestore (`auditEvents/{id}`) and local SQLite.
