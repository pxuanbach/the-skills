---
name: wiki-manager
description: Manage, organize, query, store, and update project documentation and artifacts in the LLM Wiki (wiki/). Use this skill whenever initializing a wiki, storing or updating requirements (requirement.md), technical designs (design.md), mockups (mockup/*.md), implementation plans (plan.md), testing evidence (evidence.md), project UI/UX design standards (DESIGN.md), system architecture (SYSTEM.md), appending log entries (log.md), or reading project knowledge across the SDLC workflow.
---

# Wiki Manager Skill

The **Wiki Manager** is the central documentation and knowledge repository for the SDLC workflow. It organizes all requirements, designs, mockups, implementation plans, and testing evidence into a structured markdown wiki indexed by `wiki/registry.yaml`. A chronological `log.md` tracks all changes for auditability.

## Wiki Architecture & Directory Structure

All wiki documents reside in the `wiki/` directory at the project root:

```
wiki/
├── registry.yaml             # Central index of feature modules, artifacts, status, and descriptions
├── DESIGN.md                 # UI style, design tokens, UI/UX guidelines, component standards (UI source of truth)
├── SYSTEM.md                 # Core project intent, high-level architecture, tech stack, directory structure, app boundaries
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
Before creating feature artifacts, check if `wiki/registry.yaml` exists. If not, the Agent MUST execute the interactive initialization workflow:

#### Step 1: Collect Project Information
The Agent prompts the user for three core inputs:
1. **Project Description & Intent**: Summary of the project, target audience, core problem solved, and key user flows.
2. **`DESIGN.md` Specifications**:
   - UI style & aesthetic direction.
   - Design tokens (color palette, typography, spacing, border radius, shadows).
   - Component guidelines and interactive UI/UX patterns.
   - *Role*: Serves as the single source of truth so that whenever an Agent implements or modifies UI components, it strictly adheres to these project design standards.
3. **`SYSTEM.md` Specifications**:
   - Core project intent & high-level architecture (services, communication, topology).
   - Tech stack (languages, frameworks, DB, tools).
   - Directory structure (including the explicit purpose and use of each directory).
   - Monorepo application boundaries and modular isolation rules (if applicable).

#### Step 2: Auto-Generation Option
- For `DESIGN.md` and `SYSTEM.md`, ask the user if they want to provide custom content or have the Agent **auto-generate standard-compliant files** based on the Project Description.
- If **auto-generate** is selected:
  - Agent synthesizes the Project Description to establish appropriate, high-quality standards.
  - Generates `wiki/SYSTEM.md` with concrete architecture, tech stack selections, detailed directory mapping, and app boundaries.
  - Generates `wiki/DESIGN.md` with complete UI tokens, component rules, styling conventions, and accessibility rules matching the tech stack.

#### Step 3: Write Files & Initialize Registry
1. Create `wiki/` directory.
2. Create `wiki/registry.yaml` initialized with project name, system/design doc links, and empty modules array.
3. Write `wiki/SYSTEM.md` and `wiki/DESIGN.md` (user-provided or auto-generated).
4. Create `wiki/log.md` with an initial initialization entry.
5. Alternatively, run the helper script and populate the content:
   ```bash
   python <SKILLS_DIR>/wiki-manager/scripts/wiki_tool.py init
   ```

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
python <SKILLS_DIR>/wiki-manager/scripts/wiki_tool.py lint
```
The script checks for:
- Missing required frontmatter fields (`id`, `title`, `status`).
- Broken cross-links (`derived_from` / `derived_to`).
- Desynchronized items in `wiki/registry.yaml`.

---

## Reference Guides

- See [references/schemas.md](references/schemas.md) for strict YAML frontmatter metadata rules.
- See [references/templates.md](references/templates.md) for complete Markdown & ASCII wireframe templates.
