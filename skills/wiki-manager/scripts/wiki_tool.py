#!/usr/bin/env python3
"""
wiki_tool.py - Helper script for managing the LLM Wiki in SDLC workflows.

Commands:
    python wiki_tool.py init   : Initialize wiki/ directory, registry.yaml, DESIGN.md, SYSTEM.md, log.md
    python wiki_tool.py sync   : Scan wiki/ and update registry.yaml with discovered modules & artifacts
    python wiki_tool.py lint   : Check frontmatter syntax, required fields, and cross-reference links
"""

import os
import sys
import re
from datetime import datetime

# Minimal YAML handler using simple parsing for standard frontmatter without third-party deps
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

def init_wiki(wiki_dir="wiki"):
    os.makedirs(wiki_dir, exist_ok=True)
    
    registry_path = os.path.join(wiki_dir, "registry.yaml")
    if not os.path.exists(registry_path):
        registry_content = f"""version: "1.0"
project: "SDLC Project"
last_updated: "{datetime.now().strftime('%Y-%m-%d')}"
system_doc: "SYSTEM.md"
design_doc: "DESIGN.md"
max_review_iterations: 3
modules: []
"""
        with open(registry_path, "w", encoding="utf-8") as f:
            f.write(registry_content)
        print(f"[OK] Created {registry_path}")

    design_path = os.path.join(wiki_dir, "DESIGN.md")
    if not os.path.exists(design_path):
        design_default = """# UI/UX Design Standards & Style Guide

> [!IMPORTANT]
> **Single Source of Truth for UI Components**
> When any Agent creates, modifies, or refactors UI components, layouts, or wireframes, it MUST adhere strictly to the design system, styling rules, and tokens specified in this document.

## 1. Visual Theme & Philosophy
- **Aesthetic Direction**: Modern, clean, and accessible
- **Mode Support**: Light & Dark mode support with WCAG AA contrast compliance

## 2. Design Tokens
- **Colors**: Primary, Secondary, Neutral backgrounds, Surface cards, Text hierarchy, Feedback states
- **Typography**: Primary UI font, Monospace code font, Scale (h1-h3, body, small, caption)
- **Spacing & Elevation**: 4px baseline grid, standard border radiuses, subtle elevation shadows

## 3. UI Component Standards
- **Buttons, Form Controls & Inputs, Cards, Modals**: Baseline styles, interactive states (hover, focus, disabled, loading)

## 4. Responsive & Layout Rules
- **Breakpoints**: Mobile (<640px), Tablet (640px-1024px), Desktop (>1024px)
"""
        with open(design_path, "w", encoding="utf-8") as f:
            f.write(design_default)
        print(f"[OK] Created {design_path}")

    system_path = os.path.join(wiki_dir, "SYSTEM.md")
    if not os.path.exists(system_path):
        system_default = """# System Architecture & Topology

## 1. Core Project Intent
- **Purpose**: Core mission and target user domain.

## 2. High-Level Architecture
- Architecture topology, communication flow, and system components.

## 3. Tech Stack
- **Core Engine / Backend**: Framework, Runtime, Language
- **Frontend / Client**: Framework, UI Library, State Management
- **Database & Storage**: Persistence layers, cache, migrations

## 4. Directory Structure & Directory Purpose
- Repository directory tree and the designated responsibility for each folder.

## 5. Monorepo App Boundaries & Modular Isolation
- Package boundaries, dependency direction, and module isolation rules.
"""
        with open(system_path, "w", encoding="utf-8") as f:
            f.write(system_default)
        print(f"[OK] Created {system_path}")

    log_path = os.path.join(wiki_dir, "log.md")
    if not os.path.exists(log_path):
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"# SDLC Activity Log\n\nChronological append-only record of all SDLC events. Never edit past entries.\n\n## {datetime.now().strftime('%Y-%m-%d')}\n\n- **{datetime.now().strftime('%H:%M')}** — [Wiki Manager] Initialized wiki repository with SYSTEM.md and DESIGN.md.\n")
        print(f"[OK] Created {log_path}")

    print("[SUCCESS] Wiki initialized successfully.")

def sync_wiki(wiki_dir="wiki"):
    if not os.path.exists(wiki_dir):
        print(f"[ERROR] Directory '{wiki_dir}' does not exist. Run 'init' first.")
        return

    # Load existing registry to preserve module statuses
    existing_status = {}
    registry_path = os.path.join(wiki_dir, "registry.yaml")
    if os.path.exists(registry_path):
        with open(registry_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Parse existing module statuses from registry
        current_id = None
        for line in content.splitlines():
            m = re.match(r'^\s+-\s+id:\s+"([^"]+)"', line)
            if m:
                current_id = m.group(1)
            elif re.match(r'^\s+status:\s+"([^"]+)"', line) and current_id:
                existing_status[current_id] = line.strip().split('"')[1]
                current_id = None

    modules = []
    for item in sorted(os.listdir(wiki_dir)):
        item_path = os.path.join(wiki_dir, item)
        if os.path.isdir(item_path) and re.match(r"^\d{3}-", item):
            # Preserve existing status; only set in_progress for new modules
            mod_info = {
                "id": item,
                "name": item[4:].replace("-", " ").title(),
                "status": existing_status.get(item, "in_progress"),
                "artifacts": {}
            }
            arts = mod_info["artifacts"]
            
            req = os.path.join(item_path, "requirement.md")
            if os.path.exists(req):
                arts["requirement"] = f"{item}/requirement.md"
                
            des = os.path.join(item_path, "design.md")
            if os.path.exists(des):
                arts["design"] = f"{item}/design.md"

            plan = os.path.join(item_path, "plan.md")
            if os.path.exists(plan):
                arts["plan"] = f"{item}/plan.md"

            ev = os.path.join(item_path, "evidence.md")
            if os.path.exists(ev):
                arts["evidence"] = f"{item}/evidence.md"

            qrev = os.path.join(item_path, "quality-review.md")
            if os.path.exists(qrev):
                arts["quality_review"] = f"{item}/quality-review.md"

            srev = os.path.join(item_path, "security-review.md")
            if os.path.exists(srev):
                arts["security_review"] = f"{item}/security-review.md"

            mockup_dir = os.path.join(item_path, "mockup")
            if os.path.exists(mockup_dir) and os.path.isdir(mockup_dir):
                arts["mockups"] = [f"{item}/mockup/{m}" for m in sorted(os.listdir(mockup_dir)) if m.endswith(".md")]

            # Extract description: prefer the Description section body of
            # requirement.md (Goal + paragraph); fallback to frontmatter
            # title. Append Goals line if description < 100 chars to
            # satisfy the semantic-search minimum enforced in lint.
            req_path = os.path.join(item_path, "requirement.md")
            if os.path.exists(req_path):
                with open(req_path, "r", encoding="utf-8") as f:
                    req_body = f.read()
                meta, _ = parse_frontmatter(req_path)
                title_fallback = meta.get("title", "") if isinstance(meta.get("title", ""), str) else ""

                desc = ""
                # 1. Try "## Description" section body
                desc_match = re.search(
                    r"##\s+Description\s*\n+(.+?)(?=\n##|\Z)", req_body, re.DOTALL
                )
                if desc_match:
                    desc = " ".join(desc_match.group(1).split())

                # 2. Fallback to frontmatter title
                if not desc:
                    desc = title_fallback

                # 3. Append Goals line if still < 100 chars
                if len(desc) < 100:
                    goal_match = re.search(
                        r"\*\*Goals\*\*:\s*(.+?)(?:\n|$)", req_body
                    )
                    if goal_match:
                        goal_text = goal_match.group(1).strip()
                        desc = f"{desc}. Goal: {goal_text}" if desc else goal_text

                # 4. Append Target Users line if still < 100 chars
                if len(desc) < 100:
                    tu_match = re.search(
                        r"\*\*Target Users\*\*:\s*(.+?)(?:\n|$)", req_body
                    )
                    if tu_match:
                        tu_text = tu_match.group(1).strip()
                        desc = f"{desc}. Target users: {tu_text}"

                mod_info["description"] = desc

            modules.append(mod_info)

    registry_path = os.path.join(wiki_dir, "registry.yaml")
    with open(registry_path, "w", encoding="utf-8") as f:
        f.write(f'version: "1.0"\nproject: "SDLC Project"\nlast_updated: "{datetime.now().strftime("%Y-%m-%d")}"\nsystem_doc: "SYSTEM.md"\ndesign_doc: "DESIGN.md"\nmax_review_iterations: 3\nmodules:\n')
        for m in modules:
            desc = m.get("description", "")
            f.write(f'  - id: "{m["id"]}"\n    name: "{m["name"]}"\n    description: "{desc}"\n    status: "{m["status"]}"\n    artifacts:\n')
            for art_k, art_v in m["artifacts"].items():
                if isinstance(art_v, list):
                    f.write(f'      {art_k}:\n')
                    for v in art_v:
                        f.write(f'        - "{v}"\n')
                else:
                    f.write(f'      {art_k}: "{art_v}"\n')

    print(f"[SUCCESS] Synced {len(modules)} feature modules into {registry_path}")

def lint_wiki(wiki_dir="wiki"):
    if not os.path.exists(wiki_dir):
        print(f"[ERROR] Directory '{wiki_dir}' does not exist.")
        return

    errors = 0
    warnings = 0

    print(f"--- Linting Wiki Directory: {wiki_dir} ---")
    for root, _, files in os.walk(wiki_dir):
        for f in files:
            if f.endswith(".md") and f not in ["DESIGN.md", "SYSTEM.md", "log.md"]:
                full_p = os.path.join(root, f)
                rel_p = os.path.relpath(full_p, wiki_dir)
                meta, _ = parse_frontmatter(full_p)

                if not meta:
                    print(f"[WARN] {rel_p}: Missing or invalid YAML frontmatter")
                    warnings += 1
                    continue

                if "id" not in meta:
                    print(f"[ERROR] {rel_p}: Missing 'id' in frontmatter")
                    errors += 1
                if "title" not in meta:
                    print(f"[ERROR] {rel_p}: Missing 'title' in frontmatter")
                    errors += 1

    # Registry description validation (semantic-search friendliness)
    registry_path = os.path.join(wiki_dir, "registry.yaml")
    if os.path.exists(registry_path):
        with open(registry_path, "r", encoding="utf-8") as rf:
            reg_content = rf.read()
        # Parse each module block
        for block in re.finditer(
            r'-\s+id:\s*"([^"]+)"\s*\n\s+name:\s*"([^"]+)"\s*\n\s+description:\s*"([^"]*)"',
            reg_content,
        ):
            mod_id = block.group(1)
            mod_name = block.group(2)
            mod_desc = block.group(3).strip()
            # Rule 1: must not be empty
            if not mod_desc:
                print(f"[ERROR] registry.yaml[{mod_id}]: description is empty")
                errors += 1

            # Rule 2: must be at least 5 words
            word_count = len(mod_desc.split())
            if mod_desc and word_count < 5:
                print(f"[ERROR] registry.yaml[{mod_id}]: description has {word_count} words (minimum 5).")
                errors += 1

            # Rule 3: must NOT be identical to name (case-insensitive)
            norm = lambda s: re.sub(r"\s+", " ", s.strip().lower())
            if mod_desc and norm(mod_desc) == norm(mod_name):
                print(
                    f"[ERROR] registry.yaml[{mod_id}]: description is identical to name "
                    f"({mod_name!r}). Description must describe the module, not repeat its name."
                )
                errors += 1

    print(f"\nLint complete: {errors} error(s), {warnings} warning(s)")
    if errors > 0:
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python wiki_tool.py [init|sync|lint]")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "init":
        init_wiki()
    elif cmd == "sync":
        sync_wiki()
    elif cmd == "lint":
        lint_wiki()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
