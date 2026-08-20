#!/usr/bin/env python3
"""
validate_requirement.py - Validator script for Requirement Analyzer artifacts.

Usage:
    python validate_requirement.py <path_to_requirement.md>
"""

import os
import sys
import re

REQUIRED_FRONTMATTER = ["id", "title", "status"]
REQUIRED_SECTIONS = [
    "## Scope",
    "## Description",
    "## User Stories",
    "## Functional Requirements",
    "## Non-Functional Requirements",
    "## Testing Scenarios",
    "## Success Criteria"
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
    
    for line in yaml_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            meta[key.strip()] = val.strip().strip('"').strip("'")

    return meta, body

def validate_requirement(file_path):
    if not os.path.exists(file_path):
        print(f"[ERROR] File '{file_path}' does not exist.")
        return False

    meta, body = parse_frontmatter(file_path)
    errors = []

    # 1. Validate frontmatter
    if not meta:
        errors.append("Missing YAML frontmatter block (--- ... ---)")
    else:
        for key in REQUIRED_FRONTMATTER:
            if key not in meta or not meta[key]:
                errors.append(f"Missing required frontmatter field '{key}'")

    # 2. Validate section headings
    for section in REQUIRED_SECTIONS:
        if not re.search(re.escape(section), body, re.IGNORECASE):
            errors.append(f"Missing required section '{section}'")

    # 3. Output results
    if errors:
        print(f"[FAIL] Requirement validation failed for '{file_path}':")
        for err in errors:
            print(f"  - {err}")
        return False

    print(f"[SUCCESS] Requirement file '{file_path}' is valid and complete.")
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_requirement.py <path_to_requirement.md>")
        sys.exit(1)

    req_path = sys.argv[1]
    success = validate_requirement(req_path)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
