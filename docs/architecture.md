# RazorRecover AI — System Architecture

## 1. Overview
RazorRecover AI is an autonomous, policy-bounded revenue recovery platform engineered for high-volume merchant ecosystems powered by **Razorpay Test Mode** and **Firebase Firestore**.

```
                           +------------------------+
                           |  User / Merchant UI    |
                           |    (Next.js App)       |
                           +-----------+------------+
                                       | HTTP / REST
                                       v
                     +------------------------------------+
                     |       FastAPI Backend API          |
                     | ├── Risk Engine (Deterministic)    |
                     | ├── AI Agent (Gemini Reasoning)    |
                     | ├── Policy Engine (Strict Guard)   |
                     | ├── Recovery Orchestrator          |
                     | ├── Razorpay Integration           |
                     | ├── Webhook Processor (HMAC SHA256)|
                     | └── Audit Service (Append-only)    |
                     +-----------------+------------------+
                                       |
                   +-------------------+-------------------+
                   |                                       |
                   v                                       v
       +-----------------------+               +-----------------------+
       |   Razorpay Test Mode  |               |  Firebase Firestore   |
       |  - Payments API       |               |  - recoveryCases      |
       |  - Payment Links API  |               |  - payments           |
       |  - Webhook Ingestion  |               |  - webhookEvents      |
       +-----------+-----------+               |  - auditEvents        |
                   |                           |  - aiDecisions        |
                   v                           |  - policyDecisions    |
          Google Gemini LLM                    +-----------------------+
       (gemini-3.6-flash / fallback)
```

---

## 2. Core Architectural Components

### 2.1 Next.js 14 Merchant Frontend
- **Design Aesthetic**: Modern, white fintech interface with subtle card borders, neutral charcoal typography, and high-contrast status accents (Emerald for Verified Recoveries, Amber for Human Approval, Rose for Failures).
- **Zero-Secret Exposure**: No secret keys (`RAZORPAY_KEY_SECRET`, `GEMINI_API_KEY`, Firebase private credentials) exist in client components, build artifacts, or local storage.
- **Provenance Badges**: Real-time badges transparently differentiate `RAZORPAY TEST MODE`, `FIRESTORE`, and `SYNTHETIC BENCHMARK` data.

### 2.2 FastAPI Backend Core
- **Deterministic Revenue Risk Engine**: Analyzes failure reason codes, transaction value, customer historical success rates, and retry counts to generate reproducible risk scores (0–100) and recoverability scores (0–100).
- **Gemini Intelligence Layer**: Utilizes `gemini-3.6-flash` / `gemini-flash-latest` to synthesize qualitative failure context, merchant notes, and historical patterns into structured JSON recovery recommendations. Contains an instant deterministic fallback engine if external AI calls experience latency or rate limits.
- **Deterministic Policy & Safety Engine**: Acts as an unbypassable gatekeeper. Enforces hard safety boundaries:
  - Stop after verified payment
  - Maximum 2 recovery attempts per invoice
  - Hard autonomous monetary ceiling (INR 10,000 threshold triggers mandatory human review)
  - Critical risk cases (>80) trigger mandatory human review
  - AI confidence threshold (<0.70 triggers human review)
  - Unsupported action blocking
  - Cooldown period enforcement between attempts

### 2.3 Recovery Orchestrator & Razorpay Service
- Interacts exclusively with official Razorpay APIs in Test Mode (`https://api.razorpay.com/v1`).
- Generates genuine Razorpay Test Mode Payment Links (`https://rzp.io/...`) for active cases.
- Fetches real-time transaction verification details directly from Razorpay servers.

### 2.4 Webhook Processor & Idempotency
- Listens on `POST /api/webhooks/razorpay`.
- Computes and verifies `X-Razorpay-Signature` via HMAC-SHA256 using `RAZORPAY_WEBHOOK_SECRET`.
- Enforces strict event idempotency using Razorpay event IDs to guarantee zero double-counting of recovered revenue.

### 2.5 Dual-Persistence Engine (SQLite + Firebase Firestore)
- **Primary Cloud DB**: Firebase Firestore (`razorrecover-ai-88f4c`) stores all business documents:
  - `recoveryCases/{caseId}`
  - `payments/{paymentId}`
  - `customers/{customerId}`
  - `paymentLinks/{paymentLinkId}`
  - `webhookEvents/{eventId}`
  - `aiDecisions/{decisionId}`
  - `policyDecisions/{decisionId}`
  - `humanApprovals/{approvalId}`
  - `auditEvents/{eventId}`
- **High-Speed Cache**: Local SQLite DB provides instant relational indexing and millisecond query times for the frontend dashboard.
