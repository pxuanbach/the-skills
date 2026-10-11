# Security Review Report Template

Use this template to create `wiki/<NNN>-<feature>/security-review.md`.

```markdown
---
id: sreview-001
title: Security Review Report for <Feature Name>
derived_from:
  - evidence-001
status: PASS # Options: PASS | FAIL
iteration: 1
---

# Security Review Report: <Feature Name>

## Executive Security Summary
- **Final Decision**: PASS / FAIL
- **Iteration**: 1 of 3
- **Audited Components**: API endpoints, DB queries, Auth middleware, Dependencies
- **Scan Plan**: `scan-plan.json` — profiles: nextjs, fastapi; degraded categories: none
- **Total Vulnerabilities Found**: 0 High, 0 Medium, 0 Low

## 10 Vulnerability Categories Scan Results

| # | Vulnerability Category | Status | Findings / Notes |
|---|-----------------------|--------|------------------|
| 1 | Injection Attacks (SQLi, Command, XXE) | PASS | Parameterized queries used |
| 2 | Authentication & Authorization | PASS | Ownership check present on routes |
| 3 | Sensitive Data Exposure & Secrets | PASS | No hardcoded secrets or logging |
| 4 | Cryptographic Weaknesses | PASS | Standard secure hashing used |
| 5 | Input Validation & Boundaries | PASS | Pydantic schema validation active |
| 6 | Business Logic & Race Conditions | PASS | Atomic transactions enforced |
| 7 | Security Configurations & CORS | PASS | Configs secured |
| 8 | Supply Chain & Dependencies | PASS | No vulnerable packages |
| 9 | Remote Code Execution (RCE) | PASS | No dynamic code execution |
| 10| Cross-Site Scripting (XSS) | PASS | Output sanitization verified |

## Automated Scan Triage

Every high/medium finding from `findings.json` must appear here with a verdict (`confirmed` | `rejected` | `needs_validation`). A `confirmed` row needs `Verifier = upheld` (see `references/verification.md`).

| ID | Rule | Severity | Location | Verdict | Verifier | Reason |
|----|------|----------|----------|---------|----------|--------|
| F-1a2b3c4d5e | PY-ROUTE-NOAUTH | high | `app/routers/items.py:12` | rejected | - | Router mounted with `dependencies=[Depends(get_current_user)]` in `main.py` |
| F-9f8e7d6c5b | JS-ACTION-NOAUTH | high | `app/actions/item.ts:7` | confirmed | upheld | See finding 1 |

## False Positive & Low-Impact Filter Log
- **Filtered Items**:
  - `[Ignored]`: DoS concern on bulk search endpoint (Infrastructure-level control).

## Actionable Security Findings (if status = FAIL)

### High / Medium Severity Vulnerabilities
Each finding needs all fields below (validator-enforced). Field rules: `references/verification.md`.

1. **[Authentication & Authorization]**: Server Action deletes items without an ownership check
   - **ID**: F-9f8e7d6c5b
   - **Location**: `app/actions/item.ts:7`
   - **Attacker**: Any logged-in user
   - **Entry Point**: Server Action `deleteItem(id)` (callable directly as POST)
   - **Boundary**: Ownership check missing — `db.item.delete({ where: { id } })` has no `userId` filter
   - **Impact**: Delete any other user's items
   - **Verification**: upheld — trace `app/actions/item.ts:7` → `lib/db.ts:31`
   - **Required Remediation**: Add `userId: session.user.id` to the `where` clause and return 404 when no row matches
```
