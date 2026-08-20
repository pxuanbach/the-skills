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

## 11-Point Checklist Evaluation

| # | Checklist Criteria | Assessment | Notes |
|---|-------------------|------------|-------|
| 1 | Design Integrity | PASSED | Clean modular structure |
| 2 | Functionality & Edge Cases | PASSED | Checked edge cases & error paths |
| 3 | Complexity & Over-engineering | PASSED | Simple & direct implementation |
| 4 | Test Coverage & Validity | PASSED | Unit tests pass cleanly |
| 5 | Naming Conventions | PASSED | Descriptive identifiers used |
| 6 | English Comments & Clarity | PASSED | Comments explain 'WHY' |
| 7 | Style Guide Adherence | PASSED | Follows standard guidelines |
| 8 | Codebase Consistency | PASSED | Consistent with project patterns |
| 9 | Documentation Updates | PASSED | Relevant docs updated |
| 10 | Every Line Inspection | PASSED | Complete line-by-line review |
| 11 | Overall System Context | PASSED | Code health improved |

## Detailed Findings & Action Items

### Required Changes (if status = CHANGES_REQUESTED)
1. **[File Path:Line]**: Issue description and requested fix.
2. **[File Path:Line]**: Issue description and requested fix.

### Strengths & Commendations
- Highlights of exceptionally clean code or design choices.
```
