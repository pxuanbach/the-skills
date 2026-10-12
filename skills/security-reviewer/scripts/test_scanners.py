#!/usr/bin/env python3
"""Regression test: run run_scan.py on examples/fixtures and assert expected rules.

Usage: python test_scanners.py
Exit 0 when all expectations hold, 1 otherwise.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, "..", "examples", "fixtures")
EXPECT = {
    "fastapi": {"PY-CMDI", "PY-SQLI", "SEC-AWS", "PY-ROUTE-NOAUTH"},
    "nextjs": {"JS-CMDI", "JS-EVAL", "JS-ROUTE-NOAUTH"},
}


def scan(name):
    out = os.path.join(tempfile.mkdtemp(), "findings.json")
    subprocess.run([sys.executable, os.path.join(HERE, "run_scan.py"), os.path.join(FIX, name),
                    "--no-deps", "--out", out], check=True, capture_output=True)
    data = json.load(open(out, encoding="utf-8"))
    return data["findings"] if isinstance(data, dict) else data


def main():
    failed = False
    for name, want in EXPECT.items():
        found = scan(name)
        rules = {f.get("rule_id") for f in found}
        missing = want - rules
        print(f"[{'FAIL' if missing else 'OK'}] {name}: missing={sorted(missing)}")
        failed |= bool(missing)
        if name == "nextjs":
            cmdi = [f for f in found if f.get("rule_id") == "JS-CMDI"]
            if len(cmdi) != 1:
                print(f"[FAIL] nextjs: expected exactly 1 JS-CMDI (regex .exec must not fire), got {len(cmdi)}")
                failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
