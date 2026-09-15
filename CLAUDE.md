# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A modular catalog of AI agent skills distributed as plain Markdown. Each skill under `skills/<name>/` is installed into target coding agents (Claude Code, Pi Agent, Antigravity / Gemini CLI, OpenAI Codex CLI, OpenCode) via `install.sh` / `install.ps1`. Skills are content, not code — there is no build, test, or compile step.

> General conventions (file layout, frontmatter schema, versioning rules, script-file extensions) already live in `AGENTS.md` at the repo root. Read that first; this file adds only what is specific to operating here.

## Common commands

There is nothing to build. The only executable workflows are the installers.

```bash
# Local install test (Linux/macOS) — non-interactive, narrow scope
./install.sh --targets claude --skills wiki-manager

# PowerShell equivalent
.\install.ps1 -Targets claude -Skills wiki-manager

# Install every skill to every agent
./install.sh --targets all --skills all

# Validate that a skill's directory matches the convention
ls skills/<skill-name>/   # must contain SKILL.md; references/ and examples/ are optional
```

No linter, formatter, or test runner is configured. The closest thing to a "review" is the dedicated `review-skill` skill, which audits a skill for structural and metadata correctness — invoke it manually when asked to validate a new or edited skill.

## Where things live

| Path | Purpose |
|---|---|
| `skills/<name>/SKILL.md` | Skill contract — YAML frontmatter (`name`, `description`, `version`, `license`, optional `triggers`/`metadata`) + workflow body. Frontmatter `description` and `triggers` are how agents auto-select the skill, so keep them precise. |
| `skills/<name>/references/` | Optional. Reusable context the agent loads on demand. Heavy reference data lives here, not inline. |
| `skills/<name>/examples/` | Optional. Worked-through sample outputs. |
| `skills/<name>/scripts/` | Optional. `.mjs` (Node), `.ps1` (Windows), `.sh` (POSIX) helpers. The `screenshot` and SDLC skills use this directory; avoid duplicating logic across script types. |
| `install.sh` / `install.ps1` | Remote installer. Fetches the file list from the GitHub API at runtime, falls back to a hardcoded list (see `FALLBACK_SKILLS` in `install.sh`) when offline. |
| `register-skills.sh` / `.ps1` | Skill-registration helper. |
| `notes/` | Drafts and design notes that feed new skills, not user-facing docs. |
| `docs/paper_summary/` | Default output destination for the `read-paper` skill. Gitignored. |
| `CHANGELOG.md` | Follows [Keep a Changelog](https://keepachangelog.com/). Every shipped skill addition or behavior change gets a versioned entry. |
| `.claude/settings.local.json` | Project-scoped Claude Code permission allowlist + skill overrides (`skillOverrides`). Do not edit casually — these are the agent's local guardrails. |

## Skill groups and how they relate

The catalog has two layers. Treat changes to each differently.

**1. Standalone skills** — `init-agents`, `screenshot`, `antigravity-cli`, `research-workflow`, `read-paper`, `review-skill`. Each works in isolation; cross-references between them are advisory, not structural.

**2. SDLC RAD pipeline** — six skills designed to be used as a sequence, all coordinated through a shared "LLM Wiki" artifact directory:

```
requirement-analyzer  →  user-designer  →  constructor  →  {quality-reviewer, security-reviewer}
                              ↑
                        wiki-manager  (cross-cutting: shared doc hub used by every step)
```

- `requirement-analyzer` formalizes requirements and user stories into the wiki.
- `user-designer` transforms approved requirements into design + `plan.md`.
- `constructor` executes the plan and produces testing evidence.
- `quality-reviewer` and `security-reviewer` run in parallel against the constructor's output.
- `wiki-manager` is the query/organize layer every step reads from and writes to.

When editing an SDLC skill, keep the pipeline contract intact: each step's frontmatter `description` must continue to advertise the right phase, and the position-flowchart node must match the skill's actual role. Adding a new SDLC skill requires updating that flowchart in all six files plus the `README.md` SDLC table.

## Working on a skill

1. Read the existing skill (the `references/` and `examples/` files often encode rationale that's not in `SKILL.md`).
2. Edit `SKILL.md` and any supporting files together — they cross-reference each other.
3. Run `review-skill` against the changed skill if you want a self-check (it reads the file and reports frontmatter/consistency issues).
4. Add a `## [<version>] — <date>` entry to `CHANGELOG.md` under a new version section. Format follows Keep a Changelog (`### Added`, `### Changed`, `### Fixed`, `### Removed`).
5. If the skill is new, add a row to the appropriate table in `README.md` (standalone skills table or the "New SDLC Workflow — RAD (6 skills)" table). If the change affects an existing skill's behavior description, update that row's text in place.

## Things to avoid

- **Don't duplicate AGENTS.md.** Skill frontmatter schema, file layout, and extension conventions already live there. Cross-link instead of restating.
- **Don't vendor tool names into skills.** Skills are agent-agnostic on purpose. Reference tools by capability (e.g. "browser", "terminal", "OCR") and let each agent map them — `read-paper/SKILL.md` documents this explicitly under "Tool portability". The exception is `scripts/`, where `.mjs` / `.ps1` / `.sh` files are obviously platform-bound by their extension.
- **Don't add `dependencies` or `requirements.txt` at the repo root** unless something actually runs at install time. The installers are pure shell; runtime deps (e.g. `docling`, `playwright`) belong in the skill that needs them, listed in its own references.
- **Don't move file outputs out of `docs/paper_summary/`** without updating both `read-paper/SKILL.md` and `.gitignore` — the existing entry keeps the directory from being committed.
