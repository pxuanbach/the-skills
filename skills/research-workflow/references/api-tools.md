# Research Workflow — API & Tool Reference

Condensed reference for information gathering. See parent `SKILL.md` for full workflow.

---

## arXiv API

**Base URL:** `https://export.arxiv.org/api/query`

**Direct curl (primary — reliable, no extra deps):**
```bash
# Title search — best for finding papers by topic name
curl -s "https://export.arxiv.org/api/query?search_query=ti:lora+AND+ti:quantized&max_results=5&sortBy=submittedDate&sortOrder=descending"

# All-fields search — broader coverage
curl -s "https://export.arxiv.org/api/query?search_query=all:LLaMA+fine-tuning&max_results=8&sortBy=submittedDate&sortOrder=descending"

# Boolean combinations for PEFT topics (URL-encode carefully)
curl -s "https://export.arxiv.org/api/query?search_query=ti%3AQLoRA+OR+ti%3Aquantized+AND+ti%3ALoRA&start=0&max_results=5"
```

**Query prefixes:** `all:`, `ti:` (title), `au:` (author), `abs:` (abstract), `cat:` (category)

**Parsing tip:** Pipe through grep for quick extraction:
```bash
curl -s "https://export.arxiv.org/api/query?..." | grep -E "<title>|<summary>|<published>|<author>"
```

**Pitfall:** The `scripts/research_report.py` path in this doc is a relative reference that may be stale. The actual script lives at:
```
~/.local/share/<agent>/profiles/<profile>/scripts/research_report.py
```
Use the full absolute path or invoke directly.

---

## Semantic Scholar API (fast JSON alternative to arXiv)

**Base:** `https://api.semanticscholar.org/graph/v1/`

**Paper search:**
```
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=YOUR+QUERY&limit=5&fields=title,authors,year,citationCount,externalIds,abstract" | python3 -m json.tool
```

**Paper details by arXiv ID:**
```
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:2402.03300?fields=title,authors,year,citationCount,influentialCitationCount,abstract" | python3 -m json.tool
```

**Citations OF a paper:**
```
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:2402.03300/citations?fields=title,authors,year,citationCount&limit=10" | python3 -m json.tool
```

**References FROM a paper:**
```
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:2402.03300/references?fields=title,authors,year,citationCount&limit=10" | python3 -m json.tool
```

**Rate limit:** 1 req/sec (no key). No rate limit stated but be respectful.

---

## Web Search

**`web_search` tool does NOT exist in most agentic environments.** Do not call it — it will error. If your agent exposes it (some do), prefer the alternatives below for consistency.

**Instead use:**
1. **`delegate_task`** — dispatch concurrent subagents for multi-source queries
2. **`browser_navigate`** to primary sources — GitHub, PyPI, official docs (usually fastest and most accurate)
3. **`terminal curl`** to Semantic Scholar API for academic papers (fast JSON, no auth):
   ```bash
   curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=YOUR+QUERY&limit=5&fields=title,authors,year,citationCount,externalIds,abstract"
   ```

**For web search in browser:** Bing is more bot-friendly than Google or DuckDuckGo:
```
browser_navigate("https://www.bing.com/search?q=React+vs+Vue+Svelte+2024")
```

---

## Script (report generator)

**Location:** `~/.local/share/<agent>/profiles/<profile>/scripts/research_report.py`

**Usage:**
```
python3 ~/.local/share/<agent>/profiles/<profile>/scripts/research_report.py "Your topic" --type compare --libraries React Vue Svelte
python3 ~/.local/share/<agent>/profiles/<profile>/scripts/research_report.py "LLaMA fine-tuning" --type hybrid --output D:/Documents/research_reports/llama.md
```

**Key classes (for agent population):**
- `Citation(index, authors, title, source, year, url)` — add via `citations.append()`
- `Source(title, url, snippet, source_type, year, authors)` — add via `sources.append()`
- `ComparisonItem(name, url, language, license, stars, gpu_support, ...)` — add via `items.append()`
- `Finding(text, citation_indices)` — add via `findings.append()`

**The script is a TEMPLATE** — the agent must populate these structures via actual tool calls, then call `generate_report()` to produce output. Do not treat the placeholder output as real research.

---

## Output directory

Default: `D:\\Documents\\research_reports\\` (active workspace). Legacy: `C:\Users\pxuan\research_reports\\`.

To override: `--output /absolute/path/to/report.md`.
