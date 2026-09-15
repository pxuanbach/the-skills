# Reading MEMORY.md Before the Paper

`MEMORY.md` is **the user's domain knowledge in the field the paper is written about** — not a generic working-memory notebook, not a citation database, not a project log. It tells the agent who the user is *in this domain*, so the analysis can be calibrated to them instead of written for a generic reader.

> **Load this file before reading the paper** (Step 0). The three calibration questions shape the entire analysis.

---

## What `MEMORY.md` actually contains

Extract three signals in priority order:

1. **Existing knowledge** — terminology, prior methods, standard benchmarks. Skip what the user has mastered; explain only concepts novel to them.
2. **Active attention** — current projects, open questions, immediate pain points. Prioritize elements relevant to their active focus.
3. **Applicable methods** — techniques and insights that map directly onto their codebase, datasets, or workflows.

The cross-referencing step is **calibration**, not bookkeeping. It changes what you write in every PACES letter, not just a metadata field.

---

## Step 1 — Locate `MEMORY.md`

Resolution order (matches Step 0 of the main skill):

1. `MEMORY.md` in the current working directory.
2. `AGENTS.md`, `CLAUDE.md`, `SYSTEM.md`, or any file under `docs/` in the workspace.
3. If none found and the workspace is non-empty → ask once: *"Where's your MEMORY.md? It holds your domain knowledge — I'll calibrate the analysis to what you already know and what you can use."*
4. If still none → proceed without calibration; mark `memory_links: none — no MEMORY.md provided` in the frontmatter.

---

## Step 2 — Extract the three calibration signals

Read `MEMORY.md` once, in full. Extract three signals:

### Signal A — Existing expertise
What does the user already know? Look for:
- Method/technique names they mention (e.g., "I've used LoRA", "familiar with sparse attention")
- Datasets they've worked with
- Concepts they reference without explaining

→ Use this to **decide what to skip in the analysis**: omit familiar derivations and standard benchmark overviews.

### Signal B — Current attention
What is the user actively working on? Look for:
- Active projects ("currently building X", "stuck on Y")
- Recent questions ("how do I solve Z?")
- Recent reading they've been doing

→ Use this to **decide what to emphasize**: expand the Approach section for active topics; highlight targeted solutions in `S – Synthesis`.

### Signal C — Applicable methods
What can the user apply from this paper? Link the paper's method to their projects, datasets, or codebases. Be specific: not "you might find this useful", but "your seq2seq-translation-pipeline can replace the LSTM encoder with this mechanism — see Section 4".

→ Use this to **populate `S – Synthesis`** with concrete, actionable suggestions, and to populate the frontmatter `memory_links.applicable_to` field.

---

## Step 3 — Apply calibration to PACES

Each PACES letter changes based on what `MEMORY.md` says:

| PACES letter | Without MEMORY.md (generic reader) | With MEMORY.md (calibrated) |
|---|---|---|
| **P – Purpose** | Generic problem statement | Framed in terms the user already cares about; emphasis matches their active question |
| **A – Approach** | Method summary, neutral tone | Skip what they know; emphasize what is novel to *them*; use their vocabulary |
| **C – Claims** | All headline claims equally weighted | Weight claims that matter to their current project higher; de-emphasize what doesn't apply |
| **E – Evaluation** | All datasets/baselines listed | Highlight benchmarks that match their use case; flag results on datasets they've worked with |
| **S – Synthesis** | Generic "this matters because…" | Specific: "your project X could use this because Y, watch out for Z" |

---

## Step 4 — Populate frontmatter

```yaml
memory_links:
  used:
    - section: "Fine-tuning methods"
      note: "LoRA — see references/finetuning.md"
      relevance: "User has experience with LoRA; paper proposes QLoRA as a 4-bit extension"
  applicable_to:
    - "Project: seq2seq-translation-pipeline — paper's linear attention could replace LSTM encoder"
    - "Active question: long-context inference — paper directly addresses this"
  follow_up:
    - "QLoRA paper (Dettmers et al., 2023) — extends LoRA to 4-bit quantized weights; relevant to user's LoRA notes"
```

- `used` — what the user already knows; explains *what was skipped* in the analysis.
- `applicable_to` — concrete links from paper method to user's projects/questions. This is the most valuable field.
- `follow_up` — papers/topics the user should read next based on this paper.

If `MEMORY.md` yields no matches, set these fields to `none` with a brief explanation.

---

## Step 5 — Add new entries to `MEMORY.md`

For each `follow_up` entry, append to `MEMORY.md` under a reading-list section:

```markdown
## Reading list

- [ ] **<paper title>** (<year>, <first author et al.>) — <one-line reason it caught your attention> — <path to analysis>
```

Example:

```markdown
## Reading list

- [ ] **QLoRA: Efficient Finetuning of Quantized LLMs** (2023, Dettmers et al.) — Extends my LoRA notes with 4-bit quantization — docs/paper_summary/dettmers-2023-qlora_20250914.md
- [ ] **A Survey on Parameter-Efficient Fine-Tuning** (2024, Liu et al.) — Comprehensive taxonomy of the LoRA family — docs/paper_summary/liu-2024-peft-survey_20250914.md
```

Also update existing notes if the paper contradicts or extends them. Example: if `MEMORY.md` says *"Best attention: vanilla softmax"* and this paper shows linear attention matches it at long context, edit the note to add the nuance.

---

## What `MEMORY.md` typically looks like

It's a user-maintained markdown file in the paper's domain. Common sections:

- **`## Background`** — what the user knows: terminology, prior methods, foundational papers.
- **`## Active projects`** — what they're currently working on.
- **`## Open questions`** — what they're stuck on, what they're trying to figure out.
- **`## Reading list`** — papers to read next.
- **`## Notes`** — free-form observations, insights, doubts.

`MEMORY.md` is **domain-specific**, not project-specific. A user who works in NLP has a different `MEMORY.md` than one who works in robotics — even within the same repo.

If `MEMORY.md` is sparse, propose these structures to the user at the end of the analysis rather than creating them silently.

---

## Common pitfalls

| Pitfall | Why it's wrong |
|---|---|
| Treating `MEMORY.md` as a citation database | It's the user's domain knowledge profile, not a literature DB. Quality of fit > quantity of links. |
| Re-explaining basics the user already knows | Wastes reading time on familiar concepts. |
| Writing a generic analysis regardless of `MEMORY.md` | Defeats the entire purpose. The cross-reference must visibly change the analysis. |
| `applicable_to` filled with vague entries ("user might find this useful") | Be specific: name the project, the dataset, the question. Vague links add no value. |
| Forgetting to update `MEMORY.md` after reading | Leaves the reading list and domain notes stale. |

---

## Self-check before saving the analysis

- [ ] `MEMORY.md` was read before drafting (not after)
- [ ] `memory_links.used` lists *what the user already knew* (so the reader knows what was skipped)
- [ ] `memory_links.applicable_to` lists *specific user projects/questions* the paper maps to
- [ ] `memory_links.follow_up` lists new reading-list entries with one-line reasons
- [ ] Each PACES letter reflects the calibration (not a generic write)
- [ ] `MEMORY.md` was updated with new reading-list entries
- [ ] If no `MEMORY.md` was available, the frontmatter says so explicitly
