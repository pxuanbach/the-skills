#!/usr/bin/env python3
"""
validate_html_mockup.py - Validator for HTML prototypes (mockup/*.html) produced by `user-designer DESIGN html`.

Checks the rules in references/html_prototype_guide.md that can be verified statically:
skeleton, hardcoded hex outside :root, external resources, console.log,
accessibility basics, and required component states.

Usage:
    python validate_html_mockup.py <mockup_dir_or_html_file>

Exit code 1 when any ERROR is found. WARN items do not fail the run.
"""

import os
import re
import sys


def _strip_root_blocks(css):
    """Remove :root { ... } blocks (including those nested in @media) so token definitions may use hex."""
    out, i = [], 0
    while i < len(css):
        m = re.compile(r":root\s*\{").search(css, i)
        if not m:
            out.append(css[i:])
            break
        out.append(css[i:m.start()])
        depth, j = 1, m.end()
        while j < len(css) and depth:
            depth += {"{": 1, "}": -1}.get(css[j], 0)
            j += 1
        i = j
    return "".join(out)


def validate_file(path):
    errors, warns = [], []
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    lower = html.lower()

    # 1. Skeleton
    if not lower.lstrip().startswith("<!doctype html"):
        errors.append("Missing <!doctype html>")
    if not re.search(r"<html[^>]*\slang=", html, re.IGNORECASE):
        errors.append('<html> is missing a lang attribute (e.g. lang="en")')
    if "<title" not in lower:
        errors.append("Missing <title>")
    if 'name="viewport"' not in lower:
        errors.append("Missing viewport <meta>")
    if "<main" not in lower:
        errors.append("Missing <main> landmark")

    # 2. Hardcoded hex outside :root (scan <style> blocks and inline style attributes)
    css_chunks = re.findall(r"<style[^>]*>(.*?)</style>", html, re.DOTALL | re.IGNORECASE)
    css_chunks += re.findall(r'style="([^"]*)"', html, re.IGNORECASE)
    hex_hits = 0
    for chunk in css_chunks:
        hex_hits += len(re.findall(r"#[0-9a-fA-F]{3,8}\b", _strip_root_blocks(chunk)))
    if hex_hits:
        errors.append(f"{hex_hits} hardcoded hex color(s) outside :root — use var(--token) from wiki/DESIGN.md")
    if not re.search(r":root\s*\{", html):
        errors.append("No :root token block found — mirror wiki/DESIGN.md tokens")

    # 3. External resources / links
    for m in re.finditer(r'<(?:script|link|img|iframe|source)[^>]+(?:src|href)="(https?:)?//[^"]+"', html, re.IGNORECASE):
        errors.append(f"External resource: {m.group(0)[:80]}")
    for m in re.finditer(r'<a\s[^>]*href="(https?:)?//[^"]+"', html, re.IGNORECASE):
        errors.append(f"External link: {m.group(0)[:80]}")
    if re.search(r"@import\s+url\(\s*['\"]?https?:", html, re.IGNORECASE):
        errors.append("External @import in CSS")

    # 4. Debug leftovers
    if "console.log" in html:
        errors.append("console.log left in prototype")

    # 5. Accessibility
    h1_count = len(re.findall(r"<h1[\s>]", html, re.IGNORECASE))
    if h1_count != 1:
        errors.append(f"Expected exactly one <h1>, found {h1_count}")
    for m in re.finditer(r"<button\b([^>]*)>(.*?)</button>", html, re.DOTALL | re.IGNORECASE):
        attrs, inner = m.group(1), re.sub(r"<[^>]+>", "", m.group(2)).strip()
        if not inner and "aria-label" not in attrs.lower():
            errors.append("Icon-only <button> without aria-label")
    for m in re.finditer(r"<input\b([^>]*)>", html, re.IGNORECASE):
        attrs = m.group(1)
        if re.search(r'type="(hidden|submit|button)"', attrs, re.IGNORECASE):
            continue
        id_m = re.search(r'\bid="([^"]+)"', attrs)
        labelled = "aria-label" in attrs.lower() or (id_m and re.search(rf'for="{re.escape(id_m.group(1))}"', html))
        if not labelled:
            errors.append(f"<input> without label: {attrs.strip()[:60]}")
    if "prefers-color-scheme: dark" not in lower:
        warns.append("No prefers-color-scheme: dark block")
    if "animation" in lower or "transition" in lower:
        if "prefers-reduced-motion" not in lower:
            warns.append("Animation/transition used without prefers-reduced-motion")
    if "skip-link" not in lower and "skip to" not in lower:
        warns.append("No skip link to <main>")

    # 6. Required component states (at least one demo of each)
    for label, pattern in [
        ("hover", r":hover"),
        ("focus", r":focus-visible"),
        ("disabled", r"\[disabled\]|\sdisabled[\s>=]"),
        ("loading", r"is-loading"),
        ("error", r'aria-invalid="true"'),
    ]:
        if not re.search(pattern, html, re.IGNORECASE):
            warns.append(f"No '{label}' state demonstrated")
    if not re.search(r"empty", lower):
        warns.append("No empty state demonstrated")

    # 7. Lineage comment
    if "reused patterns" not in lower:
        warns.append("Missing 'Reused patterns from prior modules' comment (record 'none' if standalone)")

    return errors, warns


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_html_mockup.py <mockup_dir_or_html_file>")
        sys.exit(1)

    target = sys.argv[1]
    if os.path.isdir(target):
        files = sorted(os.path.join(target, f) for f in os.listdir(target) if f.endswith(".html"))
    elif os.path.isfile(target):
        files = [target]
    else:
        print(f"[ERROR] '{target}' does not exist.")
        sys.exit(1)

    if not files:
        print(f"[ERROR] No .html mockups found in '{target}'.")
        sys.exit(1)

    failed = False
    for path in files:
        errors, warns = validate_file(path)
        name = os.path.basename(path)
        if errors:
            failed = True
            print(f"[FAIL] {name}")
            for e in errors:
                print(f"  - ERROR: {e}")
        else:
            print(f"[OK] {name}")
        for w in warns:
            print(f"  - WARN: {w}")

        # Companion inventory (recommended by the guide)
        if not os.path.exists(path[:-5] + ".md"):
            print(f"  - WARN: no companion {name[:-5]}.md component inventory")

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
