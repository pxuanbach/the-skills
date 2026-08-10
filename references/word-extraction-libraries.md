# Python Word (.docx, .doc) Extraction Libraries — Comparison Reference

> Research date: 2026-07-25. Verified via PyPI JSON API and GitHub REST API.

## At-a-glance

| Library | GitHub URL | Stars | License | Version | Release Date |
|---|---|---|---|---|---|
| **python-docx** | https://github.com/python-openxml/python-docx | ~5,700 | MIT | 1.2.0 | 2025-06-17 |
| **mammoth** | https://github.com/mwilliamson/python-mammoth | ~1,100 | BSD-2-Clause | 1.12.0 | 2026-03-13 |
| **docx2txt** | https://github.com/ankushshah89/python-docx2txt | ~585 | unspecified | 0.9 | 2025-03-25 |
| **textract** | https://github.com/deanmalmgren/textract | ~4,700 | MIT | 2.0.0 | 2026-04-28 |
| **pypandoc** | https://github.com/JessicaTegner/pypandoc | ~1,100 | MIT | 1.17 | 2026-03-15 |

## Feature Matrix

| Feature | python-docx | mammoth | docx2txt | textract | pypandoc |
|---|---|---|---|---|---|
| `.docx` support | ✅ | ✅ | ✅ | ✅ | ✅ |
| `.doc` (legacy) support | ❌ | ❌ | ❌ | ✅ | ✅ |
| Tables | ✅ | ✅ | ✅ | ⚠️ flat | ✅ |
| Images | ✅ | ✅ | ✅ | ✅ (OCR) | ✅ |
| Headings/Structure | ✅ | ✅ | ❌ | ❌ | ✅ |
| Comments | ✅ | ✅ | ❌ | ❌ | ✅ |
| Track Changes | ❌ | ❌ | ❌ | ❌ | ✅ |
| Footnotes/Endnotes | ⚠️ | ✅ | ❌ | ❌ | ✅ |
| Embedded Objects | ⚠️ | ❌ | ❌ | ❌ | ⚠️ |
| External binaries | None | None | None | Many | Pandoc |
| Read-only | ❌ (edits) | ✅ | ✅ | ✅ | ✅ |

## Key Judgments

- **Best for structured `.docx` read/edit**: `python-docx`
- **Best for `.docx` → clean HTML/Markdown**: `mammoth` (semantic-only, ignores styling)
- **Best for quick plain-text + images**: `docx2txt` (minimal, pure Python, but unmaintained-looking; no license)
- **Best for multi-format universal extraction**: `textract` (many formats but flattens structure; heavy deps)
- **Best for feature completeness** (track changes, legacy `.doc`, footnotes, comments): `pypandoc`

## Critical notes

- **Only `pypandoc` and `textract`** handle the old binary `.doc` format.
- **`mammoth`** deliberately discards visual styling — produces semantic HTML only.
- **`textract`** requires system-level installs: antiword, pandoc, tesseract, etc. Not just pip.
- **`docx2txt`** v0.9 (latest as of 2025-03) has no license field on PyPI — caution for commercial use.
- **`python-docx`** handles comments via `part.comments`, footnotes via `part.footnotes_part` — not convenient APIs but accessible.
