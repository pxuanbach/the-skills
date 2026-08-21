---
name: review-skill
description: Review and validate Agent Skills for consistency, completeness, and quality. Use when the user asks to review a skill, check skill quality, validate skill structure, or audit an existing skill in the repository.
version: 1.0.0
---

# Review Skill

Review Agent Skills to ensure they meet quality standards — structural consistency, metadata accuracy, clear instructions, and adherence to repo conventions.

## Core Principles

### Avoid Hardcoded Specifics
Do not reference specific tool names, agent identifiers, or absolute paths in review outputs. Use generic functional descriptions instead.

**NG (Incorrect):**
- "Use `read_file` to read the document"
- `C:\Users\ADMIN\.agent\skills\abc`

**OK (Correct):**
- "Use a tool capable of reading document contents"
- `~/.agent/skills/abc`

### Output Language
Write all review content in English unless the user explicitly requests otherwise in the same message.

### Maintain Consistency
All instructions throughout this skill must be mutually consistent. If Step 1 restricts access to Scope A, Step 3 must not suddenly require access to Scope B without justification. Terminology must remain uniform — do not use multiple different terms for the same concept. Grammar and tone should be consistent throughout.

## Review Workflow

### 1. Scope Definition
Identify what to review:
- SKILL.md structure and metadata
- Frontmatter (name, description, version)
- Workflow clarity and completeness
- References and scripts folders (if present)
- Adherence to repo conventions

### 2. Review Dimensions

**Metadata Quality**
- `name` field is present and matches directory name
- `description` is concise (2-3 sentences max)
- `description` includes both "what it does" and "when to use"
- `version` follows semver format

**Structural Consistency**
- SKILL.md follows the required anatomy: YAML frontmatter + Markdown body
- Section headings use `##` and `###` hierarchy correctly
- No broken links to references or scripts

**Instruction Clarity**
- Imperative mood used in instructions
- Output formats clearly defined with examples
- Error conditions and edge cases addressed

**Convention Adherence**
- Follows repo's skill anatomy: `SKILL.md`, optional `references/`, optional `scripts/`
- References folder contains only documentation/templates (no executable logic unless in `scripts/`)
- Scripts are documented with usage instructions and input parameters

**Content Completeness**
- All required frontmatter fields present
- Workflow steps are actionable and ordered
- Checklist or guidance provided for key decisions

### 3. Evidence Collection
Document findings with:
- File path and line number reference
- Severity (critical/high/medium/low)
- Description of the issue
- Suggested fix or recommendation

### 4. Report Structure

```
# Skill Review Report
## Skill Name
/path/to/skill

## Metadata Assessment
[Pass/Fail with details]

## Structural Assessment
[Pass/Fail with details]

## Instruction Clarity
[Pass/Fail with details]

## Convention Adherence
[Pass/Fail with details]

## Content Completeness
[Pass/Fail with details]

## Findings

### Critical
[Issues requiring immediate fix]

### High
[Issues to address before merge]

### Medium
[Suggestions for improvement]

### Low
[Nice-to-have polish]

## Recommendations
Prioritized list of actions.

## Approval Status
[APPROVED / APPROVED WITH CONDITIONS / REJECTED]
```

## Repo Skill Conventions

Each skill follows this structure:
```
skills/
└── <skill-name>/
    ├── SKILL.md          # Required: YAML frontmatter + workflow body
    ├── references/       # Optional: pre-researched data and reusable patterns
    │   └── *.md
    ├── scripts/          # Optional: reusable executable scripts
    │   └── *.*
    └── examples/         # Optional: example outputs
        └── *.md
```

## Review Checklist

- [ ] Frontmatter has `name`, `description`, `version`
- [ ] Description includes "what" and "when" criteria
- [ ] SKILL.md body uses imperative mood
- [ ] All sections use consistent heading hierarchy
- [ ] References are properly linked and accessible
- [ ] Scripts have usage documentation
- [ ] No hardcoded paths or tool names in content
- [ ] Workflow steps are ordered and actionable
- [ ] Output formats are explicitly defined
