#!/usr/bin/env python3
"""
validate_security_review.py - Validator for Security Reviewer report (security-review.md).

Usage:
    python validate_security_review.py <path_to_security-review.md>
"""

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
