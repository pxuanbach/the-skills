# 11-Point Quality Review Checklist

## 1. Design
- Are interactions between modules/components logical and well-structured?
- Should this change belong in the main codebase or be abstracted into a library?
- Does it integrate seamlessly with the rest of the system architecture?
- Is the timing right for introducing this functionality?

## 2. Functionality
- Does the code achieve what the developer intended?
- Is it good for both end-users and future maintainers/developers?
- Have edge cases, null pointer risks, concurrency issues, race conditions, and deadlocks been evaluated?

## 3. Complexity
- Is the code more complex than necessary?
- Avoid over-engineering: do not implement speculative future requirements.
- Solve present problems cleanly.

## 4. Tests
- Are there sufficient unit, integration, and end-to-end tests for the change?
- Are tests correct, sensible, and useful?
- Do tests fail accurately when code breaks, or do they produce false positives?
- Are test files kept clean and free of unnecessary complexity?

## 5. Naming
- Are identifiers (variables, parameters, classes, methods) long enough to communicate intent clearly without being overly verbose?

## 6. Comments
- Are comments written in clear English?
- Do comments explain **WHY** a decision was made rather than **WHAT** the code does?
- If code is unclear, simplify the code rather than adding explanatory comments.
- Are obsolete TODOs or temporary comments removed?

## 7. Style
- Does the code strictly follow the programming language's standard style guide?
- Does it adhere to project-specific styling and formatting rules?

## 8. Consistency
- Is the style guide treated as the ultimate authority?
- If local code is inconsistent with project style guidelines, follow the official style guide and log cleanup issues if needed.

## 9. Documentation
- If changes impact build, setup, testing, or deployment processes, are READMEs and documentation updated accordingly?
- If features were deleted or deprecated, was obsolete documentation removed?

## 10. Every Line
- Did the reviewer inspect every assigned line of code (excluding auto-generated code and data files)?
- If logic is hard to understand, request clarification from Constructor.

## 11. System Context
- Is the change evaluated in the context of the full file and surrounding architecture?
- Does this change improve or degrade the overall health of the codebase?
