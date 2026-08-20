---
name: security-reviewer
description: Review source code, API routes, data handling, authentication, authorization, dependencies, and architecture for security vulnerabilities, compliance, and secret leaks. Use this skill whenever conducting security audits, scanning code for injection vulnerabilities, checking authentication flaws, applying false positive filtering, or issuing security pass/fail decisions.
---

# Security Reviewer Skill

The **Security Reviewer** skill guides AI agents in performing security audits and static vulnerability analyses on code produced by Constructor. It identifies security vulnerabilities across 10 critical categories, applies false positive filtering, and issues formal security review decisions (`PASS` or `FAIL`).

## Operational Workflow

When conducting a security review, follow these 5 steps sequentially:

```
[Constructor Codebase Diffs & evidence.md]
                       ↓
1. Scope & Target Discovery (wiki-manager skill)
                       ↓
2. 10-Category Vulnerability Analysis (vulnerability_catalog.md)
                       ↓
3. False Positive & Impact Filtering (false_positive_rules.md)
                       ↓
4. Report Generation & Decision (security-review.md)
                       ↓
5. Validation (validate_security_review.py)
```

---

### Step 1: Scope & Target Discovery
1. Read `wiki/<NNN>-<feature>/plan.md` and `wiki/<NNN>-<feature>/evidence.md` using the `wiki-manager` skill.
2. Identify all modified files, API routes, database schemas, authentication boundaries, and third-party dependencies.
3. Pay special attention to untrusted input handling, SQL/Command generation, authentication checks, data serialization, and secret storage.

---

### Step 2: 10-Category Vulnerability Analysis
Scan code for vulnerabilities listed in [references/vulnerability_catalog.md](file:///.agents/skills/security-reviewer/references/vulnerability_catalog.md):

1. **Injection Attacks**: SQLi, Command Injection, LDAP, XPath, NoSQL, XXE.
2. **Authentication & Authorization**: Broken auth, privilege escalation, IDOR, authorization bypass, session management flaws.
3. **Data Exposure**: Hardcoded credentials/tokens, sensitive logging (passwords, PII, API keys), unencrypted data transmission.
4. **Cryptographic Issues**: Weak hashing/ciphers (MD5, SHA1, DES), hardcoded secret keys, insecure random number generation.
5. **Input Validation**: Missing boundary validation, dangerous string formatting, unvalidated buffer bounds.
6. **Business Logic Flaws**: Race conditions, Time-of-Check to Time-of-Use (TOCTOU), rate/state manipulation.
7. **Configuration Security**: Insecure default settings, missing security headers, overly permissive CORS policies (`*`).
8. **Supply Chain Security**: Vulnerable or outdated dependencies, typosquatting risks.
9. **Remote Code Execution**: Dangerous deserialization (Python `pickle`, Java deserialization, `eval()`, `exec()`).
10. **Cross-Site Scripting (XSS)**: Reflected, stored, or DOM-based XSS in frontend templates/responses.

---

### Step 3: False Positive & Impact Filtering
Apply filtering guidelines from [references/false_positive_rules.md](file:///.agents/skills/security-reviewer/references/false_positive_rules.md) to eliminate low-impact or irrelevant findings:

- **Exclude Low-Impact Findings**:
  - Pure Denial of Service (DoS) or CPU/memory exhaustion concerns without execution impact.
  - Generic rate limiting recommendations.
  - Theoretical input validation issues without exploitable vectors or proven impact.
  - Open redirect vulnerabilities unless tied to OAuth token leakage.

Focus exclusively on actionable, high-impact security vulnerabilities that compromise system integrity or data privacy.

---

### Step 4: Report Generation & Security Decision
Using the template in [references/security_report_template.md](file:///.agents/skills/security-reviewer/references/security_report_template.md), create `wiki/<NNN>-<feature>/security-review.md`:

- **Status Decision**:
  - `PASS`: Zero high/medium severity true-positive vulnerabilities detected.
  - `FAIL`: Actionable vulnerabilities found; Constructor must patch them.
- Frontmatter metadata required: `id` (`sreview-xxx`), `title`, `derived_from` (`evidence-xxx`), `status` (`PASS` or `FAIL`), `iteration` (1 to N).
- **Max iterations**: Read from `wiki/registry.yaml` → `max_review_iterations` (defaults to `3` if not set). Loop with Constructor up to that limit.

---

### Step 5: Validate Security Review Document
Run the validator script to verify report structure and frontmatter:
```bash
python .agents/skills/security-reviewer/scripts/validate_security_review.py wiki/<NNN>-<feature>/security-review.md
```
Then sync the LLM Wiki index:
```bash
python .agents/skills/wiki-manager/scripts/wiki_tool.py sync
```
