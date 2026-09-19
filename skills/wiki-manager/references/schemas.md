# Wiki Manager Frontmatter & Registry Schemas

This document defines the strict schemas for YAML frontmatter headers across all Wiki Manager artifacts and the central `registry.yaml` index.

---

## 1. Registry Schema (`wiki/registry.yaml`)

```yaml
version: "1.0"
project: "SDLC Project"
last_updated: "2026-08-18"
system_doc: "SYSTEM.md"
design_doc: "DESIGN.md"
max_review_iterations: 3  # Global cap for Quality & Security reviewer loops (can be overridden per module)
modules:
  - id: "001-task-management"
    name: "Task Management"
    # description: a single sentence (< 5 words) describing the module.
    # Must NOT repeat the module name. Must be a brief descriptive sentence.
    description: "REST API enabling users to create, list, update, and delete tasks."
    status: "in_progress" # draft | in_progress | completed
    artifacts:
      requirement: "001-task-management/requirement.md"
      design: "001-task-management/design.md"
      mockups:
        - "001-task-management/mockup/task-list.md"
        - "001-task-management/mockup/create-task.md"
      plan: "001-task-management/plan.md"
      evidence: "001-task-management/evidence.md"
```

**Description validation rules** (enforced by `wiki_tool.py sync` and `lint`):

- Must be a single sentence that describes the module.
- Must be at least 5 words (≥ 5 words).
- Must NOT be identical (case-insensitive, whitespace-normalized) to `name`.
- Must NOT be empty.

---

## 2. Requirement Frontmatter Schema (`requirement.md`)

```yaml
---
id: req-001
title: Title of Requirement
status: approved # draft | pending_review | approved | deprecated
derived_to:
  - story-001
  - story-002
  - plan-001
created_at: 2026-08-18
updated_at: 2026-08-18
---
```

---

## 3. Design Frontmatter Schema (`design.md`)

```yaml
---
id: design-001
title: Technical Design for <Feature Name>
derived_from:
  - req-001
status: approved # draft | approved | deprecated
created_at: 2026-08-18
updated_at: 2026-08-18
---
```

---

## 4. Plan Frontmatter Schema (`plan.md`)

```yaml
---
id: plan-001
title: Implementation Plan Title
status: in_progress # draft | in_progress | completed
derived_from:
  - req-001
created_at: 2026-08-18
updated_at: 2026-08-18
---
```

---

## 5. Mockup Frontmatter Schema (`mockup/*.md`)

```yaml
---
id: mockup-001
title: UI Screen Mockup Title
derived_from:
  - req-001
created_at: 2026-08-18
---
```

---

## 6. Log Entry Schema (`log.md`)

```yaml
# No frontmatter — log.md is a flat chronological list
```

**Format** (append-only, no frontmatter per entry):

```markdown
## 2026-08-20

- **09:15** — [Requirement Analyzer] Created `req-001` — Task Management Core
- **09:45** — [User Designer] Created `design-001` — Task Management Core technical design
- **10:00** — [User Designer] Created `mockup-001` — Create Task Dialog
- **10:30** — [User Designer] Created `plan-001` — Task Management implementation plan
- **14:00** — [Constructor] Completed `evidence-001` — All tasks implemented and tested
- **15:00** — [Quality Reviewer] Approved quality-review — Iteration 1, status: APPROVED
- **15:30** — [Security Reviewer] Passed security-review — Iteration 1, status: PASS
```

**Rules**:
- Entries are appended chronologically — never edit past entries.
- One entry per line, prefixed with timestamp and agent name.
- Cross-reference artifacts via backticks: `req-001`, `plan-001`, `evidence-001`.
- After any `WRITE_*` or `WRITE_REVIEW` operation, append the corresponding log entry.

---

## 7. Testing Evidence Frontmatter Schema (`evidence.md`)

```yaml
---
id: evidence-001
title: Testing Evidence Title
derived_from:
  - plan-001
status: completed # completed | partial | failed
tasks_completed:
  - I-001
  - I-002
  - T-003
tested_at: 2026-08-18T23:00:00Z
environment: local
---
```

---

## 8. Quality Review Frontmatter Schema (`quality-review.md`)

```yaml
---
id: qreview-001
title: Quality Review Report for <Feature Name>
derived_from:
  - evidence-001
status: APPROVED # APPROVED | CHANGES_REQUESTED
iteration: 1
created_at: 2026-08-18
updated_at: 2026-08-18
---
```

---

## 9. Security Review Frontmatter Schema (`security-review.md`)

```yaml
---
id: sreview-001
title: Security Review Report for <Feature Name>
derived_from:
  - evidence-001
status: PASS # PASS | FAIL
iteration: 1
created_at: 2026-08-18
updated_at: 2026-08-18
---
```
