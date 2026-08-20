---
name: requirement-analyzer
description: Gather, clarify, structure, and formalize software requirements and user stories in the SDLC workflow. Use this skill whenever receiving raw or ambiguous feature requests, gathering domain requirements, formulating User Stories (US), Functional Requirements (FR), Non-Functional Requirements (NFR), Testing Scenarios, and storing formatted requirements into the LLM Wiki (wiki/<feature>/requirement.md).
---

# Requirement Analyzer Skill

The **Requirement Analyzer** skill guides AI agents in turning vague or high-level user ideas into precise, structured, and testable requirement specifications within the LLM Wiki.

## Operational Workflow

When receiving a feature request or project request, follow these 5 steps sequentially:

```
[Raw User Request] 
       ↓
1. Context Discovery (Codebase & Wiki)
       ↓
2. Ambiguity Resolution (Clarification Questions)
       ↓
3. Document Structuring (Requirement Template)
       ↓
4. Persist to LLM Wiki (wiki-manager skill integration)
       ↓
5. Validation (validate_requirement.py)
```

---

### Step 1: Context & Codebase Discovery
Before asking questions, perform background research:
1. Search the current codebase, database models, and API routes for existing functionality related to the request.
2. Read `wiki/SYSTEM.md` and `wiki/registry.yaml` (using the `wiki-manager` skill) to understand current architecture and feature module numbering.

---

### Step 2: Ambiguity Resolution
Review the request against [references/clarification_checklist.md](file:///.agents/skills/requirement-analyzer/references/clarification_checklist.md).
If the request is ambiguous or lacks critical details (e.g. scope boundary, user roles, error handling, performance targets), interact with the user to ask concise, direct questions:
- Group related questions logically.
- Offer reasonable default choices based on codebase conventions when asking.

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
   python .agents/skills/wiki-manager/scripts/wiki_tool.py sync
   ```

---

### Step 5: Validate Specification
Run the requirement validator script to confirm that all required sections and frontmatter metadata are present:
```bash
python .agents/skills/requirement-analyzer/scripts/validate_requirement.py wiki/<NNN>-<feature-slug>/requirement.md
```
