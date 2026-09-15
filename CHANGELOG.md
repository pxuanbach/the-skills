# Changelog

All notable changes to this skill are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.4.2] — 2026-09-14

### Changed
- **`read-paper` skill — review-skill Medium fixes 2-5 + docling migration.**
  - **SKILL.md fix (2):** replaced vague "Pass 4 is for the parts that earn their reading time" with four agent-checkable completion criteria (one-sentence contribution, 3-sentence framing, 5-minute explanation, answer to specific question).
  - **SKILL.md fix (3):** split the old combined "user's attention / what they can apply" question into two question-aligned signals that map to `MEMORY.md` calibration signals B (active focus) and C (applicable methods).
  - **SKILL.md fix (4):** added explicit hallucination anti-pattern with a concrete Transformer-example failure mode ("drawing a Mermaid block that resembles a Transformer encoder/decoder without naming the paper's actual modules, then claiming it represents Figure 1").
  - **SKILL.md fix (5):** named the paper in the example file description ("Attention Is All You Need", Vaswani et al., 2017) so it's clear what the example covers.
  - **Tool portability:** swapped `PyMuPDF` for `docling` in the Tool Capability Reference and the Quick-start recipe to match the new primary extraction tool.
- **`references/paper-sources.md` — full rewrite around docling.**
  - Replaced the `PyMuPDF` extraction approach with `docling` (Python API + CLI) as the primary PDF → Markdown tool. Docling preserves layout, handles scanned PDFs via built-in OCR, and outputs structured Markdown suited for downstream PACES analysis.
  - Updated install instructions (`pip install docling`, `uv add docling`, `docling[mac_intel]`), replaced PyMuPDF-specific pitfalls with docling-relevant ones (first-run ML-model download, sandboxed `pip`, large paper slicing), and updated the Quick routing table.
  - Reference: [docling quickstart](https://docling-project.github.io/docling/getting_started/quickstart/).

## [1.4.1] — 2026-09-14

### Changed
- **`read-paper` skill — slop tightening pass** (via Antigravity CLI).
  - Cut 21 instances of filler, repetition, mechanical phrasing, and inverted pitfalls across all 5 files (SKILL.md, references/, examples/).
  - Critical fix: inverted pitfall in `memory-cross-reference.md` (was listing "Skipping basics" as a pitfall title instead of "Re-explaining basics the user already knows").
  - Stripped verbatim copy-pasted Python script block and duplicated `grep` slicing recipes from `paper-sources.md`.
  - Removed scratch-note residue (`> MEMORY.md is your knowledge in the domain/fields...` quote) from `memory-cross-reference.md`.
  - Reframed `MEMORY.md` meaning to match original notes intent: user's domain knowledge profile (existing expertise / active focus / applicable methods), not a generic working-memory notebook.
  - Tightened worked examples and corrected minor grammar (`de-facto` → `de facto`).
- File line counts grew in some places (clarification sub-headings, expanded pitfall tables) but prose density improved — the per-sentence tightening is the actual win, not the line count.

## [1.4.0] — 2026-09-14

### Added
- New **`read-paper`** skill for reading and analyzing a single research paper using the PACES framework (Purpose / Approach / Claims / Evaluation / Synthesis).
- 4-pass reading strategy: title+abstract+figures → intro+conclusion → full body → targeted deep dive.
- Output template with frontmatter (title, description, authors, domain, keywords, arxiv_id, memory_links).
- Default output location: `docs/paper_summary/<slug>_<YYYYMMDD>.md` (Markdown by default, HTML on request).
- Cross-references the user's `MEMORY.md` (or `AGENTS.md` / `CLAUDE.md`) and adds follow-up entries to a reading-list section.
- Supports paper sources: arXiv URL, local PDF, paper title (via Semantic Scholar), screenshot (via OCR).
- 3 reference files: `paces-method.md` (detailed PACES guide with worked examples), `memory-cross-reference.md` (MEMORY.md linking patterns), `paper-sources.md` (arXiv / PDF / OCR recipes). 4-pass reading strategy details (time budget, stop signals) are inlined in SKILL.md to avoid duplication.
- 1 example file: `examples/sample-paces-analysis.md` (worked PACES analysis of "Attention Is All You Need").
- Anti-trigger clause in description to avoid clashing with `research-workflow` (use research-workflow for literature surveys or batch reading, not read-paper).

## [1.3.2] — 2026-09-02

### Added
- Added **OpenCode** support (`~/.config/opencode/skills`) to installer (`install.ps1`, `install.sh`) and skill registration scripts (`register-skills.ps1`, `register-skills.sh`).
- Updated fallback skill lists across installers to include all repository skills (`antigravity-cli`, `init-agents`).

## [1.3.1] — 2026-08-24

### Added
- Added SDLC workflow position flowchart to all 6 RAD skills (`wiki-manager`, `requirement-analyzer`, `user-designer`, `constructor`, `quality-reviewer`, `security-reviewer`) highlighting current node position.

## [1.3.0] — 2026-08-12

### Added
- New `screenshot` skill for capturing web page screenshots
- Stealth mode using `playwright-extra` and `puppeteer-extra-plugin-stealth` to bypass Cloudflare and anti-bot detection
- Three scripts: `screenshot.mjs`, `validate-url.mjs`, `check-deps.mjs`
- Support for multiple output formats: WebP (default), PNG, JPEG
- Viewport-only capture by default (16:9: 1280x720)
- Random browser fingerprints (Chrome, Firefox) to avoid pattern detection
- Automatic `.temp/` folder creation in workspace

### Features
- URL validation with security checks (blocks localhost, private IPs)
- Dependency checker with global install vs npx options
- Cloudflare challenge detection and reporting
- 30s default timeout, configurable via `--timeout`

### Dependencies
- `playwright`
- `playwright-extra`
- `puppeteer-extra-plugin-stealth`

## [1.2.0] — 2026-08-10

### Added
- Initial public release of the `research-workflow` skill
- 12 reference files covering APIs, data-collection patterns, software comparison, single-paper deep-dive, local PDF batch extraction, and elearning reference data
- README with installation instructions for Hermes Agent, Claude Code, Cursor, and generic system-prompt use
- LICENSE (MIT) and this changelog

### Changed
- Restructured repo to multi-skill convention: `skills/research-workflow/SKILL.md` (was `SKILL.md` at root)
- Updated README with full install instructions for Hermes Agent (with symlink recipe), Claude Code, Cursor, and generic use
- **Repo URL changed** — now hosted at `https://github.com/pxuanbach/the-skills` (multi-skill repo), not `research-workflow-skill`

### Changed
- **Generalized skill for non-Hermes agents.** Removed Hermes-specific paths, variable names, and references from `SKILL.md` and reference files. The skill now works across any agent with browser, terminal, file, and delegation tools. Specific changes:
  - `SKILL.md`: pitfall section rewritten to remove Hermes venv paths, sandbox-specific CLI examples, and Hermes-only rendering claims
  - `references/api-tools.md`: script paths generalized; `web_search` note rewritten
  - `references/data-collection-patterns.md`: tool list rephrased as agent-agnostic; `hermes_tools` mention softened to "sometimes exposes helpers"
  - `references/single-paper-deep-dive.md`: PyMuPDF install instructions rewritten for any agent venv
  - `examples/sample-report.md`: footer rephrased
- **README rewritten as a skills index.** Removed all per-skill install instructions and platform-specific setup. The README is now a short index page listing each skill in this repo (llm-wiki-style).

### Notes
- Source: extracted from a working Hermes Agent profile (`researcher`)
- Hermes references that remain (`author: Hermes Agent`, `metadata.hermes` in frontmatter) are credit/metadata only — they do not claim the skill is Hermes-only
- The skill is verified to work in any agentic environment with: `browser_navigate`, `terminal` (curl/python3/uv), `read_file`/`write_file`, `delegate_task`, `execute_code`, `skill_view`

[1.2.0]: https://github.com/pxuanbach/the-skills/releases/tag/v1.2.0
