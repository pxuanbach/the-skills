# Single-paper Deep-Dive Workflow

Use when the user provides a specific arXiv URL (or any PDF URL) and asks for analysis of THAT paper — not a literature survey.

## When to use

Trigger signals:
- User pastes `https://arxiv.org/abs/<id>` or `https://arxiv.org/pdf/<id>` directly
- Phrases like "research về bài báo này", "analyze this paper", "explain the architecture in this paper", "tóm tắt paper này"
- Specific paper title given

DO NOT use this workflow for: "find papers on X", "literature review of Y" — those are surveys and use Pattern A/B/C from SKILL.md.

## Step-by-step

### 1. Download PDF

```bash
mkdir -p "<workspace_dir>"
curl -sL -o "<workspace_dir>/paper.pdf" "https://arxiv.org/pdf/<id>" -A "Mozilla/5.0"
# Verify size > 100KB to confirm it downloaded text, not an error page
ls -la "<workspace_dir>/paper.pdf"
```

arXiv landing URLs (`/abs/<id>`) redirect to `/pdf/<id>` automatically. Use the PDF URL directly to skip the redirect.

### 2. Extract text with PyMuPDF

In many agentic environments, the default `python` points to a venv without `pip`. Install PyMuPDF into the agent's venv explicitly:

```bash
# Windows — replace with your agent's actual venv path
uv pip install pymupdf --python "C:/Users/<user>/AppData/Local/<agent>/<agent>/venv/Scripts/python.exe"

# Linux/macOS
uv pip install pymupdf --python "$HOME/.local/share/<agent>/venv/bin/python"
```

Write extraction script to disk (NOT inline `-c` — terminal blocks those):

```python
# write_file → C:/Users/<user>/extract_paper.py
import fitz, sys

pdf_path = sys.argv[1]
out_path = sys.argv[2]
doc = fitz.open(pdf_path)
print(f"Pages: {len(doc)}", file=sys.stderr)
text = "".join(f"\n\n===== PAGE {i+1} =====\n\n" + p.get_text() for i, p in enumerate(doc))
with open(out_path, "w", encoding="utf-8") as f:
    f.write(text)
print(f"Extracted {len(text)} chars to {out_path}", file=sys.stderr)
```

```bash
python C:/Users/<user>/extract_paper.py "<workspace>/paper.pdf" "<workspace>/paper.txt"
```

### 3. Locate sections (use grep, not search_files)

`search_files` (ripgrep) fails on some Windows paths with spaces. Use terminal grep instead:

```bash
cd "<workspace>" && grep -n "Appendix L\|Patient agent\|Diagnosis Ready\|Request Test" paper.txt | head -30
```

Useful section markers for typical ML papers:
- Abstract / 1. Introduction (first 2 pages)
- Architecture / Method (look for "Architecture", "Model", "Agent", "Pipeline")
- Experimental setup (look for "Experimental", "Setup", "Implementation")
- Tables and benchmarks (look for "Table", "Figure")
- Limitations / Conclusion (search "limitation", "future work", "conclusion")
- Appendix (look for "Appendix", "A.", "B.", "C.")

### 4. Read specific slices with read_file

For long extracted files (>2000 lines), use `read_file` with `offset` and `limit`:

```
read_file(path="C:/.../paper.txt", offset=740, limit=200)  # Appendix A.1 Agents
```

Combine with grep results to jump to the right slice — much faster than reading top-to-bottom.

### 5. Cross-reference version

arXiv papers have versions (v1, v2, ...). The PDF URL defaults to the latest. To cite a specific version:
- `https://arxiv.org/pdf/<id>v<N>` for explicit version
- `https://arxiv.org/abs/<id>` shows current version + history

### 6. Report structure for single-paper deep-dive

Recommended sections (in order):

1. **Problem Statement** — what problem the paper addresses, why it matters (from abstract + intro)
2. **Background & Related Work** — terminology, prior approaches cited (from intro + related-work section)
3. **Architecture / Method** — the proposed system, components, data flow (from method section + diagrams)
4. **Agent / Component breakdown** — for each agent/component: role, prompt, inputs, outputs, capabilities
5. **Communication Protocol** — how components interact (message format, actions, parser logic)
6. **Lifecycle / State Machine** — what happens from input to output (use a Mermaid flowchart)
7. **Tools / Extensions** — optional add-ons, ablation results
8. **Key Findings** — concrete claims with quoted evidence + page numbers
9. **Open Questions & Future Work** — explicit limitations the authors admit + gaps
10. **References** — primarily [1] the paper itself, plus any closely-cited prior work you actually read

Citation style: `[1, §X]` / `[1, Appendix X]` / `[1, p. N]` referencing the original paper so the reader can verify quickly.

### 7. Common paper types and what to focus on

| Paper type | Focus report on |
|---|---|
| Benchmark / survey | Comparison methodology, datasets, baseline selection |
| Architecture / model | The architecture diagram + component breakdown + compute cost |
| Agent / multi-agent | Lifecycle, communication protocol, agent prompts (verbatim), tool use |
| Empirical study | Effect sizes, statistical tests, robustness, generalizability |
| Theoretical | Assumptions, proofs (sketch), bounds |

## Pitfalls

- **Don't dispatch `delegate_task` for paper extraction** — downloading + local PyMuPDF is faster and gives you exact text control. Subagents can't see your PDF.
- **Don't `browser_navigate` to the PDF URL** — the browser snapshot truncates long PDFs and can't be grep'd. Extract to text first.
- **arXiv versions matter** — if a paper has v1 from 2023 and v5 from 2025 with major changes, cite the version you read. The PDF at `/pdf/<id>` is always the latest.
- **Tables and figures** — PyMuPDF extracts table text linearly (rows concatenated). For structured tables, look at `page.get_text("dict")` blocks or use `pdfplumber.extract_tables()`. For figures, use `browser_navigate` to arxiv.org/html/<id> if available (HTML version preserves figures).
- **References** — the bibliography is usually at the end. Use grep `"References"` or `"Bibliography"` to find the start line.