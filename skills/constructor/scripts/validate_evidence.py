#!/usr/bin/env python3
"""
validate_evidence.py - Validator for Constructor evidence artifact (evidence.md).

Usage:
    python validate_evidence.py <path_to_evidence.md>
"""

import os
import sys
import re

REQUIRED_FRONTMATTER = ["id", "title", "derived_from", "status", "tasks_completed"]
REQUIRED_SECTIONS = [
    r"## (?:Execution Summary|Execution & Testing Summary|Overview)",
    r"## Task Execution Log",
    r"## Test Verification & Logs",
    r"## (?:Artifacts & Changed Files|Code & File Artifacts|Artifacts)"
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

def validate_evidence(evidence_path):
    if not os.path.exists(evidence_path):
        print(f"[ERROR] Evidence file '{evidence_path}' does not exist.")
        return False

    meta, body = parse_frontmatter(evidence_path)
    errors = []

    # 1. Frontmatter check
    if not meta:
        errors.append("Missing YAML frontmatter (--- ... ---)")
    else:
        for k in REQUIRED_FRONTMATTER:
            if k not in meta or meta[k] is None or meta[k] == "":
                errors.append(f"Missing required frontmatter field '{k}'")

    # 2. Section check
    for sec_pattern in REQUIRED_SECTIONS:
        if not re.search(sec_pattern, body, re.IGNORECASE):
            clean_name = sec_pattern.replace(r"(?:", "").replace(r")", "").replace(r"\\", "")
            errors.append(f"Missing required section header matching '{clean_name}'")

    # 3. Test logs check (must contain a code block in body)
    if not re.search(r"```(?:bash|sh|text|out|console)?\s*\n.*?\n```", body, re.DOTALL):
        errors.append("No code block containing test logs found in document body")

    if errors:
        print(f"[FAIL] Evidence validation failed for '{evidence_path}':")
        for err in errors:
            print(f"  - {err}")
        return False

    completed_tasks = meta.get("tasks_completed", [])
    if isinstance(completed_tasks, str):
        completed_tasks = [completed_tasks]
    print(f"[SUCCESS] Evidence file '{evidence_path}' is valid ({len(completed_tasks)} task(s) verified in frontmatter).")
    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_evidence.py <path_to_evidence.md>")
        sys.exit(1)

    evidence_path = sys.argv[1]
    success = validate_evidence(evidence_path)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
