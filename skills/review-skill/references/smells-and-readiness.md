# Skill Smells and Deployment Readiness

Load this file only when the review needs to check anti-patterns or rollout readiness. Report hits in the `Also noted` section of the report.

## Skill Smells (Anti-Patterns)

If the skill under review shows any of these patterns, flag it. Sourced from the Agent Skills cheatsheet.

- **Over 5,000 words in `SKILL.md`.** Probably two skills, or reference material that belongs in `references/`.
- **Two domain teams could plausibly own it.** Not yet decomposed. Split along team boundaries.
- **You can't write three test cases for it.** Description is too vague; the skill does too many things.
- **It does not reference any other resource.** May be a long instruction that belongs in the system prompt.
- **It keeps growing "edge cases" sections.** Each edge case probably wants its own skill.
- **Description starts with "a helpful skill for...".** Rewrite — the description should name the trigger, the inputs, and the output.

## Deployment Readiness

A skill is shippable only when every box clears. This is a separate gate from review: review checks the artifact, this section checks the rollout path.

- [ ] Frontmatter lints cleanly (no schema warnings)
- [ ] Description reviewed by someone other than the author (second-pass bias check)
- [ ] Scripts have unit tests passing in CI
- [ ] Eval suite passes in CI with a documented min-pass threshold
- [ ] Security scan clean (no secrets, no untrusted third-party deps)
- [ ] Cross-tool install paths tested if shipping publicly (at least 2 of: Claude Code, Codex CLI, Antigravity, OpenCode)
- [ ] Org-level admin provisioning updated where applicable (allowed-tools, scope, skill overrides)
