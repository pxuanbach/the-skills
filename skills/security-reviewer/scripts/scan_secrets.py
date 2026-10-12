#!/usr/bin/env python3
"""
scan_secrets.py - Built-in secret scanner for any file type (stdlib regex only).

Detects well-known key formats (AWS, GitHub, Slack, Stripe, Google, OpenAI/Anthropic,
private keys, JWTs), secret-looking assignments with literal values, and filled-in
secrets in .env files that git does not ignore. Matched values are masked in the output,
so findings.json never contains the secret itself. Test fixtures and *.example files are skipped.

Usage (standalone):
    python scan_secrets.py <dir-or-file> [...]      # prints findings as JSON
"""

import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scan_common import finding, is_test_path, read_text  # noqa: E402

KNOWN_FORMATS = [
    ("SEC-AWS", r"\b(AKIA|ASIA)[0-9A-Z]{16}\b", "AWS access key id"),
    ("SEC-PRIVATE-KEY", r"-----BEGIN (RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY( BLOCK)?-----", "Private key"),
    ("SEC-GITHUB", r"\b(gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{60,})\b", "GitHub token"),
    ("SEC-SLACK", r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b", "Slack token"),
    ("SEC-STRIPE", r"\b[rs]k_live_[0-9A-Za-z]{16,}\b", "Stripe live key"),
    ("SEC-GOOGLE", r"\bAIza[0-9A-Za-z_\-]{35}\b", "Google API key"),
    ("SEC-LLM-KEY", r"\bsk-(ant-|proj-)?[A-Za-z0-9_\-]{32,}\b", "OpenAI/Anthropic API key"),
    ("SEC-JWT", r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b", "Hardcoded JWT"),
]
KNOWN = [(r, re.compile(p), d) for r, p, d in KNOWN_FORMATS]
ASSIGNMENT = re.compile(
    r"(?i)\b([A-Za-z0-9_]*(?:password|passwd|secret|api_?key|access_?key|private_?key|auth_?token|client_secret)"
    r"[A-Za-z0-9_]*)\b['\"]?\s*[:=]\s*['\"]([^'\"\s]{8,})['\"]")
ENV_LINE = re.compile(
    r"(?i)^\s*(?:export\s+)?([A-Z0-9_]*(?:PASSWORD|SECRET|API_KEY|TOKEN|PRIVATE_KEY|ACCESS_KEY|DATABASE_URL)[A-Z0-9_]*)"
    r"\s*=\s*['\"]?([^'\"\s#]{6,})")
PLACEHOLDER = re.compile(
    r"(?i)changeme|change_me|example|xxx|your[_-]|<|\$\{|process\.env|os\.environ|getenv|dummy|placeholder|\*\*\*|"
    r"todo|fake|sample|redacted|^test|localhost")
SKIP_FILES = re.compile(r"(^|/)(package-lock\.json|pnpm-lock\.yaml|yarn\.lock|poetry\.lock|uv\.lock|Cargo\.lock)$|\.(min\.js|map|svg)$")


def mask(text, value):
    return text.replace(value, value[:4] + "…" + f"[{len(value)} chars]") if value else text


def git_ignored(target, rel):
    try:
        return subprocess.run(["git", "-C", target, "check-ignore", "-q", rel],
                              capture_output=True).returncode == 0
    except OSError:
        return False


def scan(target, files, settings=None):
    findings = []
    for rel in files:
        if is_test_path(rel) or SKIP_FILES.search(rel):
            continue
        text = read_text(os.path.join(target, rel))
        if not text:
            continue
        is_env = re.search(r"(^|/)\.env[^/]*$", rel) is not None
        if is_env and git_ignored(target, rel):
            continue  # local env file, not committed
        for lineno, line in enumerate(text.splitlines(), 1):
            if len(line) > 4000:
                continue
            hit = False
            for rule, rx, desc in KNOWN:
                m = rx.search(line)
                if m:
                    findings.append(finding(rule, "data_exposure", "high", rel, lineno,
                                            f"{desc} committed to the repository; rotate it and load from env/secret store.",
                                            mask(line, m.group(0))))
                    hit = True
            if hit:
                continue
            m = (ENV_LINE if is_env else ASSIGNMENT).search(line)
            if m and not PLACEHOLDER.search(m.group(2)):
                where = "env file tracked by git" if is_env else "source"
                findings.append(finding("SEC-ASSIGN", "data_exposure", "high" if is_env else "medium", rel, lineno,
                                        f"`{m.group(1)}` has a literal value in {where}; load it from the environment.",
                                        mask(line, m.group(2))))
    return findings


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    paths = []
    for p in sys.argv[1:]:
        if os.path.isdir(p):
            for d, dirs, names in os.walk(p):
                dirs[:] = [x for x in dirs if x not in ("node_modules", ".git", ".venv", "venv", ".next")]
                paths += [os.path.relpath(os.path.join(d, n)).replace(os.sep, "/") for n in names]
        else:
            paths.append(p.replace(os.sep, "/"))
    print(json.dumps(scan(".", paths), indent=2))
