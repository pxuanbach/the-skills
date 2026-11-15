---
name: clarify-and-prompt
description: Clarify ambiguous requests through bounded questions (3-5 per round, max 2 rounds) using structured thinking frameworks, then generate a complete, context-rich task prompt the user gives to an AI agent as its starting instruction. Use when the user asks to clarify a problem, refine an idea into a prompt, or generate a detailed prompt for an agent. Do NOT use when the user wants immediate task execution or formal SDLC wiki documentation.
version: 1.1.0
license: MIT
---

# Clarify and Prompt

Turn rough ideas or underspecified requests into a complete, self-contained task prompt. The user pastes it into an agent as the agent's **first and only instruction**, so it must carry all the context the agent needs to start work.

> **This is not a handoff.** The receiving agent is not continuing another session and has no prior work to pick up. The prompt must read as a fresh task brief addressed directly to the agent ("Your task is..."), not as a summary of a past conversation, because an agent that believes earlier work exists will search for it or skip setup.

## Core Principles

- **Inspect before asking:** If the task touches a local repository or provided documents, read relevant files first because asking the user for facts already present in the workspace wastes their attention.
- **Framework-driven inquiry:** Select the right problem-framing method via the Method Router below rather than asking random surface-level questions because structured frameworks expose root causes, hidden risks, and measurable criteria in fewer turns.
- **Bounded questioning:** Ask 3–5 high-leverage questions per turn for at most 2 rounds because open-ended interviews cause decision fatigue.
- **Stop early when clear:** Skip remaining rounds as soon as the goal, constraints, and acceptance criteria are unambiguous, or when the user says "enough" / "create the prompt now".
- **Self-contained output:** Write the final prompt as a fresh task brief. The agent starts with zero knowledge of this clarification chat, so inline every fact and decision it needs.
- **Plain requirements:** State decisions as requirements ("Use HMAC-SHA256"), not as outcomes of a conversation, because phrases like "as discussed" imply a session the agent cannot see.
- **Objective only, no role:** Do not assign a persona ("You are a Senior Engineer..."), because it adds no task information. Open with the Objective.
- **Match the user's language:** Conduct the interview and write the final prompt in the language the user used, unless they request a specific output language for the prompt.

## Workflow

```
Phase 1: Context Scan & Method Routing
       │
       ▼
Phase 2: Framework-Driven Clarification (3–5 questions/round, max 2 rounds)
       │
       ▼
Phase 3: Synthesis Summary (SCQA + Decisions + Pre-mortem Risks + Assumptions)
       │
       ▼
Phase 4: Prompt Generation (Fenced code block + optional file save)
```

### Phase 1: Context Scan & Method Routing

1. **Classify the target task domain:** Coding/Bugfix, Architecture/System Design, Research/Analysis, or Writing/Content.
2. **Scan local context (when applicable):** Inspect relevant workspace files (`package.json`, `pyproject.toml`, `README.md`, target modules) to extract tech stack, conventions, and file paths before formulating questions.
3. **Route to the right clarification frameworks:** Diagnose where the user's request is weak and pick 1–2 primary methods plus the mandatory closing checks from `references/question-frameworks.md`:

| Symptom in User Request | Primary Framework to Apply | Purpose |
|---|---|---|
| Prescribes a solution without clear root problem ("Build X for me") | **First Principles & 5 Whys** | Uncover the root cause and strip away unnecessary assumptions |
| User/product feature with fuzzy value or trigger ("Add feature Y") | **Jobs-to-be-Done (JTBD)** | Lock down *When [situation] → I want [action] → So I can [outcome]* |
| Tangled, multi-part, or messy context | **SCQA + MECE** | Frame *Situation → Complication → Question* and split into non-overlapping branches |
| Uses vague adjectives ("fast, clean, modern, secure, thorough") | **Socratic Quantification** *(Mandatory)* | Convert subjective words into testable numbers, thresholds, or concrete rules |
| High risk of the agent hallucinating or over-engineering | **Pre-mortem / Inversion** *(Mandatory)* | Ask "What would make this output a failure?" to lock down **Non-Goals** and edge cases |

### Phase 2: Framework-Driven Clarification

Ask **3 to 5 numbered questions** in a single turn, synthesized from the chosen frameworks:

- **Question composition per round:**
  1. **1–2 Root/Framing questions** (from *First Principles / 5 Whys / JTBD / SCQA*) to confirm the core problem and scope.
  2. **1–2 Socratic Quantification questions** (decompose via *MECE*) to pin down ambiguous technical trade-offs, inputs/outputs, or metrics.
  3. **1 Pre-mortem / Inversion question** to surface failure modes, boundaries, and strict Non-Goals.
- **Propose a recommended default** for each question (e.g., `*(Recommended: Option A — reason)*`) because giving a concrete starting option lets the user reply quickly (`1A, 2B, 3 ok`) instead of typing essays.
- **Round 2 (only if needed):** Run a second round of at most 3 questions only if critical blockers remain after Round 1. If the user leaves some questions unanswered, turn the recommended defaults into explicit assumptions and move to Phase 3.

### Phase 3: Synthesis Summary

Before outputting the prompt, display a brief synthesis structured by **SCQA** and **Pre-mortem** so the user can verify alignment at a glance:

```markdown
### Agreed Summary
- **Situation & Complication (SCQA):** [Current state + why change is needed now]
- **Core Objective (JTBD):** [1-sentence exact outcome]
- **Key Decisions & Quantified Constraints (Socratic & MECE):** [Concrete choices, stack, and measurable thresholds]
- **Guardrails & Non-Goals (Pre-mortem):** [What the agent must NOT do + failure modes avoided]
- **Assumptions:** [Defaults applied for any skipped questions]
```

### Phase 4: Prompt Generation

Select the matching domain blueprint from `references/prompt-templates.md` and generate the complete prompt inside a single fenced markdown code block (` ```markdown ... ``` `) so the user can copy-paste it directly.

Every generated prompt must include these core sections:
1. **Objective:** The exact outcome required, in 1–3 sentences. No role or persona definition.
2. **Context & Problem Framing (SCQA):** Situation, complication, environment details, and relevant file paths or inputs (no raw chat logs).
3. **Requirements & Quantified Constraints:** Functional requirements (MECE-grouped) and Socratic measurable rules.
4. **Pre-mortem Guardrails & Non-Goals:** Explicit failure modes to avoid and out-of-scope boundaries.
5. **Execution Plan / Expected Output:** Suggested steps or exact deliverable structure.
6. **Acceptance Criteria / Verification:** Concrete checks the agent must pass before finishing.

**Post-output action:** After printing the fenced prompt block, ask the user in one short line if they want to tweak any section or save the prompt to a file (e.g., `.temp/prompt.md` or a custom path).

## Anti-Patterns to Avoid

| Anti-Pattern | Why It Fails | What to Do Instead |
|---|---|---|
| Dumping raw framework jargon on the user ("Please state your MECE SCQA and JTBD") | Makes the interview feel like a business school exam | Apply the frameworks silently to craft sharp, natural questions with options |
| Asking 10+ questions at once | Overwhelms the user and stalls progress | Cap at 3–5 highest-leverage questions with recommended defaults |
| Asking things visible in the repo | Forces the user to do the agent's reading work | Check project files (`package.json`, `README.md`, target modules) first |
| Referencing "as we discussed above" inside the generated prompt | The receiving agent has no access to this conversation | Inline all context, decisions, and constraints directly into the prompt |
| Framing the prompt as a handoff ("Continuing from a previous session...") | The agent assumes earlier work exists, looks for it, or skips setup | Write a fresh brief: Objective, current state of the repo/system, requirements |
| Opening with a role ("You are a Senior Engineer...") | Adds no information and distracts from the task | Open with the Objective |
| Leaving vague adjectives ("make it fast, clean, modern") | Agents interpret vague adjectives unpredictably | Use Socratic questioning to translate into testable constraints (e.g., "p95 < 200ms") |

## References & Examples

- `references/question-frameworks.md` — Deep-dive guide on the 5 problem-clarification frameworks (First Principles/5 Whys, JTBD, SCQA+MECE, Pre-mortem Inversion, Socratic Questioning) and domain question banks.
- `references/prompt-templates.md` — Ready-to-fill prompt blueprints for Coding, Architecture, Research, and Writing tasks.
- `assets/trigger-evals.json` — Positive and negative trigger cases plus output checks for validating this skill.
- `examples/sample-session.md` — End-to-end example showing how frameworks drive clarification, synthesis, and the final copy-pasteable prompt.
