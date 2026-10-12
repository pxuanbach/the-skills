#!/usr/bin/env python3
"""
scan_common.py - Shared helpers for the built-in security scanners (scan_python / scan_js / scan_secrets).

Not a CLI. Provides the finding record, a line-independent fingerprint, file reading
and test-path detection. Stdlib only.
"""

import hashlib
import os
import re

SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}
MAX_READ_BYTES = 1_000_000
TEST_PATH = re.compile(
    r"(^|/)(tests?|__tests__|fixtures?|mocks?|__mocks__|e2e)/|(^|/)(test_|mock_)[^/]*$"
    r"|\.(test|spec)\.[jt]sx?$|_test\.py$|\.(example|sample|template)$"
)


def finding(rule_id, category, severity, file, line, message, snippet=""):
    """Build one finding. The id hashes rule + file + snippet, not the line number,
    so a triage verdict survives unrelated edits above the finding."""
    snippet = re.sub(r"\s+", " ", snippet.strip())[:200]
    digest = hashlib.sha1(f"{rule_id}|{file}|{snippet}".encode("utf-8")).hexdigest()[:10]
    return {
        "id": f"F-{digest}",
        "rule_id": rule_id,
        "category": category,
        "severity": severity,
        "file": file,
        "line": line,
        "message": message,
        "snippet": snippet,
        "verdict": "untriaged",
    }


def read_text(path):
    try:
        if os.path.getsize(path) > MAX_READ_BYTES:
            return None
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        return None
    if b"\0" in data[:8192]:
        return None
    return data.decode("utf-8", errors="replace")


def is_test_path(path):
    return TEST_PATH.search(path) is not None


def line_at(text, pos):
    return text.count("\n", 0, pos) + 1


def line_text(text, lineno):
    lines = text.splitlines()
    return lines[lineno - 1] if 0 < lineno <= len(lines) else ""
