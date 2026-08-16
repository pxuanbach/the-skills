# Research Workflow — API & Tool Reference

Condensed reference for information gathering. See parent `SKILL.md` for full workflow.

> **Tool names in this file** (e.g. `delegate_task`, `browser_navigate`, `terminal`) are placeholder names for the corresponding capability. See the Tool Capability Reference in SKILL.md for the mapping. If your agent lacks a capability, report back to the user before substituting.

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

---

## Semantic Scholar API (fast JSON alternative to arXiv)

**Base:** `https://api.semanticscholar.org/graph/v1/`

**Paper search:**
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=YOUR+QUERY&limit=5&fields=title,authors,year,citationCount,externalIds,abstract" | python3 -m json.tool
```

**Paper details by arXiv ID:**
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:2402.03300?fields=title,authors,year,citationCount,influentialCitationCount,abstract" | python3 -m json.tool
```

**Citations OF a paper:**
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:2402.03300/citations?fields=title,authors,year,citationCount&limit=10" | python3 -m json.tool
```

**References FROM a paper:**
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:2402.03300/references?fields=title,authors,year,citationCount&limit=10" | python3 -m json.tool
```

**Rate limit:** 1 req/sec (no key). No rate limit stated but be respectful.

---

## Web Search

**Generic `web_search` tool may not exist on your agent.** If it does exist and works, use it. If not:

1. **Subagent delegation** — spawn concurrent subagents for multi-source queries
2. **URL-opening tool** to primary sources — GitHub, PyPI, official docs (usually fastest and most accurate)
3. **`curl` via shell** to Semantic Scholar API for academic papers (fast JSON, no auth):
   ```bash
   curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=YOUR+QUERY&limit=5&fields=title,authors,year,citationCount,externalIds,abstract"
   ```

**For web search via a browser tool:** Bing is more bot-friendly than Google or DuckDuckGo:
```bash
url_open("https://www.bing.com/search?q=React+vs+Vue+Svelte+2024")
```

---

## Output directory

Default: active workspace's `research_reports/` subdirectory. Create the directory if missing.

If your agent has a configured default workspace (e.g. `D:\Documents\`), use it. Otherwise fall back to the current working directory.

Legacy reports from older sessions may still live at `C:\Users\<user>\research_reports\` — move them into the new location if you want them consolidated.
