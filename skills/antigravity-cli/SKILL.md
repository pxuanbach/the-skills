---
name: antigravity-cli
description: Delegate frontend coding tasks to Google's Antigravity CLI (agy). Use this skill when the user asks to build, implement, refactor, or redesign React/Next.js components, styling, responsive layouts, UI interactions, or any frontend work that would benefit from a specialized coding subagent. Invoke agy in headless mode with a complete, self-contained task description.
version: 1.0.0
---

# Antigravity CLI

Delegate frontend coding tasks to Google's Antigravity CLI (`agy`).

## When to Use

Use Antigravity for tasks primarily involving:

* Frontend/UI implementation
* React/Next.js components
* Styling and responsive layouts
* UI interactions and animations
* Visual redesigns
* Frontend refactoring

Do not delegate trivial edits or tasks primarily involving backend, database, infrastructure, or architecture.

## Prerequisites

Verify that `agy` is available:

```bash
agy --version
```

Antigravity must have been authenticated interactively at least once before using headless mode. Run `agy auth login` if not yet authenticated.

## Invocation

Use Antigravity's headless mode (`-p` / `--prompt`) rather than the interactive TUI.

```bash
agy -p "<task>" --output-format json --print-timeout 15m --disable-slash-commands
```

**Recommended flags:**

| Flag | Purpose |
|------|---------|
| `-p` / `--prompt` | Headless single-prompt mode |
| `--output-format json` | Machine-readable output |
| `--print-timeout 15m` | Explicit timeout (default 5m) |
| `--disable-slash-commands` | Prevent skill/slash expansion interference |
| `--effort high` | Maximum reasoning effort for complex tasks |
| `--mode accept-edits` | Allow direct file modifications |
| `--dangerously-skip-permissions` | Auto-approve all permission prompts (required for headless/CI mode) |

Use `--output-format json` when the result needs to be programmatically inspected.

For headless mode (automated/CI pipelines), `--dangerously-skip-permissions` is **required** to prevent interactive permission prompts from blocking execution. In interactive sessions, prefer configured permission rules or manual approval.

## Task Handoff

Give Antigravity a self-contained task.

Include:

* Objective
* Requirements
* Relevant files or directories
* Constraints
* Expected result
* Verification requirements

Example:

```text
Implement the following frontend task.

Objective:
...

Requirements:
- ...
- ...

Relevant files:
- ...

Constraints:
- Reuse existing components and patterns.
- Do not modify backend code.

Verification:
- Run the relevant lint/test/build commands.
- Report any failures.
```

Do not delegate vague instructions such as "build the frontend for this feature".

## Execution

Run `agy` from the project root so it operates on the same workspace.

Allow Antigravity to inspect, modify, and verify the implementation autonomously.

Prefer one complete delegation over multiple small invocations.

## Result Handling

A successful process exits with code `0`.

For JSON output, inspect these top-level fields:

| Field | Description |
|-------|-------------|
| `status` | `"completed"`, `"failed"`, or `"timeout"` |
| `response` | The main output or result |
| `error` | Error message if failed |
| `conversation_id` | Conversation ID for resume/continue |

If the process fails or times out:

1. Inspect the current workspace.
2. Check `git diff`.
3. Determine whether the implementation is incomplete.
4. Retry with a more specific task if appropriate.
5. Otherwise continue the task yourself.

## Verification

Never assume the delegated task is correct.

After Antigravity completes:

1. Inspect `git diff`.
2. Check that changes are within scope.
3. Review important implementation details.
4. Run relevant checks when necessary.
5. Fix remaining issues yourself.

Treat Antigravity's output as delegated work, not as proof of completion.
