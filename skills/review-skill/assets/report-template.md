# Review Report Template

Fill this template when writing a review report. The presentation and verdict rules live in `SKILL.md` (Report Structure).

## Template

```markdown
# Review: <skill-name> — <APPROVED | APPROVED WITH CONDITIONS | REJECTED>

`<skill path, relative or with ~>` · <YYYY-MM-DD> · Findings: <n> Critical, <n> High, <n> Medium, <n> Low · Linter: <pass | n errors, n warnings>

**Summary:** <1-2 sentences: what the skill does and the main reason for the verdict.>

**Fix first**
1. <H1 — short action>
2. <M2 — short action>
3. <M1 — short action>

## Scoreboard

| Dimension | Status | Note |
|---|---|---|
| Metadata & Routing | Pass | <one short phrase> |
| Progressive Disclosure | Needs work | <e.g. SKILL.md is 6.2k words> |
| Instruction Clarity | Pass | |
| Script & Tool Hygiene | Fail | <ref IDs, e.g. see C1> |
| Testability | Needs work | |
| Content Consistency (optional) | Skipped | |

## Findings

### Critical
**C1 · `SKILL.md:12`** — <issue in one line>
Fix: <concrete change>

### High
**H1 · `scripts/run.sh:7`** — <issue>
Fix: <change>

### Medium
**M1 · `SKILL.md:88`** — <issue>
Fix: <change>

### Low
**L1 · `SKILL.md:140`** — <issue>
Fix: <change>

## Fix order
Apply in this order (blocking first, then by effort): C1 → H1 → M1 → L1.

## Also noted
<Only when relevant, one line each: Skill Smells hit, unchecked Deployment Readiness items that block shipping.>
```

## Worked mini-example

A nearly clean skill; note how little the report contains.

```markdown
# Review: pdf-summarizer — APPROVED WITH CONDITIONS

`skills/pdf-summarizer` · 2026-01-15 · Findings: 0 Critical, 1 High, 1 Medium, 0 Low · Linter: pass

**Summary:** Summarizes PDFs into a fixed outline. Routing is solid, but the description lacks an anti-trigger and one step refers to a file that does not exist.

**Fix first**
1. H1 — add a `Do NOT use for...` clause to the description
2. M1 — create or remove `references/outline.md`

## Scoreboard
| Dimension | Status | Note |
|---|---|---|
| Metadata & Routing | Needs work | see H1 |
| Progressive Disclosure | Pass | |
| Instruction Clarity | Needs work | see M1 |
| Testability | Pass | |

## Findings
### High
**H1 · `SKILL.md:4`** — Description has no anti-trigger, so it may fire on generic document questions.
Fix: append `Do NOT use for OCR or non-PDF files.`

### Medium
**M1 · `SKILL.md:31`** — Step 3 loads `references/outline.md`, which is not in the skill directory.
Fix: add the file or inline the outline.

## Fix order
H1 → M1.
```
