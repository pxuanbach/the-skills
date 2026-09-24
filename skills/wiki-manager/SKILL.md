---
name: wiki-manager
version: "1.0.0"
description: |
  Invoked via `/wiki-manager`. Initializes, queries, and maintains the LLM Wiki (wiki/) — the central documentation hub for the SDLC pipeline. Manages wiki/registry.yaml, wiki/SYSTEM.md, wiki/DESIGN.md, wiki/log.md, and feature module directories. Does not gather requirements, write implementation code, or conduct reviews — only maintains the persistent knowledge base that other SDLC skills read from and write to.
---

# Wiki Manager Skill

Store, index, and query project specifications in `wiki/`. Track module states in `wiki/registry.yaml` and append events to `wiki/log.md`.

## SDLC Workflow Position

```
[0. wiki-manager] (Init & Central Knowledge Hub)  <=== (YOU ARE HERE)
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
       ├──► [4a. quality-reviewer]  ──(loop)──┐
       │                                      ▼
       └──► [4b. security-reviewer] ──(loop)──┴─► [User Confirmation]
```

## Directory Structure

All wiki documents live in `wiki/` at the project root:

```
wiki/
├── registry.yaml             # Index of feature modules, artifacts, status, and descriptions
├── DESIGN.md                 # UI style, design tokens, and component standards (UI source of truth)
├── SYSTEM.md                 # Architecture, tech stack, directory layout, and app boundaries
├── log.md                    # Append-only record of SDLC events
├── 001-task-management/      # Feature module directory (NNN-feature-name)
│   ├── requirement.md        # Requirements and user stories (Requirement Analyzer)
│   ├── design.md             # Technical design and decisions (User Designer)
│   ├── mockup/               # UI ASCII and markdown wireframes
│   │   ├── task-list.md
│   │   └── create-task.md
│   ├── plan.md               # Task breakdown (User Designer)
│   ├── evidence.md           # Test logs and execution proofs (Constructor)
│   ├── quality-review.md     # Quality review report (Quality Reviewer)
│   └── security-review.md    # Security review report (Security Reviewer)
└── 002-feature-name/
    ├── requirement.md
    ├── design.md
    ├── mockup/
    ├── plan.md
    ├── evidence.md
    ├── quality-review.md
    └── security-review.md
```

---

## Operations

### 1. Initialize Wiki (`INIT`)
Check if `wiki/registry.yaml` exists. If not, initialize the wiki:

#### Step 1: Collect Project Information
Ask the user for three inputs:
1. **Project Intent**: Summary, target audience, core problem, and primary user flows.
2. **`DESIGN.md` Specifications**:
   - Visual style.
   - Design tokens (colors, typography, spacing, border radiuses, shadows).
   - Component rules and interactive patterns.
   - Role: Single source of truth for all UI components.
3. **`SYSTEM.md` Specifications**:
   - Architecture and service topology.
   - Tech stack (runtime, framework, database, tooling).
   - Directory structure and the purpose of each folder.
   - App boundaries and modular isolation rules.

#### Step 2: Auto-Generation Option
Offer to auto-generate standard-compliant `DESIGN.md` and `SYSTEM.md` from the Project Intent:
- Generate `wiki/SYSTEM.md` with concrete architecture, tech stack selections, and folder boundaries.
- Generate `wiki/DESIGN.md` with tokens, component rules, and accessibility standards matching the stack.

#### Step 3: Write Files & Initialize Registry
1. Create the `wiki/` directory.
2. Create `wiki/registry.yaml` with project metadata and an empty modules list.
3. Write `wiki/SYSTEM.md` and `wiki/DESIGN.md`.
4. Create `wiki/log.md` with an initial entry.
5. Or run the helper tool:
   ```bash
   python <SKILLS_DIR>/wiki-manager/scripts/wiki_tool.py init
   ```

#### Step 4: Next Step
Confirm `wiki/SYSTEM.md`, `wiki/DESIGN.md`, and `wiki/registry.yaml` exist. Tell the user to run `/requirement-analyzer` to define the first feature.

### 2. Query Wiki Knowledge (`READ_QUERY`)
Before starting any requirement, design, or coding task:
1. Read `wiki/registry.yaml` to find existing modules and IDs.
2. Read `wiki/SYSTEM.md` and `wiki/DESIGN.md` for project context.
3. Read the relevant module directory (e.g. `wiki/001-task-management/requirement.md`).

### 3. Store Requirements (`WRITE_REQUIREMENT`)
**Agent**: Requirement Analyzer
- File: `wiki/<NNN>-<feature-slug>/requirement.md`
- Include YAML frontmatter (`id`, `title`, `status`, `derived_to`).
- Follow schemas in `references/schemas.md` and templates in `references/templates.md`.
- Update `wiki/registry.yaml` under `modules.<module_id>.artifacts`.
- Append an entry to `wiki/log.md`.

### 4. Store Technical Design (`WRITE_DESIGN`)
**Agent**: User Designer
- File: `wiki/<NNN>-<feature-slug>/design.md`
- Link to parent requirement via `derived_from: [req-001]`.
- Contains: API contracts, data models, architecture decisions, approved UI summary, and acceptance criteria.
- Follow schemas in `references/schemas.md` and templates in `references/templates.md`.
- Update `wiki/registry.yaml` under `modules.<module_id>.artifacts`.
- Append an entry to `wiki/log.md`.

### 5. Store Plans and Mockups (`WRITE_DESIGN_PLAN`)
**Agent**: User Designer
- Files: `wiki/<NNN>-<feature-slug>/plan.md` and `wiki/<NNN>-<feature-slug>/mockup/<screen-slug>.md`
- Link to parent requirement via `derived_from: [req-001]`.
- Detail tasks in `plan.md` with `id`, `type`, `description`, `status`, and `steps`.
- Append an entry to `wiki/log.md`.

### 6. Store Testing Evidence (`WRITE_EVIDENCE`)
**Agent**: Constructor
- File: `wiki/<NNN>-<feature-slug>/evidence.md`
- Record command execution proofs, raw test logs, and assertion counts.
- Map evidence to task IDs from `plan.md`.
- Append an entry to `wiki/log.md`.

### 7. Store Review Reports (`WRITE_REVIEW`)
**Agent**: Quality Reviewer or Security Reviewer
- File: `wiki/<NNN>-<feature-slug>/quality-review.md` or `wiki/<NNN>-<feature-slug>/security-review.md`
- Set status: `APPROVED` or `CHANGES_REQUESTED` (quality), `PASS` or `FAIL` (security).
- Append an entry to `wiki/log.md`.

### 8. Lint Wiki (`VALIDATE_LINT`)
Check cross-link integrity and frontmatter compliance:
```bash
python <SKILLS_DIR>/wiki-manager/scripts/wiki_tool.py lint
```

---

## References

- [references/schemas.md](references/schemas.md): YAML frontmatter schemas.
- [references/templates.md](references/templates.md): Markdown templates.
