#!/usr/bin/env python3
"""
validate_skill.py — Structural validation for Agent Skills.

Validates a skill directory against the review-skill checklist.
Exit code 0 = all checks pass. Exit code 1 = one or more failures.

Usage:
    python validate_skill.py <skill_dir>
    python validate_skill.py skills/requirement-analyzer

Options:
    --json    Output machine-readable JSON instead of human-readable tags
"""

import os
import re
import sys
import json
from pathlib import Path

SEVERITY_ERROR = "error"
SEVERITY_WARN = "warn"
SEVERITY_OK = "ok"

# Required frontmatter fields in order (name, description, version are required;
# license and metadata are optional but recommended)
REQUIRED_FIELDS = ["name", "description", "version"]
RECOMMENDED_FIELDS = ["license"]

# Patterns
KEBAB_CASE_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
# Absolute paths
ABS_PATH_RE = re.compile(r"^/[a-z]+/|^[A-Z]:[/\\]")
# Caps imperatives that need rationale check
IMPERATIVES_RE = re.compile(r"\b(ALWAYS|NEVER)\b", re.IGNORECASE)
# Phrases that signal rationale is present
RATIONALE_RE = re.compile(
    r"(because|reason|why|since|explain|otherwise|otherwise\s+you|"
    r"otherwise\s+the|this\s+ensures|this\s+prevents)",
    re.IGNORECASE,
)
# Bad description opener
BAD_OPENER_RE = re.compile(r"^a\s+helpful\s+skill\s+for", re.IGNORECASE)


def parse_frontmatter(content: str):
    """Parse YAML frontmatter from SKILL.md content.

    Splits on the first '---' block. Returns (frontmatter_dict, body_str).
    Handles both scalar 'key: value' and list 'key:\\n  - item' forms.
    Returns ({}, content) if no frontmatter found.
    """
    if not content.startswith("---"):
        return {}, content

    end = content.find("\n---\n", 3)
    if end == -1:
        return {}, content

    front_text = content[4:end]
    body = content[end + 5 :]

    result = {}
    current_key = None
    current_list = []

    for line in front_text.splitlines():
        stripped = line.strip()

        # List item
        if stripped.startswith("- "):
            item_val = stripped[2:].strip()
            if current_key:
                current_list.append(item_val)
            continue

        # Key: value
        key_match = re.match(r"^(\w+):\s*(.*)$", stripped)
        if key_match:
            key, val = key_match.groups()

            # Flush previous list key
            if current_key and current_list:
                result[current_key] = current_list
                current_list = []

            current_key = key
            val = val.strip()

            if val:  # scalar value
                result[key] = val
                current_key = None
            else:
                current_list = []

    # Flush final list
    if current_key and current_list:
        result[current_key] = current_list

    return result, body


def check_frontmatter_fields(frontmatter: dict, skill_dir: str) -> list:
    """Check required and recommended frontmatter fields."""
    issues = []

    for field in REQUIRED_FIELDS:
        if field not in frontmatter:
            issues.append(
                (SEVERITY_ERROR, f"Missing required frontmatter field: '{field}'")
            )

    for field in RECOMMENDED_FIELDS:
        if field not in frontmatter:
            issues.append(
                (SEVERITY_WARN, f"Missing recommended frontmatter field: '{field}'")
            )

    # name format
    name = frontmatter.get("name", "")
    if name and not KEBAB_CASE_RE.match(name):
        issues.append(
            (
                SEVERITY_ERROR,
                f"'name' must be kebab-case (found: '{name}')",
            )
        )

    # version format
    version = frontmatter.get("version", "")
    if version and not SEMVER_RE.match(version):
        issues.append(
            (
                SEVERITY_ERROR,
                f"'version' must be semver X.Y.Z (found: '{version}')",
            )
        )

    # description length
    description = frontmatter.get("description", "")
    if description and len(description) > 1024:
        issues.append(
            (
                SEVERITY_WARN,
                f"'description' is {len(description)} chars (recommended ≤1024)",
            )
        )

    # description bad opener
    if description and BAD_OPENER_RE.match(description):
        issues.append(
            (
                SEVERITY_ERROR,
                "Description starts with 'a helpful skill for...' — "
                "rewrite to front-load trigger keywords",
            )
        )

    return issues


def check_skill_md_body(body: str, frontmatter: dict) -> list:
    """Check SKILL.md body size and ALL-CAPS imperatives."""
    issues = []

    word_count = len(body.split())
    if word_count > 5000:
        issues.append(
            (
                SEVERITY_ERROR,
                f"SKILL.md body is {word_count} words (limit: 5000) — "
                "move content to references/",
            )
        )

    # Check ALL-CAPS imperatives without rationale.
    # Strip backtick code spans first so `ALWAYS` / `NEVER` in examples don't fire.
    body_no_code = re.sub(r"`[^`]*`", "", body)
    for match in IMPERATIVES_RE.finditer(body_no_code):
        pos = match.start()
        window = body_no_code[max(0, pos - 150) : pos + 150]
        if not RATIONALE_RE.search(window):
            issues.append(
                (
                    SEVERITY_ERROR,
                    f"'ALWAYS/NEVER' at position {pos} lacks rationale — "
                    "explain why the rule exists or move to AGENTS.md",
                )
            )

    return issues


def check_directory_layout(skill_dir: str) -> list:
    """Check that required and optional directories are correctly structured."""
    issues = []
    path = Path(skill_dir)

    # SKILL.md must exist
    if not (path / "SKILL.md").exists():
        issues.append((SEVERITY_ERROR, "SKILL.md is missing"))

    # Optional dirs should contain files if they exist
    for subdir in ["references", "scripts", "assets", "examples"]:
        subdir_path = path / subdir
        if subdir_path.exists():
            if not any(subdir_path.iterdir()):
                issues.append(
                    (
                        SEVERITY_WARN,
                        f"'{subdir}/' exists but is empty — "
                        f"remove it or add content",
                    )
                )

    return issues


def check_file_content(skill_dir: str) -> list:
    """Scan all files for secrets, absolute paths, and anti-patterns."""
    issues = []
    path = Path(skill_dir)

    skip_dirs = {".git", ".claude", "__pycache__", "node_modules", ".venv"}

    # Credential assignment patterns — only flag these contexts (not plain prose)
    # Matches: TOKEN = ..., secret: ..., export API_KEY=...
    CRED_ASSIGN_RE = re.compile(
        r"(\bapi[_-]?key\b|\btoken\b|\bpassword\b|\bsecret\b|\bauth\b|\bbearer\b"
        r"|\baws[_-]?secret\b)\s*([=:]|=>)\s*[\"']?[\w\-]{3,}",
        re.IGNORECASE,
    )
    # Environment-var credential references: ${SECRET}, $TOKEN, ${API_KEY}
    CRED_ENV_RE = re.compile(
        r"\$\{?\b(api[_-]?key|token|secret|password|auth|bearer)\b\}?",
        re.IGNORECASE,
    )

    for file_path in path.rglob("*"):
        if file_path.is_dir() or file_path.parent.name in skip_dirs:
            continue

        # Skip this script itself to avoid self-referential false positives
        if file_path.name == "validate_skill.py":
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # Secrets — only credential assignment / env-var contexts
        for match in CRED_ASSIGN_RE.finditer(content):
            line_num = content[: match.start()].count("\n") + 1
            issues.append(
                (
                    SEVERITY_ERROR,
                    f"{file_path.relative_to(path)}:{line_num} — "
                    f"possible hardcoded secret '{match.group()}'",
                )
            )
        for match in CRED_ENV_RE.finditer(content):
            line_num = content[: match.start()].count("\n") + 1
            issues.append(
                (
                    SEVERITY_ERROR,
                    f"{file_path.relative_to(path)}:{line_num} — "
                    f"possible hardcoded env-var secret '{match.group()}'",
                )
            )

        # Absolute paths
        for match in ABS_PATH_RE.finditer(content):
            line_num = content[: match.start()].count("\n") + 1
            issues.append(
                (
                    SEVERITY_ERROR,
                    f"{file_path.relative_to(path)}:{line_num} — "
                    f"hardcoded absolute path '{match.group()}'",
                )
            )

        # Scripts must have docstring/usage in first 5 lines
        if file_path.suffix == ".py" and "scripts" in file_path.parts:
            first_lines = "\n".join(content.splitlines()[:5])
            if "#" not in first_lines and '"""' not in first_lines and "#!" not in first_lines:
                issues.append(
                    (
                        SEVERITY_WARN,
                        f"{file_path.relative_to(path)}: "
                        "scripts/ file missing docstring/usage comment in first 5 lines",
                    )
                )

    return issues


def check_deployment_readiness(skill_dir: str, frontmatter: dict) -> list:
    """Deployment gate checks that can be done mechanically."""
    issues = []
    path = Path(skill_dir)

    # requirements.txt or package.json — warn if deps are unpinned
    for dep_file in ["requirements.txt", "package.json", "pyproject.toml"]:
        dep_path = path / dep_file
        if dep_path.exists():
            try:
                content = dep_path.read_text(encoding="utf-8", errors="ignore")
                for line in content.splitlines():
                    stripped = line.strip()
                    if not stripped or stripped.startswith("#"):
                        continue
                    # Unpinned: no version specifier
                    if "==" not in stripped and ">=" not in stripped and "~=" not in stripped:
                        issues.append(
                            (
                                SEVERITY_WARN,
                                f"'{dep_file}' contains unpinned dependency: '{stripped}' — "
                                "pin to a version (e.g. 'package==1.2.3')",
                            )
                        )
                        break  # warn once per file
            except Exception:
                pass

    return issues


def validate_skill(skill_dir: str, json_output: bool = False):
    """Run all checks on a skill directory. Returns list of issues."""
    skill_path = Path(skill_dir)
    if not skill_path.is_dir():
        return [(SEVERITY_ERROR, f"'{skill_dir}' is not a directory")]

    issues = []

    # Parse SKILL.md
    skill_md = skill_path / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text(encoding="utf-8", errors="ignore")
        frontmatter, body = parse_frontmatter(content)
        issues += check_frontmatter_fields(frontmatter, skill_dir)
        issues += check_skill_md_body(body, frontmatter)
    else:
        issues.append((SEVERITY_ERROR, "SKILL.md not found"))
        return issues  # can't continue without frontmatter

    issues += check_directory_layout(skill_dir)
    issues += check_file_content(skill_dir)
    issues += check_deployment_readiness(skill_dir, frontmatter)

    return issues


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_skill.py <skill_dir> [--json]")
        sys.exit(1)

    json_output = "--json" in sys.argv
    # skill_dir is the first non-flag argument
    args = [a for a in sys.argv[1:] if a != "--json"]
    skill_dir = args[0] if args else "."

    issues = validate_skill(skill_dir, json_output=json_output)

    errors = [i for i in issues if i[0] == SEVERITY_ERROR]
    warnings = [i for i in issues if i[0] == SEVERITY_WARN]

    if json_output:
        result = {
            "passed": len(errors) == 0,
            "errors": [{"severity": s, "message": m} for s, m in errors],
            "warnings": [{"severity": s, "message": m} for s, m in warnings],
        }
        print(json.dumps(result, indent=2))
        sys.exit(0 if len(errors) == 0 else 1)

    # Human-readable output
    if not issues:
        print(f"[OK] Skill '{skill_dir}' passes all structural checks.")
        sys.exit(0)

    for severity, message in issues:
        tag = "[ERROR]" if severity == SEVERITY_ERROR else "[WARN]"
        print(f"{tag} {message}")

    print()
    if errors:
        print(f"[FAIL] {len(errors)} error(s), {len(warnings)} warning(s).")
        sys.exit(1)
    else:
        print(f"[OK] {len(warnings)} warning(s) only — skill is structurally valid.")
        sys.exit(0)


if __name__ == "__main__":
    main()
