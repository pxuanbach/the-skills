# Section Guides

Order of use: Title/Acronym → Abstract → Teaser → Introduction → Method/Equations → Experiments → Related Work → Figures → Conclusion.

## Title

- Condense the abstract's key contribution to a short, suggestive line. Short, memorable, relevant.
- Preliminary work that starts something new: "Towards …". Foundational or insight papers that open an area: "On …".
- Avoid being too cute; a science paper is not a marketing pamphlet.
- Put the acronym in the title when it fits naturally; do not distort the title for it.

## Acronym

- Short, pronounceable, distinctive, searchable (check it does not collide with common words or existing methods; avoid names like NASA/NeRF that mean other things).
- Prefer **invertible**: the name hints at the words that formed it, ideally from the first nouns/verbs. Bonus: the name reinforces the contribution (e.g. a model designed to be "simple" named SMPL).
- Method: list the key words, take their letters, find real words related to the topic (consider other languages, Latin, Greek). Online word-finder tools help non-native speakers. Semantic link to the topic is the goal; an awkward expansion is fine if the final name is good.
- Offer 3–5 candidates, each with its expansion and a one-line rationale.

## Abstract

Fill-in skeleton (keep the connective words; they carry Goal-Problem-Solution):

```
___ is widely used in <field> and has applications in ___.        (Goal)
Recent work addresses this problem by ___.
Unfortunately, all of these approaches ___.                       (Problem)
In contrast, we ___ [nugget].                                     (Solution)
This fixes ___; however, it does not solve ___.                   (Problem)
Consequently, we develop a novel ___.                             (Solution)
While promising, ___ is non-trivial.                              (Problem)
Therefore, we further ___.                                        (Solution)
We evaluate ___ qualitatively and quantitatively on ___ and find that it is more accurate than <named baseline>.
Code and data will be available for research purposes.
```

If the abstract lacks "Unfortunately / In contrast / While promising / Therefore" or equivalents, the story is probably not being told. Journals with a fixed summary-paragraph format: follow the venue's format, keep the same story. The skeleton expands into the introduction.

## Teaser

A teaser figure is the visual abstract; abstract + teaser may be all some read. Forms:

- **Summary of results** (strong, attractive results shown first).
- **Illustration of the problem** (how current methods fail, how yours succeeds).
- **System overview** — only if it is a simple cartoon; otherwise keep it off page one.

## Introduction

- First impression decides: by the end of the intro the reviewer has mostly decided. An unhappy reviewer stays unhappy.
- Do not write "We are interested in X". Write "X is important because … and unsolved because …". The paper is about the problem in the world, not the authors.
- Follow Goal → Problem → Solution; consider opening with a revealing example.
- Include a contributions paragraph ("Our key idea is…", "Our contributions are…") so the reviewer can lift a summary directly.
- Avoid a "the rest of this paper is organized as…" paragraph; the structure should be self-evident. Exception: a complicated method deserves a short overview section with a figure.

## Method and equations

- Explain each important concept three ways: **text** (gist, non-technical), **equation** (precision), **figure** (intuition). Repeat this block for rhythm.
- Equations must match the code. Write equations and code together so mismatches (bugs) surface while experiments can still be rerun. After experiments finish, the text follows the code, even if embarrassing.
- Notation: do not overload symbols; define conventions for scalars, vectors, matrices, constants, functions, sets, optimized parameters. Keep a notation table from day one; inconsistencies show up fast.
- Treat equations as sentences: commas and periods inside the equation, comma before "where …".
- Do not repeat equations or text; if you do, the flow is wrong.

## Experiments

- Implement the **simplest baseline first**; simple baselines are often hard to beat.
- Change **one thing at a time** (ablations). If method and data change together, nobody knows which mattered. The reader must know what was important after reading.
- Be fair: the aim is to learn and teach, not to flatten the competition. State what the experiments reveal about each method.
- A table of numbers is not enough: say what the numbers mean. The numbers should tell a story that validates a claim.
- Report results neutrally. Results test the hypothesis; they do not sell the method.

## Related work

- Organize by **theme**; each paragraph covers a topic and says what prior art got right and what it missed. Analyze, do not list.
- It should teach the history of the field and frame it relative to this paper.
- Dig back in time before writing "to the best of our knowledge we are first"; citing only the last few years makes that claim weak.
- Use present tense even for past work ("Black et al. [3] propose…").
- Treat cited authors respectfully: state what was good, then how this work goes further. Likely reviewers are among those cited.

## Figures

- Figures form a paper within the paper; many readers only read figures and captions.
- Start early: sketch placeholders so the paper has figures from day one; replace with real ones later. Placeholders also reveal which experiments are critical.
- Caption states the takeaway, what to look at, what colors mean. Highlight key regions with arrows or circles.
- Every figure is referenced in the text, as "Figure 6 shows…", not "In Figure 6 we show…".
- Text legible without zooming; axes labeled with units; color used to convey information.

## Conclusion and limitations

- Write it early, not at the last minute. Concise present-tense review of key insights and results, with a bit more analysis than the abstract.
- State limitations honestly and phrase them as future work with a practical path. Do not list so much future work that it appears you claim the whole field.

## Supplementary material and video

- Deliver everything promised in the text; mention the supplement and video in the main text.
- As polished as the main paper; no new experiments if the venue forbids it.
- Show non-cherry-picked results and failure cases. Keep it short.
- Video: < 4 minutes, narrated, scripted, each sentence recorded separately; test on multiple machines. Use time (motion, reveal, overlay) instead of replaying paper figures. More people will watch the video than read the paper.
