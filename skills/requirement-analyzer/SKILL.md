---
name: requirement-analyzer
version: "1.0.0"
description: Gather, clarify, structure, and formalize software requirements and user stories in the SDLC workflow. Use this skill whenever receiving any feature request or requirement specification (whether raw, ambiguous, or already well-defined). Always use this skill to structure, validate, and persist or update requirements into the LLM Wiki (wiki/<feature>/requirement.md) whenever the wiki does not yet contain them, before moving to design or implementation. Do NOT use for creating technical designs, writing source code, or conducting quality/security reviews.
---
# Requirement Analyzer Skill

Gather, clarify, and format feature requests into `wiki/<NNN>-<feature-slug>/requirement.md`.

If `wiki/<feature>/requirement.md` does not exist, create it before moving to design or implementation.

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

Ask only questions unresolved by Step 1:

- **Case A: Request is clear and complete**:
  - Skip questions. Move directly to Step 3.
- **Case B: Request contains ambiguities**:
  - Ask targeted questions. Group related items and propose defaults based on codebase conventions.

Always complete Steps 3 to 5 if `wiki/<feature>/requirement.md` does not exist yet.

---

### Step 3: Document Structuring

Format the specification with this template:

```markdown
---
id: req-001
title: Title of Requirement 001
status: approved
derived_to:
  - story-001
  - story-002
---

# Requirement: <Title>

## Scope
<Frontend, backend, API endpoints, or database schema affected>

## Description

Goals: <Goal description>

Target Users: <User personas>

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

## Testing Scenarios
<Validation scenarios and expected outcomes>

## Success Criteria
<List of business and user-facing criteria to confirm completion>

## User Feedbacks (Optional)
<Clarifications and notes from user interactions>
```

---

### Step 4: Persist to LLM Wiki

1. Assign the feature folder number `NNN` (e.g. `001-task-management`).
2. Write to `wiki/<NNN>-<feature-slug>/requirement.md`.
3. Sync the registry:
   ```bash
   python <SKILLS_DIR>/wiki-manager/scripts/wiki_tool.py sync
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
- If approved, tell the user to run `/user-designer DESIGN` to produce the technical design and mockups.
- If revisions are needed, update `requirement.md` until approved.

