---
name: review-skill
description: |
  Review and validate Agent Skills for consistency, completeness, and quality.
  Use when the user asks to review a skill, check skill quality, validate skill structure, or audit an existing skill in the repository.
  Do NOT use for general application code reviews or software QA testing.
version: 1.6.0
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

If it reports errors, turn each `[ERROR]` line into a finding and show only the error/warning counts in the report header (see Report Structure). Fixes to the skill must pass the linter before the review is considered complete.

### 1. Scope Definition
Identify the components of the skill under review:
- `SKILL.md` structure and metadata
- Frontmatter (`name`, `description`, `version`)
- Instruction clarity, tone, and rationale
- Supporting directories (`references/`, `scripts/`, `assets/`, `examples/` if present)
- Eval readiness and testability
- Content consistency and clarity (optional, see its dimension below)

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

**Content Consistency & Clarity (Optional)**

This dimension is optional and runs after the mandatory ones, on request or after a recent edit. It depends on the domain and workflow the skill encodes, so it is a judgment pass, not a mechanical rule. Quote the conflicting text in every finding.

- **LLM confusion.** Read the skill as the executing model would. Flag passages that can be read two ways, give conflicting steps for the same case, or refer to terms, sections, or files that are not defined anywhere.
- **Internal consistency.** Terms, step names, output fields, status values, and file names match across `SKILL.md`, `references/`, `assets/`, and `scripts/`. Flag contradictions, such as a section that requires a field no step produces.
- **Plausibility.** Steps run in a logical order, thresholds and limits agree with each other, and the workflow fits the domain. Flag steps whose prerequisites appear later in the flow or are not produced at all.
- **Redundancy.** The same rule, definition, or example appears in more than one place. Keep one canonical copy and replace the others with a pointer to it.

*Rationale:* a model follows whatever text it reads, so a contradiction yields unpredictable behavior instead of an obvious error. Duplicate copies also drift apart over time, and the drifted copy then contradicts the canonical one.

Severity follows Section 3: contradictions that change behavior are **High**, ambiguity is **Medium**, redundancy is **Low**.

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

Write the report so a reader who stops after the first screen still knows the verdict and what to fix first. Reviews are read by busy authors; a verdict buried under dimension prose gets skipped, and the same fix listed in two sections gets applied twice or not at all.

**Presentation rules**
- Order is fixed: verdict, scoreboard, findings, fix order, optional notes. Details come after the verdict so the reader can stop early.
- Give every finding an ID (`C1`, `H1`, `M1`, `L1`). Other sections refer to IDs instead of repeating the text.
- Describe each finding in one issue line and one fix line. Quote the offending text only when the problem is ambiguity or contradiction.
- Omit empty severity groups and `N/A` dimensions. A short report with nothing to say beats a full template with blank headings.
- Cap the "Fix first" list at 3 items and the scoreboard "Note" column at one short phrase. Longer reasoning belongs in the finding it describes.
- Do not paste the full linter output. Give counts, and list only the `[ERROR]` lines as findings.
- Use plain status words (`Pass`, `Needs work`, `Fail`) and add no emoji unless the user asks.

**Verdict rules** (so the status is not a judgment call)
- `REJECTED`: any Critical finding, or the linter reports errors.
- `APPROVED WITH CONDITIONS`: no Critical, at least one High or Medium finding.
- `APPROVED`: only Low findings or none.

Load `assets/report-template.md` for the exact template and a worked example before writing the report.

**Optional checks.** Load `references/smells-and-readiness.md` to check Skill Smells (anti-patterns) and Deployment Readiness (rollout gate). Mention hits in one line under `Also noted`.

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
- [ ] Description front-loads action verbs and avoids generic filler (does not start with "a helpful skill for...")
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
- [ ] (Optional) Content consistency pass run: no ambiguous passages, no contradictions, every repeated rule has one canonical source
- [ ] Report follows Report Structure: verdict first, finding IDs, one issue line + one fix line each, no empty sections
- [ ] Deployment Readiness (`references/smells-and-readiness.md`) all cleared
- [ ] None of the Skill Smells (`references/smells-and-readiness.md`)
