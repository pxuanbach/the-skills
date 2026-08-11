# Changelog

All notable changes to this skill are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/).

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
