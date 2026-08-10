# Software Library Comparison — Patterns & Pitfalls

Condensed reference for comparing open-source software libraries in research sessions.

---

## License Classification

| License | Commercial use | Copyleft | Action |
|---|---|---|---|
| MIT, Apache-2.0, BSD-2/3 | ✅ Free | No | OK to recommend freely |
| AGPL-3.0 | ⚠️ Requires source disclosure | Yes (strong) | **Warn explicitly** — for closed-source commercial, do NOT recommend without commercial licensing note |
| LGPLv3 | ⚠️ Limited linking | Yes | safer than AGPL but still restrictive for embedded use |
| Unknown/unspecified | ⚠️ Risk | — | Flag in report; do not recommend for production |

**Always check PyPI classifiers AND the repo's LICENSE file** — `license: None` on PyPI is common even for MIT/Apache projects (e.g., pdfplumber, unstructured).

---

## PDF Extraction Libraries — Key Players

| Library | PyPI name | GitHub stars | License | Special note |
|---|---|---|---|---|
| **opendataloader-pdf** | `opendataloader-pdf` | 27.8k | Apache-2.0 | PDF→Markdown/JSON/HTML, #1 benchmark (0.907 hybrid), bounding boxes, auto-tagging to Tagged PDF; Java 11+ core, Python SDK; hybrid AI mode for complex tables/OCR/formulas |
| **marker** | `marker-pdf` | 37.8k | Apache-2.0 | PDF→Markdown/JSON, no GPU needed |
| **surya** | `surya-ocr` (NOT `surya`) | 21.1k | Apache-2.0 | OCR + layout + table, 90+ languages |
| **pdfplumber** | `pdfplumber` | 10.6k | MIT | Char-level extraction, tables |
| **PyMuPDF** | `pymupdf` | 10.3k | **AGPL-3.0** ⚠️ | Fast C engine; AGPL blocks commercial |
| **camelot-py** | `camelot-py` | 3.8k | MIT | Table extraction (lattice/stream/nn); **verify GitHub is correct source** |
| **tabula-py** | `tabula-py` | 2.3k | MIT | tabula-java wrapper; **last release Oct 2024 — slightly stale** |
| **pymupdf4llm** | `pymupdf4llm` | — | **AGPL-3.0** ⚠️ | LLM/RAG-focused, AGPL |
| **unstructured** | `unstructured` | 15.2k | Apache-2.0 | Multi-format ETL (PDF+DOCX+XLSX+images) |

**Benchmark note (as of 2026):** opendataloader-pdf ranks #1 in hybrid mode (0.907 overall, 0.928 table extraction) on 200 real-world PDFs. Local mode is fastest at 0.015 s/page. See [opendataloader-bench](https://github.com/opendataloader-project/opendataloader-bench) for full comparison.

**AGPL-3.0 warning pattern:** PyMuPDF, pymupdf4llm → copyleft. For LLM/RAG pipelines, prefer `marker` (Apache-2.0, 37.8k stars) or `opendataloader-pdf` (Apache-2.0, 27.8k stars) over AGPL libraries.

---

## Excel Extraction Libraries — Key Players

| Library | PyPI name | GitHub stars | License | Notes |
|---|---|---|---|---|
| **openpyxl** | `openpyxl` | ~6.2k | MIT | Full Excel: formulas, charts, merged cells, named ranges, styles. 6.2B PyPI downloads. |
| **pandas** | `pandas` | ~49k | BSD-3 | Tabular data only — strips formulas, merged cells, charts, styles. For data analysis, not structure extraction. |
| **xlrd** | `xlrd` | ~2.2k | BSD | Legacy `.xls` specialist. **v2.0 dropped chart/macro support** ⚠️ |
| **pyexcel** | `pyexcel` | ~1.3k | BSD-3 | Thin wrapper delegating to openpyxl/xlrd/pyxlsb. Strips formatting. |
| **pyxlsb** | `pyxlsb` | ~96 | LGPLv3 | `.xlsb` binary reader only. Nearly unmaintained (last release Oct 2022). |

**`pandas-excel` does not exist as a standalone package.** pandas uses openpyxl/xlrd/pyxlsb internally as engines.

---

## Word (.docx/.doc) Extraction Libraries — Key Players

| Library | PyPI name | GitHub stars | License | Notes |
|---|---|---|---|---|
| **python-docx** | `python-docx` | ~5.7k | MIT | Full DOCX API (read/write), tables/images/headings. Does NOT read .doc legacy. |
| **mammoth** | `mammoth` | ~1.1k | BSD-2 | DOCX→clean HTML/Markdown. Best semantic structure preservation (headings, footnotes, comments). |
| **textract** | `textract` | ~4.7k | MIT | Universal extractor (many formats). Requires external binaries (antiword, tesseract, pandoc). |
| **pypandoc** | `pypandoc` | ~1.1k | MIT | Pandoc wrapper. **ONLY library supporting legacy .doc AND track changes.** |
| **docx2txt** | `docx2txt` | ~585 | **Unknown ⚠️** | Lightweight flat-text extraction. No license specified — do NOT use for commercial projects. |

**Only pypandoc supports track changes and legacy .doc binary format.**

---

## Cross-Verification Checklist

1. **License:** Check BOTH PyPI `license` field AND PyPI classifiers. If null on PyPI, check repo's LICENSE file.
2. **Stars:** Cross-reference PyPI GitHub stats badge AND GitHub REST API (slight discrepancies are normal; trust the more recent).
3. **Version:** Use PyPI latest release date (more accurate than GitHub `pushed_at` which tracks commits, not releases).
4. **Package name != library name:** Always query `https://pypi.org/pypi/<name>/json` → `project_urls['Repository']` to find the actual GitHub path.
5. **Stale library warning:** Flag if last release >18 months ago despite recent commits (e.g., tabula-py Oct 2024, pyxlsb Oct 2022).
6. **OCR libraries:** `surya` ships as `surya-ocr` on PyPI; `marker` has no OCR built-in; `unstructured` has optional Tesseract/PaddleOCR.
7. **GitHub org discovery:** When a PyPI package name doesn't match the GitHub org path, use `api.github.com/search/repositories?q=<libname>+language:<lang>` to find the correct `full_name` before calling `api.github.com/repos/<full_name>`. Example: `opendataloader-pdf` → org is `opendataloader-project` (not `OpenDataLoader`).
