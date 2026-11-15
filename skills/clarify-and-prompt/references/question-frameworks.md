# Clarification Frameworks & Question Banks

Use this reference during **Phase 1 (Context Scan & Method Routing)** and **Phase 2 (Framework-Driven Clarification)** to turn vague user requests into sharp, high-leverage questions.

Apply these frameworks **under the hood** — use them to structure your thinking and question design rather than lecturing the user on methodology.

---

## Part 1: The 5 Core Clarification Frameworks

### 1. First Principles & 5 Whys (Root-Cause Excavation)
- **When to trigger:** The user jumps straight to a specific implementation or tool (*"Write a cronjob that copies table A to table B every minute"*) without explaining the underlying problem.
- **How it works:**
  1. Ask *why* the proposed mechanism is needed to uncover the real bottleneck.
  2. Strip away inherited assumptions and identify the irreducible constraints (data, latency, cost, correctness).
- **Question pattern:**
  > *"Is the root goal of `<proposed mechanism>` to solve `<Problem A>` or `<Problem B>`? If `<A>`, should we use `<simpler direct approach>` instead of `<complex mechanism>`?"*

### 2. Jobs-to-be-Done — JTBD (Outcome-Driven Framing)
- **When to trigger:** Feature requests, workflows, or product/UI changes where user motivation or success state is fuzzy.
- **How it works:** Map the request into the 3-part JTBD formula:
  - **When** `[Situation / Trigger event]`
  - **I want to** `[Action / Capability]`
  - **So I can** `[Expected Outcome / Value]`
- **Question pattern:**
  > *"What specific event triggers this flow (When), who or what initiates it (Actor), and what exact state change or outcome must exist immediately after it finishes (So that)?"*

### 3. SCQA + MECE (McKinsey Problem Structuring)
- **When to trigger:** Complex, multi-layered problems (system architecture, large refactors, research comparisons) where context is tangled.
- **How it works:**
  - **SCQA** frames the narrative: **S**ituation (what works today) $\rightarrow$ **C**omplication (what broke, changed, or scaled beyond limits) $\rightarrow$ **Q**uestion (core decision/task) $\rightarrow$ **A**nswer (target architecture/solution).
  - **MECE** (*Mutually Exclusive, Collectively Exhaustive*) splits the problem into non-overlapping buckets (e.g., *Input/Data* | *Processing/Logic* | *Output/State* | *Failure/Edge Cases*) so 3–5 questions cover 100% of the surface area without redundancy.
- **Question pattern:**
  > Divide the 3–5 questions cleanly across buckets: Question 1 on **Data/Input**, Question 2 on **Core Logic/Complication**, Question 3 on **Output/Integration**.

### 4. Socratic Questioning (Quantifying Ambiguity)
- **When to trigger:** **Every session** where the user uses subjective adjectives (*"fast", "scalable", "clean", "modern", "lightweight", "thorough", "secure"*).
- **How it works:** Challenge vague terms by offering concrete, testable translations.
- **Vague-to-Testable Translation Table:**

| User Says | Socratic Question to Ask | Testable Constraint in Prompt |
|---|---|---|
| "Make it fast / high performance" | Latency p95 < 100ms, or high throughput (1,000 jobs/sec)? | `p95 response time < 100ms under 50 concurrent requests` |
| "Keep it simple / lightweight" | Zero external libraries (stdlib only), or single-file script? | `Use Python standard library only; single file < 300 lines` |
| "Handle errors gracefully" | Fail fast with HTTP 4xx/5xx, retry in background, or return fallback value? | `Retry 5xx/network timeouts 3x with exponential backoff; fail immediately on 4xx` |
| "Write a thorough research report" | Compare 3–5 top tools with a decision matrix, or academic literature survey? | `Evaluate top 4 open-source options across 5 weighted criteria with primary citations` |

### 5. Pre-mortem / Inversion (Failure-First Guardrails)
- **When to trigger:** **Every session** (use as the final question in Round 1) to define **Non-Goals** and prevent the agent from over-engineering or breaking existing behavior.
- **How it works:** Invert the problem — assume the agent executed the prompt and the user rejected the result or it broke production. Ask what went wrong.
- **Question pattern:**
  > *"To lock down safe boundaries (Non-goals): What must the agent strictly avoid touching or doing (e.g., do not alter existing DB schemas, do not add external packages, do not modify current UI)?"*

---

## Part 2: Composing the 3–5 Questions (The Golden Template)

When writing your clarification turn in **Phase 2**, assemble 3–5 questions using this slot structure:

1. **Slot 1 — Root Goal & Trigger (First Principles / JTBD / SCQA):** Confirm the core objective, trigger condition, and why current state is insufficient.
2. **Slot 2 — Functional Scope & Architecture (MECE Bucket A):** Pin down the main data flow, tech stack integration, or structural approach.
3. **Slot 3 — Edge Cases & Quantification (Socratic / MECE Bucket B):** Turn fuzzy requirements (error handling, performance, scale, format) into hard metrics.
4. **Slot 4 — Guardrails & Non-Goals (Pre-mortem Inversion):** Explicitly confirm what is out of scope and what failure mode must be avoided.

*(Always attach a `*(Recommended: ...)*` option to every slot so the user can confirm in seconds.)*

---

## Part 3: Domain-Specific Question Banks

### 1. Coding & Bugfix Tasks
*First inspect `package.json`, `pyproject.toml`, `Cargo.toml`, `AGENTS.md`, or target source files.*
- **[JTBD / Trigger]:** What exact input, API call, or user action triggers this behavior, and what is the expected return value/state change?
- **[MECE — State & Schema]:** Does this require schema/interface changes, or must it stay strictly backwards-compatible with existing callers? *(Recommended: Backwards-compatible)*
- **[Socratic — Error & Edge Cases]:** When invalid input, empty data, or upstream timeout occurs, should it throw an exception, retry, or return a safe default? *(Recommended: ...)*
- **[Pre-mortem — Non-Goals]:** Which existing files, public APIs, or dependencies must remain untouched, and what test command proves nothing regressed? *(Recommended: Existing dependencies only + pass unit tests)*

### 2. Architecture & System Design Tasks
- **[SCQA — Complication]:** What is the specific bottleneck or limitation in the current system that forces this new design now?
- **[Socratic — Scale & SLA]:** What concrete workload must this handle (requests/sec, dataset size, latency target) over the next 6–12 months? *(Recommended: ...)*
- **[First Principles — Trade-off Priority]:** When trade-offs arise, which wins: operational simplicity, low latency, strict data consistency, or cost? *(Recommended: Operational simplicity)*
- **[Pre-mortem — Failure Mode]:** What is the worst-case failure scenario (e.g., duplicate billing, data loss, cascading timeout) that the design must explicitly prevent?

### 3. Research & Technical Analysis Tasks
- **[First Principles — Decision Goal]:** What concrete decision or action will you take immediately after reading this research?
- **[MECE — Candidates & Scope]:** Which specific tools, papers, or approaches must be included, and which should be excluded right away?
- **[Socratic — Evaluation Rubric]:** Rank the top 3 criteria that determine the winner (e.g., open-source license, benchmark accuracy, self-hosting cost, DX). *(Recommended: ...)*
- **[Pre-mortem — Useless Output]:** What would make this report useless to you (e.g., generic surface-level summaries without benchmarks, outdated pre-2025 sources, lack of clear recommendation)?

### 4. Writing & Content Creation Tasks
- **[JTBD — Audience & Job]:** Who is the target reader, what do they already know, and what single action/belief should they walk away with?
- **[SCQA — Hook & Structure]:** What is the tension or problem that hooks the reader in the first paragraph, and what section structure works best? *(Recommended: ...)*
- **[Socratic — Tone & Length]:** What concrete length (word count / reading time) and tone (e.g., direct engineering blog vs. executive proposal) should be enforced? *(Recommended: Direct, concise, zero fluff)*
- **[Pre-mortem — Anti-Patterns]:** What stylistic habits or content mistakes would make you rewrite this draft (e.g., AI clichés, missing code examples, overly abstract prose)?
