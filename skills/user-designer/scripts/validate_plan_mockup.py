#!/usr/bin/env python3
"""
validate_plan_mockup.py - Validator for User Designer artifacts (plan.md and mockup/*.md).

Usage:
    python validate_plan_mockup.py <path_to_plan.md>
"""

import os
import sys
import re

REQUIRED_PLAN_FRONTMATTER = ["id", "title", "derived_from"]
REQUIRED_PLAN_SECTIONS = [
    "## Implementation Plan",
    "## Implementation Process",
    "## Tasks"
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

def validate_plan(plan_path):
    if not os.path.exists(plan_path):
        print(f"[ERROR] Plan file '{plan_path}' does not exist.")
        return False

    meta, body = parse_frontmatter(plan_path)
    errors = []

    # 1. Frontmatter check
    if not meta:
        errors.append("Missing YAML frontmatter (--- ... ---)")
    else:
        for k in REQUIRED_PLAN_FRONTMATTER:
            if k not in meta or not meta[k]:
                errors.append(f"Missing required frontmatter field '{k}'")

    # 2. Section check
    for sec in REQUIRED_PLAN_SECTIONS:
        if not re.search(re.escape(sec), body, re.IGNORECASE):
            errors.append(f"Missing required section '{sec}'")

    # 3. Tasks validation
    tasks = re.findall(r"(?:id|\*\*id\*\*):\s*([IT]-\d+)", body, re.IGNORECASE)
    if not tasks:
        errors.append("No valid tasks found (expected task items with id: I-xxx or T-xxx)")

    if errors:
        print(f"[FAIL] Plan validation failed for '{plan_path}':")
        for err in errors:
            print(f"  - {err}")
        return False

    print(f"[SUCCESS] Plan file '{plan_path}' is valid ({len(tasks)} task(s) verified).")

    # 4. Check optional mockups if mockup directory exists in same folder
    parent_dir = os.path.dirname(plan_path)
    mockup_dir = os.path.join(parent_dir, "mockup")
    if os.path.exists(mockup_dir) and os.path.isdir(mockup_dir):
        validate_mockups(mockup_dir)

    return True

def validate_mockups(mockup_dir):
    print(f"--- Checking Optional Mockups in {mockup_dir} ---")
    mockup_files = [m for m in os.listdir(mockup_dir) if m.endswith(".md")]
    for m in mockup_files:
        m_path = os.path.join(mockup_dir, m)
        meta, body = parse_frontmatter(m_path)
        if not meta or "id" not in meta:
            print(f"[WARN] Mockup '{m}': Missing 'id' frontmatter")
        else:
            print(f"[OK] Mockup '{m}' frontmatter valid (id: {meta['id']})")

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_plan_mockup.py <path_to_plan.md>")
        sys.exit(1)

    plan_path = sys.argv[1]
    success = validate_plan(plan_path)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
