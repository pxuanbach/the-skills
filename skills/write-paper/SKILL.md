---
name: write-paper
description: |
  Plan, draft, revise, and polish a scientific paper (ML / vision / graphics conference style) using a story-first method: Goal → Problem → Solution and a single key insight (the "nugget").
  Use when the user asks to write a paper, draft an abstract / introduction / related work, improve or polish a manuscript, pick a title or acronym, or prepare a submission.
  Do NOT use for reading someone else's paper (use read-paper) or literature surveys (use research-workflow).
version: 1.0.0
license: MIT
platforms: [linux, macos, windows]
triggers:
  - "write paper"
  - "write a scientific paper"
  - "draft abstract"
  - "draft introduction"
  - "related work section"
  - "polish manuscript"
  - "paper title"
  - "paper acronym"
  - "improve my paper"
metadata:
  category: research
  related: [read-paper, research-workflow]
---

# Write Paper

Help the user write a paper that is easy for a time-pressed reviewer to accept. Method: find the **nugget** (key insight), tell one story as **Goal → Problem → Solution (repeat)**, and keep every claim backed by the user's own evidence.

> **Tool portability.** Tools are named by capability (file read/write, terminal, web search), not by vendor. Do not assume a specific LaTeX toolchain; ask or detect.

> **Source and attribution.** The method distills Michael J. Black's essay *Writing a good scientific paper* (Medium). Rules are paraphrased in `references/`; venue-specific details (page limits, templates) come from the user's call for papers, not from this skill.

---

## Hard rules

1. **Do not invent results, numbers, citations, datasets, or baselines.** A fabricated claim can reach a submitted paper and damages the authors' credibility, so every claim comes from material the user supplied. Missing evidence → write `[TODO: <what is needed>]` and list it in the final report.
2. **Do not write the whole paper in one shot.** Work section by section, confirm the nugget first.
3. **The user owns the insight.** Propose candidate nuggets, titles, and claims; the user picks. Generic fluent prose that says nothing is the failure mode — prefer precise and short.
4. **Equations must match the code.** If code is available, check notation and loss definitions against it before finalizing the method section.

---

## Routing — which mode?

| User situation | Mode | Start at |
|---|---|---|
| Idea / early results, no text yet | **Plan** | [Step 1](#step-1--pre-writing-check) |
| Has notes, results, or partial draft; wants a section written | **Draft** | [Step 3](#step-3--draft-in-story-order) |
| Has a full draft; wants it improved | **Revise** | [Step 5](#step-5--revise-for-clarity-and-claims) |
| Deadline within days; text in shambles | **Final push** | [Final push](#final-push-deadline-in-3-days) |
| Near submission / camera-ready | **Polish** | [Step 6](#step-6--polish-and-submission-checks) |
| Wants only a title, acronym, or abstract | **Single artifact** | Jump to the matching section of `references/section-guides.md` |

If the user asks to *read or summarize* an existing paper → defer to `read-paper`.

---

## Step 0 — Resolve inputs

Collect (ask once, in one message, only what is missing):

- Target venue and format (page limit, template, anonymous or not) — if unknown, assume a ~8 page two-column conference paper and say so.
- Source material: notes, results tables, figures, code path, existing draft, related-work list.
- Output location: edit the user's files in place (LaTeX or Markdown) or write drafts to `docs/paper_draft/` by default.

---

## Step 1 — Pre-writing check

Answer the questions in [`references/pre-writing-questions.md`](references/pre-writing-questions.md) with the user: goal, audience, hypothesis, obstacle, **nugget**, 3-sentence elevator pitch, teaser, key prior work and its limits, evaluation, demo, risks, data.

Output a one-page **paper brief** (see [`examples/sample-paper-brief.md`](examples/sample-paper-brief.md)). Gate: if the nugget or hypothesis is missing, say so plainly and help find it before drafting. A paper with no insight is incremental engineering; flag that risk.

## Step 2 — Skeleton first

1. Build the story as a **talk outline** (few words, progressive order). The order of the talk is the order of the paper.
2. List figures as placeholders with one-line captions stating the takeaway; mark which experiment each needs.
3. Choose the title and acronym candidates (see `section-guides.md` → Title, Acronym). Offer 3–5 options, recommend one.

## Step 3 — Draft in story order

Draft in this order, each section against its guide in [`references/section-guides.md`](references/section-guides.md):

1. Abstract (fill-in-the-blank skeleton: goal, prior work, "Unfortunately", nugget, "While promising", evaluation).
2. Introduction (expands the abstract; why important and why unsolved; contributions paragraph).
3. Method (+ overview figure if complicated; text → equation → figure rhythm).
4. Experiments (simple baseline first; one change at a time; explain what numbers mean).
5. Related work (organized by theme, analysis not laundry list, present tense).
6. Conclusion and limitations (limitations phrased as a path to future work).

Write a rough first draft early; logical structure first, grammar later.

## Step 4 — Check claims against evidence

For each claim in the abstract and contributions, name the table, figure, or experiment that supports it. Report unsupported claims. Avoid both over-claiming ("paramount", "unique", "first" without a thorough history search) and under-claiming (state the novel contributions clearly).

## Step 5 — Revise for clarity and claims

1. Run the line-level lint in [`references/style-rules.md`](references/style-rules.md) (fewer words, direct verbs, "more/better than what?", method vs. "we", tense, filler and LLM-tell words).
2. Review as a reviewer would (see [Reviewer lens](#reviewer-lens)).
3. Rewrite to shorten. Shorter text is usually clearer.
4. Return edits as a list of `before → after` with the reason, or as a tracked diff on the user's file. Do not silently rewrite meaning.

## Step 6 — Polish and submission checks

Run [`references/latex-and-submission-checklist.md`](references/latex-and-submission-checklist.md): notation table, equation punctuation, figure/caption quality, citation order and missing references (`?`), bibliography hygiene, layout tricks to hit the page limit, supplementary material and video, proofreading passes.

---

## Reviewer lens

Make the reviewer's form easy to fill in. For the draft, produce a mock review:

| Reviewer asks | Check the paper provides |
|---|---|
| Summary in 3–5 sentences | Key ideas stated explicitly ("Our key idea is…", contributions paragraph) |
| What is good | Significance and value of the ideas are stated, not implied |
| Strengths | Experimental validation summarized with what the numbers mean |
| Weaknesses | Delta from prior work is explicit; limitations are discussed honestly |

Output: likely strengths, likely weaknesses, and the single change that most reduces rejection risk.

---

## Final push (deadline in ≤ 3 days)

Settle for what exists: find the nugget in the current results and tell that smaller, true story. Cut claims the evidence does not support, drop the half-finished second idea (one paper = one story), and prioritize in this order: abstract + intro, figures and captions, method-code consistency, limitations, proofreading.

---

## Output format

End every response with:

1. **Done:** what was produced or changed (file paths).
2. **Open items:** `[TODO]` evidence gaps and unsupported claims (max 5, most important first).
3. **Next action:** one concrete step for the user.

---

## References

| File | Load when |
|---|---|
| [`references/pre-writing-questions.md`](references/pre-writing-questions.md) | Plan mode, nugget and story |
| [`references/section-guides.md`](references/section-guides.md) | Drafting any section, title, acronym, figures |
| [`references/style-rules.md`](references/style-rules.md) | Revise mode, line-level lint |
| [`references/latex-and-submission-checklist.md`](references/latex-and-submission-checklist.md) | Polish mode, bibliography, layout, supplementary, video |
| [`examples/sample-paper-brief.md`](examples/sample-paper-brief.md) | Shape of the Step 1 output |
