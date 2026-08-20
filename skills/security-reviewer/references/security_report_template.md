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

## False Positive & Low-Impact Filter Log
- **Filtered Items**:
  - `[Ignored]`: DoS concern on bulk search endpoint (Infrastructure-level control).

## Actionable Security Findings (if status = FAIL)

### High / Medium Severity Vulnerabilities
1. **[Vulnerability Category]**: <Description>
   - **Location**: `file_path.py:L42`
   - **Impact**: <Potential impact>
   - **Required Remediation**: <Specific fix for Constructor>
```
