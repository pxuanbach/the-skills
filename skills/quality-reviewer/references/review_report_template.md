# Quality Review Report Template

Use this template to create `wiki/<NNN>-<feature>/quality-review.md`.

```markdown
---
id: qreview-001
title: Quality Review Report for <Feature Name>
derived_from:
  - evidence-001
status: APPROVED # Options: APPROVED | CHANGES_REQUESTED
iteration: 1
---

# Quality Review Report: <Feature Name>

## Review Summary
- **Overall Status**: APPROVED / CHANGES_REQUESTED
- **Iteration**: 1 of 3
- **Evaluated Files**:
  - `path/to/file1.py`
  - `path/to/file2.py`

## 12-Point Checklist Evaluation

| # | Checklist Criteria | Assessment | Notes |
|---|-------------------|------------|-------|
| 1 | Design & Integration Points | PASSED | Clean architecture, data contracts & API chaining verified |
| 2 | Functionality & Routing Logic | PASSED | Fulfills intent, route guards & navigation handled |
| 3 | Error Handling & Resilience | PASSED | Graceful failure paths, no silent unhandled errors |
| 4 | Edge Cases & Data Boundaries | PASSED | Checked boundaries, concurrency & race conditions |
| 5 | Complexity & Over-engineering | PASSED | Simple, maintainable implementation |
| 6 | Test Coverage & Flow Verification | PASSED | Unit & integration/workflow tests pass |
| 7 | Naming Conventions | PASSED | Clear and descriptive identifiers |
| 8 | English Comments & Clarity | PASSED | Clear comments explaining 'WHY' |
| 9 | Style Guide Adherence | PASSED | Follows language & project style |
| 10 | Codebase Consistency | PASSED | Consistent with existing conventions |
| 11 | Documentation Updates | PASSED | API/route docs and READMEs updated |
| 12 | Every Line & System Context | PASSED | Full line-by-line review & system health |

## Detailed Findings & Action Items

### Required Changes (if status = CHANGES_REQUESTED)
1. **[File Path:Line]**: Issue description and requested fix.
2. **[File Path:Line]**: Issue description and requested fix.

### Strengths & Commendations
- Highlights of exceptionally clean code or design choices.
```
