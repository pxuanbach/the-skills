#!/usr/bin/env python3
"""
run_scan.py - Run the built-in security scanners described by a scan plan and write findings.json.

Reads scan-plan.json (from plan_scan.py), or builds one on the fly when given a directory.
For each detected project it runs the selected scanners:
  builtin-python -> scan_python.py   builtin-js -> scan_js.py   builtin-secrets -> scan_secrets.py
  npm-audit / pip-audit -> optional, only when installed (network call to the package registry)
Every finding starts with verdict "untriaged"; the reviewer triages it in security-review.md.

Usage:
    python run_scan.py wiki/<NNN>-<feature>/scan-plan.json [--out findings.json] [--no-deps]
    python run_scan.py <project-dir> [--diff <base-ref>] [--out findings.json] [--no-deps]
"""

import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plan_scan  # noqa: E402
import scan_js  # noqa: E402
import scan_python  # noqa: E402
import scan_secrets  # noqa: E402
from scan_common import SEVERITY_ORDER, finding  # noqa: E402

AUDIT_SEVERITY = {"critical": "high", "high": "high", "moderate": "medium", "medium": "medium", "low": "low", "info": "low"}


def run_npm_audit(target, root):
    res = subprocess.run([shutil.which("npm") or "npm", "audit", "--json", "--omit=dev"],
                         cwd=os.path.join(target, root), capture_output=True, text=True, timeout=180)
    data = json.loads(res.stdout or "{}")
    if "error" in data:
        raise RuntimeError(data["error"].get("summary", "npm audit failed"))
    lock = f"{root}/package-lock.json" if root != "." else "package-lock.json"
    out = []
    for name, vuln in (data.get("vulnerabilities") or {}).items():
        titles = [v.get("title") or v.get("url") for v in vuln.get("via", []) if isinstance(v, dict)]
        if not titles:
            continue  # only pulled in through another vulnerable package; reported there
        out.append(finding("DEP-NPM", "supply_chain", AUDIT_SEVERITY.get(vuln.get("severity"), "medium"), lock, 1,
                           f"{name} {vuln.get('range', '')}: {'; '.join(titles[:3])}", f"{name}@{vuln.get('range', '')}"))
    return out


def run_pip_audit(target, root):
    req = os.path.join(target, root, "requirements.txt")
    res = subprocess.run(["pip-audit", "-r", req, "-f", "json", "--progress-spinner", "off"],
                         capture_output=True, text=True, timeout=300)
    data = json.loads(res.stdout or "{}")
    rel = f"{root}/requirements.txt" if root != "." else "requirements.txt"
    out = []
    for dep in data.get("dependencies", data if isinstance(data, list) else []):
        for v in dep.get("vulns", []):
            fix = ", ".join(v.get("fix_versions", [])) or "none"
            out.append(finding("DEP-PIP", "supply_chain", "high", rel, 1,
                               f"{dep['name']} {dep.get('version', '')}: {v.get('id')} (fixed in {fix})",
                               f"{dep['name']}=={dep.get('version', '')} {v.get('id')}"))
    return out


RUNNERS = {
    "builtin-python": lambda t, p: scan_python.scan(t, p["scope_files"], p["settings"]),
    "builtin-js": lambda t, p: scan_js.scan(t, p["scope_files"], p["settings"], p["root"]),
    "builtin-secrets": lambda t, p: scan_secrets.scan(t, p["scope_files"]),
    "npm-audit": lambda t, p: run_npm_audit(t, p["root"]),
    "pip-audit": lambda t, p: run_pip_audit(t, p["root"]),
}


def run(plan, skip_deps=False):
    target = plan["target"]
    findings, errors, ran = {}, [], {}
    for project in plan["projects"]:
        key = f"{project['profile']}:{project['root']}"
        for role, info in project["scanners"].items():
            sid = info["selected"]
            if not sid or (skip_deps and role == "deps"):
                continue
            try:
                for f in RUNNERS[sid](target, project):
                    f["project"] = key
                    if f["id"] in findings:
                        findings[f["id"]].setdefault("also_lines", []).append(f["line"])
                    else:
                        findings[f["id"]] = f
                ran[(key, role)] = sid
            except (OSError, ValueError, RuntimeError, subprocess.SubprocessError, KeyError) as exc:
                errors.append(f"[{key}] {sid} failed: {exc}")

        # Coverage: a tool-owned category is "scanned" only if its scanner actually ran.
        for cat, cov in project["coverage"].items():
            if cov["status"] == "planned":
                cov["status"] = "scanned" if (key, cov["role"]) in ran else "degraded"

    ordered = sorted(findings.values(), key=lambda f: (SEVERITY_ORDER[f["severity"]], f["file"], f["line"]))
    summary = {}
    for cat in plan_scan.CATEGORIES:
        states = [{"project": f"{p['profile']}:{p['root']}", **p["coverage"][cat]}
                  for p in plan["projects"] if cat in p["coverage"]]
        summary[cat] = states or [{"project": None, "owner": "manual", "status": "manual"}]
    return {
        "schema_version": 1,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "target": target,
        "mode": plan["mode"],
        "counts": {s: sum(1 for f in ordered if f["severity"] == s) for s in SEVERITY_ORDER},
        "findings": ordered,
        "coverage_summary": summary,
        "errors": errors,
    }


def print_summary(result, limit=40):
    c = result["counts"]
    print(f"Findings: {c['high']} high, {c['medium']} medium, {c['low']} low")
    for f in result["findings"][:limit]:
        print(f"  {f['id']}  {f['severity']:<6} {f['rule_id']:<18} {f['file']}:{f['line']}  {f['message']}")
    if len(result["findings"]) > limit:
        print(f"  ... {len(result['findings']) - limit} more in findings.json")
    print("\nCoverage needing manual review:")
    for cat, states in result["coverage_summary"].items():
        todo = [s for s in states if s["status"] in ("degraded", "manual") or s["owner"] == "tool+manual"]
        if todo:
            print(f"  {cat:<17} " + ", ".join(f"{s['owner']}/{s['status']}" + (f"@{s['project']}" if s["project"] else "") for s in todo))
    for e in result["errors"]:
        print(f"[WARN] {e}")


def main():
    ap = argparse.ArgumentParser(description="Run built-in security scanners from a scan plan.")
    ap.add_argument("plan", help="scan-plan.json, or a project directory to plan and scan in one go")
    ap.add_argument("--diff", metavar="BASE_REF", help="With a directory: limit scope to files changed since BASE_REF")
    ap.add_argument("--out", help="Output path (default: findings.json next to the plan, or stdout summary only)")
    ap.add_argument("--no-deps", action="store_true", help="Skip npm-audit / pip-audit (no network)")
    args = ap.parse_args()

    if os.path.isdir(args.plan):
        plan = plan_scan.build_plan(args.plan, args.diff)
        out = args.out
    else:
        with open(args.plan, "r", encoding="utf-8") as f:
            plan = json.load(f)
        out = args.out or os.path.join(os.path.dirname(os.path.abspath(args.plan)), "findings.json")

    result = run(plan, args.no_deps)
    if out:
        with open(out, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
            f.write("\n")
    print_summary(result)
    if out:
        print(f"\n[SUCCESS] {len(result['findings'])} finding(s) written to {out}")


if __name__ == "__main__":
    main()
