# Implementation Guidelines for Constructor Agent

## 1. Task State & Todo Tracking
- Always parse all tasks from `plan.md` before writing code.
- Convert tasks into a clean checklist:
  - `[ ] Task I-001: Description`
  - `[ ] Task I-002: Description`
  - `[ ] Task T-003: Description`
- Update task status sequentially as work progresses.

## 2. Skill Auto-Discovery
- Look for project configuration files (`package.json`, `pyproject.toml`, `requirements.txt`, `go.mod`, `Cargo.toml`).
- Auto-detect libraries and frameworks (e.g. Next.js, React, FastAPI, SQLAlchemy, Pytest, Jest, Vitest).
- If skills exist in `.agents/skills/` or user's skill catalog matching the tech stack, load and follow their best practices.

## 3. Code Implementation Best Practices
- **No Mock Fallbacks**: Write genuine, fully functional logic. Do not write placeholder stubs that bypass real logic.
- **English Comments**: Write comments in English explaining business rationale and non-obvious algorithms.
- **No Unused Code**: Clean up temporary test files or scratch scripts before finalizing.
- **Exact Signatures**: Match interface declarations and types across callers and implementations.

## 4. Test Evidence & Verification
- Execute actual test runners (`pytest`, `npm test`, `vitest`, etc.) using shell commands.
- Never fake test logs or fabricate exit codes.
- Save full output into `## Test Verification & Logs` inside `evidence.md`.

## 5. Review Feedback Loops (Quality & Security)
- If **Quality Reviewer** requests refactoring:
  - Check code against quality checklist (design, functionality, complexity, naming, comments, style, consistency).
  - Apply requested refactoring cleanly without breaking existing tests.
- If **Security Reviewer** reports vulnerabilities:
  - Verify if vulnerability is a true positive (SQL injection, XSS, insecure auth, secret leak, etc.).
  - Implement security patches immediately and re-run tests.
- Re-run `validate_evidence.py` after updating `evidence.md`.
