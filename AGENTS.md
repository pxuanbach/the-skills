# AGENTS.md

This repository hosts modular AI agent skills for Claude Code, Pi Agent, Gemini CLI, Codex CLI, and OpenCode. Each skill is self-contained with its own `SKILL.md` and optional `references/` and `examples/` directories.

## Commands

This is a skill repository — no build/test commands apply. To validate skill structure:

```bash
# Check skill directories follow convention
ls skills/<skill-name>/
# Each skill should have: SKILL.md, and optionally references/ and examples/

# Test installation scripts (requires target agent directories)
./install.sh --targets claude --skills all
```

## Architecture

```
the-skills/
├── skills/                      # All agent skills
│   └── <skill-name>/
│       ├── SKILL.md             # Required: YAML frontmatter + workflow body
│       ├── references/          # Optional: reusable context data
│       ├── examples/            # Optional: sample outputs
│       └── scripts/             # Optional: helper scripts
├── notes/                      # Drafts and ideas for skills
├── install.sh / install.ps1    # Multi-agent skill installer
├── register-skills.sh/.ps1     # Skill registration scripts
├── CHANGELOG.md
└── README.md
```

## Patterns & Conventions

### Skill Structure (Required)

Every skill must follow this structure:

```
skills/<skill-name>/
├── SKILL.md          # Required: YAML frontmatter + markdown workflow
├── references/       # Optional: reusable context data
│   └── *.md
└── examples/         # Optional: sample outputs
    └── *.md
```

### Skill Frontmatter (Required)

```yaml
---
name: <skill-name>
description: <trigger conditions and purpose>
version: X.Y.Z
license: MIT
---
```

### Adding a New Skill

1. Create `skills/<skill-name>/SKILL.md` with valid YAML frontmatter
2. Add `references/` and `examples/` as needed
3. Update the skill table in `README.md`
4. Bump `CHANGELOG.md` under a new version section

### Script Conventions

- `.mjs` — ES module scripts (Node.js)
- `.ps1` — PowerShell scripts (Windows)
- `.sh` — Bash scripts (macOS/Linux)

### Versioning

- Follows [Semantic Versioning](https://semver.org/)
- Changelog follows [Keep a Changelog](https://keepachangelog.com/)
