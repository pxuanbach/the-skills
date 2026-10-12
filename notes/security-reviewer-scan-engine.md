# Security Reviewer — Scan Engine Research (Step 3)

Date: 2026-10-01. Status: implemented in `security-reviewer` 1.2.0 (`plan_scan.py`, `run_scan.py`, `scan_*.py`).

## 1. What the two reference projects actually do

| | alibaba/open-code-review | cloudflare/security-audit-skill |
|---|---|---|
| Type | Go CLI (`ocr review`, `ocr scan`), Apache-2.0 | Agent skill (Markdown + Node validators), MIT |
| Detection engine | **LLM agent**, no AST. Rule docs per file type (`internal/config/rules/rule_docs/python.md`, `ts_js_tsx_jsx.md`) are prompt text | **LLM agents** (hunter → verifier → record verifier). No SAST tool integrated |
| Deterministic part | File selection, file bundling, glob → rule-doc routing (`system_rules.json`, content `sniffer.go`), per-path rules in `.opencodereview/rule.json`, SARIF/JSON output | `coverage-ledger.json` (unit = surface × boundary × attack class), `report-schema.json`, zero-dep validators `validate-findings.cjs`, `validate-coverage-ledger.cjs` |
| FP reduction | "Precision over recall" stance in every rule doc; reflection + positioning modules | The agent that checks a finding is never the agent that found it; verdicts `confirmed` / `needs_validation` / `rejected`; severity = likelihood × impact |

**Conclusion:** neither repo is a deterministic scanner. Both use LLMs for detection and code only for *routing, bookkeeping and validation*. They are good models for the **orchestration and triage layers**, not for the detection engine itself. The detection engine has to come from SAST tooling.

### Ideas adopted

- From open-code-review: glob + sniff routing (done in `plan_scan.py`), path-scoped repo overrides (`.security-reviewer.json`), SARIF output, precision-over-recall default.
- From cloudflare: coverage ledger with explicit status (done: `planned`/`degraded`/`manual`), three-verdict triage, zero-dep validators that gate the report, stable fingerprints so re-runs don't re-litigate rejected findings.

## 2. Decision (2026-10-01): built-in Python, no external SAST

Opengrep / Semgrep + gitleaks + osv-scanner were evaluated (Opengrep is the LGPL-2.1 fork of Semgrep CE with cross-function taint restored; CodeQL needs a build DB and is free only for public repos). They were rejected as overkill for this skill: every reviewer machine would need three extra binaries, and the stack focus is only Next.js + FastAPI.

Shipped instead (stdlib only):

| Script | Technique | Why it is enough |
|---|---|---|
| `scan_python.py` | `ast` visitor | Python's own parser gives real call/argument structure: f-string vs bound params, `shell=True`, `Depends(...)` on route params, router-level `dependencies=`. Cross-file pre-pass resolves `include_router(..., dependencies=[...])`. |
| `scan_js.py` | Regex per line + per-export segments | Next.js risks are mostly syntactic: `"use server"` exports, `route.ts` handlers, `NEXT_PUBLIC_`, `dangerouslySetInnerHTML`, `$queryRawUnsafe`. No TS parser needed for these. |
| `scan_secrets.py` | Known-format regex + assignment heuristics | Covers the gitleaks core cases; values masked. |
| `npm audit` / `pip-audit` | Optional | Used only if already installed. |

Trade-off accepted: no cross-file taint. The triage step (agent reads `file:line` and records `confirmed` / `rejected` / `needs_validation`) absorbs the extra false positives, and the validator enforces that every high/medium finding is triaged. If precision becomes a problem later, the profile `scanners` lists can add `opengrep` ahead of `builtin-*` without changing the rest of the pipeline.

## Sources

- https://github.com/alibaba/open-code-review
- https://github.com/cloudflare/security-audit-skill
- https://semgrep.dev/docs/faq/comparisons/opengrep
- https://appsecsanta.com/sast-tools/opengrep-vs-semgrep
- https://shoulder.dev/rules/fastapi-missing-authentication
