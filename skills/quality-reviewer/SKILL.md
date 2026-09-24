---
name: quality-reviewer
version: "1.0.0"
description: |
  Invoked via `/quality-reviewer`. Audits implementation code against a 12-point quality checklist: design integrity, complexity, error handling, naming, comments, style, test coverage, and documentation. Issues a quality approval (APPROVED/CHANGES_REQUESTED) in wiki/<feature>/quality-review.md. Does not review security vulnerabilities, conduct penetration testing, or write code — only evaluates the quality of what Constructor built.
---

# Quality Reviewer Skill

Audit source code and test logs in `evidence.md` against the 12-point quality checklist. Loop with Constructor until all criteria pass.

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
       ├──► [4a. quality-reviewer]  <=== (YOU ARE HERE) ──(loop)──┐
       │                                                         ▼
       └──► [4b. security-reviewer] ──────────────────────(loop)──┴─► [User Confirmation]
```

## Workflow

```
[Constructor Outputs: Source Code & evidence.md]
                          ↓
1. Discovery (Find changed files in evidence.md)
                          ↓
2. 12-Point Inspection (references/quality_checklist.md)
                          ↓
3. Report Decision (wiki/<feature>/quality-review.md)
                          ↓
4. Constructor Feedback Loop (Up to max iterations)
                          ↓
5. Validate Report (validate_quality_review.py)
                          ↓
6. Next Step
```

---

### Step 1: Discovery
1. Read `wiki/<NNN>-<feature>/plan.md` and `wiki/<NNN>-<feature>/evidence.md`.
2. List all modified or created source files.
3. Inspect full files, not just git diffs.

---

### Step 2: 12-Point Quality Inspection
Evaluate changes against `references/quality_checklist.md`:

1. **Design & Integration Points**: Clean interfaces, schema validation, and multi-step API chains.
2. **Functionality & Routing Logic**: Route transitions, redirect codes, and route guards.
3. **Error Handling**: Failure fallbacks, error responses, and no silent try/catch blocks.
4. **Edge Cases & Data Boundaries**: Null/empty boundaries, concurrency, and token lifecycles.
5. **Complexity**: No speculative features or over-engineering. Solves the stated problem.
6. **Tests**: Unit and integration coverage for primary paths and failure states.
7. **Naming**: Clear, concise variable, function, and module names.
8. **Comments**: English comments explaining why a choice was made, not what the syntax does.
9. **Style**: Adheres to language and project conventions.
10. **Consistency**: Matches patterns in the existing codebase.
11. **Documentation**: Updates to READMEs, API contracts, or schemas when affected.
12. **Line-by-line Context**: Inspect every line of changed code in system context.

---

### Step 3: Report Generation
Write `wiki/<NNN>-<feature>/quality-review.md` using `references/review_report_template.md`:

- **Status**:
  - `APPROVED`: Meets all 12 criteria.
  - `CHANGES_REQUESTED`: Issues must be fixed by Constructor.
- Frontmatter: set `id` (`qreview-xxx`), `title`, `derived_from` (`evidence-xxx`), `status`, and `iteration` (1 to N).
- Max iterations: Read `max_review_iterations` from `wiki/registry.yaml` (default: 3).

---

### Step 4: Constructor Feedback Loop
If status is `CHANGES_REQUESTED`:
1. Send feedback citing file paths, line numbers, and concrete fixes.
2. Constructor refactors code, runs tests, and updates `evidence.md`.
3. Re-evaluate up to `max_review_iterations`.
4. When all issues are resolved, set status to `APPROVED`.

---

### Step 5: Validate Quality Review
Run the validator:
```bash
python <SKILLS_DIR>/quality-reviewer/scripts/validate_quality_review.py wiki/<NNN>-<feature>/quality-review.md
```
Sync the registry:
```bash
python <SKILLS_DIR>/wiki-manager/scripts/wiki_tool.py sync
```

---

### Step 6: Next Step
- If `CHANGES_REQUESTED`: Tell Constructor to address the findings in `quality-review.md`.
- If `APPROVED`:
  - If `security-review.md` is missing, tell the user to run `/security-reviewer`.
  - If `security-review.md` is already passed, tell the user the feature is ready for final confirmation.
