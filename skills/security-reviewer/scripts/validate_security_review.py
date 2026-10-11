#!/usr/bin/env python3
"""
validate_security_review.py - Validator for Security Reviewer report (security-review.md).

Usage:
    python validate_security_review.py <path_to_security-review.md>
"""

import json
import os
import sys
import re

REQUIRED_FRONTMATTER = ["id", "title", "derived_from", "status", "iteration"]
VALID_STATUSES = ["PASS", "FAIL"]
REQUIRED_SECTIONS = [
    r"## Executive Security Summary",
    r"## 10 Vulnerability Categories Scan Results",
    r"## (?:False Positive & Low-Impact Filter Log|Actionable Security Findings)"
]

def parse_frontmatter(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if not match:
        return {}, content

    yaml_text = match.group(1)
    body = match.group(2)
    meta = {}
    
    current_key = None
    for line in yaml_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- ") and current_key:
            val = line[2:].strip().strip('"').strip("'")
            if not isinstance(meta.get(current_key), list):
                meta[current_key] = []
            meta[current_key].append(val)
        elif ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            current_key = key
            if val:
                meta[key] = val
            else:
                meta[key] = []

    return meta, body

VERDICT = re.compile(r"\b(confirmed|rejected|needs_validation)\b", re.IGNORECASE)


def check_triage(findings_path, body, status):
    """Each high/medium finding id must appear on a report line that carries a verdict.
    A PASS report may not contain a confirmed high/medium finding."""
    with open(findings_path, "r", encoding="utf-8") as f:
        findings = json.load(f).get("findings", [])
    errors = []
    lines = body.splitlines()
    for item in findings:
        if item.get("severity") not in ("high", "medium"):
            continue
        rows = [l for l in lines if item["id"] in l]
        verdicts = {m.group(1).lower() for l in rows for m in VERDICT.finditer(l)}
        if not verdicts:
            errors.append(f"Untriaged {item['severity']} finding {item['id']} ({item['rule_id']} {item['file']}:{item['line']}) "
                          "- add it to '## Automated Scan Triage' with confirmed | rejected | needs_validation")
            continue
        if "confirmed" in verdicts and not any("upheld" in l.lower() for l in rows):
            errors.append(f"Finding {item['id']} is confirmed without independent verification "
                          "(Verifier column must be 'upheld', see references/verification.md)")
        if "confirmed" in verdicts and str(status).upper() == "PASS":
            errors.append(f"Status is PASS but {item['severity']} finding {item['id']} is confirmed")
    return errors


CLAIM_FIELDS = ["Location", "Attacker", "Entry Point", "Boundary", "Impact", "Verification", "Required Remediation"]


def check_actionable(body, status):
    """FAIL reports list each finding with the full claim, verified as upheld."""
    m = re.search(r"^## Actionable Security Findings.*?$(.*?)(?=^## |\Z)", body, re.M | re.S)
    section = m.group(1) if m else ""
    blocks = re.split(r"^\s*\d+\.\s+(?=\*\*)", section, flags=re.M)[1:]
    errors = []
    if str(status).upper() == "FAIL" and not blocks:
        errors.append("Status is FAIL but '## Actionable Security Findings' lists no numbered finding")
    for i, block in enumerate(blocks, 1):
        for field in CLAIM_FIELDS:
            fm = re.search(rf"\*\*{field}\*\*:\s*(.*)", block)
            value = fm.group(1).strip() if fm else ""
            if not value or re.fullmatch(r"<[^>]*>", value):
                errors.append(f"Actionable finding {i}: missing or placeholder '**{field}**'")
            elif field == "Verification" and "upheld" not in value.lower():
                errors.append(f"Actionable finding {i}: Verification must be 'upheld' (otherwise reject it "
                              "or move it to needs_validation)")
    return errors


def validate_security_review(review_path):
    if not os.path.exists(review_path):
        print(f"[ERROR] Security review file '{review_path}' does not exist.")
        return False

    meta, body = parse_frontmatter(review_path)
    errors = []

    # 1. Frontmatter check
    if not meta:
        errors.append("Missing YAML frontmatter (--- ... ---)")
    else:
        for k in REQUIRED_FRONTMATTER:
            if k not in meta or meta[k] is None or meta[k] == "" or (isinstance(meta[k], list) and len(meta[k]) == 0):
                errors.append(f"Missing required frontmatter field '{k}'")

        status = meta.get("status", "")
        if isinstance(status, list):
            status = status[0] if status else ""
        if status.upper() not in VALID_STATUSES:
            errors.append(f"Invalid status '{status}'. Must be one of {VALID_STATUSES}")

    # 2. Section check
    for sec_pattern in REQUIRED_SECTIONS:
        if not re.search(sec_pattern, body, re.IGNORECASE):
            clean_name = sec_pattern.replace(r"(?:", "").replace(r")", "").replace(r"\\", "")
            errors.append(f"Missing required section header matching '{clean_name}'")

    # 3. Triage gate: every high/medium finding from run_scan.py needs a verdict in the report
    findings_path = os.path.join(os.path.dirname(os.path.abspath(review_path)), "findings.json")
    if os.path.exists(findings_path):
        errors.extend(check_triage(findings_path, body, meta.get("status", "")))

    # 4. Claim + verification gate for actionable findings
    errors.extend(check_actionable(body, meta.get("status", "")))

    if errors:
        print(f"[FAIL] Security review validation failed for '{review_path}':")
        for err in errors:
            print(f"  - {err}")
        return False

    print(f"[SUCCESS] Security review file '{review_path}' is valid (status: {meta.get('status')}).")
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_security_review.py <path_to_security-review.md>")
        sys.exit(1)

    review_path = sys.argv[1]
    success = validate_security_review(review_path)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
