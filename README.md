# the-skills

A small repo of AI agent skills — modular, each skill is self-contained with its own `SKILL.md` and `references/`.

**License:** MIT
**Repo:** `https://github.com/pxuanbach/the-skills`

---

## Skills

| Skill | Description |
|---|---|
| [research-workflow](skills/research-workflow/) | Structured 4-phase research workflow (problem framing → info gathering → analysis → report drafting) with parallel data collection, citation-grounded outputs, and reusable reference data for software comparisons, paper deep-dives, and PDF batch extraction. |

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
3. Add a row to the table above.
4. Bump `CHANGELOG.md` under a new version section.

---

## License

MIT — see `LICENSE`.
