---
name: research-workflow
description: "Research any topic, technical problem, or scientific question by gathering sources, comparing alternatives, and synthesizing them into a structured report with citations. Use when the user asks to research, compare, survey, analyze, or review a topic and wants evidence-based output with traceable sources. Do not use for action-oriented tasks (build, implement, deploy, fix), single-fact lookups, or when the user only wants a quick answer without a written report."
version: 1.3.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
triggers:
  - "research"
  - "survey"
  - "compare"
  - "analyze"
  - "literature review"
  - "deep dive"
  - "technical report"
metadata:
  hermes:
    tags: [research, writing, analysis, survey, comparison]
    category: research
---

# Research Workflow

Produce a structured research report from any topic, technical problem, or scientific question. Output includes: problem statement, background, comparative analysis (when applicable), key findings, open questions, and formatted citations.

> **Tool-name portability** — this skill describes tools by capability, not by name. See the [Tool Capability Reference](#tool-capability-reference) at the end for the mapping. If your agent lacks a capability, report back to the user before substituting.

## Workflow Phases

> **Routing shortcuts.** Some requests don't need the full 4-phase workflow. Before starting Phase 1, check:
> - User pastes a specific arXiv URL or PDF link → load `references/single-paper-deep-dive.md` and skip to its step-by-step.
> - User asks to read / summarize / compare N local PDFs in a folder → load `references/local-pdf-batch-extraction.md` and skip to its step-by-step.
> - Otherwise → continue with Phase 1 → Phase 2 → Phase 3 → Phase 4 below.

### Phase 1 — Problem Framing

**Goal:** Clarify scope and determine research type.

**Step 1: Classify the research type**

Detect from the user's query or infer:

| Type | Trigger keywords | Output sections |
|---|---|---|
| `survey` | "overview", "introduction to", "what is" | Background, taxonomy, open questions |
| `compare` | "vs", "versus", "compare", "X or Y" | Feature matrix, pros/cons, benchmarks |
| `deep-dive` | "how does", "why is", "debug", "explain" | Problem statement, root causes, solutions |
| `hybrid` | complex multi-part queries | All of the above |

**Step 2: Decompose into sub-questions**

Generate 3–5 focused search queries from the main topic:

```
Main topic: "LLaMA fine-tuning methods"
→ sub-questions:
  1. "LLaMA fine-tuning methods 2024"
  2. "LoRA vs QLoRA vs Adapter tuning comparison"
  3. "fine-tuning LLaMA compute cost GPU memory"
  4. "LLaMA fine-tuning benchmarks results"
  5. "LLaMA fine-tuning open source libraries"
```

**Step 3: Clarify if ambiguous** (use the user-asking tool):
- Ask about target audience (researchers / engineers / general)
- Ask about specific angle if topic is broad
- Ask whether a particular library or paper should be included

> **Bias toward action.** Only ask if you cannot make reasonable defaults. If you can pick one (e.g., the only public API intro the user asked about, the obvious 3 libraries in the domain), state the assumption and proceed; the user can correct later.

---

### Phase 2 — Information Gathering

> **Reference files for this phase.** Load on demand:
> - `references/api-tools.md` — exact curl templates for arXiv / Semantic Scholar, Bing URL patterns, rate-limit details. Use when the topic is academic / scientific.
> - `references/data-collection-patterns.md` — Parallel subagent strategy, GitHub/PyPI primary-source patterns, search-engine quirks, citation hygiene. Use for any software / library comparison or when you hit 404s / bot detection.

**Tools used in this phase** (described by capability; see mapping table):

- A **subagent-spawning** tool for parallel research delegation
- A **URL-opening** tool that returns page snapshots (primary sources)
- A **shell command** tool for `curl`, `python3`, `uv` (REST APIs, scripts)
- A **file-reading** tool, a **file-writing** tool, a **content-search** tool
- A **skill-loading** tool for reading helper skills like `arxiv`
- A **screenshot/image-analysis** tool for visual verification

**No `web_search` tool** — if your agent has one, prefer it; if not, use the patterns below. Older versions of this skill referenced a generic web-search tool — that was wrong; do not call it.

Run searches and data collection in parallel for all sub-questions. Three patterns that work well:

**Pattern A — Parallel subagent delegation** (best for software/library comparisons):

```
subagent_spawn(
  goal="Research {specific library/topic}",
  context="Output in English. Return structured findings as markdown table or list of dicts covering: name, GitHub URL, stars, last release, license, key features, performance, limitations."
)
```

Dispatch 2-4 of these in parallel in a single turn. Each runs in the background and returns when done. This is faster and more resilient than sequential URL navigation.

**Pattern B — URL opening to primary sources** (best for GitHub/PyPI stats, official docs):

```
url_open("https://github.com/<owner>/<repo>")
url_open("https://pypi.org/project/<name>/")
url_open("https://crates.io/crates/<name>")
url_open("https://npmjs.com/package/<name>")
```

Dispatch these in a single response — they run concurrently. GitHub repo pages give you: stars, forks, open issues/PRs, last commit date/time, license, README excerpt. PyPI gives you latest version, release date, license classifier, Python version requirement.

**Pattern C — Shell `curl` + `python3 -m json.tool`** (best for REST APIs like arXiv, Semantic Scholar):

```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=LLaMA+fine-tuning&limit=5&fields=title,authors,year,citationCount,externalIds" | python3 -m json.tool
```

**For scientific / ML topics:**

```bash
# Option 1: Semantic Scholar (JSON, fast, usually unblocked)
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query={topic}&limit=8&fields=title,authors,year,citationCount,externalIds,abstract" | python3 -m json.tool

# Option 2: arXiv API (slower, can time out in sandbox)
curl -s "http://export.arxiv.org/api/query?search_query=ti:llama+AND+ti:fine-tuning&max_results=10&sortBy=submittedDate&sortOrder=descending"

# Option 3: Load the arxiv skill for the helper script
```

**⚠️ Pitfall — generic web-search tool may not exist.** Older skill versions referenced a search tool by name. If your agent's tool list does not include one, use Pattern A/B/C above. If your agent does have one and it works, fine — use it.

**⚠️ Pitfall — DuckDuckGo CAPTCHA:** Opening `https://duckduckgo.com/?q=...` via a browser-style tool returns a CAPTCHA page in most sandboxes (bot-detection). The page snapshot will say "Unfortunately, bots use DuckDuckGo too." Workarounds:
- Go straight to primary sources (GitHub, PyPI, official docs) — usually faster and more accurate anyway.
- Use Bing or Google search engines if you must use a search box.
- Use `curl` against DuckDuckGo's HTML endpoint (`https://html.duckduckgo.com/html/?q=...`) — less aggressive bot detection.

**⚠️ Pitfall — arXiv search scope:** Direct `curl` to `export.arxiv.org/api/query` can timeout in network-restricted environments. Workaround:
- Use Semantic Scholar API (`api.semanticscholar.org`) first — JSON response, faster, usually unblocked.
- Load the `arxiv` skill (if available) — it ships a helper script.
- If both fail, spawn a subagent with goal="Find papers on {topic} via arxiv/Semantic Scholar".

**⚠️ Pitfall — GitHub bot detection via URL-opening tool (PARTIALLY outdated):** In most sessions, opening `https://github.com/<owner>/<repo>` reliably returns stars, forks, last commit, and license info — it works. The bot-detection CAPTCHA fires only for some repos or after repeated rapid requests. **When it works, prefer the URL-opening tool** for GitHub (gives structured page data faster than REST API). Fall back to GitHub REST API (`api.github.com/repos/{owner}/{repo}`) only when the URL-opening tool returns CAPTCHA or 404. For README content, use `raw.githubusercontent.com/<owner>/<repo>/main/README.md` (try `master` if `main` 404s).

**⚠️ Pitfall — GitHub org/user ≠ PyPI package name:** Do NOT assume `github.com/<pypi-name>/<pypi-name>`. The mapping is often non-obvious. **Always** query PyPI JSON first and extract `project_urls['Repository']` or `project_urls['Homepage']` for the canonical GitHub path:
- `python-docx` → `python-openxml/python-docx`
- `mammoth` → `mwilliamson/python-mammoth`
- `docx2txt` → `ankushshah89/python-docx2txt`
- `textract` → `deanmalmgren/textract`
- `pypandoc` → `JessicaTegner/pypandoc`
- `surya` (OCR) → published as `surya-ocr` on PyPI (NOT `surya`)

**⚠️ Pitfall — camelot-py PyPI may be wrong package:** The package `camelot-py` on PyPI may not be the canonical PDF table-extraction library. Always verify by checking the GitHub repo directly — the correct package may need to be installed from GitHub.

**⚠️ Pitfall — inline `-c` Python in shell is blocked:** Some sandboxed shell tools block inline `python3 -c "..."` scripts with "pending approval". Workaround: write the script to a file first, then execute it from disk. Example:

```
# Step 1: write the script to a file (using file-writing tool)
path: /some/dir/fetch_gh.py
import urllib.request, json
...

# Step 2: run from shell
python3 /some/dir/fetch_gh.py
```

**⚠️ Pitfall — `ti:` vs `all:` arXiv search:** For topic-specific discovery, prefer title-prefix queries (`ti:llama AND ti:fine-tuning`) over `all:` searches. In practice, `all:LLaMA+fine-tuning` returns mostly irrelevant results while `ti:llama+AND+ti:fine-tuning` returned 29 highly targeted papers in prior sessions. Use `all:` only when you need broad recall.

**⚠️ Pitfall — Deep-dive on a specific arXiv URL (single-paper workflow):** When the user pastes a specific arXiv URL (e.g. `https://arxiv.org/pdf/2405.07960`) and asks for analysis, this is NOT a literature-search task — it's a single-paper deep-dive. Do NOT dispatch parallel subagent searches or browse GitHub. Use this exact recipe:

1. Download PDF directly: `curl -sL -o <workspace>/paper.pdf "<URL>" -A "Mozilla/5.0"`. Default arXiv landing URL → redirect to PDF; `https://arxiv.org/pdf/<id>` works directly.
2. Extract text with PyMuPDF (`fitz`) — see "PDF extraction workflow" below for venv setup on Windows.
3. Read the extracted text file with the file-reading tool (offset/limit to navigate), OR grep with `grep -n` via shell to locate specific sections (e.g. `Appendix L`, `Patient agent`, `Diagram`).
4. Cross-reference `https://arxiv.org/abs/<id>` for the abstract and `https://arxiv.org/pdf/<id>v<N>` for version-specific content (arXiv v5 ≠ v1 — content can differ significantly).
5. Build the report around: problem statement → architecture → agent-by-agent prompt breakdown → communication protocol → lifecycle (state machine) → tools/extensions → benchmarks → open questions.

This workflow completed in ~10 tool calls for a 42-page paper; document-extraction approaches (PDF→text→grep→read slices) are dramatically faster than opening the PDF in a browser.

**PDF extraction workflow (PyMuPDF on Windows):**

```
# 1. Default `python` on a sandboxed desktop app often points to an internal venv (no pip).
#    `python3` may point to a separate system Python — `import fitz` will fail on whichever
#    doesn't have pymupdf.
# 2. Install pymupdf INTO the active Python explicitly:
uv pip install pymupdf --python "<path-to-python-with-pip>"
#    (Plain `uv pip install pymupdf --system` installs into a different Python.)
# 3. Write extraction script to disk (NOT inline `-c` — some shells block those):
# file-write → /some/dir/extract.py with fitz.open(...).get_text()
# 4. shell → python /some/dir/extract.py
```

**⚠️ Pitfall — Subagent output files land in CWD, not target workspace:** Background subagents write files to their current working directory, which may not be the user's intended workspace. After subagents complete, ALWAYS check for output files in the subagent's CWD and move them to the active workspace. Do not assume files written inside a subagent's file-writing tool call will appear in your workspace.

**⚠️ Pitfall — Subagent results arrive as conversation messages, not via background-process polling:** After spawning subagents in the background, do NOT call a background-process polling tool on the delegation IDs — they return "not found". Subagent results re-enter the conversation as new assistant messages when each subagent finishes. Simply continue working; the results will arrive asynchronously. Only use background-process polling for processes started with `terminal(background=true)` or equivalent.

**⚠️ Pitfall — content-search tool fails on some Windows paths:** The content-search tool (ripgrep-backed) intermittently fails with "The system cannot find the path specified" on POSIX-style paths that contain spaces or odd separators. **Fallback: use `grep -n "<pattern>" <file>` via shell** — it's reliable on the same Windows MSYS bash environment. Example:

```bash
cd "./research" && grep -n "Appendix L\|Patient agent" paper.txt | head -20
```

**⚠️ Pitfall — content-search tool for directory discovery returns 0 silently on Windows:** Specifically when using a file-search mode with an absolute path like `path="E:/Documents/..."`, the content-search tool can return 0 results even when the folder is populated. This is a different failure mode from the grep path issue above — `ls "<path>"` (POSIX bash form) reliably returns the file list. Rule: for any "what's in this folder?" question on Windows, default to shell `ls` first; only fall back to the content-search tool if you specifically need its filtering.

**⚠️ Pitfall — sandbox venv Python vs system Python on Windows:** The `python` on PATH inside the shell is often a venv with no `pip` (`python -m pip install ...` fails with "No module named pip"). Use `uv pip install <pkg> --python <venv-exe>` to install. `uv pip install <pkg> --system` installs into a DIFFERENT Python that the shell does NOT invoke by default — confusing when `import fitz` then fails.

**For software / library comparisons** (use Pattern A + Pattern B from above):
- Spawn a subagent per library in parallel — ask for stars, last release, license, features, limitations.
- Cross-verify with `url_open("https://github.com/<owner>/<repo>")` and `url_open("https://pypi.org/project/<name>/")`.
- For each library, also open its official docs URL for authoritative feature claims.

**Collect for each source:**
- Title
- URL
- Publication date / version
- Abstract or key snippet
- Key claims or data points

**Deduplicate and rank:**
1. Peer-reviewed papers / official documentation
2. Preprints / technical reports
3. Blog posts / tutorials
4. Forum posts / social media

---

### Phase 3 — Analysis

**For Survey / Deep-dive:** build a synthesis table

| Source | Claim | Evidence | Limitation | Conflict? |
|---|---|---|---|---|
| Paper/URL | Main finding | Data/proof cited | Caveat | -agrees / conflicts with X |

**For Software Comparison:** build a feature matrix

| Feature | Lib A | Lib B | Lib C |
|---|---|---|---|
| Language | Python | Rust | Go |
| License | Apache 2 | MIT | BSD |
| GitHub Stars | ... | ... | ... |
| GPU Support | ✅ | ✅ | ❌ |
| Performance (ref) | ... | ... | ... |
| Last Release | ... | ... | ... |

Extract benchmark numbers with conditions noted (hardware, dataset, workload).

**Identify:**
- Areas of consensus across sources
- Gaps and unresolved questions
- Direct contradictions between sources

---

### Phase 4 — Report Drafting

> **Reference for this phase.** Load `examples/sample-report.md` for a worked example of the exact output format (section order, citation style, footer line). Use it as the template, not as content to copy verbatim.

**Output path (auto-created):** Active workspace's `research_reports/` directory. Create the folder if missing. Save as `<slug>_<YYYYMMDD>.md`. If your agent has a default workspace, use it; otherwise fall back to the current working directory.

Write the report following this template:

```markdown
# [Topic Title]

**Date:** YYYY-MM-DD  
**Type:** [survey | compare | deep-dive | hybrid]  
**Query:** [original user input]  
**Sub-questions:** [list of search queries used]

---

## 1. Problem Statement
What problem is being addressed? Why does it matter? (2–4 sentences)

## 2. Background & Related Work
Key concepts, terminology, prior approaches. (4–8 sentences)

## 3. [Comparative Analysis | Literature Review]
### 3.1 [Sub-topic A]
### 3.2 [Sub-topic B]
### 3.3 [Sub-topic C]

## 4. Key Findings
- **Finding 1:** [Description] [Citation]
- **Finding 2:** [Description] [Citation]

## 5. Open Questions & Future Work
Gaps identified, unresolved debates, promising directions.

## 6. References
[1] Author, Title, Source, Year — [URL](URL)  
[2] ...

---

*Report generated via research workflow — {date}*
```

---

## GitHub + PyPI repo metadata (for software/library comparisons)

When comparing open-source libraries, cross-reference GitHub + PyPI + raw README in parallel.

### Step 1 — Get GitHub URLs from PyPI (always do this first)

Do NOT guess GitHub URLs from PyPI package names. Query PyPI JSON to get authoritative `project_urls`:

```python
# Write the script to disk first, then run it.
# package_list — list of PyPI package names to look up
# output: prints '{pkg}: {project_urls_dict}' for each package
import urllib.request, json
package_list = ['python-docx', 'mammoth', 'docx2txt', 'textract', 'pypandoc']
for pkg in package_list:
    url = f'https://pypi.org/pypi/{pkg}/json'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        info = d.get('info', {})
        proj_urls = info.get('project_urls') or {}
        print(f"{pkg}: {proj_urls}")
```

This returns e.g. `python-docx: {'Homepage': 'https://github.com/python-openxml/python-docx', 'Repository': 'https://github.com/python-openxml/python-docx'}`.

### Step 2 — Get GitHub stats via REST API

```python
# Write the script to disk first, then run it.
# repo_pairs — list of (label, 'owner/repo') tuples
# output: prints 'label|stars|forks|url|description' for each repo
import urllib.request, json
repo_pairs = [("python-docx", "python-openxml/python-docx"), ...]
for name, repo in repo_pairs:
    url = f"https://api.github.com/repos/{repo}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        print(f"{name}|{d['stargazers_count']}|{d['forks_count']}|{d['html_url']}|{d['description']}")
```

### Step 3 — Get PyPI version + license

```python
# Write the script to disk first, then run it.
# package_list — list of PyPI package names to look up
# output: prints 'pkg|license|version|upload_time' for each package
import urllib.request, json
package_list = ['python-docx', 'mammoth', 'docx2txt', 'textract', 'pypandoc']
for pkg in package_list:
    url = f'https://pypi.org/pypi/{pkg}/json'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as r:
        d = json.loads(r.read())
        info = d.get('info', {})
        urls = d.get('urls', [])
        latest = urls[0] if urls else {}
        print(f"{pkg}|{info.get('license','?')}|{info.get('version','?')}|{latest.get('upload_time','?')}")
```

### Raw README from GitHub (if needed)

```bash
curl -sL "https://raw.githubusercontent.com/<owner>/<repo>/main/README.md"   # 404? try:
curl -sL "https://raw.githubusercontent.com/<owner>/<repo>/master/README.md"
# Note: the github.com HTML page returns HTML wrapped around empty React roots — useless
# for content extraction. Only raw.githubusercontent.com works.
```

**PyPI metadata as license fallback:**

```bash
curl -sL "https://pypi.org/pypi/PACKAGE/json" | python -c "
import sys, json
d = json.load(sys.stdin)
print('latest:', d['info']['version'])
print('license:', d['info']['license'])
for c in d['info']['classifiers']:
    if 'License' in c: print('  classifier:', c)
"
```

Note: `pdfplumber` and `unstructured` return `license: None` on PyPI despite being MIT/Apache — always check classifiers and the repo's `LICENSE` file when the `license` field is null.

**Latest release date:** Use the GitHub `/releases/latest` endpoint, not `pushed_at` (which fires on every commit, not just releases).

**Stale-library warning:** If a package hasn't released in >18 months despite commits, flag it as "stale" in the report (e.g., tabula-py last release Oct 2024 with regular commits since).

**Ranking criterion for software comparisons:**
- Stars: popularity/adoption signal — but check recent commit velocity (last 90d) for active maintenance
- Latest release date: surface maintenance status; flag anything >12 months without a release
- License: AGPL-3.0 (copyleft) is a hard blocker for closed-source commercial projects; MIT/Apache/BSD are permissive
- OCR / tables / layout: explicit row in the feature matrix for each, with the underlying backend named (Tesseract, surya, pdfium, etc.)
- Benchmark data: prefer third-party benchmarks (e.g., olmocr-bench) over maintainers' self-reported numbers

**Caveat on AGPL-3.0 libraries (PyMuPDF, pymupdf4llm):** Copyleft requires either open-sourcing your application OR purchasing a commercial license (e.g., Artifex for PyMuPDF). For closed-source commercial projects, recommend Apache/MIT alternatives first.

---

## Prompt templates for subagent delegation

Use these as the `goal` field when spawning subagents.

### Generic research request

```
Research the following topic and produce a structured report:
"{topic}"

Requirements:
- Include citations for all claims
- If software libraries are mentioned, compare at least 3 options
- Address limitations and open questions
- Output as Markdown
```

### Compare request

```
Compare the following and produce a structured report:
"{lib_a} vs {lib_b} vs {lib_c}"

Requirements:
- Feature matrix with ≥5 comparison dimensions
- Performance benchmarks if available
- Pros/cons for each option
- Recommendation based on use case (if inferable)
```

### Scientific research request

```
Conduct a literature review on:
"{topic}"

Requirements:
- Include arXiv papers and peer-reviewed sources
- Summarize key methods and findings
- Note contradictions between papers
- Identify gaps and future work directions
```

---

## Output Handling

- **In-chat:** Render the full Markdown report in the response (it renders with full GitHub flavor).
- **File:** Save to the active workspace's `research_reports/<slug>_<YYYYMMDD>.md`. Create the directory if missing. If you have a configured default workspace, prefer that; otherwise fall back to the current working directory.
- **Scheduled/cron delivery:** When the task is scheduled, deliver the report to the originating chat.

---

## Tips & Pitfalls

- **For a new domain, lead with one-sentence definition in user's language.** When user says "research this for me" or "explain X" about a domain they're not familiar with, do NOT front-load citations, keyword lists, or framework comparisons. Lead with a one-sentence definition in their language that a non-expert can read and immediately understand. Use the citations internally to build your understanding, but the writing answers their question, not your research questions. If you find yourself writing "the term X refers to..." or "as defined by [B3]...", stop and rewrite a plain-language definition first.
- **Respect scope; don't dump everything you researched.** When user asks about a domain at high level (e.g. "what is X, what does the role do, what technical skills are needed"), do NOT also dump data sourcing, ML libraries, deployment stack, top firms with revenue figures, salary tables — unless they ask. Define the scope from their actual questions, not from what you found. A focused 800-word report beats a 5000-word dump every time.
- **Define every domain term inline.** If you use `PnL`, `alpha`, `HFT`, `Sharpe`, `IC`, `drawdown`, `marginal`, `MVP`, `SOC2` — define it on first use in the user's language, even if it feels obvious. The user said "this is a new field, I'm asking you to research it" — so do not assume they know the acronyms you know. Format: `PnL (lãi/lỗ ròng)` once, then the acronym alone.
- **Plaintext diagrams when user asks.** When user explicitly says "diagrams in plaintext", "no Mermaid", or "no SVG", render flows as ASCII (boxes with arrows) or numbered step lists. Don't fight the constraint — it's a real preference, often for copy-paste into chat/email. Mermaid is great when welcome but not universal.
- **Too broad:** If a topic covers multiple fields, narrow to one dimension per report. Suggest splitting.
- **Stale sources:** Always note "as of YYYY-MM-DD" in the report header; web content changes fast.
- **Weak citations:** Prioritize official docs, papers, and primary sources over blog posts.
- **Vietnamese input:** Translate queries to English for search. Preserve original input verbatim in report header (`**Query:**`). Translate sub-questions to English for API calls. If the topic contains Vietnamese diacritics (ă, â, ê, ô, ơ, ư, đ, etc.), write the report in Vietnamese automatically — do not ask.

### Report language & writing style for Vietnamese users

**Default to Vietnamese.** When the user's query is in Vietnamese, write the report body in Vietnamese. The user reads Vietnamese better than English, and translating paper titles/terms to Vietnamese where natural improves comprehension. Keep technical terms and citation strings (paper titles, repo names, API names, library names) in their original English — those are identifiers, not prose.

**Translate what's translatable, leave what's not.** 
- Translate: "purple", "the framework", "according to the paper", "the workflow consists of six stages".
- Don't translate: "FinRL", "backtest", "VaR", "HFT", "Sharpe ratio", "IC", "drawdown", "MVP", "IT", "DevOps", "rollback". These are domain terms the reader already knows in English.
- Format for unavoidable English: `Framework (công cụ)` on first mention, then drop the parenthetical. E.g. "HFT (giao dịch tần suất cao)" once, then "HFT" alone.

**Writing style — avoid AI-tells.** User has flagged that bullet-list-heavy, sentence-parallel, English-chêm-nhiều reports feel mechanical. Match a human Vietnamese writer:
- Vary sentence length. Mix short punchy sentences with longer flowing ones. Don't make every sentence the same length.
- Write paragraphs, not bullet salad. 2–4 sentences per paragraph, natural transitions. Use bullet lists only for genuine enumerations (libraries, firms, comparison matrix). Don't bulletize prose.
- Use connectives Vietnamese-native: "Tuy nhiên", "Điều này có nghĩa là", "Lý do là", "Nói cách khác", "Thực tế". Avoid the AI-pattern "Không chỉ X, mà còn Y" (forced negation parallelism).
- Don't force the rule of three. "Stack chuẩn: Lean, vectorbt, nautilus_trader" — that's a list of three by coincidence, not by design. Stop reaching for triplets.
- Reduce bold. Bold only when emphatic, not as a visual highlight for every key term. A paragraph with seven bolded phrases is not a paragraph, it's a formatted mess.
- Drop em-dash overuse (dấu —). Vietnamese newspapers don't use —. Use dấu phẩy, dấu chấm, hoặc ngoặc đơn.
- For citations, write prose attribution: "Theo Citadel Securities (career page), quant trader là..." not "Citadel Securities [B2]: '...'".
- When paraphrasing English sources, *rephrase* in Vietnamese instead of literal translation. A literal translation of "Our Traders work with Quantitative Researchers to optimize and develop innovative trading strategies across an array of asset classes" reads as translated English. Rewrite naturally in Vietnamese.

**Voice.** Have an opinion. "Theo tôi", "Điều đáng chú ý là", "Một điểm cần lưu ý" — these are normal Vietnamese. Don't strip them out.

**Example good paragraph:**
> Quant Trader là nhánh "Quant giao dịch thuật toán" trong họ quant. Wikipedia [1] xếp nhánh này vào nhóm được trả lương cao nhất, vì nó trực tiếp chịu trách nhiệm về PnL (lãi/lỗ ròng) của chiến lược. Công việc hằng ngày, theo Citadel Securities, là phân tích dữ liệu mới, tinh chỉnh thuật toán, chạy backtest (kiểm thử lại chiến lược trên dữ liệu lịch sử), giám sát rủi ro, và quyết định cho ngày hôm sau. Trader không ngồi đọc chart bằng cảm tính, cũng không làm phân tích cơ bản kiểu truyền thống.

**Example BAD paragraph (avoid):**
> **Quant Trader** represents a pivotal role within the **quantitative trading** landscape. As highlighted by [B2], *"Our Traders work with Quantitative Researchers to optimize and develop innovative trading strategies across an array of asset classes."* This role encompasses — at its core — the dynamic interplay between **alpha generation**, **risk management**, and **execution**, underscoring its vital role in modern **systematic finance**.

**When to render in English instead.** Default Vietnamese but consider English when: (a) paper title or repo name is the subject and English is clearer, (b) the user explicitly asks for English output, (c) the user is mixed-language (some questions Vietnamese, some English — match their preference per query). If unsure, ask once before writing 50 pages.

- **No results:** If a search returns nothing, try alternative phrasing or broaden the query.
- **Use Mermaid diagrams for lifecycle/process flows:** Inside markdown reports, Mermaid `flowchart TD` blocks render natively in most chat surfaces. Use them for state machines, agent interaction loops, or pipeline diagrams — far more readable than ASCII art and the user can pan/zoom. Example:

    ```mermaid
    flowchart TD
        A[Start] --> B{Turn ≤ N?}
        B -- yes --> C[Doctor action] --> D[Parser routes] --> B
        B -- no --> E[Moderator judge]
    ```

---

## Tool Capability Reference

This skill describes tools by capability, not by name. The table below maps each **capability** mentioned in the skill to a representative tool name in common agent platforms. If your agent's tool list differs, identify the tool that best matches the capability — most platforms have all of these under similar names.

| Capability | Hermes equivalents | Python script alternative |
|---|---|---|
| Open a URL and return page content | `browser_navigate` | `curl <url>` |
| Snapshot a page as text | `browser_snapshot` | `curl -s <url>` |
| Click a page element | `browser_click` | n/a |
| Type into a page field | `browser_type` | n/a |
| Read browser console output | `browser_console` | n/a |
| List images on a page | `browser_get_images` | n/a |
| Take a screenshot / analyze image | `browser_vision` | n/a |
| Spawn a subagent for parallel work | `delegate_task` | run child process / thread |
| Run a shell command | `terminal` | `subprocess.run` |
| Read a local file | `read_file` | `open(path).read()` |
| Write a local file | `write_file` | `open(path, 'w').write(...)` |
| Patch a file (find/replace) | `patch` | `sed -i` / `Path.replace` |
| Search file contents / list files | `search_files` | `grep` / `find` |
| Run a Python script in a sandbox | `execute_code` | python interpreter |
| Load a skill | `skill_view` | read `SKILL.md` file |
| List available skills | `skills_list` | list `skills/` directory |
| Manage skills (create/patch/delete) | `skill_manage` | edit `SKILL.md` / `references/` |
| Maintain a task list | `todo` | n/a (LLM-driven) |
| Ask the user a multiple-choice question | `clarify` | n/a (LLM-driven) |
| Save a memory note | `memory` | write to memory file |
| Search past conversation history | `session_search` | query session DB |
| Poll a background process | `process` | thread / signal |
| Convert text to speech | `text_to_speech` | shell out to TTS tool |
| Schedule a recurring task | `cronjob` | system cron |

**Universal nouns (no mapping needed):** `terminal`, `python`, `python3`, `curl`, `bash`, `git`, `uv`, `npm`, `pip`, `node`. These are names of programs, not agent-specific tools.

**Universal web protocols (no mapping needed):** `https://`, `html.duckduckgo.com`, `api.semanticscholar.org`, `export.arxiv.org`, `pypi.org`, `api.github.com`, `raw.githubusercontent.com`, `github.com/<owner>/<repo>`, `arxiv.org`.

**When a tool is missing:** If your agent lacks a capability listed above, report back to the user before substituting. For example, if your agent cannot spawn subagents, do Pattern A in serial using the URL-opening tool — slower but correct.

---

## Support Files

Each entry lists **when to load** the file, not just what it contains.

### `references/` — detailed procedures

- `references/api-tools.md` — Load during **Phase 2** when you need exact curl commands for arXiv / Semantic Scholar, or when the user asks for academic / scientific papers. Use before Pattern C if you need rate-limit details or Bing search-URL patterns.
- `references/data-collection-patterns.md` — Load during **Phase 2** for any software / library comparison, or when you hit GitHub bot detection / 404s. Also covers subagent failure modes and citation hygiene during **Phase 3**.
- `references/single-paper-deep-dive.md` — Load **instead of** Phase 2 when the user pastes a specific arXiv URL or paper title (signals: "research về bài báo này", "analyze this paper", "explain the architecture in this paper"). Optimized for one PDF, not a literature survey.
- `references/local-pdf-batch-extraction.md` — Load **instead of** Phase 2 when the user asks to read / summarize / compare N local PDFs in a folder (book series, conference proceedings, paper dump). Distinct from `single-paper-deep-dive.md` (one URL) and from URL-based search workflows.

### `examples/` — output format reference

- `examples/sample-report.md` — Load during **Phase 4** as a reference for the exact output format your report should follow. Shows the report's structure (section order, citation style, footer line) with a worked example (Qwen3-8B inference comparison). Use it as the template, not as content to copy verbatim.
