---
name: requirement-analyzer
description: Gather, clarify, structure, and formalize software requirements and user stories in the SDLC workflow. Use this skill whenever receiving any feature request or requirement specification (whether raw, ambiguous, or already well-defined). Always use this skill to structure, validate, and persist or update requirements into the LLM Wiki (wiki/<feature>/requirement.md) whenever the wiki does not yet contain them, before moving to design or implementation.
---
# Requirement Analyzer Skill

The **Requirement Analyzer** skill guides AI agents in structuring, clarifying, and formalizing feature requests — from vague, high-level ideas to already well-defined specifications — into precise, standardized, and testable requirement specifications within the LLM Wiki.

> [!IMPORTANT]
> **Wiki Persistence is Mandatory**: Even if a requirement is provided with full clarity and detail by the user, you must still use this skill to structure, validate, and persist it to `wiki/<feature>/requirement.md` if the wiki does not yet have it. Never bypass requirement formalization and go straight to implementation without wiki documentation.

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

> **Current Position**: `requirement-analyzer` (Step 1 — Gathers, clarifies, and formalizes requirements into `wiki/<feature>/requirement.md`)

## Operational Workflow

When receiving a feature request or project request, follow these steps sequentially:

```
[Feature Request (Raw, Ambiguous, or Clear)] 
       ↓
1. Context Discovery (Codebase & Wiki Check)
       ↓
2. Ambiguity & Completeness Check (Clarify only if needed)
       ↓
3. Document Structuring (Standard Template)
       ↓
4. Persist to LLM Wiki (wiki/<feature>/requirement.md)
       ↓
5. Validation (validate_requirement.py)
       ↓
6. Next Skill Guidance (Handoff to user-designer)
```

---

### Step 1: Context &amp; Codebase Discovery

Before asking questions or drafting, perform background research using parallel subagents for speed and breadth:

1. **Check Wiki First**:
  - Read `wiki/SYSTEM.md` and `wiki/registry.yaml` (using the `wiki-manager` skill) to understand current architecture, existing feature modules, and check if this requirement already exists or needs updating.
2. **Spawn subagent A — Local Codebase Inspection**:
  - Inspect relevant wiki documents, local files, existing patterns, constraints, tests, and likely integration points.
  - Search for similar functionality in the codebase to avoid duplication.
  - Identify existing models, API routes, configuration files, and shared utilities related to the request.
  - Return a structured summary: `files_found`, `patterns_identified`, `integration_points`, `gaps`.
3. **Spawn subagent B — External &amp; Ecosystem Context**:
  - Explore external knowledge from official docs, related blog to improve/enrich the answer.
  - Search for official documentation, recent releases, community patterns, blog, or best practices from external sources.
  - Return a structured summary: `external_sources`, `ecosystem_patterns`, `relevant_versions`, `recommendations`.

> **When to skip subagent B**: If the request is purely local (e.g., refactoring existing code, updating a known feature), skip external research and rely on subagent A + wiki files only.

---

### Step 2: Ambiguity &amp; Completeness Check

Review the request against [references/clarification_checklist.md](references/clarification_checklist.md):

- **Case A: Request is already clear and complete**:
  - If the prompt provides complete scope, behaviors, and constraints that pass the checklist, **do NOT ask redundant questions**.
  - Proceed directly to **Step 3 (Document Structuring)** to standardize and format the specification.
- **Case B: Request is raw, vague, or ambiguous**:
  - If the request lacks critical details (e.g. scope boundary, user roles, error handling, performance targets), interact with the user to ask concise, direct questions:
    - Group related questions logically.
    - Offer reasonable default choices based on codebase conventions when asking.

> [!NOTE]
> Regardless of whether Case A or Case B applies, **Steps 3, 4, and 5 must always be executed** if the requirement is not yet recorded in `wiki/<feature>/requirement.md`.

---

### Step 3: Document Structuring

Format the requirement using the standard template:

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
<scope of requirement, e.g. frontend/backend, API endpoint, DB schema>

## Description

Goals: <goal description>

Target Users: <list of target users>

<detailed description of the requirement>

## User Stories

### US-001
<description of user story 1>

### US-002
<description of user story 2>

## Functional Requirements

### FR-001
<description of functional requirement 1>

### FR-002
<description of functional requirement 2>

## Non-Functional Requirements

### NFR-001
<description of non-functional requirement 1>

## Testing Scenarios
<list of testing scenarios to validate the requirement>

## Success Criteria
<a list of criteria to determine if the requirement is successfully implemented>

## User Feedbacks (Optional)
<list of feedbacks from users to clarify the requirement>
```

---

### Step 4: Persist to LLM Wiki

1. Determine feature folder number `NNN` (e.g., `001-task-management`).
2. Write the file to `wiki/<NNN>-<feature-slug>/requirement.md`.
3. Invoke the `wiki-manager` skill synchronization tool to index the artifact in `wiki/registry.yaml`:
  ```bash
   python <SKILLS_DIR>/wiki-manager/scripts/wiki_tool.py sync
  ```

---

### Step 5: Validate Specification

Run the requirement validator script to confirm that all required sections and frontmatter metadata are present:

```bash
python [[ORCA_RICH_MD:27785be5634e8e9f3b28080d21344a53:inline-html:%3CSKILLS_DIR%3E]]/requirement-analyzer/scripts/validate_requirement.py wiki/[[ORCA_RICH_MD:27785be5634e8e9f3b28080d21344a53:inline-html:%3CNNN%3E]]-[[ORCA_RICH_MD:27785be5634e8e9f3b28080d21344a53:inline-html:%3Cfeature-slug%3E]]/requirement.md
```

---

### Step 6: Next Skill Guidance (Handoff)

After validating and presenting the finalized requirement to the user:

1. Ask the user for confirmation/approval of `requirement.md` (or confirm directly if formulated from a pre-approved clear spec).
2. **Explicitly guide the user on the next step**:
  - If approved: *"The requirements are formalized in `wiki/<NNN>-<feature-slug>/requirement.md`. Next, run the `/user-designer` skill with the `DESIGN` command (or type `user-designer DESIGN`) to produce the Technical Design (`design.md`) and UI mockups (`mockup/*.md`)."*
  - If revisions are requested: Iterate on `requirement.md` with the user until approved.

