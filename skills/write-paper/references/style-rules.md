# Style Rules (line-level lint)

Apply in Revise mode. Report each hit as `location: before → after (rule)`.

## Concision and directness

| Rule | Bad | Better |
|---|---|---|
| Use fewer words; cut filler | "It is worth noting that…" | delete |
| No hedged "can" for things done | "We can compute X with Y." | "We compute X with Y." |
| Drop "aim to / try to" | "We aim to exploit…" | "We exploit…" |
| Skip announcements | "In this section we do the following…" | just do it |
| "More / better" needs a comparator | "Our method is more accurate." | "…more accurate than <baseline>." |
| Avoid "allows to" | "A warping field allows to model deformations." | "A warping field models deformations." |
| Replace vague verbs (provides, enables, allows) with the mechanism | "enables robust tracking" | "tracks robustly by <how>" |
| No absolutes that invite a fight | "paramount", "unique", "first" | state a bounded, supported claim |
| "To that end" only if the end is clear | | |

## Subject and voice

- The **method** does things, not "we": "The method optimizes over shape space", not "We optimize…" (that implies the authors did it by hand).
- "Figure 6 shows…", not "In Figure 6 we show…".
- State what was done; if it was not done, do not write it.

## Tense and tone

- Present tense throughout, including prior work. Exception: describing how a dataset was collected or human-subject experiments (past).
- No contractions. No exclamation marks.
- Impartial: results evaluate the method; do not "showcase" them.
- Watch for LLM-tell filler: delve, showcase, pivotal, comprehensive landscape. Grammatical but empty prose is a red flag; if a sentence says nothing, cut it. Use language tools for grammar only; the insight must come from the authors.

## Consistency

- One capitalization style for headings and stick to it. Inconsistent details suggest inconsistent code and experiments.
- Hyphenate compound adjectives ("state-of-the-art results"; not "the state of the art" as a noun). Spell out an abbreviation at first use.
- Define each acronym once; keep notation unchanged across sections.

## Citations in prose

- Do not start a sentence with a bare citation ("[10] was first…"). Write "Author et al. [10] were first…" or reword without the author.
- Names followed by a reference take one space, not zero or two.
- Not italicized: et al., e.g.

## Reduce

- Reworking to shorten almost always improves clarity.
- Repeated text or equations signal a flow problem; restructure instead.
- Every paragraph last line with 1–2 words: rework to reclaim the line (and clarify).
