# Batch Local PDF Extraction & Synthesis

Use this when the user asks to read, summarize, compare, or review **N local PDFs in a folder** (a book series, vendor paper dump, conference proceedings, research library). Distinct from single-paper deep-dive (`references/single-paper-deep-dive.md`) and from URL-based paper work.

> **Tool names in this file** (e.g. `terminal`, `read_file`, `write_file`, `search_files`) are placeholder names for the corresponding capability. See the Tool Capability Reference in SKILL.md for the mapping. If your agent lacks a capability, report back to the user before substituting.

## Why this needs its own workflow

- Single-paper workflow reads one PDF end-to-end into context. With N PDFs of 30-60 pages each, that blows the context window and degrades fidelity on later files.
- URL-based workflow assumes one URL per paper. Local folder has no URL list to crawl.
- The right shape is **bulk extract → selective read → cross-file synthesis**.

## Step 1 — Enumerate the folder (Windows quirk)

The content-search tool (ripgrep-backed) sometimes silently returns 0 results for absolute Windows paths even when the folder is populated. Do NOT conclude the folder is empty.

Reliable fallbacks, in order:

```bash
# POSIX-style under git-bash / MSYS — works
ls -la "E:/Documents/Research/Series Name/"
ls -la /e/Documents/Research/"Series Name"/
```

If still nothing, try the native form:
```bash
ls -la "E:/Documents/Research/Series Name" 2>&1
```

**Pitfall — don't trust the content-search tool for directory discovery on Windows.** It's a ripgrep-backed file finder; absolute paths with spaces or with `/e/` prefix may not resolve. Use shell `ls` for any "what's in this folder?" question.

## Step 2 — Bulk extract to markdown in one pass

Don't read PDFs page-by-page into context. Extract everything to disk first, then read selectively.

```python
# Write this script to disk first, then run it.
# Inputs: base_dir (folder holding the PDFs), file_label_pairs (list of (filename, label) tuples)
# Output: writes <base_dir>/_extracted/<label>_full.md for each input file
import pymupdf, os

base_dir = "/path/to/folder/with/pdfs"
file_label_pairs = [
    ("file1.pdf", "Label1"),
    ("file2.pdf", "Label2"),
    # ...add more (filename, label) tuples here
]
os.makedirs(os.path.join(base_dir, "_extracted"), exist_ok=True)

for fname, label in file_label_pairs:
    path = os.path.join(base_dir, fname)
    doc = pymupdf.open(path)
    out = os.path.join(base_dir, "_extracted", f"{label}_full.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"# {label}: {fname}\n\nTotal pages: {len(doc)}\n\n")
        for i, page in enumerate(doc):
            f.write(f"\n<!-- Page {i+1} -->\n\n")
            f.write(page.get_text())
    doc.close()
```

```bash
# shell → uv run python /path/to/folder/_extract.py
```

**Pitfall — extract cheap, read selective.** The whole point of writing to disk is to enable selective reading via the file-reading tool with offset/limit. Do NOT then read every `_full.md` end-to-end back into context — that defeats the extraction.

**Pitfall — pymupdf vs marker-pdf per file.** For text-based PDFs, pymupdf is instant. For scanned PDFs you need marker-pdf. Scan the first page of each PDF via `page.get_text().strip()` before committing to the bulk extract — if any file is a scan, switch that file (or the whole batch) to marker-pdf. See the `ocr-and-documents` skill for marker-pdf install steps.

## Step 3 — Selective reading per file (in this order)

For each PDF, read these slices from the extracted markdown:

1. **Pages 1–3** — cover, acknowledgements, **table of contents**. The TOC tells you which page ranges matter for each topic. Read this even if you're tempted to skip — it saves time later.
2. **Introduction (typically pages 5–10)** — the paper's thesis and structure.
3. **2–4 key body sections from the TOC** — pick the ones the user asked about, or the highest-signal sections if the request is open-ended.
4. **Skip endnotes, references, appendices** unless explicitly asked.

Per-file rule of thumb: 200–400 lines of extracted text gives you enough to summarize without losing thread.

## Step 4 — Cross-file synthesis

Once every file has a per-file summary, build the cross-cutting output:

- **Per-file block**: title, authors, page count, 3–6 bullet "main content" + 1–2 sentence "key takeaway".
- **Cross-cutting table** when files are part of a series (Day 1/Day 2/..., chapter 1/chapter 2/..., paper A/paper B/...): columns = dimension (e.g. topic, framework, key concept), rows = file.
- **Final synthesis paragraph**: how the files relate, what they collectively argue, where they differ.

## Language and terminology rules

- Preserve original titles, author names, and proper nouns verbatim (e.g. "MCP", "A2A", "Karpathy", "vibe coding"). Do NOT translate proper nouns unless the user asks.
- If user is Vietnamese and files are English (common case): default to **Vietnamese narrative** with English terms in parentheses. The Vietnamese writing style guidance in SKILL.md applies.
- For each file, surface at least one concrete number, citation, or named framework from the source. Generic phrasing ("covers many topics") is the failure mode.

## Reference template — working example

A 5-paper series in `E:/Documents/Research/Series Name/`:
1. `ls` to enumerate → 5 PDFs found
2. Bulk extract → `_extracted/Paper1_full.md` ... `Paper5_full.md`, ~50-75 KB each
3. For each, read pages 1-3 (TOC) + intro + 2 key sections → ~200 lines per file consumed from disk
4. Synthesize: per-file block + comparison table mapping the 5 papers to a common framework (in this case: 5 sequential whitepapers on AI Agents → Mind map / Tools / Skills / Security / Production)

Total context cost: ~2000 lines of source text across all files, not 12000. Quality: each file gets accurate structure via TOC + intro before deep-dive.

## When this workflow does NOT fit

- **Single PDF** (one URL or one local file) → `references/single-paper-deep-dive.md`
- **Search the web for N papers** (URL-based) → Phase 2 Pattern A/B/C in main skill
- **N scanned PDFs needing OCR** → marker-pdf via `ocr-and-documents`, then this workflow from Step 2
- **N files of other formats** (Excel, Word, PPT) → use the same bulk-extract-then-selective-read shape, but adapt the extraction tool to the format (e.g. `openpyxl` for Excel, `python-docx` for Word)
