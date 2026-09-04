# Security & Compliance Architecture — RazorRecover AI

## 1. Secrets Management
- **Never expose gateway secrets**: `RAZORPAY_KEY_SECRET` and `GEMINI_API_KEY` are stored strictly in server-side environment variables.
- The web frontend communicates exclusively with the backend API; secrets are never passed to the browser or bundled in client builds.
- Dedicated `.env.example` provides template variables without real keys.

---

## 2. Webhook Security
- All incoming webhooks to `POST /api/webhooks/razorpay` require HMAC-SHA256 signature verification matching `RAZORPAY_WEBHOOK_SECRET`.
- Replay attack mitigation and idempotency keys ensure no transaction is processed twice.

---

## 3. Strict Input & Schema Validation
- All API request bodies and query parameters are strictly validated using Pydantic V2 models.
- LLM outputs are checked against rigid JSON schemas with boundary checks (confidence in `[0.0, 1.0]`, recoverability in `[0.0, 100.0]`).
- State transitions in the recovery lifecycle are validated by `RecoveryStateMachine` to prevent illegal state jumps.

---

## 4. Immutable Audit Trail
- Every event, actor action, policy gate verdict, and verification outcome is written to `audit_logs` with a unique `correlation_id`.
- Audit logs cannot be mutated or deleted by user-facing endpoints.
