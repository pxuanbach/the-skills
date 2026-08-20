---
name: wiki-manager
description: Manage, organize, query, store, and update project documentation and artifacts in the LLM Wiki (wiki/). Use this skill whenever initializing a wiki, storing or updating requirements (requirement.md), technical designs (design.md), mockups (mockup/*.md), implementation plans (plan.md), testing evidence (evidence.md), high-level design (DESIGN.md), system architecture (SYSTEM.md), appending log entries (log.md), or reading project knowledge across the SDLC workflow.
---

# Wiki Manager Skill

The **Wiki Manager** is the central documentation and knowledge repository for the SDLC workflow. It organizes all requirements, designs, mockups, implementation plans, and testing evidence into a structured markdown wiki indexed by `wiki/registry.yaml`. A chronological `log.md` tracks all changes for auditability.

## Wiki Architecture & Directory Structure

All wiki documents reside in the `wiki/` directory at the project root:

```
wiki/
├── registry.yaml             # Central index of feature modules, artifacts, status, and descriptions
├── DESIGN.md                 # High-level architecture and design principles
├── SYSTEM.md                 # System overview, tech stack, and component topology
├── log.md                    # Chronological append-only record of all SDLC events
├── 001-task-management/      # Feature module directory (NNN-feature-name)
│   ├── requirement.md        # Requirement & user stories (Requirement Analyzer)
│   ├── design.md             # Technical design & approved decisions (User Designer)
│   ├── mockup/               # UI/UX ASCII & semantic markdown wireframes
│   │   ├── task-list.md
│   │   └── create-task.md
│   ├── plan.md               # Implementation plan & tasks (User Designer)
│   ├── evidence.md           # Testing logs & verification evidence (Constructor)
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

## Agent Guidelines & Operations

Whenever an agent (Requirement Analyzer, User Designer, Constructor, Quality Reviewer, Security Reviewer) performs an SDLC step, follow these operational workflows:

### 1. Initialize Wiki (`INIT`)
Before creating artifacts, check if `wiki/registry.yaml` exists. If not, initialize it using the helper script:
```bash
python .agents/skills/wiki-manager/scripts/wiki_tool.py init
```
Or create the root folder `wiki/` with baseline files: `registry.yaml`, `DESIGN.md`, `SYSTEM.md`, and `log.md`.

### 2. Query / Read Wiki Knowledge (`READ_QUERY`)
Before starting any new requirement analysis or implementation task:
1. Read `wiki/registry.yaml` to discover existing feature modules and document IDs.
2. Read `wiki/SYSTEM.md` and `wiki/DESIGN.md` for architectural context.
3. Read the feature module directory (e.g., `wiki/001-task-management/requirement.md` and `plan.md`) to understand active requirements and dependencies.

### 3. Store / Update Requirements (`WRITE_REQUIREMENT`)
**Agent**: Requirement Analyzer
- Module location: `wiki/<NNN>-<feature-slug>/requirement.md`
- Requirements MUST include YAML frontmatter (`id`, `title`, `status`, `derived_to`).
- Follow the schema in `references/schemas.md#requirement-schema` and template in `references/templates.md#requirement-template`.
- Update `wiki/registry.yaml` under `modules.<module_id>.artifacts`.
- **Append entry to `wiki/log.md`** recording this artifact creation.

### 4. Store / Update Technical Design (`WRITE_DESIGN`)
**Agent**: User Designer
- Design location: `wiki/<NNN>-<feature-slug>/design.md`
- Design MUST link to parent requirements via `derived_from: [req-001]`.
- Design document serves as the final approved technical specification — it is created AFTER requirement approval and BEFORE mockup/plan drafting.
- Contains: API contracts, data models, architecture decisions, approved UI summary, and acceptance criteria.
- Follow schema in `references/schemas.md#design-schema` and template in `references/templates.md#design-template`.
- Update `wiki/registry.yaml` under `modules.<module_id>.artifacts`.
- **Append entry to `wiki/log.md`** recording this artifact creation.

### 5. Store / Update Plans & Mockups (`WRITE_DESIGN_PLAN`)
**Agent**: User Designer
- Plan location: `wiki/<NNN>-<feature-slug>/plan.md`
- Mockup location: `wiki/<NNN>-<feature-slug>/mockup/<screen-slug>.md`
- Plans MUST link to parent requirements via `derived_from: [req-001]`.
- Task list items in `plan.md` MUST specify `id`, `type`, `description`, `status`, and `steps`.
- Follow schemas in `references/schemas.md` and templates in `references/templates.md`.
- **Append entry to `wiki/log.md`** recording this artifact creation.

### 6. Store / Update Testing Evidence (`WRITE_EVIDENCE`)
**Agent**: Constructor
- Evidence location: `wiki/<NNN>-<feature-slug>/evidence.md`
- After implementation and test execution, capture test output logs, command execution proofs, and assertion results.
- Link evidence directly to task IDs from `plan.md`.
- **Append entry to `wiki/log.md`** recording this artifact creation.

### 7. Store / Update Review Reports (`WRITE_REVIEW`)
**Agent**: Quality Reviewer or Security Reviewer
- Location: `wiki/<NNN>-<feature-slug>/quality-review.md` or `wiki/<NNN>-<feature-slug>/security-review.md`
- Status: `APPROVED`/`CHANGES_REQUESTED` (quality) or `PASS`/`FAIL` (security)
- **Append entry to `wiki/log.md`** recording review outcome.

### 8. Validate & Lint Wiki (`VALIDATE_LINT`)
To ensure cross-link integrity and schema compliance across all feature modules:
```bash
python .agents/skills/wiki-manager/scripts/wiki_tool.py lint
```
The script checks for:
- Missing required frontmatter fields (`id`, `title`, `status`).
- Broken cross-links (`derived_from` / `derived_to`).
- Desynchronized items in `wiki/registry.yaml`.

---

## Reference Guides

- See [references/schemas.md](file:///.agents/skills/wiki-manager/references/schemas.md) for strict YAML frontmatter metadata rules.
- See [references/templates.md](file:///.agents/skills/wiki-manager/references/templates.md) for complete Markdown & ASCII wireframe templates.
