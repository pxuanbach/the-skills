---
name: constructor
description: Implement tasks and execute testing according to the Implementation Process in plan.md. Use this skill whenever executing tasks from an implementation plan, creating todo lists, writing source code, running unit/integration tests, gathering test logs, loading framework/language skills, and generating evidence.md in the LLM Wiki (wiki/<feature>/evidence.md).
---

# Constructor Skill

The **Constructor** skill guides AI agents in reading approved implementation plans (`plan.md`) and UI mockups (`mockup/*.md`), executing defined tasks step-by-step, discovering & loading appropriate programming language/framework skills, executing tests, and producing testing evidence (`evidence.md`) within the LLM Wiki.

## Operational Workflow

When assigned to build a feature or execute an implementation plan, follow these 6 steps sequentially:

```
[Implementation Plan (plan.md) & Mockups (mockup/*.md)]
                         ↓
1. Read Plan & Context Discovery (wiki-manager skill)
                         ↓
2. Todo List Initialization (Task Tracking)
                         ↓
3. Tech Stack & Skill Auto-Discovery (Languages, Frameworks, Testing)
                         ↓
4. Incremental Implementation & Test Execution
                         ↓
5. Persist Evidence to LLM Wiki (wiki/<feature>/evidence.md & wiki_tool.py sync)
                         ↓
6. Validation (validate_evidence.py)
```

---

### Step 1: Read Plan & Context Discovery
1. Use the `wiki-manager` skill to locate and read `wiki/<NNN>-<feature>/plan.md` and any associated mockups in `wiki/<NNN>-<feature>/mockup/`.
2. Extract all tasks defined in `plan.md`:
   - Implementation tasks (ID format: `I-xxx`)
   - Testing tasks (ID format: `T-xxx`)
3. Review `derived_from` requirements (`req-xxx`) if background context is needed.

---

### Step 2: Todo List Initialization
1. Maintain an active Todo list in memory or context representing all tasks from `plan.md`.
2. Mark tasks with status tracking: `pending` -> `in_progress` -> `completed`.
3. Work strictly on one task at a time, keeping changes modular and verifiable.

---

### Step 3: Tech Stack & Skill Auto-Discovery
Before writing code or running tests:
1. Inspect project configurations (`package.json`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`, `go.mod`, etc.) to identify languages, frameworks, and test runners.
2. Check available skills (e.g. React, Next.js, Python, FastAPI, Vitest, Pytest) and load applicable skills into context.
3. Consult loaded skill guidelines to adhere to project-specific coding standards and patterns.

---

### Step 4: Incremental Task Implementation & Testing
For each task in the Todo list:
1. **Implementation Tasks (`I-xxx`)**:
   - Write clean, well-structured, production-ready code.
   - Comment code in English explaining *why* complex decisions were made.
   - Do not leave unfinished stubs, dummy fallbacks, or commented-out code.
2. **Testing Tasks (`T-xxx`)**:
   - Write unit, integration, or end-to-end test cases corresponding to task requirements.
   - Run tests directly using project test runners (e.g. `pytest`, `npm test`).
   - Capture exact raw terminal output and exit codes for evidence.

---

### Step 5: Persist Evidence to LLM Wiki
Format testing and execution evidence using the template in [references/evidence_template.md](file:///.agents/skills/constructor/references/evidence_template.md):

1. Save the evidence document to `wiki/<NNN>-<feature>/evidence.md`.
2. Ensure frontmatter metadata includes `id` (`evidence-xxx`), `title`, `derived_from` (`plan-xxx`), `status` (`completed`), and `tasks_completed` list (`[I-001, I-002, T-003]`).
3. Include raw terminal test logs, execution summaries, and clickable links to created/modified files.
4. Sync the LLM Wiki index:
   ```bash
   python .agents/skills/wiki-manager/scripts/wiki_tool.py sync
   ```

---

### Step 6: Validate Evidence Specification
Run the evidence validator script to verify structure, metadata, and log completeness:
```bash
python .agents/skills/constructor/scripts/validate_evidence.py wiki/<NNN>-<feature>/evidence.md
```

---

## Reviewer Integration & Iteration Loops

When the optional **Quality Reviewer** or **Security Reviewer** provides feedback or requests changes:
1. Review feedback items carefully against [references/implementation_guidelines.md](file:///.agents/skills/constructor/references/implementation_guidelines.md).
2. Refactor source code to fix reported issues or vulnerabilities.
3. Re-run tests to confirm fixes do not introduce regressions.
4. Update `wiki/<NNN>-<feature>/evidence.md` with revised execution logs.
5. Re-run `validate_evidence.py` and notify reviewer for re-evaluation (up to max N review iterations).
