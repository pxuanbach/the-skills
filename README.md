# the-skills

A small repo of AI agent skills — modular, each skill is self-contained with its own `SKILL.md` and `references/`.

**License:** MIT
**Repo:** `https://github.com/pxuanbach/the-skills`

---

## Skills


| Skill                                          | Description                                                                                                                                                                                                                                                      |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [research-workflow](skills/research-workflow/) | Structured 4-phase research workflow (problem framing → info gathering → analysis → report drafting) with parallel data collection, citation-grounded outputs, and reusable reference data for software comparisons, paper deep-dives, and PDF batch extraction. |
| [screenshot](skills/screenshot/)               | Capture screenshots of web pages with stealth mode to bypass anti-bot detection. Saves images to `.temp/` in the current workspace. Supports Cloudflare-protected sites.                                                                                         |
| [review-skill](skills/review-skill/)           | Review and validate Agent Skills for structural consistency, metadata accuracy, instruction clarity, and adherence to repo conventions.                                                                                                                |


### New SDLC Workflow - RAD (6 skills)

A modular software development lifecycle workflow — each skill is self-contained and can be used independently or as a pipeline.


| Skill                                                | Role                                                                                                                                                             |
| ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [requirement-analyzer](skills/requirement-analyzer/) | Gathers, clarifies, and formalizes software requirements and user stories into the LLM Wiki.                                                                     |
| [user-designer](skills/user-designer/)               | Transforms approved requirements into technical design, UI/UX mockups and implementation plans (`plan.md`).                                                      |
| [wiki-manager](skills/wiki-manager/)                 | Central documentation hub — manages, organizes, and queries all SDLC artifacts (requirements, designs, mockups, plans, evidence). Used by all other SDLC skills. |
| [constructor](skills/constructor/)                   | Executes implementation plans step-by-step — writes code, runs tests, and produces testing evidence in the LLM Wiki.                                             |
| [quality-reviewer](skills/quality-reviewer/)         | Reviews source code, implementation plans, and test evidence for quality, design integrity, and test coverage.                                                   |
| [security-reviewer](skills/security-reviewer/)       | Audits code for security vulnerabilities across 10 critical categories and issues pass/fail decisions.                                                           |


---

## Repo convention

Each skill lives under `skills/<skill-name>/`:

```
skills/
└── <skill-name>/
    ├── SKILL.md          # Required: YAML frontmatter + workflow body
    ├── references/       # Optional: pre-researched data and reusable patterns
    │   └── *.md
    └── examples/         # Optional: example outputs
        └── *.md
```

When adding a new skill:

1. Create `skills/<skill-name>/SKILL.md` with valid YAML frontmatter (`name`, `description`, `version`, `license`).
2. Add `references/` for context that the agent should load on demand.
3. Add a row to the table above (or to the SDLC Workflow table if part of that group).
4. Bump `CHANGELOG.md` under a new version section.

> **SDLC Workflow skills** are designed to work together as a pipeline: `requirement-analyzer` → `user-designer` → `constructor` → `quality-reviewer` / `security-reviewer`, all coordinated through `wiki-manager`. When adding a skill to this group, ensure frontmatter `name` and `description` are precise — agents use these fields to select the right skill automatically.

---

## License

MIT — see `LICENSE`.