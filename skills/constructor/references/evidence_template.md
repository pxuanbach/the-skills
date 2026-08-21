# Evidence Document Template

Use this template to create `wiki/<NNN>-<feature>/evidence.md` after completing implementation and testing tasks.

```markdown
---
id: evidence-001
title: Execution and Testing Evidence for <Feature Name>
derived_from:
  - plan-001
status: completed
tasks_completed:
  - I-001
  - I-002
  - T-003
---

# Evidence: <Feature Name> Execution & Testing

## Execution Summary
<Provide a high-level summary of implemented tasks, system capabilities added, and testing outcomes.>

## Task Execution Log

### Task I-001: <Task Title>
- **Status**: Completed
- **Changes**: <Summary of code written, models updated, routes added>
- **Files Modified/Created**:
  - `path/to/file1.py`
  - `path/to/file2.py`

### Task I-002: <Task Title>
- **Status**: Completed
- **Changes**: <Summary of business logic and handlers implemented>

### Task T-003: <Testing Task Title>
- **Status**: Completed
- **Test Suite**: `tests/test_feature.py`
- **Result**: Passed (<N> assertions verified)

## Test Verification & Logs

```bash
$ <test command e.g. pytest tests/>
<Insert exact un-truncated terminal output showing test execution and pass rates>
```

## Artifacts & Changed Files
- `models/task.py`
- `routers/tasks.py`
- `tests/test_tasks.py`
```
