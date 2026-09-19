---
name: review-skill
description: |
  Review and validate Agent Skills for consistency, completeness, and quality.
  Use when the user asks to review a skill, check skill quality, validate skill structure, or audit an existing skill in the repository.
  Do NOT use for general application code reviews or software QA testing.
version: 1.4.0
license: MIT
---

# Review Skill

Review Agent Skills to ensure they meet quality standards — structural consistency, metadata accuracy, progressive disclosure, clear instructions, testability, and adherence to repository conventions.

## Core Principles

### Avoid Hardcoded Specifics
Do not reference specific tool names, agent identifiers, or absolute paths in review outputs or skill contents. Use generic functional descriptions instead.

**NG (Incorrect):**
- "Use `read_file` to read the document"
- `C:\Users\ADMIN\.agent\skills\abc`

**OK (Correct):**
- "Use a tool capable of reading document contents"
- `~/.agent/skills/abc`

### Output Language
Write all review content in English unless the user explicitly requests otherwise in the same message.

### Maintain Consistency & Rationale
All instructions throughout the skill must be mutually consistent. Terminology must remain uniform. Provide rationale for constraints rather than relying solely on capitalized imperatives (e.g., explain why a rule exists instead of just shouting "ALWAYS DO X").

### Respect Progressive Disclosure & Token Budget
A skill is procedural memory loaded on demand. `SKILL.md` must remain lightweight and concise (<5,000 words). Heavy reference data belongs in `references/`, templates and schemas belong in `assets/`, and deterministic compute belongs in `scripts/`.

## Review Workflow

### 0. Mechanical Linter (run first)
Run the structural linter before any manual review:

```
python skills/review-skill/scripts/validate_skill.py <skill_dir>
```

If it reports errors, include the linter output in the review report under **Mechanical Checks**. Fixes to the skill must pass the linter before the review is considered complete.

### 1. Scope Definition
Identify the components of the skill under review:
- `SKILL.md` structure and metadata
- Frontmatter (`name`, `description`, `version`)
- Instruction clarity, tone, and rationale
- Supporting directories (`references/`, `scripts/`, `assets/`, `examples/` if present)
- Eval readiness and testability

### 2. Review Dimensions

**Metadata & Routing Quality**
- `name` field is present, valid format (kebab-case/gerund), and matches the directory name (`snake_case`).
- `description` starts with an action verb (front-loaded keywords) and clearly explains **what it does**.
- `description` length stays within routing budget (≤1024 chars YAML, ~50 words target; downstream API callers may cap at ~200 chars).
- `description` explicitly defines **when to use** (triggers).
- `description` includes an anti-trigger clause (**when NOT to use** / `Do NOT use for...`) to avoid over-triggering.
- `version` follows Semantic Versioning (`semver`).

**Progressive Disclosure & Token Footprint**
- `SKILL.md` body is concise (<5,000 words) without unneeded boilerplate.
- Deterministic tasks (math, data formatting, parsing) are offloaded to `scripts/`.
- Deep domain context, long specifications, and edge cases are offloaded to `references/`.
- Output templates, schemas, and static artifacts are placed in `assets/`.

**Instruction Clarity & Rationale**
- Uses imperative, actionable language.
- Explains the *why* (rationale) behind strict rules to help the model generalize.
- Output formats are clearly specified with concrete examples.
- Error conditions and edge cases are addressed.
- Flags ALL-CAPS imperatives (`ALWAYS`, `NEVER`) without rationale — those rules belong in `AGENTS.md`, not in a Skill body.

**Script & Tool Hygiene**
- Scripts in `scripts/` are properly documented with usage guidelines and input parameters.
- No hardcoded secrets, credentials, or absolute file paths in scripts or instructions.
- All configuration values are passed as input arguments or environment variables.

**Testability & Verification (Eval Readiness)**

Map every check to one of the four failure modes below; a skill that fails any one stays at the draft tier.

- **Trigger Failure.** Positive (must fire) and negative (must stay quiet) test cases both exist; description hits ≥90% trigger accuracy in isolation.
- **Execution Failure.** Golden dataset of representative inputs produces correct outputs and matching tool trajectories; JSON eval cases committed alongside the skill.
- **Regression.** Adding the skill causes zero measurable drops in the existing library suite; verify by running the suite before and after install.
- **Token Budget.** Co-loaded with 5 to 15 frequently-active skills, the skill's body does not degrade unrelated turns (target body ≤5,000 tokens; describe what was measured).

### 3. Evidence Collection
Document each finding with:
- File path and line number reference
- Severity level:
  - **Critical:** Broken frontmatter/routing, hardcoded credentials, security risks.
  - **High:** Missing anti-triggers, bloated context violating progressive disclosure, missing script documentation.
  - **Medium:** Ambiguous instructions, missing rationale, formatting inconsistencies.
  - **Low:** Minor phrasing polish or cosmetic markdown adjustments.
- Description of the issue
- Concrete recommended fix

### 4. Report Structure

```markdown
# Skill Review Report: <skill-name>
**Location:** `/path/to/skill`
**Review Date:** YYYY-MM-DD
**Overall Status:** [APPROVED / APPROVED WITH CONDITIONS / REJECTED]

## 1. Executive Summary
Brief summary of the skill's purpose and overall assessment.

## 2. Dimension Assessments
- **Metadata & Routing:** [Pass / Needs Improvement / Fail] — Details
- **Progressive Disclosure & Token Budget:** [Pass / Needs Improvement / Fail] — Details
- **Instruction Clarity & Rationale:** [Pass / Needs Improvement / Fail] — Details
- **Script & Tool Hygiene:** [Pass / Needs Improvement / Fail / N/A] — Details
- **Testability & Eval Readiness:** [Pass / Needs Improvement / Fail] — Details

## 3. Findings

### Critical
- **[File:Line]**: Issue description and required remediation.

### High
- **[File:Line]**: Issue description and required remediation.

### Medium
- **[File:Line]**: Suggestion for improvement.

### Low
- **[File:Line]**: Minor polish recommendation.

## 4. Actionable Recommendations
Prioritized checklist of changes required before publishing or deployment.

## Skill Smells (Anti-Patterns)

If the skill under review shows any of these patterns, flag it. Sourced from the Agent Skills cheatsheet.

- **Over 5,000 words in `SKILL.md`.** Probably two skills, or reference material that belongs in `references/`.
- **Two domain teams could plausibly own it.** Not yet decomposed. Split along team boundaries.
- **You can't write three test cases for it.** Description is too vague; the skill does too many things.
- **It does not reference any other resource.** May be a long instruction that belongs in the system prompt.
- **It keeps growing "edge cases" sections.** Each edge case probably wants its own skill.
- **Description starts with "a helpful skill for...".** Rewrite — the description should name the trigger, the inputs, and the output.

## Deployment Readiness

A skill is shippable only when every box clears. This is a separate gate from review: review checks the artifact, this section checks the rollout path.

- [ ] Frontmatter lints cleanly (no schema warnings)
- [ ] Description reviewed by someone other than the author (second-pass bias check)
- [ ] Scripts have unit tests passing in CI
- [ ] Eval suite passes in CI with a documented min-pass threshold
- [ ] Security scan clean (no secrets, no untrusted third-party deps)
- [ ] Cross-tool install paths tested if shipping publicly (at least 2 of: Claude Code, Codex CLI, Antigravity, OpenCode)
- [ ] Org-level admin provisioning updated where applicable (allowed-tools, scope, skill overrides)

## Repo Skill Conventions

Standard directory layout for skills:
```
skills/
└── <skill_name>/
    ├── SKILL.md          # Required: YAML frontmatter + concise workflow body
    ├── references/       # Optional: deep domain context, guides, edge cases
    │   └── *.md
    ├── scripts/          # Optional: deterministic executable helper scripts
    │   └── *.*
    ├── assets/           # Optional: templates, schemas, static configs
    │   └── *.*
    └── examples/         # Optional: sample inputs/outputs
        └── *.md
```

## Review Checklist

- [ ] Mechanical linter passes: `python skills/review-skill/scripts/validate_skill.py <skill-dir>` exits 0
- [ ] Frontmatter has `name`, `description`, `version`
- [ ] Description includes **What**, **When to use**, and **When NOT to use** (Anti-trigger)
- [ ] Description length stays within routing budget (≤1024 chars YAML, ~50 words target)
- [ ] Description front-loads action verbs and avoids generic filler (never starts with "a helpful skill for...")
- [ ] SKILL.md body is concise (<5,000 words) and follows progressive disclosure
- [ ] Deterministic logic is offloaded to `scripts/` with usage docs and parameterization
- [ ] Templates/schemas are located in `assets/`, deep context in `references/`
- [ ] Instructions provide rationale rather than unsubstantiated capitalized mandates
- [ ] No ALL-CAPS imperatives without rationale (those belong in `AGENTS.md`, not the skill body)
- [ ] No hardcoded paths, secrets, or vendor-locked tool names
- [ ] Output formats are explicitly defined with examples
- [ ] Trigger coverage: positive AND negative test cases exist (target ≥90% trigger accuracy)
- [ ] Execution coverage: golden dataset + JSON eval cases produce expected outputs and trajectories
- [ ] Regression coverage: existing library suite shows no drops when this skill is added
- [ ] Token-budget coverage: skill body ≤5,000 tokens; verified under co-loaded conditions
- [ ] Deployment Readiness section (see above) all cleared
- [ ] None of the Skill Smells (see dedicated section above)
