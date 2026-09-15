# Fetching Paper Sources

The 4-pass reading strategy assumes you have paper text. This reference covers how to get that text from the four most common inputs.

> **Load this file in Step 0** when you need to fetch the paper (arXiv URL, local PDF, paper title only, screenshot).

[Docling](https://docling-project.github.io/docling/) is the primary extraction tool. It handles PDFs (including scanned ones via built-in OCR), preserves layout, and outputs clean Markdown — better than PyMuPDF for downstream PACES analysis. Install once; reuse everywhere.

---

## Source 1 — arXiv URL

The most common input. arXiv URLs come in two forms:

- **Landing page:** `https://arxiv.org/abs/2405.07960` — HTML, contains abstract and metadata.
- **Direct PDF:** `https://arxiv.org/pdf/2405.07960` — redirects to the actual PDF; works with `curl`.

### Fetch the PDF

```bash
# Direct PDF download
curl -sL -o <workdir>/paper.pdf "https://arxiv.org/pdf/2405.07960" \
  -A "Mozilla/5.0"
```

arXiv returns `v1` by default. Append `v<N>` (e.g. `.../pdf/2405.07960v3`) to fetch later revisions.

### Extract with docling

**Python API** (preferred for downstream processing):

```python
# path: <workdir>/extract.py
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("<workdir>/paper.pdf")  # accepts URL or file path

with open("<workdir>/paper.md", "w") as f:
    f.write(result.document.export_to_markdown())
```

Run:
```bash
python3 <workdir>/extract.py
```

**CLI** (faster for one-off conversions, writes `paper.md` next to input):

```bash
docling <workdir>/paper.pdf
```

### Install docling

```bash
# Most universal
pip install docling

# or with uv
uv add docling

# For Intel macOS specifically
pip install "docling[mac_intel]"
```

To find the Python interpreter you should target, run `which python3` and pass it explicitly if pip is sandboxed:

```bash
uv pip install docling --python "$(which python3)"
```

Reference: [docling installation docs](https://docling-project.github.io/docling/getting_started/installation/) and [quickstart](https://docling-project.github.io/docling/getting_started/quickstart/).

### Read the extracted Markdown

Docling outputs structured Markdown — section headers, tables, figures, references. Use `grep -n` to locate sections, then read in slices:

```bash
# Quick orientation
grep -n "^# \|^Introduction\|^Conclusion\|^References\|^Abstract" <workdir>/paper.md | head -30
```

---

## Source 2 — Local PDF

User provides a path like `~/papers/transformer.pdf` or `./downloads/paper.pdf`.

Use the same docling recipe as Source 1 — `DocumentConverter().convert()` accepts both file paths and URLs:

```python
from docling.document_converter import DocumentConverter
converter = DocumentConverter()
result = converter.convert("~/papers/transformer.pdf")
print(result.document.export_to_markdown())
```

Or CLI:
```bash
docling ~/papers/transformer.pdf
```

Docling handles encrypted/scanned PDFs via built-in OCR — no separate `ocrmypdf` step needed.

---

## Source 3 — Paper title only

User says: *"Read the AlphaFold paper"* or *"Get me the original BERT paper"* — no URL, no file.

### Workflow

1. **Web search** for the paper title — prefer official sources:
   - `site:arxiv.org "<exact title>"` (Bing / Google)
   - Semantic Scholar: `https://api.semanticscholar.org/graph/v1/paper/search?query=<urlencoded title>&limit=3&fields=title,authors,year,externalIds,abstract`
2. **Confirm** the canonical arXiv ID from the search result.
3. **Proceed** as Source 1 (arXiv URL).

### Semantic Scholar lookup (preferred — JSON, no CAPTCHA)

```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=Attention+is+All+you+Need&limit=3&fields=title,authors,year,externalIds,abstract" \
  | python3 -m json.tool
```

Look for `externalIds.arxiv` field. If present, you have the arXiv ID — go to Source 1.

---

## Source 4 — Screenshot / photo of paper page

User pastes an image of a paper page (camera photo, screenshot of a PDF viewer, OCR'd screenshot).

### Workflow

1. **OCR** the image. If your agent has an image-analysis / vision tool, use it directly. Otherwise:
   ```bash
   # tesseract
   tesseract <image-path> <output>/page -l eng
   ```
2. **Continue** with Source 1 / 2 / 3 depending on whether the OCR surfaced enough text to identify the paper.
3. If the image contains figures, note them in the analysis but don't try to OCR figures themselves.

---

## Pitfalls across all sources

### Pitfall — `curl` returns HTML instead of PDF

Some networks / proxies intercept `arxiv.org/pdf/*` and return an HTML error page. Detect by file type:

```bash
file <workdir>/paper.pdf
# If "HTML document", the fetch failed. Retry with -L (follow redirects) and a browser User-Agent.
```

### Pitfall — docling install fails in sandbox

Use `uv pip install docling --python "$(which python3)"`. Avoid `--system`, which may target the wrong interpreter. If docling's PyTorch dependency is too large, the macOS Intel extra (`docling[mac_intel]`) uses a pinned PyTorch 2.2.2.

### Pitfall — Inline `python3 -c` blocked

Some sandboxed environments block inline code strings. Write to `<workdir>/extract.py` and run from disk.

### Pitfall — First docling run is slow

Docling downloads ML models on first use (segmentation, table-structure, OCR models). Subsequent runs are fast. Budget extra time on the first conversion.

### Pitfall — Very large papers (100+ pages)

Do not load the entire Markdown into context. Locate section headers with `grep -n` and read in bounded slices.

### Pitfall — arXiv version mismatch

Paper versions can differ in results, ablations, or authorship. Fetch `vN` for the latest revision; use `v1` if targeting the original release.

---

## Quick routing table

| Input | First action | Tool |
|---|---|---|
| arXiv URL | `curl` the PDF → docling extract | `Bash` + docling |
| Local PDF path | docling extract | docling (`DocumentConverter` or CLI) |
| Paper title | Semantic Scholar API → arXiv ID → fetch + extract | `curl` + docling |
| Screenshot of page | OCR → extract text | Vision tool or `tesseract` |
| Pre-extracted text | Skip fetch, proceed to Pass 1 | `Read` |
| DOI only | Resolve via `https://doi.org/<doi>` → find PDF | `WebFetch` + docling |

---

## Output hygiene

Whichever source you use:

- Save the **raw PDF** to `<output_dir>/<slug>_raw.pdf` (or skip if user-provided).
- Save the **extracted Markdown** to `<output_dir>/<slug>_raw.md`.
- The **PACES analysis** goes in `<output_dir>/<slug>_<YYYYMMDD>.md`.

This separation means you can re-run the PACES analysis later if you improve the template, without re-fetching the paper.
