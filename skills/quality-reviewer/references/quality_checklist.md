# 12-Point Quality Review Checklist

## 1. Design & Integration Points
- Are interactions between modules, services, and components logical, decoupled, and well-structured?
- **Contract & Data Flow**: Are schemas, payloads, headers, and types strictly compatible between caller and callee?
- **Multi-Step Workflows / API Chaining**: Is the end-to-end chain verified (e.g., Auth/Login → Token/Session storage → State propagation → Next API / View)?
- Does the change integrate cleanly with system architecture without leaking abstractions?

## 2. Functionality & Routing Logic
- Does the code achieve developer and business intent end-to-end?
- **Routing & Navigation**: Are route transitions, redirect status codes (e.g., 302/303/307 redirects vs 200 JSON responses), route guards (Auth/Role permissions), query parameters, and history navigation correctly handled?
- **State Persistence**: Is session/application state preserved and synchronized across redirects, page reloads, and navigation events?

## 3. Error Handling & Resilience
- Are error paths and failure modes handled at every integration point (network failure, timeout, non-200 HTTP statuses, unauthorized 401/403, missing resources 404, server 500)?
- In multi-step flows, if a subsequent step fails (e.g. login succeeds but redirect route or destination API fails), is there graceful fallback and clear user feedback?
- Are resources cleaned up and states/transactions rolled back on error (no dangling state or half-committed mutations)?
- Are there any swallowed exceptions, silent `catch {}` blocks, or unhandled promise rejections?

## 4. Edge Cases & Data Boundaries
- Have boundary values been evaluated: null/undefined, empty strings/arrays, zero/negative numbers, special/unicode characters, oversized payloads?
- Are concurrency, race conditions, debounce/throttle, and double-submission risks (e.g., rapid clicks on submit/login) protected against?
- Is token/session expiration during in-flight requests handled gracefully?

## 5. Complexity
- Is the code more complex than necessary?
- Avoid over-engineering: do not implement speculative future requirements.
- Solve present problems cleanly and concisely.

## 6. Tests & Flow Verification
- Are there sufficient unit tests for isolated business logic?
- **Integration / Flow Tests**: Are multi-step interactions, API handoffs, and integration points tested (e.g., login → redirect → protected route data fetch)?
- Are error paths, redirect status codes, and edge case scenarios explicitly covered by tests?
- Do tests fail accurately when code breaks, without producing false positives?

## 7. Naming
- Are identifiers (variables, parameters, classes, methods, routes, endpoints) clear, descriptive, and concise without being overly verbose?

## 8. Comments
- Are comments written in clear English?
- Do comments explain **WHY** a decision was made rather than **WHAT** the code does?
- If code is unclear, simplify the code rather than adding explanatory comments.
- Are obsolete TODOs or temporary comments removed?

## 9. Style
- Does the code strictly follow the programming language's standard style guide?
- Does it adhere to project-specific styling and formatting rules?

## 10. Consistency
- Follows existing codebase conventions, design patterns, and architectural standards?
- If local code is inconsistent with project guidelines, adhere to the official standard.

## 11. Documentation
- If changes impact build, setup, APIs, route definitions, environment variables, or deployment, are READMEs and docs updated?
- If features were deleted or deprecated, was obsolete documentation removed?

## 12. Every Line & System Context
- Did the reviewer inspect every assigned line of code (excluding auto-generated code and data files)?
- Is the change evaluated in the context of the full file and surrounding architecture?
- Does this change improve or degrade the overall health of the codebase?
