# Prompt Blueprints

Use these templates during **Phase 4 (Prompt Generation)**. Each blueprint embeds the outputs of our clarification frameworks (**SCQA** context, **JTBD** objective, **MECE + Socratic** quantified requirements, and **Pre-mortem** guardrails). Adapt section headings to the user's preferred language while keeping the structure strict, concrete, and self-contained. Each blueprint is a fresh task brief addressed directly to the agent: open with the Objective, define no role or persona, and never refer to a prior session or conversation.

---

## Template 1: Coding / Implementation Agent Prompt

Use for feature implementation, refactoring, or bug fixes to a coding agent.

````markdown
# Objective (JTBD)
In `<project/repo name>`, when `<trigger/situation>`, the system must `<capability/action>` so that `<expected outcome/value>`.

# Context & Problem Framing (SCQA)
- **Situation (Current State):** `<How the codebase/module currently works>`
- **Complication (Why Change Now):** `<What is broken, missing, or bottlenecked>`
- **Tech Stack & Environment:** `<Language, runtime version, framework, key libraries, test runner>`
- **Relevant Files & Entry Points:**
  - `<path/to/file1>` — `<role of this file and what needs to change>`
  - `<path/to/file2>` — `<existing pattern or interface to follow>`

# Requirements & Quantified Constraints (MECE + Socratic)
## Functional Requirements
1. **Input / Trigger:** `<Exact input schema, payload, or CLI arguments>`
2. **Core Logic & State:** `<Step-by-step behavior and state/DB updates>`
3. **Edge Cases & Error Handling:** `<Quantified behavior on timeout, invalid input, or empty state>`
4. **Performance / SLA Targets:** `<Quantified metrics, e.g., p95 < 200ms, batch size <= 500>`

## Pre-mortem Guardrails & Non-Goals (Inversion)
- **Strict Non-Goals (Do NOT do):** `<e.g., Do not refactor unrelated modules; do not alter existing public API signatures>`
- **Failure Modes to Prevent:** `<e.g., Prevent N+1 queries; prevent partial writes without transaction rollback; do not add external packages>`

# Suggested Implementation Steps
1. `<Step 1: e.g., Update data model / types in path/to/file>`
2. `<Step 2: e.g., Implement core logic and error handling>`
3. `<Step 3: e.g., Wire up endpoint/UI and add unit tests>`

# Acceptance Criteria & Verification
- [ ] `<Criterion 1: testable happy-path condition>`
- [ ] `<Criterion 2: testable edge-case/failure-mode condition>`
- [ ] Run `<test/lint command>` and confirm all checks pass with zero errors.
````

---

## Template 2: Architecture / System Design Agent Prompt

Use for system design, technical RFCs, database schema design, or API specification tasks.

````markdown
# Objective
Design `<system/feature name>` and produce a concrete technical specification ready for engineering implementation.

# Context & Problem Framing (SCQA)
- **Situation (Current Architecture):** `<Existing services, databases, infrastructure>`
- **Complication (Bottleneck / Driver):** `<Why the current architecture cannot support the new requirement>`
- **Quantified Scale & Workload (Socratic SLA):** `<Traffic volume, RPS, data growth, latency targets, team size>`

# Design Requirements & Trade-off Priorities (First Principles)
- **Primary Trade-off Priority:** `<e.g., Operational simplicity > low latency > strict consistency>`
- **Must-Have Capabilities (MECE):**
  1. `<Data & Storage capability>`
  2. `<Processing & Integration capability>`
  3. `<Security & Observability capability>`

## Pre-mortem Guardrails & Non-Goals (Inversion)
- **Worst-Case Failure Modes to Design Against:** `<e.g., Duplicate event processing, split-brain state, cascading downstream failure>`
- **Hard Constraints & Out of Scope:** `<e.g., Must run on existing PostgreSQL + Redis stack; no new cloud vendors>`

# Required Deliverable Structure
Produce the specification in Markdown with the following sections:
1. **Architecture Overview:** High-level component diagram (Mermaid) and end-to-end data flow narrative.
2. **Data Model / Schema:** Concrete table definitions, indexes, partitioning, and state transitions.
3. **API / Interface Contracts:** Endpoints, request/response payloads, idempotency keys, and error codes.
4. **Failure Modes & Mitigations (Pre-mortem Analysis):** Concrete mechanisms for retries, dead-letter queues, rate limits, and partial outages.
5. **Trade-offs & Alternatives Considered:** Why this design was chosen over at least 2 alternatives.
````

---

## Template 3: Research / Analysis Agent Prompt

Use for deep research, library/tool evaluation, literature synthesis, or market analysis.

````markdown
# Objective (First Principles)
Investigate `<topic/question>` and deliver an evidence-backed analysis so we can make `<exact decision to make>`.

# Context & Problem Framing (SCQA)
- **Situation & Use Case:** `<Context of the project and what we are building>`
- **Complication (Why This Is Hard):** `<Key trade-off or uncertainty forcing this research>`
- **Candidates / Scope (MECE):**
  - **Must Evaluate:** `<List specific tools, papers, or approaches>`
  - **Explicitly Excluded:** `<What to skip>`

# Quantified Evaluation Rubric (Socratic Criteria)
Evaluate each candidate against these weighted criteria:
1. `<Criterion 1 (Weight %): e.g., Production readiness, license, maintenance velocity>`
2. `<Criterion 2 (Weight %): e.g., Benchmark accuracy / latency under condition X>`
3. `<Criterion 3 (Weight %): e.g., Integration effort with our stack>`

# Pre-mortem Guardrails & Evidence Rules
- **Evidence Standard:** Cite primary sources (official documentation, reproducible benchmarks, source code, or peer-reviewed papers from `<e.g., 2025–2026>`) with direct links. Flag unverified claims explicitly.
- **What Makes This Report Fail (Do NOT do):** `<e.g., Do not copy marketing fluff; do not give a "it depends" conclusion without a clear winner for our constraints>`

# Expected Output Format
1. **Executive Verdict:** Direct, opinionated recommendation for our use case in 3–5 sentences.
2. **Comparison Matrix:** Markdown table scoring all candidates across the quantified evaluation criteria.
3. **Deep-Dive Analysis:** Concrete strengths, hidden gotchas, and failure modes per candidate.
4. **Recommended Next Steps:** Actionable proof-of-concept (PoC) plan or migration checklist.
````

---

## Template 4: Writing / Content / Spec Agent Prompt

Use for technical writing, documentation, product specs, or external communication.

````markdown
# Objective (JTBD)
Write `<document type>` about `<topic>` so that `<target reader>` can `<exact action or takeaway after reading>`.

# Context & Narrative Hook (SCQA)
- **Target Audience:** `<Who they are, their baseline knowledge, and what they care about>`
- **Situation & Complication (The Hook):** `<The tension, pain point, or shift that makes this document matter right now>`
- **Core Thesis / Answer:** `<The central argument or takeaway in 1–2 sentences>`

# Key Points & Structure (MECE)
1. `<Section 1: Key argument/fact + concrete example to include>`
2. `<Section 2: Key argument/fact + concrete example to include>`
3. `<Section 3: Actionable implementation / next steps>`

# Quantified Style & Pre-mortem Guardrails
- **Voice, Tone & Length (Socratic):** Write in `<target language>`, `<word count range>`, using `<e.g., direct, authoritative, practical prose>`.
- **Pre-mortem Anti-Patterns (Must Avoid):** `<e.g., Zero AI throat-clearing intros ("In today's fast-paced world..."); no unsubstantiated claims without code/data examples; no passive voice>`

# Quality Checklist
- [ ] Opens immediately with the SCQA hook or core value proposition.
- [ ] Every claim or instruction is backed by a concrete example, table, or snippet.
- [ ] Strictly respects the word count and anti-pattern guardrails.
````
