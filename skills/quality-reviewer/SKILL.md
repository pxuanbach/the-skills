---
name: quality-reviewer
description: Review source code, implementation plans, and test evidence for quality, design integrity, complexity, test coverage, naming, English comments, style, consistency, documentation, and system health. Use this skill whenever conducting code reviews, auditing PRs/diffs, requesting changes from Constructor, or issuing a quality approval decision.
---

# Quality Reviewer Skill

The **Quality Reviewer** skill guides AI agents in conducting comprehensive code and documentation reviews on artifacts produced by Constructor. It evaluates design, functionality, complexity, test validity, naming, comments, style, consistency, and overall system health before final user confirmation.

## Operational Workflow

When reviewing completed tasks or test evidence from Constructor, follow these 5 steps sequentially:

```
[Constructor Outputs: Source Code & evidence.md]
                          ↓
1. Artifact & Context Discovery (wiki-manager skill)
                          ↓
2. 12-Point Quality Inspection (quality_checklist.md)
                          ↓
3. Review Decision & Report Generation (quality-review.md)
                          ↓
4. Constructor Feedback Loop (Max N iterations)
                          ↓
5. Validation (validate_quality_review.py)
                          ↓
6. Next Skill Guidance (Handoff based on review outcome)
```

---

### Step 1: Artifact & Context Discovery
1. Read `wiki/<NNN>-<feature>/plan.md` and `wiki/<NNN>-<feature>/evidence.md` using the `wiki-manager` skill.
2. Identify all changed or created source files listed in `evidence.md`.
3. Inspect full source files (not just diff snippets) to understand broader context and system impact.

---

### Step 2: 12-Point Quality Inspection
Evaluate the changes using the checklist in [references/quality_checklist.md](references/quality_checklist.md):

1. **Design & Integration Points**: Clean component interactions? Data contracts, schemas, and multi-step API chains (e.g. Auth → Session/Token → Navigation/Redirect → Subsequent API) verified?
2. **Functionality & Routing Logic**: Fulfills developer/user intent? Route transitions, redirect status codes, route guards (Auth/Role), and state persistence handled?
3. **Error Handling & Resilience**: Graceful error handling at all integration points? Fallback on multi-step failures? No silent `catch {}` blocks or unhandled rejections?
4. **Edge Cases & Data Boundaries**: Boundary values (null/empty/unicode), concurrency, race conditions, double-submissions, and token expiration evaluated?
5. **Complexity**: Free of over-engineering? Solves the present problem rather than speculative future features?
6. **Tests & Flow Verification**: Adequate unit AND integration/workflow tests covering multi-endpoint interactions, redirect cascades, and error paths?
7. **Naming**: Clear, descriptive, and concise names for functions, variables, and modules?
8. **Comments**: Comments written in clear English? Explain *WHY* decisions were made, not *WHAT* code does? Obsolete TODOs cleaned up?
9. **Style**: Adheres strictly to language and project style guides?
10. **Consistency**: Follows existing codebase conventions unless overriding obsolete practices?
11. **Documentation**: Updated READMEs/docs, API specs, and route definitions if affected? Cleaned up deleted/deprecated feature docs?
12. **Every Line & System Context**: Inspected every assigned line of code and evaluated overall system health?

---

### Step 3: Review Decision & Report Generation
Using the template in [references/review_report_template.md](references/review_report_template.md), create `wiki/<NNN>-<feature>/quality-review.md`:

- **Status Options**:
  - `APPROVED`: Code meets all 12 quality criteria. Ready for security review or user confirmation.
  - `CHANGES_REQUESTED`: Concrete actionable findings must be addressed by Constructor.
- Frontmatter metadata required: `id` (`qreview-xxx`), `title`, `derived_from` (`evidence-xxx`), `status` (`APPROVED` or `CHANGES_REQUESTED`), `iteration` (1 to N).
- **Max iterations**: Read from `wiki/registry.yaml` → `max_review_iterations` (defaults to `3` if not set).

---

### Step 4: Constructor Feedback Loop
If status is `CHANGES_REQUESTED`:
1. Send explicit, actionable feedback to Constructor citing file paths, line numbers, and required changes.
2. Allow Constructor to refactor code, re-run tests, and update `evidence.md`.
3. Re-evaluate updated files up to `max_review_iterations` (read from `wiki/registry.yaml` — defaults to `3` if not set).
4. If Constructor resolves all findings, update status to `APPROVED`.

---

### Step 5: Validate Quality Review Document
Run the validator script to verify report structure and frontmatter:
```bash
python <SKILLS_DIR>/quality-reviewer/scripts/validate_quality_review.py wiki/<NNN>-<feature>/quality-review.md
```
Then sync the LLM Wiki index:
```bash
python <SKILLS_DIR>/wiki-manager/scripts/wiki_tool.py sync
```

---

### Step 6: Next Skill Guidance (Handoff)

Based on the review outcome in `quality-review.md`, **explicitly guide the user on the next action**:
- **If `CHANGES_REQUESTED`**:
  - *"Quality review identified issues that require resolution. Next, invoke `/constructor` (or type `constructor`) with the feedback in `wiki/<NNN>-<feature>/quality-review.md` to address findings and re-run tests."*
- **If `APPROVED`**:
  - Check if `security-review.md` exists:
    - If `security-review.md` is **not yet done**: *"Quality review is APPROVED. Next, run the `/security-reviewer` skill (or type `security-reviewer`) to perform the security and static vulnerability audit."*
    - If `security-review.md` is **already PASSED**: *"Both Quality and Security reviews are APPROVED/PASSED! The feature is ready for final confirmation and deployment."*
