---
name: security-reviewer
version: 1.2.0
license: MIT
description: |
  Invoked via `/security-reviewer`. Runs built-in Python scanners (FastAPI, Next.js, secrets) over implementation code and dependencies, triages their findings, audits the remaining risk across 10 vulnerability categories (injection, auth, data exposure, crypto, etc.), and issues a security pass/fail decision in wiki/<feature>/security-review.md. Does not fix vulnerabilities, write code, or evaluate code style — only audits and reports security findings.
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
1. Discovery & Automated Scan (plan_scan.py → run_scan.py → findings.json)
               ↓
2. Triage findings + 10-Category manual audit + independent verification
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

### Step 1: Discovery & Automated Scan
Code runs first, reading second: the scripts find stacks, attack surface and rule matches deterministically, and your reading in Step 2 is scoped by their output.

1. Read `wiki/<NNN>-<feature>/plan.md` and `wiki/<NNN>-<feature>/evidence.md`.
2. Build the scan plan. Use `--diff <base-ref>` for the feature's changes, or omit it for a full scan:
   ```bash
   python <SKILLS_DIR>/security-reviewer/scripts/plan_scan.py <project-dir> --diff <base-ref> --out wiki/<NNN>-<feature>/scan-plan.json
   ```
3. Read the summary it prints. The plan is the source of truth for scope, not your own file search:
   - **Projects**: detected stacks (`nextjs`, `fastapi`, `generic`) and their roots. Profiles and per-repo overrides are described in `references/scan_profiles.md`.
   - **Hotspots**: attack-surface locations (route handlers, Server Actions, FastAPI endpoints, raw SQL, CORS, ...). Every hotspot must be reviewed in Step 2.
   - **Coverage**: per category, `planned` (a built-in scanner covers it), `degraded` (scanner unavailable — review manually), or `manual`.
   - **Unprofiled files**: changed files no framework profile covers — review them manually.
4. Run the built-in scanners (stdlib Python, no installs). Add `--no-deps` to skip the optional `npm audit` / `pip-audit` registry lookup:
   ```bash
   python <SKILLS_DIR>/security-reviewer/scripts/run_scan.py wiki/<NNN>-<feature>/scan-plan.json
   ```
   This writes `wiki/<NNN>-<feature>/findings.json`. Rules per scanner are listed in `references/scan_rules.md`. Every finding starts as `untriaged`.

---

### Step 2: Triage & 10-Category Vulnerability Analysis
**2a. Triage automated findings.** For each finding in `findings.json`, open the code at `file:line` and decide:
- `confirmed` — the input is attacker-reachable and the impact is real. Fill the four claim fields (**Attacker**, **Entry Point**, **Boundary**, **Impact**) from `references/verification.md`; if Attacker or Impact cannot be made concrete, reject instead.
- `rejected` — with a one-line reason (e.g. "auth enforced by middleware matcher `/api/:path*`", "value is a constant").
- `needs_validation` — the deciding fact is outside the source (deployment config, proxy, IdP).

Record every high/medium finding in the report's `## Automated Scan Triage` table; the validator fails on any that are missing.

**2b. Manual audit.** Scan code for issues in `references/vulnerability_catalog.md`. Scope comes from `scan-plan.json`: review every hotspot, and read code yourself for each category whose coverage status is `degraded` or `manual`, or whose owner is `tool+manual` (authorization, IDOR and business logic cannot be decided by pattern matching).

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
- Each subagent returns: `category`, `file`, `line`, `severity`, `attacker`, `entry_point`, `boundary`, `impact`.
- Merge findings and filter false positives in the main agent.

**2c. Independent verification.** Every high/medium finding you want to mark `confirmed` (from 2a or 2b) goes to a fresh verifier sub-agent whose only job is to disprove it. A different agent from the one that found it confirms it, which removes confirmation bias. Use the prompt and verdict mapping in `references/verification.md`: `upheld` → `confirmed`, `disproved` → `rejected`, `unresolved` → `needs_validation`. Only `upheld` findings can make the status `FAIL`.

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
Sync the registry and log the decision:
```bash
python <SKILLS_DIR>/wiki-manager/scripts/wiki_tool.py sync
python <SKILLS_DIR>/wiki-manager/scripts/wiki_tool.py log "Security Reviewer" "<status> — iteration N"
```

---

### Step 6: Next Step
- If `FAIL`: Tell Constructor to patch vulnerabilities reported in `security-review.md`. If `iteration` already equals `max_review_iterations`, stop the loop and escalate the unresolved findings to the user for a decision (accept risk, extend iterations, or re-scope).
- If `PASS`:
  - If `quality-review.md` is missing, tell the user to run `/quality-reviewer`.
  - If `quality-review.md` is already approved, ask the user for final confirmation; once confirmed, run `wiki_tool.py status <module-id> completed`.
