# 5-Minute Pitch & Demonstration Script — RazorRecover AI

**Tagline**: *"Find revenue at risk. Recover it safely."*  
**Submission**: Razorpay AI Buildathon 2026 — Track 03: AI Revenue Recovery

---

## 0:00 – 0:30: The Problem
"Payment failures cost Indian merchants up to 15% to 25% of their total digital revenue. Today, recovery is either completely dumb—like blindly retrying an expired card or hammering a customer account with fees—or completely manual. Naive retries annoy customers, trigger issuer fraud flags, and miss critical recovery windows. Merchants need an intelligent, safe way to recapture revenue at risk without risking brand reputation or compliance."

---

## 0:30 – 1:00: The Solution — RazorRecover AI
"Meet **RazorRecover AI**: an autonomous revenue recovery platform built for Razorpay merchants. 
RazorRecover AI detects revenue at risk, diagnoses root causes with an AI agent, passes every recommendation through a deterministic safety engine, executes safe recovery actions, verifies captured funds, and proves the result in an immutable audit trail.
Our foundational principle: **An AI model is never allowed to directly control money movement.**"

---

## 1:00 – 3:00: Live Interactive Demo (The Acme Media Case)
1. **Open Dashboard**:
   - Point to the environment badge: `SIMULATOR MODE` (or `RAZORPAY TEST MODE`).
   - Point to the top KPIs: Revenue at Risk, Revenue Recovered, Recovery Rate.
2. **Click `RUN DEMO`**:
   - Step 1: An incoming payment failure of ₹4,999 appears for **Acme Media** (`INSUFFICIENT_FUNDS`).
   - Step 2: Deterministic risk engine calculates Risk: 45 (Medium) and Recoverability: 78%.
   - Step 3: AI Agent diagnoses customer balance shortfall and recommends `DELAYED_RETRY` with 94% confidence.
   - Step 4: Deterministic Policy Engine verifies safety limits: amount is under ₹25,000 threshold and retry attempts are clean (`APPROVED`).
   - Step 5: Simulator executes scheduled retry, verifies capture outcome, and confirms **₹4,999 RECOVERED**.
   - Show how the audit log and dashboard metrics immediately reflect the verified recovery.
3. **Show Human-In-The-Loop Approval Center**:
   - Open Human Approvals tab: show how transactions > ₹25,000 or low-confidence actions are securely held for merchant authorization with Approve/Reject buttons.

---

## 3:00 – 4:00: Empirical Evaluation Metrics (500-Case Benchmark)
1. **Navigate to `Evaluation Benchmark`**:
   - Click `Run Evaluation (500 Cases)`.
   - Highlight the side-by-side comparison:
     - **Naive Baseline Recovery Rate**: ~38%
     - **RazorRecover AI Recovery Rate**: ~74%
     - **Incremental Capital Recovered**: +₹850,000+ INR over baseline.
     - **Unsafe Decisions Blocked**: Zero false-positive retries on stolen cards.
   - Walk through the scenario breakdown chart: show how RazorRecover AI recovers expired cards and 3DS drop-offs using payment links where the baseline failed completely.

---

## 4:00 – 4:40: Architecture & Safety Guardrails
1. **Explain the Pipeline**:
   `DETECT → DIAGNOSE → DECIDE → SAFETY CHECK → EXECUTE → VERIFY → AUDIT → MEASURE`.
2. **Highlight the 15 Controlled Tools**:
   The agent has zero direct SQL access; all context is accessed through typed tool interfaces.
3. **Highlight the Deterministic Policy Engine**:
   Max retries, retry cooldowns, contact frequency limits, and amount ceilings are enforced with deterministic code, not LLM prompts.

---

## 4:40 – 5:00: Why This Matters & Closing
"RazorRecover AI turns revenue recovery from a leaky bucket into an autonomous, safe financial profit center. It protects merchant cash flow, eliminates customer friction, and proves every rupee recovered. 
Thank you!"
