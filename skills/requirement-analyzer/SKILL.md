---
name: requirement-analyzer
version: 1.1.0
license: MIT
description: |
  Invoked via `/requirement-analyzer`. Structures and persists feature requests, bug reports, and behavior changes into wiki/<feature>/requirement.md. Produces requirement documents with user stories, functional requirements, and success criteria. This skill does not write source code, design UI, or run reviews — it only documents the "what" before any implementation begins.
---
# Requirement Analyzer Skill

Gather, clarify, and format feature requests into `wiki/<NNN>-<feature-slug>/requirement.md`.

## Anti-Skip Rule (READ THIS FIRST)

**Every** incoming request — no matter how small — MUST be persisted to
`wiki/<NNN>-<feature-slug>/requirement.md` before any other agent writes
code. Examples that MUST still produce a requirement entry:

- "Đổi màu primary button sang xanh lá"
- "Sửa typo trên trang login"
- "Thêm field `notes` vào form tạo task"
- "Disable nút X khi Y rỗng"
- "Tăng timeout API lên 30s"

If the request is purely conversational / informational (no code or
config change), skip persistence. Otherwise, persist first, then act.

> Rationale: the LLM Wiki is the only durable record of why the codebase
> looks the way it does. Skipping small changes means future agents lose
> context and re-litigate decisions. A 30-second write protects hours of
> future work.

If `wiki/<feature>/requirement.md` does not exist, create it before any
other action (design, implementation, review, or commit) — regardless of
whether design or implementation will follow.

## SDLC Workflow Position

```
[0. wiki-manager] (Init & Central Knowledge Hub)
       │
       ▼
[1. requirement-analyzer]  <=== (YOU ARE HERE)
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

## Workflow

```
[Feature Request]
       ↓
1. Context Discovery (Codebase & Wiki Check)
       ↓
2. Clarification Check (Ask only if needed)
       ↓
3. Document Structuring (Standard Template)
       ↓
4. Persist to LLM Wiki (wiki/<feature>/requirement.md)
       ↓
5. Validation (validate_requirement.py)
       ↓
6. Next Step (Handoff to user-designer)
```

---

### Step 1: Context and Codebase Discovery

Research background context before drafting questions or specs:

1. **Check Wiki First**:
   - Read `wiki/SYSTEM.md` and `wiki/registry.yaml` to confirm architecture, existing modules, and dependencies.
2. **Local Codebase Inspection (Subagent A)**:
   - Inspect related files, models, routes, tests, and configuration.
   - Search for similar logic in the codebase to prevent duplication.
   - Return: `files_found`, `patterns_identified`, `integration_points`, `gaps`.
3. **External Context (Subagent B, optional)**:
   - Search official docs, release notes, or framework best practices when external libraries are involved.
   - Skip this subagent for local refactors or self-contained features.
   - Return: `external_sources`, `ecosystem_patterns`, `recommendations`.

---

### Step 2: Clarification Check

This step has TWO mandatory outputs — never skip either:

#### 2a. Restate the Problem (ALWAYS)

Even if the request is clear and complete, rewrite the problem in 2–4
sentences using the agent's own words, then show it to the user for
confirmation before drafting the spec. Example:

> "If I understand correctly, you want users to be able to create tasks
> with name + priority, list them with status filters, and mark them
> complete with one click. The change is scoped to the FastAPI backend
> and a minimal React UI. Did I get that right?"

If the user corrects anything, loop back to Step 1 and re-do Step 2a.

#### 2b. Targeted Clarification (Only if needed)

- **Case A: Request is clear and complete**:
  - Restate + proceed. Record `None` under `## Open Questions`.
- **Case B: Request contains ambiguities**:
  - Group open questions, propose a default for each based on codebase conventions, and record them under `## Open Questions`.
  - Show the questions to the user with the restated problem and wait for answers. Never accept vague wording just to finish the document.
  - Keep `status: draft` while any question is `open`.

Always complete Steps 3 to 5 if `wiki/<feature>/requirement.md` does not exist yet.

---

### Step 3: Document Structuring

Format the specification with this template:

```markdown
---
id: req-001
title: Title of Requirement 001
status: draft # set to approved only after the user confirms
derived_to:
  - story-001
  - story-002
---

# Requirement: <Title>

## Scope
<Frontend, backend, API endpoints, or database schema affected>

## Description

**Goals**: <Goal description>

**Target Users**: <User personas>

<Detailed description of the requirement>

## User Stories

### US-001
<Description of user story 1>

### US-002
<Description of user story 2>

## Functional Requirements

### FR-001
<Functional requirement 1>

### FR-002
<Functional requirement 2>

## Non-Functional Requirements

### NFR-001
<Performance, latency, security, or reliability constraints>

## Open Questions
<Questions for the user, each with a proposed default and status (open | answered). Write "None" only if the restated problem was confirmed with no gaps.>

## Testing Scenarios
<Validation scenarios and expected outcomes>

## Success Criteria
<List of business and user-facing criteria to confirm completion>

> **Note for agents**: "Success Criteria" defines what success means from a **business/mission perspective** (e.g. "users complete task X within Y seconds", "system handles Z concurrent users"). It is NOT implementation-level acceptance criteria — do not confuse it with "Acceptance Criteria" in `design.md`.

## User Feedbacks (Optional)
<Clarifications and notes from user interactions>
```

---

### Step 4: Persist to LLM Wiki

1. Create the feature folder with the next free number: `python <SKILLS_DIR>/wiki-manager/scripts/wiki_tool.py new <feature-slug>` (prints e.g. `001-task-management`). Reuse the existing folder when the request changes an existing module.
2. Write to `wiki/<NNN>-<feature-slug>/requirement.md`.
3. Give the module a `description` in `wiki/registry.yaml`: one summary sentence of at least 100 characters describing what the module does (not its title). `sync` keeps hand-written descriptions, so write it once after the first sync.
4. Sync the registry:
   ```bash
   python <SKILLS_DIR>/wiki-manager/scripts/wiki_tool.py sync
   python <SKILLS_DIR>/wiki-manager/scripts/wiki_tool.py log "Requirement Analyzer" "Created `req-xxx` — <title>"
   ```

---

### Step 5: Validate Specification

Run the validator:
```bash
python <SKILLS_DIR>/requirement-analyzer/scripts/validate_requirement.py wiki/<NNN>-<feature-slug>/requirement.md
```

---

### Step 6: Next Step

Present the finalized requirement to the user:
- Only after the user explicitly confirms, set `status: approved`, then tell them to run `/user-designer DESIGN` to produce the technical design and mockups.
- If revisions are needed, update `requirement.md` (status stays `draft`) until approved.

