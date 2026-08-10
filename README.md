# Research Workflow Skill

A structured research workflow for AI coding agents — produces citation-grounded reports from any topic, technical problem, or scientific question.

**Author:** Hermes Agent (Nous Research)  
**License:** MIT  
**Original skill:** [`research-workflow`](https://github.com/strands-agents/...) — extracted from a working Hermes Agent profile

---

## What this skill does

When an AI agent receives a research request, this skill guides it through four phases:

1. **Problem Framing** — classify the research type (survey / compare / deep-dive / hybrid), decompose into sub-questions
2. **Information Gathering** — parallel data collection via `delegate_task`, `browser_navigate`, `curl`, and API helpers (Semantic Scholar, arXiv, GitHub, PyPI)
3. **Analysis** — build a feature matrix (software comparisons) or synthesis table (literature reviews); flag consensus, gaps, contradictions
4. **Report Drafting** — write a structured Markdown report with citations, open questions, and references

The workflow is **citation-grounded** — every metric, claim, and recommendation includes a source. The agent is instructed to say "I don't know" rather than fabricate.

---

## Repository structure

```
research-workflow-skill/
├── README.md                  ← this file
├── LICENSE                    ← MIT
├── CHANGELOG.md               ← version history
├── SKILL.md                   ← the skill itself (load with skill_view)
├── references/                ← supporting reference files
│   ├── api-tools.md
│   ├── data-collection-patterns.md
│   ├── software-comparison-patterns.md
│   ├── single-paper-deep-dive.md
│   ├── local-pdf-batch-extraction.md
│   ├── word-extraction-libraries.md
│   ├── excel-libraries.md
│   ├── elearning-nextjs-supabase.md
│   ├── elearning-techstack-reference.md
│   ├── elearning-gamification-data.md
│   ├── elearning-proposal-template.md
│   └── lms-analytics-reference.md
└── examples/
    └── sample-report.md       ← example output
```

---

## Installation

### Option A — Hermes Agent (Nous Research)

The skill is in this repo's SKILL.md format, which Hermes Agent loads natively.

Drop it into a Hermes profile:

```bash
# Locate your Hermes profile (default: %LOCALAPPDATA%\hermes\profiles\<name>\skills\)
SKILLS_DIR="$LOCALAPPDATA/hermes/profiles/researcher/skills"

# Linux / macOS
SKILLS_DIR="$HOME/.local/share/hermes/profiles/researcher/skills"

# Clone straight into the skills directory
git clone https://github.com/<your-username>/research-workflow-skill "$SKILLS_DIR/research-workflow"
```

Then in Hermes chat, invoke the skill:

```
/skill research-workflow
```

Or just describe what you want — the skill's `description` triggers auto-loading.

### Option B — Claude Code / Cursor / Windsurf

These tools don't have a native "skill" system like Hermes, but you can convert this into a `CLAUDE.md` or `.cursorrules`:

```bash
# Extract the body of SKILL.md (skip the YAML frontmatter)
awk 'BEGIN{p=0} /^---$/{p++; next} p==2{print}' SKILL.md > CLAUDE.md

# Place it where the agent picks it up
cp CLAUDE.md ~/CLAUDE.md          # Claude Code (user-level)
cp CLAUDE.md ./.claude/CLAUDE.md  # Claude Code (project-level)
cp CLAUDE.md ./.cursorrules       # Cursor (project-level)
```

**Tip:** The `references/` folder is most useful when the agent can read it on demand. For a Claude-style agent, copy it alongside `CLAUDE.md` and reference it in the body.

### Option C — Generic use as a system prompt

Load `SKILL.md` into your agent's system prompt or context window. The YAML frontmatter is informational; the markdown body is the operational instruction.

---

## Reference files

The `references/` folder contains pre-researched data and workflows. **Load these on-demand** with `skill_view(name="research-workflow", file_path="references/<file>.md")`.

| File | Purpose |
|---|---|
| `api-tools.md` | arXiv API, Semantic Scholar API, GitHub API — exact curl commands, rate limits, Python wrappers |
| `data-collection-patterns.md` | Reusable patterns: parallel `delegate_task`, GitHub/PyPI cross-reference, search-engine quirks |
| `software-comparison-patterns.md` | Pre-researched library landscape for PDF/Excel/Word — stars, licenses, package-name gotchas |
| `single-paper-deep-dive.md` | Workflow for analyzing a single arXiv paper URL (download → extract → analyze) |
| `local-pdf-batch-extraction.md` | Workflow for batch-processing a folder of PDFs (book series, paper dumps) |
| `word-extraction-libraries.md` | python-docx, mammoth, docx2txt, textract, pypandoc — comparison |
| `excel-libraries.md` | openpyxl, xlsxwriter, pandas, pyexcel — comparison |
| `elearning-nextjs-supabase.md` | Live-sourced library comparisons for elearning platform stack |
| `elearning-techstack-reference.md` | Minimal elearning MVP techstack (Next.js + Supabase) |
| `elearning-gamification-data.md` | Retention metrics, streak impact, certificate ROI |
| `elearning-proposal-template.md` | Proposal template for elearning MVP |
| `lms-analytics-reference.md` | LMS analytics: xAPI, SCORM, dashboards, metrics |

---

## Citation philosophy

This skill is opinionated about citations:

- **Every metric has a source.** Performance numbers, dates, version strings — all cited.
- **"I don't know" is a valid answer.** The skill instructs agents to refuse to fabricate data when sources are missing.
- **Verification, not self-report.** When a subagent claims "uploaded successfully", the orchestrator must verify before reporting success.
- **Official docs > peer-reviewed > preprints > blog posts > forum posts.** This ranking is enforced.

---

## Lessons encoded in pitfalls

The skill (especially `data-collection-patterns.md`) captures real failure modes observed in production:

- `web_search` tool not existing in some agent environments (use `delegate_task` / `browser_navigate` / `curl`)
- DuckDuckGo CAPTCHA fires in browser sessions (go straight to primary sources)
- GitHub org name ≠ PyPI package name (always query PyPI JSON first)
- Inline `python3 -c "..."` blocked in some terminals (write to file first)
- Subagent output files land in home directory, not workspace (check & move)
- `search_files` on Windows silently returns 0 for some directory paths (use `terminal ls`)
- AGPL-3.0 (PyMuPDF, pymupdf4llm) is a hard blocker for closed-source projects

---

## Contributing

PRs welcome. When adding or modifying reference files:

1. Keep the data live and verifiable — cite the source
2. Update the frontmatter `version` in `SKILL.md` if behavior changes
3. Add a row to `CHANGELOG.md`
4. Verify the skill still works against a fresh Hermes Agent profile before submitting

---

## License

MIT — see `LICENSE`.
