---
name: security-reviewer
version: "1.0.0"
description: Review source code, API routes, data handling, authentication, authorization, dependencies, and architecture for security vulnerabilities, compliance, and secret leaks. Use this skill whenever conducting security audits, scanning code for injection vulnerabilities, checking authentication flaws, applying false positive filtering, or issuing security pass/fail decisions. Do NOT use for general code style/linting, architectural design, or initial code implementation.
---

# Security Reviewer Skill

Audit source code and dependencies for vulnerabilities across 10 security categories. Filter false positives and record decisions in `wiki/<NNN>-<feature>/security-review.md`.

## SDLC Workflow Position

```
[0. wiki-manager] (Init & Central Knowledge Hub)
       │
       ▼
[1. requirement-analyzer]
       │
       ▼
[2. user-designer]
       │
       ▼
[3. constructor]
       │
       ├──► [4a. quality-reviewer]  ──────────────────────(loop)──┐
       │                                                         ▼
       └──► [4b. security-reviewer] <=== (YOU ARE HERE) ──(loop)──┴─► [User Confirmation]
```

## Workflow

```
[Constructor Diffs & evidence.md]
               ↓
1. Discovery (Modified files & routes)
               ↓
2. 10-Category Audit (references/vulnerability_catalog.md)
               ↓
3. Filter Low-Impact Items (references/false_positive_rules.md)
               ↓
4. Report Decision (wiki/<feature>/security-review.md)
               ↓
5. Validate Report (validate_security_review.py)
               ↓
6. Next Step
```

---

### Step 1: Discovery
1. Read `wiki/<NNN>-<feature>/plan.md` and `wiki/<NNN>-<feature>/evidence.md`.
2. Find modified files, API routes, database models, and external dependencies.
3. Check input handling, SQL generation, authentication checks, data serialization, and secret storage.

---

### Step 2: 10-Category Vulnerability Analysis
Scan code for issues in `references/vulnerability_catalog.md`:

1. **Injection Attacks**: SQLi, Command Injection, LDAP, XPath, NoSQL, XXE.
2. **Authentication & Authorization**: Broken auth, privilege escalation, IDOR, session flaws.
3. **Data Exposure**: Hardcoded keys/tokens, secret logging, unencrypted transmission.
4. **Cryptographic Issues**: Weak hashing (MD5, SHA1), static keys, predictable random numbers.
5. **Input Validation**: Missing boundaries, unsafe string formatting, buffer overflows.
6. **Business Logic Flaws**: Race conditions, TOCTOU flaws, state manipulation.
7. **Configuration Security**: Insecure defaults, missing security headers, open CORS (`*`).
8. **Supply Chain**: Outdated packages, typosquatting risks.
9. **Remote Code Execution**: Unsafe deserialization (`pickle`, Java), `eval()`, `exec()`.
10. **Cross-Site Scripting (XSS)**: Reflected, stored, or DOM-based XSS.

**Parallel subagents for large features**:
- Split scan scope across 2 subagents when inspecting extensive codebases:
  - Subagent A: injection, auth, data exposure, cryptography.
  - Subagent B: input validation, business logic, configuration, supply chain, RCE, XSS.
- Each subagent returns: `category`, `file`, `line`, `description`, `severity`.
- Merge findings and filter false positives in the main agent.

---

### Step 3: False Positive & Impact Filtering
Apply rules from `references/false_positive_rules.md`:

- Ignore DoS or CPU exhaustion without execution impact.
- Ignore generic rate-limiting recommendations.
- Ignore theoretical validation issues without exploit paths.
- Ignore open redirects unless chained to token theft.

Report only vulnerabilities with concrete exploit paths.

---

### Step 4: Report Generation & Decision
Write `wiki/<NNN>-<feature>/security-review.md` using `references/security_report_template.md`:

- **Status**:
  - `PASS`: Zero high/medium true-positive vulnerabilities.
  - `FAIL`: Actionable vulnerabilities exist. Constructor must patch them.
- Frontmatter: set `id` (`sreview-xxx`), `title`, `derived_from` (`evidence-xxx`), `status`, and `iteration` (1 to N).
- Max iterations: Read `max_review_iterations` from `wiki/registry.yaml` (default: 3).

---

### Step 5: Validate Security Review
Run the validator:
```bash
python <SKILLS_DIR>/security-reviewer/scripts/validate_security_review.py wiki/<NNN>-<feature>/security-review.md
```
Sync the registry:
```bash
python <SKILLS_DIR>/wiki-manager/scripts/wiki_tool.py sync
```

---

### Step 6: Next Step
- If `FAIL`: Tell Constructor to patch vulnerabilities reported in `security-review.md`.
- If `PASS`:
  - If `quality-review.md` is missing, tell the user to run `/quality-reviewer`.
  - If `quality-review.md` is already approved, tell the user the feature is verified and ready for release.
