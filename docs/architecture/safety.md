# Safety & Deterministic Policy Engine — RazorRecover AI

## 1. The Core Fintech Safety Principle
**Under NO circumstances is an LLM or generative model permitted to initiate money movement directly.**

```
[ AI Recommendation ]
         ↓
[ Deterministic Policy Engine ] ──(Violates Rules)──→ [ BLOCKED & AUDITED ]
         ↓ (Passes Rules)
[ Risk & Amount Checks ] ─────────(> ₹25k / Low Conf)─→ [ HUMAN APPROVAL ]
         ↓ (Clean)
[ EXECUTE & VERIFY ]
```

---

## 2. Hard Policy Guardrails

| Policy Rule | Condition | Decision | Explanation |
|---|---|---|---|
| **ACTION_WHITELIST** | Proposed action not in catalog | `BLOCK` | AI hallucinations of arbitrary actions are rejected immediately. |
| **CUSTOMER_OPT_OUT** | Customer opted out of notifications | `BLOCK` | Prevents dunning compliance violations. |
| **RECOVERY_WINDOW** | Failure age > 14 days | `BLOCK` | Reclaiming stale debts without reauthorization violates payment network rules. |
| **MAX_RETRIES** | `attempt_count >= 3` | `BLOCK` | Prevents issuer blocking and overdraft fees. |
| **RETRY_COOLDOWN** | Re-attempt within 60 minutes | `BLOCK` | Prevents card hammering and issuer rate-limiting. |
| **MAX_CONTACT_ATTEMPTS** | Contact count >= 2 | `BLOCK` | Prevents spamming customer with excessive notifications. |
| **MAX_AUTOMATIC_AMOUNT** | Amount > ₹25,000 INR | `REQUIRE_HUMAN_APPROVAL` | High-value payments must have merchant finance sign-off. |
| **CONFIDENCE_THRESHOLD** | Agent confidence < 0.70 | `REQUIRE_HUMAN_APPROVAL` | Ambiguous diagnostics cannot execute autonomously. |
| **CRITICAL_RISK** | Risk score > 80 (CRITICAL) | `REQUIRE_HUMAN_APPROVAL` | Critical risk accounts mandate human evaluation. |

Every policy check generates an immutable `policy_decisions` entry and audit record detailing the exact rule triggered and justification.
