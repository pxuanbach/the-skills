#!/usr/bin/env python3
"""
validate_design.py - Validator for User Designer technical design artifact (design.md).

Usage:
    python validate_design.py <path_to_design.md>
"""

import os
import sys
import re

REQUIRED_FRONTMATTER = ["id", "title", "derived_from", "status"]
VALID_STATUSES = ["DRAFT", "APPROVED", "DEPRECATED"]
REQUIRED_SECTIONS = [
    r"## (?:Design Decisions|System Architecture|Architecture)",
    r"## API Contracts",
    r"## Data Models",
    r"## (?:E2E & Integration Test Cases|E2E Test Cases|Integration Test Cases)",
    r"## Acceptance Criteria"
]

def parse_frontmatter(file_path):
    if not os.path.exists(file_path):
        return None, ""
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

def validate_design(design_path):
    if not os.path.exists(design_path):
        print(f"[ERROR] Technical design file '{design_path}' does not exist.")
        return False

    meta, body = parse_frontmatter(design_path)
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
        print(f"[FAIL] Technical design validation failed for '{design_path}':")
        for err in errors:
            print(f"  - {err}")
        return False

    print(f"[SUCCESS] Technical design file '{design_path}' is valid (status: {meta.get('status')}).")
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_design.py <path_to_design.md>")
        sys.exit(1)

    design_path = sys.argv[1]
    success = validate_design(design_path)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
