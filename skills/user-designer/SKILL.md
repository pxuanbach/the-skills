---
name: user-designer
version: "1.0.0"
description: Create technical designs (design.md), API contracts, data models, E2E/integration test cases, UI/UX mockups (mockup/*.md), and implementation plans (plan.md) from requirement specifications. Use this skill whenever transforming approved requirements into technical architecture and mockups (via DESIGN sub-command) or generating task breakdowns for implementation (via PLAN sub-command). Do NOT use for gathering raw user requirements, writing source code, or conducting code reviews.
---

# User Designer Skill

Convert approved requirements into technical designs (`design.md`), UI wireframes (`mockup/*.md`), and implementation plans (`plan.md`).

This skill runs two sub-commands:
1. **`DESIGN`**: Produces `design.md` (architecture, API/data contracts, test cases) and `mockup/*.md`. Halts for user review.
2. **`PLAN`**: Breaks approved designs into tasks in `plan.md` for Constructor.

## SDLC Workflow Position

```
[0. wiki-manager] (Init & Central Knowledge Hub)
       │
       ▼
[1. requirement-analyzer]
       │
       ▼
[2a. user-designer DESIGN] ──► Produces design.md & mockup/*.md ──► User Approval
       │
       ▼
[2b. user-designer PLAN]   ──► Produces plan.md (from approved design.md)
       │
       ▼
[3. constructor]
       │
       ├──► [4a. quality-reviewer]  ──(loop)──┐
       │                                      ▼
       └──► [4b. security-reviewer] ──(loop)──┴─► [User Confirmation]
```

---

## Command 1: `DESIGN` (`/user-designer DESIGN`)

Create the technical design (`design.md`) and UI mockups (`mockup/*.md`).

### Prerequisite Check
Ensure `wiki/<NNN>-<feature>/requirement.md` exists and is approved. If missing, tell the user to run `/requirement-analyzer` first.

### Workflow

```
[requirement.md & wiki/SYSTEM.md]
              ↓
1. Read Requirements & Scope Assessment
              ↓
2. Create Technical Design (design.md: Architecture, API, Data Models, Test Cases)
              ↓
3. Evaluate UI Need ──→ [UI Involved?] ──Yes──> Create Mockup (DESIGN.md → mockup/*.md)
              │                                    │
              └───No (Backend/API/CLI) ────────────┤
                                                   ↓
4. Persist, Validate & Sync (validate_design.py & wiki_tool.py)
                                                   ↓
5. User Review Loop (Present design.md and Mockups)
```

#### Step 1: Read Requirements and Architecture Context
1. Read `wiki/<NNN>-<feature>/requirement.md`.
2. Read `wiki/SYSTEM.md` to verify tech stack, directory structure, and module boundaries.
3. Note Requirement IDs (`req-xxx`), User Stories (`US-xxx`), Functional Requirements (`FR-xxx`), and Success Criteria.

#### Step 2: Create Technical Design (`design.md`)
1. Write `wiki/<NNN>-<feature>/design.md` using the template in `wiki-manager/references/templates.md#2-design-template`.
2. Include these sections:
   - **Architecture**: Service boundaries, components, and module interactions.
   - **API Contracts**: Endpoints, HTTP methods, request/response schemas, error codes.
   - **Data Models**: Schemas, entities, relations, field types, and constraints.
   - **E2E & Integration Test Cases**:
     - *UI Flows*: User actions, form inputs, loaders, toasts, and screen transitions.
     - *State Transitions & Data Flow*: Lifecycle state changes, event emission, DB updates, and side effects.
   - **UI Summary**: List of screens linking to `mockup/` (or `N/A (Backend / Non-UI feature)`).
   - **Acceptance Criteria**: Verifiable criteria mapped from requirement Success Criteria.
3. Frontmatter: set `derived_from: [req-xxx]`, `status: approved` (or `draft`).

#### Step 3: Create UI Mockups (Optional)
- If UI is involved:
  1. Read `wiki/DESIGN.md` for project tokens, components, and styling rules.
  2. Write `wiki/<NNN>-<feature>/mockup/<screen-slug>.md` using ASCII wireframes per `references/ascii_wireframe_guide.md`.
  3. Include: screen name, wireframe block, components, interactions, and related requirements.
- If Backend / API / CLI only:
  1. Omit the `mockup/` folder.
  2. Mark `UI Summary: N/A (Backend / Non-UI feature)` in `design.md`.

#### Step 4: Persist, Validate & Sync
1. Validate the technical design:
   ```bash
   python <SKILLS_DIR>/user-designer/scripts/validate_design.py wiki/<NNN>-<feature>/design.md
   ```
2. Sync the wiki registry:
   ```bash
   python <SKILLS_DIR>/wiki-manager/scripts/wiki_tool.py sync
   ```

#### Step 5: User Review
Present `design.md` and mockups to the user. Apply requested changes. Once approved, tell the user to run `/user-designer PLAN`.

---

## Command 2: `PLAN` (`/user-designer PLAN`)

Convert approved design specifications, test cases, and mockups into an implementation plan (`plan.md`).

### Prerequisite Check
Verify `wiki/<NNN>-<feature>/design.md` exists. If missing, halt and tell the user to run `/user-designer DESIGN` first.

### Workflow

```
[Approved design.md & mockup/*.md]
              ↓
1. Read Approved Design & Mockups
              ↓
2. Draft Implementation Plan (plan.md with Tasks & Mermaid diagram)
              ↓
3. Persist & Sync (wiki_tool.py sync)
              ↓
4. Validate (validate_plan_mockup.py)
              ↓
5. Next Step (Handoff to constructor)
```

#### Step 1: Read Approved Design and Context
1. Read `wiki/<NNN>-<feature>/design.md` and mockups in `wiki/<NNN>-<feature>/mockup/`.
2. Extract contracts, models, test cases, and acceptance criteria.

#### Step 2: Draft Implementation Plan (`plan.md`)

1. **Task Breakdown Rules**:
   - **Implementation Tasks (`id: I-xxx`, `type: implementation`)**:
     - Order tasks by layer: Data Models -> Business Services -> API Routes -> UI Components.
     - Specify target files, functions, and concrete steps for each task.
   - **Testing Tasks (`id: T-xxx`, `type: testing`)**:
     - Map every scenario in `design.md` to at least one testing task.
     - Classify test levels: Unit (isolated logic/components), Integration (`TC-INT-xxx`), E2E (`TC-E2E-xxx`).
     - Specify the runner (`pytest`, `vitest`, `playwright`), target test file, and expected assertions.
   - **Process Flow (`mermaid`)**:
     - Draw a flowchart (`graph TD`) mapping execution dependencies.

2. Write `wiki/<NNN>-<feature>/plan.md` using the template:

```markdown
---
id: plan-001
title: Implementation Plan for Requirement 001
status: in_progress
derived_from:
  - req-001
---

# Plan: <Title>

## Implementation Plan
<Architecture approach and technology choices>

## Implementation Process

```mermaid
graph TD
    A[Start] --> B[Task 1: Setup & Data Models]
    B --> C[Task 2: Core Logic & API Endpoints]
    C --> D[Task 3: Integration Tests]
    D --> E[Task 4: UI Components]
    E --> F[Task 5: E2E Tests]
    F --> G[Done]
```

## Tasks

### Task 1: <Setup & Models>
- **id**: I-001
- **type**: implementation
- **description**: <Task description>
- **status**: pending
- **steps**:
  1. <Step 1>
  2. <Step 2>

### Task 2: <Business Logic & API Endpoints>
- **id**: I-002
- **type**: implementation
- **description**: <Task description>
- **status**: pending
- **steps**:
  1. <Step 1>
  2. <Step 2>

### Task 3: <Integration Tests (TC-INT-001)>
- **id**: T-003
- **type**: testing
- **description**: Integration tests for state transitions from TC-INT-001
- **status**: pending
- **steps**:
  1. Write tests in `tests/integration/test_state.py`
  2. Assert status transitions and database updates

### Task 4: <UI Components>
- **id**: I-004
- **type**: implementation
- **description**: <UI task description>
- **status**: pending
- **steps**:
  1. <Step 1>
  2. <Step 2>

### Task 5: <E2E Tests (TC-E2E-001)>
- **id**: T-005
- **type**: testing
- **description**: E2E test for task flow from TC-E2E-001
- **status**: pending
- **steps**:
  1. Write test in `tests/e2e/test_flow.spec.ts`
  2. Run test runner and verify pass

## UI Mockup (if applicable)
- Relative link: `mockup/screen-name.md` OR `N/A (Backend/CLI requirement)`
```

#### Step 3: Persist and Sync
Sync `wiki/registry.yaml`:
```bash
python <SKILLS_DIR>/wiki-manager/scripts/wiki_tool.py sync
```

#### Step 4: Validate Plan and Mockup
Run the validator:
```bash
python <SKILLS_DIR>/user-designer/scripts/validate_plan_mockup.py wiki/<NNN>-<feature>/plan.md
```

#### Step 5: Next Step
Present `plan.md` to the user. Tell them to run `/constructor` to begin implementation.
