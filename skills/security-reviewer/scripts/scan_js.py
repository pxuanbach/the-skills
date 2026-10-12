#!/usr/bin/env python3
"""
scan_js.py - Built-in security scanner for JavaScript / TypeScript / Next.js (stdlib regex only).

Two kinds of checks:
- Line rules: eval/new Function, shell and SQL built from template strings, raw HTML sinks,
  NEXT_PUBLIC_ secrets, Math.random for secrets, jwt.decode, weak hashes, CORS "*",
  TLS verification off, open redirects, and dynamic server-side fetch (SSRF).
- Export checks: every Server Action export ("use server") and every App Router
  route handler (GET/POST/...) must call an auth function; Pages Router API routes too.

Usage (standalone):
    python scan_js.py <dir-or-file> [...]      # prints findings as JSON
Normally called by run_scan.py with the project's profile settings.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scan_common import finding, is_test_path, line_at, line_text, read_text  # noqa: E402
from plan_scan import glob_match  # noqa: E402

JS_EXT = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs")
SECRETISH = r"(?i)token|secret|passw|otp|nonce|salt|api_?key|session|reset"

# (rule_id, category, severity, pattern, message, require_on_line, forbid_on_line, server_only)
LINE_RULES = [
    ("JS-EVAL", "rce", "high", r"\beval\(|\bnew Function\(", "Dynamic code execution.", None, None, False),
    ("JS-CMDI", "injection", "high", r"\b(exec|execSync|spawn)\(\s*(`[^`]*\$\{|[\w.]+\s*\+)"
     r"|(?<![\w.$])(exec|execSync)\(\s*[A-Za-z_$]"
     r"|\b(child_process|childProcess|cp)\.(exec|execSync)\(\s*[A-Za-z_$]",
     "Shell command built from dynamic input; use execFile/spawn with an argument array.", None, None, False),
    ("JS-SQLI", "injection", "high",
     r"\$(queryRawUnsafe|executeRawUnsafe)\(|\.raw\(\s*`[^`]*\$\{|\.query\(\s*`[^`]*\$\{|\.query\(\s*['\"][^'\"]*['\"]\s*\+",
     "SQL built from dynamic input; use parameterized queries or tagged $queryRaw.", None, None, False),
    ("JS-XSS-HTML", "xss", "medium", r"dangerouslySetInnerHTML",
     "Raw HTML rendered without a visible sanitizer (DOMPurify/sanitize).", None, r"(?i)sanitiz|purify", False),
    ("JS-XSS-DOM", "xss", "medium", r"\.(innerHTML|outerHTML)\s*=[^=]|\bdocument\.write\(|insertAdjacentHTML\(",
     "DOM HTML sink; use textContent or sanitize.", None, None, False),
    ("JS-PUBLIC-SECRET", "data_exposure", "high", r"NEXT_PUBLIC_[A-Z0-9_]*(SECRET|TOKEN|PASSWORD|PRIVATE|API_KEY)",
     "NEXT_PUBLIC_ variables are inlined into the browser bundle.", None, None, False),
    ("JS-RANDOM", "crypto", "medium", r"Math\.random\(",
     "Math.random is predictable; use crypto.randomUUID/getRandomValues for secrets.", SECRETISH, None, False),
    ("JS-WEAKHASH", "crypto", "low", r"createHash\(\s*['\"](md5|sha1)['\"]",
     "MD5/SHA-1 are not collision-resistant.", None, None, False),
    ("JS-JWT-DECODE", "authz", "medium", r"\bjwt\.decode\(",
     "jsonwebtoken decode() does not verify the signature; use jwt.verify().", None, None, False),
    ("JS-CORS", "config", "medium",
     r"Access-Control-Allow-Origin['\"]?\s*[,:]\s*['\"]\*['\"]|\borigin\s*:\s*(['\"]\*['\"]|true)\b",
     "CORS allows any origin.", None, None, False),
    ("JS-TLS", "config", "medium", r"NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*['\"]?0|rejectUnauthorized\s*:\s*false",
     "TLS certificate verification disabled.", None, None, False),
    ("JS-REDIRECT", "input_validation", "low", r"\bredirect\([^)]*(searchParams|req\.query|query\.|params\.)",
     "Redirect target taken from the request; restrict to relative paths or an allowlist.", None, None, True),
    ("JS-SSRF", "injection", "low", r"\bfetch\(\s*(`[^`]*\$\{|[A-Za-z_])",
     "Server-side fetch with a dynamic URL; check it is not user-controlled (SSRF).", None, None, True),
]
COMPILED = [(r, c, s, re.compile(p), m, re.compile(req) if req else None, re.compile(fb) if fb else None, so)
            for r, c, s, p, m, req, fb, so in LINE_RULES]

USE_SERVER = re.compile(r"^\s*['\"]use server['\"]", re.M)
USE_CLIENT = re.compile(r"^\s*['\"]use client['\"]", re.M)
EXPORT_FN = re.compile(
    r"^export\s+(?:default\s+)?(?:async\s+)?function\s*(\w*)|^export\s+const\s+(\w+)\s*=\s*(?:async\b|\w+\()", re.M)
ROUTE_HANDLER = "**/app/**/route.{ts,js,tsx,jsx,mjs}"
PAGES_API = "**/pages/api/**/*.{ts,js,tsx,jsx,mjs}"
MIDDLEWARE = "{middleware,src/middleware,proxy,src/proxy}.{ts,js}"
HTTP_MUTATING = {"POST", "PUT", "PATCH", "DELETE"}
COMMENT = re.compile(r"^\s*(//|\*|/\*)")


def is_server_file(local, text):
    if USE_CLIENT.search(text):
        return False
    return bool(USE_SERVER.search(text)) or glob_match(local, ROUTE_HANDLER) or glob_match(local, PAGES_API) \
        or "/app/" in f"/{local}" or local.startswith("server/") or "/server/" in local


def route_path(local):
    """apps/web/app/(shop)/api/users/[id]/route.ts -> /api/users/[id]"""
    part = re.split(r"(?:^|/)app/", local, maxsplit=1)[-1]
    part = re.sub(r"/?route\.\w+$", "", part)
    part = "/".join(seg for seg in part.split("/") if not (seg.startswith("(") and seg.endswith(")")))
    return "/" + part


def export_segments(text):
    matches = list(EXPORT_FN.finditer(text))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        yield (m.group(1) or m.group(2) or "default"), m.start(), text[m.start():end]


def check_exports(rel, local, text, auth_rx, public_routes, middleware_auth):
    out = []
    if USE_SERVER.search("\n".join(text.splitlines()[:5])):  # file-level directive
        for name, pos, body in export_segments(text):
            if not auth_rx.search(body):
                ln = line_at(text, pos)
                out.append(finding("JS-ACTION-NOAUTH", "authz", "high", rel, ln,
                                   f"Server Action `{name}` has no auth call. Server Actions are public POST endpoints.",
                                   line_text(text, ln)))
    if glob_match(local, ROUTE_HANDLER):
        path = route_path(local)
        if not any(glob_match(path, p) for p in public_routes):
            for name, pos, body in export_segments(text):
                if name not in HTTP_MUTATING | {"GET", "HEAD", "OPTIONS"} or name == "OPTIONS" or auth_rx.search(body):
                    continue
                sev = "high" if name in HTTP_MUTATING else "medium"
                note = ""
                if middleware_auth:
                    sev = "medium" if sev == "high" else "low"
                    note = " Middleware calls auth; confirm its matcher covers this path."
                ln = line_at(text, pos)
                out.append(finding("JS-ROUTE-NOAUTH", "authz", sev, rel, ln,
                                   f"{name} {path} has no auth call.{note}", line_text(text, ln)))
    if glob_match(local, PAGES_API) and not auth_rx.search(text):
        out.append(finding("JS-ROUTE-NOAUTH", "authz", "low" if middleware_auth else "medium", rel, 1,
                           "Pages Router API route without an auth call.", line_text(text, 1)))
    return out


def make_auth_regex(settings):
    names = [re.escape(n) for n in settings.get("auth_functions", [])]
    parts = [rf"\b({'|'.join(names)})\s*\("] if names else []
    if settings.get("auth_pattern"):
        parts.append(re.sub(r"^\(\?i\)", "", settings["auth_pattern"]))
    return re.compile("|".join(f"(?:{p})" for p in parts) or r"\bauth\s*\(", re.IGNORECASE)


def scan(target, files, settings, root="."):
    """Scan repo-relative JS/TS files of one project rooted at `root`."""
    auth_rx = make_auth_regex(settings)
    public_routes = settings.get("public_routes", [])
    prefix = "" if root == "." else root + "/"
    middleware_auth = False
    for name in ("middleware", "src/middleware", "proxy", "src/proxy"):
        for ext in (".ts", ".js"):
            text = read_text(os.path.join(target, root, name + ext))
            if text and auth_rx.search(text):
                middleware_auth = True

    findings = []
    for rel in files:
        if not rel.endswith(JS_EXT) or is_test_path(rel) or rel.endswith(".d.ts"):
            continue
        text = read_text(os.path.join(target, rel))
        if not text:
            continue
        local = rel[len(prefix):] if rel.startswith(prefix) else rel
        server = is_server_file(local, text)
        for lineno, line in enumerate(text.splitlines(), 1):
            if COMMENT.match(line) or len(line) > 2000:
                continue
            for rule, cat, sev, rx, msg, req, forbid, server_only in COMPILED:
                if server_only and not server:
                    continue
                if rx.search(line) and (req is None or req.search(line)) and not (forbid and forbid.search(line)):
                    findings.append(finding(rule, cat, sev, rel, lineno, msg, line))
        findings.extend(check_exports(rel, local, text, auth_rx, public_routes, middleware_auth))
    return findings


def _expand(paths):
    for p in paths:
        if os.path.isdir(p):
            for d, dirs, names in os.walk(p):
                dirs[:] = [x for x in dirs if x not in ("node_modules", ".next", "dist", "build", ".git")]
                yield from (os.path.relpath(os.path.join(d, n)).replace(os.sep, "/") for n in names)
        else:
            yield p.replace(os.sep, "/")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    print(json.dumps(scan(".", list(_expand(sys.argv[1:])), {}), indent=2))
