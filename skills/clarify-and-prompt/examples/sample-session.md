# Sample Session: Clarify and Prompt

This example demonstrates a complete 1-round framework-driven clarification and prompt generation flow.

---

## Turn 1: User's Initial Request

> **User:** I want to add a webhook notification feature to our existing order system so we can notify a partner whenever an order status changes. Help me clarify the requirements and write a detailed prompt I can give to a coding agent.

---

## Turn 2: Agent Clarifies (Phase 1 & Phase 2)

*(Agent routes the request through JTBD, MECE/Socratic Quantification, and Pre-mortem Inversion, then asks 4 bounded questions with recommended defaults.)*

> **Agent:** To build a complete, zero-ambiguity prompt for the coding agent, please confirm these 4 decisions (you can reply briefly like `1A, 2A, 3B...`):
>
> 1. **[JTBD & Socratic SLA] Delivery Mechanism & Retry Policy:**
>    - **A *(Recommended — prevents blocking order updates)*:** Dispatch asynchronously via background queue with exponential backoff retries (up to 5 attempts) on network timeout or HTTP `5xx` / `429`.
>    - **B:** Send synchronously inside the order status update request.
>
> 2. **[MECE — Security] Payload Signing & Authentication:**
>    - **A *(Recommended — industry standard)*:** Sign payloads with `HMAC-SHA256` in `X-Webhook-Signature` alongside `X-Webhook-Timestamp` to prevent replay attacks.
>    - **B:** Send a static Bearer token / API key header.
>
> 3. **[First Principles — Scope] Endpoint Configuration & Audit Log:**
>    - **A *(Recommended for multi-partner)*:** Store partner endpoints in a `webhook_endpoints` DB table and log every attempt in `webhook_deliveries`.
>    - **B *(Recommended for single partner)*:** Configure the single partner URL/Secret via environment variables (`.env`), and only create the `webhook_deliveries` table in DB for delivery auditing.
>
> 4. **[Pre-mortem — Tech Stack & Guardrails] Current Stack & Non-Goals:**
>    - What is your current backend stack + background worker (e.g., FastAPI + SQLAlchemy + `arq`, or NestJS + BullMQ), and are there any existing modules the agent must NOT touch?

---

## Turn 3: User Replies

> **User:** 1A, 2A, and 3B since we only have one partner right now, but definitely keep the `webhook_deliveries` table for auditing. Stack is FastAPI + SQLAlchemy 2.0 (async) + PostgreSQL, using `arq` (Redis) for background jobs. Don't touch our existing payment service.

---

## Turn 4: Agent Synthesizes & Generates Prompt (Phase 3 & Phase 4)

> **Agent:**
>
> ### Agreed Summary
> - **Situation & Complication (SCQA):** The FastAPI order system needs to notify an external partner whenever an `Order` changes status without slowing down core order mutations or losing events during partner downtime.
> - **Core Objective (JTBD):** When an order status update commits, asynchronously dispatch a signed webhook event via `arq` and record every delivery attempt in PostgreSQL for auditability.
> - **Key Decisions & Quantified Constraints (Socratic & MECE):** FastAPI + Async SQLAlchemy 2.0 + PostgreSQL + `arq` (Redis); partner URL/Secret loaded from `.env`; `HMAC-SHA256` signature with timestamp; max 5 retries with exponential backoff; 10s HTTP timeout per attempt.
> - **Guardrails & Non-Goals (Pre-mortem):** Do NOT build a multi-tenant endpoint CRUD API/table; do NOT block the main order HTTP transaction; do NOT touch the payment service; do NOT retry on `4xx` responses (except `429`).
> - **Assumptions:** Outbound HTTP requests use `httpx.AsyncClient(timeout=10.0)`; backoff schedule is `15s, 60s, 300s, 900s`.
>
> Here is the complete prompt, ready to paste into your coding agent:
>
> ````markdown
> # Objective (JTBD)
> In this FastAPI + Async SQLAlchemy 2.0 + PostgreSQL + `arq` codebase, when an `Order` status changes, asynchronously dispatch a signed outbound webhook via `arq` and persist delivery state in PostgreSQL so that our partner receives reliable notifications without degrading order API latency.
>
> # Context & Problem Framing (SCQA)
> - **Situation (Current State):** The application runs on FastAPI, SQLAlchemy 2.0 (Async), PostgreSQL, and `arq` (Redis background worker).
> - **Complication (Why Change Now):** Partner systems require real-time order status updates with cryptographic verification and retry resilience, while we need an audit trail of every delivery attempt.
> - **Architecture Scope:** Because we currently integrate with a single partner, load `WEBHOOK_TARGET_URL` and `WEBHOOK_SECRET` from environment settings (Pydantic `BaseSettings`) rather than creating an endpoint management table.
>
> # Requirements & Quantified Constraints (MECE + Socratic)
>
> ## 1. Database Schema (`webhook_deliveries`)
> Create an Async SQLAlchemy model and Alembic migration for `webhook_deliveries`:
> - `id`: UUID (Primary Key)
> - `event_id`: UUID (Unique idempotency key for the event)
> - `order_id`: Foreign key / reference to the order
> - `event_type`: String (e.g., `order.status_changed`)
> - `payload`: JSONB (Full JSON payload sent)
> - `status`: Enum (`PENDING`, `SUCCESS`, `FAILED`)
> - `attempt_count`: Integer (default `0`)
> - `last_response_code`: Integer, nullable
> - `last_error`: Text, nullable
> - `next_retry_at`: Timestamp (timezone-aware), nullable
> - `created_at`, `updated_at`: Timestamp (timezone-aware)
>
> ## 2. Payload Contract & Security (HMAC-SHA256)
> - **JSON Body:**
>   ```json
>   {
>     "event_id": "<uuid>",
>     "event_type": "order.status_changed",
>     "occurred_at": "<ISO-8601 UTC timestamp>",
>     "data": {
>       "order_id": "<id>",
>       "old_status": "<old_status>",
>       "new_status": "<new_status>",
>       "updated_at": "<ISO-8601 UTC timestamp>"
>     }
>   }
>   ```
> - **Required HTTP Headers:**
>   - `Content-Type: application/json`
>   - `X-Webhook-Id: <event_id>`
>   - `X-Webhook-Timestamp: <unix_epoch_seconds>`
>   - `X-Webhook-Signature: sha256=<hex_digest>` computed via `HMAC-SHA256(WEBHOOK_SECRET, f"{timestamp}.{raw_json_body}")`.
>
> ## 3. Execution Flow & Retry SLA (`arq` Worker)
> - After an order status transition commits to PostgreSQL:
>   1. Insert a `webhook_deliveries` row with `status = PENDING`.
>   2. Enqueue the `deliver_order_webhook(delivery_id)` job in `arq`.
> - Inside `deliver_order_webhook`:
>   - Send an HTTP `POST` using `httpx.AsyncClient(timeout=10.0)` to `WEBHOOK_TARGET_URL`.
>   - **On HTTP `2xx`:** Set `status = SUCCESS`, increment `attempt_count`, record `last_response_code`, clear `next_retry_at`.
>   - **On Network Error, Timeout, HTTP `5xx`, or `429`:**
>     - Increment `attempt_count` and store `last_response_code` / `last_error`.
>     - If `attempt_count < 5`: Schedule retry with exponential backoff (`15s, 60s, 300s, 900s`) and update `next_retry_at`.
>     - If `attempt_count >= 5`: Mark `status = FAILED` and stop retrying.
>   - **On HTTP `4xx` (except `429`):** Increment `attempt_count`, mark `status = FAILED` immediately, and do not retry.
>
> ## Pre-mortem Guardrails & Non-Goals (Inversion)
> - **Strict Non-Goals:**
>   - Do NOT create a `webhook_endpoints` table or CRUD endpoints.
>   - Do NOT touch or refactor anything inside the payment module/service.
>   - Do NOT make synchronous outbound HTTP calls inside the order mutation request cycle.
> - **Failure Modes to Prevent:**
>   - Never log or persist `WEBHOOK_SECRET` in plaintext logs or database columns.
>   - Ensure HMAC signing uses the exact serialized UTF-8 byte payload sent over the wire to avoid signature mismatches due to key-ordering differences.
>
> # Suggested Implementation Steps
> 1. Inspect existing repository layout (`models/`, `settings`, order service, `arq` worker configuration) to match project conventions.
> 2. Add `WEBHOOK_TARGET_URL` and `WEBHOOK_SECRET` to Pydantic settings.
> 3. Implement `WebhookDelivery` model and Alembic migration.
> 4. Implement `webhook_signer.py` and the `deliver_order_webhook` `arq` task.
> 5. Hook the delivery creation + job enqueue into the order status transition service.
> 6. Write unit tests covering: HMAC signature generation, `200 OK` delivery, `503`/timeout backoff retry up to 5 attempts, and immediate failure on `400 Bad Request`.
>
> # Acceptance Criteria & Verification
> - [ ] `X-Webhook-Signature` matches `HMAC-SHA256(secret, "{timestamp}.{raw_body}")`.
> - [ ] `200 OK` response transitions `webhook_deliveries.status` to `SUCCESS` with `attempt_count == 1`.
> - [ ] `500` or timeout schedules retries up to 5 attempts before transitioning to `FAILED`.
> - [ ] `400` response transitions immediately to `FAILED` with zero retries.
> - [ ] All new and existing `pytest` suites pass with zero errors.
> ````
>
> Would you like to adjust any section of this prompt or save it to a file (e.g., `.temp/webhook-prompt.md`)?
