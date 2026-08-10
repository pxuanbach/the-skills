# Excel Library Research — Python Ecosystem

Condensed findings from library comparison research. For the full structured report see `C:\Users\pxuan\excel_libraries_research.md`.

---

## Libraries at a Glance

| Library | GitHub | Stars (≈) | License | Latest Version | Date |
|---|---|---|---|---|---|
| **openpyxl** | openpyxl/openpyxl (canonical moved from Launchpad) | ~3k–4k+ | MIT | 3.1.5 | Jun 2024 |
| **pandas** (read_excel) | pandas-dev/pandas | ~49,300 | BSD-3 | 3.0.5 | Jul 2026 |
| **xlrd** | python-excel/xlrd | ~2,206 | BSD | 2.0.2 | Jun 2025 |
| **pyxlsb** | willtrnr/pyxlsb | ~96 | LGPL v3 | 1.0.10 | Oct 2022 |
| **pyexcel** | pyexcel/pyexcel | ~1,290 | BSD-3 | 0.7.6 | Jun 2026 |

> **pandas-excel**: Does not exist as a standalone package. Pandas' Excel I/O uses openpyxl/xlrd/pyxlsb internally as engines.

---

## Feature Comparison for Complex Extraction

| Feature | openpyxl | pandas | xlrd | pyxlsb | pyexcel |
|---|---|---|---|---|---|
| **Multiple sheets** | ✅ Full | ✅ All | ✅ Full | ✅ Basic | ✅ Via plugins |
| **Formula text** | ✅ Read/write | ❌ Values only | ✅ Text + value | ❌ Values only | ❌ Values only |
| **Charts** | ✅ Full | ❌ | ⚠️ Basic | ❌ | ❌ |
| **Cell formatting** | ✅ Full | ❌ | ✅ Full | ❌ Limited | ❌ |
| **Merged cells** | ✅ Full | ⚠️ Partial | ✅ Full | ❌ | ❌ |
| **Named ranges** | ✅ Full | ❌ | ✅ Full | ❌ | ❌ |
| **Data validation** | ✅ | ❌ | ✅ | ❌ | ❌ |
| **Conditional formatting** | ✅ | ❌ | ⚠️ Basic | ❌ | ❌ |
| **Images** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Write support** | ✅ | ✅ (via engine) | ❌ | ❌ | ✅ |
| **File formats** | .xlsx, .xlsm | .xlsx, .xls, .xlsb | .xls only | .xlsb only | All (via plugins) |

---

## When to Use Each

**openpyxl** — complex extraction (formulas, charts, formatting, merged cells, named ranges)
- ~6.2B PyPI downloads; de facto standard for .xlsx
- Can read formula text OR cached values via `data_only=False/True`
- Pure Python; fast enough with `read_only=True` for large files
- MIT license — permissive for commercial use

**xlrd** — legacy .xls (binary) files only
- v2.0+ dropped chart/macro support for .xls (use v1.x for chart support, but deprecated)
- Fast C internals
- If you need .xlsx, use openpyxl instead

**pandas `read_excel`** — tabular data analysis, not structural Excel features
- All formatting, charts, merged cells, named ranges are lost
- Use `engine='openpyxl'` (default for .xlsx) or `engine='pyxlsb'` for .xlsb
- Formula results readable; formula text not accessible

**pyxlsb** — only option for .xlsb (Excel Binary Workbook) format
- Very limited; maintainer says "functional enough for basic data extraction"
- Largely unmaintained since 2022
- Not recommended unless .xlsb is the only format available

**pyexcel** — thin wrapper only; delegates to the above
- Development stalled (alpha for years)
- Discards all formatting and structural features
- Use the underlying libraries directly instead

---

## Quick Code Snippets

**openpyxl — read all sheets with formulas:**
```python
from openpyxl import load_workbook
wb = load_workbook('file.xlsx', data_only=False)  # formulas
for name in wb.sheetnames:
    ws = wb[name]
    for row in ws.iter_rows():
        for cell in row:
            if cell.value:
                print(cell.coordinate, cell.value)
```

**openpyxl — read named ranges:**
```python
wb = load_workbook('file.xlsx')
for dn in wb.defined_names.definedName:
    print(dn.name, dn.attr_text)
```

**xlrd — basic extraction:**
```python
import xlrd
book = xlrd.open_workbook('file.xls')
for sname in book.sheet_names():
    sh = book.sheet_by_name(sname)
    print(sh.name, sh.nrows, sh.ncols)
```

**pandas with specific engine:**
```python
import pandas as pd
df = pd.read_excel('file.xlsx', sheet_name=None, engine='openpyxl')
df2 = pd.read_excel('file.xlsb', engine='pyxlsb')
```
