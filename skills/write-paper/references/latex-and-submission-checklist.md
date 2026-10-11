# LaTeX and Submission Checklist

Use in Polish mode. Skip LaTeX items if the manuscript is not LaTeX. Report as pass / fail / n/a with locations.

## Timeline

- [ ] Writing started early (draft intro before results; figures as placeholders).
- [ ] Complete draft exists days before the deadline, leaving time for several proofreading passes by multiple people.
- [ ] Senior co-authors receive a polished draft to refine arguments, not to copy edit.

## Content

- [ ] One story; nugget stated; contributions paragraph present.
- [ ] Every claim in abstract and contributions maps to evidence.
- [ ] Limitations discussed, with a path forward.
- [ ] Equations match the code; notation table complete; no overloaded symbols.
- [ ] Simple baseline included; ablations change one thing at a time.
- [ ] Cited most recent or definitive version (conference version, not arXiv, if published).
- [ ] No major related work missing; no disparaging of prior work.

## Equations (LaTeX)

- [ ] Equations punctuated as sentences; "where…" follows a comma.
- [ ] `\hat{c}_i`, not `\hat{c_i}`.
- [ ] No blank line before/after an equation unless a new paragraph is intended (a blank line adds space and indents the next line).
- [ ] No equation runs into margins or gutter: move a part into the text line, or use `\lefteqn`.

## Figures and tables

- [ ] Placed top of page or column (`[t]` or `[tbh]`), not `[h]`.
- [ ] Use `\centering` or `\centerline`, not `center` environment (adds vertical space).
- [ ] Captions state the takeaway; text readable without zoom; axes labeled with units.
- [ ] Every figure and table is referenced in the text.
- [ ] Negative `\vspace` used sparingly; tight pages are harder to read.

## Quotes and typography

- [ ] Opening quotes written as two backticks (` ``quote'' `), not straight `"`.
- [ ] `et al.` / `e.g.` not italicized; one space before `\cite` (`Author~\cite{}` is redundant).
- [ ] Tense consistent; no contractions; consistent heading capitalization.

## Bibliography

- [ ] Citations sorted numerically within brackets: `[3,9,23,64]` (e.g. natbib with `numbers,sort,compress`).
- [ ] Search the PDF for `?` to catch missing references.
- [ ] Proofread the bibliography (there is almost always at least one error); page numbers added where possible.
- [ ] Capitalization protected with braces: `{SMPL}`, `{3D}`, `{AMASS}`.
- [ ] Likely reviewers' work cited and treated fairly.

## Length and layout

- [ ] Uses the full page limit; a short paper looks unfinished.
- [ ] To cut a page without negative space: fix paragraphs whose last line has 1–2 words; pull the `E(x)=` start of a multi-line equation onto the previous text line; condense until a stranded section heading jumps back to the previous page. Do not panic-cut major content first.

## Proofreading

- [ ] Read every word: title, captions, equations, references. Read as a first-time, critical reader who does not know the acronyms, math, or literature.
- [ ] At least one reader who is not an author.

## Supplementary material and video

- [ ] Delivers all that the text promises; mentioned in the main text.
- [ ] Includes failure cases and non-cherry-picked results; no forbidden new experiments.
- [ ] Video (if any): < 4 min, narrated, scripted, plays on several machines, uses motion/time rather than static slides.
