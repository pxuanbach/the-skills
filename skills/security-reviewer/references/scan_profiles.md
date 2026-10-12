# Scan Profiles

`scripts/plan_scan.py` turns a target directory into `scan-plan.json`: which framework projects exist, which files are in scope, which scanners are installed, where the attack-surface hotspots are, and who owns each vulnerability category. The design borrows two ideas:

- **Deterministic routing before any reasoning** (alibaba/open-code-review): files are routed to rules by path globs and content sniffing, never by agent judgment.
- **Coverage ledger** (cloudflare/security-audit-skill): every category has an explicit owner and status, so "not scanned" can never read as "clean".

## Built-in profiles

| Profile | Detected by | Root |
|---|---|---|
| `generic` | always | repo root: secrets + dependency scan for any stack |
| `nextjs` | `next.config.*`, or `next` in `package.json` deps | directory of the marker |
| `fastapi` | `fastapi` in `pyproject.toml` / `requirements*.txt` / `Pipfile` / `setup.*`; falls back to sniffing `from fastapi` in `*.py` | directory of the manifest |

Monorepos produce one project per detected root. When the same profile matches nested directories, the outermost root wins.

## Profile schema (`references/profiles/<id>.json`)

| Field | Meaning |
|---|---|
| `id` | Profile name, referenced in overrides and the plan. |
| `detect` | `always`, `any_files`, `package_deps`, `python_deps`, `content_sniff {glob, regex, max_files}`. |
| `include` / `exclude` | Globs relative to the project root. Supports `**`, `*`, `?`, `{a,b}`. |
| `scanners` | `role → [scanner ids]` in preference order. Roles: `sast`, `secrets`, `deps`. Ids come from `references/scanners.json`; `builtin-*` scanners are always available, others are resolved on PATH. |
| `settings` | Framework knowledge the rules use: `auth_functions` (Next.js), `auth_dependencies` (FastAPI), `auth_pattern` (regex fallback), `public_routes` (globs skipped by the no-auth rules). |
| `coverage` | `category → owner`, where owner is `tool`, `tool+manual`, or `manual`. |
| `hotspots` | `{id, glob, regex?, category, why}` — attack-surface locations listed for the manual review. A hotspot is a place to look, not a finding. |

## Coverage status

| Status | Meaning | Reviewer action |
|---|---|---|
| `planned` | Owner includes `tool` and the scanner is available (becomes `scanned` after `run_scan.py`). | Triage the tool findings; review hotspots if owner is `tool+manual`. |
| `degraded` | Owner includes `tool` but the scanner is unavailable or failed. | Review the category manually and state the degradation in the report. |
| `manual` | Category is owned by the reviewer only. | Review hotspots and scope files for this category. |

Categories that no detected profile covers appear as `manual` with `project: null`.

## Per-repo overrides (`<target>/.security-reviewer.json`)

```json
{
  "disable_profiles": ["generic"],
  "profiles": {
    "fastapi": {
      "settings": { "auth_dependencies": ["get_principal"] },
      "+exclude": ["**/legacy/**"]
    }
  }
}
```

Merge rules: objects merge recursively, lists are **replaced**, and a `+key` list is **appended** to `key`. An override entry with its own `detect` block defines a new profile inline. `--profiles-dir <dir>` loads additional profile files with the same schema.

## Adding a framework

1. Copy `profiles/nextjs.json` or `profiles/fastapi.json` to `profiles/<id>.json`.
2. Set `detect`, `include`/`exclude`, `scanners`, `coverage`, and `hotspots`.
3. Run `python scripts/plan_scan.py <sample-repo>` and confirm the project, scope, and hotspots are detected.
