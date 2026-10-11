#!/usr/bin/env python3
"""
plan_scan.py - Detect project stacks and resolve scan profiles for the Security Reviewer.

Step 1 (Detection): walks the target, finds framework projects (Next.js, FastAPI, ...)
by manifest files and content sniffing, and computes the file scope (full repo or a git diff).
Step 2 (Profiles): loads references/profiles/*.json, merges per-repo overrides from
<target>/.security-reviewer.json, resolves which scanners are installed, maps attack-surface
hotspots, and assigns every vulnerability category an owner (tool / tool+manual / manual).

The output (scan-plan.json) is the input contract for the scan engine and the manual review.
Stdlib only.

Usage:
    python plan_scan.py <target_dir> [--diff <base_ref> | --files <f1> <f2> ...]
                        [--out <scan-plan.json>] [--profiles-dir <dir>] [--quiet]
"""

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys

try:
    import tomllib
except ImportError:  # Python < 3.11
    tomllib = None

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REFERENCES_DIR = os.path.join(SKILL_DIR, "references")
OVERRIDE_FILE = ".security-reviewer.json"

CATEGORIES = [
    "injection", "authz", "data_exposure", "crypto", "input_validation",
    "business_logic", "config", "supply_chain", "rce", "xss",
]
# Which scanner role a "tool" owner relies on for each category.
CATEGORY_ROLE = {"supply_chain": "deps", "data_exposure": "secrets"}

PRUNE_DIRS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__", ".next", "dist", "build",
    ".tox", ".mypy_cache", ".pytest_cache", ".ruff_cache", "site-packages", "coverage", "out",
}
PYTHON_MANIFESTS = ("pyproject.toml", "Pipfile", "setup.py", "setup.cfg")
MAX_READ_BYTES = 1_000_000
MAX_HITS_PER_HOTSPOT = 300
MAX_LINES_PER_FILE = 20
MAX_SCOPE_FILES_LISTED = 5000


# ---------------------------------------------------------------- helpers

def glob_to_regex(pattern):
    """Translate a glob with **, *, ?, {a,b} into an anchored regex (posix paths)."""
    i, out = 0, []
    while i < len(pattern):
        c = pattern[i]
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
            continue
        if pattern.startswith("**", i):
            out.append(".*")
            i += 2
            continue
        if c == "*":
            out.append("[^/]*")
        elif c == "?":
            out.append("[^/]")
        elif c == "{":
            end = pattern.find("}", i)
            if end == -1:
                out.append(re.escape(c))
            else:
                alts = pattern[i + 1:end].split(",")
                out.append("(?:" + "|".join(glob_to_regex(a)[1:-1] for a in alts) + ")")
                i = end + 1
                continue
        else:
            out.append(re.escape(c))
        i += 1
    return "^" + "".join(out) + "$"


_GLOB_CACHE = {}


def glob_match(path, pattern):
    rx = _GLOB_CACHE.get(pattern)
    if rx is None:
        rx = _GLOB_CACHE[pattern] = re.compile(glob_to_regex(pattern))
    return rx.match(path) is not None


def matches_any(path, patterns):
    return any(glob_match(path, p) for p in patterns)


def read_text(path):
    try:
        if os.path.getsize(path) > MAX_READ_BYTES:
            return None
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        return None
    if b"\0" in data[:8192]:
        return None
    return data.decode("utf-8", errors="replace")


def rel_to(path, root):
    """Path relative to root ("." means repo root); None when outside root."""
    if root == ".":
        return path
    prefix = root + "/"
    return path[len(prefix):] if path.startswith(prefix) else None


def deep_merge(base, override):
    """Dicts merge recursively, lists are replaced; a key "+name" appends to list "name"."""
    result = dict(base)
    for key, val in override.items():
        if key.startswith("+") and isinstance(val, list):
            name = key[1:]
            result[name] = list(result.get(name, [])) + val
        elif isinstance(val, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], val)
        else:
            result[key] = val
    return result


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------- step 1: inventory

def walk_files(target):
    files = []
    for dirpath, dirnames, filenames in os.walk(target):
        dirnames[:] = [d for d in dirnames if d not in PRUNE_DIRS]
        rel_dir = os.path.relpath(dirpath, target).replace(os.sep, "/")
        for name in filenames:
            files.append(name if rel_dir == "." else f"{rel_dir}/{name}")
    files.sort()
    return files


def files_by_dir(files):
    index = {}
    for f in files:
        d, _, name = f.rpartition("/")
        index.setdefault(d or ".", set()).add(name)
    return index


def package_deps(path):
    try:
        data = load_json(path)
    except (OSError, ValueError):
        return set()
    deps = set()
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        deps.update((data.get(key) or {}).keys())
    return deps


def python_manifest_has(path, dep):
    text = read_text(path) or ""
    if path.endswith("pyproject.toml") and tomllib:
        try:
            data = tomllib.loads(text)
            project = data.get("project", {})
            poetry = data.get("tool", {}).get("poetry", {})
            names = list(project.get("dependencies", []))
            for group in project.get("optional-dependencies", {}).values():
                names.extend(group)
            names.extend(poetry.get("dependencies", {}).keys())
            return any(re.match(rf"^{re.escape(dep)}\b", n.strip(), re.I) for n in names)
        except tomllib.TOMLDecodeError:
            pass
    return re.search(rf"(?im)(^|[\s\"'\[,]){re.escape(dep)}([\s\[=<>~!;,\"']|$)", text) is not None


def nearest_python_root(file_rel, dir_index):
    parts = file_rel.split("/")[:-1]
    while parts:
        d = "/".join(parts)
        names = dir_index.get(d, set())
        if any(n in names for n in PYTHON_MANIFESTS) or any(n.startswith("requirements") for n in names):
            return d
        parts.pop()
    return "."


def detect_roots(profile, target, files, dir_index):
    """Return {root: [evidence, ...]} for one profile."""
    det = profile.get("detect", {})
    roots = {}

    def add(root, why):
        roots.setdefault(root, []).append(why)

    if det.get("always"):
        add(".", "always")
    for d, names in dir_index.items():
        for marker in det.get("any_files", []):
            if marker in names:
                add(d, f"file:{marker}")
        if det.get("package_deps") and "package.json" in names:
            deps = package_deps(os.path.join(target, d, "package.json"))
            for dep in det["package_deps"]:
                if dep in deps:
                    add(d, f"package.json dep:{dep}")
        for dep in det.get("python_deps", []):
            manifests = [n for n in names if n in PYTHON_MANIFESTS or re.match(r"requirements.*\.txt$", n)]
            for m in manifests:
                if python_manifest_has(os.path.join(target, d, m), dep):
                    add(d, f"{m} dep:{dep}")

    sniff = det.get("content_sniff")
    if sniff and not roots:
        rx = re.compile(sniff["regex"], re.M)
        checked = 0
        for f in files:
            if checked >= sniff.get("max_files", 300):
                break
            if not glob_match(f, sniff["glob"]):
                continue
            checked += 1
            text = read_text(os.path.join(target, f))
            if text and rx.search(text):
                add(nearest_python_root(f, dir_index), f"sniff:{f}")

    # Keep the outermost root when the same profile matches nested directories.
    ordered = sorted(roots, key=lambda r: (r.count("/") if r != "." else -1, r))
    kept = {}
    for r in ordered:
        if any(k == "." or r.startswith(k + "/") for k in kept):
            continue
        kept[r] = sorted(set(roots[r]))
    return kept


def changed_files(target, base_ref):
    def git(*args):
        res = subprocess.run(["git", "-C", target, *args], capture_output=True, text=True)
        if res.returncode != 0:
            first = (res.stderr.strip().splitlines() or [f"git {' '.join(args)} failed"])[0]
            raise RuntimeError(f"--diff needs a git work tree: {first}")
        return [l.strip() for l in res.stdout.splitlines() if l.strip()]

    diff = git("diff", "--name-only", "--relative", "--diff-filter=ACMR", base_ref)
    untracked = git("ls-files", "--others", "--exclude-standard")
    return sorted(set(diff) | set(untracked))


# ---------------------------------------------------------------- step 2: profiles

def load_profiles(extra_dir):
    profiles = {}
    for d in [os.path.join(REFERENCES_DIR, "profiles"), extra_dir]:
        if not d or not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if name.endswith(".json"):
                p = load_json(os.path.join(d, name))
                profiles[p["id"]] = deep_merge(profiles.get(p["id"], {}), p)
    return profiles


def apply_overrides(profiles, target):
    path = os.path.join(target, OVERRIDE_FILE)
    if not os.path.exists(path):
        return profiles, None
    override = load_json(path)
    for pid in override.get("disable_profiles", []):
        profiles.pop(pid, None)
    for pid, patch in override.get("profiles", {}).items():
        if pid in profiles:
            profiles[pid] = deep_merge(profiles[pid], patch)
        elif "detect" in patch:  # a repo may define a whole new profile inline
            profiles[pid] = dict(patch, id=pid)
    return profiles, OVERRIDE_FILE


def resolve_scanners(profile, registry, target, root):
    root_names = set(os.listdir(os.path.join(target, root))) if os.path.isdir(os.path.join(target, root)) else set()
    resolved = {}
    for role, candidates in profile.get("scanners", {}).items():
        options = []
        for sid in candidates:
            spec = registry.get(sid)
            if spec is None:
                options.append({"id": sid, "available": False, "reason": "unknown scanner id"})
                continue
            if spec.get("builtin"):
                options.append({"id": sid, "available": True, "builtin": True})
                continue
            binary = next((b for b in spec["binaries"] if shutil.which(b)), None)
            needs = spec.get("requires_any_file")
            if not binary:
                options.append({"id": sid, "available": False, "reason": "not installed", "install": spec.get("install")})
            elif needs and not any(n in root_names for n in needs):
                options.append({"id": sid, "available": False, "reason": f"no {'/'.join(needs)} in project root"})
            else:
                options.append({"id": sid, "available": True, "binary": shutil.which(binary)})
        selected = next((o["id"] for o in options if o["available"]), None)
        resolved[role] = {"selected": selected, "candidates": options}
    return resolved


def map_hotspots(profile, target, root, scope):
    results = []
    for spot in profile.get("hotspots", []):
        rx = re.compile(spot["regex"], re.M) if spot.get("regex") else None
        hits, truncated = [], False
        for f in scope:
            local = rel_to(f, root)
            if local is None or not glob_match(local, spot["glob"]):
                continue
            if rx is None:
                hits.append({"file": f, "lines": []})
            else:
                text = read_text(os.path.join(target, f))
                if not text:
                    continue
                lines = [text.count("\n", 0, m.start()) + 1 for m in rx.finditer(text)]
                if lines:
                    hits.append({"file": f, "lines": lines[:MAX_LINES_PER_FILE]})
            if len(hits) >= MAX_HITS_PER_HOTSPOT:
                truncated = True
                break
        if hits:
            results.append({"id": spot["id"], "category": spot.get("category"), "why": spot.get("why"),
                            "hits": hits, "truncated": truncated})
    return results


def resolve_coverage(profile, scanners):
    coverage = {}
    for cat, owner in profile.get("coverage", {}).items():
        role = CATEGORY_ROLE.get(cat, "sast")
        if role not in scanners:
            role = "sast"  # e.g. secrets are scanned repo-wide by `generic`; framework profiles use SAST
        tool_ready = bool(scanners.get(role, {}).get("selected"))
        if owner == "manual":
            status = "manual"
        elif tool_ready:
            status = "planned"
        else:
            status = "degraded"  # tool owner but no scanner: manual review must cover it
        coverage[cat] = {"owner": owner, "role": role, "status": status}
    return coverage


# ---------------------------------------------------------------- main

def build_plan(target, base_ref=None, explicit_files=None, extra_profiles=None):
    target = os.path.abspath(target)
    files = walk_files(target)
    dir_index = files_by_dir(files)
    registry = load_json(os.path.join(REFERENCES_DIR, "scanners.json"))["scanners"]
    profiles, override_used = apply_overrides(load_profiles(extra_profiles), target)
    warnings = []

    if explicit_files:
        mode, changed = "files", sorted({re.sub(r"^(\./)+", "", f.replace("\\", "/")) for f in explicit_files})
    elif base_ref:
        mode, changed = "diff", changed_files(target, base_ref)
    else:
        mode, changed = "full", None
    universe = set(changed) & set(files) if changed is not None else set(files)

    projects, covered_files = [], set()
    for pid, profile in sorted(profiles.items()):
        for root, evidence in detect_roots(profile, target, files, dir_index).items():
            scope = []
            for f in sorted(universe):
                local = rel_to(f, root)
                if local is not None and matches_any(local, profile.get("include", ["**/*"])) \
                        and not matches_any(local, profile.get("exclude", [])):
                    scope.append(f)
            if mode != "full" and not scope:
                continue  # nothing changed in this project
            scanners = resolve_scanners(profile, registry, target, root)
            if pid != "generic":
                covered_files.update(scope)
            projects.append({
                "profile": pid,
                "root": root,
                "evidence": evidence,
                "scope_file_count": len(scope),
                "scope_files": scope[:MAX_SCOPE_FILES_LISTED],
                "scanners": scanners,
                "settings": profile.get("settings", {}),
                "coverage": resolve_coverage(profile, scanners),
                "hotspots": map_hotspots(profile, target, root, scope),
            })
            for role, info in scanners.items():
                if not info["selected"]:
                    warnings.append(f"[{pid}:{root}] no {role} scanner available "
                                    f"(tried {', '.join(c['id'] for c in info['candidates'])})")

    summary = {}
    for cat in CATEGORIES:
        owners = [{"project": f"{p['profile']}:{p['root']}", **p["coverage"][cat]}
                  for p in projects if cat in p["coverage"]]
        summary[cat] = owners or [{"project": None, "owner": "manual", "status": "manual",
                                   "note": "no detected profile covers this category"}]

    plan = {
        "schema_version": 1,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "target": target,
        "mode": mode,
        "base_ref": base_ref,
        "override_file": override_used,
        "projects": projects,
        "coverage_summary": summary,
        "warnings": warnings,
    }
    if changed is not None:
        plan["changed_files"] = changed
        plan["unprofiled_files"] = sorted(universe - covered_files)
    return plan


def print_summary(plan):
    print(f"Target: {plan['target']}  (mode: {plan['mode']}{', base ' + plan['base_ref'] if plan['base_ref'] else ''})")
    if plan["override_file"]:
        print(f"Overrides: {plan['override_file']}")
    print(f"\nProjects ({len(plan['projects'])}):")
    for p in plan["projects"]:
        sel = ", ".join(f"{r}={i['selected'] or 'MISSING'}" for r, i in p["scanners"].items())
        print(f"  - {p['profile']:<8} root={p['root']:<20} files={p['scope_file_count']:<5} {sel}")
        for h in p["hotspots"]:
            print(f"      hotspot {h['id']:<18} {len(h['hits'])} file(s){' (truncated)' if h['truncated'] else ''}")
    print("\nCoverage:")
    for cat, owners in plan["coverage_summary"].items():
        states = ", ".join(f"{o['owner']}/{o['status']}" + (f"@{o['project']}" if o["project"] else "") for o in owners)
        print(f"  {cat:<17} {states}")
    if plan.get("unprofiled_files"):
        print(f"\nChanged files outside any framework profile: {len(plan['unprofiled_files'])} (manual review)")
    if plan["warnings"]:
        print("\nWarnings:")
        for w in plan["warnings"]:
            print(f"  - {w}")


def main():
    ap = argparse.ArgumentParser(description="Detect stacks and resolve security scan profiles.")
    ap.add_argument("target", help="Repository or project directory to scan")
    scope = ap.add_mutually_exclusive_group()
    scope.add_argument("--diff", metavar="BASE_REF", help="Limit scope to files changed since BASE_REF (plus untracked)")
    scope.add_argument("--files", nargs="+", help="Limit scope to these paths (relative to target)")
    ap.add_argument("--out", help="Write the plan JSON here (e.g. wiki/<NNN>-<feature>/scan-plan.json)")
    ap.add_argument("--profiles-dir", help="Extra directory of profile JSON files")
    ap.add_argument("--quiet", action="store_true", help="Do not print the human summary")
    args = ap.parse_args()

    if not os.path.isdir(args.target):
        print(f"[ERROR] Target '{args.target}' is not a directory.")
        sys.exit(1)
    try:
        plan = build_plan(args.target, args.diff, args.files, args.profiles_dir)
    except (RuntimeError, ValueError, KeyError) as exc:
        print(f"[ERROR] {exc}")
        sys.exit(1)

    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=2)
            f.write("\n")
    if not args.quiet:
        print_summary(plan)
        if args.out:
            print(f"\n[SUCCESS] Scan plan written to {args.out}")
    elif not args.out:
        json.dump(plan, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
