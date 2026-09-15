---
name: constructor
version: "1.0.0"
description: Implement tasks and execute testing according to the Implementation Process in plan.md. Use this skill whenever executing tasks from an implementation plan, creating todo lists, writing source code, running unit/integration tests, gathering test logs, loading framework/language skills, and generating evidence.md in the LLM Wiki (wiki/<feature>/evidence.md). Do NOT use for collecting requirements, drafting technical designs or mockups, or conducting independent quality/security audits.
---
# Constructor Skill

Implement tasks from `plan.md`, run tests, and write testing evidence to `wiki/<NNN>-<feature>/evidence.md`.

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
[3. constructor]  <=== (YOU ARE HERE)
       │
       ├──► [4a. quality-reviewer]  ──(loop)──┐
       │                                      ▼
       └──► [4b. security-reviewer] ──(loop)──┴─► [User Confirmation]
```

## Prerequisite Check (MANDATORY — DO NOT SKIP)

Before implementing ANY task — including single-line tweaks, typo fixes,
config edits, or copy changes — verify all of the following:

1. **Requirement exists**: `wiki/<NNN>-<feature>/requirement.md` is present
   AND its frontmatter `status` is `approved`.
2. **Plan exists**: `wiki/<NNN>-<feature>/plan.md` is present.
3. **Evidence target**: you know which `evidence.md` file will receive
   the test logs and changed-file list.

If any check fails:

- **Missing requirement.md** → HALT and tell the user:
  > "No `wiki/<NNN>-<feature>/requirement.md` found. Run
  > `/requirement-analyzer` first to capture the change in the LLM Wiki.
  > The SDLC workflow requires every change — including small tweaks —
  > to be recorded in the wiki before any code is written."
- **status != approved** → HALT and tell the user the requirement is
  still in `draft` and must be approved first.
- **Missing plan.md** → HALT and tell the user to run
  `/user-designer PLAN` to produce the implementation plan.

Only proceed to the Workflow below once all three checks pass.

## Workflow

```
[plan.md & mockup/*.md]
           ↓
1. Read Plan & Context (wiki-manager skill)
           ↓
2. Track Tasks (Todo list)
           ↓
3. Load Tech Stack Skills
           ↓
4. Implement Tasks & Run Tests
           ↓
5. Write Evidence (wiki/<feature>/evidence.md)
           ↓
6. Validate Evidence (validate_evidence.py)
           ↓
7. Next Step (Handoff to reviewers)
```

---

### Step 1: Read Plan and Context

1. Read `wiki/<NNN>-<feature>/design.md`, `wiki/<NNN>-<feature>/plan.md`, and any files in `wiki/<NNN>-<feature>/mockup/`.
2. Extract tasks:
   - Implementation tasks (`I-xxx`)
   - Testing tasks (`T-xxx`)
3. Read `derived_from` requirements (`req-xxx`) if background context is needed.

---

### Step 2: Track Tasks

1. Maintain a task list tracking status: `pending` -> `in_progress` -> `completed`.
2. Work on one task at a time.

---

### Step 3: Load Tech Stack Skills

1. Inspect project configs (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`) to identify languages, frameworks, and test runners.
2. Load available skills matching the stack (e.g. React, Python, FastAPI, Vitest, Pytest).
3. Follow the loaded skill conventions.

**Parallel subagents for independent tasks**:
- When tasks (`I-xxx`) touch separate modules with no shared state, spawn one subagent per task group.
- Complete shared models or common utilities in the main agent before spawning subagents.
- Merge evidence and verify no file collisions occur.

---

### Step 4: Implement Tasks and Run Tests

For each task:

1. **Implementation Tasks (`I-xxx`)**:
   - Write working code. No stubs or commented blocks.
   - Comment in English only to explain non-obvious logic.
2. **Testing Tasks (`T-xxx`)**:
   - Write unit, integration, or E2E tests matching the task criteria.
   - Run tests with project test runners (`pytest`, `npm test`).
   - Save terminal output and exit codes for evidence.

---

### Step 5: Write Evidence to LLM Wiki

Follow the template in `references/evidence_template.md`:

1. Save to `wiki/<NNN>-<feature>/evidence.md`.
2. Set frontmatter: `id` (`evidence-xxx`), `title`, `derived_from` (`plan-xxx`), `status` (`completed`), and `tasks_completed` list (`[I-001, I-002, T-003]`).
3. Include raw terminal test logs, execution summaries, and links to changed files.
4. Sync the wiki registry:
   ```bash
   python <SKILLS_DIR>/wiki-manager/scripts/wiki_tool.py sync
   ```

---

### Step 6: Validate Evidence

Run the validator:
```bash
python <SKILLS_DIR>/constructor/scripts/validate_evidence.py wiki/<NNN>-<feature>/evidence.md
```

---

### Step 7: Next Step

Summarize modified files and test results to the user.
Tell the user to run:
- `/quality-reviewer` to review code quality and architecture.
- `/security-reviewer` to run security and vulnerability scans.

---

## Reviewer Feedback Loop

When Quality Reviewer or Security Reviewer requests changes:

1. Read findings against `references/implementation_guidelines.md`.
2. Fix reported issues.
3. Re-run tests to verify fixes and prevent regressions.
4. Update `wiki/<NNN>-<feature>/evidence.md` with new test logs.
5. Re-run `validate_evidence.py` and notify the reviewer.

